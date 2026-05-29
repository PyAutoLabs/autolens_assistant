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

Galaxy-scale lensing
assumes a single dominant deflector. Group-scale and cluster-scale
lensing don't: multiple lens galaxies (a primary + companions, or many
cluster members) all contribute to the deflection. The modelling
question changes from "what is this lens like?" to "how do I parameterise
N deflectors without exploding the parameter space?"

## The mass scale

The jump from galaxy to group to cluster is mostly a jump in how much of
the image-plane deflection field must be modeled at once.

- galaxy-scale systems usually have Einstein radii of order 1 arcsec
- group-scale systems are broader, often a few arcsec to around 10 arcsec
- cluster-scale systems can extend to tens of arcsec

That change drives nearly every workflow choice:

- the field of view has to be larger
- more foreground galaxies matter dynamically
- multiple background sources are more common
- light and mass bookkeeping becomes the main technical problem

## Three modelling strategies

There are three stable regimes.

1. **Free per-companion** for small `N`.
   Each extra lens galaxy gets its own light and mass profile. This is
   practical when only a few companions matter and you want each to have
   independent parameters.

2. **Scaling-relation members** for medium `N`.
   Many companions are tied to a shared luminosity-to-mass relation so
   that their observed photometry sets the relative scale while only a
   small number of hyperparameters remain free.

3. **CSV-driven composition** for large `N`.
   Once the model contains tens to hundreds of member galaxies, inline
   Python becomes error-prone. The CSV API moves the bookkeeping into
   tabular files that still load into the standard `af.Model` machinery.
   See [`../api/csv_api.md`](../api/csv_api.md).

## Source-side considerations

Group and cluster lenses often include multiple sources at different
redshifts. That changes both the information content and the model
composition:

- each source adds its own imaging or point-source constraint
- the deflector model is shared across those constraints
- if source redshifts differ materially, the full calculation is
  multi-plane rather than a single source plane

This is one reason cluster modeling tends to look like a multi-dataset
problem even when all observations come from one instrument.

## Member-galaxy mass profiles

Cluster-lensing papers often use PIEMD-like families for member galaxies
because they are compact, interpretable, and easy to scale with
luminosity. In PyAutoLens / PyAutoGalaxy, the nearest out-of-the-box
analogs are the isothermal family plus dark-halo components, with custom
profiles available when a literal PIEMD parameterization is required.

The practical choice is usually driven by workflow compatibility rather
than naming purity:

- use built-in profiles when they capture the intended physics and keep
  the rest of the pipeline standard
- introduce a custom profile when the project must match a field-standard
  parameterization or a legacy analysis

For the custom-profile route, see
[`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md).

## Related pages

- [`api/csv_api.md`](../api/csv_api.md) — cluster-scale CSV composition.
- [`api/mass_profile_catalog.md`](../api/mass_profile_catalog.md) — NFW
  / Isothermal rows used at cluster scale.
- [`concepts/multi_wavelength.md`](./multi_wavelength.md) — cluster
  lensing is frequently multi-band.
- [`concepts/extra_galaxies_and_noise_scaling.md`](./extra_galaxies_and_noise_scaling.md)
  — the galaxy-scale counterpart, where extra galaxies are contaminants to
  noise-scale rather than deflectors to model.
