---
title: Regularization of pixelised source models
type: concept
topics: [lens-modelling]
sources: []
status: drafted
---

# Regularization

## TL;DR

When a [[source-reconstruction|source is pixelised]], the inversion is
ill-posed without a prior on smoothness or sparsity. Regularisation adds
a penalty term λ · sᵀH s (or an analogous L1 sparsity term) to the
likelihood, suppressing noise-driven oscillations. PyAutoLens treats λ
(and the form of H) as hyperparameters with their own evidence
optimisation.

## Forms in common use

- **Constant gradient / Laplacian (H = DᵀD)** — penalises spatial
  curvature of the source. Default.
- **Luminosity-weighted / brightness-adaptive** — penalty strength scales
  with local brightness, so faint regions are heavily smoothed and bright
  features keep their structure.
- **Cross-correlation / non-local** — relates non-neighbour pixels via a
  learned or photometric similarity.
- **L1 / sparsity (wavelet)** — drop the Gaussian-prior assumption and
  impose sparsity in a wavelet basis (SLIT / SLIT-ronomy, Galan 2021).

## Choosing λ

Two practical strategies coexist:

1. **Hierarchical Bayesian**: λ is a hyperparameter; the Bayesian
   evidence is maximised over λ at fixed mass-model parameters. This is
   the Suyu / Koopmans approach. It naturally penalises overfitting.
2. **Empirical / cross-validation**: split data, choose λ to optimise
   predictive accuracy on held-out pixels.

## Pitfalls

- **Over-regularisation absorbs lensing signal**: the source ends up too
  smooth, residuals look mass-model-like, biasing the mass model.
- **Under-regularisation absorbs noise**: the source recovers
  pixel-by-pixel noise, inflating the evidence locally but biasing the
  mass model in the opposite direction.
- The hyperparameter posterior **must be marginalised** when comparing
  models. Two fits with different λ are not comparable on χ² alone.

## See also

- [[source-reconstruction]]
- [[bayesian-inference-lensing]]
