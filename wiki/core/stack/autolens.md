---
title: PyAutoLens (autolens)
sources:
  - project: PyAutoLens
    paths:
      - autolens/lens/
      - autolens/imaging/model/
      - autolens/interferometer/model/
      - autolens/point/
      - README.md
    pinned_commit: main
last_updated: 2026-07-09
---

# PyAutoLens — strong lensing umbrella

Project: [`PyAutoLens`](https://github.com/PyAutoLabs/PyAutoLens). Import: `autolens`,
aliased to `al`. The user-facing library of the stack.

PyAutoLens adds the lensing-specific pieces on top of PyAutoGalaxy: multi-plane ray
tracing, the lensing-aware analysis objects (`AnalysisImaging`,
`AnalysisInterferometer`, `AnalysisPoint`), and lensing-specific plotting and
diagnostics.

If you stay at the `al.*` surface, you rarely have to look further into the stack.
When you do — to read a light profile's source, debug an `Imaging` constructor, or
inspect autofit's search internals — the underlying classes are in the lower-layer
packages.

## Tracer — multi-plane ray tracing

The headline lensing object. A `Tracer` takes an ordered list of `Galaxy` objects
(grouped into per-redshift `Galaxies` planes for multi-plane systems) and knows how to ray-trace image-plane
grids through them.

```python
tracer = al.Tracer(galaxies=[lens, source])

# Image-plane image of the tracer applied to a grid.
image = tracer.image_2d_from(grid=grid)

# Source-plane grid: where image-plane (y, x) coordinates land after deflection.
src_grid = tracer.traced_grid_2d_list_from(grid=grid)[-1]

# Critical curves and caustics for diagnostic plots.
crits = tracer.critical_curves_from(grid=grid)
caust = tracer.caustics_from(grid=grid)
```

Source: `PyAutoLens:autolens/lens/tracer.py`. Concept page:
[`concepts/tracer`](../concepts/tracer.md).

## Analyses

Three flavours, one per dataset type:

- **`al.AnalysisImaging`** — CCD imaging. PSF convolution, masked likelihood. Source:
  `PyAutoLens:autolens/imaging/model/analysis.py`.
- **`al.AnalysisInterferometer`** — visibility-plane interferometer data. NUFFT from
  real-space to (u, v). Source: `PyAutoLens:autolens/interferometer/model/analysis.py`.
- **`al.AnalysisPoint`** — point-source lensing (quasar positions, time delays).
  Source: `PyAutoLens:autolens/point/model/analysis.py`.

The analysis object is what you hand to a PyAutoFit search. It provides the
log-likelihood for the model on this dataset.

See [`api/analysis_objects`](../api/analysis_objects.md).

## Inversions and pixelisations

PyAutoLens re-exposes the pixelisation machinery in PyAutoArray. The key user-facing
objects:

- `al.Pixelization(mesh=..., regularization=...)` — wraps a source-plane mesh + a
  regularisation scheme. Lives inside a `Galaxy`.
- `al.mesh.Delaunay` / `al.mesh.RectangularUniform` / `al.mesh.RectangularAdaptImage`
  / `al.mesh.KNearestNeighbor` — mesh choices; inspect `dir(al.mesh)` for the
  complete set. `Voronoi` and `Rectangular` have been replaced.
- `al.reg.Constant` / `al.reg.ConstantSplit` / `al.reg.Adapt` / `al.reg.AdaptSplit` —
  regularisation schemes (the older `AdaptiveBrightness` has been split into the
  `Adapt*` family).

See [`concepts/inversions_and_pixelizations`](../concepts/inversions_and_pixelizations.md).

## Point-source lensing

`autolens/point/` adds:

- `al.PointDataset` — image positions + time delays + magnifications, with errors.
- `al.ps.Point` / `al.ps.PointFlux` profile-like objects to plug into a Galaxy.
  (A separate `PointTimeDelay` class has been removed; time-delay information is
  carried by `al.PointDataset` itself.)
- `al.AnalysisPoint` — the corresponding analysis.

Used for quasar lensing and time-delay cosmography.

## Derived quantities

The former `autolens/quantity/` package has been archived (it lives on in
`autolens_workspace_developer/legacy`). Derived lensing quantities — Einstein
radius/mass, enclosed masses, magnifications — are computed from `Tracer`
methods and posterior samples directly; the workspace guides
(`autolens_workspace:scripts/guides/lens_calc.py`, `scripts/guides/units/`) are
the recipes. See
[`concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md) and
[`concepts/cosmology_and_units`](../concepts/cosmology_and_units.md).

## Plotting

`autolens.plot` (aliased `aplt`) is a flat module of free functions — there are
no plotter classes. The main entry points:

- `aplt.subplot_tracer` / `aplt.subplot_galaxies_images` —
  ray-traced images, per-galaxy decomposition.
- `aplt.subplot_fit_imaging` / `aplt.subplot_fit_interferometer` — fit
  residuals; `aplt.subplot_fit_imaging_of_galaxy` for per-galaxy decomposition.
- `aplt.subplot_basis_image` — pixelised-source mesh overlay (closest
  remaining substitute for the old `InversionPlotter`).
- `aplt.plot_array` / `aplt.plot_grid` — single-figure helpers, taking
  `output_path` / `output_filename` / `output_format` directly.

`Tracer` does not surface magnification, critical curves, or caustics directly;
derive them from the deflection field. See [`api/plotting`](../api/plotting.md).

## Configuration

`autolens/config/` adds the lensing-specific defaults: prior YAMLs for `Tracer`,
plot settings for `FitImaging`, and notation.

## Dependencies

`autogalaxy` (which pulls in `autofit`, `autoarray`, `autoconf`), `nautilus-sampler`.
Optional: `numba`, `pynufft`, `UltraNest`, `Zeus`, `getdist`.

## See also

- [`concepts/tracer`](../concepts/tracer.md).
- [`api/analysis_objects`](../api/analysis_objects.md).
- [`api/plotting`](../api/plotting.md).
- The [`../../../skills/`](../../../skills/) directory — every skill above is operationally
  centred on `al.*`.
