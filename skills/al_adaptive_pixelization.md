---
name: al_adaptive_pixelization
description: Build a model whose source reconstruction uses an adaptive pixelisation (mesh density tracks source brightness or surface density) and adaptive regularisation (smoothing strength inferred from data, not fixed). Use when a uniform mesh wastes resolution on dim regions and under-resolves bright ones — common for complex arcs and ALMA data. More expressive than `al_build_imaging_model`'s "pixelised source" branch, at the cost of more knobs. Pairs with `al_inspect_source_reconstruction` (post-fit inspection). Writes a runnable Python script in scripts/. **Status: stub.**
---

# Adaptive pixelisation + adaptive regularisation

A fixed-resolution pixelised source treats every region of the source
plane the same. An adaptive pixelisation concentrates pixels where the
flux concentrates, and adaptive regularisation lets the smoothness
strength vary spatially — both inferred jointly with the lens parameters.

The wins are sharper at high signal-to-noise and especially for
interferometer data where rectangular meshes waste capacity on empty
sky.

Workspace path: `autolens_workspace:scripts/imaging/features/pixelization/adaptive.py`,
`scripts/imaging/features/pixelization/delaunay.py`.

## Ask

- *"Mesh type — Delaunay (default adaptive), KMeans-Voronoi, Hilbert
  (memory-efficient for groups), rectangular adaptive?"*
- *"Regularisation — constant (single strength), split (different per
  region), brightness-adaptive (strength scales with local source
  flux)?"*
- *"Adapt-image source — do you have a converged base fit to use as the
  adapt-image, or should we bootstrap from a parametric source fit
  first?"* — either way the source adapt image is capped at S/N 3.0
  before use (see below); the cap applies regardless of which fit it
  came from.

## Adapt image S/N cap (always)

The Hilbert image-mesh weights and the adaptive regularization pixel signals are both
max-normalised — `(adapt_image / max) ** power` — so the brightest peak of a raw
signal-to-noise adapt image sets the scale for everything else. Fainter multiply-imaged
features fall to a few percent of that weight and lose both source-pixel density and
regularization weight, so the source adapt image is capped at S/N 3.0 wherever it is
built. The library applies no cap; it is the script's job at every site.

Apply it immediately after the dict is built, before `al.AdaptImages(...)` or a Hilbert
`image_plane_mesh_grid_from(adapt_data=...)`:

```python
galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(result=result)

adapt_image_snr_cap = 3.0

source_adapt_image = galaxy_image_name_dict["('galaxies', 'source')"].copy()
source_adapt_image[source_adapt_image > adapt_image_snr_cap] = adapt_image_snr_cap
galaxy_image_name_dict["('galaxies', 'source')"] = source_adapt_image
```

Rules:

- **Cap a copy, never the dict entry in place.** `.copy()` keeps the class and mask; an
  in-place cap would silently truncate the raw image every later consumer shares.
- **Anything that needs the raw image binds it before the cap.** The adaptive
  over-sampling map (`np.where(source_image_raw > 3.0, 4, 2)`, see "Adaptive pixelization
  over-sampling" below) reads a
  `source_image_raw = galaxy_image_name_dict["('galaxies', 'source')"]` bound above the cap
  block, because the capped image never exceeds the threshold.
- **Every stage that builds `AdaptImages` from a source image gets the cap** — `source_lp`,
  `source_pix_*`, `light_lp` and `mass_total` alike; the three lines repeat per stage.
- Scripts with more than one source cap every source key present
  (`"('galaxies', 'source_0')"`, `"('galaxies', 'source_1')"`, …).

### Interferometer

Interferometer adapt images are real-space *model* images in flux units
(`use_model_images=True`): the interferometer dirty noise map is a dirty beam rather than a
noise map, so dividing by it does not give a usable S/N image. Derive the clip level from a
beam-smoothed S/N instead — transform the model image to a dirty image, divide by the
homogeneous image-plane noise, and clip the copy at the flux where that S/N crosses 3.0:

```python
adapt_image_snr_cap = 3.0

source_adapt_image = galaxy_image_name_dict["('galaxies', 'source')"].copy()
sigma_pix = np.sqrt(0.5 * np.sum(np.abs(dataset.noise_map.array) ** 2))
dirty_source = dataset.transformer.image_from(
    visibilities=dataset.transformer.visibilities_from(image=source_adapt_image)
)
above_cap = source_adapt_image.array[
    dirty_source.array / sigma_pix > adapt_image_snr_cap
]
if above_cap.size:
    source_adapt_image[source_adapt_image > above_cap.min()] = above_cap.min()
else:
    print(
        "Adapt image S/N cap not applied: no pixel reaches S/N 3.0 in the dirty image."
    )
galaxy_image_name_dict["('galaxies', 'source')"] = source_adapt_image
```

`sigma_pix` is the square root of *half* the summed visibility variances, because the dirty
image is the real part of the transform.

Worked sites to copy from:

- `autolens_workspace:scripts/guides/modeling/slam_start_here.py` — the canonical SLaM
  template, capped at every stage.
- `autolens_workspace:scripts/imaging/features/pixelization/delaunay.py` — the cap feeding
  a Hilbert image mesh.
- `autolens_workspace:scripts/interferometer/features/pixelization/slam.py` — the
  interferometer form above.

## Adaptive pixelization over-sampling (from `source_pix_2`)

Every SLaM pipeline — imaging, group, multi-galaxy, multi-dataset — over-samples the
pixelization grid adaptively from `source_pix_2` onwards: sub-size 4 where the source is
detected, 2 elsewhere. Build the map from the *raw* (pre-cap) source entry and re-apply the
dataset before the fit is composed; `source_pix_2` and every later stage receive that
dataset.

```python
signal_to_noise_threshold = 3.0

source_image_raw = al.galaxy_name_image_dict_via_result_from(result=source_pix_result_1)[
    "('galaxies', 'source')"
]

over_sample_size_pixelization = al.Array2D(
    values=np.where(source_image_raw > signal_to_noise_threshold, 4, 2), mask=dataset.mask
)

dataset = dataset.apply_over_sampling(
    over_sample_size_pixelization=over_sample_size_pixelization
)
```

- **The dict entry is already a signal-to-noise map**, so it is thresholded directly.
  `al.galaxy_name_image_dict_via_result_from` with its default `use_model_images=False`
  returns `subtracted_image / noise_map` (its on-disk cache is literally
  `galaxy_images_snr.fits`); only `use_model_images=True` returns flux-unit model images.
  The function's docstring says "model-image" and is misleading.
- **Never do this:** `al.util.over_sample.over_sample_size_via_adapt_from(data=<S/N map>,
  noise_map=...)`. That helper divides by the noise itself, so feeding it an S/N map divides
  twice (~18x inflation on HST-depth data — ~90 % of the mask at sub-size 4 instead of
  ~30 %), and its `signal_to_noise_cut` defaults to 5.0 and silently drops to `max / 2` when
  the map's maximum is below `2 * cut`. The workspace no longer calls it anywhere.
- **`source_pix_1` is exempt** — it keeps the library default uniform sub-size (4), because
  its adapt image comes from the parametric SOURCE LP fit and is not yet reliable enough to
  steer over-sampling.
- **Interferometer SLaM does not do this** — a pixelization fit to visibilities cannot be
  over-sampled.

## Branch — Delaunay mesh + adaptive brightness regularisation

> TODO: recipe. Pattern: `pix = al.Pixelization(mesh=al.mesh.Delaunay(...),
> regularization=al.reg.AdaptiveBrightnessSplit(...))` ; wrap in a
> `Galaxy`; analysis needs `adapt_images` set from the bootstrap fit.
> See `PyAutoArray:autoarray/inversion/...` and
> `PyAutoLens:autolens/imaging/...`.

## Branch — bootstrap workflow

Two-stage: (1) fit with a parametric source to produce an adapt image,
(2) refit with the adaptive pixelisation, using the parametric model
image as the adapt source.

> TODO: recipe.

## Combine

- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md)
  — post-fit inspection of the reconstructed source + regularisation
  state.
- [`al_chain_searches`](./al_chain_searches.md) — the bootstrap is a
  classic two-search chain.
- [`al_datacube_modeling`](./al_datacube_modeling.md) — datacube
  pixelisation is similar but spectrally extended.

## Further reading

- **Student / new to lensing** — [HowToLens: chapter_3 tutorial_8 adaptive](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_pixelizations/tutorial_8_adaptive_pixelization.ipynb):
  pedagogical adaptive-pixelisation walkthrough.
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  pixelisation feature section.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/features/pixelization/adaptive.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/imaging/features/pixelization/adaptive.py):
  the canonical adaptive setup.

See also [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md)
for the underlying inversion theory.
