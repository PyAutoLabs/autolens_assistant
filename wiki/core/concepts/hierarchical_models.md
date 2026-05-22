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

A single lens gives a
posterior on its own parameters. A sample of lenses, fit jointly with
hyperparameters linking them, gives a posterior on the *population*. The
machinery is PyAutoFit's graphical-model framework: per-lens factors, a
hyperparameter node, message passing or joint sampling.

## What "hierarchical" means here

In a hierarchical model, each lens keeps its own local parameters, but
some of those parameters are assumed to be draws from a shared parent
distribution. The parent distribution is itself inferred from the data.

Typical lensing examples:

- `H0` shared across a sample of time-delay lenses
- a population mean and scatter for the density slope of SLACS-like
  galaxies
- a concentration-mass relation for a sample of clusters
- a shared dark-matter model mapped through many sensitivity-calibrated
  subhalo searches

The statistical payoff is shrinkage: individual noisy systems borrow
strength from the ensemble without being forced to be identical.

## Joint vs. message-passing fitting

There are two main operating regimes.

- **Joint sampling** puts every local and global parameter in one search.
  This is conceptually simple and usually preferred when the sample is
  small enough that the dimensionality remains manageable.

- **Expectation propagation (EP)** factorizes the problem into per-lens
  factors that exchange messages about the shared hyperparameters. This
  scales much better once the number of lenses becomes large.

PyAutoFit's documentation explicitly positions EP as the route for
high-dimensional graphical models where a monolithic fit becomes
inefficient or impractical.

## Defining a factor graph

The implementation lives in `PyAutoFit:autofit/graphical/`. The core
pattern is:

1. create one local `Model` per dataset
2. tie selected parameters across those models by reusing the same prior
   object or by introducing explicit parent-distribution parameters
3. pair each local model with its local `Analysis` in an
   `AnalysisFactor`
4. combine the factors into a `FactorGraphModel`

This is the graphical-model generalization of ordinary multi-dataset
fitting. The "nodes" are dataset-specific analyses; the "links" are the
shared priors or hyperparameters.

## Expectation propagation in practice

EP alternates between local fits and global message updates. In practice
you watch for:

- stabilization of the shared-parameter posterior
- consistency of messages passed between factors
- agreement between EP and a smaller joint fit on a reduced problem,
  when such a cross-check is affordable

If the graph is small and EP bookkeeping adds more complexity than it
saves, fall back to a direct joint fit. If the graph is very large, EP is
often the only realistic path.

## Use cases

- H0 from a time-delay ensemble.
- Mass-slope distribution from a SLACS-like sample.
- Concentration-mass relation from a cluster sample.
- WDM particle-mass or subhalo-abundance limits from a stack of
  sensitivity-calibrated non-detections.

## Related pages

- [`concepts/time_delay_cosmography.md`](./time_delay_cosmography.md) —
  H0 from a single time-delay lens; this page extends to samples.
- [`api/aggregator.md`](../api/aggregator.md) — bulk loading of the
  per-lens fits a hierarchical model consumes.
