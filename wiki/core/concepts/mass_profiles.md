---
title: Mass profiles
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/mass/total/
      - autogalaxy/profiles/mass/dark/
      - autogalaxy/profiles/mass/stellar/
      - autogalaxy/profiles/mass/sheets/
      - autogalaxy/profiles/mass/point/
      - autogalaxy/profiles/mass/abstract/abstract.py
    pinned_commit: 2547ca175a82f365a64af261923e0ac7232655ac
last_updated: 2026-05-22
---

# Mass profiles

A mass profile is a parametric description of a galaxy's *total* mass distribution
(stellar + dark) or of a single component thereof. In PyAutoLens, mass profiles drive
the lensing — they're what `Tracer` integrates to compute deflections, convergence,
and magnification.

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/`. Exposed through PyAutoLens as
`al.mp.*`. For the full catalogue see
[`../api/mass_profile_catalog`](../api/mass_profile_catalog.md).

## Required interface

Every mass profile implements:

- `convergence_2d_from(grid)` — surface mass density `κ(θ)`.
- `deflections_yx_2d_from(grid)` — deflection field `α(θ)`.
- `potential_2d_from(grid)` — lensing potential.

The base class `MassProfile` (`PyAutoGalaxy:autogalaxy/profiles/mass/abstract/abstract.py`)
provides numerical defaults if you only override convergence — but performance is
dramatically better when deflections have a closed form.

## Total mass

Single-component models of the total (luminous + dark) mass.

- **`al.mp.Isothermal`** — Singular Isothermal Ellipsoid (SIE). The canonical lens-
  modelling baseline. Two free angular parameters (`einstein_radius`, ellipticity).
- **`al.mp.IsothermalSph`** — spherical SIS. Even simpler.
- **`al.mp.PowerLaw`** — generalised SIE with a free density slope. Parameter
  `slope=2.0` reduces to Isothermal.
- **`al.mp.PowerLawCore`** — PowerLaw with a finite core, regular at the centre.
- **`al.mp.PowerLawBroken`** — broken-slope power law for piecewise radial
  structure.
- **`al.mp.PowerLawMultipole`** — PowerLaw plus an `m=3` or `m=4` angular multipole
  for departures from elliptical symmetry.
- **`al.mp.PIEMass` / `al.mp.dPIEMass`** — pseudo-isothermal alternatives used in
  some galaxy- and cluster-scale models.

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/total/`.

## Dark matter

NFW and variants. Used in decomposed light + dark fits.

- **`al.mp.NFW`** — standard NFW with elliptical symmetry; parameters `kappa_s`,
  `scale_radius`.
- **`al.mp.NFWMCRLudlow`** / **`al.mp.NFWMCRLudlowSph`** — NFW with a Ludlow
  mass-concentration relation baked in.
- **`al.mp.NFWMCRDuffySph`** — spherical NFW with the Duffy relation.
- **`al.mp.NFWVirialMassConcSph`** — spherical NFW parameterised by virial mass.
- **`al.mp.NFWTruncatedSph`** — spherical truncated NFW.
- **`al.mp.gNFW`** / **`al.mp.gNFWSph`** — generalised NFW with a free inner slope.
- **`al.mp.gNFWMCRLudlow`** — gNFW with a Ludlow mass-concentration relation.

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/dark/`.

## Stellar / baryonic

For decomposed mass models: stellar mass tied to a light profile via a
mass-to-light ratio.

- **`al.mp.Sersic` / `al.mp.SersicSph`**
- **`al.mp.Exponential` / `al.mp.ExponentialSph`**
- **`al.mp.DevVaucouleurs` / `al.mp.DevVaucouleursSph`**
- **`al.mp.Gaussian`** and gradient / chameleon variants

## Sheets

Background line-of-sight effects.

- **`al.mp.ExternalShear`** — constant shear from line-of-sight structure. Two free
  parameters (`gamma_1`, `gamma_2`).
- **`al.mp.MassSheet`** — uniform convergence sheet.
- **`al.mp.ExternalPotential`** — external potential term for specialised cases.

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/sheets/`.

## Point masses

Compact deflectors such as stars, black holes, or toy microlensing components.

- **`al.mp.PointMass`** — ideal point lens.
- **`al.mp.SMBH` / `al.mp.SMBHBinary`** — supermassive black hole variants.

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/point/`.

## Picking the right model

| Goal | Starting mass model |
|---|---|
| First-fit galaxy-scale lens | `Isothermal` + `ExternalShear` |
| Total-mass-slope measurement | `PowerLaw` + `ExternalShear` |
| Disentangle stellar vs dark | `Sersic` (stellar) + `NFW` (dark) + `ExternalShear` |
| Substructure / subhalo detection | `Isothermal` + `ExternalShear` + subhalo as a free `NFWTruncated` |
| Group / cluster lens | multi-galaxy `Isothermal` ± scaling relations |

For practical model composition, see
[`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md).

## See also

- [`../api/mass_profile_catalog`](../api/mass_profile_catalog.md) — full table.
- [`lensing_basics`](./lensing_basics.md) — physical meaning of κ, α, µ.
- [`tracer`](./tracer.md) — how profiles combine into a lens system.
- [`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md) — writing
  your own.
