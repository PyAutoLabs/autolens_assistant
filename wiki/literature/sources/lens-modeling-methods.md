---
title: Sources — lens modelling methods
type: sources
topics: [lens-modelling, methods]
status: drafted
---

# Sources: lens modelling methods

Bibliography of papers describing forward-model formulations, pipelines,
and analytic methods.

## Birrer 2018 — lenstronomy code paper

**Reference:** Birrer 2018 — lenstronomy code paper
**Concepts:** [[mass-models]], [[source-reconstruction]], [[lenstronomy]]
**Summary:** Introduces `lenstronomy`, a
Python framework for strong-lens modelling. Implements an extensive
profile library, multi-plane lensing, pixelated source reconstruction,
and the Bayesian-evidence formalism. Together with PyAutoLens, one of
the two main community modelling codes.

## Birrer 2018 — lenstronomy companion / kinematics

**Reference:** Birrer 2018 — lenstronomy companion / kinematics
**Concepts:** [[lenstronomy]], [[kinematics-and-lensing]]
**Summary:** Follow-up `lenstronomy` paper extending the framework toward
joint lensing-and-kinematics applications and companion-methods use
cases.

## Nightingale 2015 — adaptive SLI (foundational PyAutoLens)

**Reference:** https://arxiv.org/abs/1412.7436 (MNRAS 452, 2940)
**Concepts:** [[source-reconstruction]], [[pyautolens]], [[mass-models]]
**Status:** drafted

**Summary (drafted):** Nightingale & Dye introduce **adaptive Semi-Linear
Inversion (SLI)** — the source-plane reconstruction kernel that became
PyAutoLens. The "semi-linear" half (after Warren & Dye 2003) solves for
the source-pixel intensities as a linear least-squares problem given the
lens model; the "adaptive" half is the original contribution: an
h-means clustering algorithm builds the source-plane pixel grid *from
the lens-model magnification map at each likelihood evaluation*, so the
discretisation tracks where the source actually has signal. Every
likelihood evaluation gets a fresh random-initialised pixelisation, so
the source grid is no longer a fixed nuisance parameter biasing
posteriors.

The paper compares adaptive SLI against fixed-grid SLI on simulated
singular-power-law ellipsoid lenses and shows: (a) adaptive SLI fixes
the number of degrees of freedom so the optimisation isn't gamed by
grid-resolution choice; (b) it averages over the discretisation
systematics that contaminate fixed-grid fits; (c) for highly degenerate
SPLE posteriors, it samples the full posterior with a single
non-linear search where fixed-grid methods need bespoke chaining.

This is the foundational paper for what eventually became
PyAutoLens' [[gravitational-imaging|pixelised-source]] inversion. Cite
this when a fork uses any of the PyAutoLens adaptive Delaunay /
Voronoi / brightness-based pixelisations, or when explaining why
PyAutoLens' source-plane discretisation is decoupled from the
likelihood evaluation count.

## Nightingale 2018 — AutoLens code paper

**Reference:** https://arxiv.org/abs/1708.07377 (MNRAS 478, 4738)
**Concepts:** [[pyautolens]], [[bulge-halo-decomposition]],
[[source-reconstruction]]
**Status:** drafted

**Summary (drafted):** Nightingale, Dye & Massey introduce **AutoLens**,
the first fully automated galaxy-scale strong-lens modelling pipeline.
AutoLens simultaneously fits the lens galaxy's light (superposition of
Sérsic profiles), mass (single-component or decomposed bulge + halo),
and the source galaxy on an adaptive pixelised grid (per Nightingale &
Dye 2015), running entirely without user intervention. Model complexity
— including whether the lens light and mass are geometrically aligned —
is chosen automatically by Bayesian model comparison ([[bayesian-inference-lensing]]).

The paper validates AutoLens on a large suite of simulated images
spanning lens-profile shapes, source morphologies, and lensing
geometries, demonstrating accurate light, mass, and source recovery
across data quality representative of HST and Euclid. The bulge–halo
decomposition is shown to recover the geometric alignment between
luminous and dark mass when present, a measurement subsequent work
(Etherington 2022 below) generalised across the SLACS-like sample.

This is the PyAutoLens **code paper for galaxy-scale modelling** —
i.e. the paper that justifies citing PyAutoLens in a methods section.
The 2021 JOSS paper (Nightingale 2021 below) is the citation for the
software *package* itself; this 2018 paper is for the modelling
*methodology* the package implements.

## Nightingale 2021 — PyAutoLens (JOSS)

**Reference:** https://arxiv.org/abs/2106.01384 (JOSS 6(58), 2825)
**Concepts:** [[pyautolens]], [[pyautofit]]
**Status:** drafted

**Summary (drafted):** The Journal of Open Source Software paper for
PyAutoLens. Concise software-citation paper covering scope, features
(automated modelling, imaging + interferometer support, simulators,
HowToLens tutorials), and dependencies (the PyAuto\* stack — PyAutoNerves,
PyAutoArray, PyAutoFit, PyAutoGalaxy). Authors: Nightingale, Hayes,
Kelly, Amvrosiadis, Etherington, He, Li, Cao, Frawley, Cole, Enia,
Frenk, Harvey, Li, Massey, Negrello, Robertson.

This is the **software citation** for PyAutoLens — what a fork's
methods section uses when introducing the package: "We use PyAutoLens
(Nightingale et al. 2021)…". The 2018 AutoLens paper is the
methodology citation for the underlying lens-modelling pipeline; this
JOSS paper is the citation for the software itself.

## Etherington 2022 — automated galaxy-galaxy modelling (SLaM)

**Reference:** https://arxiv.org/abs/2202.09201 (MNRAS 517, 3275)
**Concepts:** [[slam-pipeline]], [[pyautolens]], [[bulge-halo-decomposition]]
**Status:** drafted

**Summary (drafted):** Etherington et al. describe the **Strong Lens
Automated Modelling (SLaM) pipeline** — the chained-search workflow that
takes a user from raw HST imaging to a converged composite mass model
without intervention. Demonstrates "no lens left behind" on a 59-lens
HST sample: every lens is successfully modelled at ~1% Einstein-radius
measurement precision out to z ≈ 0.7, with the paper documenting the
small-handful failure modes and the pipeline adjustments that recover
them.

The pipeline phases — lens-light subtraction → SIE + parametric source
→ EPL + parametric source → EPL + pixelised source → composite (Sérsic
+ NFW) + pixelised source, with optional multipole and subhalo-scan
phases — pass posteriors as priors via PyAutoFit search chaining. The
paper argues that automated modelling is essential for the
hundred-thousand-lens samples anticipated from Euclid and beyond, where
labour-intensive per-lens modelling does not scale.

This is the **canonical SLaM citation**. Forks that run
`scripts/imaging.py` against the SLaM template are running the pipeline
this paper validates. PyAutoLens is also installed in the ESA Euclid
mission's Science Data Centre as a result of this work.

## Etherington 2022 (BulgeHalo) — beyond the bulge-halo conspiracy

**Reference:** https://arxiv.org/abs/2207.04070 (MNRAS 517, 3275)
**Concepts:** [[bulge-halo-decomposition]], [[pyautolens]],
[[radial-angular-degeneracy]]
**Status:** drafted

**Summary:** Companion paper to the SLaM modelling release.
Decomposes mass into stellar bulge (constrained by lens light) and
dark-matter halo for the 59-lens HST sample, testing whether the
near-isothermal total density profile (the "bulge-halo conspiracy") is
maintained at HST resolution. The paper finds departures from
isothermality that the smooth power-law model masks, with implications
for stellar-population and IMF studies.

## Anowar 2020 — lens modelling study

**Reference:** Anowar 2020 — lens modelling study
**Concepts:** [[mass-models]]
**Summary:** Lens-modelling methodology and case-study paper focused on
practical model construction and comparison.

## Du 2019 — analytic lensing

**Reference:** Du 2019 — analytic lensing
**Concepts:** [[lens-equation]], [[mass-models]]
**Summary:** Analytic or semi-analytic lensing results, most likely
closed-form deflections for a specific profile family.

## Holloway 2024 — JWST forecasts

**Reference:** Holloway 2024 — JWST forecasts
**Concepts:** [[pyautolens]], [[dark-matter-substructure]]
**Summary:** Forecasts what JWST imaging buys for lens modelling
and substructure detection.

## Holloway 2024 — Bayesian lens finding

**Reference:** Holloway 2024 — Bayesian lens finding
**Concepts:** [[lens-finding]], [[bayesian-inference-lensing]],
[[pyautolens]]
**Summary:** Uses PyAutoLens lens-model Bayesian evidence as a
lens-finding criterion in DES — folding modelling into discovery.

## Tessore 2015 — lensed images of power-law ellipsoids

**Reference:** Tessore 2015 — lensed images of power-law ellipsoids
**Concepts:** [[mass-models]]
**Summary:** Analytic / semi-analytic deflection field for
elliptical power-law mass profiles via hypergeometric functions —
foundational for fast EPL evaluation in modelling codes.

## Tessore 2016 — elliptical power-law

**Reference:** Tessore 2016 — elliptical power-law
**Concepts:** [[mass-models]]
**Summary:** Follow-up to Tessore 2015; extends the power-law
deflection formalism. Used by PyAutoLens, lenstronomy, etc.

## Maresca 2021 — unphysical perturbers

**Canonical BibTeX key:** `Maresca2021`
**Reference:** MNRAS 503, 2229--2241; arXiv:2012.04665; doi:10.1093/mnras/stab387
**Concepts:** [[gravitational-imaging]], [[dark-matter-substructure]]

**Supports:**
- Incorrectly initialised lens models can produce unphysical source
  reconstructions in semi-analytic strong-lens modelling.
- CNN-based checks can catch those reconstructions and re-initialise the
  lens model automatically, reducing the rate of unphysical source
  reconstructions.

**Use when:**
- Justifying automated quality-control steps for lens-model fits and
  source reconstructions.

**Do not use for:**
- Claims about subhalo mass profiles or perturber physics.

## Tan 2024 — strong-lens slope

**Reference:** Tan 2024 — strong-lens slope
**Concepts:** [[mass-models]], [[radial-angular-degeneracy]]
**Summary:** Recent study of the recovered mass-density slope γ
under various model assumptions.

## Melo 2024 — AutoLens MGE

**Reference:** Melo 2024 — AutoLens MGE
**Concepts:** [[mass-models]], [[pyautolens]]
**Summary:** Implementation and validation of Multi-Gaussian
Expansion mass profiles in PyAutoLens.

## See also

- [[sources-mass-models]]
- [[sources-source-reconstruction]]
- [[mass-models]]
