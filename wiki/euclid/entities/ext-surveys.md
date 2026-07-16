---
title: EXT surveys (ground-based optical data in Euclid)
type: entity
topics: [survey, ground]
sources:
  - Miyazaki et al. 2018 — Miyazaki2018
  - Ibata et al. 2017 — Ibata2017
  - Chambers et al. 2016 — Chambers2016
  - Abbott et al. 2021 — Abbott2021
  - Euclid Collaboration - Romelli et al. 2025 — Q1-TP004
status: drafted
---

# EXT surveys — the ground-based optical component of Euclid data

## What it is

Euclid's own bands stop at one broad optical filter, so multi-band optical
photometry comes from external ("EXT") ground surveys merged into the Euclid
catalogues by the MER processing function (Romelli et al. 2025, `Q1-TP004`).

## Key facts

- **Northern hemisphere:** Subaru Hyper Suprime-Cam for g and z (Miyazaki et al.
  2018, `Miyazaki2018`); the Canada–France Imaging Survey for u and r (Ibata et
  al. 2017, `Ibata2017`); Pan-STARRS for i (Chambers et al. 2016, `Chambers2016`).
- **Southern hemisphere:** the Dark Energy Survey in griz (Abbott et al. 2021,
  `Abbott2021`).
- EXT imaging is much lower resolution than [[vis]] — typically ~1" seeing vs
  0.16" — so lens modeling on EXT bands always holds the VIS model fixed
  (`euclid_strong_lens_modeling_pipeline:scripts/lens_model_waveband.py`) and
  photometry across bands needs [[psf-homogenisation]].
- Per-band PSFs for EXT data are target-specific just like Euclid's own
  ([[euclid-psf]]).

## See also

- [[nisp]], [[euclid-photo-z]], [[psf-homogenisation]]
