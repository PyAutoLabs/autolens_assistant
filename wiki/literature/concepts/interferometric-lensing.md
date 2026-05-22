---
title: Interferometric strong lensing
type: concept
topics: [methods, observations]
sources:
  - Strong_Lens/Powell2020interfermeter.pdf
  - Strong_Lens/McKean2015SLSKA.pdf
  - Strong_Lens/Jackson2015SLRadioMaseMerlin.pdf
  - Strong_Lens/Dye2017ModelingAlma.pdf
  - Strong_Lens/Enia2018AlmaImaging.pdf
  - Strong_Lens/Stacey2024MultipolesALMA.pdf
status: drafted
---

# Interferometric lensing

## TL;DR

ALMA, VLBI, MERLIN, and (forthcoming) SKA observe strong lenses with
angular resolution from 10 mas (ALMA long baselines) down to ~1 mas
(VLBI). At these resolutions:

- Subhaloes down to ~10⁶ M_⊙ are detectable (Powell 2020, VLBI).
- Dust continuum from DSFGs is resolved to ~100 pc in the source plane.
- [[multipoles|Angular complexity]] of the lens is *required* to fit the
  data (Stacey 2024).

## What it is

Interferometric data live in the (u,v) plane, not the image plane.
Modelling is done in (u,v) directly:

- Predict the model image, FFT, sample at observed baselines, compare
  visibilities.
- The likelihood is naturally Gaussian in visibility space.
- Pixelated source models ([[source-reconstruction]]) extend cleanly.

## Why it matters for PyAutoLens

PyAutoLens supports both image-plane and direct-uv-plane fits. For ALMA
science with thousands of channels, direct-uv is essential. NUFFT-based
forward modelling is standard.

## See also

- [[source-reconstruction]]
- [[dark-matter-substructure]]
- [[multipoles]]
- [[lensed-source-science]]
- [[sources-interferometric-lensing]]
