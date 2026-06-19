---
title: Joint lensing + kinematics
type: concept
topics: [methods, galaxy-structure]
sources:
  - Gebhardt et al. 2011 — M87 Gemini IFIS
  - Smith et al. 2017 — stellar dynamics IMF
  - Cao et al. 2021 — MaNGA lenses
status: drafted
---

# Joint lensing + kinematics

## TL;DR

The same potential that lenses light also confines stars. Combining
lensing constraints (mass within θ_E, angular structure) with stellar
kinematics (radial profile of σ) breaks the
[[mass-sheet-degeneracy]] and the [[radial-angular-degeneracy]],
giving the absolute radial mass profile.

## What it is

- Long-slit or IFU spectroscopy of the lens galaxy → spatially-resolved
  σ(R).
- Forward-model σ(R) under a chosen anisotropy parameterisation (Jeans /
  Schwarzschild).
- Joint Bayesian inference over the lens + dynamical model
  ([[pyautofit]] supports this via shared parameters).

## Why it matters

- **H0 cosmography** — kinematics is the primary route to closing the
  [[mass-sheet-degeneracy]] for TDCOSMO ([[tdcosmo]]).
- **GR tests** — the lensing/dynamics ratio probes γ_PPN
  ([[gr-tests|Collett 2018]]).
- **IMF / dark matter** — bulge-halo decomposition gains a second
  independent constraint on M(R).

## Datasets

- SDSS / MaNGA velocity dispersions for SLACS lenses (Cao 2021, Smith
  2017).
- IFU spectroscopy of TDCOSMO lenses (Birrer 2020 and follow-ups).
- ETG kinematics literature (ETGKine1, ETGKine2 — not currently in
  scope).

## See also

- [[bulge-halo-decomposition]]
- [[mass-sheet-degeneracy]]
- [[time-delay-cosmography]]
- [[gr-tests]]
- [[sources-kinematics]]
