---
title: autolens_workspace — example catalogue routing
type: external_index
audience: experienced
source: https://github.com/PyAutoLabs/autolens_workspace
---

# autolens_workspace / lens

`PyAutoLabs/autolens_workspace` is the production-style example library: example and
tutorial scripts (with generated notebooks) organised by science case (imaging, group,
interferometer, point-source, cluster, multi-wavelength, weak) and difficulty
(`start_here` → modeling → features → advanced → results → simulators). Audience:
experienced lensing scientists and returning PyAutoLens users.

## Use the workspace's own generated catalogue as the source of truth

Do **not** recite per-script paths from this page or from memory — they drift. The
workspace repo ships a routing catalogue at its **repo root**, regenerated to stay in
sync with the actual files:

- **`llms.txt`** — compact, paste-sized routing layer ("Start here", "I want to…").
  Small enough to paste wholesale into a chat that cannot browse GitHub.
- **`llms-full.txt`** — the full per-script catalogue, one entry per example.
- **`workspace_index.json`** — the same listing, machine-readable.

When routing a user to an example, **resolve `autolens_workspace` the normal way**
(installed copy → sibling clone → clone-on-demand from [`sources.yaml`](../../../sources.yaml);
see [Source-of-truth resolution](../../../AGENTS.md)) and **read these catalogue files** to
find the current, correct path — rather than reproducing a path list here that goes stale.
`llms.txt` also defines the canonical routing answer shape (Start here → Then see →
Related guide → Why this is the right example → What to modify → What needs local
execution); follow it so this assistant and the workspace navigator agree.

**When to cite the workspace:**

- The user knows lensing and wants a working example to fork from.
- The user is mid-project and needs a concrete recipe for a feature (pixelization,
  MGE, subhalo search, multi-wavelength fit).
- A skill produces a script that is a direct adaptation of a workspace example.

**URL base** (derived from `sources.yaml`): `https://github.com/PyAutoLabs/autolens_workspace`.
Scripts live under `blob/main/scripts/<relative-path>`; the catalogue files
(`llms.txt`, `llms-full.txt`, `workspace_index.json`) live at the repo root. Get the
`<relative-path>` from the catalogue, then build the URL from this base.
