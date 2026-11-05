"""Pin `colab/contexts.yaml` and the Colab Gemini instruction the COSMOS-Web Ring notebook carries.

Stdlib + PyYAML, fast: nothing is executed.
"""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from autoassistant import colab_contexts

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = REPO_ROOT / "docs" / "colab" / "cosmos_web_ring_colab.ipynb"
NOTEBOOK_NAME = "autolens_assistant/docs/colab/cosmos_web_ring_colab.ipynb"


def test_mapping_is_sound():
    assert colab_contexts.check() == []


def test_cosmos_notebook_maps_to_the_greeting():
    label, skills = colab_contexts.match(colab_contexts.load(), NOTEBOOK_NAME)
    assert label == NOTEBOOK_NAME
    assert skills[0] == "al_greeting_cosmos_web_ring"


def test_context_id_matches_pyautohands():
    # PyAutoHands' build_util.gemini_context_id derives ids the same way: one id per project.
    assert colab_contexts.context_id("autolens") == str(
        uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/PyAutoLabs/colab-gemini/autolens")
    )


def test_committed_notebook_carries_the_current_instruction(tmp_path):
    copy = tmp_path / NOTEBOOK.name
    shutil.copy(NOTEBOOK, copy)
    colab_contexts.apply(copy, NOTEBOOK_NAME)
    assert copy.read_text(encoding="utf-8") == NOTEBOOK.read_text(encoding="utf-8"), (
        "docs/colab/cosmos_web_ring_colab.ipynb carries a stale Gemini instruction: run "
        f"`python -m autoassistant.colab_contexts apply {NOTEBOOK.relative_to(REPO_ROOT)} "
        f"--name {NOTEBOOK_NAME}` (metadata only, no re-execution)"
    )
    colab = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["metadata"]["colab"]
    assert colab["selectedAiContext"] in colab["aiContexts"]


def test_apply_changes_metadata_only(tmp_path):
    notebook = {
        "cells": [{"cell_type": "markdown", "id": "cell-0", "metadata": {}, "source": ["Hi é"]}],
        "metadata": {"colab": {"provenance": []}, "kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path = tmp_path / "x.ipynb"
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    colab_contexts.apply(path, NOTEBOOK_NAME)
    colab_contexts.apply(path, NOTEBOOK_NAME)  # idempotent
    stamped = json.loads(path.read_text())
    assert stamped["cells"] == notebook["cells"]
    assert stamped["metadata"]["colab"]["provenance"] == []
    assert len(stamped["metadata"]["colab"]["aiContexts"]) == 1
    assert path.read_text().endswith("}\n") and "Hi é" in path.read_text()
