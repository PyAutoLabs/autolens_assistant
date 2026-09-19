---
title: Galaxy and Galaxies (redshift planes)
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy.py
      - autogalaxy/galaxy/galaxies.py
      - autogalaxy/galaxy/mass_field.py
    pinned_commit: dfb04cc6cc51fecbe5cdeadd584a9de0d1b561de
  - project: PyAutoLens
    paths:
      - autolens/lens/tracer.py
    pinned_commit: 8279bce04493d073261e1db07ae7bccd5ca4fd09
last_updated: 2026-09-19
content_sha256: 6524498022530e907e2bc532a570fa05a235095fbacdffbb92e30fce2ea79817
---

# Galaxy and Galaxies (redshift planes)

The two structural objects between profiles (`al.lp.*`, `al.mp.*`) and a `Tracer`.
A `Galaxy` bundles light + mass profiles at one redshift. An external shear or mass
sheet belongs to a separate `MassField` at its own redshift. A `Galaxies` collection
(used internally by `Tracer`) groups these objects at the same redshift — what lensing
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
)
field = al.MassField(redshift=0.5, shear=al.mp.ExternalShear(...))
source = al.Galaxy(redshift=1.0, bulge=al.lp.Sersic(...))
tracer = al.Tracer(galaxies=[galaxy, source], fields=[field])
```

Key points:

- **Attribute names are arbitrary.** `bulge`, `disk`, and `mass` are conventions
  used in the workspace, not enum values. You can call a profile `weirdcomponent` if
  you want; the name becomes the key in the model later
  (`model.galaxies.lens.weirdcomponent`).
- **A galaxy can hold multiple light or multiple mass profiles.** Each one is a
  separate kwarg.
- **External fields have their own container.** `MassField` holds shear, sheets, or
  other external mass profiles. Put one field per redshift in `Tracer(fields=[...])`;
  in a fitted model, use a bare `fields=field` for one plane.
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
over its members. `Tracer` groups its input galaxies and fields by redshift into one
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
