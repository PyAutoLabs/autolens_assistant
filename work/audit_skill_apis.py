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
    python work/audit_skill_apis.py --scope all   # skills + wiki/core/api + wiki/core/stack
    python work/audit_skill_apis.py --scope skills
    python work/audit_skill_apis.py --scope wiki

Report lands at `work/audit/skill_api_audit_<YYYY-MM-DD>.md` by default.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import importlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterable

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
    status: str                       # "ok" | "missing_attr" | "import_failed"
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

    return Resolution(status="ok", resolved_depth=len(sym.chain), parent_repr=_short_repr(current))


def _short_repr(obj) -> str:
    mod = getattr(obj, "__module__", None)
    name = getattr(obj, "__name__", None) or getattr(obj, "__class__", type(obj)).__name__
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
    if scope == "skills":
        return skills
    if scope == "wiki":
        return wiki_api + wiki_stack
    if scope == "all":
        return skills + wiki_api + wiki_stack
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
        f for f, d in occurrences_by_file.items()
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
        lines.append("_No PyAuto\\* libraries importable. Activate the venv (`source activate.sh`) and re-run._")
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
                tail = ".".join(sym.chain[res.resolved_depth:])
                status = f"missing `.{tail}`"
                parent = res.parent_repr
            else:
                status = "import_failed"
                parent = f"`{res.error}`"
            suggestions = ", ".join(f"`{c}`" for c in res.candidates) if res.candidates else "_(none found)_"
            lines.append(f"| `{sym.text}` | {status} | `{parent}` | {suggestions} | {ctx} |")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit PyAuto* API references in skills + wiki.")
    parser.add_argument("--scope", choices=["skills", "wiki", "all"], default="all")
    parser.add_argument("--out", default=None)
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    if not (root / "sources.yaml").exists():
        sys.exit(f"sources.yaml not found under {root}; pass --root.")

    versions = gather_versions()

    files = select_files(root, args.scope)
    occurrences_by_file: dict[Path, dict[Symbol, set[str]]] = {}
    all_symbols: set[Symbol] = set()
    for f in files:
        text = f.read_text(encoding="utf-8")
        per_file = extract_symbols(text)
        occurrences_by_file[f] = per_file
        all_symbols.update(per_file)

    print(f"[audit] scanned {len(files)} files; {len(all_symbols)} unique symbols", file=sys.stderr)

    resolutions: dict[Symbol, Resolution] = {
        sym: resolve(sym) for sym in sorted(all_symbols, key=lambda s: s.text)
    }

    out_path = Path(args.out) if args.out else (
        root / "work" / "audit" / f"skill_api_audit_{dt.date.today().isoformat()}.md"
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
