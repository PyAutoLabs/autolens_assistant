---
title: Nested sampling
type: concept
topics: [methods, sampling]
sources: []
status: drafted
---

# Nested sampling

## TL;DR

Nested sampling estimates the Bayesian evidence and posterior in a single
sweep by transforming a many-dimensional integral over parameter space into
a one-dimensional integral over prior mass enclosed by likelihood contours.
It handles multi-modal posteriors gracefully and is the right default family
for lens-model fitting in PyAutoLens
([[sources-bayesian-inference-methods#skilling-2006-nested-sampling]]).

## What it is

Originally proposed by Skilling (2006), nested sampling holds a swarm of
`N` "live points" drawn from the prior. At each iteration the
lowest-likelihood live point is **removed** and replaced by a fresh draw
from the prior, *conditioned on having higher likelihood than the one just
removed*. The removed points form a sequence of samples with monotonically
increasing likelihood, and the prior mass `X_i` enclosed by each
iso-likelihood contour shrinks deterministically (on average) by a factor
`(N − 1)/N` per iteration.

The evidence integral

```
Z = ∫ L(θ) π(θ) dθ
```

then collapses to a one-dimensional sum

```
Z ≈ Σ_i L_i · w_i,   w_i = X_{i−1} − X_i
```

where the discarded live points provide both the likelihoods `L_i` and the
prior-mass weights `w_i`. Re-weighting the same samples by `L_i w_i / Z`
recovers the posterior as a by-product.

The non-trivial engineering is the "constrained prior" draw — sampling
uniformly from the prior restricted to `L > L_min`. Different implementations
solve this differently:

- **Dynesty** (Speagle 2020) — random walks, slice sampling, or
  multi-ellipsoidal rejection sampling
  ([[sources-bayesian-inference-methods#speagle-2020-dynesty]]).
- **Nautilus** (Lange 2023) — *importance* sampling with a neural network
  trained on accumulated live points as the proposal
  ([[sources-bayesian-inference-methods#lange-2023-nautilus]]).
- **UltraNest** — reactive sampling that scales to higher dimensions.

The differences in efficiency between implementations can be one or two
orders of magnitude; the underlying mathematical guarantee is the same.

## Why it matters for PyAutoLens

Strong-lens modelling is a textbook nested-sampling use case:

- **Multi-modal posteriors.** Positional degeneracies (image parity flips),
  source-light vs. lens-light blending, mass-slope vs. Einstein-radius
  trade-offs, parametric source vs. pixelised source — all routinely
  produce multi-modal posterior landscapes. Standard MCMC samplers can get
  stuck in a single mode; nested sampling sweeps across all of them.
- **No initial guess required.** Searches start from prior draws and find
  the posterior bulk autonomously, which is essential for SLaM-style
  pipelines that pass priors from search to search rather than initial
  conditions ([[bayesian-inference-lensing]]).
- **Evidence for model comparison.** Comparing SIE vs. power-law mass
  models, with vs. without external shear, smooth vs. with substructure —
  the canonical metric is the log-evidence difference `Δ log Z`, which
  nested sampling produces directly. Two-sided differences ≳ 5 are
  considered decisive in the lensing literature.
- **Analytic source marginalisation.** For pixelised sources under Gaussian
  regularisation, PyAutoLens analytically marginalises over source pixels
  *inside* the likelihood, so nested sampling explores only mass-model and
  regularisation hyper-parameters — typically 10–30 free parameters, which
  is in nested sampling's sweet spot.

The workspace defaults reflect this: `af.Nautilus(n_live=200)` is the
recommended first-fit search, with `af.DynestyStatic` as the well-tested
alternative.

## Key results from the literature

- Nested sampling is invariant to the absolute scale of the likelihood,
  depending only on the *shape* of nested contours — which is why it
  handles phase-change problems that defeat parallel-tempering MCMC
  ([[sources-bayesian-inference-methods#skilling-2006-nested-sampling]]).
- Dynamic nested sampling can adaptively allocate live points between
  evidence-tail and posterior-bulk regions, improving efficiency by
  factors of a few over static nested sampling
  ([[sources-bayesian-inference-methods#speagle-2020-dynesty]]).
- Importance nested sampling with deep-learning-trained proposals
  (Nautilus) achieves order-of-magnitude efficiency gains over Dynesty,
  Emcee, UltraNest, and pocoMC on lensing-relevant problem geometries
  ([[sources-bayesian-inference-methods#lange-2023-nautilus]]).
- The Bayesian evidence for pixelised lens sources has an analytic
  closed form (Suyu / Koopmans evidence), reducing the effective
  dimensionality of what the sampler explores ([[bayesian-inference-lensing]]).

## See also

- [[mcmc-sampling]] — the alternative family.
- [[bayesian-inference-lensing]] — Bayesian inference applied to lensing
  generally.
- [`wiki/core/concepts/non_linear_search.md`](../../core/concepts/non_linear_search.md)
  — PyAutoFit's conceptual map of the search catalogue.
- [`wiki/core/api/searches.md`](../../core/api/searches.md) — concrete
  `af.Nautilus` / `af.DynestyStatic` / `af.DynestyDynamic` / `af.UltraNest`
  signatures and knobs.
