---
name: al_prepare_imaging_data
description: Load CCD imaging of a strong lens (HST / JWST / Euclid / ground-based) from FITS files into an `al.Imaging` dataset, then apply a mask, over-sampling, and noise scaling so it's ready for model fitting. Produces a runnable Python script in scripts/ that the user can re-run on their own data. Use before invoking `al_build_imaging_model`. For interferometer data, `al_build_interferometer_model` covers loading + masking inline.
---

# Preparing CCD imaging for lens modelling

Before fitting a model you need three things on disk: the image counts, a per-pixel
noise map, and the point-spread function (PSF). This skill loads them, applies a
circular mask around the lens, sets up adaptive over-sampling so light profiles are
evaluated accurately where they matter, and (optionally) scales the noise to mask out
contaminating galaxies. The output is a ready-to-fit `al.Imaging` object.

For real observational data, treat preprocessing as part of model setup, not an
optional cleanup step. **The first action is always to plot the dataset and look at it**:
call `aplt.subplot_imaging_dataset(dataset=dataset, output_path=..., output_filename="dataset",
output_format="png")` (the functional plot API takes the output path directly),
quote the `dataset.png` path, and ask the user to confirm they've inspected it — flagging
**extra galaxies** (nearby companions, foreground stars, data-reduction artefacts) as the
single most important thing to check. Only once that's done, decide how large the modelled
region should be, whether any nearby objects or artifacts must be excluded (and how —
noise-scale a mask, or shrink the circular mask), and whether a manual or GUI-assisted
masking step is needed to define those regions. Don't speed-run past this into modeling.

Background: [`wiki/core/concepts/grids_and_masks.md`](../wiki/core/concepts/grids_and_masks.md)
covers what a mask and an over-sample grid actually are; the canonical reference for
the loader is `PyAutoArray:autoarray/dataset/imaging/dataset.py` and the workspace
example at `autolens_workspace:scripts/imaging/start_here.py`.

## Ask

Before generating code, ask:

- *"Is this simulated data or real observational imaging?"* — simulated data often
  ships already clean; real data usually needs explicit preprocessing decisions before
  modelling starts.
- *"What's the path to your data, noise map and PSF FITS files, and the pixel scale
  in arcseconds/pixel?"* (Without these you can't load anything.)
- *"How large is the lens system on the sky?"* — drives the mask radius. A galaxy-
  scale lens fits in a 2–3" circular mask; a group lens may need 5–10".
- *"What parts of the image should not be modelled?"* — e.g. nearby galaxies,
  foreground stars, diffraction spikes, cosmic rays, sky residuals, detector edges.
- *"Do you need a manual or GUI-assisted masking step to mark excluded regions before
  fitting?"* — if yes, define that mask first and only then continue to model setup.
- *"Are there contaminating galaxies near the lens that you want to noise-scale out?"*
  — if yes, you'll need an `extra_galaxies` mask (see the branch below).

## Branch — minimal load + mask

For simulated data, or for real data that has already been inspected and cleaned, this
is often enough as a starting point:

```python
# scripts/prepare_imaging.py
from autoconf import jax_wrapper  # set JAX env before other PyAuto* imports
from pathlib import Path
import autolens as al
import autolens.plot as aplt

dataset_path = Path("dataset/imaging/<your_lens_name>")  # adjust

dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,  # arcsec/pixel — set this for your data
)

mask = al.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=2.5,  # arcsec
)

dataset = dataset.apply_mask(mask=mask)

# Adaptive over-sampling: evaluate light profiles on a finer sub-grid near the lens
# centre, coarser sub-grid far from it. This is the standard recipe.
over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 1],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

# Save the inspection plot — never rely on interactive display.
plot_dir = Path("scripts/scratch") / dataset_path.name
plot_dir.mkdir(parents=True, exist_ok=True)
aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path=str(plot_dir),
    output_filename="dataset",
    output_format="png",
)
print(f"Dataset plot saved to: {plot_dir.resolve()}")
```

After running, quote the printed `dataset.png` path to the user and hold for their
confirmation that they have inspected it (per the real-data gate) before moving on.

Source citations:
- `PyAutoArray:autoarray/dataset/imaging/dataset.py` — `Imaging.from_fits`, `apply_mask`,
  `apply_over_sampling`.
- `PyAutoArray:autoarray/mask/mask_2d.py` — `Mask2D.circular`.
- `PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py` — `over_sample_size_via_radial_bins_from`.

Read [`wiki/core/concepts/grids_and_masks.md`](../wiki/core/concepts/grids_and_masks.md) for
*why* over-sampling matters (steep light profiles in pixels near the centre alias
without sub-grid integration).

For real data, do not treat the circular mask radius above as automatic truth. It is an
initial modelling choice that should be checked against the arc extent and against any
features you intend to exclude from the likelihood.

## Branch — with noise scaling for contaminating galaxies

If a nearby foreground star or unrelated galaxy is bleeding into your mask, do not leave
it in the fit. The preferred fix is to keep those pixels in the dataset but inflate their
noise so they contribute negligibly to the likelihood (rather than removing them entirely,
which can create discontinuities for a pixelised source). This needs a FITS mask flagging
the contaminating pixels. The conceptual background — noise-scale vs model-the-galaxy vs
shrink-the-mask — is in
[`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

**Provided datasets already ship a mask.** The bundled `dataset/imaging/cosmos_web_ring/...`
and `dataset/imaging/slacs0946+1006/` datasets each include a `mask_extra_galaxies.fits`.
Load it and apply it — and **tell the user plainly** that you are doing so and which region
it scales out; never apply it silently:

```python
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` means a pixel is scaled.
)
dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
```

Apply this **before** the model mask and over-sampling.

**The user's own data, with a visible extra galaxy but no mask.** Two options — surface both:

- **Create a `mask_extra_galaxies.fits` and noise-scale it** (preferred when the contaminant
  is close to the lens/source). Use the GUI
  `autolens_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py` to scribble
  the mask interactively, or the manual
  `autolens_workspace:scripts/imaging/data_preparation/examples/optional/mask_extra_galaxies.py`.
  Then load + `apply_noise_scaling` as above.
- **Shrink the circular mask** so the extra galaxy falls outside it (simpler, and fine when the
  contaminant is well separated from the arcs). This *removes* those pixels from the fit rather
  than down-weighting them — cheaper, but avoid it near a pixelised source where dropped pixels
  can introduce reconstruction discontinuities.

Source: `PyAutoArray:autoarray/dataset/imaging/dataset.py` (`apply_noise_scaling`).

## Branch — with a manual exclusion mask

If the user has regions that should not contribute to the fit at all, create a manual
mask for those pixels first. This is often needed for real data with bright nearby
objects, image defects, subtraction residuals, or field features that lie inside an
otherwise sensible circular lens mask.

The end product should be a FITS mask that records the user-defined exclusion regions.
Apply that exclusion step before the main model mask and over-sampling. If the user has
not yet defined those regions, pause here and create the mask rather than continuing
straight into modelling.

## Branch — if you don't have a noise map or PSF

These are required. Workspace scripts under
`autolens_workspace:scripts/imaging/data_preparation/` describe how to measure them
from raw data:

- Noise map from a sigma image or from background-RMS estimation.
- PSF from a stacked star in the field.

If the user genuinely doesn't have these yet, walk them through measuring them rather
than faking placeholders. Faked noise maps produce nonsensical posteriors.

## Combine

Once `dataset` is loaded and masked, hand it to:

- [`al_build_imaging_model`](./al_build_imaging_model.md) — compose a `Tracer` and
  wrap it in `al.AnalysisImaging`.
- [`al_run_search`](./al_run_search.md) — execute the fit.

If you're new to *what* this dataset represents physically, read
[`wiki/core/concepts/lensing_basics.md`](../wiki/core/concepts/lensing_basics.md) first.

## Further reading

- **Student / new to lensing** — [HowToLens: Real telescope imaging and
  instrumental effects](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_6_data.ipynb):
  CCD imaging from instruments like HST, telescope optics, exposure, detector noise.
- **General reference** — [RTD: New user guide](https://pyautolens.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html):
  decision-tree routing by lens scale and data type — orients a new PyAutoLens user
  before they touch FITS data.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/data_preparation/start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/imaging/data_preparation/start_here.py):
  canonical reference for getting telescope data analysis-ready.
