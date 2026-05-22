---
title: Sensitivity mapping for substructure detection
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/grid/sensitivity.py
    pinned_commit: main
  - project: PyAutoLens
    paths:
      - autolens/lens
    pinned_commit: main
last_updated: 2026-05-22
---

# Sensitivity mapping

**Status: stub — content to be filled out.** A subhalo detection is
informative; a subhalo *non-detection* is informative only if you know
what could have been detected. Sensitivity mapping answers that by
simulating the same dataset with subhaloes injected at many (y, x, mass)
positions, fitting each simulation with and without a subhalo, and
recording the evidence gain.

## The framework

> TODO: PyAutoFit's `Sensitivity` class wraps a `(simulator, base_analysis,
> perturbed_analysis, perturbed_grid)` quadruple; per-cell it simulates,
> fits both, and emits a Δlog-evidence. Cite
> `PyAutoFit:autofit/non_linear/grid/sensitivity.py`.

## Choosing the grid

> TODO: spatial extent (where the arcs are), mass range (1e7–1e10
> M_sun typical), grid resolution vs. compute budget.

## Per-cell simulation realism

> TODO: noise matched to the real data, PSF matched, exposure matched.
> The point of the calibration is that the sensitivity map applies to
> *this* observation, not a generic one.

## From sensitivity to constraint

> TODO: how a sensitivity map combines with a population-level subhalo
> mass function to yield an upper limit on, e.g., the WDM particle mass
> or the subhalo abundance.

## Compute cost

> TODO: sensitivity is the heaviest PyAutoLens workflow; expect HPC.
> Reference [`operations/hpc.md`](../operations/hpc.md).

## Related pages

- [`concepts/substructure_and_subhalos.md`](./substructure_and_subhalos.md).
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) — stacking
  sensitivity-calibrated constraints across a sample.
- [`api/aggregator.md`](../api/aggregator.md) — sensitivity output is a
  classic many-fits workload.
