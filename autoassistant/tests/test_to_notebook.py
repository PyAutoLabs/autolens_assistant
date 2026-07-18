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
