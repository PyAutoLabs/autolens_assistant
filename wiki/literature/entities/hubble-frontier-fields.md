---
title: Hubble Frontier Fields
type: entity
topics: [cluster-lensing, sample]
sources:
  - StrongLensCluster/Richard2017HFFModels.pdf
  - StrongLensCluster/Atek2015HFFUV.pdf
status: drafted
---

# Hubble Frontier Fields (HFF)

## What it is

A Hubble Space Telescope multi-cycle programme that obtained deep
imaging of six massive lensing clusters: Abell 2744, MACS J0416, MACS
J0717, MACS J1149, Abell S1063, Abell 370. Each was modelled by multiple
independent teams (CATS, GLAFIC, Bradac, Diego, Sharon, Williams, etc.),
yielding "all-team" mass models used for high-z source magnification.

## Key facts

- Each cluster has hundreds of multiple-image constraints, including
  spectroscopic confirmations from MUSE.
- Used to probe galaxies at z ~ 6–10 via cluster magnification (Atek
  2015 on UV luminosity functions).
- MACS J1149 hosted [[lensed-supernovae|SN Refsdal]].

## Why it matters for PyAutoLens

PyAutoLens supports cluster modelling (parametric profile + many
members), though more specialised codes (LENSTOOL, glafic) dominate
practice. HFF-style high-multiplicity constraints are an excellent
testbed.

## See also

- [[cluster-lensing]]
- [[lensed-supernovae]]
- [[lensed-source-science]]
- [[sources-cluster-lensing]]
