---
title: PyAutoLens (autolens)
sources:
  - project: PyAutoLens
    paths:
      - autolens/lens/
      - autolens/imaging/model/
      - autolens/interferometer/model/
      - autolens/point/
      - autolens/quantity/
      - README.rst
    pinned_commit: main
last_updated: 2026-05-22
---

# PyAutoLens — strong lensing umbrella

Project: [`PyAutoLens`](https://github.com/Jammy2211/PyAutoLens). Import: `autolens`,
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
(or `Plane` objects for multi-plane systems) and knows how to ray-trace image-plane
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
- `al.mesh.Delaunay` / `al.mesh.Voronoi` / `al.mesh.Rectangular` — mesh choices.
- `al.reg.Constant` / `al.reg.ConstantSplit` / `al.reg.AdaptiveBrightness` —
  regularisation schemes.

See [`concepts/inversions_and_pixelizations`](../concepts/inversions_and_pixelizations.md).

## Point-source lensing

`autolens/point/` adds:

- `al.PointDataset` — image positions + time delays + magnifications, with errors.
- `al.PointFlux` / `al.PointTimeDelay` profile-like objects to plug into a Galaxy.
- `al.AnalysisPoint` — the corresponding analysis.

Used for quasar lensing and time-delay cosmography.

## Quantity API

`autolens/quantity/` exposes objects for measuring derived lensing quantities — total
Einstein mass within a radius, projected enclosed mass, mass-to-light ratios — with
proper uncertainty propagation from the posterior. See
[`concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md) and
[`concepts/cosmology_and_units`](../concepts/cosmology_and_units.md).

## Plotting

`autolens.plot` (aliased `aplt`) provides the lensing-specific plotters:

- `aplt.TracerPlotter` — ray-traced images, critical curves, caustics, convergence,
  deflection field.
- `aplt.FitImagingPlotter` / `aplt.FitInterferometerPlotter` — fit residuals,
  per-galaxy decomposition.
- `aplt.InversionPlotter` — pixelised source diagnostics.

See [`api/plotting`](../api/plotting.md).

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
