---
title: Weak lensing in PyAutoLens
sources:
  - project: PyAutoLens
    paths:
      - autolens/weak
    pinned_commit: main
last_updated: 2026-07-09
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

## Shear vs. reduced shear (`is_reduced`)

What a survey actually measures from galaxy shapes is not the shear
`gamma` but the **reduced shear** `g = gamma / (1 - kappa)` — the
convergence `kappa` rescales the observed ellipticity. Far from the lens
the two converge, but near a cluster core the difference is real.
`WeakDataset` carries an `is_reduced` flag and `FitWeak` computes the
matching model quantity, so the comparison is always like-for-like. The
catalogue loaders (`from_csv`, `from_fits`, `from_arrays`) default to
`is_reduced=True` because real catalogues are ellipticity-based; only the
bare constructor defaults to `False`.

## Joint strong + weak

Joint strong-plus-weak fitting is where this module becomes most useful.
The strong-lens data constrain the inner critical region, while weak shear
extends the lever arm to much larger radii. Because the two datasets are
independent measurements of the same mass distribution, the joint log
likelihood is simply the sum: one `Tracer` shared between a `FitImaging`
and a `FitWeak`, or between an `AnalysisImaging` and an `AnalysisWeak`
in a combined-analysis fit. The workspace has a dedicated
strong-plus-weak feature series at
`autolens_workspace:scripts/weak/features/strong_lensing/`
(`simulator.py` → `fit.py` → `modeling.py`).

## API touchpoints

The API surface is the `autolens/weak/` package:

- **`al.WeakDataset`** (`PyAutoLens:autolens/weak/dataset.py`) — the
  catalogue container: irregular source positions with per-source
  `(gamma_1, gamma_2)` and noise, optional redshifts, the `is_reduced`
  flag, and `from_csv` / `from_fits` / `from_arrays` loaders.
- **`al.FitWeak`** (`PyAutoLens:autolens/weak/fit.py`) — fits a `Tracer`
  to the catalogue: `model_shear`, `residual_map`,
  `normalized_residual_map`, `chi_squared`, `log_likelihood`,
  `figure_of_merit`. Deliberately NumPy-first — weak fits are cheap
  enough that no GPU/JAX path is needed.
- **`al.AnalysisWeak`** (`PyAutoLens:autolens/weak/model/`) — wraps
  `FitWeak` in the PyAutoFit likelihood interface so any non-linear
  search can sample the mass model.

The workspace series mirrors the imaging one:
`autolens_workspace:scripts/weak/` has `simulator.py`, `fit.py`
(hand-picked model + residuals), `modeling.py` (full Nautilus fit — N=5
in minutes on a CPU), and `likelihood_function.py`.

## Real catalogues — the Abell 2744 capstone

`autolens_workspace:scripts/weak/real_data/a2744.py` fits a dark-matter
halo model to a real JWST-era shape catalogue of Abell 2744 (from the
public pyRRG code; Harvey & Massey 2024, MNRAS 529, 802). It is the
practical template for any new catalogue: load a FITS shape table,
convert RA/Dec to tangent-plane arcseconds, apply the standard
weak-lensing quality cuts, build a `WeakDataset` with `is_reduced=True`,
and sanity-check the result against a model-independent Kaiser-Squires
mass map before trusting any parametric fit.

## Related pages

- [`api/datasets.md`](../api/datasets.md) — the current dataset-page
  contrast with imaging, interferometer, and point-source fitting.
- [`concepts/group_and_cluster_lensing.md`](./group_and_cluster_lensing.md)
  — weak shear is most useful at cluster scale.
