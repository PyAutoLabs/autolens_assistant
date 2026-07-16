---
title: PSF homogenisation for multi-band photometry
type: concept
topics: [data, photometry, psf]
sources:
  - Euclid Collaboration - Romelli et al. 2025 — Q1-TP004
  - Boucaud et al. 2016 — Boucaud2016
status: drafted
---

# PSF homogenisation

## The concept

Aperture photometry compared across bands only measures colours if every band sees
the galaxy through the *same* effective PSF. The standard approach is to
homogenise: build per-band convolution kernels that degrade each
higher-resolution image to the PSF of the lowest-resolution band, then measure
matched apertures. Euclid's MER processing (Romelli et al. 2025, `Q1-TP004`;
DR1 update Kümmel et al. 2026 in prep) uses the kernel-creation algorithm of
Boucaud et al. 2016 (`Boucaud2016`), which builds kernels by Wiener filtering
with a tunable regularisation parameter.

## Why it matters for lens modeling

The modeling pipeline's aperture-photometry latents follow the same logic: the
lowest-resolution band's PSF and FWHM are loaded alongside the VIS data
(`euclid_strong_lens_modeling_pipeline:util.py`, `load_vis_dataset`) and set the
common aperture scale for the multi-band flux measurements. Model-based
photometry (fitting each band's image with its own PSF, as
`scripts/lens_model_waveband.py` and `scripts/sersic_lens_model.py` do) sidesteps
kernel homogenisation entirely — one of its main advantages for blended
lens/source systems.

## See also

- [[euclid-psf]], [[euclid-photo-z]], [[ext-surveys]]
