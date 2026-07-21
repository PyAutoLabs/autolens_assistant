---
title: Non-linear search catalogue
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/nest/nautilus/
      - autofit/non_linear/search/nest/dynesty/
      - autofit/non_linear/search/mcmc/emcee/
      - autofit/non_linear/search/mcmc/zeus/
      - autofit/non_linear/search/mle/bfgs/
      - autofit/non_linear/search/mle/drawer/
      - autofit/non_linear/search/mle/multi_start_gradient/
    pinned_commit: main
last_updated: 2026-07-21
---

# Non-linear search catalogue

The full menu of non-linear searches PyAutoFit ships. For the conceptual map (what
nested sampling vs MCMC actually does), see
[`../concepts/non_linear_search`](../concepts/non_linear_search.md).

## Nested samplers (best default for lensing)

### `af.Nautilus`

The recommended default. Fast, robust to multi-modality, scales well to 30+ free
parameters.

```python
af.Nautilus(
    path_prefix=..., name=..., unique_tag=...,
    n_live=200,                  # 100 (exploration) / 200 (production) / 400+ (complex)
    number_of_cores=4,
    iterations_per_quick_update=2500,  # cadence for the on-the-fly max-likelihood fit
)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/nautilus/`. Optional dep:
`nautilus-sampler` (pinned to 1.0.5 in the stack).

Reference: Lange (2023), arXiv:2306.16923 — see
[`wiki/literature/sources/bayesian-inference-methods.md`](../../literature/sources/bayesian-inference-methods.md#lange-2023--nautilus).

### `af.DynestyStatic` / `af.DynestyDynamic`

Static = fixed live-point count throughout. Dynamic = focuses live points where
they're most useful (tails for evidence, posterior bulk for parameters).

```python
af.DynestyStatic(path_prefix=..., name=..., nlive=150)
af.DynestyDynamic(path_prefix=..., name=..., nlive_init=100)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/dynesty/`. Pinned: `dynesty==2.1.4`.

Reference: Speagle (2020), arXiv:1904.02180 — see
[`wiki/literature/sources/bayesian-inference-methods.md`](../../literature/sources/bayesian-inference-methods.md#speagle-2020--dynesty).

### UltraNest

UltraNest is not exposed as a public `autofit` search class, and its former
`nest/ultranest/` module has been removed from `main` entirely. Prefer
`af.Nautilus`, `af.DynestyStatic`, or `af.DynestyDynamic` for nested-sampling
runs.

```python
af.Nautilus(path_prefix=..., name=..., n_live=200)
```

Reference: Buchner — algorithmic foundation in
[`wiki/literature/concepts/nested-sampling.md`](../../literature/concepts/nested-sampling.md)
(Skilling 2006); UltraNest itself is documented at
https://johannesbuchner.github.io/UltraNest.

## MCMC

### `af.Emcee`

Affine-invariant ensemble. The MCMC default. Best for posterior characterisation
around a known mode, not for finding the mode in the first place.

```python
af.Emcee(path_prefix=..., name=..., nwalkers=50, nsteps=10000)
```

Source: `PyAutoFit:autofit/non_linear/search/mcmc/emcee/`. Pinned: `emcee>=3.1.6`.

Reference: Foreman-Mackey et al. (2013), arXiv:1202.3665 — see
[`wiki/literature/sources/bayesian-inference-methods.md`](../../literature/sources/bayesian-inference-methods.md#foreman-mackey-2013--emcee).

### `af.Zeus`

Ensemble slice sampler. Handles correlated posteriors better than Emcee, similar
runtime per step.

```python
af.Zeus(path_prefix=..., name=..., nwalkers=50, nsteps=10000)
```

Source: `PyAutoFit:autofit/non_linear/search/mcmc/zeus/`. Optional dep.

Reference: Karamanis, Beutler & Peacock (2021), arXiv:2105.03468 — see
[`wiki/literature/sources/bayesian-inference-methods.md`](../../literature/sources/bayesian-inference-methods.md#karamanis-2021--zeus).

## Optimisation (no posterior)

### `af.MultiStartProdigy` (recommended JAX gradient optimizer)

The recommended JAX / `optax` multi-start gradient optimizer for a fast maximum-a-posteriori
(MAP) *point* estimate. Launches `n_starts` broad starts in parallel via `jax.vmap` and returns
the best — the **multi-start** approach from GIGA-Lens (Gu, Huang et al. 2022, arXiv:2202.07663;
2.0 arXiv:2606.30633) that makes gradient descent robust where a single-start optimizer
(`BFGS`/`LBFGS`) gets stuck. Prodigy is *learning-rate free* (Mishchenko & Defazio 2024,
arXiv:2306.06101), so there is no `learning_rate` to set; it matches a hand-tuned `MultiStartAdam`.

```python
af.MultiStartProdigy(path_prefix=..., name=..., n_starts=50, n_steps=500)
```

`MultiStartAdam` (GIGA-Lens original; takes `learning_rate`) and `MultiStartADABelief` are drop-in
alternatives; `MultiStartLion` is a further sign-based option (~10x smaller `learning_rate`).

Requires a JAX-traceable analysis (`use_jax=True`). **Validated for parametric sources (MGE,
Sersic) only — not pixelised sources**, where the likelihood has non-finite gradient regions that
stall the optimizer; use `Nautilus` there. Making these work on pixelised sources is ongoing work.

Source: `PyAutoFit:autofit/non_linear/search/mle/multi_start_gradient/`. Optional deps: `jax`,
`optax` (>=0.2.5 for the Prodigy rule).

### `af.BFGS`

Quasi-Newton gradient descent to the MLE. No posterior, no errors. Useful as a
starting point for an MCMC chain or as a quick mode-finding pass.

```python
af.BFGS(path_prefix=..., name=...)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/bfgs/`.

### Particle Swarm / MLE Searches

PySwarms is not exposed as a public `autofit` search class, and its former
`mle/pyswarms/` module has been removed from `main` entirely. Use the public
MLE/debug searches instead.

```python
af.LBFGS(path_prefix=..., name=...)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/`.

### `af.Drawer`

Draws random samples from the prior. Not a real search — for debugging that the
prior gives reasonable models.

```python
af.Drawer(path_prefix=..., name=..., total_iterations=100)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/drawer/`.

## Picking a search at a glance

| Goal | Pick |
|---|---|
| First-fit, model under ~30 free params | `Nautilus(n_live=200)` |
| Production, multi-modal expected | `Nautilus(n_live=400)` |
| Bayesian evidence comparison | `Nautilus` or `DynestyStatic` |
| Posterior refinement around known mode | `Emcee` or `Zeus` |
| Very high-D (>50 params) | `Nautilus(n_live=400+)` |
| Fast JAX MAP point estimate, parametric source | `MultiStartProdigy` |
| Find a starting point fast | `BFGS` or `LBFGS` |
| Check that the prior is sane | `Drawer` |

## Shared knobs

Every search accepts:

- `path_prefix: str` — output folder prefix.
- `name: str` — identifier; combined with the model hash to form `unique_id`.
- `unique_tag: Optional[str]` — extra discriminator for runs that share path + name.
- `number_of_cores: int` — parallel likelihood evals.
- `iterations_per_quick_update: int` / `iterations_per_full_update: int` — checkpoint
  cadence (quick intermediate writes, incl. the max-likelihood `fit.png`, vs full output +
  visualisation). Config fallbacks in `general.yaml` `updates:` (HPC mode overrides under
  `hpc:`).
- `live_visual_update: bool` — default `False`; if `True`, each quick update is also pushed
  to a live display surface (matplotlib viewer from a foreground script, in-place cell
  refresh in Jupyter/Colab) in addition to the unconditional disk write. Keep `False` on
  HPC/headless/background runs. Accepted by every search (common base class); reaches
  `af.Nautilus(...)` via `**kwargs`.
- `silence: bool` — suppress console output.

See `PyAutoFit:autofit/non_linear/search/abstract_search.py` for the common base
class.

## See also

- [`../concepts/non_linear_search`](../concepts/non_linear_search.md) — when each
  family applies.
- [`../../../skills/al_configure_search.md`](../../../skills/al_configure_search.md) —
  authoring a search in code.
- [`../../../skills/al_chain_searches.md`](../../../skills/al_chain_searches.md) — using
  one search's result as another's prior.
