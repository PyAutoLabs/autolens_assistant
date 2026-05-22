---
title: External convergence and shear
type: concept
topics: [systematics, environment]
sources:
  - Strong_Lens/Wong2011ShearEnvironment.pdf
  - Strong_Lens/Birrer2019ShearWLSL.pdf
  - Strong_Lens/Fleury2022LosShear.pdf
  - Strong_Lens/Chirivi2017_Lineofsight_Clusters.pdf
status: drafted
---

# External convergence and shear

## TL;DR

The mass between the observer and the source — and **not** in the lens
galaxy — perturbs the lensing signal. A constant sheet adds external
convergence κ_ext (rescales the mass-sheet, see
[[mass-sheet-degeneracy]]). A tidal field adds external shear γ_ext.
Both are mandatory in any high-precision lens model.

## What it is

- κ_ext is estimated by counting galaxies along the LOS to the lens
  (Suyu / Rusu method) and calibrating against ray-traced cosmological
  simulations like Millennium.
- γ_ext is fit directly from the image as a two-parameter constant shear,
  but is partially degenerate with lens ellipticity (see
  [[shear-ellipticity-degeneracy]]).
- LOS halos beyond the leading-order κ_ext, γ_ext add higher-order
  perturbations (flexion-like terms; Fleury 2022; Birrer 2019; Chirivi 2017
  for clusters).

## Why it matters

- H0 from time delays scales with (1 − κ_ext). Mis-estimating κ_ext by
  Δκ propagates linearly to ΔH0/H0 = -Δκ.
- LOS halos contribute to apparent [[dark-matter-substructure|substructure
  signal]] at the ~10–50% level (Despali 2018, He 2021).
- [[lens-statistics|Population statistics]] inherit a bias if LOS effects
  are not modelled.

## See also

- [[mass-sheet-degeneracy]]
- [[time-delay-cosmography]]
- [[line-of-sight-effects]]
- [[shear-ellipticity-degeneracy]]
- [[sources-external-shear-los]]
