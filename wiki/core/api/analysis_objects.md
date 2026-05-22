---
title: Analysis objects — AnalysisImaging, AnalysisInterferometer, AnalysisPoint
sources:
  - project: PyAutoLens
    paths:
      - autolens/imaging/model/analysis.py
      - autolens/interferometer/model/analysis.py
      - autolens/point/model/analysis.py
    pinned_commit: a91febcb1aa12797f9d5ece54c1cbbac528cd087
last_updated: 2026-05-22
---

# Analysis objects

An `Analysis` object holds a dataset and knows how to compute a log-likelihood for a
proposed model on it. It's the lensing-specific half of the PyAutoFit / PyAutoLens
interface: the search proposes parameter values, the analysis says how well they
fit.

Three flavours:

| Analysis | Dataset type | Source |
|---|---|---|
| `AnalysisImaging` | `Imaging` | `PyAutoLens:autolens/imaging/model/analysis.py` |
| `AnalysisInterferometer` | `Interferometer` | `PyAutoLens:autolens/interferometer/model/analysis.py` |
| `AnalysisPoint` | `PointDataset` | `PyAutoLens:autolens/point/model/analysis.py` |

## AnalysisImaging

```python
analysis = al.AnalysisImaging(dataset=dataset)
```

Options worth knowing:

```python
analysis = al.AnalysisImaging(
    dataset=dataset,
    positions_likelihood_list=[al.PositionsLH(positions=positions, threshold=0.5)],
    settings=al.Settings(use_positive_only_solver=False),
    adapt_images=earlier_result.adapt_images_from(),
    cosmology=al.cosmo.Planck15(),
)
```

- **`positions_likelihood_list`** — one or more `al.PositionsLH` penalties that
  discourage mass models whose observed image positions fail to trace back to a
  consistent source-plane location. Critical for pixelised-source fits.
- **`settings`** — inversion and solver knobs via `al.Settings(...)`, for example
  positive-only linear solves or mixed precision.
- **`adapt_images`** — adaptive images from an earlier result, used to drive
  adaptive meshes and regularisation.
- **`cosmology`** — override the default Planck 2018 cosmology if needed.

## AnalysisInterferometer

```python
analysis = al.AnalysisInterferometer(dataset=dataset)
```

Same option surface as `AnalysisImaging`, plus:

- **`transformer_class`** — NUFFT implementation for real-space → visibility
  transforms on the dataset side. The default is `al.TransformerNUFFT`; the
  legacy `al.TransformerNUFFTPyNUFFT` backend is still available when explicitly
  requested.

## AnalysisPoint

```python
analysis = al.AnalysisPoint(dataset=dataset, solver=al.PointSolver(...))
```

`AnalysisPoint` needs a `PointSolver` that maps source-plane positions back to image
positions — typically via a ray-tracing root-find on the lens equation.

## Multi-dataset analysis

For multi-wavelength or imaging + interferometer joint fits, combine analyses:

```python
analysis = analysis_imaging + analysis_interferometer
```

The combined analysis sums log-likelihoods. Each component can have its own model
(e.g. different source intensities per band) or share parameters across analyses
via the model composition.

See `autolens_workspace:scripts/multi/modeling.py`.

## Calling the analysis

You rarely call `analysis.log_likelihood_function(...)` yourself — the search does
it. But for debugging:

```python
instance = model.instance_from_vector(vector=[1.2, 0.0, ...])
loglike = analysis.log_likelihood_function(instance=instance)
```

This evaluates the model at a specific parameter vector and returns the
log-likelihood. Useful for prior-bound sanity checks.

## Visualisations during fit

Analyses also produce diagnostic plots that PyAutoFit writes to `output/.../image/`
at each update step (controlled by `iterations_per_update` on the search). The
plot routines live in the same packages as the analyses:

- `PyAutoLens:autolens/imaging/model/visualizer.py`
- `PyAutoLens:autolens/interferometer/model/visualizer.py`
- `PyAutoLens:autolens/point/model/visualizer.py`

## See also

- [`datasets`](./datasets.md) — what each analysis ingests.
- [`searches`](./searches.md) — the other half of `search.fit(model=, analysis=)`.
- [`../../../skills/al_build_imaging_model.md`](../../../skills/al_build_imaging_model.md) —
  wraps a dataset in `AnalysisImaging`.
- [`../../../skills/al_run_search.md`](../../../skills/al_run_search.md).
