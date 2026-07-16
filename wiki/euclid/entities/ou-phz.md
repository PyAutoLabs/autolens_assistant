---
title: OU-PHZ (Photometric-Redshift Organisation Unit)
type: entity
topics: [collaboration, photo-z]
sources:
  - Euclid Collaboration - Desprez et al. 2020 — Desprez-EP10
  - Euclid Collaboration - Tucci et al. 2025 — Q1-TP005
status: drafted
---

# OU-PHZ — the Euclid photometric-redshift unit

## What it is

The Euclid Organisation Unit responsible for photometric redshifts and the
photometric calibration that feeds them. Its pre-launch algorithm comparison is the
Euclid photo-z challenge (Desprez et al. 2020, `Desprez-EP10`); the Q1 PHZ
processing function is Tucci et al. 2025 (`Q1-TP005`).

## Key facts

- OU-PHZ computes the zero-point corrections (ZPCs) applied to Euclid + EXT
  photometry — [[zero-point-corrections]] — and the galaxy photo-zs and physical
  properties in the MER catalogues.
- For strong lensing, lens/source photo-zs from blended catalogue photometry are
  unreliable; the modeling pipeline instead produces deblended lens and source
  fluxes ([[euclid-photo-z]]).

## See also

- [[euclid-photo-z]], [[zero-point-corrections]]
