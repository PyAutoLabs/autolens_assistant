---
title: Point-source lensing — positions, fluxes, time delays
sources:
  - project: PyAutoLens
    paths:
      - autolens/point/dataset.py
      - autolens/point/model/analysis.py
    pinned_commit: main
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/point/abstract.py
    pinned_commit: main
last_updated: 2026-05-22
---

# Point-source lensing

**Status: stub — content to be filled out.** This page introduces the
point-source regime in PyAutoLens: when the lensed source is effectively
a point (a quasar nucleus, an unresolved supernova, a faint compact
source whose extended structure is below the imaging resolution), the
observables are the **image positions** in the lens plane, optionally
augmented with **flux ratios** and **time delays** between images.

## What's different from extended-source lensing

Likelihood is built in the source plane: do all observed image positions
map back to a single source-plane point under the candidate mass model?
There's no PSF convolution, no pixelised inversion, no positions-penalty
trick — the positions *are* the data.

## The `PointDataset` and `AnalysisPoint` API

> TODO: walk through `al.PointDataset` (positions + uncertainties +
> optional fluxes + optional time delays) and the
> `al.AnalysisPoint(dataset=...)` log-likelihood definition. Cite
> `PyAutoLens:autolens/point/dataset.py` and
> `PyAutoLens:autolens/point/model/analysis.py`.

## Solving the lens equation for image positions

> TODO: image-position solvers (Newton vs. Frahm; PyAutoLens uses a
> grid + refinement). Discuss multiplicity (doubles, quads) and how
> magnification ratios are computed from the inverse-magnification
> matrix at each image.

## Flux ratios as a substructure probe

> TODO: flux-ratio anomalies and the link to subhalo / line-of-sight
> structure. Cross-reference [[substructure_and_subhalos]].

## Time delays

> TODO: time-delay formula in terms of the Fermat potential; lead-in to
> [[time_delay_cosmography]].

## Related pages

- [`api/datasets.md`](../api/datasets.md) — `PointDataset` row.
- [`api/analysis_objects.md`](../api/analysis_objects.md) — `AnalysisPoint` row.
- [`concepts/time_delay_cosmography.md`](./time_delay_cosmography.md).
- [`concepts/substructure_and_subhalos.md`](./substructure_and_subhalos.md).
