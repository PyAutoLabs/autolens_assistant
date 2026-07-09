---
title: PyAutoGalaxy (autogalaxy)
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/
      - autogalaxy/profiles/mass/
      - autogalaxy/galaxy/
      - autogalaxy/galaxy/
      - autogalaxy/cosmology/
      - README.md
    pinned_commit: main
last_updated: 2026-07-09
---

# PyAutoGalaxy — light and mass profiles

Project: [`PyAutoGalaxy`](https://github.com/PyAutoLabs/PyAutoGalaxy). Import:
`autogalaxy`. Most of its classes are re-exported through PyAutoLens as `al.lp.*`,
`al.mp.*`, `al.Galaxy`, etc.

PyAutoGalaxy is the *galaxy modelling* layer. It defines:

- A catalogue of **light profiles** (Sersic family, Exponential, Gaussian, Moffat,
  Shapelets, Multi-Gaussian Expansion, …) — see
  [`api/light_profile_catalog`](../api/light_profile_catalog.md).
- A catalogue of **mass profiles** (Isothermal, PowerLaw, NFW + variants, multipole,
  external shear, point mass, mass sheets, …) — see
  [`api/mass_profile_catalog`](../api/mass_profile_catalog.md).
- **`Galaxy`** — composes light + mass profiles with a redshift.
- **`Galaxies`** — one redshift slice of a lens system (lensing theory's "plane");
  multiple make a tracer (in PyAutoLens).
- **Cosmology** helpers — distance + redshift conversions.

It's used both standalone (for non-lens galaxy fitting) and as PyAutoLens's profile
catalogue.

## Light profiles

Live under `autogalaxy/profiles/light/`. Two sub-families:

- **Standard** (`autogalaxy/profiles/light/standard/`) — Sersic, Exponential,
  Gaussian, Moffat, DevVaucouleurs, Shapelets. Each profile has an `image_2d_from(grid)`
  method.
- **Linear** (`autogalaxy/profiles/light/linear/`) — same shapes, but the intensity
  is solved *analytically* during the fit instead of sampled. Linear profiles cut
  search dimensionality without changing model expressiveness, which is the right
  default for most lens-light models.

Exposed via PyAutoLens as `al.lp.*` (standard) and `al.lp_linear.*` (linear).
A basis expansion of multiple linear profiles (MGE) is `al.lp_basis.Basis`.

See [`concepts/light_profiles`](../concepts/light_profiles.md) and the catalogue.

## Mass profiles

Live under `autogalaxy/profiles/mass/`. Sub-families:

- `total/` — Isothermal, PowerLaw, point mass. Total (luminous + dark) mass models.
- `dark/` — NFW + variants (gNFW, MCR, truncated, virial mass parameterisations).
  Used to represent dark-matter halos.
- `stellar/` — stellar-mass profiles for decomposed light + dark fits.
- `sheets/` — external shear, mass sheets, point masses for line-of-sight effects.
- `multipole/` — angular harmonic expansion of departures from elliptical symmetry.

Each implements `convergence_2d_from(grid)`, `deflections_yx_2d_from(grid)`, and
`potential_2d_from(grid)`. Exposed via PyAutoLens as `al.mp.*`.

See [`concepts/mass_profiles`](../concepts/mass_profiles.md) and the catalogue.

## Galaxy and Plane

```python
galaxy = al.Galaxy(
    redshift=0.5,
    bulge=al.lp.Sersic(...),       # one or more light profiles
    mass=al.mp.Isothermal(...),    # one or more mass profiles
)
```

Galaxy attribute names are arbitrary; they become the keys you address in the model
later (e.g. `model.galaxies.lens.bulge`).

Source: `PyAutoGalaxy:autogalaxy/galaxy/galaxy.py`.

## Cosmology

`autogalaxy/cosmology/` exposes an astropy-backed cosmology API for redshift →
angular diameter distance, mass-to-light unit conversions, etc. See
[`concepts/cosmology_and_units`](../concepts/cosmology_and_units.md).

## Configuration

`autogalaxy/config/` adds priors-by-class entries to the autoconf system: when you
write `af.Model(al.lp.Sersic)`, the default prior for each Sersic parameter comes
from `autogalaxy/config/priors/`. Also includes config for cosmology defaults,
notation, plotting.

## Dependencies

`autofit`, `autoarray`, `colossus` (cosmology helpers for dark matter halo
relations), `astropy`, `nautilus-sampler`. Optional: `numba`, `pynufft`.

## See also

- [`api/light_profile_catalog`](../api/light_profile_catalog.md).
- [`api/mass_profile_catalog`](../api/mass_profile_catalog.md).
- [`concepts/galaxy_and_plane`](../concepts/galaxy_and_plane.md).
- [`stack/autolens`](./autolens.md) — what PyAutoLens adds on top.
