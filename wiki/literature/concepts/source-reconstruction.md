---
title: Source reconstruction
type: concept
topics: [lens-modelling]
sources:
  - Galan et al. 2021 — SLIT
  - Galan et al. 2022 — Wavelet
  - Koopmans et al. 2005 — Grav Imaging
  - Ding et al. 2016 — SHARPIX Gal Recon
  - Suyu et al. 2009 — Spiral Potential Corr
status: drafted
---

# Source reconstruction

## TL;DR

For a given mass model, source reconstruction is the step where the
unlensed background source is solved for. Three families are in common
use:

1. **Parametric** — Sérsic, exponential, MGE; few free parameters, robust,
   but biased when the source is complex.
2. **Pixelised / semi-linear inversion** — adaptive grid or Voronoi
   tessellation in the source plane, linear inversion under
   [[regularization]] (Warren & Dye 2003; Suyu / Koopmans formalism).
   Lets the source be anything but needs regularisation to suppress noise.
3. **Wavelet / sparse** — represent the source in a basis (starlets,
   wavelets) and impose sparsity; SLIT and SLIT-ronomy
   ([[sources-source-reconstruction|Galan 2021, 2022]]).

## Why it matters for PyAutoLens

PyAutoLens supports parametric, MGE, Voronoi-pixelised, and Delaunay
sources, with built-in regularisation schemes (constant, adaptive,
luminosity-weighted). Choice of source matters because:

- An under-flexible source absorbs **mass-model error** into its residuals
  → biased mass parameters.
- An over-flexible source absorbs **real lensing signal** → biased source
  morphology and washed-out [[dark-matter-substructure|substructure
  detectability]].

For [[gravitational-imaging]] (subhalo detection), pixelated sources are
essentially mandatory: the perturbation is small, and the signal is
spread across many pixels.

## Pixelised source — mechanics

Given a linear forward model **d = L s + n** where **L** is the
lens-mapping + PSF operator and **s** is the source vector, the
maximum-likelihood (regularised) source is

```
ŝ = (LᵀC⁻¹L + λ H)⁻¹ LᵀC⁻¹ d
```

with **C** the noise covariance, **H** a regularisation matrix, and **λ**
its strength. The Bayesian evidence
([[bayesian-inference-lensing]]) marginalises over **s** analytically and
penalises overcomplexity through |LᵀC⁻¹L + λH|.

The grid:

- Square uniform grids are simple but waste resolution.
- Adaptive Voronoi / Delaunay grids tessellate where the lensing maps
  many image-plane pixels — i.e. where signal is highest.
- Brightness-adaptive (luminosity-weighted) regularisation strengthens
  smoothing in dim regions and relaxes it in bright structure.

## Potential corrections

A related thread: rather than (or in addition to) freeing the source,
free **potential perturbations δψ(θ)** that absorb un-parametrised lens
mass complexity ([[gravitational-imaging]]; Suyu 2009; Koopmans 2005;
Vernardos / Verbados 2022). This is one of the two routes to subhalo
detection.

## Common pitfalls

- **Source degeneracy with shear**: a more elliptical source can mimic
  external shear and vice-versa. Compare fits with and without external
  shear ([[external-convergence-shear]]).
- **Mass-sheet absorbing source size**: scaling the source by (1-κ_∞)
  exactly compensates a sheet — see [[mass-sheet-degeneracy]].
- **Discreteness artefacts**: pixelisation introduces a finite resolution
  scale; check that posterior subhalo masses are above the resolution
  threshold (Minor 2024/2025 on supersampling).

## See also

- [[regularization]]
- [[gravitational-imaging]]
- [[lens-equation]]
- [[mass-sheet-degeneracy]]
- [[sources-source-reconstruction]]
