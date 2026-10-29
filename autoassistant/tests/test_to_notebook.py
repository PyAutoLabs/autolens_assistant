"""Unit tests for the narrative-docstring script → notebook converter.

Fast and stdlib-only (json + tmp files): pins the cell-split semantics — docstring blocks
become markdown cells, code between becomes code cells — including the back-to-back
docstring case the PyAutoHands reference pipeline mis-renders (two adjacent markdown
cells, never a code cell containing literal `# %%`/`'''` markers).
"""

from __future__ import annotations

import json

from autoassistant.to_notebook import convert, script_to_cells

SCRIPT = '''"""
Title
=====

Intro prose with __Contents__.
"""

import autolens as al

"""
__Section One__

Explains the next code block.
"""

tracer = None  # code cell

"""
__Section Two__
"""

"""
__Back To Back__

A second docstring immediately after the first — must stay markdown.
"""

print("done")
'''


def test_cell_split_alternation():
    cells = script_to_cells(SCRIPT)
    kinds = [c["cell_type"] for c in cells]
    assert kinds == [
        "markdown",  # title
        "code",  # import
        "markdown",  # section one
        "code",  # tracer
        "markdown",  # section two
        "markdown",  # back-to-back stays markdown
        "code",  # print
    ]
    assert "__Section One__" in "".join(cells[2]["source"])
    joined = "".join("".join(c["source"]) for c in cells)
    assert "# %%" not in joined and "'''" not in joined


def test_convert_writes_valid_nbformat4(tmp_path):
    script = tmp_path / "example.py"
    script.write_text(SCRIPT, encoding="utf-8")
    out = convert(script)
    assert out == script.with_suffix(".ipynb")
    nb = json.loads(out.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4
    assert all("id" in c for c in nb["cells"])
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert all(c["outputs"] == [] and c["execution_count"] is None for c in code)


def test_ordinary_cli_does_not_load_hands(tmp_path, monkeypatch):
    import builtins
    from autoassistant.to_notebook import main

    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert "autohands" not in name and "build_util" not in name
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    source = tmp_path / "example.py"
    source.write_text(SCRIPT)
    assert main([str(source)]) == 0


def test_optional_hands_pipeline_bootstraps_fresh_colab(tmp_path, monkeypatch):
    import builtins
    import importlib
    import os
    import subprocess
    from types import SimpleNamespace

    import pytest
    from autoassistant.to_notebook import main

    hands = os.environ.get("PYAUTOHANDS_PATH")
    if not hands:
        pytest.skip("maintainer integration requires PYAUTOHANDS_PATH checkout")
    source = tmp_path / "cosmos_web_ring_colab.py"
    source.write_text(
        '"""Title\n\n__Google Colab Setup__\n\nOld setup text.\n"""\n'
        'from autolens import setup_colab\n'
        'setup_colab.setup("autolens", raise_error_if_not_gpu=False)\n'
    )
    assert main([str(source), "--colab-setup", hands]) == 0
    notebook = json.loads(source.with_suffix(".ipynb").read_text())
    cell = notebook["cells"][1]
    assert cell["metadata"]["cellView"] == "form"
    events = []
    setup = SimpleNamespace(setup=lambda *args, **kwargs: events.append((args, kwargs)))
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "google.colab":
            return SimpleNamespace()
        assert name != "autolens", "fresh Colab must install before importing PyAutoLens"
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(subprocess, "check_call", lambda command: events.append(command))
    monkeypatch.setattr(importlib, "import_module", lambda name: setup)
    exec("".join(cell["source"]), {})
    assert events[0][-3:] == ["install", "autonerves", "--no-deps"]
    assert events[1] == (("autolens",), {"raise_error_if_not_gpu": False})
