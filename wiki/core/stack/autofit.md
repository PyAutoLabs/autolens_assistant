---
title: PyAutoFit (autofit)
sources:
  - project: PyAutoFit
    paths:
      - autofit/mapper/
      - autofit/non_linear/
      - autofit/aggregator/
      - autofit/database/
      - README.rst
    pinned_commit: main
last_updated: 2026-05-22
---

# PyAutoFit — model composition + non-linear search

Project: [`PyAutoFit`](https://github.com/rhayes777/PyAutoFit). Import: `autofit`,
aliased to `af` everywhere.

PyAutoFit is the *probabilistic modelling and inference* layer. PyAutoLens uses it
for everything that isn't lensing-specific: composing a parametric model out of
profiles + galaxies, running a non-linear search to fit it, and reading the resulting
posterior.

PyAutoFit is **non-lensing-aware**. The model could just as easily describe a chemical
reaction network or a regression. PyAutoLens supplies the lensing-specific likelihood
via its `AnalysisImaging` / `AnalysisInterferometer` classes; PyAutoFit handles the
inference around it.

## Model composition

The two headline classes:

- **`af.Model`** — a single class wrapped in a model-aware shell. `af.Model(al.lp.Sersic)`
  is "a Sersic profile whose parameters are free during the fit". Each parameter gets
  a default prior from the YAML config; you can override per-instance with
  `model.intensity = af.UniformPrior(...)`.
- **`af.Collection`** — an ordered collection of models. `af.Collection(lens=lens_model,
  source=source_model)` groups them with names you can address.

A full lens model is typically:

```python
model = af.Collection(galaxies=af.Collection(lens=lens, source=source))
```

Source: `PyAutoFit:autofit/mapper/prior_model/prior_model.py` and `.../collection.py`.

## Non-linear searches

PyAutoFit ships a catalogue of samplers, all callable via the same `search.fit(model=,
analysis=)` interface. See [`api/searches`](../api/searches.md) for the full table.
Headline picks:

- **`af.Nautilus`** — nested sampling, the default for lensing. Robust to
  multimodality, fast on modern CPUs.
- **`af.DynestyStatic` / `af.DynestyDynamic`** — alternative nested samplers.
- **`af.Emcee`** — ensemble MCMC, for known-unimodal posterior characterisation.
- **`af.Zeus`** — ensemble slice sampling.
- **`af.UltraNest`** — reactive nested sampling, for high-dimensional posteriors.
- **`af.PySwarms`** — particle swarm optimisation (MLE only).
- **`af.BFGS`** / **`af.Drawer`** — gradient descent / random draws (debug).

Sources: `PyAutoFit:autofit/non_linear/search/`.

## Samples and aggregator

After a fit, PyAutoFit produces a `Samples` object holding every accepted sample,
and writes a CSV + JSON manifest to disk. The aggregator
(`PyAutoFit:autofit/aggregator/`) iterates over many fits without loading them all
into memory at once — useful when you've run hundreds of fits and want summary
statistics.

For bulk querying of large numbers of fits, the SQLAlchemy-backed database in
`autofit/database/` exists. See [`concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md).

## Configuration

`autofit/config/` ships `general.yaml`, `logging.yaml`, `notation.yaml`,
`output.yaml`, plus default prior YAMLs under `priors/` and plot settings under
`visualize/`. The prior YAMLs are how PyAutoFit knows that
`al.lp.Sersic.effective_radius` should default to `UniformPrior(lower_limit=0.0,
upper_limit=8.0)` (or whatever the workspace config says).

See [`api/configuration`](../api/configuration.md).

## Dependencies

`autoconf`, `array_api_compat`, plus a deep scientific stack — `anesthetic`, `corner`,
`dynesty`, `emcee`, `pyswarms`, `h5py`, `SQLAlchemy`, `scipy`, `networkx`, `pyvis`,
`psutil`, `xxhash`. Optional: `astropy`, `getdist`, `Nautilus`, `UltraNest`, `Zeus`.

The `Nautilus` and `UltraNest` deps are optional because they're heavier; install
them when you need them.

## See also

- [`api/searches`](../api/searches.md) — full search catalogue with knobs.
- [`concepts/non_linear_search`](../concepts/non_linear_search.md) — what each
  sampler does conceptually.
- [`concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md) — using
  the `Samples` API.
- [`api/analysis_objects`](../api/analysis_objects.md) — the lensing-side counterpart
  to PyAutoFit's search (the `Analysis` is what provides the log-likelihood).
