---
title: Radial-angular decomposition of lensing constraints
type: concept
topics: [degeneracies]
sources:
  - Strong_Lens/Kochanek2020radialangular.pdf
  - Strong_Lens/Kochanek2021radialdog.pdf
  - Strong_Lens/Saha2000.pdf
status: drafted
---

# Radial-angular decomposition

## TL;DR

Kochanek (2020, 2021) argued that lensing data fundamentally decompose into
two nearly-orthogonal pieces of information:

- **Angular structure** — the locations of multiple images and the
  azimuthal pattern of arcs constrain the angular structure of the
  potential (ellipticity, [[multipoles]], position angle) very precisely.
- **Radial structure** — the radial mass profile (slope γ, inner/outer
  decline) is only weakly constrained, principally near the
  [[einstein-radius]].

## What it is

Imaging gives you:

- Image positions → primarily angular structure of the potential plus the
  enclosed mass at θ_E.
- Image fluxes (with corrections) → some angular information.
- Time delays → a radial constraint, modulo the [[mass-sheet-degeneracy]].
- Stellar kinematics → an independent radial constraint.

So a strong lens **excellently fixes mass at θ_E** but only weakly the
slope. Quoting precise values of γ or the dark-matter fraction at radii
far from θ_E without external data is misleading. Kochanek 2020 / 2021
make this point sharply and warn against over-interpreting SLACS-style
"isothermal everywhere" claims.

## Why it matters for PyAutoLens

- Posteriors on γ that are tight without external information are
  suspect. Check the prior dependence.
- Reports of dark-matter fractions inside small radii require external
  size / luminosity priors.
- For [[bulge-halo-decomposition]] fits, stellar M/L and halo
  concentration are partially degenerate along the radial direction.

## See also

- [[einstein-radius]]
- [[mass-sheet-degeneracy]]
- [[bulge-halo-decomposition]]
- [[sources-degeneracies-systematics]]
