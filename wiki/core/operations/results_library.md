---
title: Results libraries — index, completeness, exports and releases
sources:
  - project: PyAutoFit
    paths:
      - autofit/results/index.py
      - autofit/results/classify.py
      - autofit/results/library.py
      - autofit/results/completeness.py
      - autofit/results/enrich.py
      - autofit/results/shard.py
      - autofit/aggregator/summary/aggregate_csv/__init__.py
      - autofit/export/package.py
      - autofit/export/verify.py
      - autofit/export/parity.py
    pinned_commit: main
  - project: autolens_assistant
    paths:
      - hpc/sync
    pinned_commit: main
last_updated: 2026-11-02
---

# Results libraries

A **results library** is a set of finished fits treated as one dataset: many lenses,
one or more searches each, and the products a catalogue is built from. The Aggregator
loads fits into Python; the results library answers the questions above it — *which*
fits exist, which are missing or broken and why, and how to turn the set into a
catalogue release that can be checked and reproduced. The workflow is the
[`al_build_results_library`](../../../skills/al_build_results_library.md) skill.

## Why it exists

The Euclid DR1 catalogue build (September–October 2026) took about 26 hours against a
4–5 hour estimate, needed ~4,200 lines of project-specific tooling, and still shipped
lenses with the wrong cut-out, duplicated lenses and silently missing lenses. Each
failure was quiet: the tools read whatever was on disk and assumed it was complete and
correct. The library makes every one of those failures loud.

## Result states

`python -m autofit.results index` classifies each result (one fit's `output_path`, as a
folder, a zip or both) from its small files only:

| State | Meaning |
|---|---|
| `completed` | `.completed` present and the zip reads back cleanly |
| `superseded` | completed, but a later fit of the same search and object exists (a rerun) |
| `running` | its status record says running and was written recently |
| `interrupted_valid_ckpt` | stopped early with a checkpoint it can resume from |
| `corrupt_ckpt` | stopped early and its checkpoint is unreadable |
| `corrupt_zip` | the zip cannot be read or fails its CRC check |
| `failed` | its status record says a Python exception ended it |
| `never_started` | a folder with no checkpoint, or a status record only |

The index is one JSON record per result under `<root>/.autofit_index/` (or
`--index-dir`) plus a local SQLite cache; re-indexing opens only results whose files
changed. An I/O error (common over network or WSL filesystems) is *unreadable this
time*, never *corrupt*.

## The declared library and completeness

A library declaration (`library.yaml`, `af.ResultsLibrary.grid`, or `from_campaign:`
an hpc `campaign.yaml`) lists the expected (dataset, search) results and the products
each must hold. `check` gives each one a status — `done`, `missing`, `incomplete`,
`failed`, `duplicate` — and a reason, and counts completed results nobody declared
(`unexpected`: usually the wrong tree, or an object-name convention that drifted). The
gaps go to `<name>.missing.csv`. Declaring from the campaign file means the file that
said what to run is the one that says what should exist.

## Honest exports

`AggregateCSV.save` can refresh incrementally (`cache=True`), give every expected lens a
row or a reason (`expected=`, `on_error="row"` → `status_reason`), describe every
column in `<name>.columns.json` (source path, parameter or latent, statistic,
`quantile_1sigma` bounds, unit, blank count), flag medians at a prior edge, and split
across array tasks (`shard="i/N"`) with a merge byte-identical to the serial export.

## Releases: package, verify, compare

`python -m autofit.export package` writes part zips (each lens folder whole, media
stored, text deflated), `parts_manifest.csv`, `SHA256SUMS`, `package.json` and a
provenance README (git revisions, the results-index hash); rebuilds rewrite only
changed parts so published checksums stay valid. `verify` checks a package end to end.
`compare` diffs two catalogue tables: identity and exact columns gate; value columns
report z = |a − b| / √(σa² + σb²) and gate only when named.

**Run-to-run scatter.** Independent sampler runs are not reproducible to their quoted
errors — two Nautilus runs of the same lens model on the same data differed by a median
z of 15 in DR1 tests. Measure the scatter between two runs
(`af.export.scatter_between`) before choosing any parity tolerance.

## On a cluster

`hpc/sync results [root ...]` indexes the roots on the cluster and pulls back only the
index (into `hpc/results/<root>/`) and `inspect/`; `hpc/sync results check
<library.yaml>` runs the completeness check there and pulls the gap list. Pulling the
whole `output/` tree to count it is never needed. The pulled index names the cluster's
paths, so read it with `--index-dir` and never re-index it locally.

## See also

- [HPC infrastructure](./hpc_infrastructure.md) — campaigns, `hpc/sync`.
- [`wiki/core/api/aggregator.md`](../api/aggregator.md) — loading fits.
