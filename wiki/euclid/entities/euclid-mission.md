---
title: Euclid mission
type: entity
topics: [mission, space]
sources:
  - Euclid Collaboration - Mellier et al. 2025 — EuclidSkyOverview
  - Euclid Collaboration - Scaramella et al. 2022 — Scaramella-EP1
status: drafted
---

# Euclid

## What it is

ESA's wide-field space survey mission (launched July 2023) mapping the extragalactic
sky to constrain dark energy and dark matter through weak lensing and galaxy
clustering. One wide visible band ([[vis|VIS I_E]]) plus three near-infrared bands
([[nisp|NISP Y_E, J_E, H_E]]), over the ~14,000 deg² [[euclid-wide-survey]].

## Key facts

- ~1.5 billion galaxies imaged over the Wide Survey footprint.
- I_E PSF FWHM ≈ 0.16" at 0.1"/pixel — space-quality resolution over a
  hemisphere-scale area for the first time.
- Deep Fields (~53 deg², ~2 mag deeper) support calibration and hard-negative
  mining for lens finding.
- Data flow: quick release Q1 (2025, ~63 deg²) → DR1 (~2000 deg²) → final ~14,000
  deg² ([[q1-dr1-releases]]).

## Why it matters for strong lensing

Resolution + area is the strong-lensing revolution: simulations predict ~10⁵
galaxy-galaxy lenses in the Wide Survey, an order of magnitude beyond the known
population per data release ([[../sources/euclid-strong-lensing|sources]],
[[lens-finding]]). Uniform image quality also makes automated, standardised lens
modeling — the premise of `euclid_strong_lens_modeling_pipeline` — feasible at
survey scale.

## See also

- [[vis]], [[nisp]], [[euclid-wide-survey]], [[ext-surveys]]
- [[../literature/entities/euclid-q1|euclid-q1]] (general wiki page on the Q1 lens sample)
