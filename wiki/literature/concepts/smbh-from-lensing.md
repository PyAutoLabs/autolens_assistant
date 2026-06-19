---
title: Supermassive black holes from strong lensing
type: concept
topics: [smbh, dark-matter]
sources:
  - Nightingale et al. 2023 — SMBH
  - Spingola et al. 2019 — SMBHVLBI
  - Banik et al. 2019 — SMBH Razor Arc
  - Chen et al. 2018 — SMBH
status: drafted
---

# Supermassive black holes from strong lensing

## TL;DR

A central SMBH adds a sharp point-mass deflection on top of the smooth
galaxy potential. Its main observable signatures are:

- A **central demagnified image** at the SMBH location (rare; sometimes
  called the "core image").
- Local **arc perturbations** near the centre.
- VLBI-detectable astrometric shifts in radio-loud lensed AGN
  (Spingola 2019).

Nightingale 2023 placed an upper limit on the SMBH mass in Abell 1201 by
absence of a central image; Chen 2018 develops the central-image
methodology.

## What it is

- The point-mass adds a radial deflection ∝ M_BH / θ that diverges at the
  centre, producing a logarithmic time-delay and a demagnified central
  image whose flux scales with the central density slope.
- The "Razor Arc" / "Mothra" geometry (Banik 2019) maximises sensitivity
  to perturbers near a critical curve.

## Why it matters for PyAutoLens

PyAutoLens can include a point-mass profile at the centre of the smooth
lens. For SMBH searches, the analysis is:

1. Best-fit model **without** SMBH.
2. Add point-mass profile; refit.
3. Compute Bayes factor; upper limit when M_BH = 0 is preferred.

This is mechanically the same as [[gravitational-imaging|subhalo
scanning]] but constrained to the centre.

## See also

- [[gravitational-imaging]]
- [[abell-1201]]
- [[sources-smbh-vlbi]]
