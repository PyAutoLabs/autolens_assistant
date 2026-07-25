---
title: Multi-galaxy, group- and cluster-scale strong lensing
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy.py
      - autogalaxy/galaxy/galaxy_model_csv.py
    pinned_commit: main
last_updated: 2026-07-25
---

# Multi-galaxy, group- and cluster-scale lensing

Galaxy-scale lensing assumes a single dominant deflector. Above that
scale, PyAutoLens organises lenses into a **ladder of three regimes** —
`multi_galaxy`, `group`, `cluster` — each with its own workspace package.
Every group and cluster is a multi-galaxy system, but not vice versa;
what changes as you climb is first the mass model, then the entire
analysis strategy:

- **Multi galaxy** (`autolens_workspace/*/multi_galaxy`): two or more
  co-dominant galaxies, NO shared dark-matter halo. One free light and
  mass model per deflector (untruncated isothermals — no host halo means
  no tidal truncation), one extended source, the standard pixel-level
  `AnalysisImaging` workflow.
- **Group** (`autolens_workspace/*/group`): a dominant group-scale halo
  (~10^13–10^14 M_sun) enters as an **explicit modelling choice** —
  `group/features/group_halo` fits the same data with and without it —
  and fainter members go on luminosity scaling relations (tidally
  truncated dPIE members in the Lenstool-convention workflow). Still one
  extended source, still `AnalysisImaging`.
- **Cluster** (`autolens_workspace/*/cluster`): the same mass framework
  as a group (host halo(s) + many truncated members on scaling
  relations), but the **analysis itself changes**: many sources at many
  redshifts are fitted as point-source multiple-image positions
  (`AnalysisPoint` + factor graph, multi-plane), and the lens galaxies'
  light is not modeled.

## The mass scale

The jump up the ladder is mostly a jump in how much of the image-plane
deflection field must be modeled at once.

- galaxy-scale systems usually have Einstein radii of order 1 arcsec
- multi-galaxy systems have comparable, overlapping deflectors whose
  combined Einstein radius spans the pair/set (~1–3 arcsec)
- group-scale systems are broader, often a few arcsec to around 10 arcsec
- cluster-scale systems can extend to tens of arcsec

That change drives nearly every workflow choice:

- the field of view has to be larger
- more foreground galaxies matter dynamically
- multiple background sources are more common
- light and mass bookkeeping becomes the main technical problem

## Three modelling strategies

The three strategies map onto the three regimes.

1. **Free per-deflector** — the multi-galaxy regime's default.
   Each co-dominant galaxy gets its own light and mass profile
   (`lens_0`, `lens_1`, … in the list-based API). Practical for small
   `N`, and the only strategy that measures each galaxy's mass centre
   independently of its light (the mass/light-offset science of systems
   like SDSS J1011+0143).

2. **Scaling-relation members** — the group regime's default for the
   faint tier. Many members are tied to a shared luminosity relation so
   photometry sets relative scale while one normalization stays free.
   The modern convention (Bergamini et al. 2019) ties the truncation
   exponent to the dispersion exponent via 2*alpha + beta_cut = 1 + gamma
   (gamma = 0.2 fixed), with vanishing unscaled member cores. Whether a
   separate group halo joins the members is an explicit, testable choice
   — see `group/features/group_halo`.

3. **CSV-driven composition + point-source constraints** — the cluster
   regime. Tens to hundreds of members load from tabular files
   (see [`../api/csv_api.md`](../api/csv_api.md)) and the fit switches
   from pixel-level source reconstruction to multiple-image positions
   with per-source redshifts (multi-plane). Extended-source
   reconstruction becomes a specialised follow-up of individual systems.

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

Cluster-lensing papers use the dPIE / PIEMD family for member galaxies
because it is compact, interpretable, and easy to scale with luminosity.
PyAutoLens now ships this natively: `al.mp.dPIEMass` / `dPIEMassSph`
take Lenstool's own parameters (`sigma` = the fiducial v_disp, `r_core`,
`r_cut`), so a fitted posterior reads like a Lenstool results table, and
`r_core = 0` (the vanishing-core convention for BCGs and members) is
analytic. Untruncated isothermals remain the right choice at
multi-galaxy scale, where no host halo motivates truncation.

The practical choice is usually driven by workflow compatibility rather
than naming purity:

- use built-in profiles when they capture the intended physics and keep
  the rest of the pipeline standard
- introduce a custom profile when the project must match a field-standard
  parameterization or a legacy analysis

For the custom-profile route, see
[`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md).

## Related pages

- `autolens_workspace/*/multi_galaxy`, `*/group` (incl.
  `features/group_halo`) and `*/cluster` — the three regime packages.
- [`api/csv_api.md`](../api/csv_api.md) — cluster-scale CSV composition.
- [`api/mass_profile_catalog.md`](../api/mass_profile_catalog.md) — NFW
  / Isothermal rows used at cluster scale.
- [`concepts/multi_wavelength.md`](./multi_wavelength.md) — cluster
  lensing is frequently multi-band.
- [`concepts/extra_galaxies_and_noise_scaling.md`](./extra_galaxies_and_noise_scaling.md)
  — the galaxy-scale counterpart, where extra galaxies are contaminants to
  noise-scale rather than deflectors to model.
