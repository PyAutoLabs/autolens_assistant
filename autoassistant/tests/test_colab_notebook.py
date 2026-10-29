"""Pin the tracked Colab-facing COSMOS-Web Ring notebook.

`docs/colab/cosmos_web_ring_colab.ipynb` is generated from `docs/colab/cosmos_web_ring_colab.py`
by `autoassistant.to_notebook` and committed **executed** (`make colab`), so a reader sees every
figure before running anything. These tests keep the source and the notebook in step (outputs
and execution metadata stripped), check that every code cell carries its output, and check that
the notebook still carries its Colab setup cell and the content the README promises.
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
STARTING_PROMPT_CLONE = "First clone that repository, cd into it and follow its AGENTS.md."


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
    assert first_code.startswith('# @title Set up Google Colab { display-mode: "form" }')
    assert cells[1]["metadata"]["cellView"] == "form"
    assert cells[1]["metadata"]["jupyter"]["source_hidden"] is True
    assert "raise_error_if_not_gpu=False" in first_code
    assert "locally or in HTML" in "".join(cells[0]["source"])
    assert 'setup(\n    "autolens"' in first_code or 'setup("autolens"' in first_code


def test_prose_covers_the_promised_content():
    prose = _prose()
    for band in ("F115W", "F150W", "F277W", "F444W"):
        assert band in prose, band
    assert "achromatic" in prose
    assert "Gemini" in prose
    assert STARTING_PROMPT_OPENING in prose
    assert STARTING_PROMPT_CLONE in prose


def _stripped(notebook: dict) -> dict:
    """The notebook with everything execution adds removed: outputs, execution counts,
    per-cell execution metadata and the kernel's language_info."""
    cells = []
    for cell in notebook["cells"]:
        cell = {key: value for key, value in cell.items() if key not in ("outputs", "execution_count")}
        cell["metadata"] = {
            key: value for key, value in cell.get("metadata", {}).items() if key != "execution"
        }
        cells.append(cell)
    return {
        "cells": cells,
        "kernelspec": notebook["metadata"].get("kernelspec"),
        "nbformat": notebook["nbformat"],
        "nbformat_minor": notebook["nbformat_minor"],
    }


def test_notebook_matches_its_source(tmp_path):
    regenerated = convert(SOURCE, tmp_path / "regenerated.ipynb")
    fresh = json.loads(regenerated.read_text(encoding="utf-8"))
    committed = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    # The maintainer pipeline expands only the setup cell through PyAutoHands.
    # Ordinary script conversion deliberately keeps the lightweight source call.
    source_setup = "".join(fresh["cells"][1]["source"])
    assert source_setup == (
        'from autolens import setup_colab\n\n'
        'setup_colab.setup("autolens", raise_error_if_not_gpu=False)'
    )
    assert "".join(fresh["cells"][0]["source"]).rstrip() == "".join(
        committed["cells"][0]["source"]
    ).rstrip()
    fresh["cells"] = fresh["cells"][2:]
    committed["cells"] = committed["cells"][2:]
    assert _stripped(fresh) == _stripped(committed), (
        "docs/colab/cosmos_web_ring_colab.ipynb is stale: run `make colab` from the "
        "repository root (it converts docs/colab/cosmos_web_ring_colab.py and executes it)"
    )


def test_every_code_cell_is_executed():
    unexecuted = [
        index
        for index, cell in enumerate(_cells())
        if cell["cell_type"] == "code" and not cell.get("outputs")
    ]
    assert not unexecuted, (
        f"code cells {unexecuted} have no outputs: the notebook must be committed executed "
        "(`make colab`), so a Colab reader sees every figure before running anything"
    )
    errors = [
        index
        for index, cell in enumerate(_cells())
        if cell["cell_type"] == "code"
        and any(output.get("output_type") == "error" for output in cell["outputs"])
    ]
    assert not errors, f"code cells {errors} raised an error when the notebook was executed"


def test_every_section_has_an_illustration_or_executed_figure():
    """Readers can inspect saved outputs without duplicate static illustrations."""
    cells = _cells()
    missing = []
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "markdown":
            continue
        text = "".join(cell["source"])
        headers = [line for line in text.splitlines() if line.startswith("__") and line.endswith("__")]
        if not headers or headers[0] in ("__Contents__", "__Imports__"):
            continue
        if "https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/" in text:
            continue
        following = cells[index + 1] if index + 1 < len(cells) else {}
        has_figure = following.get("cell_type") == "code" and any(
            any(mime.startswith("image/") for mime in output.get("data", {}))
            for output in following.get("outputs", [])
        )
        if not has_figure:
            missing.append(headers[0])
    assert not missing, f"sections without a figure: {missing}"

    markdown = "\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "markdown")
    for filename in ("cosmos_web_ring_intro.png", "cosmos_web_ring_bands.png", "cosmos_web_ring_prepared.png"):
        assert filename not in markdown, f"duplicate of executed figure: {filename}"


def test_no_search_is_run():
    code = "\n".join("".join(cell["source"]) for cell in _cells() if cell["cell_type"] == "code")
    assert "search.fit" not in code
    assert "MultiStartProdigy" not in code
