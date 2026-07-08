---
name: al_hierarchical_inference
description: Fit a population-level (hierarchical) model across many strong lenses — shared cosmology, shared mass-model slope distribution, or any parameter linked across systems. Implemented via PyAutoFit's graphical-model framework, including expectation propagation for samples that don't fit in one joint fit. Use when the question is "what does the *population* tell me?" rather than "what does this *one* lens look like?" Pairs with `al_aggregator_bulk_analysis` (operating on the per-lens fits this skill consumes). Writes a runnable Python script in scripts/. **Status: stub.**
---

# Hierarchical / graphical inference across a lens sample

A single lens gives you point-estimate parameters with uncertainty. A
sample of lenses, fit jointly with shared hyperparameters, gives you the
*population* distribution: H0 from a time-delay ensemble, the
mass-profile-slope distribution from a SLACS-like sample, the
NFW-concentration relation from a cluster sample.

PyAutoFit's graphical-model machinery is what makes this tractable at
scale. Expectation propagation (EP) handles cases where joint sampling is
infeasible by passing factorised messages between per-lens fits.

Workspace path: `autolens_workspace:scripts/guides/modeling/advanced/hierarchical.py`,
`scripts/guides/modeling/advanced/graphical.py`,
`scripts/guides/modeling/advanced/expectation_propagation.py`.

## Ask

- *"What's the shared parameter — H0, mass-slope distribution mean/scatter,
  source population, something else?"*
- *"How many lenses, and do you already have per-lens fits?"* This skill
  assumes per-lens fits exist; if not, run them first.
- *"Joint fit feasible, or do you need EP?"* Joint is fine up to ~10–20
  lenses; past that, EP scales better.
- *"What's the parent distribution — Gaussian (mean + scatter), uniform,
  custom?"*

## Branch — joint graphical fit, small N

> TODO: recipe. Pattern: define a `Factor` per lens linking that lens's
> parameters to a shared hyperparameter node; build a `FactorGraph`; fit
> with `Nautilus`. See `PyAutoFit:autofit/graphical/...`.

## Branch — expectation propagation, large N

> TODO: recipe. Pattern: same `FactorGraph` but with `MeanField` /
> `EPMeanField` and an iterative message-passing fit. Per-lens factors
> retain their own non-linear search; messages converge to a global
> hyperparameter posterior.

## Combine

- [`al_aggregator_bulk_analysis`](./al_aggregator_bulk_analysis.md) —
  operates on the per-lens fits this skill aggregates.
- [`al_time_delay_cosmography`](./al_time_delay_cosmography.md) — H0 from
  delays is the headline use case.

## Further reading

- **Student / new to lensing** — _ (advanced PyAutoFit topic).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  graphical models in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: guides/modeling/advanced/hierarchical.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/modeling/advanced/hierarchical.py):
  canonical hierarchical setup; sibling files cover graphical models and
  expectation propagation.

See also [`wiki/core/concepts/hierarchical_models.md`](../wiki/core/concepts/hierarchical_models.md)
for the statistical framing (parent distributions, marginalisation,
shrinkage).
