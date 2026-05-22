---
title: Weak lensing in PyAutoLens
sources:
  - project: PyAutoLens
    paths:
      - autolens/weak
    pinned_commit: main
last_updated: 2026-05-22
---

# Weak lensing

**Status: stub — content to be filled out.** Weak lensing is the
statistical regime — each background galaxy is barely sheared, but
across thousands of sources the coherent shear field traces the
foreground mass. PyAutoLens's weak-lensing module is intentionally
narrow: a `WeakDataset` (a shear catalogue with positions + γ1, γ2 +
errors) and an `AnalysisWeak` that compares the catalogue against a
model-predicted shear field.

## Observable: shear estimates per source

> TODO: how shear is measured in practice (KSB, Bayesian model fitting),
> what the inputs to `WeakDataset` should look like.

## The likelihood

> TODO: Gaussian residual on (γ1, γ2) at each source position, with the
> shear measurement uncertainty as σ. No PSF, no inversion, no positions
> penalty.

## Cluster shear vs. cosmic shear

> TODO: PyAutoLens's weak module is aimed at cluster-scale fits where
> the lens mass is the unknown. Cosmic-shear cosmology (Σ_8, S_8)
> requires a much larger framework and is not the workspace's focus.

## Joint strong + weak

> TODO: sum the strong-lens log-likelihood and the weak-lens
> log-likelihood; shared mass model across both. Powerful for clusters
> where arcs pin the inner profile and the shear field pins the outer.

## API touchpoints

> TODO: cite `PyAutoLens:autolens/weak/dataset.py` (verify path) and
> `PyAutoLens:autolens/weak/model/analysis.py`.

## Related pages

- [`api/datasets.md`](../api/datasets.md) — `WeakDataset` row (TBD when
  added).
- [`concepts/group_and_cluster_lensing.md`](./group_and_cluster_lensing.md)
  — weak shear is most useful at cluster scale.
