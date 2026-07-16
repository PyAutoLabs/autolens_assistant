---
title: Euclid Wide Survey (EWS)
type: entity
topics: [survey]
sources:
  - Euclid Collaboration - Scaramella et al. 2022 — Scaramella-EP1
  - Euclid Collaboration - Mellier et al. 2025 — EuclidSkyOverview
status: drafted
---

# Euclid Wide Survey

## What it is

The ~14,000 deg² main survey (Scaramella et al. 2022, `Scaramella-EP1`; updated in
the mission overview `EuclidSkyOverview`): a contiguous high-latitude footprint
imaged in I_E + Y_E/J_E/H_E, complemented by ground-based [[ext-surveys]] optical
photometry.

## Key facts

- ~1.5 billion galaxies; predicted ~10⁵ discoverable galaxy-galaxy strong lenses.
- Depth I_E ≈ 24.5 (10σ extended); NIR ≈ 24.0 (5σ point).
- Observed in ~0.7 deg² tiles; calibration (PSF, zero-points) is tile- and
  position-dependent ([[euclid-psf]], [[zero-point-corrections]]).
- Released progressively — [[q1-dr1-releases]].

## Why it matters for strong lensing

Sample sizes jump from hundreds to tens of thousands of lenses: discovery,
grading, modeling and population analysis all have to be automated and uniform
([[lens-finding]], [[lens-statistics]], [[selection-effects]]), which is what the
standardised `euclid_strong_lens_modeling_pipeline` outputs are for.

## See also

- [[euclid-mission]], [[ext-surveys]], [[q1-dr1-releases]]
