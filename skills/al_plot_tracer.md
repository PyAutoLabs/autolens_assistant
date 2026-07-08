---
name: al_plot_tracer
description: Plot ray-tracing visuals from a `Tracer` — image-plane and source-plane galaxy images, deflection vector field, convergence and potential maps, critical curves and caustics, magnification map. Use after `al_load_results` has handed you a Tracer, or right after building one in `al_simulate_dataset`. For *fit*-derived plots (residuals, model image with PSF) see `al_plot_fit_residuals`.
---

# Plotting a Tracer

A `Tracer` knows how to ray-trace grids of (y, x) coordinates through one or more
lens planes. From it you can extract everything that depends only on the *model*,
without needing the data: critical curves, caustics, deflection fields, convergence
maps, magnification maps, and per-galaxy images on the image and source planes.

This skill produces those plots for the user's tracer. For fit-vs-data diagnostics
that depend on the dataset (residuals, normalised residuals, chi-squared), use
[`al_plot_fit_residuals`](./al_plot_fit_residuals.md) instead.

Canonical references: `autolens_workspace:scripts/guides/plot/examples/plotters.py`
and `visuals.py`.

## Ask

- *"Which plot do you want?"* — pick from: image-plane subplot, source-plane subplot,
  deflection field, convergence, potential, magnification, critical curves +
  caustics overlay. Each lives in a different branch.
- *"On what grid?"* — if you have a dataset, use `dataset.grid`. Otherwise build a
  `al.Grid2D.uniform(...)` of your choice.

For the physics behind each visual — what convergence is, why caustics matter, what
a critical curve traces — see
[`wiki/core/concepts/lensing_basics.md`](../wiki/core/concepts/lensing_basics.md).

## Saving plots

In `2026.5.21+` `autolens.plot` is a flat module of free functions —
the previous object-oriented plotter/configuration classes
are gone. Each plotting function takes `output_path` / `output_filename` /
`output_format` kwargs directly. Define your destination once and reuse it:

```python
from pathlib import Path
import autolens.plot as aplt

PLOT_DIR = Path("scripts/scratch") / "<dataset_or_slug>"   # pick a meaningful slug
PLOT_DIR.mkdir(parents=True, exist_ok=True)
```

After running, the agent quotes `PLOT_DIR.resolve()` and offers
`open <path>` — see `_style.md` "Plot output and path announcement". The
function-style plot API is documented in
[`wiki/core/api/plotting.md`](../wiki/core/api/plotting.md).

## Branch — quick subplots

```python
# Assume `tracer` and `grid` exist (e.g. from al_load_results + al_prepare_imaging_data).
aplt.subplot_tracer(
    tracer=tracer, grid=grid,
    output_path=str(PLOT_DIR), output_format="png",
)               # 2x3: image, source, convergence, potential, deflection y, deflection x

aplt.subplot_galaxies_images(
    tracer=tracer, grid=grid,
    output_path=str(PLOT_DIR), output_format="png",
)               # per-galaxy image-plane images

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Source: `PyAutoLens:autolens/lens/plot/tracer_plots.py`.

## Branch — single quantity at high resolution

`MassProfilePlotter`-style figures are now built by extracting the array from
the profile (or the tracer) and passing it to `aplt.plot_array`:

```python
# Per-quantity overlays on a single mass profile
mass = tracer.galaxies[0].mass
aplt.plot_array(array=mass.convergence_2d_from(grid=grid),
                output_path=str(PLOT_DIR), output_filename="convergence",
                output_format="png", use_log10=True)
aplt.plot_array(array=mass.potential_2d_from(grid=grid),
                output_path=str(PLOT_DIR), output_filename="potential",
                output_format="png")

# Or the whole tracer:
aplt.plot_array(array=tracer.convergence_2d_from(grid=grid),
                output_path=str(PLOT_DIR), output_filename="tracer_convergence",
                output_format="png", use_log10=True)
aplt.plot_array(array=tracer.image_2d_from(grid=grid),
                output_path=str(PLOT_DIR), output_filename="tracer_image",
                output_format="png")

print(f"Saved to: {PLOT_DIR.resolve()}")
```

`tracer.deflections_yx_2d_from(grid=grid)` returns a `VectorYX2D`; access the
two components and plot separately, or use `aplt.subplot_tracer` to get the
combined figure. `Tracer` does not surface magnification, critical curves, or
caustics directly — build the magnification map from the deflection Jacobian
(see [`wiki/core/concepts/lensing_basics.md`](../wiki/core/concepts/lensing_basics.md)).

## Branch — multi-plane systems (>2 redshifts)

When the `Tracer` has more than two lens planes (e.g. cluster lenses), the source
plane is the *final* plane. There is no dedicated plane plotter in the flat function
API — extract each intermediate plane's galaxies via `tracer.planes[i]`, evaluate
their images on the traced grid for that plane, and pass the arrays to
`aplt.plot_array`. See `PyAutoLens:autolens/lens/plot/`.

[`wiki/core/concepts/tracer.md`](../wiki/core/concepts/tracer.md) — multi-plane ray tracing
explanation.

## Combine

- [`al_load_results`](./al_load_results.md) — usually how you get the `Tracer` you're
  plotting.
- [`al_plot_fit_residuals`](./al_plot_fit_residuals.md) — fit quality plots.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) — for
  pixelised sources, the reconstruction is a `FitImaging` property.

## Further reading

- **Student / new to lensing** — [HowToLens: Ray tracing and deflection
  angles](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_2_ray_tracing.ipynb):
  the physics under every tracer plot — how light deflects, how critical curves and
  caustics arise.
- **General reference** — [RTD: Start here](https://pyautolens.readthedocs.io/en/latest/overview/overview_1_start_here.html):
  the `Tracer` object in action — building one, evaluating it on a grid, plotting
  the result.
- **Experienced PyAutoLens user** — [workspace/lens: guides/tracer.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/tracer.py):
  full pattern for inspecting an inferred `Tracer` — ray tracing, profiles, numpy
  arrays, visualization.
