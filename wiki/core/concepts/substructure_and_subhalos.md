---
title: Substructure and subhaloes in strong lenses
sources:
  - project: PyAutoLens
    paths:
      - autolens/lens
    pinned_commit: main
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/mass/dark
    pinned_commit: main
last_updated: 2026-05-22
---

# Substructure and subhaloes

**Status: stub — content to be filled out.** Cold dark matter predicts
many low-mass subhaloes orbiting every massive lens galaxy. Strong-lens
images encode this substructure: a smooth mass model leaves coherent
residuals; an added perturber matches them. Detection (and non-detection
calibrated by sensitivity) constrains the dark-matter halo mass
function — the strongest astrophysical probe of CDM-vs-WDM-vs-fuzzy DM at
sub-galaxy scales.

## Why strong lenses probe substructure

> TODO: angular scale of subhaloes vs. resolution of imaging vs. flux
> ratios. Reference Mao & Schneider 1998, Dalal & Kochanek 2002,
> Vegetti & Koopmans 2009 (cross-link [[VegettiKoopmans2009]] in
> literature wiki when added).

## Detection statistic — Bayesian model comparison

> TODO: Δlog-evidence between with-subhalo and without-subhalo fits;
> conventional 5σ threshold ~ Δln Z > 50 (or Δln Z > 10 for "interesting").

## Grid-search workflow

> TODO: (y, x, m) grid over candidate perturber positions; per-cell
> refit; aggregate evidence map. Link to
> [`skills/al_subhalo_detect`](../../../skills/al_subhalo_detect.md).

## Sensitivity calibration

> TODO: every non-detection needs a sensitivity map to be a constraint.
> Cross-reference [`concepts/sensitivity_mapping.md`](./sensitivity_mapping.md).

## Line-of-sight haloes vs. subhaloes

> TODO: perturbers along the LOS produce similar signatures to subhaloes
> but at different redshifts; PyAutoLens supports both via multi-plane
> tracing.

## Subhalo mass parameterisations

> TODO: NFW with concentration-mass relation; truncated NFW (tNFW);
> point-mass approximation for sub-resolution perturbers. List API
> entries from `PyAutoGalaxy:autogalaxy/profiles/mass/dark/`.

## Related pages

- [`api/mass_profile_catalog.md`](../api/mass_profile_catalog.md) — NFW
  and dark-matter profile rows.
- [`concepts/sensitivity_mapping.md`](./sensitivity_mapping.md).
- [`concepts/multi_plane_lensing`]] (LOS haloes — page TBD).
