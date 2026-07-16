---
name: euclid_workflow_products
description: Turn many Euclid pipeline fits into inspectable products with the workflow/ scripts — .csv model catalogues (csv_make.py), .fits image stacks (fits_make.py), and one-line .png summaries (png_make.py) driven by the PyAutoFit aggregator over the output/ folder. Use when a Euclid lens sample has been fitted and browsing output/ lens-by-lens has become tedious; NOT for inspecting a single fit (al_load_results / al_plot_fit_residuals) or for generic aggregator scripting (al_aggregator_bulk_analysis).
---

# Inspecting Euclid results at sample scale

After the pipeline has run on tens or hundreds of lenses, `output/` holds a full
PyAutoFit result tree per lens per stage — far too much to click through. The
`workflow/` scripts compress a whole sample into three kinds of flat product, all
driven by the PyAutoFit **aggregator** (`PyAutoFit:autofit/aggregator/`), which loads
every completed fit under `output/` and lets you map over them:

- **`workflow/csv_make.py`** — one row per lens: maximum-likelihood parameters, derived
  quantities (Einstein radius, magnitudes from the latent aperture photometry), errors.
  The catalogue you hand to collaborators or feed into population science.
- **`workflow/fits_make.py`** — extract a chosen HDU (e.g. the model lens-subtracted
  image from `model_galaxy_images.fits`) across all lenses into a single folder or
  stacked .fits, so a whole sample opens in DS9 in one go.
- **`workflow/png_make.py`** — cut chosen panels out of each lens's `subplot_fit.png`
  and tile them one-lens-per-line, so fit quality for a full sample is one scroll.

`workflow/example/` holds worked examples of the output these produce.

## Ask

- *"Which stage's results?"* — each pipeline stage (`initial_lens_model`, `sersic`,
  `full_model`, …) has its own output subfolder; the aggregator is pointed at one.
- *"What does the science need — a catalogue, images, or a quick-look?"* — picks the
  script; most samples eventually want all three.
- *"Standard columns/panels, or custom quantities?"* — the scripts are examples meant to
  be copied and adapted; custom latents mean editing the aggregator mapping inside.

## Branch — run and adapt

Each script is run from the repo root and adapted in place (they are examples, not a
frozen CLI):

```bash
python workflow/csv_make.py
python workflow/fits_make.py
python workflow/png_make.py
```

Inside each, the pattern is: build the aggregator over `output/`, filter to the sample
and stage, then map a per-fit extraction into the product file. When you need a
quantity the examples don't export, the latent variables computed at fit time
(aperture fluxes, AB magnitudes via MAGZERO, magnification — see
`euclid_strong_lens_modeling_pipeline:util.py`, `LatentEuclid`) are already in each
fit's samples, so most additions are a one-line column, not a re-fit.

Products are for **inspection and science**, not archival — they regenerate from
`output/` at any time, so keep them out of git and re-run after re-fits.

## Combine

- A lens flagged bad in the .png sweep → [`al_load_results`](./al_load_results.md) and
  [`al_plot_fit_residuals`](./al_plot_fit_residuals.md) for the deep dive, then
  [`al_debug_fit_failure`](./al_debug_fit_failure.md) if the fit itself is at fault.
- Catalogue-level population questions (mass slopes, magnification distributions) build
  on the .csv — [`al_aggregator_bulk_analysis`](./al_aggregator_bulk_analysis.md) covers
  the generic aggregator patterns behind these scripts.
- Fitting the sample in the first place: [`euclid_hpc_runs`](./euclid_hpc_runs.md).

## Further reading

- **General reference** — [euclid_strong_lens_modeling_pipeline README](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline#readme):
  the workflow folder's role after `start_here.py` runs on many lenses.
- **Experienced PyAutoLens user** — [workspace: results workflow examples](https://github.com/PyAutoLabs/autolens_workspace/tree/main/scripts/results):
  the generic aggregator/results examples the Euclid workflow scripts specialise.
