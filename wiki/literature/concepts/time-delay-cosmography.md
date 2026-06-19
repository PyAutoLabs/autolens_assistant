---
title: Time-delay cosmography (H0 from strong lensing)
type: concept
topics: [cosmology]
sources:
  - Suyu et al. 2016 — Holicow
  - Birrer et al. 2018 — Holicow IX
  - Birrer et al. 2020 — TDCOSMOSIVH0
  - Wong et al. 2019 — H0licow6lenses
  - Grillo et al. 2018 — Refsdel Ho
status: drafted
---

# Time-delay cosmography

## TL;DR

When a multiply-imaged variable source (typically a lensed quasar or SN)
has measured time delays Δt between images, the absolute scale of the
lens — and hence the distance to the lens and source — becomes
measurable. This anchors the [[time-delay-distance|time-delay distance]]
D_Δt ∝ 1/H0. Strong-lensing H0 is independent of the distance ladder and
the CMB, so it is an important cross-check on the
[[hubble-tension|Hubble tension]].

## What it is

For a lens with deflection ψ and time-delay distance D_Δt,

```
Δt_ij = (D_Δt / c) · [φ(θ_i, β) − φ(θ_j, β)]
φ(θ, β) = ½ (θ − β)² − ψ(θ)
```

so a measured Δt and a modelled φ give D_Δt directly. Modelling
requirements:

- A precise mass model — the dominant residual systematic.
- An accurate [[external-convergence-shear|κ_ext]] estimate.
- Lens-galaxy [[kinematics-and-lensing|stellar velocity dispersion]] (to
  break the [[mass-sheet-degeneracy]]).
- Precise time-delay measurements (~few %).

## Programs

- [[h0licow]] — 6 lenses, ~2% H0 (Wong 2019).
- [[tdcosmo]] — successor; relaxed power-law assumption in 2020 (Birrer
  2020), getting ~8% H0 closer to Planck.
- [[refsdal-supernova|SN Refsdal]] — first time-delay cosmography from a
  supernova (Grillo 2018, Kelly 2023).
- Forthcoming: LSST hundreds of lensed quasars, Euclid + Roman ~10⁴
  quadruple lenses.

## The H0 tension and lensing

Pre-2020 lensing-only H0 was ~73–74 km/s/Mpc, in tension with Planck
(~67.5). TDCOSMO 2020, releasing the power-law assumption, broadened the
uncertainty to overlap Planck. Whether the tension is real or a
mass-model systematic remains active.

## Why it matters for PyAutoLens

- A PyAutoLens user doing cosmography must use a flexible mass model
  (composite or power-law with [[multipoles]]) and explicitly propagate
  κ_ext priors.
- Posteriors on D_Δt or H0 are end-to-end Bayesian — PyAutoFit chains
  the imaging fit, kinematics fit, and κ_ext prior together.

## See also

- [[mass-sheet-degeneracy]]
- [[external-convergence-shear]]
- [[kinematics-and-lensing]]
- [[lensed-supernovae]]
- [[h0licow]]
- [[tdcosmo]]
- [[sources-time-delay-cosmography]]
