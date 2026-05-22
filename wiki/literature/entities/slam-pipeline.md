---
title: SLaM (Strong Lens Automated Modelling) pipeline
type: entity
topics: [software, pipeline]
sources:
  - Strong_Lens/Etherington2022SLaM.pdf
  - Strong_Lens/Etherington2022BulgeHalo.pdf
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

## See also

- [[pyautolens]]
- [[pyautofit]]
- [[bulge-halo-decomposition]]
- [[sources-lens-modeling-methods]]
