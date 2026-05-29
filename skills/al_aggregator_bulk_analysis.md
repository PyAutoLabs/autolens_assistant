---
name: al_aggregator_bulk_analysis
description: Operate on many completed lens fits at once via PyAutoFit's `Aggregator` — load samples, models, fits, derived quantities across an entire output directory; filter, sort, query; export to CSV/FITS/plots. Use when you've fitted N>1 lenses (SLACS sample, cluster members, sensitivity-map cells) and need to extract a comparable result table or run derived calculations across the lot. Pairs with `al_hierarchical_inference` (which builds population models on top). Writes a runnable Python script in ./work/. **Status: stub.**
---

# Bulk analysis across many completed fits

`al_load_results` loads one fit. The aggregator loads N — every fit in a
parent output directory, queryable by metadata, with lazy access to
samples, models, fits, and derived quantities. It's the difference between
"inspect this one result" and "produce the results table for a paper".

The result database (an optional SQLite layer) makes per-fit queries cheap
for very large samples (1000s of fits).

Workspace path: `autolens_workspace:scripts/guides/results/start_here.py`,
`scripts/guides/results/aggregator/`,
`scripts/guides/results/database/start_here.py`,
`scripts/guides/results/workflow/`.

## Ask

- *"Where do the fits live — one output folder per lens under a common
  parent?"* (`output/<sample>/<lens>/` is the standard layout.)
- *"What do you want out — a CSV of best-fit parameters, FITS stacks of
  model images, posterior PDF plots, or all three?"*
- *"How many fits — handful, hundreds, thousands?"* Thousands → enable
  the database backend.
- *"Filter criteria — all lenses, lenses meeting a quality cut, only
  fits with a converged subhalo grid?"*

## Branch — aggregator basics

> TODO: recipe. Pattern: `agg = af.Aggregator(af.db.open_database("sqlite://"))`,
> then `agg.add_directory("output/sample/")` and iterate with
> `for samples in agg.values("samples"): ...`. See
> `PyAutoFit:autofit/aggregator/...`.

## Branch — derived quantities + CSV export

> TODO: recipe. Pattern: build a per-fit derived quantity (Einstein
> radius, magnification at source position, log-evidence) via
> `agg.map(...)`; collect into a `pandas.DataFrame`; write to CSV.

## Branch — database backend for large samples

> TODO: recipe. Pattern: `agg = af.Aggregator.from_database("results.sqlite")`,
> `agg.add_directory(...)`; queries are SQLAlchemy-backed. See workspace
> database tutorial.

## Branch — FITS / PNG batch outputs

The `workflow/` examples wrap aggregator output into automated FITS
stacks (model image, residuals, source map) and PNG sets per fit.

> TODO: recipe.

## Combine

- [`al_load_results`](./al_load_results.md) — the single-fit primitive
  the aggregator generalises.
- [`al_hierarchical_inference`](./al_hierarchical_inference.md) —
  population-level inference on top of bulk-loaded per-lens results.
- [`al_sensitivity_mapping`](./al_sensitivity_mapping.md) — sensitivity
  outputs are a canonical "many fits" workload.

## Further reading

- **Student / new to lensing** — _ (data-engineering layer rather than
  lensing physics).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  results / aggregator section.
- **Experienced PyAutoLens user** — [workspace/lens: guides/results/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/results/start_here.py):
  the entry point — sub-folders cover aggregator, database, workflow
  outputs.

See also [`wiki/core/api/aggregator.md`](../wiki/core/api/aggregator.md)
for the API surface.
