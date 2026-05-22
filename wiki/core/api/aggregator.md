---
title: Aggregator and result database
sources:
  - project: PyAutoFit
    paths:
      - autofit/aggregator
      - autofit/database
    pinned_commit: main
last_updated: 2026-05-22
---

# Aggregator and result database

**Status: stub — content to be filled out.** PyAutoFit's aggregator
loads completed fits in bulk: every fit under a parent output directory,
each accessible as a `samples`, `model`, `fit`, or derived-quantity
object. The optional SQLite-backed database scales the same surface to
thousands of fits.

## When you need this

> TODO: single fit → `al_load_results`. N>1 fits → aggregator. N >>
> few-hundred → database backend.

## Aggregator basics

> TODO: `af.Aggregator.from_directory(...)`, `agg.values("samples")`,
> per-key access pattern (`"model"`, `"samples"`, `"fit_imaging"`, …).
> Cite `PyAutoFit:autofit/aggregator/...`.

## Filtering and querying

> TODO: filter by search name, by completed-status, by metadata fields.
> Document the query API.

## Map/reduce over the aggregator

> TODO: `agg.map(func)` applies a per-fit function and collects the
> result. Common idiom for derived quantities (Einstein radius,
> log-evidence comparison).

## Database backend

> TODO: `af.SqliteAggregator(...)`; `db.add_from_directory(...)`;
> SQL-like queries. Cite `PyAutoFit:autofit/database/...`.

## Workflow outputs (CSV / FITS / PNG)

> TODO: the workspace `guides/results/workflow/` examples wrap
> aggregator output into automated export. Document the pattern; this
> page is the natural home until a dedicated workflow page exists.

## Related pages

- [`concepts/samples_and_posteriors.md`](../concepts/samples_and_posteriors.md)
  — per-fit `Samples` interface the aggregator generalises.
- [`concepts/hierarchical_models.md`](../concepts/hierarchical_models.md)
  — graphical models consume aggregator output.
