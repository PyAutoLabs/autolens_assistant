---
title: Euclid PSFs (per-tile, per-position)
type: concept
topics: [data, psf]
sources:
  - Euclid Collaboration - McCracken et al. 2025 — Q1-TP002
  - Euclid Collaboration - Polenta et al. 2025 — Q1-TP003
  - Euclid Collaboration - Cropper et al. 2025 — EuclidSkyVIS
status: drafted
---

# Euclid PSFs are target-specific

## The concept

There is no single "Euclid PSF". The point spread function of a given band is
unique to each target, depending on its survey tile and sky coordinates: detector
position, optical distortion, guiding and (for ground [[ext-surveys]] bands)
seeing all vary. The VIS and NIR processing pipelines (McCracken et al. 2025,
`Q1-TP002`; Polenta et al. 2025, `Q1-TP003`; DR1 updates in prep) model and
interpolate the PSF to each object's position. Reference FWHM values: I_E ≈ 0.16",
Y_E/J_E/H_E ≈ 0.35".

## Why it matters for lens modeling

The PSF enters the lens likelihood through convolution of the model image —
an incorrect PSF biases the mass model and the source reconstruction. This is why
each lens cutout in `euclid_strong_lens_modeling_pipeline` carries **its own**
per-band PSF inside the multi-HDU dataset FITS, loaded automatically by
`euclid_strong_lens_modeling_pipeline:util.py` (`load_vis_dataset`). Never reuse
another lens's PSF or a generic Gaussian for real Euclid fits.

Aperture photometry across bands additionally requires matching PSFs between
bands — [[psf-homogenisation]].

## See also

- [[vis]], [[nisp]], [[psf-homogenisation]]
