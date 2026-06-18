"""Audit PyAuto* API references in skills/ and wiki/core/ against the installed stack.

Walks every Markdown file in scope, extracts fully-qualified symbols cited under
the standard aliases (`al`, `aplt`, `af`, `ag`, `aa` and the bare module names),
resolves each one by importing the underlying module and walking attribute by
attribute, and writes a Markdown report listing the misses with suggested
replacements.

This is the mechanical half of the `al_audit_skill_apis` skill. The skill drives
interpretation and curates fixes; this script just produces the raw report.

Usage:

    source activate.sh
    python autoassistant/audit_skill_apis.py --scope all   # skills + wiki/core/api + wiki/core/stack
    python autoassistant/audit_skill_apis.py --scope skills
    python autoassistant/audit_skill_apis.py --scope wiki

Report lands at `autoassistant/audit/skill_api_audit_<YYYY-MM-DD>.md` by default.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import importlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterable

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
    "autoconf",
    "autoarray",
    "autofit",
    "autogalaxy",
    "autolens",
    "autolens.plot",
)
VERSIONED_MODULES: tuple[str, ...] = (
    "autoconf",
    "autoarray",
    "autofit",
    "autogalaxy",
    "autolens",
)

# ---------------------------------------------------------------------------
# Aliases. Standardised in CLAUDE.md Part 1 "Conventions". Order is
# length-descending so the regex alternation prefers `autolens` over `al`.
# ---------------------------------------------------------------------------
ALIAS_TO_MODULE: dict[str, str] = {
    "al": "autolens",
    "aplt": "autolens.plot",
    "af": "autofit",
    "ag": "autogalaxy",
    "aa": "autoarray",
    "autoconf": "autoconf",
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
        status="ok", resolved_depth=len(sym.chain), parent_repr=_short_repr(current)
    )


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
    for mod_name in ("autoconf", "autoarray", "autofit", "autogalaxy", "autolens"):
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
        p
        for p in sorted((root / "scripts").rglob("*.py"))
        if p.name not in tooling
    ]
    if scope == "skills":
        return skills
    if scope == "wiki":
        return wiki_api + wiki_stack
    if scope == "scripts":
        return scripts
    if scope == "all":
        return skills + wiki_api + wiki_stack + scripts
    raise SystemExit(f"unknown scope: {scope!r}")


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
) -> str:
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
    lines.append("")

    if not missing:
        lines.append("All cited symbols resolve cleanly. No drift detected.")
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
    for name in ("autoconf", "autoarray", "autofit", "autogalaxy", "autolens"):
        try:
            mod = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001
            out[name] = f"NOT INSTALLED ({e!r})"
            continue
        ver = getattr(mod, "__version__", "(no __version__)")
        out[name] = str(ver)
    return out


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


def check_version(root: Path) -> int:
    """Compare the installed stack against the committed baseline.

    Returns 0 when versions and API hashes match, 1 on any drift (or a missing
    baseline). Prints a short human-readable summary. Intentionally cheap — no
    Markdown scan — so it is safe to run at session start.
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

    version_drift = [
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

    if not version_drift and not hash_drift:
        print(
            f"[drift] clean — installed stack matches baseline "
            f"(autolens {current['versions']['autolens']}, generated {baseline.get('generated')})."
        )
        return 0

    print(
        "[drift] API DRIFT vs baseline "
        f"(baseline generated {baseline.get('generated')}):",
        file=sys.stderr,
    )
    for m, old, new in version_drift:
        print(f"  - {m}: {old} -> {new}", file=sys.stderr)
    if hash_drift:
        print(
            f"  - public API surface changed: {', '.join(hash_drift)}", file=sys.stderr
        )
    print(
        "  The skills/wiki were validated against the baseline. Upgrade/downgrade to the "
        "pinned version (`pip install -U autolens`), or run `--scope all` to audit drift "
        "and `--write-baseline` to re-pin once fixed.",
        file=sys.stderr,
    )
    return 1


# ---------------------------------------------------------------------------
# Code gate (--code / --file)
# ---------------------------------------------------------------------------
def validate_source(text: str) -> tuple[int, list[str]]:
    """Resolve every alias-rooted symbol in raw Python `text` against the installed
    stack.

    Unlike the Markdown/scripts report (which writes a file and is keyed to a
    version baseline), this is a cheap, version-independent gate over a snippet or
    a single file the agent is *about to run* — the place a stale symbol like
    `al.Kernel2D` or `aplt.FitImagingPlotter` actually crashes. Returns
    `(n_stale, report_lines)`; `report_lines` is empty when everything resolves.
    """
    symbols = extract_symbols_code(text)
    lines: list[str] = []
    n_stale = 0
    for sym in sorted(symbols, key=lambda s: s.text):
        res = resolve(sym)
        if res.status == "ok":
            continue
        n_stale += 1
        if res.status == "missing_attr":
            tail = ".".join(sym.chain[res.resolved_depth :])
            status = f"not in installed stack (missing `.{tail}`)"
        elif res.status == "import_failed":
            status = f"import failed ({res.error})"
        else:
            status = f"error ({res.error})"
        # `candidates` are fuzzy/cross-module name matches, NOT a verified rename map
        # (e.g. FitImagingPlotter -> subplot_fit_imaging is a paradigm change difflib
        # can't know). Present them as hints and point at the authoritative source.
        if res.candidates:
            hint = "closest live names: " + ", ".join(res.candidates) + " (verify)"
        else:
            hint = "no close match — ground against skills/ or `dir()` of the live module"
        lines.append(f"STALE  {sym.text}  —  {status}; {hint}")
    return n_stale, lines


def run_code_gate(*, code: str | None, file: str | None) -> int:
    """Validate a snippet (`--code`) or a single `.py` file (`--file`) and return an
    exit code: 0 = all symbols resolve, 2 = at least one stale symbol (distinct from
    the report mode's 1). Self-contained — needs neither `sources.yaml` nor the
    baseline, only the installed library."""
    if code is not None:
        text, label = code, "<--code>"
    else:
        p = Path(file)  # type: ignore[arg-type]
        if not p.exists():
            print(f"[gate] file not found: {p}", file=sys.stderr)
            return 2
        text, label = p.read_text(encoding="utf-8"), str(p)

    n_stale, report = validate_source(text)
    if n_stale:
        print(
            f"[gate] {n_stale} stale PyAuto* symbol(s) in {label} — "
            f"fix against the live API before running:",
            file=sys.stderr,
        )
        for line in report:
            print("  " + line, file=sys.stderr)
        return 2
    print(f"[gate] {label}: all PyAuto* symbols resolve.", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit PyAuto* API references in skills + wiki + scripts."
    )
    parser.add_argument(
        "--scope", choices=["skills", "wiki", "scripts", "all"], default="all"
    )
    parser.add_argument("--out", default=None)
    parser.add_argument("--root", default=None)
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Snapshot the installed stack (versions + API-surface hash) to "
        "wiki/core/api_audit_baseline.json and exit. Re-pin after a deliberate upgrade.",
    )
    parser.add_argument(
        "--check-version",
        action="store_true",
        help="Compare the installed stack against the committed baseline and exit "
        "(non-zero on drift). Cheap — no Markdown scan; safe at session start.",
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

    # Code-gate modes are self-contained: they resolve symbols straight against the
    # installed library, so they need neither `sources.yaml` nor the version baseline.
    if args.code is not None or args.file is not None:
        return run_code_gate(code=args.code, file=args.file)

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    if not (root / "sources.yaml").exists():
        sys.exit(f"sources.yaml not found under {root}; pass --root.")

    # Baseline actions short-circuit the (expensive) Markdown/script scan.
    if args.check_version:
        return check_version(root)
    if args.write_baseline:
        path = write_baseline(root)
        print(f"[baseline] wrote {path}", file=sys.stderr)
        return 0

    versions = gather_versions()

    files = select_files(root, args.scope)
    occurrences_by_file: dict[Path, dict[Symbol, set[str]]] = {}
    all_symbols: set[Symbol] = set()
    for f in files:
        text = f.read_text(encoding="utf-8")
        # `.py` files (scripts scope) are code throughout; Markdown is split into
        # code/prose segments by extract_symbols.
        per_file = (
            extract_symbols_code(text) if f.suffix == ".py" else extract_symbols(text)
        )
        occurrences_by_file[f] = per_file
        all_symbols.update(per_file)

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
    )
    out_path.write_text(report, encoding="utf-8")

    n_missing = sum(1 for r in resolutions.values() if r.status != "ok")
    print(f"[audit] missing/broken: {n_missing}", file=sys.stderr)
    print(f"[audit] report written to {out_path}", file=sys.stderr)

    return 0 if n_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
