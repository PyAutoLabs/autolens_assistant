---
title: Lens finding in wide-field surveys
type: concept
topics: [surveys, methods]
sources:
  - Metcalf et al. 2018 — lens finding challenge
  - Jacobs et al. 2019 — strong lensing DES
  - Jaelani et al. 2023 — strong lensing find HSC
  - Rojas et al. 2022 — DES lens model finding
  - Holloway et al. 2024 — Bayesian lens finding
  - Gavazzi et al. 2014 — Ringfinder
  - Sonnenfeld et al. 2018 — Yattalens
  - Sonnenfeld et al. 2020 — HSC lens modelling find
status: drafted
---

# Lens finding

## TL;DR

Wide imaging surveys contain ~10²–10⁴ strong lenses per 10⁴ deg² (Collett
2015). Finding them requires automated classification; the field
converged on convolutional neural networks (Jacobs 2019, Rojas 2022) trained on simulated
lenses and validated against expert inspection and spectroscopic follow-up. Citizen-science
projects such as Space Warps provide classifications and validation samples.

## What it is

- **Ringfinder** (Gavazzi 2014) — colour-image residuals after PSF
  subtraction.
- **YattaLens** (Sonnenfeld 2018) — arc detection followed by lens-model fitting.
- **CNN lens finders** — Jacobs et al., Petrillo et al.,
  Schaefer, Rojas 2022; standard for DES, KiDS, HSC.
- **Calibrated classifier ensembles** (Holloway 2024) — combine citizen-science and
  neural-network scores into probabilities suitable for candidate ranking.
- **Citizen science** — Space Warps for HFF and CFHT-LS;
  human-classification is still competitive on rare morphologies.

## Why it matters

- For science with samples of 100+ lenses, the **selection function** is
  set by the finder (see [[selection-effects]]). Robust statistical
  inference (e.g. [[lens-statistics|Sonnenfeld statistics series]])
  requires a calibrated selection function.
- For [[euclid-q1]] and Roman / LSST, the lens-finding pipeline is part
  of the science pipeline, not a pre-processing step.

## Why it matters for PyAutoLens

PyAutoLens can be used downstream of a finder to model candidates in batch. The finder's
selection function is an input to any population study built on the PyAutoLens models.

## See also

- [[selection-effects]]
- [[lens-statistics]]
- [[deep-learning-lensing]]
- [[euclid-q1]]
- [[space-warps]]
- [[sources-lens-finding]]
