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

PyAutoFit's aggregator
loads completed fits in bulk: every fit under a parent output directory,
each accessible as a `samples`, `model`, `fit`, or derived-quantity
object. The optional SQLite-backed database scales the same surface to
thousands of fits.

## When you need this

Use the aggregator when the unit of work is no longer one fit. For a
single result, ordinary result loading is simpler. For a sample of fits,
the aggregator gives you one query surface over all of them. Once the fit
count gets large, the database-backed version is the stable default.

## Aggregator basics

The current durable implementation is in
`PyAutoFit:autofit/database/aggregator/aggregator.py`.

Typical flow:

```python
agg = af.Aggregator.from_database("results.sqlite", completed_only=True)
samples = agg.values("samples")
models = agg.values("model")
```

An aggregator iterates over `Fit` objects. Each fit exposes stored
artifacts by key, and `values(name)` collects one key from every matching
fit.

## Filtering and querying

The query API is object-based. The docs expose:

- `aggregator.search` for fit-level fields like `name`, `unique_tag`,
  `path_prefix`, `is_complete`, and `is_grid_search`
- `aggregator.model` for queries against the best-fit model structure

Queries return a new aggregator, so filtering, ordering, and slicing stay
composable instead of mutating the original object.

## Map/reduce over the aggregator

`agg.map(func)` is the standard derived-quantity pattern. Apply a
per-fit function, collect the output, and turn it into a table, plot, or
export. This is how you build sample-level products such as Einstein
radius tables, evidence comparisons, magnification summaries, or quality
flags.

## Database backend

The database layer matters because it separates result scraping from
result querying. The documented entry points are:

- `af.Aggregator.from_database(...)` to open or create the SQLite view
- `agg.add_directory(...)` to scrape an output tree into that database
- `grid_searches()`, `children()`, and `cell_number(...)` for
  grid-search-specific traversal

This is the right tool for large survey runs, sensitivity maps, and any
workflow where you will query the same result collection repeatedly.

## Workflow outputs (CSV / FITS / PNG)

The workspace `guides/results/` and `guides/results/workflow/` examples
use the aggregator as the extraction layer between completed fits and
science-ready products. The stable pattern is:

1. query the subset of fits you care about
2. load or derive the quantity of interest per fit
3. export it in a uniform table or image naming scheme

That keeps the expensive fitting stage separate from cheap, repeatable
post-processing.

## Related pages

- [`concepts/samples_and_posteriors.md`](../concepts/samples_and_posteriors.md)
  — per-fit `Samples` interface the aggregator generalises.
- [`concepts/hierarchical_models.md`](../concepts/hierarchical_models.md)
  — graphical models consume aggregator output.
