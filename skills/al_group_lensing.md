---
name: al_group_lensing
description: Model a group-scale strong lens — one or two main lens galaxies plus a population of companion ("extra") galaxies whose light + mass must also be modelled. Two strategies: (a) free per-companion profiles for small N, (b) "scaling-relation" galaxies tied to a luminosity-to-mass relation for larger N. Pairs with `al_cluster_csv_api` (when N is large enough that inline Python composition becomes unwieldy). Writes a runnable Python script in scripts/. **Status: stub.**
---

# Group-scale lensing — companion galaxies and scaling relations

A galaxy-scale model assumes one dominant lens. A group-scale lens has
multiple deflectors: a primary galaxy plus companions whose mass cannot be
ignored. With ~3–10 companions you can give each its own light + mass
profile (free). Past that, parameter count explodes and you instead tie
each companion's mass to its observed luminosity via a scaling relation.

Workspace path: `autolens_workspace:scripts/group/start_here.py` and
`scripts/group/features/scaling_relation/modeling.py`.

## Ask

- *"How many lens galaxies — main + how many companions?"* This picks the
  branch.
- *"Do you have light + position measurements for the companions, or just
  positions?"* Scaling relations need a measured luminosity per
  companion.
- *"Source — single or multiple?"* Group lenses sometimes have multiple
  background sources at different redshifts.
- *"Parametric or pixelised source?"* Same trade-off as galaxy-scale.

## Branch — small N: free per-companion mass profiles

> TODO: recipe. Pattern: each companion gets its own `Galaxy` with light
> + mass; centres are fixed from imaging measurements; mass-profile
> normalisations are free. Bundle into a single `af.Collection`.

## Branch — large N: scaling-relation companions

> TODO: recipe. Pattern: a single set of shared scaling-relation
> parameters (slope, normalisation, scatter) governs the mass of every
> companion as a function of its measured luminosity. See
> `PyAutoGalaxy:autogalaxy/galaxy/...` for the scaling-relation
> machinery.

## Branch — group with extra + scaling galaxies together

Some companions are bright enough to deserve free mass; the rest follow
the scaling relation. Composed in one model.

> TODO: recipe.

## Combine

- [`al_cluster_csv_api`](./al_cluster_csv_api.md) — for very large N
  (cluster-scale), spreadsheet-driven composition.
- [`al_run_slam_pipeline`](./al_run_slam_pipeline.md) — group SLaM
  variant exists in the workspace.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md)
  — pixelised sources are common in group lenses.

## Further reading

- **Student / new to lensing** — _ (no direct HowToLens chapter; group
  lensing is an advanced topic).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  group lensing in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: group/start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/group/start_here.py):
  the canonical group fit — extra galaxies, scaling relations, group
  SLaM.

See also [`wiki/core/concepts/group_and_cluster_lensing.md`](../wiki/core/concepts/group_and_cluster_lensing.md)
for the physics (group mass scale, cluster member kinematics, the
extra-galaxy vs. scaling-relation choice).
