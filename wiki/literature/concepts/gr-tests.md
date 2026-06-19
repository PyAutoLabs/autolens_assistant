---
title: Tests of GR with strong lensing
type: concept
topics: [cosmology, fundamental-physics]
sources:
  - Collett et al. 2018 — GR
  - Melo et al. 2023 — probing GR
status: drafted
---

# Tests of GR with strong lensing

## TL;DR

Strong lensing measures the projected mass via light deflection while
stellar dynamics measures it via test particles in the same potential.
The ratio is sensitive to the post-Newtonian γ_PPN parameter — GR
predicts γ_PPN = 1. Collett 2018 (using ESO325-G004) achieved a
~10% extragalactic test, an order of magnitude tighter than other
extragalactic measurements.

## What it is

In a metric theory parameterised by γ_PPN, light bends by a factor
(1 + γ_PPN)/2 relative to a Newtonian deflector; a non-GR theory
predicts a lensing-to-dynamics ratio different from unity. Massive
ellipticals with both Einstein-radius lensing and well-measured stellar
σ are ideal targets.

Melo 2023 extends this to other systems and other PPN-type tests.

## Why it matters for PyAutoLens

PyAutoLens already supports joint lensing + kinematics fits via
PyAutoFit; the addition of γ_PPN as a free parameter is mechanically
straightforward but requires:

- A spatially-resolved σ map (IFU data) to break the
  [[mass-sheet-degeneracy]] / [[radial-angular-degeneracy]].
- A flexible mass model so γ_PPN is not absorbed into the slope.

## See also

- [[kinematics-and-lensing]]
- [[mass-sheet-degeneracy]]
- [[time-delay-cosmography]]
- [[sources-gr-cosmology]]
