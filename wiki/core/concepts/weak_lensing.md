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

Weak lensing is the
statistical regime — each background galaxy is barely sheared, but
across thousands of sources the coherent shear field traces the
foreground mass. PyAutoLens's weak-lensing module is intentionally
narrow: a `WeakDataset` (a shear catalogue with positions + γ1, γ2 +
errors) and an `AnalysisWeak` that compares the catalogue against a
model-predicted shear field.

## Observable: shear estimates per source

The raw observable is not "mass" but noisy estimates of source shape.
In real surveys those estimates come from a separate shape-measurement
pipeline, for example a moment-based or Bayesian ellipticity estimator.
PyAutoLens assumes that work has already been done and starts from the
catalog product:

- source positions on the sky
- shear or reduced-shear estimates, typically `gamma_1` and `gamma_2`
- uncertainties per source, often dominated by intrinsic shape noise

This is why the weak-lensing interface is compact. PyAutoLens is not a
full survey shear-measurement framework; it is the model-fitting layer
for an already prepared catalog.

## The likelihood

For a proposed mass model, the lens equation predicts the shear field at
each source position. The weak-lensing likelihood then compares the model
and observed shear components source by source, usually under a Gaussian
approximation in `(gamma_1, gamma_2)` with the catalog uncertainties as
the noise term.

This is a very different regime from strong-lens image fitting:

- no PSF-convolved image likelihood
- no pixelized inversion
- no explicit image-finding problem

The data volume can be large, but each source contributes only a small
amount of information.

## Cluster shear vs. cosmic shear

The weak module in this workspace is aimed at *lens-specific* weak
lensing, especially clusters and massive groups where the same mass model
should explain both the inner strong-lensing arcs and the outer shear
field. It is not intended to replace a dedicated cosmic-shear pipeline
for parameters like `S8`, survey masks, tomography, intrinsic alignments,
and survey-wide covariance modeling.

## Joint strong + weak

Joint strong-plus-weak fitting is where this module becomes most useful.
The strong-lens data constrain the inner critical region, while weak shear
extends the lever arm to much larger radii. In PyAutoFit terms this is
just another combined-analysis problem: one analysis for the arc data,
one for the weak catalog, one shared mass model.

## API touchpoints

The intended API surface is the `autolens/weak/` package:

- `PyAutoLens:autolens/weak/dataset.py` for the catalog container
- `PyAutoLens:autolens/weak/model/analysis.py` for the likelihood wrapper

The companion workspace example is `weak/fit.py`, which is the practical
reference for how the catalog is loaded and handed to the search.

## Related pages

- [`api/datasets.md`](../api/datasets.md) — the current dataset-page
  contrast with imaging, interferometer, and point-source fitting.
- [`concepts/group_and_cluster_lensing.md`](./group_and_cluster_lensing.md)
  — weak shear is most useful at cluster scale.
