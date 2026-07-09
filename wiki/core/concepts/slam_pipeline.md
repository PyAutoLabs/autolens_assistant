---
title: SLaM pipeline — Source, Light, Mass
sources:
  - project: autolens_workspace
    paths:
      - scripts/guides/modeling/slam_start_here.py
    pinned_commit: main
last_updated: 2026-07-09
---

# SLaM pipeline — Source, Light, Mass

SLaM is the canonical automated lens-modelling workflow for PyAutoLens. It chains
four or more non-linear searches, each focused on one slice of the model, with
priors passed forward so each later phase starts from a near-correct initialisation.

The acronym names the three model components SLaM disentangles:

- **Source** — the source-plane light (parametric, then pixelised).
- **Light** — the lens galaxy's own light.
- **Mass** — the lens galaxy's mass model.

Canonical reference: `autolens_workspace:scripts/guides/modeling/slam_start_here.py`.
Treat that file as the template; every other workspace SLaM script ("group SLaM",
"interferometer SLaM", "subhalo SLaM") is described relative to it.

## Why it exists

A 20+ parameter lens model with a pixelised source is hard to fit from scratch:

- Wide priors mean the search wastes time exploring nonsense.
- Pixelised sources are vulnerable to demagnification modes if mass is wrong.
- Lens light and lens mass are partially degenerate; fitting both at once is
  fragile.

SLaM untangles these by fitting cheaper sub-problems first and passing their answers
forward.

## Stages

The standard SLaM pipeline (covered in `slam_start_here.py`) has four stages:

### 1. SOURCE LP

A fast parametric source fit. Lens mass: SIE + shear. Source: parametric Sersic
(often `SersicCore` to avoid central divergence). Lens light: simple (single Sersic
or skipped).

Goal: get a rough mass model and source position. The result is mostly thrown away
except for the mass model + adapt image (the lens-light-subtracted image used in
later phases to drive adaptive regularisation).

### 2. SOURCE PIX (×2 searches)

Two-step pixelised source fit. Switches the source from a parametric Sersic to a
pixelised inversion (e.g. Delaunay mesh with adaptive regularisation). Lens mass is
held loosely close to the SOURCE LP result.

The first search initialises the pixelisation hyperparameters; the second refines
them with the final mesh resolution and regularisation scheme.

Goal: a high-fidelity source reconstruction without the mass model running off.

### 3. LIGHT LP

Fit a complex lens-light model on top — typically a Multi-Gaussian Expansion with
many basis Gaussians. Mass and source are held close to the SOURCE PIX result.

Goal: separate lens light from lensed source light. The high-component MGE captures
complex lens galaxy morphology that a single Sersic can't.

### 4. MASS TOTAL

Fit a more complex mass model (PowerLaw, PowerLawMultipole, decomposed Light+Dark)
with lens light and source held close.

Goal: the final, publication-quality mass model.

Some pipelines add a **MASS LIGHT DARK** phase that decomposes mass into stellar
(tied to the LIGHT LP profile) and dark (NFW) components.

## Prerequisites for using SLaM

- Comfortable with [`non_linear_search`](./non_linear_search.md) — especially prior
  chaining.
- Familiar with [`inversions_and_pixelizations`](./inversions_and_pixelizations.md).
- Have measured image positions (for the positions likelihood penalty during
  SOURCE PIX).

If you're not yet at that depth, start with
[`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md)
+ [`../../../skills/al_run_search.md`](../../../skills/al_run_search.md). SLaM is
production tooling, not an introductory workflow.

## How to actually run it

The SLaM driver functions live in the workspace, not in PyAutoLens itself — defined
**inline** in `autolens_workspace:scripts/guides/modeling/slam_start_here.py` (the
canonical reference for pipeline structure and function signatures; there is no
separate `slam/` package). Per-topic SLaM examples live under each topic's
`features/slam/` folder. From a workspace clone:

```bash
# The pipeline stages (source_lp -> source_pix -> light -> mass) are plain
# functions defined inline in the script; copy it and adapt the stages.
python scripts/guides/modeling/slam_start_here.py
```

See [`../../../skills/al_run_slam_pipeline.md`](../../../skills/al_run_slam_pipeline.md).

## Outputs

Each phase writes its own `output/<path_prefix>/<phase_name>/<unique_id>/` folder.
The MASS TOTAL output is usually the final answer; the SOURCE PIX folder contains
the canonical pixelised reconstruction.

Load each phase separately with
[`../../../skills/al_load_results.md`](../../../skills/al_load_results.md). It's normal to
inspect SOURCE PIX (for the source) and MASS TOTAL (for the mass model) in different
sessions.

## See also

- [`../../../skills/al_run_slam_pipeline.md`](../../../skills/al_run_slam_pipeline.md).
- `autolens_workspace:scripts/guides/modeling/slam_start_here.py` — canonical
  reference.
- [`non_linear_search`](./non_linear_search.md) — the prior-chaining mechanism.
