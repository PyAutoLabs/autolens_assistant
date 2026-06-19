---
title: Angular multipoles in lens mass models
type: concept
topics: [lens-modelling, systematics]
sources:
  - Chu et al. 2013 — Multipoles
  - Cohen et al. 2024 — Multipoles
  - Stacey et al. 2024 — Multipoles ALMA
  - Amvrosiadis et al. 2025 — M1 Multipole
  - ORiodan et al. 2024 — Angularcomplexity
  - vandevyree et al. 2022 — Azimuthal
  - vandevyree et al. 2022 — Boxyness Discyness
status: drafted
---

# Angular multipoles

## TL;DR

Beyond the elliptical power-law lies a hierarchy of angular harmonics
(m = 1 lopsidedness, m = 3 isophotal twist, m = 4 boxiness / disciness).
Lens galaxies show all of these at observable amplitudes; omitting them
biases recovered mass-model parameters and contaminates
[[dark-matter-substructure|substructure inference]] at a level
comparable to the signal itself.

## What it is

Decompose the convergence as:

```
κ(θ, φ) = κ_0(θ) + Σ_m a_m(θ) cos(m(φ − φ_m))
```

Common terms:

- m = 1 — lopsidedness (Amvrosiadis 2025).
- m = 3 — isophotal twist; produces image-position residuals at the
  ~milliarcsecond level.
- m = 4 — boxy / discy; common in massive ellipticals (van de Vyvere
  2022).
- m = 4 also captures the "non-ellipticity" of NFW + Sérsic composite
  shapes.

## Why it matters

- Stacey 2024 (ALMA): m=4 multipole signal at the ~1% level in resolved
  arcs is required to fit ALMA data — and absorbing it via subhaloes
  produces false substructure detections.
- Cohen 2024, O'Riordan 2024: angular complexity is the dominant
  systematic for substructure detection in galaxy-galaxy lenses;
  multipoles must be marginalised over.
- Time-delay cosmography is less affected (image positions are still well
  fit) but the inferred mass slope shifts.

## In PyAutoLens

PyAutoLens supports m=1,3,4 multipole `MassProfile` additions to the
primary mass model. The recommended SLaM-derived workflow includes them
as a routine step before declaring a substructure detection.

## See also

- [[mass-models]]
- [[dark-matter-substructure]]
- [[shear-ellipticity-degeneracy]]
- [[sources-multipoles]]
