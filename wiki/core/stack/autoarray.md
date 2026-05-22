---
title: PyAutoArray (autoarray)
sources:
  - project: PyAutoArray
    paths:
      - autoarray/structures/
      - autoarray/dataset/
      - autoarray/mask/
      - autoarray/operators/
      - README.rst
    pinned_commit: main
last_updated: 2026-05-22
---

# PyAutoArray — arrays, grids, masks, datasets

Project: [`PyAutoArray`](https://github.com/Jammy2211/PyAutoArray). Import:
`autoarray`. PyAutoLens re-exports the user-facing classes through `autolens`, so you
mostly see them as `al.Array2D`, `al.Grid2D`, `al.Mask2D`, `al.Imaging`, etc.

PyAutoArray is the data + geometry layer. It defines the array containers PyAutoLens
analyses use, the masks that select which pixels are fitted, the grids on which
light/mass profiles are evaluated, and the dataset wrappers that hold imaging and
visibility data along with their PSFs and noise maps.

## Headline classes

| Class | Purpose | Source |
|---|---|---|
| `Array2D` | 2D array with native (y, x) layout + slim (1D over mask) layout | `autoarray/structures/arrays/uniform_2d.py` |
| `Grid2D` | 2D grid of (y, x) coordinates with over-sampling support | `autoarray/structures/grids/uniform_2d.py` |
| `Mask2D` | Boolean 2D mask, with `.circular`, `.elliptical`, `.from_fits` constructors | `autoarray/mask/mask_2d.py` |
| `Imaging` | Image + noise map + PSF dataset wrapper | `autoarray/dataset/imaging/dataset.py` |
| `Interferometer` | Visibilities + noise map + uv-coverage wrapper | `autoarray/dataset/interferometer/dataset.py` |
| `Kernel2D` | PSF / convolution kernel | `autoarray/structures/arrays/kernel_2d.py` |

## Slim vs. native

Arrays have two layouts:

- **`native`** — `(y_pixels, x_pixels)` 2D shape. This is what you'd plot.
- **`slim`** — 1D, only the pixels inside a mask. Most internal computation runs on
  the slim layout for speed.

```python
arr.native   # 2D for inspection / plotting
arr.slim     # 1D, masked subset, for fast math
```

The conversion is handled by the array's `Mask2D`. See
[`concepts/grids_and_masks`](../concepts/grids_and_masks.md).

## Over-sampling

For pixels near the centre of a steep light profile, single-point evaluation aliases
the analytic intensity. PyAutoArray supports adaptive sub-grid integration:

```python
import autolens as al

grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.05)
over = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid, sub_size_list=[8, 4, 1], radial_list=[0.3, 0.6], centre_list=[(0.0, 0.0)],
)
grid = grid.apply_over_sampling(over_sample_size=over)
```

Sub-grids are denser where it matters and coarser everywhere else. Source:
`PyAutoArray:autoarray/operators/over_sampling.py`.

## Inversions

Pixelised source reconstruction lives in `autoarray/inversion/`. The classes you
touch via PyAutoLens are `al.Pixelization`, `al.mesh.*`, `al.reg.*` — these wrap
the lower-level mesh/regularisation/mapper machinery in
`autoarray/inversion/mesh/` etc.

See [`concepts/inversions_and_pixelizations`](../concepts/inversions_and_pixelizations.md).

## Configuration

`autoarray/config/` ships `general.yaml`, `notation.yaml`, `output.yaml`. The
notation controls plot labels (e.g. arcseconds vs. radians); see
[`api/configuration`](../api/configuration.md).

## Dependencies

`astropy`, `decorator`, `dill`, `matplotlib`, `scipy`, `scikit-image`, `scikit-learn`,
plus optional `numba` for JIT-acceleration of geometry kernels and optional `pynufft`
for visibility transforms.

## See also

- [`api/datasets`](../api/datasets.md) — `Imaging`, `Interferometer`, `PointDataset`.
- [`concepts/grids_and_masks`](../concepts/grids_and_masks.md) — what a grid and mask
  actually do under the hood.
- [`api/plotting`](../api/plotting.md) — `aplt` plotters operate on these arrays.
