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
    pinned_commit: main
last_updated: 2026-07-09
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
    iterations_per_update=2500,
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
| Find a starting point fast | `BFGS` or `LBFGS` |
| Check that the prior is sane | `Drawer` |

## Shared knobs

Every search accepts:

- `path_prefix: str` — output folder prefix.
- `name: str` — identifier; combined with the model hash to form `unique_id`.
- `unique_tag: Optional[str]` — extra discriminator for runs that share path + name.
- `number_of_cores: int` — parallel likelihood evals.
- `iterations_per_quick_update: int` / `iterations_per_full_update: int` — checkpoint
  cadence (quick intermediate writes vs full output + visualisation).
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
