---
title: COSMOS-Web Ring
type: entity
topics: [specific-lens, jwst]
sources:
  - Mercier et al. 2024 — COSMOS Ring
  - Nightingale et al. 2025 — COWLS I
status: drafted
---

# COSMOS-Web Ring

## What it is

A near-complete Einstein ring discovered in the JWST/NIRCam imaging of the
COSMOS-Web survey (GO #1727) and characterised in depth by Mercier et al.
2024 (A&A 687, A61; arXiv:2309.15986). A massive, compact, quiescent
elliptical galaxy at z ≈ 2 lenses a star-forming galaxy at z ≈ 5 into an
almost circular ring. It is catalogued as **COSJ100024+015334** and is one of
the lenses of the COSMOS-Web Lens Survey (COWLS; Nightingale et al. 2025,
COWLS I, arXiv:2503.08777), which found over 100 strong-lens candidates in
the 0.54 deg² of contiguous COSMOS-Web imaging.

It is the example lens that ships with this assistant
(`dataset/imaging/cosmos_web_ring/`) and with `autolens_workspace`
(`scripts/imaging/start_here.py`).

## Key facts

- **Imaging:** JWST/NIRCam in four bands, F115W, F150W (0.03"/px) and F277W,
  F444W (0.06"/px); all four are bundled under
  `dataset/imaging/cosmos_web_ring/wavebands/`. The ring has the same shape
  and radius in every band: lensing is achromatic.
- **Redshifts:** lens z = 2.02 ± 0.02 (photometric; Mercier 2024 adopt
  z_lens = 2.00 ± 0.02 for masses). Mercier 2024 give three photometric
  source solutions, z_source = 5.48 ± 0.06 (LePhare, their reference),
  5.27 ± 0.02 (Cigale) and 5.08 ± 0.05 (EAZY). The bundled `info.json`
  uses z_lens = 2.0 and z_source = 5.1043.
- **Einstein radius (Mercier 2024, Table 3):** θ_Ein = 0.78 ± 0.04"
  (`sl_fit`, the reference value) and 0.77 ± 0.01" (PyAutoLens).
- **Enclosed mass (Mercier 2024):** M_tot(<θ_Ein) = (3.66 ± 0.36) × 10¹¹ M_⊙
  for z_source = 5.48, rising to (3.84 ± 0.38) × 10¹¹ M_⊙ for z_source = 5.08
  (`sl_fit`); the PyAutoLens values are 3.56–3.73 × 10¹¹ M_⊙. Stellar mass
  M_⋆ = 1.37 (+0.14/−0.11) × 10¹¹ M_⊙; the total mass implies a dark-matter
  halo of ~10¹³ M_⊙.

## This assistant's reference fit

`scripts/cosmos_web_ring/fit_cosmos_web_ring.py` fits the F444W imaging with
an MGE lens light, an isothermal mass plus external shear and an MGE source
using `MultiStartProdigy` (a maximum-likelihood point estimate with no error
bars). The numbers, figures and provenance are in
[`scripts/cosmos_web_ring/results/README.md`](../../../scripts/cosmos_web_ring/results/README.md).

- Isothermal `einstein_radius` = **0.80"**; the effective Einstein radius of
  the tangential critical curve (mass plus shear) = **0.77"**, the quantity
  Mercier 2024 quote. The effective value agrees with Mercier's 0.77–0.78" to
  within 0.01"; the isothermal parameter is 0.02–0.03" (about 3%) larger,
  which is within their `sl_fit` uncertainty (± 0.04") and reflects the
  different definition, not a disagreement.
- Enclosed mass ≈ 3.9 × 10¹¹ M_⊙ (effective radius, Planck15, z_source =
  5.1043), inside Mercier's range for z_source ≈ 5.1: about 400 billion Suns.
- The F277W fit with the same model gives the same Einstein radius within
  a few hundredths of an arcsecond (see the results README).

## See also

- [[lensed-source-science]]
- [[sources-specific-lenses]]
- [[lens-finding]]
