---
title: Sources — cluster lensing
type: sources
topics: [cluster-lensing]
status: drafted
---

# Sources: cluster lensing

## Richard 2017 — HFF mass models

**Reference:** Richard 2017 — HFF mass models
**Concepts:** [[hubble-frontier-fields]]
**Summary:** Public Hubble Frontier Fields mass and magnification models
from the CATS / LENSTOOL collaboration. These models became a reference
deliverable for the HFF program because they translate the imaging and
multiple-image constraints into magnification maps that downstream
high-redshift source papers could actually use.

## Atek 2015 — HFF UV LF

**Reference:** Atek 2015 — HFF UV LF
**Concepts:** [[hubble-frontier-fields]],
[[lensed-source-science]]
**Summary:** Early HFF science result using lensing magnification to push
the UV luminosity function to much fainter intrinsic galaxies at
`z ~ 6-8` than blank-field surveys could reach. The paper is a good
example of cluster lens models being used as a tool for source-population
inference, not only for cluster physics.

## Jullo 2008 — cosmological constraints

**Reference:** Jullo 2008 — cosmological constraints
**Concepts:** [[cluster-lensing]]
**Summary:** Demonstrates that a cluster with many multiply-imaged sources
at different redshifts can be used as a cosmographic probe. The core idea
is geometric: the angular-diameter-distance ratios entering the lens
equation vary with `Omega_m` and `w`, so a well-constrained cluster lens
model can in principle inform cosmology as well as mass structure.

## Harrington 2016 — Planck SL sources

**Reference:** Harrington 2016 — Planck SL sources
**Concepts:** [[cluster-lensing]],
[[lensed-source-science]]
**Summary:** Builds a sample of extremely bright high-redshift dusty
galaxies selected by Planck and followed up with Herschel and the Large
Millimeter Telescope. For this wiki, the important point is that some of
the most luminous submillimetre sources are cluster-lensed DSFGs, making
cluster lensing a route into high-redshift ISM and gas studies.

## Abedi 2026 — LEGGOS II arc magnifications

**Canonical BibTeX key:** `Abedi2026`
**Reference:** arXiv:2606.20804; doi:10.48550/arXiv.2606.20804 (submitted to ApJ)
**Concepts:** [[cluster-lensing]], [[lensed-source-science]]

**Supports:**
- The magnification of an extended arc can be computed as its image-plane area over the
  source-plane area it maps from, with the source-plane area the sum over the arc's pixels
  of pixel area divided by that pixel's magnification (their Eq. 6-7).
- The magnification of a compact clump is taken as the lens model's magnification-map
  value at the pixel containing the clump's centroid.
- Arc masks are kept on the arc's own side of the critical curve, recomputed for each
  posterior model, so that masks of separate images do not merge.
- Magnification uncertainties are estimated from the spread over 300 models drawn from
  the Lenstool MCMC posterior.
- Applied to the JWST + HST model of the cluster SDSSJ1110+6459 and its giant arc at
  z = 2.48.

**Use when:**
- Citing the area (pixel-inversion) definition of an arc's magnification, or the
  map-value magnification of a clump, in cluster or giant-arc source science.
- Motivating per-image segmentation by the critical curve and posterior-draw
  magnification errors.

**Do not use for:**
- Galaxy-scale lens modelling methodology, or claims about PyAutoLens itself (the paper
  uses Lenstool).

## See also

- [[cluster-lensing]]
- [[hubble-frontier-fields]]
