"""The al_explain_setup skill (likelihood lifecycle phase 5G, autolens_assistant#191).

It explains the compute setup a fit used from the records the library writes, so its
promises are pinned: it reads files/setup.json and files/parallel.json, cites the rule
table, the day-zero evidence and the Pulse decision, covers a planned fit through
al.estimate_runtime with a concrete setup_id, and is discoverable by every harness.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "al_explain_setup"
SKILL = ROOT / "skills" / f"{NAME}.md"


def _text():
    return SKILL.read_text(encoding="utf-8")


def _section(text, heading_prefix):
    """Body of the first `## <heading_prefix>...` section, up to the next `## `."""
    match = re.search(
        rf"^## {re.escape(heading_prefix)}.*?$(.*?)(?=^## |\Z)", text, re.M | re.S
    )
    assert match, f"no '## {heading_prefix}' section in {SKILL.name}"
    return match.group(1)


def test_skill_exists_with_frontmatter_name():
    text = _text()
    assert text.startswith("---\n")
    assert f"name: {NAME}\n" in text.split("---")[1]


def test_follows_the_conversation_arc():
    text = _text()
    headings = ("## Orient", "## Ask", "## Branch A", "## Branch B", "## Combine")
    positions = [text.index(h) for h in headings]
    assert positions == sorted(positions)


def test_finished_fit_branch_reads_the_records_and_cites_the_evidence():
    branch = _section(_text(), "Branch A")
    for needle in (
        "files/setup.json",
        "files/parallel.json",
        "chosen_by",
        "decision_id",
        "setup_rules.yaml",
        "day_zero.md",
        "PyAutoPulse:decisions/",
        "Untested branches",
        "estimate_line",
    ):
        assert needle in branch, needle
    for reason in ("requested", "detected_cores", "jax", "expectation_propagation", "memory"):
        assert f"`{reason}`" in branch, reason
    assert "uncalibrated" in branch


def test_planned_fit_branch_uses_a_concrete_setup_id():
    """al.estimate_runtime does not accept setup="auto" yet; the recipe must not show it."""
    branch = _section(_text(), "Branch B")
    assert "al.estimate_runtime(" in branch
    assert 'setup="numba_cpu_sparse_fp64"' in branch
    assert 'setup="auto",' not in branch
    for handoff in ("al_profiling_setup", "al_inference_setup"):
        assert handoff in branch, handoff


def test_skill_is_discoverable_everywhere_skills_are_indexed():
    assert f"./{NAME}.md" in (ROOT / "skills" / "README.md").read_text(encoding="utf-8")
    for mirror in (".claude/skills", ".claude/commands"):
        link = ROOT / mirror / f"{NAME}.md"
        assert link.is_symlink() and link.resolve() == SKILL.resolve(), link
    codex = ROOT / ".codex/skills/autolens-assistant-al-explain-setup/SKILL.md"
    assert codex.is_file()
    assert f"skills/{NAME}.md" in codex.read_text(encoding="utf-8")
    assert f"skills/{NAME}.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_configure_search_defaults_to_auto_and_links_the_skill():
    text = (ROOT / "skills" / "al_configure_search.md").read_text(encoding="utf-8")
    compute = _section(text, "Compute setup: auto unless")
    assert 'setup="auto"' in compute
    assert 'number_of_cores="auto"' in compute
    assert f"./{NAME}.md" in compute
    assert "jax_gpu_sparse_fp64_wtilde" in compute
    assert "apply_sparse_operator()" in compute
    assert "The sparse operator does not support JAX" not in text
