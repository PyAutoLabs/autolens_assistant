---
title: Group- and cluster-scale strong lensing
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy.py
    pinned_commit: main
  - project: PyAutoLens
    paths:
      - autolens/csv
    pinned_commit: main
last_updated: 2026-05-22
---

# Group- and cluster-scale lensing

**Status: stub — content to be filled out.** Galaxy-scale lensing
assumes a single dominant deflector. Group-scale and cluster-scale
lensing don't: multiple lens galaxies (a primary + companions, or many
cluster members) all contribute to the deflection. The modelling
question changes from "what is this lens like?" to "how do I parameterise
N deflectors without exploding the parameter space?"

## The mass scale

> TODO: typical Einstein radii by scale (galaxy ~1″, group ~3–10″,
> cluster 10–40″) and what that implies for the imaging FOV and the
> number of member galaxies that matter.

## Three modelling strategies

> TODO:
> 1. **Free per-companion** (small N): each companion has its own
>    light + mass profile. Works for ~3–10.
> 2. **Scaling-relation members** (medium N): companion mass is tied to
>    observed luminosity via a population-level M-L relation. Works for
>    ~10–100.
> 3. **CSV-driven composition** (large N): cluster-scale, hundreds of
>    members, where inline Python composition is impractical. See
>    [`api/csv_api.md`](../api/csv_api.md).

## Source-side considerations

> TODO: group lenses often have multiple sources at different
> redshifts. Each source has its own analysis term; the mass model is
> shared across them — multi-plane lensing if redshifts are distinct.

## Member-galaxy mass profiles

> TODO: PIEMD (pseudo-isothermal elliptical mass distribution) is the
> cluster-lensing field standard; PyAutoGalaxy's nearest equivalent is
> `mp.Isothermal` (truncated) or a custom PIEMD. Document the choice
> and any custom profile recipe (cross-reference
> [`skills/al_custom_profile`](../../../skills/al_custom_profile.md)).

## Related pages

- [`api/csv_api.md`](../api/csv_api.md) — cluster-scale CSV composition.
- [`api/mass_profile_catalog.md`](../api/mass_profile_catalog.md) — NFW
  / Isothermal rows used at cluster scale.
- [`concepts/multi_wavelength.md`](./multi_wavelength.md) — cluster
  lensing is frequently multi-band.
