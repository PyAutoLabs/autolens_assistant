---
title: Euclid Q1 lens sample
type: entity
topics: [survey, sample, space]
sources:
  - Strong_Lens/EuclidQ12025paperI.pdf
  - Strong_Lens/EuclidQ12025paperII.pdf
  - Strong_Lens/EuclidQ12025paperIII.pdf
  - Strong_Lens/ORiodan2023Euclid.pdf
  - Strong_Lens/Wang2025SLEuclid.pdf
status: drafted
---

# Euclid Q1 lens sample

## What it is

The Q1 (Quick Release 1) data release from the Euclid space mission
produced the first wide-field, sub-arcsec, near-IR strong-lens catalogue
of the 2020s. The Q1 lensing papers (I, II, III) describe finding,
modelling, and population analyses; O'Riordan 2023 and Wang 2025
forecast / analyse the substructure-detection prospects.

## Key facts

- Resolution ~ 0.15″ in VIS; comparable depth to HST in a 14000 deg²
  footprint by mission end.
- Expected sample: ~100,000 lenses end-of-mission; Q1 already in the
  thousands.
- PyAutoLens is one of the modelling codes in the Euclid Strong Lens WG.

## Why it matters for PyAutoLens

Euclid is the largest user-facing customer for PyAutoLens at scale.
Pipelines must run unattended on thousands of lenses, with robust
[[selection-effects|selection]] characterisation and
[[multipoles|angular complexity]] for substructure work.

## See also

- [[lens-finding]]
- [[lens-statistics]]
- [[dark-matter-substructure]]
- [[sources-lens-finding]]
