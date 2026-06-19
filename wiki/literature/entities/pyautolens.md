---
title: PyAutoLens
type: entity
topics: [software]
sources:
  - AutoLens — PyAutoLens method/code paper
  - AutoLens paper I (2018 resubmission)
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

## Key papers

PyAutoLens has four canonical citations (full read-ups in
[[sources-lens-modeling-methods]]):

- **Nightingale & Dye 2015** — adaptive Semi-Linear Inversion; the
  source-plane-discretisation kernel that became PyAutoLens.
- **Nightingale, Dye & Massey 2018** — AutoLens code paper; the
  methodology citation for the automated lens-modelling pipeline.
- **Nightingale et al. 2021** — PyAutoLens (JOSS); the software
  citation for the package itself.
- **Etherington et al. 2022** — SLaM pipeline / "no lens left
  behind"; the production-pipeline citation behind `scripts/imaging.py`.

## See also

- [[slam-pipeline]]
- [[pyautofit]]
- [[lenstronomy]]
- [[sources-lens-modeling-methods]]
