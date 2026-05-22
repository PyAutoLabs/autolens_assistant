---
title: Sources — Bayesian inference methods
type: sources
topics: [methods, sampling, optimisation]
status: drafted
---

# Sources: Bayesian inference methods

The canonical-paper backing for the non-linear searches that PyAutoFit ships
and PyAutoLens defaults to. Six entries: three full reads (`drafted`) covering
the load-bearing samplers, three single-paragraph stubs (`stub`) for the
remaining MCMC entries. The concept pages [[nested-sampling]] and
[[mcmc-sampling]] cite into these sections.

PyAutoFit's search catalogue is documented in
[`wiki/core/api/searches.md`](../../core/api/searches.md); the conceptual map
is in [`wiki/core/concepts/non_linear_search.md`](../../core/concepts/non_linear_search.md).

## Skilling 2006 — Nested sampling

**File:** https://doi.org/10.1214/06-BA127 (Bayesian Analysis 1(4):833–860)
**Concepts:** [[nested-sampling]], [[bayesian-inference-lensing]]
**Status:** drafted

**Summary (drafted):**
Skilling's foundational paper that defines nested sampling — the algorithm
underneath every nested sampler PyAutoFit exposes (`Nautilus`, `DynestyStatic`,
`DynestyDynamic`, `UltraNest`). The idea is to recast the multi-dimensional
evidence integral `Z = ∫ L(θ) π(θ) dθ` as a one-dimensional integral over the
*prior mass* enclosed by the likelihood contour `L > L*`. A swarm of "live
points" is held inside successively shrinking iso-likelihood surfaces; at each
step the lowest-likelihood live point is replaced by a new draw constrained to
`L > L_min`. The accumulated discarded points form a sequence whose weighted
sum estimates Z, and re-weighting the same samples recovers the posterior as a
by-product.

The crucial property is that nested sampling is **invariant to the absolute
scale of the likelihood** — it depends only on the shape of nested contours.
That makes it robust to multi-modal posteriors and to "phase-change" problems
where thermal-annealing methods (parallel tempering, simulated annealing)
fail. It also returns the Bayesian evidence in a single sweep, which is the
quantity downstream model comparison needs.

For PyAutoLens this is the theoretical foundation behind the workspace's
default sampler choice. Lens-modelling posteriors are routinely multi-modal
(positional degeneracies, source-light vs. mass-light ambiguities, slope vs.
shear trade-offs), and the evidence is the canonical metric for choosing
between competing models (SIE vs. power-law, parametric vs. pixelised source,
smooth vs. with substructure). All of the nested samplers in PyAutoFit are
algorithmic refinements of Skilling's construction.

## Speagle 2020 — Dynesty

**File:** https://arxiv.org/abs/1904.02180 (MNRAS 493, 3132)
**Concepts:** [[nested-sampling]], [[bayesian-inference-lensing]]
**Status:** drafted

**Summary (drafted):**
Speagle's paper introduces `dynesty`, a Python package implementing **dynamic
nested sampling** — an extension of Skilling's static nested sampling that
adaptively allocates live points based on posterior structure. Static nested
sampling uses a fixed live-point count throughout the run, which is efficient
for evidence estimation but wastes computation when only the posterior bulk is
of interest. Dynamic nested sampling can be tuned along a spectrum from
"pure-evidence" allocation (live points concentrated in tail regions) to
"pure-posterior" allocation (live points concentrated where the posterior is
high), and any blend in between.

The paper also gives a careful exposition of the algorithmic choices: how new
live points are sampled under the likelihood constraint (uniform / random
walks / slice sampling), how to bound the constrained prior region (single /
multi ellipsoids / balls / cubes), and how to estimate sampling uncertainty
on Z itself. The appendix collects the statistical underpinnings of nested
sampling more rigorously than Skilling 2006.

For PyAutoLens, `af.DynestyStatic` and `af.DynestyDynamic` wrap this library
(pinned `dynesty==2.1.4` in the stack). Dynesty was the workspace's nested
sampler of record before Nautilus arrived; it remains the well-tested
alternative when Nautilus struggles or when reproducibility against older
papers matters. The "Static = fixed live points, Dynamic = adaptive" framing
in `wiki/core/api/searches.md` comes directly from this paper.

## Lange 2023 — Nautilus

**File:** https://arxiv.org/abs/2306.16923 (MNRAS 525, 3181)
**Concepts:** [[nested-sampling]], [[bayesian-inference-lensing]]
**Status:** drafted

**Summary (drafted):**
Lange introduces `nautilus`, a Python sampler that combines **importance
nested sampling** with **deep-learning-driven proposal distributions**.
Importance sampling (unlike rejection sampling in vanilla nested sampling)
uses *every* likelihood evaluation for both posterior and evidence
estimation — so the efficiency floor is much higher, provided the proposal
distribution closely matches the posterior. Nautilus learns that proposal on
the fly via a neural-network regression of the likelihood surface over the
live points already accumulated, and refines it as the run proceeds.

The headline empirical claim is that on a suite of toy and real problems
(exoplanet detection, galaxy SED fitting, cosmology) Nautilus achieves
sampling efficiencies often more than an order of magnitude higher than
Emcee, Dynesty, UltraNest, and pocoMC, while using fewer likelihood
evaluations. Scaling with parameter-space dimensionality is good through
~30 free parameters, and the method parallelises trivially across CPU cores.

For PyAutoLens this is the workspace's **de-facto default sampler**.
`af.Nautilus` (pinned to `nautilus-sampler==1.0.5`) is what
`scripts/imaging.py` reaches for, and what `_style.md`'s newcomer / returning
audiences will see first. The order-of-magnitude efficiency gain matters
because lens-model fits often involve 20–50 free parameters and expensive
forward models (PSF convolution + pixelised source inversion + position-
penalty term); cutting likelihood evaluations by 10× turns multi-hour fits
into minutes.

## Foreman-Mackey 2013 — emcee

**File:** https://arxiv.org/abs/1202.3665 (PASP 125, 306)
**Concepts:** [[mcmc-sampling]], [[bayesian-inference-lensing]]
**Status:** stub

**Summary (stub):** Foreman-Mackey et al. introduce `emcee`, a stable Python
implementation of Goodman & Weare's (2010) affine-invariant ensemble MCMC
sampler. Affine invariance means the sampler is unaffected by linear
re-parameterisations — it handles correlated posteriors without manual
proposal tuning. Compared to traditional Metropolis-Hastings, emcee requires
only 1–2 hand-tuned hyper-parameters in an N-dimensional problem (vs ~N²)
and exploits ensemble parallelism across CPU cores. PyAutoFit exposes this
as `af.Emcee` (pinned `emcee>=3.1.6`). Used in PyAutoLens for posterior
refinement around a known mode — not for finding the mode in the first
place.

## Karamanis 2021 — zeus

**File:** https://arxiv.org/abs/2105.03468 (MNRAS 508, 3589)
**Concepts:** [[mcmc-sampling]], [[bayesian-inference-lensing]]
**Status:** stub

**Summary (stub):** Karamanis, Beutler, and Peacock introduce `zeus`,
implementing **Ensemble Slice Sampling** (ESS). Like emcee, zeus is an
ensemble MCMC requiring minimal hand-tuning (1–2 hyper-parameters); unlike
emcee, its locally-adaptive slice-sampling updates handle strong *non-linear*
correlations between parameters, scale to thousands of CPUs, and sample
multi-modal distributions in high dimensions efficiently. Empirically the
paper reports zeus outperforming emcee by 9–29× on cosmological and
exoplanet benchmarks. PyAutoFit exposes this as `af.Zeus` (optional
dependency). Used in PyAutoLens when posteriors have strong non-linear
correlations (e.g. between mass-slope and Einstein radius) that hurt emcee's
affine-invariant updates.

## Hoffman 2014 — NUTS

**File:** https://arxiv.org/abs/1111.4246 (JMLR 15, 1593)
**Concepts:** [[mcmc-sampling]], [[bayesian-inference-lensing]]
**Status:** stub

**Summary (stub):** Hoffman and Gelman introduce the **No-U-Turn Sampler
(NUTS)**, an extension of Hamiltonian Monte Carlo (HMC) that eliminates
HMC's requirement to pre-set the number of leapfrog steps `L`. NUTS uses a
recursive doubling scheme that builds a candidate trajectory and stops
automatically when it starts to retrace its own path (the "no-U-turn"
criterion). Paired with primal-dual averaging for adaptive step-size
selection, NUTS is a turnkey gradient-informed sampler — the engine behind
Stan and BUGS-style probabilistic-programming systems. PyAutoFit exposes
NUTS via BlackJAX (`af.BlackJAXNUTS`); usable in PyAutoLens whenever the
likelihood pipeline is JAX-traceable, which is the route to gradient-based
sampling for the JAX-backed PyAutoLens likelihoods.
