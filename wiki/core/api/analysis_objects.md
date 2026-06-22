---
title: Analysis objects — AnalysisImaging, AnalysisInterferometer, AnalysisPoint
sources:
  - project: PyAutoLens
    paths:
      - autolens/imaging/model/analysis.py
      - autolens/interferometer/model/analysis.py
      - autolens/point/model/analysis.py
    pinned_commit: ae4a27afc0fe7ad712777807d4269759c1a2b6ed
  - project: PyAutoFit
    paths:
      - autofit/graphical/declarative/factor/analysis.py
      - autofit/graphical/declarative/collection.py
      - autofit/graphical/declarative/abstract.py
    pinned_commit: ce2baa2b6611de99922e04d44b272de1be3ceb8e
last_updated: 2026-06-22
content_sha256: 8c415d521a9a0e4789eeb9ef69cb9bc9371ae5e7131e4035506554ed443d765b
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

## Multi-dataset analysis — the factor graph

To fit one lens to several datasets at once (multi-wavelength imaging, joint
imaging + interferometer, multi-epoch), you do **not** combine the `Analysis` objects
directly. You build one `Analysis` per dataset, wrap each in an `af.AnalysisFactor`
that pairs it with a model, and combine the factors into an `af.FactorGraphModel`. The
factor graph's log-likelihood is the sum of the per-factor log-likelihoods, and the
graph machinery decides which priors are shared across datasets and which are free.

```python
import autofit as af

# 1. One analysis per dataset.
analysis_list = [al.AnalysisImaging(dataset=dataset) for dataset in dataset_list]

# 2. Wrap each analysis in a factor, pairing it with a (copy of the) model.
analysis_factor_list = [
    af.AnalysisFactor(prior_model=model.copy(), analysis=analysis)
    for analysis in analysis_list
]

# 3. Combine the factors into one global model.
factor_graph = af.FactorGraphModel(*analysis_factor_list)

# 4. Fit. The model passed to the search is the graph's global prior model; the
#    analysis is the graph itself. The result is one Result per factor.
result_list = search.fit(
    model=factor_graph.global_prior_model, analysis=factor_graph
)
```

- **`af.AnalysisFactor(prior_model, analysis, optimiser=None, name=None)`** — pairs one
  analysis with the model whose log-likelihood it evaluates
  (`PyAutoFit:autofit/graphical/declarative/factor/analysis.py`).
- **`af.FactorGraphModel(*model_factors, name=None, ...)`** — collects the factors; its
  `global_prior_model` property is the `Collection` (one model per factor) you hand to
  the search (`PyAutoFit:autofit/graphical/declarative/collection.py`,
  `PyAutoFit:autofit/graphical/declarative/abstract.py`).
- **`search.fit(...)`** returns a `CombinedResult` — iterable and indexable, one `Result`
  per factor in order (`PyAutoFit:autofit/non_linear/combined_result.py`).

**Shared vs. per-dataset parameters.** With a bare `model.copy()` per factor and no prior
overrides, every prior is *identified* across factors — the graph deduplicates them, so
the global model has the same dimensionality as the single-dataset model (everything
shared). To free a parameter per dataset (e.g. a per-band source `intensity`, or a
per-dataset astrometric offset), override that prior on the `model.copy()` *before*
wrapping it in its `AnalysisFactor`. See `autolens_workspace:scripts/multi/start_here.py`
for the canonical walkthrough, and [`../concepts/multi_wavelength.md`](../concepts/multi_wavelength.md)
for the shared-vs-free design.

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
