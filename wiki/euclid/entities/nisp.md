---
title: NISP (Near-Infrared Spectrometer and Photometer)
type: entity
topics: [instrument]
sources:
  - Euclid Collaboration - Jahnke et al. 2025 — EuclidSkyNISP
  - Euclid Collaboration - Polenta et al. 2025 — Q1-TP003
status: drafted
---

# NISP — the Euclid near-infrared instrument

## What it is

Euclid's near-infrared imager and slitless spectrograph, providing the Y_E, J_E, H_E
photometric bands at 0.3"/pixel (PSF FWHM ≈ 0.35"). Instrument paper: Jahnke et al.
2025 (`EuclidSkyNISP`); Q1 NIR processing: Polenta et al. 2025 (`Q1-TP003`; DR1
update in prep).

## Key facts

- Three NIR bands give the colour information the single [[vis]] band lacks —
  crucial for photometric redshifts ([[euclid-photo-z]]) and for lens/source SED
  separation.
- 3× coarser pixels and ~2× wider PSF than VIS: in the modeling pipeline NIR bands
  are fitted with the full VIS lens model held fixed, with only a per-band
  astrometric offset free
  (`euclid_strong_lens_modeling_pipeline:scripts/lens_model_waveband.py`).
- Multi-band photometry of lens and source requires PSF care across the resolution
  gap — [[psf-homogenisation]].

## See also

- [[vis]], [[ext-surveys]], [[euclid-photo-z]]
