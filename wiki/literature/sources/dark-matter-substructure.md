---
title: Sources — dark matter substructure
type: sources
topics: [dark-matter]
status: drafted
---

# Sources: dark matter substructure

Per-paper entries for substructure-detection literature. Round 8 (2026-05-22)
expanded the previously thin one-liners against arXiv for 17 entries.

## Vegetti & Koopmans 2009 — adaptive grids + nested sampling

**Reference:** https://arxiv.org/abs/0805.0201 (MNRAS 392, 945)
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

**Reference:** arXiv:1801.01505
MNRAS 481, 3661)
**Authors:** Vegetti, Despali, Lovell, Enzi
**Concepts:** [[dark-matter-substructure]], [[dark-matter-physics]]
**Summary:** Combines the detected subhalo + line-of-sight halo counts from
gravitational imaging across 11 SLACS lenses to constrain the
free-streaming scale of resonantly-produced sterile-neutrino dark matter.
Folding in the [[line-of-sight-effects]] contribution (per Despali 2018)
they derive a 2σ upper limit `log M_hm[M⊙] < 12.0`, equivalent to a
thermal-relic mass `m_th > 0.3 keV`, which excludes sterile-neutrino
models with `m_s < 0.8 keV` at any lepton-asymmetry parameter `L_6`.
The companion lensing-properties paper is Despali et al. 2020
(arXiv:1907.06649). Cite alongside Ritondale 2018 (BELLS) for the
combined-sample CDM consistency story.

## Nightingale 2022 — PyAutoLens subhalo scan

**Reference:** arXiv:2209.10566
MNRAS 527, 10480)
**Authors:** Nightingale, He, Cao, Etherington, Li, Frenk, et al.
**Concepts:** [[gravitational-imaging]], [[pyautolens]],
[[slam-pipeline]]
**Summary:** Defines and executes a near-automated subhalo scan over 54
strong lenses from the [[slacs]] and [[bells-gallery]] samples using
PyAutoLens — 28 of them analysed for substructure for the first time.
The pipeline builds on the Etherington 2022 SLaM modelling pass, then
runs an evidence-thresholded grid scan for an NFW perturber across the
image plane of every lens, reporting both detection candidates and
sensitivity maps. The paper is the operational backbone of every later
PyAutoLens dark-matter analysis, and the canonical reference for the
workspace's subhalo-scanning workflow.

## Despali 2017 — baryons on substructure

**Reference:** arXiv:1608.06938
MNRAS 469, 1997 — note the paper is 2017, the filename "2018" is the
journal-volume year)
**Authors:** Despali & Vegetti
**Concepts:** [[dark-matter-substructure]]
**Summary:** Compares subhalo populations in the EAGLE and Illustris
hydrodynamical simulations against their DM-only twins, in host haloes of
`10^{12.5}`–`10^{14} M⊙ h^{-1}` at `z = 0.2`–`0.5` — i.e. the SLACS /
BELLS host regime. Baryons systematically suppress the subhalo mass
function near the host centre (tidal disruption is more efficient when
the central baryonic potential is included), with the effect strongest
inside the Einstein radius where strong-lens substructure searches
operate. Cite this paper whenever DM-only predictions of subhalo
abundance are being compared to strong-lens detections — there is a
substantial baryonic correction.

## Despali 2018 — LOS

**Reference:** arXiv:1710.05029
5424)
**Authors:** Despali, Vegetti, White, Giocoli, van den Bosch
**Concepts:** [[line-of-sight-effects]],
[[dark-matter-substructure]]
**Summary:** Derives the analytic mass–redshift relation that lets a
strong-lens substructure detection threshold (e.g. `10^{8} M⊙` at the
lens redshift) be rescaled into the corresponding NFW-mass threshold for
a halo at any other redshift along the line of sight. Folding the rescaled
threshold into the cosmological halo mass function shows that the *total*
number of detectable perturbers in a SLACS-like lens is dominated by
foreground/background LOS haloes rather than in-lens subhaloes — typically
by factors of 3–10 depending on geometry. This is the paper that
operationalised the LOS contribution as a distinct, simulable component
of every modern substructure search; required reading for any of the
[[dark-matter-physics]] constraints downstream.

## Despali 2022 — detecting low-mass haloes I (sensitivity)

**Reference:** arXiv:2111.08718
Despali et al. 2022 — Sensitivity *(same paper — both filenames
are local copies of arXiv:2111.08718; the 2021/2022 split in the previous
wiki was an artefact of submission-year vs publication-year naming)*.
arXiv:2111.08718, MNRAS 510, 2480 (2022).
**Authors:** Despali, Vegetti, White, Powell, Stacey, Fassnacht, Rizzo,
Enzi
**Concepts:** [[dark-matter-substructure]],
[[gravitational-imaging]]
**Summary:** Quantifies the lowest detectable NFW mass at every pixel
of the lens plane as a function of data quality (SNR), instrument
angular resolution and pixel scale, source brightness distribution, and
lensing geometry — the "sensitivity map" formalism. The minimum
detectable mass varies from `~1.5 × 10^{8} M⊙` (HST-quality data on a
bright extended source) up to `~3 × 10^{9} M⊙` (typical ground-based or
poorly-resolved lenses). Provides analytic scaling laws used to forecast
substructure science for HST, JWST, and Euclid surveys; Paper I in the
"Detecting low-mass haloes with strong gravitational lensing" series and
the calibration reference behind every later sensitivity-map paper.

## Despali 2024 — detecting low-mass haloes II

**Reference:** arXiv:2407.12910
A&A 2025)
**Authors:** Despali, Heinze, Fassnacht, Vegetti, Spingola, Klessen
**Concepts:** [[dark-matter-substructure]], [[dark-matter-physics]]
**Summary:** Paper II of the sensitivity series — turns from forecasting
to *measuring* the density profiles of the two best-constrained
detected subhaloes, SDSSJ0946+1006 (the [[Minor 2021]] perturber) and
JVASB1938+666 (the Vegetti 2012 perturber). The recovered inner slopes
are close to or steeper than isothermal, requiring concentrations well
above the median CDM `c-M` relation. The paper compares to FIRE-2,
TNG50, and EAGLE simulations and shows that ~1% of CDM subhaloes can
produce such profiles via tidal stripping and adiabatic contraction, but
the resulting baryonic content exceeds the photometric upper limits in
at least one system — i.e. the tension with vanilla CDM is real and is
the data-side motivation for re-examining SIDM and warm-DM alternatives.

## Amorisco 2022 — halo concentration

**Reference:** Amorisco 2022 — halo concentration
**Concepts:** [[dark-matter-substructure]]
**Summary:** Studies how halo concentration changes the detectability of
low-mass perturbers in galaxy-galaxy strong lenses, showing that more
concentrated haloes strengthen dark-matter constraints and clarifying the
relative sensitivity to lens-plane and line-of-sight structure.

## He 2017 — substructure halos vs globular clusters

**Reference:** arXiv:1707.01849
(arXiv:1707.01849, MNRAS 480, 5084; submitted 2017, published 2018)
**Authors:** He, Li, Lim, Frenk, Cole, Peng, Wang
**Concepts:** [[dark-matter-substructure]]
**Summary:** Asks whether the globular-cluster population of an early-type
lens galaxy could masquerade as the dark-matter perturbers that
substructure searches are trying to detect. They show that the number
density of GCs at `M_GC ~ 10^{6} M⊙` near the Einstein ring is *comparable*
to the predicted detectable subhalo abundance — so naive non-detections of
DM are potentially confused by GCs. The saving grace is that GCs are much
more compact than NFW subhaloes of the same mass, so their lensing
signatures differ at the milli-arcsecond level; sufficiently high-
resolution data (VLBI / JWST / ELT) can distinguish the two. Cite this as
the "GC contamination" reference whenever the assistant explains why
low-mass perturbers are not automatically dark.

## He 2022 — preprint

**Reference:** He 2022 — preprint
**Concepts:** [[dark-matter-substructure]]
**Summary:** Tests subhalo-detection pipelines on mock strong lenses
generated from a cosmological hydrodynamical simulation, showing that
simple power-law macromodels can create false positives when the true
lens has non-elliptical structure and that decomposed stellar+dark-matter
models recover the injected perturber more reliably.

## Loudas 2022 — millilensing

**Reference:** arXiv:2209.13393
**Authors:** Loudas, Pavlidou, Casadio, Tassis
**Concepts:** [[dark-matter-substructure]], [[dark-matter-physics]]
**Summary:** Develops a semi-analytic forecast of the milli-lensing
optical depth — the expected rate of milli-arcsecond multiple-imaging of
compact radio sources by sub-galactic DM haloes — as a function of source
redshift and DM model. Cold DM produces an order-unity detectable rate
across a flux-limited radio sample; warm DM (`m_th ~ 3 keV`) suppresses
the rate to near zero; self-interacting DM only produces efficient
millilenses in the gravothermal-collapse regime where central
concentrations spike. Sets the theoretical underpinning for SKA / VLBA
millilensing-search programs, complementary to the strong-lens
substructure searches that dominate this hub.

## Ran Li 2016 — CDM vs WDM from strong lenses

**Reference:** arXiv:1512.06507
**Authors:** Li, Frenk, Cole, Gao, Bose, Hellwing
**Concepts:** [[dark-matter-substructure]], [[dark-matter-physics]]
**Summary:** Uses Aquarius / COCO N-body simulations to forecast how many
strong-lens systems are needed to distinguish cold from warm dark matter
via the substructure mass function. The headline result is that a sample
of ~100 lenses with a detection limit `M_low = 10^{7} h^{-1} M⊙` cleanly
separates CDM from a `~3.3 keV` thermal-relic WDM model and from the
7-keV-sterile-neutrino scenario invoked for the unresolved 3.5 keV X-ray
line. Foundational forecast paper that motivates the SLACS + BELLS
substructure programs, and explicitly the target sample sizes pursued by
Vegetti 2018 and Ritondale 2018.

## Ran Li 2016 — projection effects (LOS)

**Reference:** arXiv:1612.06227
1426)
**Authors:** Li, Frenk, Cole, Wang, Gao
**Concepts:** [[dark-matter-substructure]],
[[line-of-sight-effects]]
**Summary:** Companion paper that quantifies the line-of-sight
contribution from independent N-body simulations, finding that LOS haloes
contribute as many detectable image-plane perturbations as in-lens
subhaloes — sometimes more — depending on lens/source redshifts. Independent
confirmation of the [[Despali 2018]] LOS result via a different
simulation suite, and a numerical complement to its analytic
mass-redshift rescaling.

## Diaz-Rivero 2019 — subhalo without lens model

**Reference:** arXiv:1910.00015
(arXiv:1910.00015, Phys. Rev. D 101, 023515)
**Authors:** Diaz Rivero & Dvorkin
**Concepts:** [[dark-matter-substructure]],
[[deep-learning-lensing]]
**Summary:** Trains a convolutional neural network to detect dark-matter
substructure directly from strong-lens images without first solving for
the macromodel — a deliberate departure from the gravitational-imaging
pipeline ([[Vegetti & Koopmans 2009]]) which always pivots through a
fitted smooth lens. With a single perturber the network detects masses
down to `~10^{9} M⊙` even under `~30%` noise, and the false-positive rate
remains low when the perturber sits inside the main lens. Demonstrates
the "bypass-the-macromodel" approach that motivates much of the later
deep-learning substructure literature.

## Ritondale 2018 — BELLS subhaloes

**Reference:** arXiv:1811.03627
485, 2179)
**Authors:** Ritondale, Vegetti, Despali, Auger, Koopmans, McKean
**Concepts:** [[bells-gallery]],
[[dark-matter-substructure]]
**Summary:** Runs the gravitational-imaging pipeline on the 17 BELLS-
GALLERY lenses at `z_l ~ 0.5` (Lyα-emitter sources at `z_s ~ 2-3`),
yielding the highest-redshift sample of objective substructure analyses
to date. No statistically significant subhalo detections are found, but
the number of *candidate* perturbations is consistent with the LOS-halo
counts predicted by ΛCDM combined with [[Despali 2018]]. Combined with
the earlier SLACS analyses (Vegetti 2014) the result tightens the
sterile-neutrino bound feeding into [[Vegetti 2018]] and remains the
canonical BELLS substructure non-detection paper.

## Ritondale 2018 — BELLS-GALLERY Lyman-α morphology

**Reference:** arXiv:1811.03628
MNRAS 482, 4744)
**Authors:** Ritondale, Auger, Vegetti, McKean
**Concepts:** [[bells-gallery]],
[[lensed-source-science]]
**Summary:** Source-plane reconstruction of the UV continuum of the 17
BELLS-GALLERY Lyα emitters with the same lens models used in the
substructure paper above. The achieved physical resolution is `~80 pc`
at `z ~ 2-3`, revealing that LAEs in this magnification-selected sample
are predominantly clumpy disc-like systems with multiple compact star-
forming regions, and ~2 candidate mergers. Companion paper to the
substructure analysis — its source-plane fidelity is what made the
companion's evidence-based subhalo limits trustworthy.

## Sawala 2016 — the chosen few

**Reference:** arXiv:1406.6362
MNRAS 456, 85)
**Authors:** Sawala et al. (the APOSTLE collaboration)
**Concepts:** [[dark-matter-substructure]]
**Summary:** Uses zoom-in hydrodynamical simulations of Local Group
analogues to ask which low-mass dark-matter haloes successfully host a
luminous dwarf galaxy. Reionisation suppresses star formation in most
haloes below `~3 × 10^{9} M⊙`, so only a biased "chosen few" become
visible; among the survivors, the galaxy-hosting subset is on average
older, more concentrated, and more tidally stripped than a random pull
from the halo population. The biased mapping between haloes and visible
galaxies is the reason strong-lens substructure searches are interpreted
as constraints on the full DM halo population rather than on the
satellite-galaxy population alone — a fundamental ingredient in
[[dark-matter-physics]] inference from lensing.

## Benitez-Llambay 2020 — onset of galaxy formation

**Reference:** arXiv:2004.06124
(arXiv:2004.06124, MNRAS 498, 4887)
**Authors:** Benitez-Llambay & Frenk
**Concepts:** [[dark-matter-substructure]]
**Summary:** Builds an analytic "Halo Occupation Fraction" model — the
fraction of low-mass DM haloes that contain a luminous galaxy as a
function of halo mass and cosmic time — calibrated against the EAGLE
suite. Predicts a present-day suppression around `3 × 10^{8} M⊙` and full
occupation above `~5 × 10^{9} M⊙`, with a mass-scale that drops at earlier
cosmic times. Complementary to [[Sawala 2016]] and required for forward
modelling the dark-fraction in any lensing-DM constraint that wants to
distinguish a "dark" subhalo detection from an undetected satellite
galaxy.

## Minor 2021 — overconcentrated subhalo in SDSSJ0946+1006

**Reference:** arXiv:2011.10627
Minor et al. 2021 — DM Concentration *(same paper — both filenames
are local copies of arXiv:2011.10627; the 2020/2021 wiki split was a
submission-year vs publication-year artefact).*
arXiv:2011.10627, MNRAS 507, 1662 (2021).
**Authors:** Minor, Gad-Nasr, Kaplinghat, Vegetti
**Concepts:** [[dark-matter-substructure]],
[[dark-matter-physics]]
**Summary:** Re-models the Vegetti 2010 / 2012 substructure detection in
SDSSJ0946+1006 with a more flexible perturber profile and measures its
projected mass `M(<1 kpc) ≈ 2-3.7 × 10^{9} M⊙` (`>95%`) plus an inner
slope at least as steep as isothermal. The implied concentration is
*well above* the median ΛCDM `c-M` relation for the inferred mass; only
`<1%` of CDM subhaloes simultaneously match the mass, concentration, and
darkness constraint, placing the system in measured tension with vanilla
CDM. The detection that motivates the Despali 2024 follow-up and the
SIDM-gravothermal-collapse interpretations (e.g. Nadler 2024, Yang 2025).

## See also

- [[dark-matter-substructure]]
- [[gravitational-imaging]]
