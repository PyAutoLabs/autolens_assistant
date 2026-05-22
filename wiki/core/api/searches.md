---
title: Non-linear search catalogue
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/nest/nautilus.py
      - autofit/non_linear/search/nest/dynesty.py
      - autofit/non_linear/search/nest/ultranest.py
      - autofit/non_linear/search/mcmc/emcee.py
      - autofit/non_linear/search/mcmc/zeus.py
      - autofit/non_linear/search/mle/bfgs.py
      - autofit/non_linear/search/mle/pyswarms.py
      - autofit/non_linear/search/mle/drawer.py
    pinned_commit: main
last_updated: 2026-05-22
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

Source: `PyAutoFit:autofit/non_linear/search/nest/nautilus.py`. Optional dep:
`nautilus-sampler` (pinned to 1.0.5 in the stack).

### `af.DynestyStatic` / `af.DynestyDynamic`

Static = fixed live-point count throughout. Dynamic = focuses live points where
they're most useful (tails for evidence, posterior bulk for parameters).

```python
af.DynestyStatic(path_prefix=..., name=..., nlive=150)
af.DynestyDynamic(path_prefix=..., name=..., nlive_init=100)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/dynesty.py`. Pinned: `dynesty==2.1.4`.

### `af.UltraNest`

Reactive nested sampling — scales to high-dim problems with strong constraints.
Heavier; use when Nautilus struggles.

```python
af.UltraNest(path_prefix=..., name=..., num_live_points=200)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/ultranest.py`. Optional dep.

## MCMC

### `af.Emcee`

Affine-invariant ensemble. The MCMC default. Best for posterior characterisation
around a known mode, not for finding the mode in the first place.

```python
af.Emcee(path_prefix=..., name=..., nwalkers=50, nsteps=10000)
```

Source: `PyAutoFit:autofit/non_linear/search/mcmc/emcee.py`. Pinned: `emcee>=3.1.6`.

### `af.Zeus`

Ensemble slice sampler. Handles correlated posteriors better than Emcee, similar
runtime per step.

```python
af.Zeus(path_prefix=..., name=..., nwalkers=50, nsteps=10000)
```

Source: `PyAutoFit:autofit/non_linear/search/mcmc/zeus.py`. Optional dep.

## Optimisation (no posterior)

### `af.BFGS`

Quasi-Newton gradient descent to the MLE. No posterior, no errors. Useful as a
starting point for an MCMC chain or as a quick mode-finding pass.

```python
af.BFGS(path_prefix=..., name=...)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/bfgs.py`.

### `af.PySwarms`

Particle swarm optimisation. Slower than BFGS but more robust to local minima.

```python
af.PySwarms(path_prefix=..., name=..., n_particles=50)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/pyswarms.py`. Pinned:
`pyswarms==1.3.0`.

### `af.Drawer`

Draws random samples from the prior. Not a real search — for debugging that the
prior gives reasonable models.

```python
af.Drawer(path_prefix=..., name=..., total_iterations=100)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/drawer.py`.

## Picking a search at a glance

| Goal | Pick |
|---|---|
| First-fit, model under ~30 free params | `Nautilus(n_live=200)` |
| Production, multi-modal expected | `Nautilus(n_live=400)` |
| Bayesian evidence comparison | `Nautilus` or `DynestyStatic` |
| Posterior refinement around known mode | `Emcee` or `Zeus` |
| Very high-D (>50 params) | `UltraNest` |
| Find a starting point fast | `PySwarms` or `BFGS` |
| Check that the prior is sane | `Drawer` |

## Shared knobs

Every search accepts:

- `path_prefix: str` — output folder prefix.
- `name: str` — identifier; combined with the model hash to form `unique_id`.
- `unique_tag: Optional[str]` — extra discriminator for runs that share path + name.
- `number_of_cores: int` — parallel likelihood evals.
- `iterations_per_update: int` — checkpoint cadence.
- `force_pickle_overwrite: bool` — overwrite on restart.

See `PyAutoFit:autofit/non_linear/search/abstract_search.py` for the common base
class.

## See also

- [`../concepts/non_linear_search`](../concepts/non_linear_search.md) — when each
  family applies.
- [`../../../skills/al_configure_search.md`](../../../skills/al_configure_search.md) —
  authoring a search in code.
- [`../../../skills/al_chain_searches.md`](../../../skills/al_chain_searches.md) — using
  one search's result as another's prior.
