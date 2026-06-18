---
name: al_mge_decomposition
description: Build and fit a Multi-Gaussian Expansion (MGE) model for the lens light and/or the source — a basis of N Gaussians with tied or free centres / ellipticities, whose intensities are solved linearly inside the fit. MGE is the workhorse for complex lens galaxy morphologies (where a single Sersic is too rigid) and increasingly for source modelling. More structured than `al_build_imaging_model`'s "MGE option", less open-ended than `al_custom_profile`. Writes a runnable Python script in scripts/. **Status: stub.**
---

# Multi-Gaussian Expansion (MGE) workflows

MGE represents a galaxy's light (or surface mass density) as a sum of N
Gaussians sharing some structure — typically a common centre and
ellipticity, with the widths (σ) and intensities free. The trick: when
the Gaussians are *linear* light profiles, their intensities are solved
analytically each iteration, so the non-linear search only varies σ's.
Result: high expressivity, few non-linear dimensions.

Standard recipe: 20–30 Gaussians per basis, tied centres + ellipticities,
log-spaced σ priors covering the galaxy scale.

Workspace path:
`autolens_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`
(and sibling files for fit, likelihood, SLaM variants).

## Ask

- *"What is being decomposed — lens light, lens mass (via MGE-derived
  surface density), source light?"* Each has slightly different
  composition.
- *"How many Gaussians?"* 20–30 is the standard starting point; more
  helps for very complex morphologies at fitting cost.
- *"What's tied across the basis — just centre, centre + ellipticity, or
  free per-Gaussian?"* Tied is the standard; freeing is a debugging
  knob.
- *"Cored or full Sersic-equivalent?"* MGE Gaussians don't have a
  natural cusp; if the galaxy has a strong cusp, augment with one
  parametric core profile.

## Branch — lens light MGE

> TODO: recipe. Pattern from `al_build_imaging_model`'s MGE branch but
> with full disambiguation of priors, basis size, and the bias against
> too-few Gaussians.

## Branch — MGE source

Source MGE is rarer but useful when the source is too complex for a
single parametric profile and pixelisation is overkill.

> TODO: recipe.

## Branch — MGE-derived mass profile

A light-MGE can be converted to a mass model with a constant M/L assumption,
useful for stellar-dynamics-style decompositions.

> TODO: recipe — see `PyAutoGalaxy:autogalaxy/profiles/mass/stellar/...`
> for whether an MGE mass profile exists or needs to be built via
> [`al_custom_profile`](./al_custom_profile.md).

## Combine

- [`al_build_imaging_model`](./al_build_imaging_model.md) — the MGE
  light branch is a stub recipe here; this skill is the full workflow.
- [`al_custom_profile`](./al_custom_profile.md) — if you need a custom
  MGE-derived mass profile.
- [`al_adaptive_pixelization`](./al_adaptive_pixelization.md) — common
  pairing: MGE lens light + pixelised source.

## Further reading

- **Student / new to lensing** — _ (MGE is a technique, not a topic
  HowToLens has its own chapter for).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  MGE in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/features/multi_gaussian_expansion/modeling.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/multi_gaussian_expansion/modeling.py):
  the canonical MGE modeling script; sibling files cover SLaM, fit,
  likelihood.

See also [`wiki/core/concepts/light_profiles.md`](../wiki/core/concepts/light_profiles.md)
(linear-profile section) and
[`wiki/core/api/light_profile_catalog.md`](../wiki/core/api/light_profile_catalog.md)
(MGE / basis rows).
