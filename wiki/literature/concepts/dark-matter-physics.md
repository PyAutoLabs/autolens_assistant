---
title: Dark matter physics from strong lensing
type: concept
topics: [dark-matter, cosmology]
sources:
  - Bose et al. 2016 — WDM simulations
  - Newton et al. 2021 — constraints on satellites
  - Robertson et al. 2018 — SIDM simulation
  - Navarro et al. 1996 — structure of CDM halos
  - Enzi et al. 2020 — joint constraints thermal relic
  - Gomez et al. 2016 — fermionic DM
status: drafted
---

# Dark matter physics from strong lensing

## TL;DR

Strong-lensing measurements of the [[dark-matter-substructure|subhalo
mass function]], inner-halo densities, and macro-lens slopes all
distinguish among CDM, warm DM, self-interacting DM and fuzzy/scalar
field DM.

## Candidate models the lensing community tests

- **CDM** — Navarro 1996; cusped NFW haloes, no characteristic cutoff
  mass.
- **WDM** — thermal relic; suppressed mass function below ~10⁸ M_⊙ /
  (m_WDM / keV)⁻¹·⁵. Lensing limit currently m_WDM ≳ 5–6 keV
  ([[sources-dark-matter-physics|Enzi 2020]]).
- **SIDM** — self-interactions form constant-density cores at scales set
  by σ/m. Cluster cores and central galaxy concentrations probe this
  (Robertson 2018).
- **Fuzzy / ULDM** — interferes on the de Broglie scale (~kpc for
  10⁻²² eV); distinctive granular substructure imprint on arcs.
- **Fermionic DM** (Gómez 2016) — degenerate-fermion equation of state
  in haloes.

## What lensing measures

| Observable                             | Discriminates among                |
|----------------------------------------|------------------------------------|
| Subhalo mass function below 10⁹ M_⊙    | CDM vs. WDM vs. ULDM               |
| Inner subhalo concentration            | CDM vs. SIDM                       |
| Macro-lens slope and core size         | CDM vs. SIDM (clusters)            |
| LOS halo population                    | Same as subhalo mass function      |
| Power spectrum of arc perturbations    | ULDM granularity                   |

## Tensions

- The "Jackpot" J0946+1006 perturber appears overconcentrated for CDM
  expectations (Minor 2021); various explanations — selection,
  baryonic compression, alternative DM.
- Satellite galaxy counts (Newton 2021) consistent with CDM after
  Milky Way completeness corrections.

## Why it matters for PyAutoLens

PyAutoLens users testing DM physics infer the perturber's M and c, then
compare against model-predicted (M, c) distributions. The forward model
must support the chosen DM model (e.g. truncated WDM mass function).
SBI tools downstream of PyAutoLens (e.g. Brehmer 2019) compress lensing
data into DM-model posteriors.

## See also

- [[dark-matter-substructure]]
- [[gravitational-imaging]]
- [[flux-ratio-anomalies]]
- [[sources-dark-matter-physics]]
