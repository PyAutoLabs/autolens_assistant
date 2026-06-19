---
title: SLaM (Strong Lens Automated Modelling) pipeline
type: entity
topics: [software, pipeline]
sources:
  - Etherington et al. 2022 — S La M
  - Etherington et al. 2022 — Bulge Halo
status: drafted
---

# SLaM pipeline

## What it is

A canonical PyAutoLens pipeline that automates a sequence of chained
fits, taking a user from raw imaging to a [[bulge-halo-decomposition|composite
mass model]] without manual intervention. Phases include:

1. Mask + lens-light subtraction.
2. SIE + parametric source.
3. EPL (power-law) + parametric source.
4. EPL + pixelated source.
5. Composite (Sérsic-mass + NFW) + pixelated source.
6. Optional: [[multipoles|multipole]] + [[gravitational-imaging|subhalo
   scan]] phases.

Each phase passes its posterior as a prior to the next via PyAutoFit
search chaining ([[bayesian-inference-lensing]]).

## Canonical citation

**Etherington et al. 2022** — "Automated galaxy-galaxy strong lens
modelling: no lens left behind" (arXiv:2202.09201, MNRAS 517, 3275).
The "no lens left behind" demonstration on 59 HST lenses with ~1%
Einstein-radius precision is the production-validation paper for this
pipeline. Full read-up in
[[sources-lens-modeling-methods]].

## See also

- [[pyautolens]]
- [[pyautofit]]
- [[bulge-halo-decomposition]]
- [[sources-lens-modeling-methods]]
