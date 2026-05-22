---
title: PyAutoLens
type: entity
topics: [software]
sources:
  - AutoLens.pdf
  - autolens_paper1_resubmit_20180216.pdf
status: drafted
---

# PyAutoLens

## What it is

Open-source Python software for strong-lens modelling. Implements
parametric and pixelated lens-modelling, multi-plane ray tracing,
direct-uv interferometric fits, and the [[bayesian-inference-lensing]]
backend via [[pyautofit|PyAutoFit]]. The audience for this wiki is the
PyAutoLens user / AI assistant.

## Key facts

- **Forward model**: composable `MassProfile` + `LightProfile` for lens,
  parametric / MGE / pixelated source.
- **Inference**: PyAutoFit (nested sampling, MCMC, search chaining).
- **Pipelines**: SLaM ([[slam-pipeline]]) for galaxy-scale chained fits.
- **Data types**: imaging, interferometric, multi-wavelength.
- **Use cases**: substructure detection, time-delay cosmography, source
  reconstruction, lens population fits.

## See also

- [[slam-pipeline]]
- [[pyautofit]]
- [[lenstronomy]]
- [[sources-lens-modeling-methods]]
