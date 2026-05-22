---
title: MCMC sampling
type: concept
topics: [methods, sampling]
sources: []
status: drafted
---

# MCMC sampling

## TL;DR

Markov chain Monte Carlo (MCMC) draws correlated samples from a posterior
without ever computing the evidence — fast and tight when you already know
where the posterior mode is, but ill-suited to multi-modal or
poorly-localised problems. In PyAutoLens, MCMC is the second-stage tool:
[[nested-sampling]] finds the mode, MCMC refines the posterior characterisation
around it.

## What it is

MCMC constructs a Markov chain whose stationary distribution is the target
posterior `p(θ|D) ∝ L(θ) π(θ)`. After a burn-in transient, samples from the
chain approximate independent posterior draws (up to autocorrelation). The
methodological lineage relevant to lensing software:

- **Metropolis-Hastings (1953/1970).** The original: propose a step from a
  fixed proposal distribution, accept or reject by the likelihood ratio.
  Hyper-parameters (proposal width, etc.) scale roughly as `~N²` in an
  N-dimensional problem and require manual tuning per posterior shape.
- **Goodman & Weare (2010) → emcee (Foreman-Mackey 2013).** Affine-invariant
  ensemble sampling: a swarm of walkers propose moves using offsets between
  pairs of walkers. The proposal is invariant under linear
  re-parameterisations, so the sampler handles *linearly* correlated
  posteriors with no manual tuning. Hyper-parameters drop to just 1–2
  regardless of dimensionality
  ([[sources-bayesian-inference-methods#foreman-mackey-2013-emcee]]).
- **Karamanis & Beutler (2021) → zeus.** Replaces emcee's stretch moves
  with ensemble *slice sampling* updates. The locally-adaptive slice
  proposals handle *non-linear* correlations between parameters and
  multi-modal targets that hurt emcee
  ([[sources-bayesian-inference-methods#karamanis-2021-zeus]]).
- **Hamiltonian Monte Carlo → NUTS (Hoffman & Gelman 2014).** Uses the
  gradient of the log-likelihood to inform proposal trajectories,
  suppressing random-walk behaviour and accelerating mixing in high
  dimensions. NUTS removes HMC's trajectory-length hyper-parameter via
  automatic stopping, making HMC turnkey
  ([[sources-bayesian-inference-methods#hoffman-2014-nuts]]).

All four are exposed somewhere in PyAutoFit: `af.Emcee` (emcee),
`af.Zeus` (zeus), `af.BlackJAXNUTS` (NUTS via BlackJAX), and the abstract
base classes for custom Metropolis-Hastings variants.

## Why it matters for PyAutoLens

MCMC is the **second stage** of a typical PyAutoLens fit. The first stage
is nested sampling — usually Nautilus — to find the posterior mode and
roughly localise its width without an initial guess. Once that's in hand,
MCMC has three useful applications:

1. **Tighter posterior characterisation around a known mode.** A few
   thousand MCMC steps from a Nautilus MAP can produce smoother corner
   plots and tighter tail estimates than re-running nested sampling at
   higher `n_live`, especially for the 1–2σ contours that observational
   papers report.
2. **Non-linearly correlated parameters.** Mass-slope ↔ Einstein-radius
   trade-offs, multipole amplitudes ↔ position angle, source-pixelisation
   coefficients — when the posterior has strong curved degeneracies,
   `af.Zeus`' slice updates outperform emcee's affine-invariant stretches.
3. **Gradient-based sampling for JAX likelihoods.** When PyAutoLens'
   likelihood pipeline is JAX-traceable end-to-end, `af.BlackJAXNUTS`
   gives gradient-informed proposals, which scale much better than
   gradient-free MCMC in high-dimensional pixelised-source fits.

MCMC's blind spot is **mode-finding**. Emcee and Zeus walkers initialised
from the prior on a multi-modal lens-model posterior will routinely collapse
onto a single mode and miss the others. This is why the workspace defaults
to a nested-sampling first stage and reserves MCMC for posterior refinement.

## Key results from the literature

- Affine-invariant ensemble MCMC needs only ~1–2 hand-tuned hyper-parameters
  regardless of problem dimensionality, vs. ~N² for traditional
  Metropolis-Hastings
  ([[sources-bayesian-inference-methods#foreman-mackey-2013-emcee]]).
- Ensemble slice sampling (zeus) outperforms emcee by 9–29× on benchmark
  cosmology and exoplanet problems, particularly when posteriors have
  strong non-linear correlations
  ([[sources-bayesian-inference-methods#karamanis-2021-zeus]]).
- NUTS eliminates HMC's path-length hyper-parameter via a recursive
  doubling + no-U-turn stopping rule, enabling turnkey gradient-based
  sampling
  ([[sources-bayesian-inference-methods#hoffman-2014-nuts]]).
- For posteriors that are uni-modal and well-localised, the evidence-
  integration overhead of nested sampling is wasted; MCMC is faster per
  effective sample. The workspace's chained-search convention uses nested
  sampling to find the mode, MCMC to characterise it
  ([[bayesian-inference-lensing]]).

## See also

- [[nested-sampling]] — the complementary family.
- [[bayesian-inference-lensing]] — Bayesian inference applied to lensing
  generally.
- [`wiki/core/concepts/non_linear_search.md`](../../core/concepts/non_linear_search.md)
  — PyAutoFit's conceptual map of the search catalogue.
- [`wiki/core/api/searches.md`](../../core/api/searches.md) — concrete
  `af.Emcee` / `af.Zeus` / `af.BlackJAXNUTS` signatures and knobs.
