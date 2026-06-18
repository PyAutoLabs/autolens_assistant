---
name: al_plot_fit_residuals
description: Plot fit-vs-data diagnostics — model image, residuals, normalised residuals, chi-squared map, per-galaxy model images, source-plane reconstruction. Use after `al_load_results` has handed you a tracer + dataset, or after `al_run_search` completes. The standard "is this a good fit?" inspection.
---

# Plotting fit residuals

The fit object (`FitImaging` / `FitInterferometer`) is where the model meets the
data. The residual = data − model_image. The chi-squared map = residual² / noise².
A good fit has residuals that look like the noise; a bad fit has structured
residuals (arcs, double images, lens-light leakage).

Canonical reference: `autolens_workspace:scripts/guides/plot/examples/plotters.py`.

## Ask

- *"What do you want to see — quick overview, specific quantity, or per-galaxy
  decomposition?"*
- *"Did the fit use a pixelised source?"* — pixelised fits also expose
  source-plane image and reconstruction-error maps; see
  [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md).

## Saving plots

In `2026.5.21+` `autolens.plot` is a flat module of free functions —
`FitImagingPlotter` / `MatPlot2D` / `Output` no longer exist. The function-call
API takes `output_path` / `output_filename` / `output_format` kwargs directly:

```python
from pathlib import Path
import autolens as al
import autolens.plot as aplt

PLOT_DIR = Path("scripts/scratch") / "<dataset_or_slug>"   # pick a meaningful slug
PLOT_DIR.mkdir(parents=True, exist_ok=True)
```

After running, the agent quotes `PLOT_DIR.resolve()` and offers
`open <path>` — see `_style.md` "Plot output and path announcement". The
function-style plot API is documented in
[`wiki/core/api/plotting.md`](../wiki/core/api/plotting.md).

## Branch — quick subplot

```python
# Assume `dataset` (al_prepare_imaging_data) and `tracer` (al_load_results) exist.
fit = al.FitImaging(dataset=dataset, tracer=tracer)

aplt.subplot_fit_imaging(
    fit=fit,
    output_path=str(PLOT_DIR), output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

The default subplot shows: data, model image, residual map, normalised residual map,
chi-squared map, and (if the fit uses an inversion) the source-plane reconstruction.

Source: `PyAutoLens:autolens/imaging/plot/fit_imaging_plots.py`.

## Branch — single quantity

The previous `FitImagingPlotter.figures_2d(...)` is replaced by extracting the
desired array from the `FitImaging` object and plotting it directly:

```python
aplt.plot_array(array=fit.data,
                output_path=str(PLOT_DIR), output_filename="data",
                output_format="png")
aplt.plot_array(array=fit.model_data,
                output_path=str(PLOT_DIR), output_filename="model_image",
                output_format="png")
aplt.plot_array(array=fit.residual_map,
                output_path=str(PLOT_DIR), output_filename="residuals",
                output_format="png", symmetric=True)
aplt.plot_array(array=fit.normalized_residual_map,
                output_path=str(PLOT_DIR), output_filename="normalized_residuals",
                output_format="png", symmetric=True)
aplt.plot_array(array=fit.chi_squared_map,
                output_path=str(PLOT_DIR), output_filename="chi_squared",
                output_format="png")

print(f"Saved to: {PLOT_DIR.resolve()}")
```

## Branch — per-galaxy decomposition

```python
# Per-plane fit subplots (replaces FitImagingPlotter.subplot_of_galaxies(...)):
aplt.subplot_fit_imaging_of_planes(
    fit=fit, output_path=str(PLOT_DIR), output_format="png",
)

# Per-galaxy contribution images:
aplt.subplot_fit_imaging_of_galaxy(
    fit=fit, output_path=str(PLOT_DIR), output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

## Branch — interferometer fits

The interferometer fit subplots are at
`PyAutoLens:autolens/interferometer/plot/fit_interferometer_plots.py`:

```python
fit = al.FitInterferometer(dataset=dataset, tracer=tracer)
aplt.subplot_fit_interferometer(
    fit=fit, output_path=str(PLOT_DIR), output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

## Reading residuals

Wiki: [`wiki/core/concepts/lensing_basics.md`](../wiki/core/concepts/lensing_basics.md) for
what each residual pattern usually means physically. Common cases:

- **Structured arcs in residuals** → source model not flexible enough; try pixelised.
- **Double-image residual signature** → mass model slightly off; add positions.
- **Centre-of-lens residual blob** → lens light model missing or wrong.

## Combine

- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — if residuals are bad, this
  is the diagnosis loop.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) — for
  pixelised inversion diagnostics.
- [`al_plot_tracer`](./al_plot_tracer.md) — model-only plots (no dataset needed).

## Further reading

- **Student / new to lensing** — [HowToLens: Fitting lens models to observational
  data](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_7_fitting.ipynb):
  introduces the fit object, residuals, and chi-squared — what each diagnostic plot
  is *telling* you.
- **General reference** — [RTD: Likelihood function](https://pyautolens.readthedocs.io/en/latest/general/likelihood_function.html):
  how PyAutoLens computes the likelihood the residuals contribute to — useful for
  interpreting structured residuals statistically.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/results/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/results/start_here.py):
  production-quality fit inspection — residuals, chi-squared, FITS exports.
