---
title: Grids and masks
sources:
  - project: PyAutoArray
    paths:
      - autoarray/structures/grids/uniform_2d.py
      - autoarray/mask/mask_2d.py
      - autoarray/operators/over_sampling/over_sample_util.py
    pinned_commit: main
last_updated: 2026-07-09
---

# Grids and masks

PyAutoArray's `Grid2D` and `Mask2D` are the geometric primitives every lensing
analysis builds on. They control *where* on the image plane the model is evaluated
and *which* pixels contribute to the likelihood.

Sources: `PyAutoArray:autoarray/structures/grids/uniform_2d.py` and
`PyAutoArray:autoarray/mask/mask_2d.py`.

## Grid2D

A 2D grid of (y, x) coordinates in arcseconds. Profiles evaluate on it; the tracer
ray-traces it.

```python
import autolens as al
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.05)
```

- **`shape_native`** — `(y_pixels, x_pixels)`. The 2D layout.
- **`pixel_scales`** — arcsec/pixel. Either a scalar (square pixels) or `(dy, dx)`.

Grids live in **arcsecond coordinates centred at (0, 0)**. The bottom-left pixel of
a `(100, 100)` grid at `0.05"/pix` is at `(-2.475, -2.475)`; the centre pixel is at
`(0, 0)`.

The grid behaves both as a 2D image (`.native`, shape `(y, x, 2)` last dim being
the y/x coordinate) and as a flat list of coordinates (`.slim`, shape `(N, 2)`
where `N` is the number of unmasked pixels — see Mask2D below).

## Mask2D

A boolean array indicating which pixels are excluded from the fit. The convention is
**`True` means excluded**.

```python
mask = al.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=2.5,
)
```

Constructors:

- `Mask2D.circular(radius, centre=(0.0, 0.0))` — disc.
- `Mask2D.elliptical(major_axis, axis_ratio, angle, centre)`.
- `Mask2D.annular(inner_radius, outer_radius)`.
- `Mask2D.from_fits(file_path, pixel_scales, invert=False)` — load from disk.

Applied to a dataset:

```python
dataset = dataset.apply_mask(mask=mask)
```

After masking, the dataset internally tracks slim vs. native:

- `dataset.data.slim` — flat list of unmasked pixel values, length = unmasked count.
- `dataset.data.native` — 2D shape, masked pixels filled with zeros (for display).

Likelihood computation always runs on `slim` — it's the only data the fit sees.

## Over-sampling

A pixel containing the centre of a steep light profile (Sersic `n=4`, small
effective radius) under-samples the intensity if you evaluate at the pixel centre
only. Adaptive sub-grid integration evaluates each pixel on a finer NxN sub-grid and
averages.

```python
over = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 1],          # 4x4 inside r=0.3, 2x2 inside r=0.6, 1x1 outside
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over)
```

`over_sample_size_lp` controls light-profile over-sampling. Mass-profile evaluation
uses a separate `over_sample_size_pixelization` for inversions.

Source: `PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py`.

When to over-sample more aggressively:

- High sersic index sources very close to the lens centre.
- Pixelised sources with fine source-plane meshes.

When *not* to:

- The fit gets dramatically slower with higher sub-sizes — `[8, 4, 2, 1]` already
  costs ~4× the per-pixel evaluation of `[1]`. Only apply where it's needed.

## Common mistakes

- **Mask too tight.** If the mask radius is smaller than the lensed arc, the fit
  ignores most of the signal and converges to a degenerate solution.
- **Mask too loose.** Empty sky just slows the fit without adding info.
- **Forgetting over-sampling.** Steep profiles get under-evaluated and fits prefer
  smoother profiles than the data actually supports.
- **Wrong pixel scale.** A factor-of-two error in `pixel_scales` silently rescales
  every angular quantity in the fit.

## See also

- [`../api/datasets`](../api/datasets.md) — `Imaging`, `Interferometer`, what they
  hold.
- [`../../../skills/al_prepare_imaging_data.md`](../../../skills/al_prepare_imaging_data.md) —
  the standard load + mask + over-sample recipe.
- [`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md) — masking
  out contaminating galaxies by inflating their noise (`apply_noise_scaling`).
- [`tracer`](./tracer.md) — the tracer evaluates on whatever grid you hand it.
