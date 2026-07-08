---
title: Non-linear search
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/abstract_search.py
      - autofit/non_linear/search/nest/
      - autofit/non_linear/search/mcmc/
      - autofit/non_linear/search/mle/
    pinned_commit: main
last_updated: 2026-05-22
---

# Non-linear search

A non-linear search is the algorithm that explores parameter space to fit a model
to data. PyAutoFit ships a catalogue of them; you pick one, configure its knobs,
and hand it to `search.fit(model=model, analysis=analysis)`.

The full catalogue is in [`../api/searches`](../api/searches.md). This page is the
conceptual map.

Source: `PyAutoFit:autofit/non_linear/search/`.

## Families

PyAutoFit groups searches into three families.

### Nested sampling

Estimates the Bayesian evidence by sweeping a shrinking iso-likelihood surface.
Naturally handles multi-modal posteriors. The right default for lensing.

- **Nautilus** — fast, modern, well-tuned. The workspace's default.
- **DynestyStatic / DynestyDynamic** — alternative, well-tested.

(UltraNest is not currently exposed as a public `autofit` search class — see
[`../api/searches.md`](../api/searches.md).)

### MCMC

Walks chains through parameter space, sampling proportional to likelihood × prior.
Excellent for posterior characterisation of a known unimodal mode; poor at finding
modes from scratch.

- **Emcee** — affine-invariant ensemble sampler.
- **Zeus** — ensemble slice sampler; handles correlations better than Emcee.

### Maximum-likelihood / optimisation

Finds the single max-likelihood point. No posterior; no errors. Used for
exploration, gradient-based refinement, or producing a starting point for an MCMC
chain.

- **BFGS / LBFGS** — gradient descent (LBFGS = limited-memory variant).
- **Drawer** — random prior draws. Debugging only.

(PySwarms is not currently exposed as a public `autofit` search class.)

## When to use which

| Situation | Pick |
|---|---|
| First-fit of an unknown lens | `Nautilus` |
| Production posterior, multi-modal expected | `Nautilus` (n_live=300+) |
| Posterior refinement around a known mode | `Emcee` or `Zeus` |
| Bayesian evidence comparison | `Nautilus` or `DynestyStatic` |
| Very high-dim model (>50 free parameters) | `Nautilus` (n_live=400+) |
| Fast exploration / sanity check | `BFGS` or `LBFGS` |
| Confirming the prior gives reasonable models | `Drawer` |

## Prior chaining

Search results can be fed back as priors for subsequent searches:

```python
result_1 = search_1.fit(model=model_1, analysis=analysis)
lens_2 = af.Model(al.Galaxy, mass=result_1.model.galaxies.lens.mass)  # inherit
```

`result.model` returns a new `af.Model` whose priors are the previous search's
posterior (Gaussian around the MAP, with widths from the marginals). `result.instance`
returns the values *fixed* — no priors, no free parameters.

This is the foundation of [`../../../skills/al_chain_searches.md`](../../../skills/al_chain_searches.md)
and of the SLaM pipeline.

## Knobs every search has

- **`path_prefix`** — output folder prefix.
- **`name`** — search identifier; combined with `path_prefix` + a hash of the model
  to produce a unique output directory.
- **`unique_tag`** — extra identifier to distinguish otherwise-identical runs.
- **`number_of_cores`** — parallel likelihood evaluations.
- **`iterations_per_update`** — how often the search writes intermediate samples to
  disk.

Per-search knobs (`n_live` for nested, `nwalkers` / `nsteps` for MCMC) are in the
search-specific entries of [`../api/searches`](../api/searches.md).

## Output

Every search produces, in
`output/<path_prefix>/<name>/<unique_id>/`:

- `files/samples.csv` — every accepted sample.
- `files/samples_summary.json` — MAP + 1-sigma bounds.
- `files/model.json` — fitted model definition.
- `files/tracer.json` — MAP `Tracer` (PyAutoLens-specific).
- `image/fit.fits`, `image/tracer.fits` — diagnostic images.
- `model.info`, `model.results` — human-readable summaries.
- `search.summary` — search-specific log.

[`../../../skills/al_load_results.md`](../../../skills/al_load_results.md) walks loading
each piece.

## See also

- [`../api/searches`](../api/searches.md) — full catalogue with knobs.
- [`samples_and_posteriors`](./samples_and_posteriors.md) — what to do with the
  posterior.
- [`slam_pipeline`](./slam_pipeline.md) — chained-search pipeline.

## Further reading

The canonical papers behind each algorithm family live in the literature
sub-wiki:

- [`wiki/literature/concepts/nested-sampling`](../../literature/concepts/nested-sampling.md)
  — Skilling, Dynesty, Nautilus.
- [`wiki/literature/concepts/mcmc-sampling`](../../literature/concepts/mcmc-sampling.md)
  — Emcee, Zeus, NUTS.
- [`wiki/literature/sources/bayesian-inference-methods`](../../literature/sources/bayesian-inference-methods.md)
  — per-paper bibliography.
