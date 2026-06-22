"""Tests for the canonical literature citation layer."""

from pathlib import Path

from autoassistant.literature import (
    extract_canonical_keys,
    parse_aliases,
    parse_bibtex,
    validate_citations,
)


def test_parse_small_bibtex_file():
    inventory = parse_bibtex(
        """
@article{Alpha2024,
  title = {Alpha},
}
@misc{Beta2025,
  title = {Beta},
}
"""
    )

    assert inventory.keys == {"Alpha2024", "Beta2025"}
    assert inventory.duplicates == ()


def test_extract_canonical_keys_from_source_markdown():
    citations = extract_canonical_keys(
        """
## Alpha 2024 — result

**Canonical BibTeX key:** `Alpha2024`
**Reference:** doi:example
"""
    )

    assert [(citation.key, citation.line) for citation in citations] == [
        ("Alpha2024", 4)
    ]


def test_detect_missing_canonical_key(tmp_path):
    bibliography = tmp_path / "literature.bib"
    bibliography.write_text("@article{Alpha2024,\n}\n", encoding="utf-8")
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "topic.md").write_text(
        "**Canonical BibTeX key:** `Missing2025`\n", encoding="utf-8"
    )
    aliases = tmp_path / "aliases.yaml"
    aliases.write_text("{}\n", encoding="utf-8")

    result = validate_citations(bibliography, sources, aliases)

    assert [citation.key for citation in result.missing_source_keys] == [
        "Missing2025"
    ]
    assert not result.valid


def test_validate_alias_targets(tmp_path):
    bibliography = tmp_path / "literature.bib"
    bibliography.write_text("@article{Canonical2024,\n}\n", encoding="utf-8")
    sources = tmp_path / "sources"
    sources.mkdir()
    aliases = tmp_path / "aliases.yaml"
    aliases.write_text(
        "LocalKey: Canonical2024\nBrokenKey: Missing2025\n", encoding="utf-8"
    )

    result = validate_citations(bibliography, sources, aliases)

    assert parse_aliases(aliases.read_text(encoding="utf-8")) == {
        "LocalKey": "Canonical2024",
        "BrokenKey": "Missing2025",
    }
    assert result.missing_alias_targets == (("BrokenKey", "Missing2025"),)
    assert not result.valid


def test_detect_claim_entry_without_key(tmp_path):
    bibliography = tmp_path / "literature.bib"
    bibliography.write_text("@article{Alpha2024,\n}\n", encoding="utf-8")
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "topic.md").write_text(
        "## Alpha 2024 — result\n\n**Supports:**\n- A claim.\n",
        encoding="utf-8",
    )
    aliases = tmp_path / "aliases.yaml"
    aliases.write_text("", encoding="utf-8")

    result = validate_citations(bibliography, sources, aliases)

    assert [(entry.key, entry.line) for entry in result.claim_entries_without_keys] == [
        ("Alpha 2024 — result", 1)
    ]
    assert not result.valid
