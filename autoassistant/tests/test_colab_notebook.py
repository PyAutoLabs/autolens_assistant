"""Pin the tracked Colab-facing COSMOS-Web Ring notebook.

`docs/colab/cosmos_web_ring_colab.ipynb` is generated from `docs/colab/cosmos_web_ring_colab.py`
by `autoassistant.to_notebook`; these tests keep the two in step and check that the
notebook still carries its Colab setup cell and the content the README promises.
Stdlib-only and fast: nothing is executed.
"""

from __future__ import annotations

import json
from pathlib import Path

from autoassistant.to_notebook import convert

REPO_ROOT = Path(__file__).resolve().parents[2]
COLAB_DIR = REPO_ROOT / "docs" / "colab"
SOURCE = COLAB_DIR / "cosmos_web_ring_colab.py"
NOTEBOOK = COLAB_DIR / "cosmos_web_ring_colab.ipynb"

STARTING_PROMPT_OPENING = (
    "I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant"
)


def _cells():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]


def _prose():
    return "\n".join(
        "".join(cell["source"]) for cell in _cells() if cell["cell_type"] == "markdown"
    )


def test_notebook_and_source_exist():
    assert SOURCE.is_file()
    assert NOTEBOOK.is_file()


def test_first_code_cell_is_the_colab_setup_right_after_the_title():
    cells = _cells()
    assert cells[0]["cell_type"] == "markdown"
    assert cells[1]["cell_type"] == "code"
    first_code = "".join(cells[1]["source"])
    assert "google.colab" in first_code
    assert "autonerves" in first_code
    assert 'setup(\n    "autolens"' in first_code or 'setup("autolens"' in first_code


def test_prose_covers_the_promised_content():
    prose = _prose()
    for band in ("F115W", "F150W", "F277W", "F444W"):
        assert band in prose, band
    assert "achromatic" in prose
    assert "Gemini" in prose
    assert STARTING_PROMPT_OPENING in prose


def test_notebook_regenerates_byte_identically(tmp_path):
    regenerated = convert(SOURCE, tmp_path / "regenerated.ipynb")
    assert regenerated.read_bytes() == NOTEBOOK.read_bytes(), (
        "docs/colab/cosmos_web_ring_colab.ipynb is stale: run "
        "`python -m autoassistant.to_notebook docs/colab/cosmos_web_ring_colab.py "
        "docs/colab/cosmos_web_ring_colab.ipynb`"
    )
