---
name: al_inspect_source_reconstruction
description: Inspect a pixelised source reconstruction from a completed fit — source-plane image, mesh / regularisation state, reconstruction error, and the inversion's linear solution. Pixelised sources are common for complex arcs and for ALMA/JVLA visibilities. Use after `al_load_results` has handed you the dataset + tracer; needs to rebuild the `FitImaging` because pixelisation state isn't stored in `tracer.json`.
---

# Inspecting a pixelised source reconstruction

When the source has been reconstructed on a pixel grid (Delaunay / Voronoi /
rectangular mesh) rather than as a parametric Sersic, the interesting object is the
**inversion** — the linear solution that mapped source-plane pixels to image-plane
counts. Pixelised reconstructions live in `FitImaging.inversion`, *not* in the
saved `tracer.json`. To see them you have to rebuild the fit.

For the theory — what regularisation does, what makes a pixelisation adaptive vs.
fixed, why the inversion can demagnify pathologically without a positions penalty —
read [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md).

Canonical reference:
`autolens_workspace:scripts/guides/plot/advanced/plotters_pixelization.py`.

## Ask

- *"What do you want to look at — the source image on its mesh, the regularisation
  matrix structure, the reconstruction error, the data-mapping matrix?"*
- *"Was this a parametric or pixelised fit?"* — if parametric, this skill doesn't
  apply; use [`al_plot_tracer`](./al_plot_tracer.md) for the source-plane image.

## Saving plots

`autolens.plot` in `2026.5.21+` is a flat module of free functions — the old
`InversionPlotter` / `MatPlot2D` / `Output` classes are gone. Plot the
inversion's component arrays directly via `aplt.plot_array`:

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

> ⚠️ **Known regression (still open as of `2026.7.6`).** `Delaunay` and
> `KNNBarycentric` crash inside `FitImaging` (`'NoneType' object has no attribute
> 'array'`), and `ConstantSplit` is broken on `RectangularUniform`. Use
> `al.mesh.RectangularUniform` + `al.reg.Constant` for now; tracking:
> <https://github.com/Jammy2211/PyAutoArray/issues/332>.

## Branch — source-plane reconstruction

Rebuild the fit so the inversion is computed, then plot the components:

The quickest full view is the fit subplot — when the fit uses an inversion its
final panel *is* the source-plane reconstruction:

```python
# `dataset` from al_prepare_imaging_data, `tracer` from al_load_results.
fit = al.FitImaging(dataset=dataset, tracer=tracer)

aplt.subplot_fit_imaging(
    fit=fit, output_path=str(PLOT_DIR), output_format="png",
)
```

For component-level access, the inversion exposes (names verified against the
2026.7 stack):

```python
inv = fit.inversion

# Image-plane image the linear solution reconstructs (Array2D — plottable):
aplt.plot_array(array=inv.mapped_reconstructed_data,
                output_path=str(PLOT_DIR),
                output_filename="mapped_reconstruction",
                output_format="png")

# Source-plane solution: a 1D vector of per-source-pixel intensities
# (keyed per mapper in inv.reconstruction_dict). For a RectangularUniform
# mesh, reshape to the mesh's native 2D shape to plot it.
reconstruction = inv.reconstruction

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Source: `PyAutoArray:autoarray/inversion/inversion/`.

## Branch — mesh + regularisation diagnostics

The previous object-oriented inversion plotter API is removed.
The closest current entry point is `aplt.subplot_basis_image`, which renders
the mapper's pixelisation overlaid on the image:

```python
aplt.subplot_basis_image(
    inversion=fit.inversion,
    output_path=str(PLOT_DIR), output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

The mesh-triangulation and regularisation-neighbour graphs no longer have
direct plot helpers; build them with NumPy and `aplt.plot_grid` if needed.

## Branch — double Einstein ring / multi-plane pixelisations

For systems with two source planes (each pixelised independently), the
`pixelization_index` argument indexes into the planes. See
`autolens_workspace:scripts/guides/plot/advanced/plotters_double_einstein_ring.py`.

## Quality checks

A healthy pixelised reconstruction:

- Source-plane reconstruction shows recognisable structure (clumps, arms), not white
  noise.
- Reconstruction error / signal-to-noise is positive across the source.
- Regularisation weights smoothly decrease toward the edges (for adaptive variants).
- The reconstructed image-plane model matches the data with featureless residuals
  (see [`al_plot_fit_residuals`](./al_plot_fit_residuals.md)).

Pathological signs:

- Source-plane is a single bright pixel — the inversion has demagnified. Add image
  positions and refit.
- Reconstruction looks like the noise map — regularisation is too low. Raise the
  regularisation coefficient range.
- Source is unphysically extended beyond the caustic — mass model is wrong; the
  positions penalty isn't holding it in.

Connect to [`al_debug_fit_failure`](./al_debug_fit_failure.md) when any of these
appear.

## Combine

- [`al_plot_tracer`](./al_plot_tracer.md) — overlay caustics on the source-plane
  reconstruction to confirm signal is inside the caustic.
- [`al_chain_searches`](./al_chain_searches.md) — the canonical chain for moving from
  a parametric source fit to a pixelised one.
- [`al_run_slam_pipeline`](./al_run_slam_pipeline.md) — automated pipeline that
  handles the parametric → pixelised transition.

## Further reading

- **Student / new to lensing** — [HowToLens: Reconstructing source light via
  least-squares](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_3_inversions.ipynb):
  the inversion at its heart — least-squares solution for source-plane pixel
  intensities. Chapter 4 as a whole covers mappers, regularization, adaptive grids.
- **General reference** — [RTD: Features overview](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  the pixelization feature sits here alongside MGE / interferometry / shapelets —
  links into deeper docs.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/features/pixelization/modeling.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/pixelization/modeling.py):
  rectangular-mesh + constant-regularization pixelization model — production
  pattern for extended-arc sources.
