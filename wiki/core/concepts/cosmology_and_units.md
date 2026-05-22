---
title: Cosmology and units
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/cosmology/
    pinned_commit: main
last_updated: 2026-05-22
---

# Cosmology and units

PyAutoLens does all its internal arithmetic in **angular** units — arcseconds for
positions, dimensionless surface densities for convergence, dimensionless deflections.
Converting to physical units (kpc, solar masses, Einstein masses) requires a
cosmology + the lens and source redshifts.

Source: `PyAutoGalaxy:autogalaxy/cosmology/`.

## Default cosmology

Each `Tracer` (or `Plane`, or analysis object) carries a cosmology. The default is
Planck 2018 via astropy:

```python
import autolens as al
print(al.cosmo.Planck18().H0)
```

You can override by passing `cosmology=` explicitly to `Tracer` (and to analyses
that need redshift-distance ratios for multi-plane fits).

## Angular vs. physical

The headline conversions you'll want from a finished fit:

### Einstein radius and mass

```python
einstein_radius_arcsec = tracer.einstein_radius_from(grid=grid)
einstein_mass_angular = tracer.einstein_mass_angular_from(grid=grid)

# Physical: depends on cosmology + lens redshift.
einstein_radius_kpc = tracer.einstein_radius_kpc_from(
    grid=grid, redshift_object=0.5,
)
einstein_mass_solar = tracer.einstein_mass_solar_from(
    grid=grid, redshift_lens=0.5, redshift_source=1.0,
)
```

Source: `PyAutoLens:autolens/lens/tracer.py` (the `*_kpc_from` and `*_solar_from`
methods).

### Convergence to surface mass density

Convergence κ is dimensionless. To convert to physical surface mass density (kg/m²
or M_sun/kpc²), multiply by the **critical surface density**:

```
Σ_cr = (c² D_s) / (4πG D_l D_ls)
```

PyAutoGalaxy exposes this:

```python
sigma_cr = al.cosmo.Planck18().critical_surface_density_between_redshifts_from(
    redshift_0=0.5, redshift_1=1.0,
)
sigma = kappa * sigma_cr  # M_sun / kpc^2
```

### Mass-to-light ratios

The mass-to-light ratio (M/L) for a stellar-mass component tied to a light profile
needs both physical mass and physical luminosity. Workspace reference:
`autolens_workspace:scripts/guides/units/mass_to_light_ratio_units.py`.

## When the units matter

Most lens-modelling outputs make sense in angular units alone:

- Einstein radius in arcseconds.
- Light profile effective radius in arcseconds.
- Ellipticity (dimensionless).

You only need physical units when the answer is a *mass*, a *luminosity*, or a
*linear physical size*, e.g. comparing across surveys at different redshifts or
constraining cosmological parameters.

**Always include units in numerical reports.** *"Einstein radius = 1.23 arcsec"* is
fine; *"Einstein radius = 1.23"* is a bug — the reader can't tell if it's
arcseconds, kpc, or pixels.

## Custom cosmology

For non-Planck cosmologies (testing cosmological dependence, modified gravity), set
the cosmology explicitly:

```python
import autolens as al
cosmo = al.cosmo.FlatLambdaCDM(H0=70.0, Om0=0.3)
tracer = al.Tracer(galaxies=galaxies, cosmology=cosmo)
```

The `cosmology` argument is also accepted by `AnalysisImaging` if you need a non-
default cosmology during the fit.

Source: `PyAutoGalaxy:autogalaxy/cosmology/`.

## See also

- [`lensing_basics`](./lensing_basics.md) — what each angular quantity represents.
- [`samples_and_posteriors`](./samples_and_posteriors.md) — propagating posterior
  uncertainties through unit conversions.
- `autolens_workspace:scripts/guides/units/` — concrete workspace examples.
