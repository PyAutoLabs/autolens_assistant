---
title: Lensed supernovae
type: concept
topics: [cosmology, transients]
sources:
  - Goobar et al. 2016 — Multi Im Super Nova
  - Grillo et al. 2018 — Refsdel Ho
  - Ryberg et al. 2018 — Strong Lens Supernova Redshift7
status: drafted
---

# Lensed supernovae

## TL;DR

Multiply-imaged supernovae are the cleanest [[time-delay-cosmography|time-delay
cosmography]] probe: the light curve is well characterised, the source is
effectively a point, and the time delay can be measured directly.
SN Refsdal (2014, behind MACS J1149) was the first. iPTF16geu (Goobar
2016) and several JWST-era detections have followed. Roman is expected
to find hundreds.

## What they are

- **SN Refsdal** — Type II behind a cluster member, in a cluster lens
  ([[hubble-frontier-fields|HFF]] field). The predicted-and-observed
  reappearance was a benchmark for cluster lens models
  ([[sources-lensed-supernovae|Grillo 2018]]).
- **iPTF16geu** — Type Ia at z = 0.4, lensed by a galaxy at z = 0.2,
  microlensed and ~50× magnified.
- **SN Requiem / SN H0pe / SN Encore** — JWST-era cluster-lensed
  supernovae.
- **High-z lensed SN** — Ryberg 2018 predicts strongly-lensed SNe
  detectable to z ~ 7 in upcoming surveys.

## Why they matter

- Time delays from SNe are measured more cleanly than from quasars
  (no microlensing variability of the source itself, no AGN intrinsic
  variability biases).
- Cluster-lensed Type Ia SNe can be used as **standard candles behind
  lenses** — independent check of magnification and the
  [[mass-sheet-degeneracy]].
- Sample size in LSST/Roman era → competitive H0.

## Why it matters for PyAutoLens

PyAutoLens supports time-varying sources in the forward model. Users
modelling cluster-lensed SNe combine imaging + time delays + source
spectroscopy in the same hierarchical inference. Cluster lensing models
require dozens of mass components; pipelines like SLaM scale poorly here
— see [[cluster-lensing]].

## See also

- [[time-delay-cosmography]]
- [[cluster-lensing]]
- [[hubble-frontier-fields]]
- [[sources-lensed-supernovae]]
