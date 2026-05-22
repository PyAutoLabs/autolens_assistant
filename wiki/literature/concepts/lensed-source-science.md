---
title: Source-plane science with strongly-lensed sources
type: concept
topics: [high-redshift, dsfg, agn]
sources:
  - Strong_Lens/Rizzo2018KinematicsStrongLenssources.pdf
  - Strong_Lens/Rizzo2020DSFGNature.pdf
  - Strong_Lens/Rizzo2021DSFTSample.pdf
  - Strong_Lens/Berg2018WindowOnSF.pdf
  - Strong_Lens/Dye2017ModelingAlma.pdf
  - Strong_Lens/Bayliss2017_Hyodrgen_Lensed_Quasar.pdf
status: drafted
---

# Source-plane science

## TL;DR

Strong lensing magnifies background sources by factors of 5–100, so a
correctly-deprojected source-plane reconstruction reaches sub-kpc
resolution at z ≳ 2 — out of reach of any direct telescope. Used for:

- **Dusty star-forming galaxies (DSFGs)** — kinematics, morphology, gas
  content at z = 2–6 (Rizzo 2020/2021).
- **Lyman-α emitters and break galaxies** at z = 4–7 (Berg 2018,
  Lipnicky 2018, James 2018 — the Cosmic Horseshoe).
- **Lensed quasars** — host morphology, narrow-line region kinematics.
- **Reionisation-era galaxies** at z > 6 (HFF + JWST).

## Why it matters

- Galaxy formation at high z requires resolved kinematics; lensing
  delivers them.
- The lens model is a **scientific instrument** — systematic errors in
  the mass model propagate directly into source-plane morphology.
- Pixelated source reconstruction ([[source-reconstruction]]) is the
  standard tool for this regime.

## Why it matters for PyAutoLens

A PyAutoLens user doing source-plane science needs:

- A pixelated or wavelet source with sensible
  [[regularization|regularisation]].
- Robust mass model — including [[multipoles]] for high-fidelity
  morphology.
- Often interferometric data ([[interferometric-lensing|ALMA, VLBI]])
  rather than imaging.

## See also

- [[source-reconstruction]]
- [[interferometric-lensing]]
- [[kinematics-and-lensing]]
- [[sources-lensed-source-science]]
