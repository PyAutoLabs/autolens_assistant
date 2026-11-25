---
name: al_configure_search
description: Pick and tune a non-linear search for a lens-modelling fit. Defaults to Nautilus (nested sampling, the recommended choice); covers Dynesty, Emcee, Zeus, and the JAX multi-start gradient optimizers (MultiStartProdigy recommended when a fast MAP point estimate on a parametric source is wanted — not pixelized). Sets sampler-specific knobs (live points, walkers, tolerance) and the output `path_prefix` / `name` that determine where results land. Pairs with `al_run_search`, which actually calls `search.fit`.
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
    number_of_cores="auto",  # detected cores for numba, 1 for JAX (see "Compute setup")
)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/nautilus/`.

Knobs to know:
- `n_live` — more = more accurate posterior, slower. Start at 200; go to 400+ only if
  the posterior looks multi-modal or thin.
- `number_of_cores` — parallel likelihood evaluations (Python multiprocessing). `"auto"`
  gives a numba likelihood the detected cores and a JAX one 1 worker, because JAX never
  forks. It works on the search or on `af.SettingsSearch`. See "Compute setup" below.
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
  - **Set it the right way — directly on the search.** Pass `iterations_per_quick_update=…`
    straight to the search constructor, e.g. `af.Nautilus(..., iterations_per_quick_update=…)`
    (the idiom used throughout `autolens_workspace`, e.g. `point_source/modeling.py`,
    `weak/modeling.py`). Do **not** try to set it via `settings_search.search_dict[...] = …`:
    `SettingsSearch.search_dict` is a fixed-key property (`path_prefix`, `unique_tag`,
    `number_of_cores`, `session`, `use_jax_vmap`), so assigning a new key to it is a **silent
    no-op** — the value never reaches the search and the config default (often `1e99`, i.e.
    *never* quick-update) silently wins. To set it globally for a whole pipeline without
    editing every search, write it to the live config once after `conf.instance.push(...)`:
    `conf.instance["general"]["updates"]["iterations_per_quick_update"] = N`.

## Compute setup: auto unless…

The compute setup is how each likelihood is evaluated: numba or JAX, CPU or GPU, sparse
operator or dense, precision. It never changes the model or the posterior. On CPU, though,
a wrong choice costs days: a SLaM run misconfigured here spends >12 h in its first search.
By default, let the library choose:

```python
analysis = al.AnalysisImaging(dataset=dataset, setup="auto")
search = af.Nautilus(path_prefix=..., name=..., n_live=200, number_of_cores="auto")
```

When the fit starts, `setup="auto"` reads the dataset type, the source model (a mesh
selects its pixelized rule; no mesh selects MGE) and the hardware (A100 GPU or many-core
CPU). It picks the designated setup from `PyAutoArray:autoarray/config/setup_rules.yaml`,
attaches the operator that setup needs to the dataset (no `apply_sparse_operator*` call),
and prints `Setup:`, `Parallel:` and `Estimate:` lines, recorded in `files/setup.json` and
`files/parallel.json`. Each stage of a SLaM pipeline resolves its own setup, so SOURCE LP
(JAX) and the pixelized stages (numba sparse on CPU) need no separate settings. `setup` is
opt-in in this release: without it nothing changes, and the log says what auto would
choose. [`al_explain_setup`](./al_explain_setup.md) explains a choice; the workspace guide is
[`guides/advanced/auto_setup.py`](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/advanced/auto_setup.py).

Override when:

- **Debugging or reproducing a run.** Pin `setup="<setup_id>"` (e.g. `"numba_cpu_sparse_fp64"`)
  or set `PYAUTO_SETUP=<setup_id>`. `PYAUTO_SETUP=cpu|gpu` forces the hardware class, and
  `JAX_PLATFORMS=cpu` makes detection choose CPU.
- **Forcing numba or JAX**, or running a profiling or validation leg that must use one named setup.
- **Memory limits.** Cap `number_of_cores` at an integer when workers × peak memory would exceed the node.
- **Laptop or non-A100 GPU.** The rules were measured on ≥16-core nodes and A100s, so the
  banner says `extrapolated`. It is a sensible default; pin a setup if you measured a better one.
- **A sampler that needs JAX** (`MultiStartProdigy`, `BlackJAXNUTS`, `SMC`, `NSS`). Pass a
  JAX setup_id, e.g. `jax_cpu_dense_fp64`.

The explicit route is the override, and is the only route on releases without `setup=`:

| Fit type | CPU, explicit | A100 designation |
|---|---|---|
| Parametric source (MGE, Sersic) | `use_jax=True`, `number_of_cores` unset | `jax_gpu_dense_fp64` |
| Pixelized imaging | `dataset.apply_sparse_operator_cpu()`, `use_jax=False`, `number_of_cores=N` | `jax_gpu_dense_fp64` (sparse fallback) |
| Pixelized interferometer | numba sparse w-tilde (`numba_cpu_sparse_fp64_wtilde`) | `jax_gpu_sparse_fp64_wtilde` |

JAX is not GPU-only: it is the right CPU choice for parametric fits too. The imaging sparse
operator has a numba form (`apply_sparse_operator_cpu()`, with `use_jax=False`) and a JAX
form (`apply_sparse_operator()`). On a many-core CPU the numba form is 3–35× faster per node
for pixelized sources (`autolens_profiling:wiki/campaigns/imaging/rectangular/day_zero.md`).
Never mix numba operators with `use_jax=True`. For a single `al.FitImaging` outside a search,
`aa.Settings(lazy_sparse_operator="auto")` builds the numba operator on first use. Worked
example: `autolens_workspace:scripts/imaging/features/pixelization/cpu_fast_modeling.py`.

## Branch — MultiStartProdigy (JAX gradient optimizer, parametric sources)

When the user explicitly wants a **JAX gradient optimizer** — a fast maximum-a-posteriori (MAP)
*point* estimate rather than a full posterior — the recommended default is `MultiStartProdigy`.
Reach for it when the goal is speed to a best-fit model on a **parametric source** (MGE, Sersic)
and errors are not yet needed; otherwise keep Nautilus.

```python
import autofit as af

search = af.MultiStartProdigy(
    path_prefix="imaging/<your_lens>",
    name="modeling_sie_sersic",
    unique_tag="<your_dataset>",
    n_starts=50,   # broad starts run in parallel via jax.vmap
    n_steps=500,
)
```

Requires a JAX-traceable analysis: `al.AnalysisImaging(dataset=dataset, use_jax=True)` (the
parametric-source regime of "Compute setup" above).

Why Prodigy, and what the family is:

- The **multi-start** approach — launch many broad starts in parallel and keep the best — was
  introduced for strong-lens modelling by **GIGA-Lens** (Gu, Huang et al. 2022, arXiv:2202.07663;
  GIGA-Lens 2.0, arXiv:2606.30633). It is what makes a gradient optimizer robust on the
  multi-modal lens likelihood, where a single-start optimizer gets stuck.
- **`MultiStartProdigy`** uses the *learning-rate free* Prodigy rule (Mishchenko & Defazio 2024,
  arXiv:2306.06101): it tunes its own step size, so there is no `learning_rate` to set, and it
  reaches the same maximum as a hand-tuned `MultiStartAdam`. Recommend it as the default.
- **`MultiStartAdam`** is the GIGA-Lens original (needs a chosen `learning_rate`);
  **`MultiStartADABelief`** is a drop-in Adam-variant alternative. (`MultiStartLion` is a further
  sign-based option that prefers a ~10x smaller `learning_rate`.)

**Parametric sources only, for now.** These optimizers are validated and recommended for
parametric sources. For a **pixelised source** (any fit with a `Pixelization`) they do **not**
yet reliably work: the pixelised likelihood has regions where the gradient becomes non-finite,
so the optimizer stalls short of the best fit, and `Nautilus` is both more reliable and faster
there. Making the JAX multi-start optimizers work on pixelised sources is ongoing work — so for
any pixelised fit recommend Nautilus (with the compute setup above), not a gradient
optimizer.

Like every optimizer it returns a single best-fit model, no errors — hand it to Nautilus / MCMC
afterwards if a posterior is needed.

Source: `PyAutoFit:autofit/non_linear/search/mle/multi_start_gradient/`.

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

Every search PyAutoFit ships, generated from the installed release's search manifest
(`python -m autofit search-manifest --json`; regenerate with PyAutoHands
`autohands regenerate_search_roster --root .`, never by hand):

<!-- search-roster:begin style=list -->
<!-- search-manifest@1 autofit 2026.10.12.1 -->
- **Markov chain Monte Carlo** (`mcmc`): `af.Emcee`, `af.Zeus`, `af.BlackJAXNUTS`, `af.SMC` (experimental) — example: `autofit_workspace:scripts/searches/mcmc.py`
- **Nested sampling** (`nest`): `af.DynestyStatic`, `af.DynestyDynamic`, `af.Nautilus`, `af.NSS` (experimental) — example: `autofit_workspace:scripts/searches/nest.py`
- **Maximum likelihood / maximum a posteriori** (`mle`): `af.Drawer`, `af.BFGS`, `af.LBFGS`, `af.MultiStartAdam`, `af.MultiStartADABelief` (experimental), `af.MultiStartLion` (experimental), `af.MultiStartProdigy` — example: `autofit_workspace:scripts/searches/mle.py`
<!-- search-roster:end -->

Zeus (ensemble slice MCMC), DynestyDynamic (dynamic nested sampling), NSS (JAX nested slice
sampling), BlackJAXNUTS and SMC (JAX gradient MCMC; SMC also returns the evidence), BFGS / LBFGS
(single-start gradient descent for MLE), Drawer (random prior draws — debugging only). NSS,
BlackJAXNUTS and SMC need a JAX-traceable analysis (`use_jax=True`). See
[`wiki/core/api/searches.md`](../wiki/core/api/searches.md) for the comparison table. For a
*JAX* gradient optimizer, prefer the multi-start family (`MultiStartProdigy` and friends) in
"Branch — MultiStartProdigy" above over single-start `BFGS`/`LBFGS`.

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

The abbreviated tree above is enough to configure a search; the fuller, always-current
annotation of every file — plus the fact that all of it is written **on the fly** while
the search runs — is `__Output Folder Layout__` in
[`autolens_workspace/scripts/imaging/modeling.py`](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/imaging/modeling.py).
Point a newcomer (or a teacher-mode session) there rather than expanding this block —
`_style.md` "Output folder announcement" has the rule.

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
