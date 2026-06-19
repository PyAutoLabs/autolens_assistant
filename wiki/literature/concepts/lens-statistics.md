---
title: Lens population statistics
type: concept
topics: [populations]
sources:
  - Sonnenfeld et al. 2021 — statistics I
  - Sonnenfeld et al. 2021 — statistics II
  - Sonnenfeld et al. 2022 — statistics
  - Li et al. 2023 — strong lens populations
  - Geng et al. 2025 — strong lensing relations
status: drafted
---

# Lens statistics

## TL;DR

With 10²–10⁵ lenses (now from HSC / DES, soon from
[[euclid-q1|Euclid]] and LSST), strong lensing becomes a **population
science**: scaling relations between σ, M_*, M_E, redshift, dark-matter
fraction, etc., constrain galaxy evolution and ΛCDM.

## What it is

Population-level inference treats each lens as a noisy realisation of a
hierarchical model:

- Hyperparameters describing the joint distribution of lens properties.
- Per-lens parameters with priors set by the hyperposterior.
- Marginalise per-lens parameters; constrain hyperparameters from the
  ensemble.

[[sources-lens-statistics|Sonnenfeld 2021/2022/2023]] is the canonical
treatment; uses HSC photometry + spectroscopy.

## Why it matters

- Mass-slope evolution with redshift, mass, σ.
- Stellar IMF / dark-matter-fraction trends with M_*.
- Selection-function corrections (see [[selection-effects]]).

## Why it matters for PyAutoLens

PyAutoFit supports hierarchical inference: per-lens PyAutoLens fits are
chained into a top-level hyperparameter inference. Holloway 2024 uses
this stack on DES sample.

## See also

- [[selection-effects]]
- [[lens-finding]]
- [[sources-lens-statistics]]
