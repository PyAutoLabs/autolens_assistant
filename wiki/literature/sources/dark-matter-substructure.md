---
title: Sources — dark matter substructure
type: sources
topics: [dark-matter]
status: drafted
---

# Sources: dark matter substructure

Per-paper stubs of substructure-detection literature. All marked stub.

## Vegetti & Koopmans 2009 — adaptive grids + nested sampling

**File:** https://arxiv.org/abs/0805.0201 (MNRAS 392, 945)
**Concepts:** [[dark-matter-substructure]], [[gravitational-imaging]],
[[source-reconstruction]], [[bayesian-inference-lensing]]
**Status:** drafted

**Summary (drafted):** Vegetti & Koopmans introduce the **adaptive,
Bayesian, grid-based gravitational-imaging framework** for objectively
detecting substructure in galaxy-scale lenses. Three core ingredients
distinguish this paper from Koopmans 2005:

1. The source-plane discretisation is **adaptive** — a Delaunay
   tessellation built by lens-mapping a regular image-plane grid back
   to the source plane, so source pixels naturally cluster where the
   lens model says signal lives.
2. The regularisation strength on both the source and the potential
   correction is selected by **Bayesian evidence** (in the Suyu 2006
   sense), so the user does not tune it manually.
3. A **nested-sampling** sweep over the non-linear mass-model
   parameters returns the full evidence Z, allowing **objective
   model ranking** between smooth-only and smooth + perturber models.

The paper validates the method on a suite of simulated lens systems —
one smooth-only system, twelve systems with a single NFW perturber at
varying masses and positions, one system with two NFW perturbers.
Recovery is demonstrated down to ~10⁷ M_⊙ for perturbers on the
Einstein ring, ~10⁹ M_⊙ for perturbers off the ring. The framework
became the production method behind the Vegetti / Nightingale subhalo
searches in real SLACS / BELLS data (Vegetti 2010, 2012; Ritondale 2018;
Nightingale 2022) and is the algorithm that PyAutoLens'
subhalo-scanning workflow generalises. **Cite this paper when invoking
evidence-based substructure detection.**

## Vegetti 2018 — sterile-neutrino constraints

**File:** `Substructure/Vegetti2018StellarNeutrinos.pdf`
**Concepts:** [[dark-matter-substructure]], [[dark-matter-physics]]
**Summary:** Combined sample analysis using gravitational
imaging; constrains the sterile-neutrino / thermal-relic warm-DM mass.

## Nightingale 2022 — PyAutoLens subhalo scan

**File:** `Substructure/Nightingale2022Scanm.pdf`
**Concepts:** [[gravitational-imaging]], [[pyautolens]]
**Summary:** Subhalo scanning methodology in PyAutoLens applied
to a sample of galaxy-galaxy lenses; statistical population constraints
on subhalo abundance.

## Despali 2018 — baryons on substructure

**File:** `Substructure/Despali2018BaryonsonSub.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Hydrodynamical simulations show baryons modify
subhalo populations relative to DM-only predictions.

## Despali 2018 — LOS

**File:** `Substructure/Despali2018LOS.pdf`
**Concepts:** [[line-of-sight-effects]],
[[dark-matter-substructure]]
**Summary:** Quantifies the fraction of detected perturbers in
strong lenses that are LOS halos rather than in-lens subhaloes.

## Despali 2021 — sensitivity

**File:** `Substructure/Despali2021Senstitoty.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Forward-model sensitivity study for subhalo
detection.

## Despali 2022 — sensitivity

**File:** `Strong_Lens/Despali2022Sensitivity.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Updated detection-sensitivity grids for subhaloes
across mass, position, and noise levels.

## Despali 2024 — sensitivity II

**File:** `Substructure/Despali2024SensitivityII.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Continuation of the Despali sensitivity series with
updated forward modelling.

## Amorscio 2022 — sensitivity

**File:** `Strong_Lens/Amorscio2022Sensiti.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Sensitivity / forecast paper. Filename misspelled —
verify author (likely Amorisco).

## He 2017 — substructure halos vs globular clusters

**File:** `Strong_Lens/He2017_Substructure_Halos_vs_Globs.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Argues that lensing perturbers may include globular
clusters as well as DM subhaloes.

## He 2022 — preprint

**File:** `Strong_Lens/He2022Preprint.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Substructure-related paper whose exact angle needs the PDF,
but it sits in the perturber-identification and detection-methods part
of the literature.

## Loudas 2022 — millilensing

**File:** `Substructure/Loudas2022MiliLensing.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Mas-scale "millilensing" by DM subhaloes in radio
lenses.

## Ran Li 2016 — substructure

**File:** `Strong_Lens/RanLi2016Sub.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Substructure inference paper.

## Ran Li 2016 — substructure II

**File:** `Strong_Lens/RanLi2016Sub2.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Companion paper.

## Diaz-Rivero 2019 — subhalo without lens model

**File:** `Strong_Lens/Rivero2019DirectSubhaLoCircumventLensmodel.pdf`
**Concepts:** [[dark-matter-substructure]],
[[deep-learning-lensing]]
**Summary:** Direct subhalo-population inference that bypasses
the per-lens mass model — population-level statistics from arc residuals.

## Ritondale 2018 — BELLS subhaloes

**File:** `Substructure/Ritondale2018BELLS.pdf`
**Concepts:** [[bells-gallery]],
[[dark-matter-substructure]]
**Summary:** Subhalo search in BELLS-GALLERY sample.

## Ritondale 2018 — Lyman-α

**File:** `Substructure/Ritondale2018BELLLymaAlphs.pdf`
**Concepts:** [[bells-gallery]],
[[lensed-source-science]]
**Summary:** Lyman-α emission from BELLS-GALLERY sources.

## Sawala 2016 — the chosen few

**File:** `Substructure/Sawala2016TheChosenFew.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** N-body / hydro simulations exploring which subhaloes
host galaxies — calibrates the lensing-DM-galaxy connection.

## Benitez 2020 — detailed structure of halos

**File:** `Substructure/Benitez2020DetailedstructureHalos.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Detailed-structure simulations relevant to lensing
subhalo predictions.

## Minor 2020 — DM concentration of J0946

**File:** `Strong_Lens/Minor2020DMConcentration0946.pdf`
**Concepts:** [[dark-matter-substructure]]
**Summary:** Mass-concentration of the perturber in SDSSJ0946.

## Minor 2021 — DM concentration

**File:** `Strong_Lens/Minor2021DMConcentration.pdf`
**Concepts:** [[dark-matter-substructure]],
[[dark-matter-physics]]
**Summary:** Constrains the perturber's c-M relation; J0946
appears overconcentrated for CDM.

## See also

- [[dark-matter-substructure]]
- [[gravitational-imaging]]
