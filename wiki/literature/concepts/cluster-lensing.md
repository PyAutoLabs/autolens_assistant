---
title: Cluster-scale strong lensing
type: concept
topics: [cluster-lensing]
sources:
  - StrongLensCluster/Richard2017HFFModels.pdf
  - StrongLensCluster/Atek2015HFFUV.pdf
  - StrongLensCluster/Jullo2008CosmologicalConstraints.pdf
  - Strong_Lens/Chirivi2017_Lineofsight_Clusters.pdf
  - Strong_Lens/Schneider2013SPT.pdf
status: drafted
---

# Cluster-scale strong lensing

## TL;DR

Clusters produce many multiple-image systems from background galaxies at
different redshifts. A single mass model — typically NFW or
elliptical-NFW for the smooth dark matter halo plus dozens to hundreds of
parametric profiles for member galaxies — is jointly fit to all the
constraints. The deliverable is the cluster mass map and the
magnification at every position behind it.

## What it is

- **Smooth halo(s)** — one or more NFW or PIEMD profiles for the
  cluster-scale DM.
- **Cluster members** — hundreds of small Pseudo-Jaffe / PIEMD profiles
  tied to the galaxies' luminosities via a scaling relation.
- **External + LOS structure** — necessary for the most precise models
  ([[line-of-sight-effects]]; Chirivi 2017).
- **Time-delay anchors** — when a lensed SN
  ([[lensed-supernovae|Refsdal]]) or quasar is present.

## Why it matters

- **High-z science** — clusters magnify galaxies at z > 6 by factors of
  10–100, enabling JWST observations of otherwise undetectable sources
  ([[hubble-frontier-fields]], Atek 2015).
- **Cosmography** — geometric constraints from multiple sources at
  different z_s give independent constraints on Ω_m, w (Jullo 2008,
  Caminha 2022).
- **DM physics** — cluster cores test SIDM core sizes and the
  baryon-dark-matter offset.

## Codes

- LENSTOOL (Jullo / Kneib).
- glafic (Oguri).
- MARS / Light-traces-mass approaches.
- PyAutoLens supports cluster-scale modelling but is more commonly used
  at galaxy scale.

## See also

- [[hubble-frontier-fields]]
- [[lensed-supernovae]]
- [[line-of-sight-effects]]
- [[lensed-source-science]]
- [[sources-cluster-lensing]]
