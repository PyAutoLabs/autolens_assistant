---
name: al_configure_search
description: Pick and tune a non-linear search for a lens-modelling fit. Defaults to Nautilus (nested sampling, the recommended choice); covers Dynesty, Emcee, Zeus, and the gradient/optimizer options for completeness. Sets sampler-specific knobs (live points, walkers, tolerance) and the output `path_prefix` / `name` that determine where results land. Pairs with `al_run_search`, which actually calls `search.fit`.
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
  (Nautilus / Dynesty) over MCMC.
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
    iterations_per_full_update=2500,
    number_of_cores=4,    # parallel likelihood evaluations
)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/nautilus/`.

Knobs to know:
- `n_live` — more = more accurate posterior, slower. Start at 200; go to 400+ only if
  the posterior looks multi-modal or thin.
- `number_of_cores` — set to your CPU core count for parallel likelihood eval.
- `iterations_per_full_update` / `iterations_per_quick_update` — how often the search
  writes full output (samples, visualisation) vs quick intermediate updates to disk.
  **Actively choose `iterations_per_quick_update` so the user always has quick access to
  result inspection** — don't just take the default. Judge it against the likelihood cost so
  the first on-the-fly `fit.png` / `samples` lands within a few minutes and refreshes
  regularly, but not so often that per-update visualisation overhead eats into throughput.
  Rules of thumb: ~500–1000 is a good interactive default; **lower it for a slow/expensive
  likelihood** (large MGE, pixelised source, GPU-batched fit, high `n_live`) so an inspection
  point still appears early; only **raise it** (≈2500–5000) when the likelihood is very fast
  and frequent updates would measurably dominate runtime. A common failure is leaving it high
  on a heavy fit, so the run shows *nothing* to inspect for an hour — avoid that. On HPC/batch
  runs the same value governs what a `sync pull` surfaces, so pick it before submitting.

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

Source: `PyAutoFit:autofit/non_linear/search/nest/dynesty/`.

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

Source: `PyAutoFit:autofit/non_linear/search/mcmc/emcee/`.

## Branch — Other searches

Zeus (ensemble slice MCMC), DynestyDynamic (dynamic nested sampling), BFGS / LBFGS
(gradient descent for MLE), Drawer (random prior draws — debugging only). See
[`wiki/core/api/searches.md`](../wiki/core/api/searches.md) for the comparison table.

## Branch — Live visual updates

When configuring an **interactive production fit** (foreground script or notebook), ask once:
*watch the fit update live?* The quick-update image (`fit.png`) is **always written to disk**
every `iterations_per_quick_update` iterations regardless; `live_visual_update=True` (default
`False`) additionally pushes it to a live display surface:

- **foreground Python script** — a matplotlib viewer opens and refreshes with each quick
  update;
- **Jupyter / Colab** — the cell that ran `search.fit(...)` refreshes one image in place;
- **HPC, headless, background, or unattended runs** — keep it `False` (nothing to attach to;
  HPC mode disables it in config).

```python
search = af.Nautilus(
    ...,
    iterations_per_quick_update=1000,  # quick-update (and live refresh) cadence
    live_visual_update=True,           # script: matplotlib viewer; notebook: in-place cell
)
```

Both are shared search options (accepted by every search via the common base class), with
config fallbacks in `config/general.yaml` `updates:`. Don't re-ask on later runs — the
choice is recorded in the search configuration.

Source: `PyAutoFit:autofit/non_linear/search/abstract_search.py`.

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
