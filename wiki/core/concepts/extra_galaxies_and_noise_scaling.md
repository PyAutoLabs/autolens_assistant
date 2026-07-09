---
title: Extra galaxies and noise scaling
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/imaging/dataset.py
      - autoarray/dataset/dataset_model.py
      - autoarray/mask/mask_2d.py
    pinned_commit: main
last_updated: 2026-07-09
---

# Extra galaxies and noise scaling

An **extra galaxy** is any source of light in the image that is *not* part of the strong
lens being studied — a nearby companion galaxy, a foreground star, or a data-reduction
artefact — whose emission (and sometimes mass) blends into the field around the lens and
source. Left untreated, this light contaminates the likelihood and biases the inferred lens
model: the fit tries to explain flux that the lens model has no business explaining.

This is the single most common thing to miss when moving real data to modeling. **Always
plot `dataset.png` and look for extra galaxies before composing a model** (see
[`../../../skills/al_prepare_imaging_data.md`](../../../skills/al_prepare_imaging_data.md)).

## Three strategies

There is a spectrum of ways to deal with an extra galaxy; which one fits depends on how close
it is to the lens/source and how much its mass matters:

1. **Noise-scale it (recommended default).** Keep the contaminating pixels in the dataset but
   scale their data toward zero and inflate their noise-map values to very large numbers, so
   they contribute negligibly to the likelihood. This is preferable to removing the pixels
   entirely because, for a pixelised source reconstruction, hard-removing pixels can introduce
   discontinuities in the pixelisation and produce systematics. Done via a
   `mask_extra_galaxies.fits` and `dataset.apply_noise_scaling(...)`.
2. **Model it.** Include the extra galaxy in the lens model as a light profile (to fit and
   subtract its emission) and/or a mass profile (to account for its lensing of the source).
   Use this when the emission blends significantly with the lensed source, or its mass
   perturbs the ray-tracing. Its centre is normally fixed to its observed position to keep the
   model tractable. See the workspace `imaging/features/extra_galaxies/modeling.py`.
3. **Shrink the mask.** Make the circular modelling mask smaller so the extra galaxy falls
   outside it and is dropped from the fit entirely. Simplest, and fine when the contaminant is
   well separated from the arcs — but it removes those pixels rather than down-weighting them,
   so avoid it near a pixelised source.

## The noise-scaling API

Noise scaling needs a FITS mask flagging the contaminating pixels. Load it inverted (so `True`
marks the pixels to scale) and apply it **before** the model mask and over-sampling:

```python
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` means a pixel is scaled.
)
dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
```

A `mask_extra_galaxies.fits` is created interactively with the data-preparation GUI
(`autolens_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py`) or the
manual script (`.../data_preparation/examples/optional/mask_extra_galaxies.py`).

Source: `PyAutoArray:autoarray/dataset/imaging/dataset.py` (`apply_noise_scaling`).

## Sky background

The other light in every image that is not the strong lens is the **sky
background** — sky glow, zodiacal light and unresolved field sources. Data
reduction normally subtracts it, but the subtraction is never perfect, and its
residual is degenerate with the faint outskirts of the lens galaxy's light: an
over-subtracted sky can masquerade as a smaller effective radius or steeper
Sersic index, and the formal errors on those parameters will be underestimated
if the sky is assumed perfect.

When low-surface-brightness structure matters, fit the sky as a model
component: `al.DatasetModel(background_sky_level=...)` adds the sky level as a
free parameter of the non-linear search (one extra dimension), so the
posterior on every light-profile parameter marginalises over the sky
uncertainty. The same `DatasetModel` object also carries `grid_offset` and
`grid_rotation_angle`, the nuisance parameters used for astrometric offsets in
multi-dataset fitting (see
[`multi_wavelength`](./multi_wavelength.md)).

Source: `PyAutoArray:autoarray/dataset/dataset_model.py`. Workspace example:
`autolens_workspace:scripts/imaging/features/advanced/sky_background/modeling.py`
(fits a dataset simulated *without* sky subtraction, so the image outskirts sit
at the sky level rather than zero).

## Galaxy-scale vs group-scale

The strategy split mirrors the lens scale. At **galaxy scale** (one main lens), extra galaxies
are contaminants — noise-scale them out, or model one or two if their mass matters. At **group
and cluster scale**, the "extra" galaxies *are* the science: multiple comparable deflectors
that must be modelled jointly, often via scaling relations. See
[`group_and_cluster_lensing`](./group_and_cluster_lensing.md) for that regime.

## Provided datasets ship a mask

The bundled example datasets `dataset/imaging/cosmos_web_ring/...` and
`dataset/imaging/slacs0946+1006/` each include a ready-made `mask_extra_galaxies.fits`. When
using them, apply the mask via `apply_noise_scaling` **and tell the user explicitly** that it
is being applied and which region it scales out — never silently.

## See also

- [`grids_and_masks`](./grids_and_masks.md) — what a `Mask2D` is and how `apply_mask` differs
  from `apply_noise_scaling`.
- [`../api/datasets`](../api/datasets.md) — the `al.Imaging` API, including `apply_noise_scaling`.
- [`group_and_cluster_lensing`](./group_and_cluster_lensing.md) — when extra galaxies are
  deflectors to model rather than contaminants to scale.
- [`../../../skills/al_prepare_imaging_data.md`](../../../skills/al_prepare_imaging_data.md) —
  the load + inspect + mask + noise-scale recipe.
