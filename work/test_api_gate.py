# pyauto-api-gate: skip — this file contains intentional stale-symbol fixtures.
"""Regression tests for the pre-execution PyAuto* API gate.

These pin the two failures that motivated the gate — `al.FitImagingPlotter` and
`from autoarray.structures.arrays.kernel_2d import Kernel2D`, both run from memory via
`python3 -c "..."` against a stack where the symbols had been renamed/removed — plus the
current-correct call (`aplt.subplot_fit_imaging`) that must NOT be flagged.

Two layers are covered: the validator modes (`audit_skill_apis.py --code/--file`) and the
PreToolUse hook (`.claude/hooks/validate_pyauto_code.py`). Both shell out using
`sys.executable`, so the tests resolve symbols against the same interpreter/stack pytest
runs under (source `activate.sh` first). Each case imports autolens, so the file is slow
by design — it is a guard, not a unit-speed test.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "work" / "audit_skill_apis.py"
HOOK = ROOT / ".claude" / "hooks" / "validate_pyauto_code.py"

GOOD = "import autolens.plot as aplt; aplt.subplot_fit_imaging(fit=fit)"
STALE_PLOTTER = "import autolens as al; al.FitImagingPlotter(fit=fit).subplot_fit()"
STALE_KERNEL = "from autoarray.structures.arrays.kernel_2d import Kernel2D"

# Keep numba/matplotlib caches writable in sandboxed/CI runs (see CLAUDE.md).
ENV = {
    **os.environ,
    "NUMBA_CACHE_DIR": "/tmp/numba_cache",
    "MPLCONFIGDIR": "/tmp/matplotlib",
    "PYAUTO_SKIP_WORKSPACE_VERSION_CHECK": "1",
}


def _run_validator(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True, text=True, env=ENV, timeout=180,
    )


def _run_hook(command: str, *, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    payload = json.dumps(
        {"tool_name": "Bash", "cwd": str(ROOT), "hook_event_name": "PreToolUse",
         "tool_input": {"command": command}}
    )
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload, capture_output=True, text=True,
        env={**ENV, **(env_extra or {})}, timeout=180,
    )


def _decision(proc: subprocess.CompletedProcess) -> str | None:
    """Return the hook's permissionDecision, or None for a silent allow."""
    out = proc.stdout.strip()
    if not out:
        return None
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"]


# --- validator (--code / --file) -------------------------------------------------------
def test_validator_passes_current_api():
    assert _run_validator("--code", GOOD).returncode == 0


def test_validator_flags_stale_plotter():
    proc = _run_validator("--code", STALE_PLOTTER)
    assert proc.returncode == 2
    assert "FitImagingPlotter" in proc.stderr


def test_validator_flags_stale_kernel_module():
    proc = _run_validator("--code", STALE_KERNEL)
    assert proc.returncode == 2
    assert "kernel_2d" in proc.stderr


def test_validator_file_mode(tmp_path):
    script = tmp_path / "stale.py"
    script.write_text(f"import autolens as al\n{STALE_PLOTTER}\n", encoding="utf-8")
    assert _run_validator("--file", str(script)).returncode == 2
    assert _run_validator("--file", str(tmp_path / "missing.py")).returncode == 2


# --- hook ------------------------------------------------------------------------------
def test_hook_denies_stale_snippet():
    proc = _run_hook(f"{sys.executable} -c '{STALE_PLOTTER}'")
    assert _decision(proc) == "deny"
    assert "FitImagingPlotter" in proc.stdout


def test_hook_denies_stale_kernel():
    proc = _run_hook(f'{sys.executable} -c "{STALE_KERNEL}"')
    assert _decision(proc) == "deny"


def test_hook_allows_current_api():
    assert _decision(_run_hook(f"{sys.executable} -c '{GOOD}'")) is None


def test_hook_allows_non_pyauto_python():
    assert _decision(_run_hook(f"{sys.executable} -c 'import numpy as np; np.zeros(3)'")) is None


def test_hook_allows_non_python_command_without_import():
    # Pre-screen must short-circuit (no autolens import) — assert both allow and speed.
    proc = _run_hook("ls -la /tmp")
    assert _decision(proc) is None


def test_hook_escape_hatch():
    proc = _run_hook(f"{sys.executable} -c '{STALE_PLOTTER}'", env_extra={"PYAUTO_SKIP_API_GATE": "1"})
    assert _decision(proc) is None


def test_hook_validates_py_file_argument(tmp_path):
    good = tmp_path / "good.py"
    good.write_text(f"import autolens.plot as aplt\n{GOOD}\n", encoding="utf-8")
    assert _decision(_run_hook(f"{sys.executable} {good}")) is None

    bad = tmp_path / "bad.py"
    bad.write_text(f"import autolens as al\n{STALE_PLOTTER}\n", encoding="utf-8")
    assert _decision(_run_hook(f"{sys.executable} {bad}")) == "deny"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
