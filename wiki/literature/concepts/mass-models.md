---
title: Mass models for lens galaxies
type: concept
topics: [lens-modelling]
sources:
  - Tessore et al. 2015 — Lensed
  - Tessore et al. 2016 — Power Law
  - Oguri et al. 2021 — CSE
  - Shajib et al. 2020 — Gaussian Decomp
  - He et al. 2024 — MGE
status: drafted
---

# Mass models for lens galaxies

## TL;DR

A lens mass model assigns a parametric (or semi-parametric) form to the
convergence κ(θ) so the deflection α(θ) of the [[lens-equation]] can be
computed. The canonical galaxy-scale model is the **elliptical power-law**
(SIE for slope = isothermal); the canonical cluster model is **NFW +
member galaxies**; the canonical galaxy decomposition is **stellar light
profile traced to mass + NFW dark halo** (see
[[bulge-halo-decomposition]]). Beyond the elliptical power-law,
[[multipoles|angular multipoles]] and external [[external-convergence-shear|shear]]
are typically required.

## Common parametric profiles

### Singular Isothermal Sphere / Ellipsoid (SIS / SIE)

- κ ∝ 1/θ, equivalent to a flat rotation curve.
- Two parameters (SIS: one + θ_E; SIE: θ_E + axis ratio + PA).
- Predicts isothermal mass profile observed in massive ellipticals at
  galaxy scales (Treu, Auger, SLACS).

### Elliptical Power-law (EPL / PEMD)

- κ ∝ θ^(1-γ), where γ = 2 is isothermal.
- Three-parameter generalisation of SIE.
- Analytic deflection via hypergeometric / Tessore-Metcalf integrals
  ([[sources-mass-models|Tessore 2015/2016]]); the standard PyAutoLens
  profile.
- Slope γ couples to the [[radial-angular-degeneracy]] and the
  [[mass-sheet-degeneracy]].

### NFW

- Two-parameter (scale radius r_s, concentration / mass).
- Standard CDM halo profile. Used for cluster cores and as the dark-matter
  component of [[bulge-halo-decomposition|composite models]].
- Generalised-NFW adds an inner slope; relevant for cores or contracted
  haloes.

### Cored, Pseudo-Jaffe, Hernquist, Sersic-mass

- Cored isothermal → finite central density, allows a central image.
- Pseudo-Jaffe / Hernquist used for galaxy-scale members in cluster fits.
- Sersic-mass (mass-follows-light) used as the stellar mass component of
  composite models, with M/L as a free parameter.

### Multi-Gaussian Expansion (MGE / Chameleon / CSE)

- Decomposes an arbitrary surface density (Sérsic, light map) into a sum
  of Gaussians with analytic deflections
  ([[sources-mass-models|Shajib 2020, Oguri 2021]], [[sources-mass-models|He 2024]],
  [[sources-mass-models|Melo 2024]]).
- Lets a model follow the photometry without imposing a rigid analytic
  parameterisation — important when stellar light has [[multipoles|isophotal
  twists, boxy/discy components]].

## Composite models

For galaxy-scale lenses where a [[bulge-halo-decomposition|stars + halo]]
decomposition is desired:

- Light-traces-mass for the baryons (Sérsic-mass, MGE of the imaged
  stellar light, or a free-M/L extension).
- NFW (or gNFW) for the dark matter.
- Optional inner contraction; optional external shear.

The SLaM ([[slam-pipeline]]) pipeline in PyAutoLens automates fitting this
hierarchy.

## Beyond the elliptical power-law

Real lenses are not pure ellipses. The data demand:

- [[external-convergence-shear|External shear γ_ext]] — capturing
  large-scale tidal field; nearly always included.
- [[multipoles|Multipoles m=1,3,4]] — boxiness/disciness, lopsidedness,
  twist; under-fitting these contaminates [[dark-matter-substructure|substructure
  inference]] (Stacey 2024, Cohen 2024, Amvrosiadis 2025).
- Cored or steeper inner regions for clusters and BCGs.

## Why it matters for PyAutoLens

PyAutoLens treats mass models as composable `MassProfile` objects. A user
choosing between `EllIsothermal`, `EllPowerLaw`, an MGE, or a composite
`stellar + dark` model is making a statement about which systematic
matters most for their science:

- For [[time-delay-cosmography]] and H0: power-law slope and external
  convergence dominate.
- For [[dark-matter-substructure]] detection: angular complexity
  (multipoles) and source flexibility dominate.
- For [[bulge-halo-decomposition]]: stellar mass-to-light is the key
  freedom.

## See also

- [[lens-equation]]
- [[einstein-radius]]
- [[bulge-halo-decomposition]]
- [[multipoles]]
- [[external-convergence-shear]]
- [[mass-sheet-degeneracy]]
- [[sources-mass-models]]
