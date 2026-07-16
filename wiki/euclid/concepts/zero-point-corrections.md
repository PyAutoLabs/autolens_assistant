---
title: Zero-point corrections (ZPCs)
type: concept
topics: [data, photometry, calibration]
sources:
  - Euclid Collaboration - Desprez et al. 2020 — Desprez-EP10
  - Euclid Collaboration - Tucci et al. 2025 — Q1-TP005
status: drafted
---

# Zero-point corrections

## The concept

A photometric zero-point ties instrumental counts to physical magnitudes
(`m_AB = ZP − 2.5 log₁₀(counts)`). Residual band-to-band calibration errors
propagate directly into colours and hence into photometric redshifts, so the
Euclid Photometric-Redshift Organisation Unit ([[ou-phz]]) computes zero-point
*corrections* — per-band adjustments calibrated so that galaxy SEDs are consistent
across Euclid and [[ext-surveys]] photometry (Desprez et al. 2020, `Desprez-EP10`;
Q1 implementation in Tucci et al. 2025, `Q1-TP005`).

The weak-lensing forecast literature is the reason the requirements are so tight:
photo-z biases at the ~10⁻³ level already degrade dark-energy constraints —
see [[../sources/euclid-forecasts|the forecasts sources page]] (Ma et al. 2006;
Huterer et al. 2006; Amara & Réfrégier 2007; Kitching et al. 2008).

## Why it matters for lens modeling

The modeling pipeline converts fitted fluxes to AB magnitudes with the MAGZERO
zero-point read from each dataset's FITS header
(`euclid_strong_lens_modeling_pipeline:util.py`, `ab_mag_via_flux_from`).
Deblended lens/source photometry inherits whatever zero-point calibration the
cutouts were built with — when comparing to catalogue magnitudes or fitting SEDs,
confirm whether ZPCs were already applied to your cutouts.

## See also

- [[euclid-photo-z]], [[ou-phz]]
