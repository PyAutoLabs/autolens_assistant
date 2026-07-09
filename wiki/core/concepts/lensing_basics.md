---
title: Lensing basics — deflection, convergence, magnification, caustics
sources:
  - project: PyAutoLens
    paths:
      - autolens/lens/tracer.py
    pinned_commit: main
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/mass/abstract/
    pinned_commit: main
last_updated: 2026-07-09
---

# Lensing basics

A short tour of the physical quantities PyAutoLens computes from a mass model, so you
know what each plot or method on a `Tracer` actually represents.

For the canonical strong-lensing review, see Treu (2010, ARA&A) or Bartelmann (2010,
Class. Quantum Grav.). The notation below matches PyAutoLens's source.

## The lens equation

A light ray from a source at angular position `β` is deflected by the lens galaxy's
mass and arrives at the observer from position `θ`:

    β = θ − α(θ)

where `α(θ)` is the **deflection angle** at image-plane position `θ`. PyAutoLens
computes `α` from a mass profile via `mass_profile.deflections_yx_2d_from(grid=...)`,
where the grid is a set of `θ` values.

A `Tracer` chains deflections from multiple lens planes: `tracer.traced_grid_2d_list_from`
returns the (β-equivalent) coordinate of each image-plane grid point after passing
through every lens plane.

## Convergence

Convergence `κ(θ)` is the dimensionless surface mass density, normalised so `κ = 1`
marks the **critical surface density** (the threshold for strong lensing). It is the
2D projection of the 3D mass distribution along the line of sight.

```python
kappa = tracer.convergence_2d_from(grid=grid)
```

A galaxy-cluster region typically has `κ > 1`; a small foreground halo `κ ≪ 1`.

Source: `PyAutoLens:autolens/lens/tracer.py` (`convergence_2d_from`) and
`PyAutoGalaxy:autogalaxy/profiles/mass/abstract/` (`convergence_2d_from`).

## Magnification

Magnification `µ(θ)` is the ratio of image-plane to source-plane areas. Bright,
distorted arcs sit at high-magnification regions; the magnification diverges (`µ →
∞`) along the **critical curves**.

Magnification is not surfaced as a `Tracer` method; build the magnification map
from the deflection Jacobian:

```python
# Numerical magnification via finite-differencing the deflection field.
import numpy as np
defl = np.asarray(tracer.deflections_yx_2d_from(grid=grid)).reshape(
    *grid.shape_native, 2
)
dady_dx = np.gradient(defl[..., 0], grid.pixel_scales[0], axis=0)
dady_dy = np.gradient(defl[..., 0], grid.pixel_scales[1], axis=1)
dadx_dx = np.gradient(defl[..., 1], grid.pixel_scales[0], axis=0)
dadx_dy = np.gradient(defl[..., 1], grid.pixel_scales[1], axis=1)
det_A = (1 - dady_dx) * (1 - dadx_dy) - dady_dy * dadx_dx
mu = 1.0 / det_A
```

## Critical curves and caustics

- **Critical curve** — the image-plane locus where `µ → ∞`. A closed loop near the
  lens centre for an SIE.
- **Caustic** — the source-plane image of the critical curve. Sources inside a
  caustic produce multiple images; sources outside, a single image.

```python
crits = tracer.critical_curves_from(grid=grid)   # list of arrays, one per critical curve
caustics = tracer.caustics_from(grid=grid)
```

These are routinely overlaid on data figures; the
[`al_plot_tracer`](../../../skills/al_plot_tracer.md) skill walks through doing this.

## Einstein radius / mass

The **Einstein radius** is the angular radius at which the deflection of an SIS-like
lens equals the angle to the source. For an Isothermal profile, it is literally
`einstein_radius` — a parameter on `al.mp.Isothermal`. For more general mass
profiles, compute it numerically from the convergence:

```python
einstein_radius = tracer.einstein_radius_from(grid=grid)
einstein_mass_angular = tracer.einstein_mass_angular_from(grid=grid)
```

The Einstein mass in physical solar masses requires a cosmology; see
[`cosmology_and_units`](./cosmology_and_units.md).

## Multi-plane lensing

When more than one redshift contributes to the deflection (e.g. group lensing, line-
of-sight halos), `Tracer` handles the recursive deflection bookkeeping. See
[`tracer`](./tracer.md).

## See also

- [`tracer`](./tracer.md) — the PyAutoLens object that computes all of the above.
- [`mass_profiles`](./mass_profiles.md) — which profiles parameterise `κ` how.
- [`../api/mass_profile_catalog`](../api/mass_profile_catalog.md) — full catalogue.
- [`../../../skills/al_plot_tracer.md`](../../../skills/al_plot_tracer.md) — visualising
  these quantities.
