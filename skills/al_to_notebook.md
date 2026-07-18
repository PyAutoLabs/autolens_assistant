---
name: al_to_notebook
description: Convert a generated narrative-docstring PyAutoLens script (.py) into a Jupyter notebook (.ipynb) — each top-level docstring becomes a markdown cell, the code between becomes code cells. Use when the user says "turn this into a notebook", "convert to ipynb", or wants a Jupyter/Colab version of a script the assistant produced.
user-invocable: true
---

# Script → notebook

Generated scripts follow the workspace narrative-docstring style (`_style.md` "Generated
script style") precisely so this conversion is mechanical: each top-level `"""` docstring
block becomes a **markdown cell**; the Python between blocks becomes a **code cell**.

## Orient

The converter is `autoassistant/to_notebook.py` — stdlib-only, no external tools. It adapts
the converter the PyAuto workspaces use at build time (`PyAutoHands:autobuild/build_util.py`
`py_to_notebook` + `add_notebook_quotes.py`) and mirrors its cell-split semantics. In a
science project, run it from the resolved assistant clone (refer-back).

## Ask

Nothing, usually — the script to convert is normally the one just produced. Ask only if
several candidate scripts are in play.

## Branch — convert

```bash
python -m autoassistant.to_notebook scripts/<name>.py            # -> scripts/<name>.ipynb
python -m autoassistant.to_notebook scripts/<name>.py <out>.ipynb
```

(From a science project: `python <resolved-assistant>/autoassistant/to_notebook.py …` works
identically.) The CLI prints the absolute output path — quote it and offer to open it.

- The script must be in the narrative-docstring style; a script of bare comments converts to
  one big code cell (correct, but probably not what the user wanted — say so).
- The notebook is **generated output**: never hand-edit the `.ipynb`; edit the `.py` and
  reconvert. Keep the script the committed source of truth unless the user explicitly wants
  the notebook tracked (e.g. a shared/Colab-facing artifact in a science project).

## Combine

- A converted notebook in a science project pairs well with the shareable-repo story
  (`start-new-project.md` Collaborate/Publish): reviewers and collaborators often prefer
  opening a notebook to running a script.
- For workspace-published notebooks (Colab setup cells, magic handling), the build pipeline
  in PyAutoHands remains authoritative — this skill is for assistant/project scripts.
