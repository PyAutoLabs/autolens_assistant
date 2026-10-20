"""One starting prompt, everywhere.

The COSMOS-Web Ring starting prompt is the assistant's front door: a visitor who copies it from
the README, from `docs/setup/first_prompts.md`, from the Colab notebook header or reads it in the
greeting skill must get the same text. These tests extract the prompt (from "I want to use the
PyAutoLens Assistant:" through "...change the analysis along the way.") from each file, strip
the markdown blockquote prefix where it is quoted, and compare. Stdlib-only and fast.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

PROMPT_START = "I want to use the PyAutoLens Assistant:"
PROMPT_END = "change the analysis along the way."

README = REPO_ROOT / "README.md"
FIRST_PROMPTS = REPO_ROOT / "docs" / "setup" / "first_prompts.md"
NOTEBOOK_SOURCE = REPO_ROOT / "docs" / "colab" / "cosmos_web_ring_colab.py"
GREETING_SKILL = REPO_ROOT / "skills" / "al_greeting_cosmos_web_ring.md"


def _prompt(path: Path) -> str:
    """The starting prompt as quoted in ``path``, with any ``> `` blockquote prefix removed."""
    text = path.read_text(encoding="utf-8")
    start = text.index(PROMPT_START)
    end = text.index(PROMPT_END, start) + len(PROMPT_END)
    lines = text[start:end].splitlines()
    return "\n".join(re.sub(r"^> ?", "", line) for line in lines)


def _words(text: str) -> list[str]:
    return text.split()


def test_readme_first_prompts_and_notebook_are_byte_identical():
    readme = _prompt(README)
    assert _prompt(FIRST_PROMPTS) == readme, "docs/setup/first_prompts.md differs from README.md"
    assert _prompt(NOTEBOOK_SOURCE) == readme, (
        "docs/colab/cosmos_web_ring_colab.py header differs from README.md"
    )


def test_greeting_skill_has_the_same_words():
    assert _words(_prompt(GREETING_SKILL)) == _words(_prompt(README))


@pytest.mark.xfail(
    strict=True,
    reason=(
        "skills/al_greeting_cosmos_web_ring.md wraps the prompt's second paragraph at ~90 "
        "columns, while README.md keeps it on one line; the words are identical "
        "(test_greeting_skill_has_the_same_words). Aligning the skill is phase 2 of the "
        "COSMOS-Web Ring walkthrough (autolens_assistant#160 epic); remove this xfail then."
    ),
)
def test_greeting_skill_is_byte_identical():
    assert _prompt(GREETING_SKILL) == _prompt(README)
