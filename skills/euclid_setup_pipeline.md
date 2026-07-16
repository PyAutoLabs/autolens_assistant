---
name: euclid_setup_pipeline
description: Set up and run the Euclid strong lens modeling pipeline (euclid mode entry point). Clone euclid_strong_lens_modeling_pipeline, verify the PyAutoLens + JAX environment, understand the dataset/<sample>/<dataset>/ layout, and run start_here.py as a black box on a Euclid lens. Use for any "model Euclid data" request that hasn't already got the pipeline running; NOT for general non-Euclid lens modeling (al_build_imaging_model) or for HST/JWST data preparation.
---

# Setting up the Euclid pipeline

This is the entry point of the assistant's **euclid mode**: modeling Euclid strong
lenses through the collaboration's standard pipeline repo,
[`euclid_strong_lens_modeling_pipeline`](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline),
rather than hand-built PyAutoLens scripts. The pipeline exists so every Euclid lens is
modeled the same way — an MGE lens + source with an SIE + shear mass model as the
standard first fit — and so its outputs (deblended images, aperture photometry,
magnifications) are uniform across the collaboration and the data release.

Euclid VIS imaging is 0.1"/pixel with a ~0.16" PSF over the 14,000 deg² Wide Survey —
see [`wiki/euclid/entities/euclid-mission.md`](../wiki/euclid/entities/euclid-mission.md)
and [`wiki/euclid/entities/vis.md`](../wiki/euclid/entities/vis.md) for the mission and
instrument context, and
[`wiki/euclid/sources/euclid-strong-lensing.md`](../wiki/euclid/sources/euclid-strong-lensing.md)
for the discovery papers behind the lens samples you will be modeling.

## Ask

- *"Do you already have the pipeline repo cloned and PyAutoLens installed, or are we
  starting from scratch?"* — decides whether to walk installation or jump to running.
- *"Are you on a GPU machine?"* — the pipeline is ~10 min/lens on a GPU, ~20 min on an
  8-core CPU; JAX must be installed with GPU support **before** PyAutoLens for the fast
  path.
- *"Is your lens one of the bundled examples, or your own cutout?"* — your own data
  needs the dataset-layout branch below and possibly
  [`euclid_prepare_data`](./euclid_prepare_data.md) first.

## Branch — install and verify

The pipeline runs from a clone, not a pip package. PyAutoLens supports Python 3.12+,
3.13 recommended:

```bash
pip install --upgrade pip
pip install autolens
git clone https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline
cd euclid_strong_lens_modeling_pipeline
```

For GPU acceleration install JAX with GPU support *first* (per the
[JAX installation guide](https://jax.readthedocs.io/en/latest/installation.html)), then
PyAutoLens — installing the other way round leaves you on the CPU fallback (a warning is
printed). Verify with the assistant's environment check
([`al_setup_environment`](./al_setup_environment.md)) if anything looks off.

The repo pushes its own config at run time
(`euclid_strong_lens_modeling_pipeline:start_here.py` does `conf.instance.push` on its
`config/` folder), so no PyAutoLens config setup is needed — running from the repo root
is the only requirement.

## Branch — the dataset layout

Datasets live at `dataset/<sample>/<dataset_name>/` — the sample groups lenses (e.g. the
bundled `q1_walsmley` Q1 discovery sample), and each lens folder contains:

- `<dataset_name>.fits` — one multi-HDU FITS file with the image, noise-map and PSF per
  waveband (VIS first, then NIR / EXT bands). HDU mapping is resolved by
  `euclid_strong_lens_modeling_pipeline:util.py` (`dataset_instrument_hdu_dict_via_fits_from`).
- `info.json` — per-lens metadata: `pixel_scale` (0.1 for VIS), `mask_radius`,
  `mask_centre`, and optionally redshifts.
- `mask_extra_galaxies.fits` *(optional)* — noise-scaling mask for contaminating
  objects, produced by the GUI tools ([`euclid_prepare_data`](./euclid_prepare_data.md)).
- `rgb_*.png` — quick-look colour images.

`util.load_vis_dataset` reads all of this in one call: it loads the VIS image/noise/PSF,
anchors model priors on the brightest central pixel, reads the photometric zero-point
(MAGZERO) and WCS from the FITS header, applies the extra-galaxies noise scaling and
circular mask, sets standard adaptive over-sampling (4/2/1× radial bins), and loads the
lowest-resolution band PSF for aperture photometry. The per-band PSF is unique to each
lens's tile and sky position — see
[`wiki/euclid/concepts/euclid-psf.md`](../wiki/euclid/concepts/euclid-psf.md).

## Branch — run the pipeline black-box

```bash
python start_here.py --sample=q1_walsmley --dataset=102018665_NEG570040238507752998 --iterations_per_quick_update=10000
```

This fits the standard initial lens model — MGE lens light (2×20 Gaussians) + SIE +
external shear + MGE source (20 Gaussians), ~15 non-linear parameters, Nautilus with
`n_live=100` — and writes results to `output/<sample>/<dataset>/initial_lens_model/`.
`--iterations_per_quick_update` controls how often on-the-fly visualisations refresh, so
you can watch the model improve during the fit. The science and inference framing is
documented inline in `euclid_strong_lens_modeling_pipeline:start_here.py` — read it
end-to-end once; every other pipeline is documented relative to it.

Key outputs: the SIE + shear mass model, deblended lens/source images, MGE lens and
source models, plus Euclid-specific latent variables (aperture fluxes in the VIS band
converted to AB magnitudes via MAGZERO, magnification) computed by
`euclid_strong_lens_modeling_pipeline:util.py` (`AnalysisImaging`, `LatentEuclid`).

Before a long run, smoke the wiring with `PYAUTO_TEST_MODE=1` — the fit short-circuits
but import/config/dataset errors surface in seconds.

## Combine

- [`euclid_model_lens`](./euclid_model_lens.md) — the staged pipelines beyond the
  initial fit: Sersic photometry, lens-only MGE subtraction, multi-waveband fits, the
  full SLaM pixelized model.
- [`euclid_prepare_data`](./euclid_prepare_data.md) — segmentation checks, extra-galaxy
  masks and centres for your own cutouts.
- [`euclid_workflow_products`](./euclid_workflow_products.md) — once you have many
  lenses fitted, export .csv/.fits/.png summaries instead of browsing `output/`.
- [`euclid_hpc_runs`](./euclid_hpc_runs.md) — push the project to a supercomputer and
  run lens samples as SLURM batches.

## Further reading

- **General reference** — [euclid_strong_lens_modeling_pipeline README](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline#readme):
  installation, the black-box run, and the pipeline inventory.
- **Experienced PyAutoLens user** — [RTD: Features overview](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  the PyAutoLens features (MGE, pixelizations, SLaM) the pipeline composes.
