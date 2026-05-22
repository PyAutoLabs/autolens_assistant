---
name: al_adaptive_pixelization
description: Build a model whose source reconstruction uses an adaptive pixelisation (mesh density tracks source brightness or surface density) and adaptive regularisation (smoothing strength inferred from data, not fixed). Use when a uniform mesh wastes resolution on dim regions and under-resolves bright ones — common for complex arcs and ALMA data. More expressive than `al_build_imaging_model`'s "pixelised source" branch, at the cost of more knobs. Pairs with `al_inspect_source_reconstruction` (post-fit inspection). Writes a runnable Python script in ./work/. **Status: stub.**
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
  first?"*

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

- **Student / new to lensing** — [HowToLens: chapter_4 tutorial_5 adaptive](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_5_adaptive_pixelization.ipynb):
  pedagogical adaptive-pixelisation walkthrough.
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  pixelisation feature section.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/features/pixelization/adaptive.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/pixelization/adaptive.py):
  the canonical adaptive setup.

See also [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md)
for the underlying inversion theory.
