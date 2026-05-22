---
title: Strong gravitational lensing — overview
type: concept
topics: [overview]
sources: []
status: drafted
---

# Strong gravitational lensing — overview

## TL;DR

Strong gravitational lensing is the regime where a foreground mass
distribution bends light from a background source enough to produce
**multiple images, arcs, or rings**. Each image is a separate solution of
the [[lens-equation]]. The geometry and brightness of those images encode
the projected mass of the lens (often a galaxy or cluster) and the
intrinsic surface brightness of the source. PyAutoLens is a code that
solves the inverse problem: given an observed image, infer both the lens
mass model and the unlensed source.

## What it is

A massive object sits between an observer and a background source. The
lens deflects light rays by an angle set by its [[lens-equation|deflection
field]]; when the alignment is close enough, multiple light paths reach
the observer. The observable consequences fall into three regimes:

- **Weak**: small, statistical shape distortions of many background
  galaxies (see `[[weak-lensing]]`, out of scope for this wiki).
- **Strong**: a single source produces multiple images, arcs, or an
  Einstein ring. Image positions and shapes give a near-direct measurement
  of the mass enclosed within the [[einstein-radius]].
- **Micro**: stellar-mass deflectors imprint variability on macro-images,
  used for the [[microlensing-imf|stellar IMF]] in lens galaxies.

## Why it matters for PyAutoLens

PyAutoLens is built to solve the strong-lensing forward problem
end-to-end: a [[mass-models|parametric or composite mass model]] for the
lens, a [[source-reconstruction|parametric or pixelised source model]] for
the background, ray-traced via the [[lens-equation]], compared to data
under a likelihood with [[regularization]] for the source pixels and
[[bayesian-inference-lensing|Bayesian inference]] over the parameters.
Every concept in this wiki maps to a choice the user makes when assembling
that pipeline.

## Science applications

Strong lensing is used to:

- Measure [[dark-matter-substructure|dark matter on sub-galactic scales]],
  testing CDM versus warmer / self-interacting alternatives
  ([[dark-matter-physics]]).
- Measure H0 via [[time-delay-cosmography]].
- Test [[gr-tests|general relativity]] at galactic scales.
- Magnify [[lensed-source-science|high-redshift galaxies, DSFGs and AGN]]
  to study the early universe at sub-kpc resolution.
- Probe galaxy structure via the [[bulge-halo-decomposition|separation of
  stars and dark matter]] in the lens.
- Constrain the [[microlensing-imf|stellar IMF]] in massive ellipticals.
- Discover and study [[smbh-from-lensing|supermassive black holes]] via
  central images and arc perturbations.

## See also

- [[lens-equation]]
- [[einstein-radius]]
- [[mass-models]]
- [[source-reconstruction]]
- [[pyautolens]]
