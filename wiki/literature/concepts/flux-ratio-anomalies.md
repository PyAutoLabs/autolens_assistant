---
title: Flux-ratio anomalies
type: concept
topics: [dark-matter, methods]
sources:
  - Strong_Lens/Gilman2018ProbeNatureDMForwardModel.pdf
  - Strong_Lens/Gilman2019ConstraintsDM.pdf
  - Strong_Lens/Gilman2016FluxMethod.pdf
  - Strong_Lens/CyrRacine2018SLMany.pdf
status: drafted
---

# Flux-ratio anomalies

## TL;DR

In a smooth lens model, magnifications of multiply-imaged compact sources
(lensed quasars) satisfy "magnification relations" that fail when small
perturbers are present. The deviation — a flux-ratio anomaly — is a
population-level probe of dark matter on ~10⁶–10⁹ M_⊙ scales. Gilman et
al. developed a forward-modelling Bayesian pipeline that delivers
competitive WDM and thermal-relic constraints from samples of lensed
quasars.

## What it is

- The standard four-image (quad) lens has image magnifications constrained
  by parity and the local Jacobian of the smooth model
  ([[lens-equation]]). A perturber alters the local Jacobian and breaks
  the relation.
- Microlensing by lens stars muddles the radio-optical comparison; radio
  / mid-IR (dust-emission) fluxes are preferred because they probe
  larger source sizes immune to microlensing.
- Hsueh 2016/2017/2018 ("Disk Substruct" series) warn that **baryonic
  disks** in lens galaxies also produce flux anomalies — a confounder for
  DM-substructure inference.

## Inference

Gilman pipeline:

1. Forward-simulate lensed quasars with realisations of a (sub-)halo
   population (mass function, c-M relation, LOS, baryonic disk).
2. Compute magnifications.
3. Approximate Bayesian computation / NN-based density-estimation to
   constrain DM-population parameters.

## Why it matters for PyAutoLens

PyAutoLens is principally an extended-arc code; the flux-ratio probe
typically uses separate tools. But the underlying physics — the lens
equation, perturber profiles, source models — is shared. Users
cross-comparing the two channels need to keep mass-model assumptions
consistent.

## See also

- [[dark-matter-substructure]]
- [[gravitational-imaging]]
- [[multipoles]]
- [[sources-flux-ratios]]
