---
title: Gravitational imaging
type: concept
topics: [dark-matter, methods]
sources:
  - Strong_Lens/Koopmans2005GravImaging.pdf
  - Strong_Lens/Vegetti2018StellarNeutrinos.pdf
  - Strong_Lens/Nightingale2022Scanm.pdf
  - Strong_Lens/Verbados2022PotentialCoorr.pdf
status: drafted
---

# Gravitational imaging

## TL;DR

Gravitational imaging is the technique of detecting small mass
perturbers (DM subhaloes, LOS halos) by their distortion of an extended
lensed arc, treating the perturber as a localised correction to a smooth
mass model. Introduced as a pixelated-potential method by Koopmans
(2005), developed into a parametric NFW / pseudo-Jaffe scan by
Vegetti & Koopmans, and into a Bayesian-evidence scan / search by
Nightingale, Etherington, He and co-authors.

## What it is

Two equivalent formulations:

- **Potential correction** — free a pixelated δψ(θ) along with the
  source, look for localised peaks of |δψ| above the
  [[regularization|regularisation]] noise floor (Koopmans 2005; Suyu
  2009; Verbados 2022; Vernardos 2024).
- **Parametric perturber scan** — at each candidate position in the lens
  plane, fit an NFW (or pseudo-Jaffe) subhalo with mass M_sub and assess
  the Bayes factor against the null. Cleanest for individual detections.

PyAutoLens supports the parametric scan via SLaM-style chained searches.

## Sensitivity drivers

- Source contrast: lensed AGN > smooth galaxies for a given S/N.
- Arc curvature: high-magnification regions are more sensitive.
- Angular complexity of the smooth model — see [[multipoles]] —
  determines what counts as a residual.
- Source-pixel resolution (Minor 2024 / 2025 supersampling).

## Notable detections

- SDSSJ0946+1006 ("the Jackpot") — Vegetti 2010, Minor 2021, Nightingale
  ongoing. Apparently very concentrated → DM concentration puzzle.
- JVAS B1938+666 — Vegetti 2012.
- SDSSJ1430 — Powell 2020 (interferometric subhalo detection with VLBI).

## See also

- [[dark-matter-substructure]]
- [[flux-ratio-anomalies]]
- [[multipoles]]
- [[source-reconstruction]]
- [[sources-dark-matter-substructure]]
