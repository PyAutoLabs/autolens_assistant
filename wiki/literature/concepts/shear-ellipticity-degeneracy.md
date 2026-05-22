---
title: Shear–ellipticity degeneracy
type: concept
topics: [degeneracies]
sources:
  - Strong_Lens/Witt1997Shear.pdf
  - Strong_Lens/Keeton1997ShearEllipticity.pdf
  - Strong_Lens/Gomer2021ShearEllipseDegen.pdf
  - Strong_Lens/Hogg2022SLShear.pdf
status: drafted
---

# Shear–ellipticity degeneracy

## TL;DR

Internal ellipticity of the lens and external shear from the environment
produce similar angular signatures on image positions. Reliably
disentangling them needs either lots of images, complex arc structure, or
external information about the LOS density field.

## What it is

A lens with ellipticity e and PA φ produces image patterns that resemble
those of a less-elliptical lens with an additional external shear γ_ext
aligned with the major axis (Keeton 1997, Witt 1997). For four-image
systems with simple sources, the degeneracy is partly broken because
relative positions and flux ratios depend differently on internal vs.
external angular structure — but the residual covariance is real and
inflates uncertainties on γ_ext.

Gomer 2021 and Hogg 2022 revisit the degeneracy in the context of
[[time-delay-cosmography|H0]] systematics.

## Why it matters

- Cosmography (H0) cares about γ_ext because it correlates with the
  external convergence κ_ext.
- [[dark-matter-substructure|Substructure detection]] suffers if angular
  complexity is misattributed to the lens vs. the environment.
- A PyAutoLens user fitting with vs. without shear and seeing γ_ext be
  ~0.05 should check that ellipticity hasn't rotated to absorb it.

## Remediation

- Joint imaging + stellar kinematics breaks the orientation freedom of
  the lens ellipticity.
- LOS-based external convergence priors (Suyu / Rusu / Wong 2011) bound
  γ_ext physically rather than statistically.
- Multipole models ([[multipoles]]) free angular complexity from being
  forced into pure ellipticity or shear.

## See also

- [[external-convergence-shear]]
- [[multipoles]]
- [[mass-sheet-degeneracy]]
- [[sources-degeneracies-systematics]]
