---
title: Source position transformation (SPT)
type: concept
topics: [degeneracies]
sources:
  - Strong_Lens/Wertz2018PySPT.pdf
status: drafted
---

# Source position transformation (SPT)

## TL;DR

The SPT is a family of transformations on the deflection field and source
plane that leaves image positions and morphologies nearly invariant. The
[[mass-sheet-degeneracy]] is the special case of an isotropic
multiplicative rescaling. More general SPTs are not exactly degenerate —
they leave small residuals in image shapes — but those residuals are
typically below imaging noise, making the degeneracy effective.

## What it is

Schneider & Sluse 2014 introduced the SPT as a generalisation: any
deflection α′(θ) = α(θ) + δα(θ) such that the multiple-image consistency
is preserved produces a model fit that is observationally
indistinguishable at imaging precision. The pySPT code
([[sources-degeneracies-systematics|Wertz 2018]]) computes these.

## Why it matters

- Treating SPT-invariant differences as physical inflates apparent
  constraints on the lens model.
- The SPT systematically biases time delays in the same direction as the
  MSD — relevant for [[time-delay-cosmography]].
- Breaking the SPT requires extra information: stellar kinematics, source
  size priors, or LOS data.

## See also

- [[mass-sheet-degeneracy]]
- [[radial-angular-degeneracy]]
- [[sources-degeneracies-systematics]]
