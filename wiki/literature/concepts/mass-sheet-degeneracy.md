---
title: Mass-sheet degeneracy
type: concept
topics: [degeneracies]
sources:
  - Strong_Lens/Birrer2020TDCOSMOSIVH0.pdf
  - Strong_Lens/Wertz2018PySPT.pdf
  - Strong_Lens/Tagore2017_Error_On_Ho.pdf
status: drafted
---

# Mass-sheet degeneracy (MSD)

## TL;DR

A transformation that adds a constant convergence κ_λ everywhere and
rescales the source size by (1 − λ) leaves all image positions and image
shapes invariant but rescales **time delays** by (1 − λ). This is the
mass-sheet degeneracy: it is the dominant systematic in
[[time-delay-cosmography|H0 from strong lensing]].

Formally:

```
κ(θ) → λ κ(θ) + (1 − λ),  β → (1 − λ) β
```

## What it is

The lens equation is invariant under the transformation above for any
constant λ. Imaging data cannot break the degeneracy on its own because
they measure only relative deflections and magnifications. What can break
it:

- **External information on the source size** — if you know the unlensed
  source intrinsic luminosity, the (1-λ) source-plane rescaling is no
  longer free.
- **Stellar kinematics of the lens** — the velocity dispersion of the
  deflector depends on the absolute mass, not its scaled image-plane
  effect.
- **Independent line-of-sight measurements** — e.g.
  [[external-convergence-shear|κ_ext from galaxy counts or weak lensing]].

The internal MSD (a rescaling of the lens's own density slope) is
separately distinct from the line-of-sight MSD (an actual sheet of mass
along the LOS).

## The Source Position Transformation (SPT)

The MSD is a special case of the more general **Source Position
Transformation** ([[sources-degeneracies-systematics|Schneider & Sluse, Wertz 2018]]):
any radial reparameterisation of the source plane that leaves multiple
images consistent acts as an approximate degeneracy. The pySPT code
formalises this.

## Why it matters for PyAutoLens

- For science cases that quote **absolute** masses or H0, MSD must be
  broken by external data or strong priors. PyAutoLens supports passing
  external velocity-dispersion or κ_ext priors into the inference.
- For science cases that quote **relative** quantities (image positions,
  flux ratios, substructure inference), MSD is mostly benign — but a
  hidden internal MSD can mimic a change in the radial slope γ
  ([[radial-angular-degeneracy]]).

## Recent developments

- TDCOSMO IV ([[sources-time-delay-cosmography|Birrer 2020]]) relaxed the
  power-law assumption and allowed an internal MSD, yielding a larger H0
  uncertainty (~8%) that converges towards Planck.
- Multiple authors argue that combining
  [[kinematics-and-lensing|spatially-resolved kinematics]] with imaging
  closes the MSD ([[h0licow]], [[tdcosmo]] post-2020 effort).

## See also

- [[time-delay-cosmography]]
- [[source-position-transformation]]
- [[radial-angular-degeneracy]]
- [[external-convergence-shear]]
- [[sources-degeneracies-systematics]]
