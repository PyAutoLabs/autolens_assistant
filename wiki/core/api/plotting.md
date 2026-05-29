---
title: Plotting — aplt functions and subplot helpers
sources:
  - project: PyAutoArray
    paths:
      - autoarray/plot/
      - autoarray/dataset/plot/
      - autoarray/fit/plot/
      - autoarray/inversion/plot/
    pinned_commit: bd18a76996183aed01cab820878d763e5513a13f
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/plot/
      - autogalaxy/profiles/plot/
    pinned_commit: 2547ca175a82f365a64af261923e0ac7232655ac
  - project: PyAutoLens
    paths:
      - autolens/lens/plot/
      - autolens/imaging/plot/
      - autolens/interferometer/plot/
      - autolens/point/plot/
    pinned_commit: a91febcb1aa12797f9d5ece54c1cbbac528cd087
last_updated: 2026-05-22
---

# Plotting

Current plotting lives in `autolens.plot`, aliased to `aplt`, but the public API is
now mostly **functions** rather than the older `*Plotter`, `Visuals2D`, and
`MatPlot2D` classes. Older docs that reference those classes are stale for the
current source tree.

## Headline functions

| Function | What it plots | Source |
|---|---|---|
| `aplt.plot_array` | Single 2D array (model image, residual map, etc.) | `PyAutoArray:autoarray/plot/array.py` |
| `aplt.plot_grid` | Grid coordinates or sparse spatial overlays | `PyAutoArray:autoarray/plot/grid.py` |
| `aplt.subplot_imaging_dataset` | Imaging data, PSF, S/N, oversampling panels | `PyAutoArray:autoarray/dataset/plot/imaging_plots.py` |
| `ag.plot.subplot_interferometer_dataset` | Visibility-plane dataset overview | `PyAutoArray:autoarray/dataset/plot/interferometer_plots.py` |
| `aplt.subplot_fit_imaging` | Imaging fit summary, residuals, tracer-derived panels | `PyAutoLens:autolens/imaging/plot/fit_imaging_plots.py` |
| `aplt.subplot_fit_interferometer` | Interferometer fit summary | `PyAutoLens:autolens/interferometer/plot/fit_interferometer_plots.py` |
| `aplt.subplot_tracer` | Tracer image, source plane, convergence, potential, magnification | `PyAutoLens:autolens/lens/plot/tracer_plots.py` |
| `aplt.subplot_point_dataset` | Point-source dataset positions / fluxes | `PyAutoLens:autolens/point/plot/point_dataset_plots.py` |
| `aplt.subplot_fit_point` | Point-source fit summary | `PyAutoLens:autolens/point/plot/fit_point_plots.py` |
| `aa.plot.plot_mapper` / `aa.plot.subplot_image_and_mapper` | Pixelised-source mapper views | `PyAutoArray:autoarray/inversion/plot/mapper_plots.py` |

## Pattern

```python
aplt.subplot_tracer(
    tracer=tracer,
    grid=grid,
    output_path="figures",
    output_format="png",
)
```

For single-panel figures, call the direct helper:

```python
aplt.plot_array(
    array=fit.residual_map,
    title="Residual Map",
    positions=[positions],
    output_path="figures",
    output_filename="residuals",
    output_format="png",
)
```

Most plotting functions now take explicit keyword arguments like `positions=`,
`lines=`, `line_colors=`, `colormap=`, `use_log10=`, `output_path=`, and
`output_format=` rather than wrapper objects.

## Overlays and styling

- `positions=` overlays one or more position sets.
- `lines=` / `line_colors=` overlays critical curves, caustics, or user-defined
  polylines.
- `colormap=` and `use_log10=` replace most of the old styling wrappers.
- `output_path=` and `output_format=` control file output directly.

Every entry point takes `output_path` / `output_filename` / `output_format`
kwargs directly; the module is a flat set of free functions with no plotter
classes or `Output` objects.

## FITS and helper utilities

```python
aplt.fits_imaging(dataset=dataset, file_path="dataset.fits", overwrite=True)
aplt.fits_interferometer(dataset=dataset, file_path="dataset.fits", overwrite=True)
```

## See also

- [`../../../skills/al_plot_tracer.md`](../../../skills/al_plot_tracer.md).
- [`../../../skills/al_plot_fit_residuals.md`](../../../skills/al_plot_fit_residuals.md).
- [`../../../skills/al_inspect_source_reconstruction.md`](../../../skills/al_inspect_source_reconstruction.md).
- [`configuration`](./configuration.md) — plot-styling YAMLs.
