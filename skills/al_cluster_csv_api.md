---
name: al_cluster_csv_api
description: Compose a cluster-scale strong lens model from CSV spreadsheets (`mass.csv`, `light.csv`, `point.csv`) instead of inline Python. Used when a model has tens of main lenses, hundreds of member galaxies, or dozens of background sources — at that scale Python composition becomes unmanageable and a spreadsheet is diff-friendly, Excel/LibreOffice-editable, and round-trippable to the standard `af.Model` objects. Writes a runnable Python script in scripts/ that reads the CSVs and instantiates the model. **Status: stub.**
---

# Cluster lensing via the CSV API

A cluster lens model has scale problems an `af.Collection(...)` literal
can't handle gracefully — tens of main lenses, hundreds of cluster
members, sometimes dozens of background sources. The CSV API solves this:
three (or four) spreadsheets, one per profile family, describe every
galaxy + its profile parameters. Python only reads them in and hands the
result to the standard model/analysis stack.

Workspace path: `autolens_workspace:scripts/cluster/csv_api.py`,
`scripts/cluster/modeling.py`.

## Ask

- *"How many lenses, members, and sources?"* This sets whether the CSV
  workflow is worth the setup; below ~20 galaxies inline Python is still
  faster.
- *"Do you have a starting catalogue (galaxy positions, magnitudes) in a
  spreadsheet or table already?"*
- *"Which profile families per galaxy class — main lens (PIEMD?
  PowerLaw?), members (SIE? scaling relation?), sources?"*
- *"How are scaling-relation members handled — separate file or rows in
  `mass.csv` with a relation flag?"*

## Branch — three-file canonical layout

Three CSVs: `mass.csv`, `light.csv`, `point.csv`. Each row = one galaxy +
its profile parameters (centre, ell_comps, normalisation, …) and prior
ranges.

> TODO: recipe. Pattern: `model = al.csv.model_from(mass_csv=Path("mass.csv"),
> light_csv=Path("light.csv"), point_csv=Path("point.csv"))` (verify
> exact API in `PyAutoGalaxy:autogalaxy/galaxy/galaxy_model_csv.py`; the
> workspace walkthrough is `autolens_workspace:scripts/cluster/csv_api.py`).

## Branch — adding scaling-tier members

Legacy `scaling_galaxies.csv` (or a flag column in `mass.csv`) marks
members whose mass follows a population-level scaling relation, not free
per-row parameters.

> TODO: recipe.

## Branch — round-tripping for inspection

Read CSVs → compose model → write model back to CSV to verify the
round-trip is identity. Useful as a sanity check before launching a long
fit.

> TODO: recipe.

## Combine

- [`al_group_lensing`](./al_group_lensing.md) — for smaller groups the
  inline Python path is fine; use this skill when the CSV scale tips
  over.
- [`al_run_slam_pipeline`](./al_run_slam_pipeline.md) — cluster SLaM
  variants exist in the workspace.

## Further reading

- **Student / new to lensing** — _ (no HowToLens equivalent; cluster
  lensing is research-grade).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  cluster lensing in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: cluster/csv_api.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/cluster/csv_api.py):
  the canonical CSV schema + round-trip demo.

See also [`wiki/core/api/csv_api.md`](../wiki/core/api/csv_api.md) for the
CSV schema reference and
[`wiki/core/concepts/group_and_cluster_lensing.md`](../wiki/core/concepts/group_and_cluster_lensing.md)
for the physics.
