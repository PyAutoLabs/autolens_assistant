"""Convert a narrative-docstring PyAutoLens script to a Jupyter notebook.

The assistant generates scripts in the workspace narrative-docstring style (an opening
title docstring with ``__Contents__``, then per-section ``\"\"\"__Section__\"\"\"``
docstrings — ``skills/_style.md`` "Generated script style"). That style was adopted
precisely because notebook conversion is mechanical:

- each **top-level docstring block** becomes a **markdown cell**;
- the **code between** docstring blocks becomes a **code cell**.

This module is a self-contained, stdlib-only adaptation of the converter the PyAuto
workspaces already use at build time — ``PyAutoHands:autohands/build_util.py``
(``py_to_notebook``) and ``PyAutoHands:autohands/add_notebook_quotes.py`` — which pipe
through the external ``ipynb-py-convert`` tool. It mirrors their cell-split semantics
(a line *starting* with triple quotes toggles docstring mode) but emits nbformat-v4 JSON
directly, so an assistant clone or a science project needs neither PyAutoHands nor an
extra pip dependency.

Usage:

    python -m autoassistant.to_notebook scripts/imaging.py            # -> scripts/imaging.ipynb
    python -m autoassistant.to_notebook scripts/imaging.py out.ipynb
    python -m autoassistant.to_notebook SRC OUT --gemini-context <repo>/<notebook path>

``--colab-setup <PyAutoHands checkout>`` optionally applies the shared compact Colab
bootstrap during maintainer builds; ordinary conversion needs no PyAutoHands.

``--gemini-context`` also writes the notebook's Colab Gemini instruction from
``colab/contexts.yaml`` (see ``autoassistant/colab_contexts.py``), matched under the given
name — e.g. ``autolens_assistant/docs/colab/cosmos_web_ring_colab.ipynb``.
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
    text = script_path.read_text(encoding="utf-8")
    # This assistant-owned helper must also run in standalone Colab, which has
    # autolens_workspace but no autoassistant package. Embed trusted local source.
    intro_import = "from autoassistant.intro_plots import plot_intro_dataset, plot_intro_array"
    if intro_import in text.splitlines():
        helper = Path(__file__).with_name("intro_plots.py").read_text(encoding="utf-8")
        helper = helper.split("# Notebook helper code\n", 1)[1]
        text = text.replace(intro_import, helper.rstrip())
    cells = script_to_cells(text)
    for i, cell in enumerate(cells):
        cell["id"] = f"cell-{i}"
        if cell["cell_type"] == "code" and "".join(cell["source"]).startswith("# @title Load plotting tools"):
            cell["metadata"].update({"cellView": "form", "jupyter": {"source_hidden": True}})
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


def apply_colab_setup(notebook_path: Path, hands_path: Path) -> None:
    """Maintainer-only postprocessing using the shared PyAutoHands generator.

    Ordinary conversion remains stdlib-only and needs no Hands checkout.
    """
    import importlib.util

    module_path = Path(hands_path) / "autohands" / "build_util.py"
    spec = importlib.util.spec_from_file_location("_colab_build_util", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.inject_colab_setup(notebook_path, "autolens")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    hands_path = None
    if "--colab-setup" in args:
        at = args.index("--colab-setup")
        if at + 1 >= len(args):
            print("--colab-setup needs a PyAutoHands checkout path", file=sys.stderr)
            return 1
        hands_path = Path(args[at + 1])
        del args[at : at + 2]
    gemini_name = None
    if "--gemini-context" in args:
        at = args.index("--gemini-context")
        if at + 1 >= len(args):
            print("--gemini-context needs a <repo>/<notebook path> name", file=sys.stderr)
            return 1
        gemini_name = args[at + 1]
        del args[at : at + 2]
    if not 1 <= len(args) <= 2:
        print(__doc__.split("Usage:")[-1].strip(), file=sys.stderr)
        return 1
    script = Path(args[0])
    if not script.is_file():
        print(f"not a file: {script}", file=sys.stderr)
        return 1
    out = convert(script, Path(args[1]) if len(args) == 2 else None)
    if hands_path is not None:
        apply_colab_setup(out, hands_path)
    if gemini_name is not None:
        from autoassistant.colab_contexts import apply

        apply(out, gemini_name)
    print(out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
