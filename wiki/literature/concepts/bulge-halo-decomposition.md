---
title: Bulge–halo (stellar + dark matter) decomposition
type: concept
topics: [galaxy-structure]
sources:
  - Strong_Lens/Etherington2022BulgeHalo.pdf
  - Strong_Lens/Etherington2022SLaM.pdf
  - Strong_Lens/Etherington2023aBeyondBulge.pdf
  - Strong_Lens/Shajib2021MassSlopeNFW.pdf
  - Strong_Lens/Oldham2018StellarAndDark.pdf
status: drafted
---

# Bulge–halo decomposition

## TL;DR

Decompose a lens galaxy's mass into a stellar component (mass-traces-
light Sérsic or MGE) and a dark-matter component (NFW or gNFW). This
splits what the elliptical-power-law model conflates into a single slope
into physically meaningful components — stellar M/L and DM concentration
— at the cost of more parameters and a stronger sensitivity to the
[[radial-angular-degeneracy]].

## What it is

Inputs:

- A high-resolution image of the lens light → MGE / Sérsic / multi-Sérsic
  decomposition (see [[sources-bulge-halo|Etherington series]]).
- A free overall M/L or per-component M/L.
- An NFW (or gNFW) DM halo.
- Optional adiabatic contraction.
- [[external-convergence-shear|External shear]].

Outputs:

- Stellar M/L, often inverted to **the IMF**
  ([[microlensing-imf|complementary to microlensing-IMF measurements]]).
- DM concentration and mass.
- Stellar-to-halo mass ratio inside the [[einstein-radius]].

## Why it matters

- Tests galaxy formation: do massive ellipticals have NFW-consistent
  haloes or contracted ones?
- Calibrates the **dark-matter fraction inside R_eff**, a benchmark
  galaxy-evolution quantity.
- Disentangles IMF from DM concentration, the long-standing
  bulge-vs-halo degeneracy.

## In PyAutoLens

The SLaM pipeline ([[slam-pipeline]]) chains:

1. Sérsic-mass + SIE phase.
2. Power-law phase with parametric source.
3. Power-law phase with pixelated source.
4. Composite Sérsic + NFW phase — the bulge-halo step.

Each phase informs the next via PyAutoFit search chaining
([[bayesian-inference-lensing]]).

## See also

- [[mass-models]]
- [[radial-angular-degeneracy]]
- [[microlensing-imf]]
- [[slam-pipeline]]
- [[sources-bulge-halo]]
