---
title: Galaxy and Galaxies (redshift planes)
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy.py
      - autogalaxy/galaxy/galaxies.py
    pinned_commit: main
last_updated: 2026-07-09
---

# Galaxy and Galaxies (redshift planes)

The two structural objects between profiles (`al.lp.*`, `al.mp.*`) and a `Tracer`.
A `Galaxy` bundles light + mass profiles at one redshift; a `Galaxies` collection
(used internally by `Tracer`) groups galaxies at the same redshift — what lensing
theory calls a *plane*. (Older PyAutoLens versions had a dedicated `Plane` class;
it no longer exists — the redshift slice is now just a `Galaxies` collection.)

Source: `PyAutoGalaxy:autogalaxy/galaxy/galaxy.py` and
`PyAutoGalaxy:autogalaxy/galaxy/galaxies.py`.

## Galaxy

```python
galaxy = al.Galaxy(
    redshift=0.5,
    bulge=al.lp.Sersic(...),
    disk=al.lp.Exponential(...),
    mass=al.mp.Isothermal(...),
    shear=al.mp.ExternalShear(...),
)
```

Key points:

- **Attribute names are arbitrary.** `bulge`, `disk`, `mass`, `shear` are conventions
  used in the workspace, not enum values. You can call a profile `weirdcomponent` if
  you want; the name becomes the key in the model later
  (`model.galaxies.lens.weirdcomponent`).
- **A galaxy can hold multiple light or multiple mass profiles.** Each one is a
  separate kwarg.
- **Redshift is required.** It's how the tracer orders galaxies into planes and
  applies cosmological distance ratios.
- **You can add a pixelisation** instead of (or alongside) light profiles for a
  source: `al.Galaxy(redshift=1.0, pixelization=al.Pixelization(...))`. See
  [`inversions_and_pixelizations`](./inversions_and_pixelizations.md).

What a galaxy can do directly:

```python
img = galaxy.image_2d_from(grid)            # sum of light profile images
conv = galaxy.convergence_2d_from(grid)     # sum of mass profile convergences
defl = galaxy.deflections_yx_2d_from(grid)  # sum of mass profile deflections
```

These delegate to the profiles. For lensing-specific operations (ray tracing,
critical curves, magnification), wrap the galaxies in a `Tracer`.

## Galaxies — the redshift-plane grouping

`al.Galaxies` is a list-like collection of galaxies that computes summed
quantities (`image_2d_from`, `convergence_2d_from`, `deflections_yx_2d_from`)
over its members. `Tracer` groups its input galaxy list by redshift into one
`Galaxies` per plane:

```python
tracer = al.Tracer(galaxies=[lens, source])
tracer.planes      # [Galaxies([lens]), Galaxies([source])] — ascending redshift
```

You'd build a `Galaxies` directly only when you want several same-redshift
galaxies treated as a single unit outside a tracer (e.g. plotting a cluster
plane's total convergence). The standard workflow is to pass the full list to
`Tracer` and let it group by redshift.

Source: `PyAutoGalaxy:autogalaxy/galaxy/galaxies.py`.

## Galaxies in `af.Model`

For fitting, wrap a `Galaxy` in `af.Model` to mark its parameters as free:

```python
import autofit as af

lens = af.Model(
    al.Galaxy,
    redshift=0.5,                       # fixed by default
    bulge=af.Model(al.lp.Sersic),       # free
    mass=af.Model(al.mp.Isothermal),    # free
)
```

`redshift` is passed as a plain value (fixed). The profile attributes are wrapped
again in `af.Model`, which makes their internal parameters free. Override priors
on individual parameters after wrapping:

```python
lens.bulge.effective_radius = af.UniformPrior(lower_limit=0.1, upper_limit=2.0)
```

See [`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md).

## See also

- [`tracer`](./tracer.md) — how galaxies and planes compose into a lens system.
- [`light_profiles`](./light_profiles.md) and [`mass_profiles`](./mass_profiles.md) —
  what goes inside a galaxy.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — pixelised
  sources as a special galaxy.
