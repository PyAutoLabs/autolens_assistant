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

A time-delay strong lens
constrains the **time-delay distance** D_dt, which combines three
angular-diameter distances (observer-lens, observer-source, lens-source)
and scales as ~ 1/H0. Fitting D_dt with the mass model lets you measure
H0 geometrically, independent of the local distance ladder.

## The Fermat potential

The basic observable is the arrival-time difference between two images of
the same variable source:

`Delta t_ij = (D_dt / c) [phi(theta_i, beta) - phi(theta_j, beta)]`

The Fermat potential `phi` has two pieces:

- a geometric delay from the extra path length of the bent ray
- a gravitational delay from the lens potential

Image positions constrain the stationary points of `phi`; time delays
constrain the *difference in height* between those stationary points.
That is why delay lenses are especially sensitive to the radial profile
of the mass model and to transformations that preserve image positions
but rescale the potential.

## What you measure vs. what you want

The inference chain is:

1. observe image positions and delay differences in days
2. fit a lens model that predicts the image geometry and the Fermat-potential differences
3. solve for `D_dt`, the distance factor needed to match the observed delays
4. translate `D_dt` into `H0` once the background cosmology is specified

At fixed `Omega_m`, dark-energy model, and spatial curvature, the
dominant scaling is `D_dt ~ 1 / H0`. A single precision delay lens
therefore gives a one-dimensional cosmology constraint; a sample of
lenses can be combined into a joint `H0` posterior or a broader
cosmological fit.

## The mass-sheet degeneracy

The dominant systematic is the mass-sheet degeneracy. Adding or
absorbing a nearly uniform convergence field can preserve image
positions while rescaling the source plane and the predicted time delays.
If unaccounted for, that directly rescales the inferred `H0`.

In practice, the phrase covers several closely related effects:

- an internal mass-sheet-like freedom in the lens parameterisation
- external convergence from the environment and line of sight
- profile choices that mimic a mass-sheet transform over the radial range
  actually probed by the data

The literature-side physics background is in
[`../../literature/concepts/mass-sheet-degeneracy.md`](../../literature/concepts/mass-sheet-degeneracy.md).

## Breaking the degeneracy

Time-delay cosmography is therefore never "delays only". Robust analyses
usually add one or more external anchors:

- stellar kinematics, typically a velocity-dispersion measurement, to
  constrain the enclosed three-dimensional mass
- composite or otherwise more physical mass models that reduce the
  freedom of a pure power-law fit
- environment and line-of-sight information to estimate external convergence
- multiple source planes or additional resolved arcs, when available

PyAutoLens can host these as extra likelihood terms or as a broader model
composition problem. In this workspace that usually means a
point-source fit for the delays plus a custom analysis term for
kinematics or environment information.

## API touchpoints

The core PyAutoLens objects are straightforward:

- `al.PointDataset(...)` stores `time_delays` and
  `time_delays_noise_map` alongside the image positions
- `al.AnalysisPoint(dataset=..., solver=...)` evaluates the delay
  likelihood together with any position and flux terms
- a lensing cosmology object from `PyAutoGalaxy:autogalaxy/cosmology/`
  supplies the distance conversion used by the `Tracer`

This means time-delay cosmography is not a separate solver stack. It is a
specialized point-source analysis in which the mass model, point-source
geometry, and cosmology are all coupled.

## Related pages

- [`concepts/point_source.md`](./point_source.md) — the underlying
  data shape and analysis class.
- [`concepts/cosmology_and_units.md`](./cosmology_and_units.md) —
  general cosmology framework PyAutoLens uses.
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) —
  joining a sample of delay lenses for a single H0.
