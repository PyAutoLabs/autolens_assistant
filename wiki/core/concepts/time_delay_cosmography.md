---
title: Time-delay cosmography — H0 from strong lensing
sources:
  - project: PyAutoLens
    paths:
      - autolens/point/dataset.py
      - autolens/point/model/analysis.py
    pinned_commit: main
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/cosmology
    pinned_commit: main
last_updated: 2026-05-22
---

# Time-delay cosmography

**Status: stub — content to be filled out.** A time-delay strong lens
constrains the **time-delay distance** D_dt, which combines three
angular-diameter distances (observer-lens, observer-source, lens-source)
and scales as ~ 1/H0. Fitting D_dt with the mass model lets you measure
H0 geometrically, independent of the local distance ladder.

## The Fermat potential

> TODO: Δt_ij = (D_dt / c) · [φ(θ_i, β) − φ(θ_j, β)], where φ is the
> Fermat potential combining geometric and gravitational delay.

## What you measure vs. what you want

> TODO: lay out the chain from observed delays + image positions →
> Fermat potential differences → D_dt → H0 at fixed Ω_m, w.

## The mass-sheet degeneracy

> TODO: the dominant systematic. A constant convergence sheet
> reparameterises the mass model without changing image positions or
> flux ratios, but rescales every time delay by the same factor — and
> hence rescales the inferred H0. Cross-reference
> [[mass_sheet_degeneracy]] (literature wiki).

## Breaking the degeneracy

> TODO: kinematic measurements (velocity dispersion), explicit
> composite mass models (stars + DM), independent line-of-sight
> constraints.

## API touchpoints

> TODO: `PointDataset` with `time_delays` populated; `AnalysisPoint`
> log-likelihood; cosmology object plumbed through the `Tracer`.

## Related pages

- [`concepts/point_source.md`](./point_source.md) — the underlying
  data shape and analysis class.
- [`concepts/cosmology_and_units.md`](./cosmology_and_units.md) —
  general cosmology framework PyAutoLens uses.
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) —
  joining a sample of delay lenses for a single H0.
