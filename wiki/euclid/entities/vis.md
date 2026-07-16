---
title: VIS (Visible Camera)
type: entity
topics: [instrument]
sources:
  - Euclid Collaboration - Cropper et al. 2025 — EuclidSkyVIS
  - Euclid Collaboration - McCracken et al. 2025 — Q1-TP002
status: drafted
---

# VIS — the Euclid Visible Camera

## What it is

Euclid's wide-optical imager: a single broad band I_E (~550–900 nm) at 0.1"/pixel
with PSF FWHM ≈ 0.16". The instrument paper is Cropper et al. 2025
(`EuclidSkyVIS`); Q1 VIS processing and data products are McCracken et al. 2025
(`Q1-TP002`; a DR1 update is in prep).

## Key facts

- The lens-modeling band: nearly all Euclid strong-lens discovery and modeling is
  done on I_E, with other bands fixed to the VIS model
  (`euclid_strong_lens_modeling_pipeline:scripts/lens_model_waveband.py`).
- The broad single band maximises depth but carries no colour information on its
  own — colours come from [[nisp]] and [[ext-surveys]].
- The PSF varies with detector position, tile and epoch: each lens's cutout ships
  its own PSF ([[euclid-psf]]).
- Photometric calibration enters through the header zero-point
  ([[zero-point-corrections]]), which the modeling pipeline uses to convert
  aperture fluxes to AB magnitudes.

## See also

- [[euclid-psf]], [[nisp]], [[euclid-mission]]
