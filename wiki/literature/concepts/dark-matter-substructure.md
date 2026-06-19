---
title: Dark matter substructure from strong lensing
type: concept
topics: [dark-matter]
sources:
  - Vegetti et al. 2018 — stellar neutrinos
  - Nightingale et al. 2022 — scan method
  - Despali et al. 2022 — sensitivity
  - Despali et al. 2024 — sensitivity II
  - Gilman et al. 2019 — constraints on DM
status: drafted
---

# Dark matter substructure

## TL;DR

The CDM paradigm predicts a population of low-mass subhaloes inside
galaxy haloes that are largely invisible electromagnetically. Strong
lensing detects them via two principal techniques:

1. **[[gravitational-imaging]]** — the perturber distorts an extended arc;
   modelled directly. (Vegetti, Koopmans, Nightingale, He, Minor lines of
   work.)
2. **[[flux-ratio-anomalies]]** — the perturber alters image fluxes in a
   multiply-imaged QSO; statistical inference over the population.
   (Mao & Schneider, Dalal & Kochanek, Gilman.)

PyAutoLens implements (1); (2) is typically done with separate tooling.

## What it is

In CDM, subhaloes follow a steep mass function dN/dM ∝ M⁻¹·⁹ above
~10⁶ M_⊙. Warm or self-interacting DM ([[dark-matter-physics]]) cuts the
mass function or modifies inner densities. The strong-lensing observable
in extended-arc systems is local **convergence + flexion** from each
subhalo, with detection threshold set by data noise, source contrast, and
mass-model flexibility.

## Sensitivity and biases

- Despali 2018 / 2022 / 2024 calibrate sensitivity vs. mass, position,
  and image properties.
- Maresca 2021 warns that "unphysical" pseudo-Jaffe perturbers are
  preferred over NFW by lens data, suggesting a flexibility bias.
- LOS halos (not in the lens plane) contribute substantially
  ([[line-of-sight-effects]]; Despali 2018; He 2021).
- Mass-sheet-style degeneracies between subhalo profile and the smooth
  mass model are partially broken by spatial gradient information
  (Minor 2020 / 2021 on dark concentration).
- [[multipoles|Angular multipoles]] absorb part of what would otherwise
  be interpreted as substructure (Cohen 2024, Amvrosiadis 2025, Stacey
  2024).

## State of the art

- ~2–3 individual subhalo detections in galaxy-galaxy lenses
  (JVAS B1938+666, SDSSJ0946+1006).
- Population-level constraints from samples (Vegetti 2018; Ritondale
  2018; Enzi 2020) consistent with CDM, increasingly tight on WDM
  thermal-relic mass m_WDM > 5–6 keV.
- Forecasts for [[euclid-q1|Euclid]] / Roman / SKA show 10⁴-class samples
  → high-precision DM constraints.

## Why it matters for PyAutoLens

- PyAutoLens is one of the principal codes used for the gravitational-
  imaging detection problem ([[sources-dark-matter-substructure|Nightingale 2022, Etherington]]
  series).
- The pipeline must: include sufficient angular complexity, treat LOS
  halos, control source-regularisation systematics, and report Bayes
  factors against a "no subhalo" model.

## See also

- [[gravitational-imaging]]
- [[flux-ratio-anomalies]]
- [[multipoles]]
- [[dark-matter-physics]]
- [[line-of-sight-effects]]
- [[sources-dark-matter-substructure]]
