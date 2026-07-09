---
title: CSV API — spreadsheet-driven cluster model composition
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy_model_csv.py
      - autogalaxy/galaxy/galaxy_table.py
    pinned_commit: main
last_updated: 2026-07-09
---

# CSV API — cluster-scale model composition

When a model has hundreds
of galaxies (cluster-scale strong lensing), inline Python composition
becomes unmanageable. The CSV API lets you describe each galaxy + its
profile parameters as one row in a per-family spreadsheet, then load
the lot into the standard `af.Model` machinery in two lines.

## Why CSVs

The CSV route exists for bookkeeping, not elegance. At cluster scale the
model catalog itself becomes difficult to maintain in inline Python.
Tabular files are:

- diff-friendly in git
- editable in Excel or LibreOffice
- easy to validate row by row
- easy to export again for review or collaboration

Below roughly group scale, inline Python is usually clearer. CSV becomes
worth it when catalog size dominates the cognitive load.

## Schema — `mass.csv`, `light.csv`, `point.csv`

The exact schema lives in `PyAutoGalaxy:autogalaxy/galaxy/galaxy_model_csv.py`
(with `PyAutoGalaxy:autogalaxy/galaxy/galaxy_table.py` for the
`output_to_csv` / `list_from_csv` table helpers), but the conceptual
layout is stable:

- one row per galaxy or point-source component
- identifying columns such as object id and redshift
- profile-selection columns naming the mass or light family
- parameter columns containing values or prior settings
- optional flags marking fixed, free, or scaling-relation behavior

The CSV therefore serializes the same model graph you would otherwise
write inline.

## Loading into a model

Loading converts the tabular representation back into ordinary PyAutoFit
and PyAutoLens model objects. The important architectural point is that
only the *construction* step changes. Downstream analyses and searches
still consume a standard collection of galaxies and sources.

## Scaling-relation members

Scaling-relation members are where the CSV approach earns its keep. Many
cluster galaxies follow the same functional form, with only their
luminosity or other measured property changing row by row. The table can
therefore mark those galaxies as belonging to a shared relation rather
than giving each one its own fully free mass normalization.

## Round-tripping

Round-tripping is part of the design. A CSV-defined model should be
inspectable after load and exportable again after fit. That supports two
important workflows:

- verify that import is identity-preserving before a long run
- capture a fitted cluster model in a human-reviewable tabular form

## Related pages

- [`concepts/group_and_cluster_lensing.md`](../concepts/group_and_cluster_lensing.md)
  — the physics motivating cluster-scale composition.
- [`api/mass_profile_catalog.md`](./mass_profile_catalog.md) — profile
  classes the CSV rows reference.
