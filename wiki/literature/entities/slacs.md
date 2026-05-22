---
title: SLACS (Sloan Lens ACS Survey)
type: entity
topics: [survey, sample]
sources:
  - Strong_Lens/Shu2012SLACSXII.pdf
  - Strong_Lens/Shu2018SLACS4Mass.pdf
  - Strong_Lens/Sonnenfeld2024SlacsDebiased.pdf
  - Strong_Lens/Sonnefendl2025SLACSDebiadedII.pdf
status: drafted
---

# SLACS — Sloan Lens ACS Survey

## What it is

A spectroscopically-selected sample of ~85–100 galaxy-galaxy strong
lenses found by scanning SDSS spectra of luminous red galaxies for
emission lines at a discrepant redshift, then confirming with HST/ACS
imaging. The defining strong-lens sample for the 2000s–2010s.

## Key facts

- Lenses are massive ellipticals at z_l ~ 0.1–0.4.
- Sources are typically [OII] emitters at z_s ~ 0.5–1.
- Einstein radii ~ 0.5–1.5″.
- Mass profile: very close to isothermal at θ_E, ⟨γ⟩ ~ 2.08.
- Used for the canonical [[bulge-halo-decomposition]] and IMF studies.

## Selection bias

The spectroscopic selection prefers high-σ galaxies with bright,
compact, blue sources — heavily biased ([[selection-effects]];
Sonnenfeld 2023/2024/2025 series).

## Why it matters for PyAutoLens

SLACS lenses are the standard benchmark sample. Most of the
Etherington / Nightingale PyAutoLens development was tested on SLACS-like
data. The Shu/Bolton parametric models are the reference comparison.

## See also

- [[bells-gallery]]
- [[selection-effects]]
- [[bulge-halo-decomposition]]
- [[sources-lens-statistics]]
