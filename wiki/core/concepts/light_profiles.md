---
title: Light profiles
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/standard/
      - autogalaxy/profiles/light/linear/
      - autogalaxy/profiles/light/linear_operated/
      - autogalaxy/profiles/light/abstract.py
    pinned_commit: 2547ca175a82f365a64af261923e0ac7232655ac
last_updated: 2026-05-22
---

# Light profiles

A light profile is a parametric description of a galaxy's surface brightness. In
PyAutoLens, light profiles model the lens galaxy's own light *and* the source's
unlensed light (which the tracer then deflects).

Source: `PyAutoGalaxy:autogalaxy/profiles/light/`. Exposed through PyAutoLens as
`al.lp.*` (standard), `al.lp_linear.*` (linear), and `al.lp_basis.*` (basis
expansions). The current source tree also exports PSF-convolved variants as
`al.lp_operated.*` and `al.lp_linear_operated.*`.

For the full menu, see [`../api/light_profile_catalog`](../api/light_profile_catalog.md).

## Standard vs. linear

Two flavours of every profile shape.

- **Standard** (`al.lp.Sersic`, `al.lp.Exponential`, …) — every parameter, including
  `intensity`, is sampled by the non-linear search.
- **Linear** (`al.lp_linear.Sersic`, …) — every shape parameter is sampled, but
  `intensity` is solved *analytically* via a linear inversion during the fit. The
  search dimensionality drops; the same physics is captured.

**Default to linear** for lens light. The dimensionality saving is large for
multi-component lens light (bulge + disk + MGE), and the analytic intensity solve is
faster than a sampled one.

Standard profiles are still appropriate for sources where you want the intensity in
the posterior (e.g. when comparing two models that differ in source brightness).

## The Sersic family

The workhorse. A flexible profile that nests Exponential (`n=1`) and de Vaucouleurs
(`n=4`) as special cases.

```python
sersic = al.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=(0.1, 0.0),  # ellipticity components (e_y, e_x)
    intensity=1.0,
    effective_radius=0.5,
    sersic_index=2.5,
)
```

Variants:

- `al.lp.SersicSph` — spherical (no ellipticity), faster.
- `al.lp.SersicCore` — Sersic with a core to avoid central divergence; preferred for
  source profiles in pixelised fits.
- `al.lp.DevVaucouleurs` — `n=4` fixed.
- `al.lp.Exponential` / `al.lp.ExponentialCore` — `n=1`.

Source: `PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py` and friends.

## Multi-Gaussian Expansion (MGE)

For complex lens-galaxy light, an MGE — a linear basis of Gaussians with shared
centre and ellipticity, varying `sigma` and `intensity` — gives huge flexibility
without huge dimensionality. The intensity of each Gaussian is solved analytically
via `lp_linear`.

```python
n_gaussians = 30
gaussians = [af.Model(al.lp_linear.Gaussian) for _ in range(n_gaussians)]
for g in gaussians[1:]:
    g.centre = gaussians[0].centre
    g.ell_comps = gaussians[0].ell_comps
bulge = af.Model(al.lp_basis.Basis, profile_list=gaussians)
```

Used in the MGE branch of [`al_build_imaging_model`](../../../skills/al_build_imaging_model.md).

## Shapelets

For sources, a Shapelet basis (Cartesian or polar) captures asymmetric / clumpy
morphologies. See `PyAutoGalaxy:autogalaxy/profiles/light/standard/shapelets/`.

## Operated profiles

`autogalaxy/profiles/light/operated/` and
`autogalaxy/profiles/light/linear_operated/` contain profiles that are already
convolved with the PSF. They are still fit through the normal imaging pipeline;
the distinction is that the PSF is baked into the profile itself instead of
being applied as a separate convolution step.

## Required interface for a custom profile

Subclasses inherit from `LightProfile` (or `LightProfileLinear`) and implement
`image_2d_from(grid, **kwargs)` returning a 1D slim or 2D native `Array2D` of
intensities.

See [`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md) for the
walk-through.

## See also

- [`../api/light_profile_catalog`](../api/light_profile_catalog.md) — full table.
- [`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md) —
  using profiles in a model.
- [`mass_profiles`](./mass_profiles.md) — mass-side equivalent.
