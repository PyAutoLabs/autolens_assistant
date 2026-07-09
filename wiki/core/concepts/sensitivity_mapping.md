---
title: Sensitivity mapping for substructure detection
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/grid/sensitivity/
    pinned_commit: main
  - project: PyAutoLens
    paths:
      - autolens/lens
    pinned_commit: main
last_updated: 2026-07-09
---

# Sensitivity mapping

A subhalo detection is
informative; a subhalo *non-detection* is informative only if you know
what could have been detected. Sensitivity mapping answers that by
simulating the same dataset with subhaloes injected at many (y, x, mass)
positions, fitting each simulation with and without a subhalo, and
recording the evidence gain.

## The framework

PyAutoFit provides the generic engine in
`PyAutoFit:autofit/non_linear/grid/sensitivity/`. The key abstraction is
that you define:

- a `base_model` that represents the smooth lens fit
- a `perturb_model` that represents the extra component you want to test
- a simulation function that injects the perturbation into realistic mock data
- an analysis class that fits the simulated data

`Sensitivity.run()` then iterates over the perturbation prior grid,
simulates datasets, fits each with and without the perturbation, and
records the evidence difference. For lensing, the perturbation is usually
an extra dark perturber, but the same machinery is more general than
subhaloes.

## Choosing the grid

The grid should cover the region where the data are actually informative.
For strong-lens substructure work that usually means:

- positions spanning the arcs and their immediate surroundings
- masses large enough to matter for the angular resolution of the data
- spacing fine enough that narrow sensitive regions near critical curves
  are not missed

This is not a place for "whole detector" brute force. Most of the image
plane is insensitive, so a science-driven grid beats a symmetric but
wasteful one. In practice, the grid resolution is set by compute budget:
each cell is itself a pair of non-linear fits.

## Per-cell simulation realism

The simulations must look like the real observation, not like a generic
toy dataset. At minimum, that usually means matching:

- PSF or interferometric sampling
- pixel scale or visibility sampling
- noise level and noise correlations as closely as the workflow permits
- masking, oversampling, and inversion settings

Sensitivity maps are instrument- and dataset-specific. A map calibrated
for one HST image cannot simply be reused for a shallower JWST cutout or
for an ALMA visibility dataset of the same lens.

## From sensitivity to constraint

The map is not the end product. It becomes scientifically useful when
combined with a population model. Conceptually:

1. choose a model for the perturber population, for example a CDM or
   WDM subhalo mass function
2. forward-model how many perturbers that population should produce in
   the sensitive region of each lens
3. fold in the sensitivity map to predict the expected number of
   detections or non-detections
4. compare that prediction with the observed sample

That is why sensitivity mapping and hierarchical inference naturally go
together: the per-lens map is the calibration object, while the
population parameters are inferred across a sample.

## Compute cost

Sensitivity mapping is usually the most expensive workflow in this
workspace. Even a modest 10 x 10 position grid can imply hundreds of
simulations and hundreds of paired fits, often with pixelized sources.
Treat it as an HPC or batch-compute task by default. Operational guidance
is in [`../operations/hpc.md`](../operations/hpc.md).

## Related pages

- [`concepts/substructure_and_subhalos.md`](./substructure_and_subhalos.md).
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) — stacking
  sensitivity-calibrated constraints across a sample.
- [`api/aggregator.md`](../api/aggregator.md) — sensitivity output is a
  classic many-fits workload.
