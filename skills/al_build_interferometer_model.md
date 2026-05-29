---
name: al_build_interferometer_model
description: Compose a strong-lens model for visibility-plane (ALMA / JVLA / interferometer) data. Same galaxy + profile composition as the imaging variant, but wraps the dataset in `al.AnalysisInterferometer`. Writes a runnable Python script in ./work/. Pairs with `al_run_search` (executes the fit) and uses the same light + mass profile catalogue as imaging.
---

# Composing an interferometer lens model

Interferometers (ALMA, JVLA, NOEMA, etc.) record visibilities in the (u, v) plane
rather than images in the (y, x) plane. PyAutoLens fits these directly without first
imaging the data, so the *model* is identical to the imaging case (galaxies, light
profiles, mass profiles) but the *analysis* is `AnalysisInterferometer` and the
likelihood is computed in visibility space.

Canonical example: `autolens_workspace:scripts/interferometer/modeling.py`. This
skill produces the equivalent for the user's dataset.

## Ask

- *"Do you have your visibilities already in PyAutoArray-compatible form, or do you
  need CASA reduction first?"* — if the latter, point at
  `autolens_workspace:scripts/interferometer/casa_reduction.py` before this skill.
- *"What's the lens system?"* — same questions as `al_build_imaging_model` (galaxy
  count, light vs mass-only, source parameterisation, redshifts).
- *"How dense is your uv coverage?"* — short-baseline / sparse coverage usually wants
  a pixelised source over a parametric one.

## Branch — minimal SIE lens + Sersic source

Save to `work/build_interferometer_model.py`:

```python
# work/build_interferometer_model.py
from autoconf import jax_wrapper
from pathlib import Path
import autofit as af
import autolens as al

dataset_path = Path("dataset/interferometer/<your_lens>")

real_space_mask = al.Mask2D.circular(
    shape_native=(400, 400),
    pixel_scales=0.025,
    radius=3.0,
)

dataset = al.Interferometer.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    uv_wavelengths_path=dataset_path / "uv_wavelengths.fits",
    real_space_mask=real_space_mask,
)

# Identical model composition to the imaging case.
lens = af.Model(
    al.Galaxy,
    redshift=0.5,
    mass=af.Model(al.mp.Isothermal),
    shear=af.Model(al.mp.ExternalShear),
)
source = af.Model(
    al.Galaxy,
    redshift=1.0,
    bulge=af.Model(al.lp.SersicCore),
)
model = af.Collection(galaxies=af.Collection(lens=lens, source=source))

# Difference from imaging: AnalysisInterferometer, plus a transformer class that
# converts the model image to visibilities via NUFFT.
analysis = al.AnalysisInterferometer(
    dataset=dataset,
    settings=al.Settings(),
)
```

Source citations:
- `PyAutoArray:autoarray/dataset/interferometer/dataset.py` — `Interferometer.from_fits`.
- `PyAutoLens:autolens/interferometer/model/analysis.py` — `AnalysisInterferometer`.
- `PyAutoArray:autoarray/operators/transformer.py` — NUFFT transform from real-space
  image to visibilities.

Wiki:
- [`wiki/core/api/datasets.md`](../wiki/core/api/datasets.md) — `Imaging` vs `Interferometer` vs
  `PointDataset` contrast.
- [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md) —
  why pixelised sources are common for interferometer fits.

## Branch — pixelised source on visibility data

Most ALMA / JVLA lens fits use a pixelised source. The model wiring follows the same
pattern as imaging, but the inversion is computed in real-space and then FFT'd to
visibilities. See `autolens_workspace:scripts/interferometer/features/pixelization/`
for a complete example.

## Combine

- [`al_run_search`](./al_run_search.md) — execute the fit.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) — pixelised
  source diagnostics.
- [`al_load_results`](./al_load_results.md) — load a completed interferometer fit.

## Further reading

- **General reference** — [RTD: Features overview](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  tour of advanced features including interferometry, where the visibility-plane fit
  fits alongside MGE / pixelization / multi-wavelength capabilities.
- **Experienced PyAutoLens user** — [workspace/lens: interferometer/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/interferometer/start_here.py):
  canonical strong-lens fit of radio/mm interferometer data — NUFFT-based forward
  model, scaling to millions of visibilities.
