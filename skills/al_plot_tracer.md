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

Every recipe below saves to disk through `aplt.Output(...)` so plots persist
for review. Define this once at the top of your script and reuse it across
branches:

```python
from pathlib import Path
import autolens.plot as aplt

PLOT_DIR = Path("work/plots") / "<dataset_or_slug>"   # pick a meaningful slug
PLOT_DIR.mkdir(parents=True, exist_ok=True)

def _mat_plot(filename: str) -> aplt.MatPlot2D:
    return aplt.MatPlot2D(
        output=aplt.Output(path=str(PLOT_DIR), filename=filename, format="png")
    )
```

After running, the agent quotes `PLOT_DIR.resolve()` and offers
`open <path>` — see `_style.md` "Plot output and path announcement".

## Branch — quick subplots

```python
# Assume `tracer` and `grid` exist (e.g. from al_load_results + al_prepare_imaging_data).
aplt.TracerPlotter(
    tracer=tracer, grid=grid, mat_plot_2d=_mat_plot("tracer_subplot"),
).subplot_tracer()          # 2x3: image, source, convergence, potential, deflection y, deflection x

aplt.TracerPlotter(
    tracer=tracer, grid=grid, mat_plot_2d=_mat_plot("galaxies_images"),
).subplot_galaxies_images()  # per-galaxy image-plane images

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Source: `PyAutoLens:autolens/lens/plot/tracer_plotters.py`.

## Branch — critical curves + caustics overlay

The critical curve is the image-plane locus where magnification → ∞. Its source-plane
counterpart is the caustic. Both are routinely overlaid on the data for figures.

```python
visuals = aplt.Visuals2D(
    critical_curves=tracer.critical_curves_from(grid=grid),
    caustics=tracer.caustics_from(grid=grid),
)

aplt.TracerPlotter(
    tracer=tracer, grid=grid,
    visuals_2d=visuals,
    mat_plot_2d=_mat_plot("critical_curves_caustics"),
).figures_2d(image=True)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Source: `PyAutoLens:autolens/lens/tracer.py` (`critical_curves_from`, `caustics_from`).

Wiki: [`wiki/core/concepts/lensing_basics.md`](../wiki/core/concepts/lensing_basics.md) and
[`wiki/core/api/plotting.md`](../wiki/core/api/plotting.md).

## Branch — single quantity at high resolution

For one specific quantity:

```python
aplt.MassProfilePlotter(
    mass_profile=tracer.galaxies[0].mass, grid=grid,
    mat_plot_2d=_mat_plot("lens_mass_quantities"),
).figures_2d(convergence=True, deflections_y=True, deflections_x=True, potential=True)
```

Or for the whole tracer:

```python
aplt.TracerPlotter(
    tracer=tracer, grid=grid, mat_plot_2d=_mat_plot("tracer_quantities"),
).figures_2d(image=True, source_plane=True, convergence=True, magnification=True)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

## Branch — multi-plane systems (>2 redshifts)

When the `Tracer` has more than two lens planes (e.g. cluster lenses), the source
plane is the *final* plane. Plot each intermediate plane via
`tracer.planes[i].galaxies[j]` and the dedicated `PlanePlotter`. See
`PyAutoLens:autolens/lens/plot/`.

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
- **Experienced PyAutoLens user** — [workspace/lens: guides/tracer.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/tracer.py):
  full pattern for inspecting an inferred `Tracer` — ray tracing, profiles, numpy
  arrays, visualization.
