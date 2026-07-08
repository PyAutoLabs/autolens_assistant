---
name: al_configure_search
description: Pick and tune a non-linear search for a lens-modelling fit. Defaults to Nautilus (nested sampling, the recommended choice); covers Dynesty, Emcee, Zeus, UltraNest, and the gradient/swarm options for completeness. Sets sampler-specific knobs (live points, walkers, tolerance) and the output `path_prefix` / `name` that determine where results land. Pairs with `al_run_search`, which actually calls `search.fit`.
---

# Configuring a non-linear search

The non-linear search is *how* PyAutoFit explores the model's parameter space. PyAutoLens
exposes the same searches PyAutoFit ships, with Nautilus as the default. Picking the
right one — and tuning its knobs sensibly — is often the difference between a fit that
converges in hours and one that doesn't converge at all.

For the catalogue of available searches and when to use each,
[`wiki/core/api/searches.md`](../wiki/core/api/searches.md). For the *concept* of a non-linear
search (what nested sampling does, what MCMC does, what gradient descent does),
[`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md).

## Ask

- *"How complex is the model?"* — number of free parameters and whether any are
  expected to be multi-modal. Multi-modality strongly favours nested sampling
  (Nautilus / Dynesty / UltraNest) over MCMC.
- *"How fast does the likelihood evaluate?"* — fast (<1s with JAX) → can afford more
  live points or walkers. Slow → tighten the search.
- *"Is this a first exploratory fit, or a final production run?"* — exploratory fits
  use fewer live points and looser tolerance to fail fast.
- *"Where should the output go?"* — `output/<dataset>/modeling/<name>/<hash>/` is the
  convention; the user chooses `<dataset>` and `<name>`.

## Branch — Nautilus (recommended default)

For most lens models — parametric, pixelised, simple, complex — Nautilus is the right
first pick. It handles multi-modal posteriors and is fast enough on modern CPUs.

```python
# scripts/configure_search.py
import autofit as af

search = af.Nautilus(
    path_prefix="imaging/<your_lens>",
    name="modeling_sie_sersic",
    unique_tag="<your_dataset>",
    n_live=200,           # 100 for exploration, 200 for production, 400+ for complex models
    iterations_per_update=2500,
    number_of_cores=4,    # parallel likelihood evaluations
)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/nautilus.py`.

Knobs to know:
- `n_live` — more = more accurate posterior, slower. Start at 200; go to 400+ only if
  the posterior looks multi-modal or thin.
- `number_of_cores` — set to your CPU core count for parallel likelihood eval.
- `iterations_per_update` — how often the search writes intermediate samples to disk.

## Branch — Dynesty

Use Dynesty for problems where you specifically want its dynamic sampling features
(e.g. focusing samples in the posterior tails for precise evidence estimation).

```python
search = af.DynestyStatic(
    path_prefix="...",
    name="...",
    nlive=150,
)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/dynesty.py`.

## Branch — Emcee (MCMC)

Use Emcee for posterior characterisation on a *known unimodal* posterior, when you
already have a tight initial guess (e.g. from a chained earlier fit). Don't use for
exploration of multi-modal spaces.

```python
search = af.Emcee(
    path_prefix="...",
    name="...",
    nwalkers=50,
    nsteps=10000,
)
```

Source: `PyAutoFit:autofit/non_linear/search/mcmc/emcee.py`.

## Branch — Other searches

Zeus (ensemble slice), UltraNest (nested sampling alternative), PySwarms (particle swarm),
BFGS (gradient descent for MLE), Drawer (random prior draws — debugging only). See
[`wiki/core/api/searches.md`](../wiki/core/api/searches.md) for the comparison table.

## Output folder layout

After `search.fit(...)` runs, results land at:

```
output/<path_prefix>/<name>/<unique_id>/
    files/
        tracer.json
        model.json
        samples.csv
        samples_summary.json
        search.json
    image/
        dataset.fits
        fit.fits
        ...
    model.info
    model.results
```

The `unique_id` hash is derived from the model + dataset + search settings, so identical
re-runs land in the same folder (and resume from where they stopped).

See [`al_load_results`](./al_load_results.md) for the inverse — loading what
`search.fit` writes.

## Combine

- [`al_run_search`](./al_run_search.md) — call `search.fit(model=..., analysis=...)`.
- [`al_chain_searches`](./al_chain_searches.md) — feed this search's result into a
  follow-up.
- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — when the search runs but the
  result is wrong.

## Further reading

- **Student / new to lensing** — [HowToLens (optional): Alternative non-linear search
  algorithms](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_optional/tutorial_searches.ipynb):
  the menu of searches beyond Nautilus (MCMC, optimizers) and how to think about
  tuning them.
- **General reference** — [RTD: Features overview](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  tour of advanced capabilities; search configuration interacts directly with most
  of them (especially pixelization, MGE, point-source).
- **Experienced PyAutoLens user** — [workspace/lens: guides/modeling/slam_start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/modeling/slam_start_here.py):
  the SLaM pipeline pre-configures sensible searches per stage — a reference for
  *which* knobs matter at *which* phase.
