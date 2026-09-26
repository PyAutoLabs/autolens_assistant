"""The public COSMOS-Web Ring greeting skill (autolens_assistant#136).

The website's starting prompt lands a newcomer here, so the skill's promises are
pinned: the F444W image first, the four JWST bands and achromatic lensing, then
exactly one background question before any fit — and the skill must be
discoverable by every harness that indexes skills.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "al_greeting_cosmos_web_ring"
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


def test_skill_uses_f444w_and_names_all_four_bands():
    text = _text()
    assert "wavebands/F444W" in text
    for band in ("F115W", "F150W", "F277W", "F444W"):
        assert band in text, band
    assert "achromatic" in text.lower()


def test_ask_step_asks_exactly_one_question():
    ask = _section(_text(), "Step 2")
    assert ask.count("?") == 1
    assert "curious reader, a student, or a researcher who wants the code?" in ask


def test_skill_routes_every_audience_and_fabricates_no_numbers():
    route = _section(_text(), "Step 3")
    for target in ("modes/teacher.md", "modes/assistant.md", "Curious reader"):
        assert target in route, target
    assert "scripts/cosmos_web_ring/results/README.md" in _text()


def test_skill_is_discoverable_everywhere_skills_are_indexed():
    assert f"./{NAME}.md" in (ROOT / "skills" / "README.md").read_text(encoding="utf-8")
    for mirror in (".claude/skills", ".claude/commands"):
        link = ROOT / mirror / f"{NAME}.md"
        assert link.is_symlink() and link.resolve() == SKILL.resolve(), link
    codex = ROOT / ".codex/skills/autolens-assistant-al-greeting-cosmos-web-ring/SKILL.md"
    assert codex.is_file()
    assert f"skills/{NAME}.md" in codex.read_text(encoding="utf-8")
    assert f"skills/{NAME}.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
