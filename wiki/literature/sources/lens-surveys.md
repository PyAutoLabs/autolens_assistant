---
title: Sources — lens surveys
type: sources
topics: [surveys, samples]
status: drafted
---

# Sources: lens surveys

Founding papers for the three lens surveys most often referenced in
PyAutoLens fits. Each paragraph identifies the survey-defining
publication, its selection method, and what a fork user gets when they
load data from it.

## Bolton 2006 — SLACS-I

**File:** https://arxiv.org/abs/astro-ph/0511453 (ApJ 638, 703)
**Concepts:** [[slacs]], [[lens-finding]]
**Status:** drafted

**Summary:** The founding SLACS (Sloan Lens ACS) paper. Defines the
spectroscopic selection method — scan SDSS galaxy spectra for nebular
emission lines at a redshift discrepant from the target's, then confirm
with HST/ACS snapshot imaging. Reports the first 19 confirmed galaxy-scale
lenses out of 28 observed candidates (>68% efficiency). The SLACS sample
grew through subsequent papers to ~85–100 lenses and is the standard
benchmark for galaxy-scale strong-lens modelling — including the bulk of
Nightingale / Etherington PyAutoLens development. When a fork user says
"I have SLACS imaging," this is the paper that defines what SLACS *is*.

## Brownstein 2012 — BELLS-I

**File:** https://arxiv.org/abs/1112.3683 (ApJ 744, 41)
**Concepts:** [[bells-gallery]], [[lens-finding]]
**Status:** drafted

**Summary:** The founding BELLS (BOSS Emission-Line Lens Survey)
paper. Extends the SLACS spectroscopic-selection methodology to higher
redshift (z_l ≈ 0.4–0.7) using BOSS spectra instead of SDSS-I/II. Reports
25 definite + 11 probable lenses from the first six months of BOSS data,
confirmed with HST/ACS imaging. BELLS-GALLERY (Shu 2016) is the Lyman-α-
emitter sub-sample of this survey. BELLS combined with SLACS gives the
redshift baseline for early-type galaxy structural evolution studies, and
the BELLS sample is heavily used in substructure-detection work (e.g.
Ritondale 2018 in `sources/dark-matter-substructure.md`).

## Suyu 2017 — H0LiCOW-I

**File:** https://arxiv.org/abs/1607.00017 (MNRAS 468, 2590)
**Concepts:** [[h0licow]], [[time-delay-cosmography]], [[hubble-tension]]
**Status:** drafted

**Summary:** Program-overview paper for H0LiCOW (H₀ Lenses in
COSMOGRAIL's Wellspring), a multi-institution collaboration measuring H₀
from time-delay distances in five quadruply-imaged quasar lens systems
(B1608+656, RXJ1131-1231, HE0435-1223, WFI2033-4723, HE1104-1805). The
five-lens result was extended to six lenses in Wong et al. 2019, giving
H₀ = 73.3 ± 1.7 km/s/Mpc — a ~3σ tension with Planck under ΛCDM. This is
the paper to cite when a fork's time-delay-cosmography work invokes the
H0LiCOW methodology; the [[tdcosmo|TDCOSMO]] successor relaxes the
power-law assumption made here.

## See also

- [[slacs]], [[bells-gallery]], [[h0licow]] — entity pages for each
  survey.
- [[time-delay-cosmography]], [[lens-finding]] — relevant concepts.
- [`wiki/literature/sources/lens-finding.md`](./lens-finding.md) — broader
  lens-finding methodology bibliography.
