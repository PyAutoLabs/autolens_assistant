---
name: al_build_results_library
description: Turn hundreds or thousands of finished lens fits into a checked, shippable results library with PyAutoFit's results tools — index every result and its state, declare what should exist and list what is missing (with reasons), add a product to finished fits without rerunning them, export catalogue tables incrementally (sharded on a cluster), package them into checksummed part zips, verify a package, and compare a rebuild against a reference. Use for a lens sample or survey catalogue (Euclid, SLACS-scale and up), after a cluster campaign, or whenever "which fits are missing or broken?" matters more than loading one fit. For one fit use `al_load_results`; for querying a few fits use `al_aggregator_bulk_analysis`.
---

# Build and ship a results library

A survey's science lives in its catalogue, and a catalogue is only as good as its
**completeness**: every lens that should have a row has one, every row comes from the
right fit, and every missing lens is missing *for a stated reason*. With tens of fits
you can check that by eye. With thousands — a Euclid tile set, a cluster campaign —
you cannot, and the failures are silent: a fit that timed out simply has no output, a
rerun leaves its old copy beside the new one, a result copied into the wrong lens's
folder reads back as that lens. The Euclid DR1 catalogue build shipped all three.

This skill is the workflow PyAutoFit's results library (`autofit.results`,
`autofit.export`) was built for, from that experience. Read
[`wiki/core/operations/results_library.md`](../wiki/core/operations/results_library.md)
for the concepts — result states, the index, the declared library, honest exports —
before running anything large.

## Orient

Six steps, each a small script or one command, each re-runnable:

1. **Index** — classify every result on disk (completed, running, interrupted with a
   checkpoint, failed, corrupt, superseded by a later fit of the same search, never
   started) without loading any of them. Incremental: re-indexing after a few new fits
   opens only those.
2. **Declare and check** — say which (lens, search) results *should* exist and which
   products each needs (`image`, `latent`, `files/model.fits` …); get every gap with a
   reason in `<name>.missing.csv`.
3. **Enrich** (optional) — add a new product (a `coolest.json`, a WCS record) to
   finished fits, computed from the saved result, without rerunning anything.
4. **Export** — the catalogue tables (`AggregateCSV`), refreshed incrementally, a row
   *or a reason* for every expected lens, a `columns.json` saying what each column
   is; shard it across array tasks and merge.
5. **Package and verify** — size-capped part zips with a manifest, checksums and a
   provenance README; `verify` before you publish.
6. **Compare** — a rebuild against the previous release, with run-to-run scatter as
   the yardstick rather than the quoted error bars.

The statistical point to keep in mind for step 6: two runs of the same sampler on the
same data are not bitwise reproducible, and their medians can differ by much more than
their quoted 1σ (two Nautilus runs differed by a median z of 15 in the DR1 tests). A
parity check that demands "within 3σ" will fail reruns that are scientifically
identical — measure the scatter first.

## Ask

- *"Where are the results — one output root, or several (`output/`, `output_sed/`)?
  On this machine or on the cluster?"* (On the cluster, run steps 1–2 there with
  `hpc/sync results`; never pull `output/` just to count it.)
- *"Is there a manifest of what you ran — an hpc campaign (`hpc/campaign.yaml`) or a
  list of lens names?"* A campaign file is the best declaration: it already says what
  was run.
- *"Which products must every finished lens have?"*
- *"What is the deliverable — a CSV for a paper, a public data release, or a check that
  a rebuild reproduces the last release?"*

## Branch — index and status

```python
from autofit.results import ResultsIndex

index = ResultsIndex("output")          # several roots need index_dir=...
counts = index.update()                 # opens only new or changed results
print(counts)                           # scanned / new / changed / unchanged / removed
print(index.counts())                   # results per state
```

From the shell: `python -m autofit.results index output` then
`python -m autofit.results status output` (add `--state failed,corrupt_zip` to list
them). A read-only tree takes `--index-dir`. Source:
`PyAutoFit:autofit/results/index.py`, `PyAutoFit:autofit/results/classify.py`.

On the cluster, `hpc/sync results [root ...]` indexes there and pulls back only the
index (into `hpc/results/<root>/`) and `inspect/` — read it with
`python -m autofit.results status output --index-dir hpc/results/output`.

## Branch — declare and check completeness

Write `hpc/library.yaml` (or build it in Python):

```yaml
name: dr1_v1
roots: [../output, ../output_sed]
index_dir: ../hpc/results/index
datasets_file: ../hpc/run_manifests/sample.txt   # one lens per line (first field)
searches:
  source_lp: [image, latent, samples_summary]
  mass_total:
    products: [image, latent, files/model.fits]
```

or, after a campaign, simply `from_campaign: campaign.yaml` (each manifest line × each
stage with a `success.zip_complete`; its `success.members` are the required
products).

```python
import autofit as af

library = af.ResultsLibrary.from_yaml("hpc/library.yaml")
report = library.check()
print(report.summary())
report.write_missing_csv("hpc/results")
```

`python -m autofit.results check hpc/library.yaml` does the same and exits 1 while
anything is missing; `hpc/sync results check hpc/library.yaml` runs it on the cluster.
Every gap has a reason: `no_result`, `not_completed:<state>`,
`missing_product:<product>`, `location_mismatch`, `duplicate:<n>`. A large
`unexpected` count means you indexed the wrong tree. Source:
`PyAutoFit:autofit/results/library.py`, `PyAutoFit:autofit/results/completeness.py`.

## Branch — add a product to finished fits

```python
from autofit.aggregator import Aggregator

def einstein_radius_record(search_output):
    instance = search_output.instance
    return {"einstein_radius": instance.galaxies.lens.mass.einstein_radius}

agg = Aggregator.from_index("output")
report = agg.enrich(einstein_radius_record, name="einstein_radius")   # files/einstein_radius.json
print(report)
```

Atomic per result (a killed job leaves every zip whole), skips results that already
hold the product, and `shard="i/N"` splits the work across array tasks
(`python -m autofit.results enrich output --fn module:function --name NAME --shard $SLURM_ARRAY_TASK_ID/$N`).
Source: `PyAutoFit:autofit/results/enrich.py`.

## Branch — export the catalogue tables

```python
from autofit.aggregator import Aggregator
from autofit.aggregator.summary.aggregate_csv import AggregateCSV, ValueType

summary = AggregateCSV(Aggregator.from_index("output"), strict=False)
summary.add_variable(
    "galaxies.lens.mass.einstein_radius",
    name="einstein_radius",
    value_types=[ValueType.Median, ValueType.ValuesAt1Sigma],
    unit="arcsec",
    prior_edge=True,
)
summary.save(
    "catalogue/lens_mass.csv",
    cache=True,              # re-reads only new or changed results
    expected=report,         # a row with a reason for every expected lens not done
    on_error="row",          # a result that cannot be summarised gets a reason, not a crash
    sort_by="dataset",
    columns_json=True,       # catalogue/lens_mass.columns.json describes each column
)
```

For thousands of results, run `save(..., shard="i/N")` in N array tasks and merge with
`python -m autofit.results merge catalogue/lens_mass.csv part_*.csv` — byte-identical
to a serial export. Source: `PyAutoFit:autofit/aggregator/summary/aggregate_csv/`.

## Branch — package, verify, compare

```bash
python -m autofit.export package catalogue/ dist/ --cap-gb 10 --title "My lens catalogue v1" --repo .
python -m autofit.export verify dist/
python -m autofit.export compare new/lens_mass.csv old/lens_mass.csv --key dataset --exact ra,dec --report parity.md
```

`package` keeps each lens folder whole, writes `parts_manifest.csv`, `SHA256SUMS`,
`package.json` and a provenance README, and on a rebuild rewrites only the parts whose
files changed. `compare` fails on lenses gained, lost or duplicated, on changed
`--exact` columns and on `--gate`d value columns beyond `--threshold`; every other
value column reports its median and maximum z. Calibrate with
`af.export.scatter_between(run_a, run_b, paths)` on two runs of the same fits before
choosing a gate. Source: `PyAutoFit:autofit/export/`.

## Combine

- [`al_load_results`](./al_load_results.md) — inspect any one fit the library flags.
- [`al_aggregator_bulk_analysis`](./al_aggregator_bulk_analysis.md) — querying and
  plotting across fits once the library is complete.
- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — the `failed` and
  `corrupt_ckpt` rows of `missing.csv`.
- [`al_run_slam_pipeline`](./al_run_slam_pipeline.md) — the pipeline whose stages a
  campaign declares.
- [`wiki/core/operations/hpc_infrastructure.md`](../wiki/core/operations/hpc_infrastructure.md)
  — campaigns and `hpc/sync`.

Offer (default-yes) a dated `wiki/project/` entry when the library is first built and
at each release: what was expected, what is missing and why, the index hash, the
package's `SHA256SUMS`.

## Further reading

- **General reference** — [`wiki/core/operations/results_library.md`](../wiki/core/operations/results_library.md).
- **Experienced PyAutoFit user** — [workspace/fit: features/results_library.py](https://github.com/PyAutoLabs/autofit_workspace/blob/main/scripts/features/results_library.py):
  declare → index → check → enrich on the gaussian example.
