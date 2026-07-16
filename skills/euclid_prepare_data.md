---
name: euclid_prepare_data
description: Prepare Euclid strong lens data for the pipeline — validate segmentation outputs, tune binary masks, mark extra-galaxy centres and masks with the GUI tools, and assemble the dataset/<sample>/<dataset>/ folder (multi-HDU FITS + info.json + mask_extra_galaxies.fits). Use when a Euclid lens's inputs need checking or building before modeling; NOT for HST/JWST/generic FITS preparation (al_prepare_imaging_data) and NOT for running fits (euclid_setup_pipeline / euclid_model_lens).
---

# Preparing Euclid data for the pipeline

Bad inputs, not bad models, are the #1 source of biased lens fits — a foreground star
inside the mask or an unflagged neighbouring galaxy will pull the mass model. The
pipeline repo ships the preprocessing used for the Euclid lens samples: segmentation
validation, binary-mask tuning, and GUI tools for marking contaminating objects. The
assistant's real-data gate applies in euclid mode exactly as everywhere else: **plot and
inspect the data before any fit**, and settle contaminant decisions first.

Euclid datasets combine VIS with NIR and ground-based EXT bands (HSC g/z, CFIS u/r,
Pan-STARRS i in the North; DES griz in the South) — see
[`wiki/euclid/entities/ext-surveys.md`](../wiki/euclid/entities/ext-surveys.md). Each
band's PSF depends on the lens's tile and sky coordinates
([`wiki/euclid/concepts/euclid-psf.md`](../wiki/euclid/concepts/euclid-psf.md)), which
is why every dataset carries its own per-band PSFs inside the multi-HDU FITS.

## Ask

- *"Do you have pipeline-ready cutouts already (multi-HDU FITS + info.json), or raw
  segmentation outputs?"* — picks the branch.
- *"Have you visually inspected this lens yet?"* — if not, start there: plot the
  dataset, look for extra galaxies, stars, artefacts.
- *"Galaxy-scale, or is there a nearby group?"* — group-scale lenses need extra-galaxy
  centres so members can enter the model.

## Branch — validate segmentation outputs

For lens samples processed through the segmentation stage, each lens folder gains a
`segmentation/` subfolder (`<object>_flux.fits`, `<object>_binary.fits` for
artefact/source/lens). Build the 5-panel diagnostic PNG (RGB, VIS, source flux with
inferred multiple-image positions, artefact flux, artefact binary) with:

```bash
python preprocess/segmentation.py --sample=<sample>
```

then step through lenses assigning quality labels (OK / no points / fix needed / group
issue / recentering needed) with the annotation GUI:

```bash
python preprocess/validation_GUI.py --sample=<sample>
```

A binary map that misses flux or includes artefacts is tuned per-object with
`preprocess/adjust_binary.py` (reads `segmentation/<OBJECT>_flux.fits`, writes
`segmentation/<OBJECT>_binary.fits`). Bulk-moving segmentation FITS into dataset folders
is `preprocess/move_segmentation_fits.py --dry-run` first, then without the flag.
Citations: `euclid_strong_lens_modeling_pipeline:preprocess/`.

## Branch — mark extra galaxies (masks and centres)

Two GUI tools handle contaminating objects, both writing into the lens's dataset folder:

- `tools/extra_galaxies_mask_gui.py` — paint a `mask_extra_galaxies.fits` over
  neighbouring-galaxy light, foreground stars, or reduction artefacts.
  `util.load_vis_dataset` applies it as **noise scaling**: flagged pixels get their
  variances inflated so they cannot influence the fit, without hard-discarding data.
- `tools/extra_galaxies_centres_gui.py` — mark the (y,x) arcsecond centres of galaxies
  that should enter the *model* (MGE light + isothermal mass) in group-scale fits; the
  standard `start_here.py` fit ignores them, group pipelines use them and expand the
  mask to cover the members.

`tools/psf_size.py` inspects the PSF stamp size when a band's PSF looks truncated.

## Branch — assemble a dataset folder by hand

For a lens from outside the processed samples, build
`dataset/<sample>/<dataset_name>/` yourself:

1. `<dataset_name>.fits` — multi-HDU: image, noise-map, PSF per band, VIS first, with
   MAGZERO and WCS in the header (the photometric zero-point calibration traces to
   OU-PHZ — [`wiki/euclid/concepts/zero-point-corrections.md`](../wiki/euclid/concepts/zero-point-corrections.md)).
2. `info.json` — at minimum `{"pixel_scale": 0.1, "mask_radius": 3.5, "mask_centre": [0.0, 0.0]}`;
   the mask radius should enclose all lensed emission with margin.
3. Optionally `mask_extra_galaxies.fits` from the GUI above.

Then verify the load end-to-end before fitting:

```bash
PYAUTO_TEST_MODE=1 python start_here.py --sample=<sample> --dataset=<dataset_name>
```

which exercises `util.load_vis_dataset` (HDU mapping, MAGZERO, masking, over-sampling)
without a real fit.

## Combine

Once the data loads clean, [`euclid_model_lens`](./euclid_model_lens.md) runs the
staged fits. If your cutout came from non-Euclid imaging and needs noise/PSF work
first, [`al_prepare_imaging_data`](./al_prepare_imaging_data.md) covers the generic
preparation concepts (masking, noise, PSF) that apply before Euclid conventions do.

## Further reading

- **General reference** — [euclid_strong_lens_modeling_pipeline README](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline#readme):
  the dataset conventions the pipeline expects.
- **Experienced PyAutoLens user** — [workspace: data_preparation examples](https://github.com/PyAutoLabs/autolens_workspace/tree/main/scripts/imaging/data_preparation):
  the generic PyAutoLens data-preparation examples the Euclid GUIs are adapted from.
