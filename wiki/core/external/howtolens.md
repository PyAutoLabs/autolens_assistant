---
title: HowToLens — lecture catalogue routing
type: external_index
audience: student
source: https://github.com/PyAutoLabs/HowToLens
---

# HowToLens

HowToLens teaches strong lensing **from first principles**, assuming minimal prior
astronomy or statistics knowledge — four chapters of tutorials (plus an optional
chapter), delivered as parallel Jupyter notebooks and Python scripts. Primary
audience: students new to gravitational lensing or to Bayesian inference.

## Use HowToLens's own generated catalogue as the source of truth

Do **not** recite per-tutorial titles or paths from this page or from memory — they
drift. HowToLens ships a routing catalogue at its **repo root**, regenerated to stay in
sync with the actual tutorials:

- **`llms.txt`** — compact, paste-sized routing layer ("Start here", the learning path
  by chapter, "I want to understand…"). Small enough to paste wholesale into a chat
  that cannot browse GitHub.
- **`llms-full.txt`** — the full per-tutorial catalogue, one entry per tutorial with its
  title and one-line summary.
- **`workspace_index.json`** — the same listing, machine-readable.

When routing a student to a tutorial, **resolve `HowToLens` the normal way** (installed
copy → sibling clone → clone-on-demand from [`sources.yaml`](../../../sources.yaml); see
[Source-of-truth resolution](../../../AGENTS.md)) and **read these catalogue files** to
find the current tutorial — rather than reproducing a list here that goes stale.
`llms.txt` also defines the routing answer shape (Start here → Then see → Related guide →
Why → What to modify → What needs local execution), shared with the workspace navigator
so the lecture and example routing agree.

**When to cite HowToLens:**

- The user is new to gravitational lensing, or new to Bayesian non-linear inference.
- The user wants the physics derivation or conceptual grounding behind something a skill
  is using (ray tracing, regularization, search chaining, inversions).
- Lead with the **notebook** URL (more interactive); offer the script URL if the user
  prefers reading. Once a learner wants to model their own data, route them onward to
  [`workspace.md`](./workspace.md) (the production examples).

**URL base** (derived from `sources.yaml`): `https://github.com/PyAutoLabs/HowToLens`.
Tutorials live under `blob/main/notebooks/<chapter>/<tutorial>.ipynb` (notebook) and
`blob/main/scripts/<chapter>/<tutorial>.py` (script); the catalogue files (`llms.txt`,
`llms-full.txt`, `workspace_index.json`) live at the repo root. Get the
`<chapter>/<tutorial>` from the catalogue, then build the URL from this base.
