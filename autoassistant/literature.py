"""Validate links between literature source entries and canonical BibTeX metadata."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIBLIOGRAPHY = (
    ROOT / "wiki" / "literature" / "bibliography" / "autolens_literature.bib"
)
DEFAULT_ALIASES = (
    ROOT / "wiki" / "literature" / "bibliography" / "bibkey_aliases.yaml"
)
DEFAULT_SOURCES = ROOT / "wiki" / "literature" / "sources"

BIBTEX_ENTRY = re.compile(
    r"^\s*@(?!comment\b|string\b|preamble\b)[A-Za-z]+\s*[({]\s*([^,\s]+)\s*,",
    re.MULTILINE | re.IGNORECASE,
)
CANONICAL_KEY = re.compile(
    r"^\*\*Canonical BibTeX key:\*\*\s*`([^`]+)`\s*$", re.MULTILINE
)
SOURCE_SECTION = re.compile(r"^## (?!See also\s*$)(.+?)\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class BibtexInventory:
    """Canonical keys and duplicate keys found in BibTeX text."""

    keys: frozenset[str]
    duplicates: tuple[str, ...]


@dataclass(frozen=True)
class SourceCitation:
    """A canonical key declaration in one Markdown source entry."""

    path: Path
    line: int
    key: str


@dataclass(frozen=True)
class CitationValidation:
    """Results of checking source and alias keys against the bibliography."""

    bibliography: BibtexInventory
    citations: tuple[SourceCitation, ...]
    aliases: dict[str, str]
    missing_source_keys: tuple[SourceCitation, ...]
    claim_entries_without_keys: tuple[SourceCitation, ...]
    unreferenced_bibtex_keys: tuple[str, ...]
    missing_alias_targets: tuple[tuple[str, str], ...]

    @property
    def valid(self) -> bool:
        return not (
            self.bibliography.duplicates
            or self.missing_source_keys
            or self.claim_entries_without_keys
            or self.missing_alias_targets
        )


def parse_bibtex(text: str) -> BibtexInventory:
    """Parse entry keys without requiring a third-party BibTeX package."""

    seen: set[str] = set()
    duplicates: set[str] = set()
    for key in BIBTEX_ENTRY.findall(text):
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return BibtexInventory(frozenset(seen), tuple(sorted(duplicates)))


def extract_canonical_keys(markdown: str, path: Path = Path("<memory>")) -> tuple[SourceCitation, ...]:
    """Extract canonical-key declarations from source-entry Markdown."""

    return tuple(
        SourceCitation(path=path, line=markdown.count("\n", 0, match.start()) + 1, key=match.group(1))
        for match in CANONICAL_KEY.finditer(markdown)
    )


def collect_source_citations(sources_dir: Path) -> tuple[SourceCitation, ...]:
    """Collect canonical keys from every Markdown file in the sources directory."""

    citations: list[SourceCitation] = []
    for path in sorted(sources_dir.glob("*.md")):
        citations.extend(
            extract_canonical_keys(path.read_text(encoding="utf-8"), path=path)
        )
    return tuple(citations)


def collect_claim_entries_without_keys(sources_dir: Path) -> tuple[SourceCitation, ...]:
    """Find new-schema claim sections that omit a canonical key declaration."""

    missing: list[SourceCitation] = []
    for path in sorted(sources_dir.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        for section in SOURCE_SECTION.finditer(markdown):
            if "**Supports:**" in section.group(2) and not CANONICAL_KEY.search(section.group(2)):
                missing.append(
                    SourceCitation(
                        path=path,
                        line=markdown.count("\n", 0, section.start()) + 1,
                        key=section.group(1),
                    )
                )
    return tuple(missing)


def parse_aliases(text: str) -> dict[str, str]:
    """Parse the intentionally flat alias-to-canonical YAML mapping."""

    aliases: dict[str, str] = {}
    content = text.strip()
    if not content or content == "{}":
        return aliases

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "{}":
            continue
        if ":" not in stripped:
            raise ValueError(f"invalid alias mapping on line {line_number}: {line!r}")
        alias, canonical = (part.strip().strip("'\"") for part in stripped.split(":", 1))
        if not alias or not canonical:
            raise ValueError(f"invalid alias mapping on line {line_number}: {line!r}")
        aliases[alias] = canonical
    return aliases


def validate_citations(
    bibliography_path: Path = DEFAULT_BIBLIOGRAPHY,
    sources_dir: Path = DEFAULT_SOURCES,
    aliases_path: Path = DEFAULT_ALIASES,
) -> CitationValidation:
    """Validate source and alias keys against the canonical bibliography."""

    bibliography = parse_bibtex(bibliography_path.read_text(encoding="utf-8"))
    citations = collect_source_citations(sources_dir)
    claim_entries_without_keys = collect_claim_entries_without_keys(sources_dir)
    aliases = parse_aliases(aliases_path.read_text(encoding="utf-8"))
    cited_keys = {citation.key for citation in citations}

    return CitationValidation(
        bibliography=bibliography,
        citations=citations,
        aliases=aliases,
        missing_source_keys=tuple(
            citation for citation in citations if citation.key not in bibliography.keys
        ),
        claim_entries_without_keys=claim_entries_without_keys,
        unreferenced_bibtex_keys=tuple(sorted(bibliography.keys - cited_keys)),
        missing_alias_targets=tuple(
            sorted(
                (alias, canonical)
                for alias, canonical in aliases.items()
                if canonical not in bibliography.keys
            )
        ),
    )


def _print_keys(label: str, keys: tuple[str, ...], show_all: bool) -> None:
    print(f"{label}: {len(keys)}")
    shown = keys if show_all else keys[:20]
    for key in shown:
        print(f"  - {key}")
    if len(shown) < len(keys):
        print(f"  ... {len(keys) - len(shown)} more (use --show-all)")


def _run_validation(args: argparse.Namespace) -> int:
    try:
        result = validate_citations(args.bibliography, args.sources, args.aliases)
    except (OSError, ValueError) as error:
        print(f"citation validation error: {error}")
        return 1

    print(f"Canonical BibTeX entries: {len(result.bibliography.keys)}")
    print(f"Wiki source entries with canonical keys: {len(result.citations)}")
    print(f"BibTeX key aliases: {len(result.aliases)}")
    _print_keys("Duplicate canonical BibTeX keys", result.bibliography.duplicates, args.show_all)

    print(f"Source entries with missing canonical keys: {len(result.missing_source_keys)}")
    for citation in result.missing_source_keys:
        print(f"  - {citation.path}:{citation.line}: {citation.key}")

    print(f"Claim entries without canonical key declarations: {len(result.claim_entries_without_keys)}")
    for citation in result.claim_entries_without_keys:
        print(f"  - {citation.path}:{citation.line}: {citation.key}")

    print(f"Aliases with missing canonical targets: {len(result.missing_alias_targets)}")
    for alias, canonical in result.missing_alias_targets:
        print(f"  - {alias} -> {canonical}")

    _print_keys(
        "BibTeX entries not referenced by a wiki source entry",
        result.unreferenced_bibtex_keys,
        args.show_all,
    )
    print("Citation metadata is valid." if result.valid else "Citation metadata is invalid.")
    return 0 if result.valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser(
        "validate-citations", help="check wiki source keys against canonical BibTeX"
    )
    validate.add_argument("--bibliography", type=Path, default=DEFAULT_BIBLIOGRAPHY)
    validate.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    validate.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    validate.add_argument("--show-all", action="store_true")
    validate.set_defaults(handler=_run_validation)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
