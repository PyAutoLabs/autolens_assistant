---
title: Light profile catalogue
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/standard/
      - autogalaxy/profiles/light/linear/
      - autogalaxy/profiles/light/operated/
      - autogalaxy/profiles/light/linear_operated/
      - autogalaxy/profiles/light/basis.py
    pinned_commit: 2547ca175a82f365a64af261923e0ac7232655ac
last_updated: 2026-05-22
---

# Light profile catalogue

Every light profile PyAutoGalaxy ships, by family. Exposed through PyAutoLens as
`al.lp.*` (standard), `al.lp_linear.*` (linear), `al.lp_operated.*` (PSF-convolved),
`al.lp_linear_operated.*` (linear PSF-convolved), and `al.lp_basis.*` (basis
expansions like MGE).

Concept page: [`../concepts/light_profiles`](../concepts/light_profiles.md).

## Sersic family

| Class | Parameters | Notes |
|---|---|---|
| `Sersic` | centre, ell_comps, intensity, effective_radius, sersic_index | Workhorse |
| `SersicSph` | centre, intensity, effective_radius, sersic_index | Spherical, fast |
| `SersicCore` | + radius_break | With finite core; preferred for source profiles |
| `DevVaucouleurs` | centre, ell_comps, intensity, effective_radius | Sersic with `n=4` fixed |
| `DevVaucouleursSph` | centre, intensity, effective_radius | Spherical de Vaucouleurs |
| `Exponential` | centre, ell_comps, intensity, effective_radius | Sersic with `n=1` fixed |
| `ExponentialSph` | centre, intensity, effective_radius | Spherical exponential |
| `ExponentialCore` | + radius_break | Exponential with finite core |

Source: `PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`.

## Gaussian / Moffat

| Class | Parameters | Notes |
|---|---|---|
| `Gaussian` | centre, ell_comps, intensity, sigma | 2D Gaussian |
| `GaussianSph` | centre, intensity, sigma | Spherical |
| `Moffat` | centre, ell_comps, intensity, alpha, beta | Moffat / King-like |

Source: `PyAutoGalaxy:autogalaxy/profiles/light/standard/gaussian.py`.

## Shapelets

For asymmetric / clumpy sources.

| Class | Notes |
|---|---|
| `ShapeletCartesian` | Hermite polynomial basis |
| `ShapeletPolar` | Polar basis |
| `ShapeletExponential` | Exponential weighting |

Source: `PyAutoGalaxy:autogalaxy/profiles/light/standard/shapelets/`.

## Linear variants

Identical shapes to the standard set above, but with `intensity` solved analytically
during the fit. Reduces search dimensionality with no loss of expressiveness.

| Class | Standard equivalent |
|---|---|
| `lp_linear.Sersic` | `lp.Sersic` |
| `lp_linear.SersicCore` | `lp.SersicCore` |
| `lp_linear.Exponential` | `lp.Exponential` |
| `lp_linear.Gaussian` | `lp.Gaussian` |
| `lp_linear.DevVaucouleurs` | `lp.DevVaucouleurs` |
| ... | (one linear per standard) |

**Default to linear** for lens light. Use standard when you specifically want
intensity in the posterior.

Source: `PyAutoGalaxy:autogalaxy/profiles/light/linear/`.

## Basis expansions (MGE etc.)

```python
n = 30
gaussians = [af.Model(al.lp_linear.Gaussian) for _ in range(n)]
for g in gaussians[1:]:
    g.centre = gaussians[0].centre
    g.ell_comps = gaussians[0].ell_comps
mge = af.Model(al.lp_basis.Basis, profile_list=gaussians)
```

Multi-Gaussian Expansion is the canonical use. Other basis sets (Shapelet expansions)
work the same way.

Source: `PyAutoGalaxy:autogalaxy/profiles/light/basis.py`.

## Operated profiles

Pre-convolved with the PSF. Use these when you specifically want PSF response
baked into the profile rather than applied as a separate convolution step in the
fit.

| Class |
|---|
| `lp_operated.Sersic` |
| `lp_operated.Gaussian` |
| `lp_operated.Moffat` |
| `lp_linear_operated.Sersic` |
| `lp_linear_operated.Gaussian` |
| `lp_linear_operated.Moffat` |

Source: `PyAutoGalaxy:autogalaxy/profiles/light/operated/` and
`PyAutoGalaxy:autogalaxy/profiles/light/linear_operated/`.

## Picking a profile at a glance

| Source goal | Pick |
|---|---|
| Smooth source | `lp_linear.SersicCore` |
| Complex source | pixelisation (see [`../concepts/inversions_and_pixelizations`](../concepts/inversions_and_pixelizations.md)) |
| Clumpy / asymmetric | `lp.ShapeletPolar` basis |
| Lens light, single component | `lp_linear.Sersic` |
| Lens light, complex | `lp_basis.Basis` of 20–40 Gaussians (MGE) |
| Lens light, bulge + disk | `lp_linear.DevVaucouleurs` + `lp_linear.Exponential` |
| Unresolved quasar image | `ps.Point` or `ps.PointFlux` |

## See also

- [`../concepts/light_profiles`](../concepts/light_profiles.md) — conceptual page.
- [`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md) —
  using profiles in a model.
- [`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md) — writing
  your own.
