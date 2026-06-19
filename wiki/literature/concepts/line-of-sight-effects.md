---
title: Line-of-sight effects
type: concept
topics: [systematics, environment]
sources:
  - He et al. 2021 — Lo S
  - Despali et al. 2018 — LOS
  - Fleury et al. 2022 — Los Shear
status: drafted
---

# Line-of-sight (LOS) effects

## TL;DR

Halos and groups along the line of sight perturb the lensing signal
beyond the leading external-convergence + shear terms. Their cumulative
effect is significant for both [[time-delay-cosmography|H0]] and
[[dark-matter-substructure|substructure inference]].

## What they are

- **Leading order** — uniform [[external-convergence-shear|κ_ext, γ_ext]].
- **Tidal / flexion terms** — produce small distortions in arcs; Fleury
  2022.
- **Discrete halos** — individual LOS halos can mimic subhaloes in the
  lens plane. Despali 2018 quantified the contamination: a substantial
  fraction (often ~30–50%) of detected "perturbers" in deep imaging
  surveys are LOS halos.
- **Multi-plane ray tracing** — properly accounts for non-additive
  effects; standard in cluster lensing
  ([[cluster-lensing|Chirivi 2017]]).

## Why it matters for PyAutoLens

- Substructure inference must explicitly model LOS halos or marginalise
  over their abundance ([[gilman-pipeline|Gilman pipelines]], Despali
  2024).
- Time-delay cosmography requires κ_ext priors from LOS counting (see
  [[h0licow]], [[tdcosmo]]).
- PyAutoLens supports multi-plane tracers; the user must decide whether
  to use single-plane + κ_ext or full multi-plane.

## See also

- [[external-convergence-shear]]
- [[dark-matter-substructure]]
- [[time-delay-cosmography]]
- [[sources-external-shear-los]]
