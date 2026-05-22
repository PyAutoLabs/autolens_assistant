---
title: CSV API — spreadsheet-driven cluster model composition
sources:
  - project: PyAutoLens
    paths:
      - autolens/csv
    pinned_commit: main
last_updated: 2026-05-22
---

# CSV API — cluster-scale model composition

**Status: stub — content to be filled out.** When a model has hundreds
of galaxies (cluster-scale strong lensing), inline Python composition
becomes unmanageable. The CSV API lets you describe each galaxy + its
profile parameters as one row in a per-family spreadsheet, then load
the lot into the standard `af.Model` machinery in two lines.

## Why CSVs

> TODO: diff-friendly, Excel/LibreOffice-editable, round-trippable.
> Manageable at scale; ill-suited below ~20 galaxies (use inline
> Python).

## Schema — `mass.csv`, `light.csv`, `point.csv`

> TODO: columns per file (id, x, y, redshift, profile_class, parameter
> columns, prior columns). Document the canonical layout. Cite
> `PyAutoLens:autolens/csv/...` for the exact column schema.

## Loading into a model

> TODO: pattern is `model = al.csv.model_from(mass_csv=..., light_csv=...,
> point_csv=...)`. The result is a standard `af.Collection` that hands
> straight to an analysis.

## Scaling-relation members

> TODO: a flag column (or separate `scaling_galaxies.csv`) marks
> members whose mass is tied to a shared scaling relation rather than
> free per-row. Document the convention.

## Round-tripping

> TODO: `al.csv.model_to_csv(model, out_dir=...)` writes a model back
> to CSVs. Useful for verifying the load is identity and for capturing
> the best-fit model in CSV form.

## Related pages

- [`concepts/group_and_cluster_lensing.md`](../concepts/group_and_cluster_lensing.md)
  — the physics motivating cluster-scale composition.
- [`api/mass_profile_catalog.md`](./mass_profile_catalog.md) — profile
  classes the CSV rows reference.
