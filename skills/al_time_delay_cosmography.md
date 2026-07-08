---
name: al_time_delay_cosmography
description: Measure H0 (or a Hubble-like time-delay distance) from a time-delay strong lens — quasar with measured delays between multiple images, or a lensed supernova. Builds on `al_point_source` (positions + delays) and `al_hierarchical_inference` (when joining several lenses into one H0 posterior). The headline observable is the **time-delay distance** D_dt, which scales inversely with H0 at fixed mass model. Writes a runnable Python script in scripts/. **Status: stub.**
---

# H0 from time-delay strong lensing

A time-delay lens lets you measure cosmological distances geometrically:
the photon travel-time difference between two images of a variable source
depends on the lens potential (the mass model) **and** the time-delay
distance D_dt, which is a combination of angular-diameter distances and
scales as ~ 1/H0. Fit the mass model to positions + delays, and the
remaining unknown is cosmology.

This is what H0LiCOW, TDCOSMO, and STRIDES measure. The workspace path is
`autolens_workspace:scripts/point_source/features/time_delays.py`.

## Ask

- *"What's the input — a single lens with measured delays, or a sample
  you'll combine hierarchically?"* Sample-level joins go through
  [`al_hierarchical_inference`](./al_hierarchical_inference.md).
- *"How precise are the delay measurements (days, with uncertainty)?"*
  This sets whether the cosmology constraint will be tight enough to
  matter.
- *"Mass model — power-law (the field standard for delay lenses) or
  composite (stars + dark matter, less degenerate with mass-sheet
  transform)?"*
- *"Are you marginalising over the mass-sheet transform, or assuming a
  specific resolution (kinematics, line-of-sight)?"* This is the
  biggest systematic in the field.

## Branch — single delay lens, power-law mass

> TODO: recipe. The pattern wraps a `PointDataset` with measured `time_delays`
> and a power-law mass model; cosmology is folded in as a fitted parameter
> on the cosmology object passed to the `Tracer`. See
> `PyAutoLens:autolens/point/dataset.py` for the dataset shape and
> `PyAutoGalaxy:autogalaxy/cosmology/*` for the cosmology parameterisation.

## Branch — joint with kinematic constraint (mass-sheet breaker)

Folds in an independent velocity-dispersion measurement to break the
mass-sheet degeneracy. Adds a custom likelihood term — see
[`al_custom_analysis`](./al_custom_analysis.md).

> TODO: recipe.

## Combine

- [`al_point_source`](./al_point_source.md) — the underlying point-source
  fit this skill builds on.
- [`al_hierarchical_inference`](./al_hierarchical_inference.md) —
  combining a sample of lenses into a single H0 posterior.
- [`al_custom_analysis`](./al_custom_analysis.md) — adding a kinematic
  likelihood term.

## Further reading

- **Student / new to lensing** — [HowToLens: chapter_5_point_source](https://github.com/PyAutoLabs/HowToLens/tree/main/notebooks/chapter_5_point_source):
  point-source lensing tutorials, foundation for time-delay analyses.
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  feature tour — point-source / time-delay section.
- **Experienced PyAutoLens user** — [workspace/lens: point_source/features/time_delays.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/point_source/features/time_delays.py):
  the canonical H0 workflow.

See also [`wiki/core/concepts/time_delay_cosmography.md`](../wiki/core/concepts/time_delay_cosmography.md)
for the physics and the mass-sheet degeneracy.
