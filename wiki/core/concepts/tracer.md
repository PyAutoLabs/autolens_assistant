---
title: Tracer — multi-plane ray tracing
sources:
  - project: PyAutoLens
    paths:
      - autolens/lens/tracer.py
      - autolens/lens/plane.py
    pinned_commit: main
last_updated: 2026-05-22
---

# Tracer — multi-plane ray tracing

`al.Tracer` is the central lensing object. It composes one or more `Galaxy` objects
(or `Plane` objects, each grouping galaxies at the same redshift) and knows how to
ray-trace a grid of image-plane coordinates back to each subsequent plane.

Source: `PyAutoLens:autolens/lens/tracer.py`.

## Two-plane systems

The galaxy-scale common case: one lens plane at redshift `z_l`, one source plane at
`z_s`.

```python
lens = al.Galaxy(redshift=0.5, mass=al.mp.Isothermal(centre=(0.0, 0.0), einstein_radius=1.2))
source = al.Galaxy(redshift=1.0, bulge=al.lp.SersicCore(...))
tracer = al.Tracer(galaxies=[lens, source])
```

`Tracer` reads the redshifts off the galaxies and constructs `Plane` objects
internally — one per unique redshift, in ascending order. With two redshifts you get
two planes; with three or more you get a multi-plane system.

## What a tracer computes

| Method | What you get |
|---|---|
| `image_2d_from(grid)` | Image-plane image (lens light + lensed source) |
| `traced_grid_2d_list_from(grid)` | List of grids, one per plane, with each subsequent plane having been deflected by the planes ahead of it |
| `deflections_yx_2d_from(grid)` | Total deflection field at every (y, x) in `grid` |
| `convergence_2d_from(grid)` | Total convergence at every grid point |
| `potential_2d_from(grid)` | Lensing potential |
| `time_delays_from(grid)` | Time delays at the given (image-plane) positions |
| `einstein_radius_from(grid)` | Numerical Einstein radius |
| `einstein_mass_angular_from(grid)` | Einstein mass in angular units |

> In `2026.5.21+`, `Tracer.magnification_2d_from`, `Tracer.critical_curves_from`,
> and `Tracer.caustics_from` are **removed**. Build magnification yourself from
> the deflection field's Jacobian, or derive critical curves / caustics from
> a magnification map. See
> [`api_deltas_2026_05.md`](../api_deltas_2026_05.md).

For physical-unit equivalents, see [`cosmology_and_units`](./cosmology_and_units.md).

## Per-galaxy and per-plane images

```python
tracer.galaxies                         # list of Galaxy objects, by redshift order
tracer.planes                           # list of Plane objects, each a redshift slice
tracer.galaxies[0].image_2d_from(grid)  # image-plane image of just the first galaxy
tracer.planes[-1].image_2d_from(grid)   # image of the source plane
```

This is how the per-galaxy plots in [`al_plot_tracer`](../../../skills/al_plot_tracer.md)
work.

## Multi-plane systems

When you have three or more redshifts (e.g. a group lens with three lens galaxies and
one source, or a galaxy-galaxy lens with a line-of-sight halo), `Tracer` automatically
handles the recursive deflection bookkeeping. The deflection at plane `i+1` is
applied to the (already-deflected) grid from plane `i`.

```python
galaxies = [
    al.Galaxy(redshift=0.3, mass=al.mp.NFW(...)),         # foreground halo
    al.Galaxy(redshift=0.5, mass=al.mp.Isothermal(...)),  # primary lens
    al.Galaxy(redshift=1.0, bulge=al.lp.SersicCore(...)), # source
]
tracer = al.Tracer(galaxies=galaxies)
```

The relative angular-diameter distances `D_ij` between every pair of planes are
computed from a cosmology (default Planck 2018; set explicitly on the tracer if you
need otherwise).

Source: `PyAutoLens:autolens/lens/plane.py`.

## Pixelised tracer output

When a source-plane `Galaxy` carries a `Pixelization`, the tracer's image-plane image
is computed via the inversion — the source plane is fit on its mesh, then mapped back
through the lens. See [`inversions_and_pixelizations`](./inversions_and_pixelizations.md).

## Serialisation

`Tracer` is `Dictable`, so it round-trips to and from JSON via
`from_json(file_path="tracer.json")`. This is how saved fits store the ground-truth or
max-log-likelihood lens model.

## See also

- [`lensing_basics`](./lensing_basics.md) — the physics of every quantity above.
- [`galaxy_and_plane`](./galaxy_and_plane.md) — what `Galaxy` and `Plane` are.
- [`../api/analysis_objects`](../api/analysis_objects.md) — how a tracer plugs into
  `AnalysisImaging` for fitting.
- [`../../../skills/al_plot_tracer.md`](../../../skills/al_plot_tracer.md).
