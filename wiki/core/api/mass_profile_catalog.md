---
title: Mass profile catalogue
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/mass/total/
      - autogalaxy/profiles/mass/dark/
      - autogalaxy/profiles/mass/stellar/
      - autogalaxy/profiles/mass/sheets/
      - autogalaxy/profiles/mass/point/
    pinned_commit: 2547ca175a82f365a64af261923e0ac7232655ac
last_updated: 2026-05-22
---

# Mass profile catalogue

Every mass profile PyAutoGalaxy ships. Exposed through PyAutoLens as `al.mp.*`.

Concept page: [`../concepts/mass_profiles`](../concepts/mass_profiles.md).

## Total mass

For single-component models of the full (luminous + dark) mass.

| Class | Parameters | Notes |
|---|---|---|
| `Isothermal` | centre, ell_comps, einstein_radius | SIE — the canonical baseline |
| `IsothermalSph` | centre, einstein_radius | Spherical SIS |
| `IsothermalCore` | + core_radius | SIE with finite core |
| `PowerLaw` | centre, ell_comps, einstein_radius, slope | Generalised SIE; `slope=2` reduces to Isothermal |
| `PowerLawSph` | centre, einstein_radius, slope | Spherical PowerLaw |
| `PowerLawCore` | + core_radius | PowerLaw with finite core |
| `PowerLawBroken` | + inner_slope, outer_slope, break_radius | Broken-slope power law |
| `PowerLawMultipole` | + multipole_comps (m=3 or m=4) | PowerLaw + angular multipole |
| `PIEMass` / `dPIEMass` | centre, ell_comps, normalization, core/radius terms | Pseudo-isothermal alternatives |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/total/`.

## Dark matter

NFW family, used in decomposed light + dark fits.

| Class | Parameters | Notes |
|---|---|---|
| `NFW` | centre, ell_comps, kappa_s, scale_radius | Standard NFW |
| `NFWSph` | centre, kappa_s, scale_radius | Spherical NFW |
| `NFWMCRDuffySph` | + mass | Spherical NFW + Duffy mass-concentration relation |
| `NFWMCRLudlow` / `NFWMCRLudlowSph` | + mass | NFW + Ludlow mass-concentration relation |
| `NFWVirialMassConcSph` | + virial_mass | Spherical NFW parameterised by virial mass |
| `NFWTruncatedSph` | + truncation_radius | Spherical NFW truncated at finite radius |
| `gNFW` | centre, kappa_s, scale_radius, inner_slope | Generalised NFW (free inner slope) |
| `gNFWSph` | centre, kappa_s, scale_radius, inner_slope | Spherical gNFW |
| `gNFWMCRLudlow` | + mass | gNFW + Ludlow MCR |
| `gNFWVirialMassConcSph` | + virial_mass | Spherical gNFW parameterised by virial mass |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/dark/`.

## Stellar mass

Mass profiles tied to a light profile via a mass-to-light ratio. Used in
decomposed Light + Dark fits.

| Class | Notes |
|---|---|
| `Sersic` (stellar) | Sersic light + linked mass via M/L |
| `SersicSph` (stellar) | Spherical Sersic stellar mass |
| `Exponential` (stellar) | Exponential light + linked mass via M/L |
| `ExponentialSph` (stellar) | Spherical exponential stellar mass |
| `DevVaucouleurs` / `DevVaucouleursSph` | de Vaucouleurs stellar mass |
| `Gaussian` (stellar) | Gaussian light + linked mass via M/L |
| `Chameleon` / `ChameleonSph` | Chameleon stellar mass |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/stellar/`.

## Sheets and line-of-sight

| Class | Parameters | Notes |
|---|---|---|
| `ExternalShear` | gamma_1, gamma_2 | Constant background shear; almost always included with an SIE |
| `MassSheet` | centre, kappa | Uniform convergence sheet |
| `ExternalPotential` | centre, ell_comps, normalization | External potential term |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/sheets/`.

## Point masses

Compact point-like deflectors and black-hole components.

| Class | Notes |
|---|---|
| `PointMass` | Ideal point lens / microlens |
| `SMBH` | Supermassive black hole |
| `SMBHBinary` | Binary SMBH system |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/point/`.

## Picking a mass model at a glance

| Lens type / goal | Mass model |
|---|---|
| First-fit, galaxy-scale | `Isothermal` + `ExternalShear` |
| Total-mass-slope measurement | `PowerLaw` + `ExternalShear` |
| Decomposed stellar + dark | stellar `Sersic` + `NFW` + `ExternalShear` |
| Subhalo / substructure | base SIE + free `NFWTruncated` at suspected position |
| Boxy/disky resolved lens | `PowerLawMultipole` + `ExternalShear` |
| Group lens | multiple `Isothermal` galaxies + `ExternalShear` |
| Cluster lens | scaling-relation–tied `Isothermal` cluster members + `NFW` halo |

## See also

- [`../concepts/mass_profiles`](../concepts/mass_profiles.md) — conceptual page.
- [`../concepts/lensing_basics`](../concepts/lensing_basics.md) — physical
  meaning of κ, α, µ.
- [`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md) —
  using mass profiles in a model.
- [`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md) — writing
  your own.
