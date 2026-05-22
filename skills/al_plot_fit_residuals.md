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

## Branch — quick subplot

```python
import autolens as al
import autolens.plot as aplt

# Assume `dataset` (al_prepare_imaging_data) and `tracer` (al_load_results) exist.
fit = al.FitImaging(dataset=dataset, tracer=tracer)

fit_plotter = aplt.FitImagingPlotter(fit=fit)
fit_plotter.subplot_fit()
```

The default subplot shows: data, model image, residual map, normalised residual map,
chi-squared map, and (if the fit uses an inversion) the source-plane reconstruction.

Source: `PyAutoLens:autolens/imaging/plot/fit_imaging_plotters.py`.

## Branch — single quantity

```python
fit_plotter.figures_2d(
    data=True, model_image=True, residual_map=True,
    normalized_residual_map=True, chi_squared_map=True,
)
```

## Branch — per-galaxy decomposition

```python
fit_plotter.subplot_of_galaxies(galaxy_index=0)  # lens
fit_plotter.subplot_of_galaxies(galaxy_index=1)  # source
```

Each shows the data, that galaxy's model image, and the residual after subtracting
*only* that galaxy's contribution.

## Branch — interferometer fits

The interferometer fit plotter sits at
`PyAutoLens:autolens/interferometer/plot/fit_interferometer_plotters.py` and exposes
visibility-plane residuals plus a real-space dirty-image-vs-dirty-model panel.

```python
fit = al.FitInterferometer(dataset=dataset, tracer=tracer)
aplt.FitInterferometerPlotter(fit=fit).subplot_fit()
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
