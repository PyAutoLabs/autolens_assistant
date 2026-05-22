---
title: Bayesian inference for strong lensing
type: concept
topics: [methods]
sources: []
status: drafted
---

# Bayesian inference for strong lensing

## TL;DR

Strong-lens modelling is a high-dimensional, multimodal, often
ill-conditioned inverse problem. The community has converged on Bayesian
inference with nested sampling for posterior + evidence estimation.
PyAutoLens uses the [[pyautofit]] library for this, supporting nested
samplers like Dynesty, UltraNest, and Nautilus, and MCMC samplers like
emcee. Pixel-source likelihoods carry an analytic source-marginalisation
term (the "Bayesian evidence" of Suyu / Koopmans).

## Why nested sampling

- Returns the **evidence Z** — central for [[mass-models|model
  comparison]] (with vs. without external shear, EPL vs. composite, etc.).
- Handles multimodality (mirror images, parity ambiguities) better than
  vanilla MCMC.
- Doesn't need an initial guess close to the peak.

## The evidence for pixelised sources

For a pixelised source under Gaussian regularisation, the marginal
likelihood over source pixels is analytic:

```
log Z(θ_mass, λ) = −½ χ²(ŝ) − ½ log|LᵀC⁻¹L + λH| + ½ log|λH| − ½ N log(2π)
```

This is the quantity nested sampling explores over **mass-model
parameters and regularisation hyperparameters**, with the source itself
already marginalised out.

## Pipelines and hierarchical fits

A modern fit (e.g. SLaM; [[slam-pipeline]]) chains together a sequence of
sub-fits: first an SIE + Sérsic, then a power-law with a parametric
source, then the same with a pixelised source, then optionally a
composite stellar + dark fit. Each phase passes its posterior as a prior
to the next via PyAutoFit's "search chaining". This is essential for
robustness on real data.

## Model comparison

Bayesian evidence is the canonical metric. In practice:

- Two-sided log-evidence differences > a few are decisive.
- Cross-check with [[bayesian-inference-lensing|posterior predictive
  checks]] and residuals.
- For [[dark-matter-substructure|subhalo detection]] the
  evidence-difference threshold is calibrated against
  [[sources-dark-matter-substructure|Despali 2018/2022 sensitivity
  studies]].

## See also

- [[regularization]]
- [[source-reconstruction]]
- [[pyautofit]]
- [[pyautolens]]
