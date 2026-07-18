"""Convert a narrative-docstring PyAutoLens script to a Jupyter notebook.

The assistant generates scripts in the workspace narrative-docstring style (an opening
title docstring with ``__Contents__``, then per-section ``\"\"\"__Section__\"\"\"``
docstrings — ``skills/_style.md`` "Generated script style"). That style was adopted
precisely because notebook conversion is mechanical:

- each **top-level docstring block** becomes a **markdown cell**;
- the **code between** docstring blocks becomes a **code cell**.

This module is a self-contained, stdlib-only adaptation of the converter the PyAuto
workspaces already use at build time — ``PyAutoHands:autobuild/build_util.py``
(``py_to_notebook``) and ``PyAutoHands:autobuild/add_notebook_quotes.py`` — which pipe
through the external ``ipynb-py-convert`` tool. It mirrors their cell-split semantics
(a line *starting* with triple quotes toggles docstring mode) but emits nbformat-v4 JSON
directly, so an assistant clone or a science project needs neither PyAutoHands nor an
extra pip dependency.

Usage:

    python -m autoassistant.to_notebook scripts/imaging.py            # -> scripts/imaging.ipynb
    python -m autoassistant.to_notebook scripts/imaging.py out.ipynb
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_TRIPLE = ('"""', "'''")


def _cell(cell_type: str, lines: list[str]) -> dict:
    """Build one nbformat-v4 cell; every source line keeps its newline except the last."""
    while lines and lines[-1].strip() == "":
        lines.pop()
    while lines and lines[0].strip() == "":
        lines.pop(0)
    source = [line + "\n" for line in lines]
    if source:
        source[-1] = source[-1].rstrip("\n")
    cell: dict = {"cell_type": cell_type, "metadata": {}, "source": source}
    if cell_type == "code":
        cell.update({"execution_count": None, "outputs": []})
    return cell


def script_to_cells(text: str) -> list[dict]:
    """Split narrative-docstring script text into alternating markdown/code cells."""
    cells: list[dict] = []
    buffer: list[str] = []
    in_docstring = False

    def flush(cell_type: str) -> None:
        nonlocal buffer
        if any(line.strip() for line in buffer):
            cells.append(_cell(cell_type, buffer))
        buffer = []

    for line in text.splitlines():
        stripped = line.lstrip()
        starts = stripped.startswith(_TRIPLE) and stripped == line  # top-level only
        if starts and not in_docstring and len(line) > 6 and line.rstrip().endswith(line[:3]):
            # Single-line docstring, e.g. """__Section__""" — one markdown cell.
            flush("code")
            cells.append(_cell("markdown", [line.strip()[3:-3]]))
            continue
        if starts:
            flush("markdown" if in_docstring else "code")
            in_docstring = not in_docstring
            continue
        buffer.append(line)
    flush("markdown" if in_docstring else "code")
    return cells


def convert(script_path: Path, notebook_path: Path | None = None) -> Path:
    """Convert ``script_path`` to a notebook; returns the notebook path."""
    script_path = Path(script_path)
    if notebook_path is None:
        notebook_path = script_path.with_suffix(".ipynb")
    cells = script_to_cells(script_path.read_text(encoding="utf-8"))
    for i, cell in enumerate(cells):
        cell["id"] = f"cell-{i}"
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    Path(notebook_path).write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return Path(notebook_path)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not 1 <= len(args) <= 2:
        print(__doc__.split("Usage:")[-1].strip(), file=sys.stderr)
        return 1
    script = Path(args[0])
    if not script.is_file():
        print(f"not a file: {script}", file=sys.stderr)
        return 1
    out = convert(script, Path(args[1]) if len(args) == 2 else None)
    print(out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
