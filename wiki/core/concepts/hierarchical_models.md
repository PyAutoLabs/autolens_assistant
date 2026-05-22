---
title: Hierarchical and graphical models across lens samples
sources:
  - project: PyAutoFit
    paths:
      - autofit/graphical
    pinned_commit: main
last_updated: 2026-05-22
---

# Hierarchical / graphical inference

**Status: stub — content to be filled out.** A single lens gives a
posterior on its own parameters. A sample of lenses, fit jointly with
hyperparameters linking them, gives a posterior on the *population*. The
machinery is PyAutoFit's graphical-model framework: per-lens factors, a
hyperparameter node, message passing or joint sampling.

## What "hierarchical" means here

> TODO: parent distributions over per-lens parameters; the population
> distribution itself becomes the inference target. Examples: H0 across
> a sample of time-delay lenses; mass-slope mean + scatter across SLACS
> lenses; concentration-mass relation across clusters.

## Joint vs. message-passing fitting

> TODO: joint sampling is fine up to ~10–20 lenses (all per-lens
> parameters in one sampler); past that, expectation propagation (EP)
> factorises into per-lens problems with messages converging to a
> global hyperparameter posterior.

## Defining a factor graph

> TODO: per-lens `AnalysisFactor` instances, hyperparameter nodes, the
> `FactorGraph` that links them. Cite `PyAutoFit:autofit/graphical/...`.

## Expectation propagation in practice

> TODO: iteration scheme, convergence diagnostics, when to fall back to
> joint sampling.

## Use cases

> TODO:
> - H0 from time-delay ensemble.
> - Mass-slope distribution from a SLACS-like sample.
> - NFW concentration-mass relation from a cluster sample.
> - WDM particle-mass limit from a stack of sensitivity maps.

## Related pages

- [`concepts/time_delay_cosmography.md`](./time_delay_cosmography.md) —
  H0 from a single time-delay lens; this page extends to samples.
- [`api/aggregator.md`](../api/aggregator.md) — bulk loading of the
  per-lens fits a hierarchical model consumes.
