"""Audit PyAuto* API references in AGENTS.md, skills/, wiki/core/ and scripts/ against the
installed stack.

Walks every Markdown file in scope, extracts fully-qualified symbols cited under
the standard aliases (`al`, `aplt`, `af`, `ag`, `aa` and the bare module names),
resolves each one by importing the underlying module and walking attribute by
attribute, checks the arguments of calls to resolvable callables against their
installed `inspect.signature`, and writes a Markdown report listing the misses
with suggested replacements. `--code` / `--file` run the same checks as the
pre-execution code gate.

This is the mechanical half of the `al_audit_skill_apis` skill. The skill drives
interpretation and curates fixes; this script just produces the raw report.

Usage:

    source activate.sh
    python autoassistant/audit_skill_apis.py --check-install
    python autoassistant/audit_skill_apis.py --scope all   # AGENTS.md + skills + wiki/core/api + wiki/core/stack + scripts
    python autoassistant/audit_skill_apis.py --scope skills
    python autoassistant/audit_skill_apis.py --scope wiki

Report lands at `autoassistant/audit/skill_api_audit_<YYYY-MM-DD>.md` by default.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import difflib
import hashlib
import importlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterable, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - yaml ships with the stack (autonerves dep)
    yaml = None

# ---------------------------------------------------------------------------
# API baseline. autolens_assistant is tied to an autolens version; this file
# records the public API surface (per-module version + a hash of sorted public
# `dir()` names) of the stack the skills/wiki were last validated against. The
# session-start drift-check (CLAUDE.md First-interaction protocol) and
# `--check-version` compare the installed stack against it, so the agent learns
# the API has moved *before* a user hits an AttributeError on a removed symbol.
# ---------------------------------------------------------------------------
BASELINE_REL_PATH = Path("wiki") / "core" / "api_audit_baseline.json"

# Modules whose public surface we hash. The five library roots carry
# `__version__`; `autolens.plot` is hashed too (it is where the plot API lives)
# but inherits the autolens version.
BASELINE_MODULES: tuple[str, ...] = (
    "autonerves",
    "autoarray",
    "autofit",
    "autogalaxy",
    "autolens",
    "autolens.plot",
)
VERSIONED_MODULES: tuple[str, ...] = (
    "autonerves",
    "autoarray",
    "autofit",
    "autogalaxy",
    "autolens",
)

INSTALL_READY = 0
INSTALL_NOT_FOUND = 2
INSTALL_IMPORT_FAILED = 3

# ---------------------------------------------------------------------------
# Aliases. Standardised in AGENTS.md "Conventions". Order is
# length-descending so the regex alternation prefers `autolens` over `al`.
# ---------------------------------------------------------------------------
ALIAS_TO_MODULE: dict[str, str] = {
    "al": "autolens",
    "aplt": "autolens.plot",
    "af": "autofit",
    "ag": "autogalaxy",
    "aa": "autoarray",
    "autonerves": "autonerves",
    "autoarray": "autoarray",
    "autofit": "autofit",
    "autogalaxy": "autogalaxy",
    "autolens": "autolens",
}

_ALIASES_SORTED = sorted(ALIAS_TO_MODULE.keys(), key=len, reverse=True)
ALIAS_RE = re.compile(
    r"(?<![A-Za-z0-9_.])(" + "|".join(_ALIASES_SORTED) + r")((?:\.[A-Za-z_]\w*)+)"
)

CODE_FENCE_RE = re.compile(r"^```(\w*)\s*$")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


# ---------------------------------------------------------------------------
# Idiom deny-list — content-vs-version drift the symbol resolver cannot see.
#
# Both the symbol resolver above and the validate_pyauto_code.py gate only resolve
# *alias-rooted dotted symbols* (`al.AnalysisImaging`) against the installed stack.
# They are structurally blind to a defunct *operator idiom* — `analysis + analysis`,
# `sum(analysis_list)` — where every named symbol still exists but the construction
# itself was removed from the API. The analysis-summing idiom is the canonical case:
# `al.AnalysisImaging(...) + al.AnalysisInterferometer(...)` resolves symbol-by-symbol,
# yet the `+` overload that summed log-likelihoods is gone. The current way to combine
# datasets is the factor graph (`af.AnalysisFactor` + `af.FactorGraphModel`). This
# curated list flags such idioms by *shape* so the audit and the gate stop trusting a
# dead construction just because its tokens still import.
#
# A file opts out (intentional fixtures, this script's own regex strings) by carrying
# the `pyauto-api-gate: skip` marker — same escape hatch the code gate honours.
# ---------------------------------------------------------------------------
IDIOM_SKIP_MARKER = "pyauto-api-gate: skip"

# Region opt-out, finer than the whole-file marker above: every line from one containing
# `pyauto-api-gate: off` through one containing `pyauto-api-gate: on` (both inclusive) is
# blanked before the symbol, call and idiom scans, keeping line numbers intact. For
# documents that must name removed API on purpose (AGENTS.md's "Wrong:" plotter
# example) while the rest of the file stays audited. In Markdown, put the markers in
# inline HTML comments (`<!-- pyauto-api-gate: off -->`) so they do not render.
GATE_OFF_MARKER = "pyauto-api-gate: off"
GATE_ON_MARKER = "pyauto-api-gate: on"


def mask_gate_off_regions(text: str) -> str:
    """Blank every line inside an off/on region (an unclosed region runs to EOF)."""
    if GATE_OFF_MARKER not in text:
        return text
    out: list[str] = []
    off = False
    for line in text.split("\n"):
        if not off and GATE_OFF_MARKER in line:
            off = True
        if off:
            out.append("")
            if GATE_ON_MARKER in line:
                off = False
            continue
        out.append(line)
    return "\n".join(out)


@dataclass(frozen=True)
class IdiomRule:
    name: str
    regex: re.Pattern
    why_defunct: str
    replacement: str
    citation: str


@dataclass(frozen=True)
class IdiomHit:
    rule: IdiomRule
    line_no: int
    line: str


# Seeded with the analysis-summing idiom (the removed multi-dataset combine). Add an
# entry whenever a construction is retired but its constituent symbols survive — i.e.
# whenever a fix is "rewrite the idiom", not "rename the symbol".
DENY_LIST: tuple[IdiomRule, ...] = (
    IdiomRule(
        name="analysis-summing-operator",
        # Both operands of a `+` name an analysis — correct factor-graph code never adds
        # two analyses, it builds an AnalysisFactor list. Catches all three forms the
        # removed idiom appears in:
        #   - bare variables:   analysis_imaging + analysis_interferometer
        #   - constructor calls: al.AnalysisImaging(...) + al.AnalysisInterferometer(...)
        #   - inline-code prose: `AnalysisImaging` + `AnalysisInterferometer`
        # `[\w.]*` allows the alias-dotted form; the optional `\(...\)` (non-greedy,
        # single-line — backtracks through nested parens) skips constructor args between
        # the class name and the operator; `[\s`]*` tolerates markdown backticks.
        regex=re.compile(
            r"\b[\w.]*[Aa]nalysis\w*\s*(?:\([^\n]*?\))?[\s`]*\+[\s`]*[\w.]*[Aa]nalysis\w*"
        ),
        why_defunct=(
            "the `+` operator that summed analysis log-likelihoods to combine datasets "
            "was removed; every named symbol still resolves, so the symbol audit and the "
            "code gate cannot see it"
        ),
        replacement=(
            "wrap each analysis in af.AnalysisFactor(prior_model=..., analysis=...), "
            "combine them with af.FactorGraphModel(*analysis_factor_list), then call "
            "result_list = search.fit(model=factor_graph.global_prior_model, "
            "analysis=factor_graph)"
        ),
        citation=(
            "PyAutoFit:autofit/graphical/declarative/factor/analysis.py; "
            "autolens_workspace:scripts/multi_dataset/start_here.py"
        ),
    ),
    IdiomRule(
        name="analysis-summing-sum-builtin",
        # `sum(analysis...` — folding a list of analyses with the builtin relied on the
        # same removed Analysis.__add__.
        regex=re.compile(r"\bsum\(\s*analysis"),
        why_defunct=(
            "sum(analysis_list) folded a list of analyses into one summed-likelihood "
            "analysis via the removed Analysis.__add__"
        ),
        replacement=(
            "build an analysis_factor_list of af.AnalysisFactor(prior_model=..., "
            "analysis=...) and pass it to af.FactorGraphModel(*analysis_factor_list)"
        ),
        citation=(
            "PyAutoFit:autofit/graphical/declarative/collection.py; "
            "autolens_workspace:scripts/multi_dataset/start_here.py"
        ),
    ),
)


def lint_idioms(text: str) -> list[IdiomHit]:
    """Return every deny-list idiom hit in `text` (line-numbered).

    Whole-text, line-by-line scan: an idiom is drift whether it appears in a fenced
    code block, an inline span, or a prose sentence, so we do not split Markdown here.
    A file carrying the skip marker opts out entirely (returns no hits)."""
    if IDIOM_SKIP_MARKER in text:
        return []
    hits: list[IdiomHit] = []
    for i, line in enumerate(mask_gate_off_regions(text).splitlines(), start=1):
        for rule in DENY_LIST:
            if rule.regex.search(line):
                hits.append(IdiomHit(rule=rule, line_no=i, line=line.strip()))
    return hits


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Symbol:
    alias: str
    chain: tuple[str, ...]

    @property
    def text(self) -> str:
        return self.alias + "." + ".".join(self.chain)


@dataclass
class Resolution:
    status: str  # "ok" | "missing_attr" | "import_failed"
    resolved_depth: int = 0
    parent_repr: str = ""
    candidates: list[str] = field(default_factory=list)
    error: str = ""
    # The resolved object itself (status "ok" only), kept so call-signature checks
    # can inspect it without a second attribute walk. Excluded from repr/compare.
    obj: object = field(default=None, repr=False, compare=False)


@dataclass
class CallIssue:
    """A call to a resolvable PyAuto* callable whose arguments its installed
    signature cannot accept (e.g. `aplt.subplot_fit_imaging(output_filename=...)`)."""

    line_no: int
    call: str  # dotted callable, e.g. "aplt.subplot_fit_imaging"
    problem: str  # e.g. "unexpected keyword argument `output_filename`"
    hint: str  # accepted names / closest match


@dataclass
class InstallationCheck:
    status: str  # "ready" | "not_installed" | "import_failed"
    python: str
    prefix: str
    versions: dict[str, str] = field(default_factory=dict)
    locations: dict[str, str] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    install_kind: str = "unknown"
    cache_defaults: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def iter_markdown_segments(text: str) -> Iterable[tuple[str, str]]:
    """Yield ("code"|"prose", segment_text) for each segment of `text`.

    Fenced ``` blocks count as code (regardless of language tag). Everything
    else is prose. Inline-code spans inside prose are surfaced separately by
    INLINE_CODE_RE so we still catch `` `al.Foo.bar` `` references inside
    explanatory paragraphs.
    """
    in_code = False
    buf: list[str] = []

    for line in text.splitlines():
        if CODE_FENCE_RE.match(line.rstrip()):
            if buf:
                yield ("code" if in_code else "prose", "\n".join(buf))
                buf = []
            in_code = not in_code
            continue
        buf.append(line)

    if buf:
        yield ("code" if in_code else "prose", "\n".join(buf))


def extract_symbols(text: str) -> dict[Symbol, set[str]]:
    """Return {symbol: {"code", "prose"}} for one file's contents."""
    out: dict[Symbol, set[str]] = {}

    for kind, segment in iter_markdown_segments(text):
        if kind == "code":
            for m in ALIAS_RE.finditer(segment):
                sym = Symbol(m.group(1), tuple(m.group(2).lstrip(".").split(".")))
                out.setdefault(sym, set()).add("code")
        else:
            for inline in INLINE_CODE_RE.findall(segment):
                for m in ALIAS_RE.finditer(inline):
                    sym = Symbol(m.group(1), tuple(m.group(2).lstrip(".").split(".")))
                    out.setdefault(sym, set()).add("prose")
    return out


def extract_symbols_code(text: str) -> dict[Symbol, set[str]]:
    """Return {symbol: {"code"}} for a raw Python source file.

    Unlike `extract_symbols` (which splits Markdown into code/prose), a `.py`
    file is code throughout, so we run the alias regex over the whole text. Used
    for the `scripts` scope, which audits generated pipelines under `scripts/`
    where stale symbols like `al.Kernel2D` actually execute.
    """
    out: dict[Symbol, set[str]] = {}
    for m in ALIAS_RE.finditer(text):
        sym = Symbol(m.group(1), tuple(m.group(2).lstrip(".").split(".")))
        out.setdefault(sym, set()).add("code")
    return out


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------
_module_cache: dict[str, ModuleType | None] = {}
_import_errors: dict[str, str] = {}


def import_root(alias: str) -> ModuleType | None:
    target = ALIAS_TO_MODULE[alias]
    if target in _module_cache:
        return _module_cache[target]
    try:
        mod = importlib.import_module(target)
    except Exception as e:  # noqa: BLE001
        _module_cache[target] = None
        _import_errors[target] = repr(e)
        return None
    _module_cache[target] = mod
    return mod


def resolve(sym: Symbol) -> Resolution:
    root = import_root(sym.alias)
    if root is None:
        return Resolution(
            status="import_failed",
            error=_import_errors.get(ALIAS_TO_MODULE[sym.alias], "import failed"),
        )

    current = root
    for i, attr in enumerate(sym.chain):
        try:
            current = getattr(current, attr)
        except AttributeError:
            if isinstance(current, ModuleType):
                module_name = f"{current.__name__}.{attr}"
                try:
                    current = importlib.import_module(module_name)
                    _module_cache[module_name] = current
                    continue
                except Exception:  # noqa: BLE001
                    pass
            candidates = difflib.get_close_matches(attr, dir(current), n=3, cutoff=0.6)
            for c in _cross_module_candidates(attr):
                if c not in candidates:
                    candidates.append(c)
            return Resolution(
                status="missing_attr",
                resolved_depth=i,
                parent_repr=_short_repr(current),
                candidates=candidates,
            )
        except Exception as e:  # noqa: BLE001
            # A pathological attribute access (recursive __getattr__, RecursionError,
            # a property that raises) must never crash the whole audit — treat it as
            # an unresolved error row instead.
            return Resolution(
                status="error", resolved_depth=i, error=f"{type(e).__name__}: {e}"[:160]
            )

    return Resolution(
        status="ok",
        resolved_depth=len(sym.chain),
        parent_repr=_short_repr(current),
        obj=current,
    )


# ---------------------------------------------------------------------------
# Call-signature checks
#
# Symbol resolution proves `aplt.subplot_fit_imaging` exists; it cannot see that
# `aplt.subplot_fit_imaging(fit=fit, output_filename="fit")` passes a keyword the
# installed function does not take (a TypeError at run time). For every call whose
# callee is an alias-rooted dotted name (`al.X(...)`, `aplt.f(...)`, `af.X.y(...)`),
# we resolve the callee, read `inspect.signature`, and flag
#   - a keyword argument the signature does not name (unless it takes **kwargs), and
#   - more positional arguments than it accepts (unless it takes *args).
# Deliberately conservative: callees we cannot resolve, inspect, or that accept
# **kwargs / *args are skipped, `**mapping` / `*seq` unpacking is never judged, and
# calls on runtime objects (`fit.foo(...)`, `al.cosmo.Planck15().bar(...)`) are out of
# reach of a static check. Source that does not parse as Python is skipped.
# ---------------------------------------------------------------------------
_MAX_ACCEPTED_LISTED = 10


def _dotted_callee(node: ast.AST) -> Optional[Symbol]:
    """`al.Mask2D.circular` -> Symbol("al", ("Mask2D", "circular")); else None."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name) and node.id in ALIAS_TO_MODULE and parts:
        return Symbol(node.id, tuple(reversed(parts)))
    return None


_signature_cache: dict[int, Optional[inspect.Signature]] = {}


def _signature_of(obj: object) -> Optional[inspect.Signature]:
    key = id(obj)
    if key not in _signature_cache:
        try:
            _signature_cache[key] = inspect.signature(obj)  # type: ignore[arg-type]
        except (TypeError, ValueError):  # builtins, C extensions, odd metaclasses
            _signature_cache[key] = None
        except Exception:  # noqa: BLE001 - never let introspection crash the audit
            _signature_cache[key] = None
    return _signature_cache[key]


def _accepted_hint(names: list[str], bad: str) -> str:
    close = difflib.get_close_matches(bad, names, n=2, cutoff=0.6)
    shown = names[:_MAX_ACCEPTED_LISTED]
    more = "" if len(names) <= _MAX_ACCEPTED_LISTED else f", … (+{len(names) - len(shown)})"
    hint = "accepts: " + (", ".join(shown) + more if shown else "no keyword arguments")
    if close:
        hint = "did you mean " + " / ".join(f"`{c}`" for c in close) + "? " + hint
    return hint


def check_call_signatures(text: str, *, line_offset: int = 0) -> list[CallIssue]:
    """Return argument mismatches for alias-rooted PyAuto* calls in Python `text`.

    `line_offset` shifts reported line numbers (used for Markdown code blocks).
    Returns [] for text that is not valid Python."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    issues: list[CallIssue] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        sym = _dotted_callee(node.func)
        if sym is None:
            continue
        res = resolve(sym)
        # A missing symbol is reported by the symbol check; don't double-report it.
        if res.status != "ok" or not callable(res.obj):
            continue
        sig = _signature_of(res.obj)
        if sig is None:
            continue
        params = list(sig.parameters.values())
        kinds = {p.kind for p in params}
        line_no = getattr(node, "lineno", 0) + line_offset

        if inspect.Parameter.VAR_KEYWORD not in kinds:
            keyword_names = [
                p.name
                for p in params
                if p.kind
                in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
            ]
            for kw in node.keywords:
                if kw.arg is None or kw.arg in keyword_names:
                    continue  # `**mapping` unpacking is never judged
                issues.append(
                    CallIssue(
                        line_no=line_no,
                        call=sym.text,
                        problem=f"unexpected keyword argument `{kw.arg}`",
                        hint=_accepted_hint(keyword_names, kw.arg),
                    )
                )

        starred = any(isinstance(a, ast.Starred) for a in node.args)
        if inspect.Parameter.VAR_POSITIONAL not in kinds and not starred:
            n_positional = sum(
                p.kind
                in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                for p in params
            )
            if len(node.args) > n_positional:
                issues.append(
                    CallIssue(
                        line_no=line_no,
                        call=sym.text,
                        problem=(
                            f"{len(node.args)} positional arguments given, "
                            f"at most {n_positional} accepted"
                        ),
                        hint=f"signature: {sym.text}{sig}"[:240],
                    )
                )
    return issues


def iter_markdown_python(text: str) -> Iterable[tuple[int, str]]:
    """Yield (line_offset, python_source) for the Python a Markdown file cites:
    fenced blocks tagged `python`/`py` or untagged, plus inline code spans that
    contain an alias-rooted call. Offsets make reported line numbers file-relative.
    Blocks in other languages (bash, yaml, text, …) are not Python and are skipped."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = CODE_FENCE_RE.match(lines[i].rstrip())
        if m:
            lang = m.group(1).lower()
            start = i + 1
            j = start
            while j < len(lines) and not CODE_FENCE_RE.match(lines[j].rstrip()):
                j += 1
            if lang in ("", "python", "py", "python3"):
                yield start, "\n".join(lines[start:j])
            i = j + 1
            continue
        for span in INLINE_CODE_RE.findall(lines[i]):
            if "(" in span and ALIAS_RE.search(span):
                yield i, span
        i += 1


def check_call_signatures_markdown(text: str) -> list[CallIssue]:
    issues: list[CallIssue] = []
    for offset, source in iter_markdown_python(text):
        issues.extend(check_call_signatures(source, line_offset=offset))
    return issues


def _short_repr(obj) -> str:
    mod = getattr(obj, "__module__", None)
    name = (
        getattr(obj, "__name__", None) or getattr(obj, "__class__", type(obj)).__name__
    )
    if mod and name:
        return f"{mod}.{name}"
    return repr(obj)[:80]


_cross_cache: dict[str, list[str]] = {}


def _cross_module_candidates(leaf: str) -> list[str]:
    """Look for `leaf` anywhere across the five PyAuto* roots + one submodule level."""
    if leaf in _cross_cache:
        return _cross_cache[leaf]
    hits: list[str] = []
    for mod_name in ("autonerves", "autoarray", "autofit", "autogalaxy", "autolens"):
        root = _module_cache.get(mod_name)
        if root is None:
            try:
                root = importlib.import_module(mod_name)
                _module_cache[mod_name] = root
            except Exception:  # noqa: BLE001
                continue
        if hasattr(root, leaf):
            hits.append(f"{mod_name}.{leaf}")
        for sub in dir(root):
            if sub.startswith("_"):
                continue
            try:
                sub_obj = getattr(root, sub)
            except Exception:  # noqa: BLE001
                continue
            if isinstance(sub_obj, ModuleType) and hasattr(sub_obj, leaf):
                hits.append(f"{mod_name}.{sub}.{leaf}")
    _cross_cache[leaf] = hits
    return hits


# ---------------------------------------------------------------------------
# File-set selection
# ---------------------------------------------------------------------------
def select_files(root: Path, scope: str) -> list[Path]:
    skills = sorted((root / "skills").glob("*.md"))
    wiki_api = sorted((root / "wiki" / "core" / "api").glob("*.md"))
    wiki_stack = sorted((root / "wiki" / "core" / "stack").glob("*.md"))
    # User pipelines + agent scripts — the .py files where stale symbols actually
    # execute (e.g. a script written against the old `al.Kernel2D`). Scanned
    # recursively because scripts/ mirrors autolens_workspace's nested layout.
    # The assistant's own tooling lives in autoassistant/ (not scanned): it
    # contains alias-pattern text (regexes, module-name strings, docstrings) that
    # isn't real API usage.
    tooling = {"audit_skill_apis.py", "refresh_api_docs.py", "test_api_gate.py"}
    scripts = [
        p for p in sorted((root / "scripts").rglob("*.py")) if p.name not in tooling
    ]
    # The MCP server (autoassistant/mcp/) is the one part of autoassistant/ with
    # real API usage rather than alias-pattern text, so it joins the scan.
    scripts += sorted((root / "autoassistant" / "mcp").glob("*.py"))
    # The agent instructions every harness loads first: their examples are copied
    # verbatim, so a stale call there is the most-copied stale call of all.
    instructions = [p for p in (root / "AGENTS.md",) if p.exists()]
    if scope == "instructions":
        return instructions
    if scope == "skills":
        return skills
    if scope == "wiki":
        return wiki_api + wiki_stack
    if scope == "scripts":
        return scripts
    if scope == "all":
        return instructions + skills + wiki_api + wiki_stack + scripts
    raise SystemExit(f"unknown scope: {scope!r}")


def select_idiom_files(root: Path) -> list[Path]:
    """Files the idiom lint scans: every `skills/` + `wiki/` Markdown page and every
    `scripts/` Python file.

    Deliberately broader than `select_files`' API-doc scope: a defunct idiom can sit
    in any prose page (e.g. `wiki/core/concepts/multi_wavelength.md`), not only the
    API tables under `wiki/core/api`+`stack`. This script's own tooling is excluded —
    it holds the deny-list regex strings as text, not as executed/ documented idioms."""
    tooling = {"audit_skill_apis.py", "refresh_api_docs.py", "test_api_gate.py"}
    md = [p for p in (root / "AGENTS.md",) if p.exists()]
    md += sorted((root / "skills").glob("*.md")) + sorted((root / "wiki").rglob("*.md"))
    py = [p for p in sorted((root / "scripts").rglob("*.py")) if p.name not in tooling]
    py += sorted((root / "autoassistant" / "mcp").glob("*.py"))
    return md + py


def run_idiom_lint(root: Path) -> int:
    """Scan skills/ + wiki/ + scripts/ for deny-list idioms. Exit 1 on any hit.

    Self-contained — needs neither `sources.yaml` nor the installed stack, so it is
    safe to run in a packaged-install CI job that has no source checkout."""
    files = select_idiom_files(root)
    by_file: list[tuple[Path, list[IdiomHit]]] = []
    total = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits = lint_idioms(text)
        if hits:
            by_file.append((f, hits))
            total += len(hits)

    if total == 0:
        print(
            f"[idiom] clean — scanned {len(files)} files, no defunct idioms.",
            file=sys.stderr,
        )
        return 0

    print(
        f"[idiom] {total} defunct idiom(s) across {len(by_file)} file(s):",
        file=sys.stderr,
    )
    for f, hits in by_file:
        rel = f.relative_to(root)
        for hit in hits:
            print(f"  {rel}:{hit.line_no}  [{hit.rule.name}]  {hit.line}", file=sys.stderr)
            print(f"      why: {hit.rule.why_defunct}", file=sys.stderr)
            print(f"      use: {hit.rule.replacement}", file=sys.stderr)
            print(f"      ref: {hit.rule.citation}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def render_report(
    *,
    versions: dict[str, str],
    occurrences_by_file: dict[Path, dict[Symbol, set[str]]],
    resolutions: dict[Symbol, Resolution],
    scope: str,
    root: Path,
    call_issues_by_file: Optional[dict[Path, list[CallIssue]]] = None,
) -> str:
    call_issues_by_file = call_issues_by_file or {}
    n_call = sum(len(v) for v in call_issues_by_file.values())
    today = dt.date.today().isoformat()
    total_symbols = sum(len(d) for d in occurrences_by_file.values())
    unique_symbols = len(resolutions)
    missing = [s for s, r in resolutions.items() if r.status != "ok"]
    files_with_misses = {
        f
        for f, d in occurrences_by_file.items()
        if any(resolutions[s].status != "ok" for s in d)
    }

    lines: list[str] = []
    lines.append(f"# Skill API audit — {today}")
    lines.append("")
    lines.append(f"Scope: `{scope}`. Root: `{root}`.")
    lines.append("")
    lines.append("## Installed versions")
    lines.append("")
    if versions:
        for name, ver in sorted(versions.items()):
            lines.append(f"- `{name}` = `{ver}`")
    else:
        lines.append(
            "_No PyAuto\\* libraries importable. Activate the venv (`source activate.sh`) and re-run._"
        )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    lines.append(f"| files scanned | {len(occurrences_by_file)} |")
    lines.append(f"| symbol occurrences (file × symbol) | {total_symbols} |")
    lines.append(f"| unique symbols | {unique_symbols} |")
    lines.append(f"| ok | {unique_symbols - len(missing)} |")
    lines.append(f"| missing or import-failed | {len(missing)} |")
    lines.append(f"| files affected by misses | {len(files_with_misses)} |")
    lines.append(f"| call-argument mismatches | {n_call} |")
    lines.append("")

    if call_issues_by_file:
        lines.append("## Call-argument mismatches")
        lines.append("")
        lines.append(
            "Calls whose callee resolves but whose keyword or positional arguments the "
            "installed signature does not accept (a `TypeError` at run time)."
        )
        lines.append("")
        lines.append("| file:line | call | problem | hint |")
        lines.append("|---|---|---|---|")
        for f in sorted(call_issues_by_file):
            rel = f.relative_to(root)
            for issue in call_issues_by_file[f]:
                hint = issue.hint.replace("|", "\\|")
                lines.append(
                    f"| `{rel}:{issue.line_no}` | `{issue.call}` | {issue.problem} | {hint} |"
                )
        lines.append("")

    if not missing:
        lines.append(
            "All cited symbols resolve cleanly."
            + ("" if n_call else " No drift detected.")
        )
        lines.append("")
        return "\n".join(lines)

    lines.append("## Misses by file")
    lines.append("")
    for f in sorted(occurrences_by_file):
        bad = [
            (s, occurrences_by_file[f][s], resolutions[s])
            for s in occurrences_by_file[f]
            if resolutions[s].status != "ok"
        ]
        if not bad:
            continue
        rel = f.relative_to(root)
        lines.append(f"### `{rel}`")
        lines.append("")
        lines.append("| symbol | status | resolved up to | suggestions | seen in |")
        lines.append("|---|---|---|---|---|")
        for sym, contexts, res in sorted(bad, key=lambda x: x[0].text):
            ctx = "/".join(sorted(contexts))
            if res.status == "missing_attr":
                tail = ".".join(sym.chain[res.resolved_depth :])
                status = f"missing `.{tail}`"
                parent = res.parent_repr
            elif res.status == "error":
                status = "error"
                parent = f"`{res.error}`"
            else:
                status = "import_failed"
                parent = f"`{res.error}`"
            suggestions = (
                ", ".join(f"`{c}`" for c in res.candidates)
                if res.candidates
                else "_(none found)_"
            )
            lines.append(
                f"| `{sym.text}` | {status} | `{parent}` | {suggestions} | {ctx} |"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def gather_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("autonerves", "autoarray", "autofit", "autogalaxy", "autolens"):
        try:
            mod = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001
            out[name] = f"NOT INSTALLED ({e!r})"
            continue
        ver = getattr(mod, "__version__", "(no __version__)")
        out[name] = str(ver)
    return out


# ---------------------------------------------------------------------------
# Installation preflight
# ---------------------------------------------------------------------------
def _prepare_import_caches() -> dict[str, str]:
    """Give import-time caches writable defaults without overriding user choices."""
    defaults = {
        "NUMBA_CACHE_DIR": str(Path(tempfile.gettempdir()) / "numba_cache"),
        "MPLCONFIGDIR": str(Path(tempfile.gettempdir()) / "matplotlib"),
    }
    applied: dict[str, str] = {}
    for name, value in defaults.items():
        if name not in os.environ:
            Path(value).mkdir(parents=True, exist_ok=True)
            os.environ[name] = value
            applied[name] = value
    return applied


def _installation_kind(module_locations: dict[str, str]) -> str:
    """Best-effort provenance; credentials and environment managers stay external."""
    try:
        distribution = importlib.metadata.distribution("autolens")
        direct_url_text = distribution.read_text("direct_url.json")
        if direct_url_text:
            direct_url = json.loads(direct_url_text)
            if direct_url.get("dir_info", {}).get("editable"):
                return "editable install"
            if str(direct_url.get("url", "")).startswith("file:"):
                return "local source install"
    except (importlib.metadata.PackageNotFoundError, json.JSONDecodeError):
        pass

    location = module_locations.get("autolens", "")
    if "site-packages" in location or "dist-packages" in location:
        return "packaged install (pip/conda provenance not distinguishable)"
    if location:
        return "source checkout or PYTHONPATH install"
    return "unknown"


def inspect_installation() -> InstallationCheck:
    """Inspect the active interpreter without assuming the PyAuto* stack works."""
    cache_defaults = _prepare_import_caches()
    versions: dict[str, str] = {}
    locations: dict[str, str] = {}
    missing: list[str] = []
    errors: dict[str, str] = {}

    for name in VERSIONED_MODULES:
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, AttributeError, ValueError):
            spec = None
        if spec is None:
            missing.append(name)
            continue
        try:
            module = importlib.import_module(name)
        except Exception as error:  # noqa: BLE001
            errors[name] = f"{type(error).__name__}: {error}"
            continue
        versions[name] = str(getattr(module, "__version__", "(no __version__)"))
        module_file = getattr(module, "__file__", None)
        if module_file:
            locations[name] = str(Path(module_file).resolve())

    if errors:
        status = "import_failed"
    elif missing:
        status = "not_installed"
    else:
        status = "ready"

    return InstallationCheck(
        status=status,
        python=sys.executable,
        prefix=sys.prefix,
        versions=versions,
        locations=locations,
        missing=missing,
        errors=errors,
        install_kind=_installation_kind(locations),
        cache_defaults=cache_defaults,
    )


def render_installation_check(check: InstallationCheck) -> str:
    lines = [
        f"[install] {check.status.replace('_', ' ').upper()}",
        f"  python: {check.python}",
        f"  environment: {check.prefix}",
    ]
    if check.versions:
        versions = ", ".join(
            f"{name}={version}" for name, version in check.versions.items()
        )
        lines.append(f"  versions: {versions}")
    if check.locations.get("autolens"):
        lines.append(f"  autolens: {check.locations['autolens']}")
        lines.append(f"  install type: {check.install_kind}")
    if check.missing:
        lines.append(f"  missing from this interpreter: {', '.join(check.missing)}")
    # Group identical errors: with e.g. a workspace-version mismatch, autofit,
    # autogalaxy and autolens all fail with the same multi-paragraph message —
    # print it once, naming every module it applies to.
    grouped: dict[str, list[str]] = {}
    for name, error in check.errors.items():
        grouped.setdefault(error, []).append(name)
    for error, names in grouped.items():
        lines.append(f"  {', '.join(names)} import failed: {error}")
    if check.cache_defaults:
        defaults = ", ".join(
            f"{name}={value}" for name, value in check.cache_defaults.items()
        )
        lines.append(f"  temporary cache defaults: {defaults}")

    if check.status != "ready":
        lines.extend(
            [
                "  Activate the project's environment (`source activate.sh`) if it exists.",
                "  Otherwise use `skills/al_setup_environment.md`; do not install into an",
                "  unrelated system Python environment.",
            ]
        )
    return "\n".join(lines)


def check_installation(*, verbose_ready: bool = True) -> int:
    check = inspect_installation()
    if check.status != "ready" or verbose_ready:
        stream = sys.stdout if check.status == "ready" else sys.stderr
        print(render_installation_check(check), file=stream)
    return {
        "ready": INSTALL_READY,
        "not_installed": INSTALL_NOT_FOUND,
        "import_failed": INSTALL_IMPORT_FAILED,
    }[check.status]


# ---------------------------------------------------------------------------
# API baseline — version pin + public-surface hash
# ---------------------------------------------------------------------------
def _public_names(mod: ModuleType) -> list[str]:
    return sorted(n for n in dir(mod) if not n.startswith("_"))


def _api_hash(mod: ModuleType) -> str:
    return hashlib.sha256("\n".join(_public_names(mod)).encode("utf-8")).hexdigest()


def compute_baseline() -> dict:
    """Snapshot the installed stack: per-module version + public-API-surface hash.

    Raises SystemExit if any library is missing — a baseline must only ever be
    written against a fully installed stack, or it would bake in `import_failed`
    placeholders that the drift-check would then read as real drift.
    """
    versions: dict[str, str] = {}
    for name in VERSIONED_MODULES:
        try:
            mod = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001
            sys.exit(
                f"cannot write baseline: {name} not importable ({e!r}). "
                f"Activate the venv (source activate.sh) and retry."
            )
        versions[name] = str(getattr(mod, "__version__", "(no __version__)"))

    api_surface: dict[str, dict] = {}
    for name in BASELINE_MODULES:
        mod = importlib.import_module(
            name
        )  # already known importable (plot via autolens)
        names = _public_names(mod)
        api_surface[name] = {"hash": _api_hash(mod), "n_symbols": len(names)}

    return {
        "_comment": "API baseline for autolens_assistant - see autoassistant/audit_skill_apis.py "
        "and skills/al_audit_skill_apis.md. Regenerate with --write-baseline.",
        "generated": dt.date.today().isoformat(),
        "versions": versions,
        "api_surface": api_surface,
    }


def write_baseline(root: Path) -> Path:
    baseline = compute_baseline()
    path = root / BASELINE_REL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    return path


def render_symbol_dump() -> str:
    """Render the installed stack's public API surface as Markdown.

    A generated page an agent on a harness without the PreToolUse code gate can
    grep to check that a symbol exists, rather than trusting prose that has to
    be hand-maintained. The baseline JSON records only a hash and a count; this
    renders the names themselves.

    Raises SystemExit if the stack is not importable — a symbol dump must never
    be written from a partial import, or it would advertise a truncated API
    surface as complete.
    """
    versions: dict[str, str] = {}
    for name in VERSIONED_MODULES:
        try:
            mod = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001
            sys.exit(
                f"cannot dump symbols: {name} not importable ({e!r}). "
                f"Activate the venv (source activate.sh) and retry."
            )
        versions[name] = str(getattr(mod, "__version__", "(no __version__)"))

    lines: list[str] = [
        "# PyAuto* public API surface (generated)",
        "",
        "Generated by `python autoassistant/audit_skill_apis.py --dump-symbols`.",
        "**Do not hand-edit.** This is the public `dir()` surface of the exact stack",
        "the assistant content was validated against — use it to check whether a symbol",
        "you are about to write actually exists.",
        "",
        # Deliberately no generation date: if this page is committed and diffed,
        # a rendered-on date would make it differ every day after it was written.
        # The stack version below is the provenance that actually matters — it
        # changes when the surface changes, and not otherwise.
        "- Stack versions: "
        + ", ".join(f"`{k}` {v}" for k, v in sorted(versions.items())),
        "",
        "> A name appearing here means the symbol exists; it does **not** document its",
        "> signature. For call syntax, mirror the matching `skills/` example.",
        "",
    ]

    total = 0
    for name in BASELINE_MODULES:
        mod = importlib.import_module(name)
        names = _public_names(mod)
        total += len(names)
        alias = {
            "autolens": "al",
            "autolens.plot": "aplt",
            "autogalaxy": "ag",
            "autoarray": "aa",
            "autofit": "af",
        }.get(name)
        heading = f"## `{name}`" + (f" (alias `{alias}`)" if alias else "")
        lines += [heading, "", f"{len(names)} public symbols.", ""]
        lines += [", ".join(f"`{n}`" for n in names), ""]

    lines += [f"**Total: {total} public symbols across {len(BASELINE_MODULES)} modules.**", ""]
    return "\n".join(lines)


def dump_symbols(out: Optional[str]) -> int:
    """Write (or print) the public-API-surface Markdown page."""
    text = render_symbol_dump()
    if out:
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")
    else:
        print(text)
    return 0


def check_version(root: Path) -> int:
    """Compare the installed stack's public API surface against the committed baseline.

    Returns 0 when the public-API-surface hashes match, 1 on any hash drift (or a
    missing baseline). Prints a short human-readable summary. Intentionally cheap
    — no Markdown scan — so it is safe to run at session start.

    The per-module ``__version__`` equality this check used to *gate* on was
    dropped (PyAutoMind build-chain #155 Phase 4 task 3). Since PyAutoConf#119 /
    PyAutoBuild#121 a release no longer commits the ``__version__`` stamp back to
    the library ``main``, so a source checkout reports a frozen stamp while the
    baseline is wheel-derived — a structurally-permanent version mismatch,
    independent of release cadence, that the API-surface hash already proves is
    spurious (the public surface is byte-identical). Versions are still shown for
    context; only the API-surface hash gates.
    """
    path = root / BASELINE_REL_PATH
    if not path.exists():
        print(
            f"[drift] no baseline at {path} — run `--write-baseline` first.",
            file=sys.stderr,
        )
        return 1

    baseline = json.loads(path.read_text(encoding="utf-8"))
    current = compute_baseline()

    # Informational only — a version-stamp difference no longer gates (frozen
    # source stamps vs a wheel-derived baseline false-positive; the API-surface
    # hash is the real signal).
    version_changes = [
        (m, baseline["versions"].get(m, "(absent)"), current["versions"][m])
        for m in VERSIONED_MODULES
        if baseline["versions"].get(m) != current["versions"][m]
    ]
    hash_drift = [
        m
        for m in BASELINE_MODULES
        if baseline["api_surface"].get(m, {}).get("hash")
        != current["api_surface"][m]["hash"]
    ]

    if not hash_drift:
        note = ""
        if version_changes:
            note = (
                " (version stamp differs but public API surface is identical: "
                + ", ".join(f"{m} {old}->{new}" for m, old, new in version_changes)
                + ")"
            )
        print(
            f"[drift] clean — installed public API surface matches baseline "
            f"(autolens {current['versions']['autolens']}, generated {baseline.get('generated')}){note}."
        )
        return 0

    print(
        "[drift] API DRIFT vs baseline "
        f"(baseline generated {baseline.get('generated')}):",
        file=sys.stderr,
    )
    print(f"  - public API surface changed: {', '.join(hash_drift)}", file=sys.stderr)
    for m, old, new in version_changes:
        print(f"  - {m} version: {old} -> {new} (informational)", file=sys.stderr)
    print(
        "  The skills/wiki were validated against the baseline. Run `--scope all` to audit "
        "drift and `--write-baseline` to re-pin once fixed.",
        file=sys.stderr,
    )
    return 1


# ---------------------------------------------------------------------------
# Provenance enforcement — bind content to the version it was validated against.
#
# The version baseline hashes the *public API surface*; the idiom lint catches dead
# *constructions*. Neither verifies that a wiki/core page's `pinned_commit` is honest.
# The original drift shipped precisely because pins were bumped without re-validating
# content: a freshly stamped page carried a dead idiom. This check closes that gap with
# two independent signals:
#
#   (a) Commit reachability (git mode) — when a git checkout of the cited project is
#       resolvable, every sha-shaped `pinned_commit` must be a real commit object AND an
#       ancestor of (or equal to) HEAD. A forged sha, or one rewritten out of history,
#       FAILS. Pins to a moving ref (`main`) are flagged but not failed — they are
#       "unpinned", a nudge to re-pin, not a forgery.
#
#   (b) Content binding (git-free, CI-safe) — a `content_sha256` frontmatter field that
#       the refresh (`--write-provenance`) stamps with a hash of the page body at
#       validation time. If a page declares it and the body no longer matches, the page
#       was edited after stamping without re-validation → FAIL. Missing field → "not
#       provenance-stamped" warning. This needs no source checkout, so it is the arm that
#       runs in a packaged-install CI job where the git-mode checks are skipped.
#
# Severity: ERROR (exit 1) for a forged/divergent pin or a content_sha256 mismatch; WARN
# (exit 0 unless --strict) for an unpinned `main` ref or a missing stamp. This lets the
# release/PR check go red on genuine forgery/staleness without nuking the 50+ legacy
# `main`-pinned pages that predate the discipline.
# ---------------------------------------------------------------------------
PROJECT_IMPORT: dict[str, str] = {
    "PyAutoNerves": "autonerves",
    "PyAutoArray": "autoarray",
    "PyAutoFit": "autofit",
    "PyAutoGalaxy": "autogalaxy",
    "PyAutoLens": "autolens",
}
_SHA_RE = re.compile(r"[0-9a-f]{7,40}\Z")
_MOVING_REFS = {"main", "master", "head"}
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)

_repo_cache: dict[str, Optional[Path]] = {}


def split_frontmatter(text: str) -> tuple[Optional[str], str]:
    """Return (frontmatter_yaml, body). `(None, text)` when the file has no leading
    `---` frontmatter block. Only the *leading* block is treated as frontmatter — a
    fenced ```yaml example in the body (e.g. a page documenting the schema) is left in
    the body and never parsed as provenance."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def _body_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=15,
    )


def _project_repo(project: str) -> Optional[Path]:
    """Resolve a git checkout of `project`: a `sources/<project>/` clone, else the git
    toplevel enclosing the installed package. None when neither exists (packaged install
    with no source tree — the caller then skips git-mode checks)."""
    if project in _repo_cache:
        return _repo_cache[project]
    result: Optional[Path] = None
    imp = PROJECT_IMPORT.get(project)
    if imp:
        try:
            mod = importlib.import_module(imp)
            pkg_dir = Path(mod.__file__).resolve().parent
            proc = _git(pkg_dir, "rev-parse", "--show-toplevel")
            if proc.returncode == 0:
                result = Path(proc.stdout.strip())
        except Exception:  # noqa: BLE001
            result = None
    _repo_cache[project] = result
    return result


@dataclass
class ProvenanceIssue:
    page: Path
    severity: str  # "error" | "warn"
    message: str


def _check_page_provenance(page: Path, root: Path) -> list[ProvenanceIssue]:
    text = page.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        return []  # no frontmatter — not a provenance-bearing page
    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:  # noqa: BLE001
        return [ProvenanceIssue(page, "error", f"unparseable frontmatter: {e}")]
    if not isinstance(meta, dict):
        return []

    issues: list[ProvenanceIssue] = []

    # (b) Content binding.
    declared = meta.get("content_sha256")
    if declared:
        actual = _body_hash(body)
        if declared != actual:
            issues.append(
                ProvenanceIssue(
                    page,
                    "error",
                    f"content_sha256 mismatch — body edited after stamping "
                    f"(declared {str(declared)[:12]}…, actual {actual[:12]}…). "
                    f"Re-validate against the pinned commit, then --write-provenance.",
                )
            )
    else:
        issues.append(
            ProvenanceIssue(
                page,
                "warn",
                "no content_sha256 — content not provenance-stamped "
                "(run --write-provenance after validating against the pinned commit).",
            )
        )

    # (a) Commit reachability.
    for source in meta.get("sources") or []:
        if not isinstance(source, dict):
            continue
        project = source.get("project")
        pin = str(source.get("pinned_commit", "")).strip()
        if not project or not pin:
            issues.append(
                ProvenanceIssue(page, "warn", f"source missing project/pinned_commit")
            )
            continue
        repo = _project_repo(project)
        if repo is None:
            issues.append(
                ProvenanceIssue(
                    page,
                    "warn",
                    f"{project}: no git checkout resolvable — commit checks skipped "
                    f"(packaged install?).",
                )
            )
            continue
        if pin.lower() in _MOVING_REFS:
            issues.append(
                ProvenanceIssue(
                    page,
                    "warn",
                    f"{project}: pinned to moving ref '{pin}', not a commit — re-pin to a sha.",
                )
            )
            continue
        if not _SHA_RE.match(pin):
            # A tag or other named ref: acceptable iff it resolves in the repo.
            if _git(repo, "rev-parse", "--verify", "--quiet", f"{pin}^{{commit}}").returncode != 0:
                issues.append(
                    ProvenanceIssue(
                        page, "error", f"{project}: pinned ref '{pin}' does not resolve."
                    )
                )
            continue
        if _git(repo, "cat-file", "-t", pin).stdout.strip() != "commit":
            issues.append(
                ProvenanceIssue(
                    page,
                    "error",
                    f"{project}: pinned_commit {pin[:12]}… is not a real commit "
                    f"(forged or unreachable).",
                )
            )
        elif _git(repo, "merge-base", "--is-ancestor", pin, "HEAD").returncode != 0:
            issues.append(
                ProvenanceIssue(
                    page,
                    "error",
                    f"{project}: pinned_commit {pin[:12]}… is not an ancestor of HEAD "
                    f"(stale or divergent pin).",
                )
            )
    return issues


def check_provenance(root: Path, *, strict: bool = False) -> int:
    """Verify every wiki/core page's provenance. Exit 1 on any ERROR (or, under
    --strict, any WARN); exit 0 otherwise."""
    if yaml is None:
        print("[provenance] PyYAML not importable — cannot parse frontmatter.", file=sys.stderr)
        return 1
    pages = sorted((root / "wiki" / "core").rglob("*.md"))
    all_issues: list[ProvenanceIssue] = []
    for page in pages:
        all_issues.extend(_check_page_provenance(page, root))

    errors = [i for i in all_issues if i.severity == "error"]
    warns = [i for i in all_issues if i.severity == "warn"]

    for issue in sorted(all_issues, key=lambda i: (i.severity != "error", str(i.page))):
        rel = issue.page.relative_to(root)
        tag = "ERROR" if issue.severity == "error" else "warn "
        print(f"[provenance] {tag} {rel}: {issue.message}", file=sys.stderr)

    print(
        f"[provenance] scanned {len(pages)} wiki/core pages — "
        f"{len(errors)} error(s), {len(warns)} warning(s).",
        file=sys.stderr,
    )
    if errors or (strict and warns):
        return 1
    return 0


def write_provenance(root: Path, only: Optional[list[Path]] = None) -> int:
    """Stamp `content_sha256` onto wiki/core pages that are *deliberately pinned* (at
    least one source on a real sha, not `main`). This is the signal check_provenance
    reads, so it asserts "this content was validated against its pinned commit" — only
    run it on pages you actually re-validated.

    `only` restricts stamping to an explicit page list (`--page`), the honest default for
    a targeted refresh. With no `--page`, every deliberately-pinned page is (re)stamped —
    a deliberate full re-pin after a validated sweep. Pages pinned to `main` are always
    skipped (they make no validation claim)."""
    if yaml is None:
        print("[provenance] PyYAML not importable — cannot parse frontmatter.", file=sys.stderr)
        return 1
    only_resolved = {p.resolve() for p in only} if only else None
    pages = sorted((root / "wiki" / "core").rglob("*.md"))
    stamped: list[Path] = []
    for page in pages:
        if only_resolved is not None and page.resolve() not in only_resolved:
            continue
        text = page.read_text(encoding="utf-8")
        fm_text, body = split_frontmatter(text)
        if fm_text is None:
            continue
        try:
            meta = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(meta, dict):
            continue
        pins = [
            str(s.get("pinned_commit", "")).strip()
            for s in (meta.get("sources") or [])
            if isinstance(s, dict)
        ]
        if not any(_SHA_RE.match(p) for p in pins):
            continue  # not deliberately pinned — make no validation claim

        h = _body_hash(body)
        fm_lines = [ln for ln in fm_text.split("\n") if not ln.startswith("content_sha256:")]
        fm_lines.append(f"content_sha256: {h}")
        new_text = "---\n" + "\n".join(fm_lines) + "\n---\n" + body
        if new_text != text:
            page.write_text(new_text, encoding="utf-8")
            stamped.append(page)

    if stamped:
        for p in stamped:
            print(f"[provenance] stamped {p.relative_to(root)}", file=sys.stderr)
    print(f"[provenance] stamped {len(stamped)} deliberately-pinned page(s).", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# Citation-path check (--check-citations)
# ---------------------------------------------------------------------------
# The symbol audit and the citation paths are independent failure axes: a page can
# cite only live `al.*` symbols while its `Project:relative/path` source citations
# point at a pre-refactor file layout (module → package moves, deleted files). This
# check resolves every citation — inline backticked `<project>:<path>` in the body
# and each `sources[].paths[]` entry in wiki frontmatter — against a real checkout.


def _sources_projects(root: Path) -> list[str]:
    """Project names from sources.yaml — the canonical set a citation may reference."""
    if yaml is None:
        return list(PROJECT_IMPORT)
    try:
        data = yaml.safe_load((root / "sources.yaml").read_text(encoding="utf-8")) or {}
        names = [p["name"] for p in data.get("projects", []) if isinstance(p, dict) and p.get("name")]
        return names or list(PROJECT_IMPORT)
    except Exception:  # noqa: BLE001
        return list(PROJECT_IMPORT)


def _project_tree(project: str, root: Path) -> Optional[tuple[Path, str]]:
    """A directory holding `project`'s source tree, tagged with how complete it is:

    - `("…", "repo")` — a full checkout: the installed package's enclosing git repo,
      a `sources/<project>/` clone, or a sibling clone. Every repo-relative path is
      checkable.
    - `("…", "package")` — a plain pip install (CI): the site-packages directory
      containing the imported package. Only paths under the package itself
      (`autofit/…`) are checkable; repo-level files (README.md, docs/) are not, and
      the caller must skip them rather than flag them.

    None when nothing is present — the caller downgrades to a warning."""
    repo = _project_repo(project)
    if repo is not None:
        return repo, "repo"
    for candidate in (root / "sources" / project, root.parent / project):
        if candidate.is_dir():
            return candidate, "repo"
    imp = PROJECT_IMPORT.get(project)
    if imp:
        try:
            mod = importlib.import_module(imp)
            return Path(mod.__file__).resolve().parent.parent, "package"
        except Exception:  # noqa: BLE001
            pass
    return None


def check_citations(root: Path) -> int:
    """Resolve every `Project:path` citation in skills/, wiki/core/, AGENTS.md and
    llms.txt against a checkout of the cited project. A path containing `...` is a
    deliberate abbreviation — only its concrete prefix is required to exist. Exit 1
    on any missing path; unresolvable project trees are warnings (packaged install
    with no clone), missing paths are errors."""
    projects = _sources_projects(root)
    cite_re = re.compile(
        r"`(" + "|".join(re.escape(p) for p in projects) + r"):([A-Za-z0-9_./\-]+?)`"
    )
    files = sorted((root / "skills").glob("*.md"))
    files += sorted((root / "wiki" / "core").rglob("*.md"))
    # Benchmark protocol docs + frozen prompt cards — but never runs/, whose
    # transcripts are historical data and may legitimately quote stale paths.
    files += sorted((root / "benchmarks").glob("*.md"))
    files += sorted((root / "benchmarks" / "prompts").glob("*.md"))
    files += [p for p in (root / "AGENTS.md", root / "llms.txt") if p.exists()]

    errors: list[str] = []
    warns: list[str] = []
    seen_missing_tree: set[str] = set()
    n_citations = 0
    n_skipped = 0

    def _check_one(rel_file: Path, project: str, cited: str) -> None:
        nonlocal n_citations, n_skipped
        n_citations += 1
        if project == "autolens_assistant":
            resolved: Optional[tuple[Path, str]] = (root, "repo")  # self-citations
        else:
            resolved = _project_tree(project, root)
        if resolved is None:
            if project not in seen_missing_tree:
                seen_missing_tree.add(project)
                warns.append(
                    f"{project}: no source tree resolvable (checkout or install) — "
                    f"its citations skipped."
                )
            n_skipped += 1
            return
        tree, kind = resolved
        concrete = cited.split("...")[0].rstrip("/")
        if not concrete:
            return
        if kind == "package":
            # Plain pip install: only package-internal paths exist on disk. Skip
            # repo-level citations (README.md, docs/) — a full checkout checks them.
            imp = PROJECT_IMPORT.get(project, "")
            if concrete.split("/")[0] != imp:
                n_skipped += 1
                return
        if not (tree / concrete).exists():
            errors.append(f"{rel_file}: `{project}:{cited}` — {concrete} not in {tree}")

    for f in files:
        text = f.read_text(encoding="utf-8")
        if IDIOM_SKIP_MARKER in text:
            continue
        rel = f.relative_to(root)
        fm_text, body = split_frontmatter(text)
        for m in cite_re.finditer(body if fm_text is not None else text):
            _check_one(rel, m.group(1), m.group(2))
        # Frontmatter sources[].paths[] make the same claim in structured form.
        if fm_text is not None and yaml is not None:
            try:
                meta = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                meta = {}
            if isinstance(meta, dict):
                for source in meta.get("sources") or []:
                    if not isinstance(source, dict):
                        continue
                    project = source.get("project")
                    if project not in projects:
                        continue
                    for path in source.get("paths") or []:
                        _check_one(rel, project, str(path))

    for w in warns:
        print(f"[citations] warn  {w}", file=sys.stderr)
    for e in errors:
        print(f"[citations] ERROR {e}", file=sys.stderr)
    print(
        f"[citations] scanned {len(files)} files, {n_citations} citation(s) "
        f"({n_skipped} skipped) — {len(errors)} missing path(s), {len(warns)} warning(s).",
        file=sys.stderr,
    )
    return 1 if errors else 0


# ---------------------------------------------------------------------------
# Code gate (--code / --file)
# ---------------------------------------------------------------------------
def validate_source(text: str) -> tuple[int, list[str], dict[str, str]]:
    """Resolve every alias-rooted symbol in raw Python `text` against the installed
    stack.

    Unlike the Markdown/scripts report (which writes a file and is keyed to a
    version baseline), this is a cheap, version-independent gate over a snippet or
    a single file the agent is *about to run* — the place a stale symbol like
    `al.Kernel2D` or `aplt.FitImagingPlotter` actually crashes. Returns
    `(n_stale, report_lines, import_failed)`; `report_lines` is empty when every
    resolvable symbol resolves, and `import_failed` maps each root module that
    failed to import to a truncated first error — a broken/blocked stack is an
    environment problem, never counted as symbol staleness.
    """
    symbols = extract_symbols_code(text)
    lines: list[str] = []
    n_stale = 0
    import_failed: dict[str, str] = {}
    for sym in sorted(symbols, key=lambda s: s.text):
        res = resolve(sym)
        if res.status == "ok":
            continue
        if res.status == "import_failed":
            # The root module didn't import — an environment problem, not API
            # drift. Marking every symbol under it STALE conflates the two and
            # repeats the (often multi-paragraph) import error once per symbol.
            module = ALIAS_TO_MODULE[sym.alias]
            err = res.error or "import failed"
            if len(err) > 200:
                err = err[:200] + "…"
            import_failed.setdefault(module, err)
            continue
        n_stale += 1
        if res.status == "missing_attr":
            tail = ".".join(sym.chain[res.resolved_depth :])
            status = f"not in installed stack (missing `.{tail}`)"
        else:
            status = f"error ({res.error})"
        # `candidates` are fuzzy/cross-module name matches, NOT a verified rename map
        # (e.g. FitImagingPlotter -> subplot_fit_imaging is a paradigm change difflib
        # can't know). Present them as hints and point at the authoritative source.
        if res.candidates:
            hint = "closest live names: " + ", ".join(res.candidates) + " (verify)"
        else:
            hint = (
                "no close match — ground against skills/ or `dir()` of the live module"
            )
        lines.append(f"STALE  {sym.text}  —  {status}; {hint}")
    return n_stale, lines, import_failed


def run_code_gate(*, code: str | None, file: str | None) -> int:
    """Validate a snippet (`--code`) or a single `.py` file (`--file`) and return an
    exit code: 0 = all symbols resolve, 2 = at least one stale symbol (distinct from
    the report mode's 1), 3 (= INSTALL_IMPORT_FAILED) = the stack itself failed to
    import so no symbol judgement is possible. Self-contained — needs neither
    `sources.yaml` nor the baseline, only the installed library."""
    if code is not None:
        text, label = code, "<--code>"
    else:
        p = Path(file)  # type: ignore[arg-type]
        if not p.exists():
            print(f"[gate] file not found: {p}", file=sys.stderr)
            return 2
        text, label = p.read_text(encoding="utf-8"), str(p)

    text = mask_gate_off_regions(text)
    n_stale, report, import_failed = validate_source(text)

    # Idiom lint runs alongside symbol resolution: the gate must catch a dead
    # *construction* (`analysis + analysis`) as well as a dead *symbol*. Emit the
    # hits as `STALE-IDIOM` lines so the PreToolUse hook (which collects `STALE*`
    # stderr lines) surfaces them with the same deny path.
    idiom_hits = lint_idioms(text)
    for hit in idiom_hits:
        report.append(
            f"STALE-IDIOM  {hit.rule.name}  —  {hit.rule.why_defunct}; "
            f"instead {hit.rule.replacement} ({hit.rule.citation})"
        )

    # Call-signature check: every symbol can resolve while a call still passes a
    # keyword the installed function does not take (`output_filename=` to
    # `aplt.subplot_fit_imaging`). Same `STALE*` prefix so the hook denies it too.
    call_issues = (
        check_call_signatures_markdown(text)
        if label.endswith(".md")
        else check_call_signatures(text)
    )
    for issue in call_issues:
        report.append(
            f"STALE-CALL  {issue.call}(...) line {issue.line_no}  —  {issue.problem}; "
            f"{issue.hint} (verify with inspect.signature)"
        )

    n_bad = n_stale + len(idiom_hits) + len(call_issues)
    if n_bad:
        print(
            f"[gate] {n_bad} stale PyAuto* reference(s) in {label} "
            f"({n_stale} symbol(s), {len(call_issues)} call(s), "
            f"{len(idiom_hits)} idiom(s)) — "
            f"fix against the live API before running:",
            file=sys.stderr,
        )
        for line in report:
            print("  " + line, file=sys.stderr)
        return 2
    if import_failed:
        print(
            f"[gate] cannot validate {label}: the PyAuto* stack failed to import — "
            "an environment problem, not API drift:",
            file=sys.stderr,
        )
        for module, err in import_failed.items():
            print(f"  {module}: {err}", file=sys.stderr)
        print(
            "  Fix the environment first (skills/al_setup_environment.md); if this is "
            "the workspace version check, set PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1.",
            file=sys.stderr,
        )
        return INSTALL_IMPORT_FAILED
    print(
        f"[gate] {label}: all PyAuto* symbols, call arguments and idioms resolve.",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit PyAuto* API references in skills + wiki + scripts."
    )
    parser.add_argument(
        "--scope",
        choices=["instructions", "skills", "wiki", "scripts", "all"],
        default="all",
        help="instructions = AGENTS.md; all = instructions + skills + wiki + scripts.",
    )
    parser.add_argument("--out", default=None)
    parser.add_argument("--root", default=None)
    parser.add_argument(
        "--check-install",
        action="store_true",
        help="Check whether the PyAuto* stack imports in the active interpreter and "
        "report its environment, versions, location, and likely install type.",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Snapshot the installed stack (versions + API-surface hash) to "
        "wiki/core/api_audit_baseline.json and exit. Re-pin after a deliberate upgrade.",
    )
    parser.add_argument(
        "--dump-symbols",
        action="store_true",
        help="Emit the installed stack's public API surface as Markdown (to --out, else "
        "stdout) and exit. Lets an agent on a harness without the code-gate hook check "
        "that a symbol exists; generated, never hand-maintained.",
    )
    parser.add_argument(
        "--check-version",
        action="store_true",
        help="Compare the installed stack against the committed baseline and exit "
        "(non-zero on drift). Cheap — no Markdown scan; safe at session start.",
    )
    parser.add_argument(
        "--lint-idioms",
        action="store_true",
        help="Scan skills/ + wiki/ + scripts/ for defunct API idioms from the deny-list "
        "(e.g. analysis-summing) and exit (0 clean, 1 hits). Self-contained; needs no "
        "installed stack. Catches dead constructions the symbol audit is blind to.",
    )
    parser.add_argument(
        "--check-provenance",
        action="store_true",
        help="Verify every wiki/core page's pinned_commit is a real, reachable commit "
        "(git mode) and that its content_sha256 still matches the body (git-free). Exit 1 "
        "on a forged/divergent pin or a stamped-but-edited page; 0 otherwise.",
    )
    parser.add_argument(
        "--write-provenance",
        action="store_true",
        help="Stamp content_sha256 onto deliberately-pinned wiki/core pages (run by the "
        "refresh after validating content against its pinned commit). Restrict to "
        "specific pages with --page; otherwise stamps every deliberately-pinned page.",
    )
    parser.add_argument(
        "--page",
        action="append",
        default=None,
        help="With --write-provenance, restrict stamping to this page (repeatable). The "
        "honest default for a targeted refresh — only stamp what you re-validated.",
    )
    parser.add_argument(
        "--check-citations",
        action="store_true",
        help="Resolve every `Project:path` source citation (inline + wiki frontmatter "
        "sources paths) against a checkout of the cited project and exit (0 ok, 1 "
        "missing). Catches pre-refactor path staleness the symbol audit is blind to.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="With --check-provenance, also fail on warnings (unpinned `main` refs, "
        "unstamped pages), not just errors.",
    )
    parser.add_argument(
        "--code",
        default=None,
        help="Validate a Python snippet's PyAuto* symbols against the installed stack "
        "and exit (0 ok, 2 stale). Version-independent gate for code about to run.",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Like --code, but validate a single .py file at any path (0 ok, 2 stale).",
    )
    args = parser.parse_args()

    if args.check_install:
        return check_installation()

    # Self-contained: reads the installed stack directly, needs no repo root.
    if args.dump_symbols:
        return dump_symbols(args.out)

    # Code-gate modes are self-contained: they resolve symbols straight against the
    # installed library, so they need neither `sources.yaml` nor the version baseline.
    if args.code is not None or args.file is not None:
        return run_code_gate(code=args.code, file=args.file)

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    if not (root / "sources.yaml").exists():
        sys.exit(f"sources.yaml not found under {root}; pass --root.")

    # Idiom lint is self-contained (no installed stack, no Markdown symbol scan).
    if args.lint_idioms:
        return run_idiom_lint(root)

    # Provenance actions are self-contained too (frontmatter + optional git).
    if args.write_provenance:
        only = [Path(p) for p in args.page] if args.page else None
        return write_provenance(root, only=only)
    if args.check_provenance:
        return check_provenance(root, strict=args.strict)
    if args.check_citations:
        return check_citations(root)

    # Baseline actions short-circuit the (expensive) Markdown/script scan.
    if args.check_version:
        install_status = check_installation(verbose_ready=False)
        if install_status != INSTALL_READY:
            return install_status
        return check_version(root)
    if args.write_baseline:
        path = write_baseline(root)
        print(f"[baseline] wrote {path}", file=sys.stderr)
        return 0

    versions = gather_versions()

    files = select_files(root, args.scope)
    occurrences_by_file: dict[Path, dict[Symbol, set[str]]] = {}
    call_issues_by_file: dict[Path, list[CallIssue]] = {}
    all_symbols: set[Symbol] = set()
    skipped: list[Path] = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        # Opt-out parity with the code gate: a file that *documents* the API surface
        # (this skill's own meta-docs, intentional stale-symbol examples) carries the
        # `pyauto-api-gate: skip` marker so its examples aren't mistaken for real usage.
        if IDIOM_SKIP_MARKER in text:
            skipped.append(f)
            continue
        text = mask_gate_off_regions(text)
        # `.py` files (scripts scope) are code throughout; Markdown is split into
        # code/prose segments by extract_symbols.
        per_file = (
            extract_symbols_code(text) if f.suffix == ".py" else extract_symbols(text)
        )
        occurrences_by_file[f] = per_file
        all_symbols.update(per_file)
        file_call_issues = (
            check_call_signatures(text)
            if f.suffix == ".py"
            else check_call_signatures_markdown(text)
        )
        if file_call_issues:
            call_issues_by_file[f] = file_call_issues

    if skipped:
        print(
            f"[audit] skipped {len(skipped)} marker-opted-out file(s): "
            + ", ".join(str(p.relative_to(root)) for p in skipped),
            file=sys.stderr,
        )

    print(
        f"[audit] scanned {len(files)} files; {len(all_symbols)} unique symbols",
        file=sys.stderr,
    )

    resolutions: dict[Symbol, Resolution] = {
        sym: resolve(sym) for sym in sorted(all_symbols, key=lambda s: s.text)
    }

    out_path = (
        Path(args.out)
        if args.out
        else (
            root
            / "autoassistant"
            / "audit"
            / f"skill_api_audit_{dt.date.today().isoformat()}.md"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = render_report(
        versions=versions,
        occurrences_by_file=occurrences_by_file,
        resolutions=resolutions,
        scope=args.scope,
        root=root,
        call_issues_by_file=call_issues_by_file,
    )
    out_path.write_text(report, encoding="utf-8")

    n_missing = sum(1 for r in resolutions.values() if r.status != "ok")
    n_call = sum(len(v) for v in call_issues_by_file.values())
    print(f"[audit] missing/broken: {n_missing}", file=sys.stderr)
    print(f"[audit] call-argument mismatches: {n_call}", file=sys.stderr)
    for f, issues in sorted(call_issues_by_file.items()):
        for issue in issues:
            print(
                f"  {f.relative_to(root)}:{issue.line_no}  {issue.call}  {issue.problem}",
                file=sys.stderr,
            )
    print(f"[audit] report written to {out_path}", file=sys.stderr)

    return 0 if n_missing == 0 and n_call == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
