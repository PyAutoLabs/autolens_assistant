#!/usr/bin/env python3
"""PreToolUse(Bash) gate: validate PyAuto* API symbols before code runs.

Two recurring failures motivated this hook: a session generated `al.FitImagingPlotter`
and `from autoarray.structures.arrays.kernel_2d import Kernel2D` from memory and ran them
via `python3 -c "..."`, crashing on symbols that were renamed/removed long ago. The
version drift-check could not catch them — the installed stack *matched* the pinned
baseline, so it reported "clean". Nothing validated the code the agent actually ran.

This hook closes that gap, independent of any version match:

  1. Read the Bash command from stdin (`tool_input.command`).
  2. Cheap pre-screen (no import): only proceed if the command runs Python AND a source
     it would execute (a `-c` snippet, or a `.py` file argument on disk) contains a
     PyAuto* alias-rooted symbol. Everything else is a silent allow — zero latency.
  3. For each flagged source, run `autoassistant/audit_skill_apis.py --code/--file` using the SAME
     interpreter the command would use, so symbols resolve against the exact stack.
  4. If any symbol does not resolve, DENY the call with the gate's report so the agent
     re-grounds against the live API / skills. Otherwise allow.

Fail-open by design: any internal error (unparseable command, missing validator, etc.)
allows the call — the gate must never block legitimate work because of its own bugs. A
broken stack (validator exit 3: imports fail, e.g. the workspace version check) also
fails open: the command will surface the same import error itself, and blocking it
would conflate a broken environment with symbol drift.
Escape hatch: set PYAUTO_SKIP_API_GATE=1 — in the hook's environment, or as a prefix on
the command itself (`PYAUTO_SKIP_API_GATE=1 python …`); the hook process env is the
session's, not the command's, so the prefix form is detected in the command text.

The same script backs both the autolens_assistant hook and the PyAutoLabs-monorepo hook;
the validator path is resolved relative to this file, so it works from either project.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# Alias-rooted symbol (`al.`, `aa.`, `aplt.`, `autoarray.` …) or the literal dead
# kernel_2d module path. Mirrors ALIAS_TO_MODULE in autoassistant/audit_skill_apis.py.
_ALIASES = (
    "aplt",
    "autoconf",
    "autoarray",
    "autofit",
    "autogalaxy",
    "autolens",
    "al",
    "aa",
    "af",
    "ag",
)
SYMBOL_RE = re.compile(
    r"(?<![A-Za-z0-9_.])(?:" + "|".join(_ALIASES) + r")\.[A-Za-z_]"
)
PYTHON_RE = re.compile(r"(?:^|/)python[0-9.]*$")

# Files that legitimately mention stale symbols as regex patterns / docstring examples /
# test fixtures — they are *about* the API surface, they don't *execute* it. Validating
# them would always block (matching the audit's own `tooling` exclusion). A file can also
# opt out by containing the marker comment below.
_SELF_FILES = {
    "audit_skill_apis.py",
    "refresh_api_docs.py",
    "validate_pyauto_code.py",
    "test_api_gate.py",
}
_SKIP_MARKER = "pyauto-api-gate: skip"

# autoassistant/audit_skill_apis.py, resolved relative to this hook (…/.claude/hooks/x.py).
VALIDATOR = Path(__file__).resolve().parent.parent.parent / "autoassistant" / "audit_skill_apis.py"


def _allow() -> None:
    """Silent exit 0 — defers to the normal permission flow."""
    sys.exit(0)


def _deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def _has_symbol(text: str) -> bool:
    return bool(SYMBOL_RE.search(text))


def _collect_sources(tokens: list[str], cwd: Path) -> tuple[str, list[tuple[str, str]]]:
    """From shell tokens, return (interpreter, [(kind, payload), …]) where kind is
    'code' (a -c snippet string) or 'file' (a .py path). Only sources that actually
    contain a PyAuto* symbol are kept — that is the no-import pre-screen."""
    interpreter = "python3"
    saw_python = False
    sources: list[tuple[str, str]] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if PYTHON_RE.search(tok):
            interpreter = tok
            saw_python = True
        elif saw_python and tok == "-c" and i + 1 < len(tokens):
            snippet = tokens[i + 1]
            if _has_symbol(snippet):
                sources.append(("code", snippet))
            i += 1
        elif saw_python and tok.endswith(".py") and not tok.startswith("-"):
            p = Path(tok)
            if not p.is_absolute():
                p = cwd / p
            if p.name in _SELF_FILES:
                i += 1
                continue
            try:
                text = p.read_text(encoding="utf-8") if p.is_file() else ""
                if text and _SKIP_MARKER not in text and _has_symbol(text):
                    sources.append(("file", str(p)))
            except OSError:
                pass
        i += 1
    return interpreter, sources


def main() -> None:
    # Always consume stdin first: exiting before reading the harness's JSON would
    # leave it writing to a closed pipe.
    raw = sys.stdin.read()

    if os.environ.get("PYAUTO_SKIP_API_GATE") == "1":
        _allow()

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        _allow()

    if payload.get("tool_name") != "Bash":
        _allow()

    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = Path(payload.get("cwd") or ".")

    # Per-command escape hatch: an env-var prefix on the command sets the variable
    # for the *command's* process, not this hook's, so it must be detected in the
    # command text itself.
    if re.search(r"\bPYAUTO_SKIP_API_GATE=1\b", command):
        _allow()

    # Fast reject: not a Python invocation, or no PyAuto* symbol anywhere in the command.
    if "python" not in command or not _has_symbol(command):
        # `_has_symbol(command)` misses symbols that live only inside a referenced .py
        # file, but those still require `python` + a `.py` arg, caught below. If the
        # command names no .py file and has no inline symbol, there is nothing to check.
        if ".py" not in command:
            _allow()

    try:
        tokens = shlex.split(command)
    except ValueError:
        _allow()  # unbalanced quotes / heredoc — cannot parse safely, fail open

    interpreter, sources = _collect_sources(tokens, cwd)
    if not sources:
        _allow()

    reports: list[str] = []
    for kind, payload_str in sources:
        flag = "--code" if kind == "code" else "--file"
        try:
            proc = subprocess.run(
                [interpreter, str(VALIDATOR), flag, payload_str],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError):
            continue  # validator unrunnable — fail open for this source
        # Only returncode 2 (stale symbols/idioms) denies. Exit 3 — the stack itself
        # failed to import (broken env / workspace version check) — falls through to
        # allow: the command will raise the same import error on its own, and the
        # gate only guards symbol drift.
        if proc.returncode == 2:
            stale = [
                ln.strip()
                for ln in proc.stderr.splitlines()
                if ln.strip().startswith("STALE")
            ]
            if stale:
                label = "snippet" if kind == "code" else payload_str
                reports.append(f"In {label}:\n" + "\n".join("  " + s for s in stale))

    if reports:
        _deny(
            "Blocked: PyAuto* API symbols that do not exist in the installed stack "
            "(these are the Kernel2D/FitImagingPlotter-style stale-from-memory errors).\n\n"
            + "\n\n".join(reports)
            + "\n\nGround the call against the live API: grep skills/ for the task "
            "(e.g. al_load_results.md uses `aplt.subplot_fit_imaging(fit=fit)`), or "
            "introspect `dir()` of the live module. Re-run once corrected. "
            "Set PYAUTO_SKIP_API_GATE=1 to bypass intentionally."
        )
    _allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 — the gate must never crash a Bash call
        sys.exit(0)
