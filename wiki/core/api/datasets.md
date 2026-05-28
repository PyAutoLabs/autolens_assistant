---
title: Datasets — Imaging, Interferometer, PointDataset
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/imaging/dataset.py
      - autoarray/dataset/interferometer/dataset.py
    pinned_commit: main
  - project: PyAutoLens
    paths:
      - autolens/point/dataset.py
    pinned_commit: main
last_updated: 2026-05-22
---

# Datasets

Three dataset flavours: CCD imaging, visibility-plane interferometer data, and
point-source datasets (positions + time delays). Each pairs with a matching
`Analysis*` object and a matching plotter.

## al.Imaging

CCD imaging. Holds the image, per-pixel noise map, and PSF.

```python
dataset = al.Imaging.from_fits(
    data_path=...,
    noise_map_path=...,
    psf_path=...,
    pixel_scales=0.05,
)
```

Methods of interest:

- `apply_mask(mask: Mask2D)` — restricts the fit to masked-in pixels.
- `apply_noise_scaling(mask: Mask2D)` — inflates noise inside `mask` (for
  contaminating-galaxy removal).
- `apply_over_sampling(over_sample_size_lp=..., over_sample_size_pixelization=...)` —
  sub-grid integration for steep profiles.
- `output_to_fits(data_path, noise_map_path, psf_path, overwrite)` — write back to
  disk after simulation.

Attributes:

- `dataset.data` — `Array2D` of image counts.
- `dataset.noise_map` — `Array2D` of per-pixel RMS.
- `dataset.psf` — `Convolver` of the point-spread function (built with
  `al.Convolver.from_gaussian(...)` or `al.Convolver.from_fits(...)`).
- `dataset.grid` — masked `Grid2D` of (y, x) coordinates.

Source: `PyAutoArray:autoarray/dataset/imaging/dataset.py`.

Skill: [`../../../skills/al_prepare_imaging_data.md`](../../../skills/al_prepare_imaging_data.md).

## al.Interferometer

Visibility-plane data. Holds the visibilities, their noise map, and the uv
coordinates of each baseline.

```python
real_space_mask = al.Mask2D.circular(shape_native=(400, 400), pixel_scales=0.025, radius=3.0)
dataset = al.Interferometer.from_fits(
    data_path=...,
    noise_map_path=...,
    uv_wavelengths_path=...,
    real_space_mask=real_space_mask,
)
```

The `real_space_mask` defines where in real-space (image-plane) the model is
evaluated before being FFT'd to visibilities.

Attributes:

- `dataset.data` — complex visibility values.
- `dataset.noise_map` — RMS on each visibility.
- `dataset.uv_wavelengths` — (u, v) coordinates of each baseline, in wavelengths.
- `dataset.real_space_mask` — image-plane mask.
- `dataset.dirty_image` — convenience: real-space inverse-FFT of the visibilities,
  for visualisation only.

Source: `PyAutoArray:autoarray/dataset/interferometer/dataset.py`.

## al.PointDataset

Point-source lensing — image positions of a multiply-imaged quasar / AGN,
optionally with time delays and image-flux magnifications.

```python
positions = al.Grid2DIrregular(values=[(1.0, 1.0), (-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0)])
position_noise = al.ArrayIrregular(values=[0.05, 0.05, 0.05, 0.05])
dataset = al.PointDataset(
    name="quasar_J1234",
    positions=positions,
    positions_noise_map=position_noise,
    fluxes=...,
    fluxes_noise_map=...,
    time_delays=...,
    time_delays_noise_map=...,
)
```

Source: `PyAutoLens:autolens/point/dataset.py`.

Used by `AnalysisPoint` to constrain mass models via image positions, time delays,
and flux ratios — common for time-delay cosmography (H₀ measurements).

## Picking a dataset type

| Telescope / data | Dataset |
|---|---|
| HST, JWST, Euclid CCD imaging | `Imaging` |
| Ground-based CCD imaging | `Imaging` |
| ALMA, JVLA, NOEMA visibilities | `Interferometer` |
| Multi-wavelength CCD | one `Imaging` per band; multi-analysis (see PyAutoLens `multi/` examples) |
| Quasar / AGN image positions | `PointDataset` |
| Mixed (point + extended) | both, combined in one `Analysis` |

## See also

- [`../concepts/grids_and_masks`](../concepts/grids_and_masks.md) — geometry behind
  every dataset.
- [`analysis_objects`](./analysis_objects.md) — paired `Analysis*` classes.
- [`../../../skills/al_prepare_imaging_data.md`](../../../skills/al_prepare_imaging_data.md).
