---
title: HPC and cluster runs
sources:
  - project: autolens_workspace
    paths:
      - scripts/guides/hpc/README.md
      - scripts/guides/hpc/example_cpu_and_gpu.py
      - scripts/imaging/features/pixelization/cpu_fast_modeling.py
    pinned_commit: main
  - project: PyAutoArray
    paths:
      - autoarray/config/setup_rules.yaml
      - autoarray/setup/setup.py
      - autoarray/dataset/imaging/dataset.py
    pinned_commit: e261e6d6f9894ef50d4302f4fc63482b5a989acd
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/analysis/setup_util.py
      - autogalaxy/analysis/analysis/setup.py
    pinned_commit: 9c3916391d76bd9c68db3a1bdd29b567386ad621
  - project: PyAutoFit
    paths:
      - autofit/non_linear/parallel/pool.py
    pinned_commit: 67164d229030bc8dbfc27ab68e5bf2fbfbf1f1cb
last_updated: 2026-11-26
content_sha256: 76b0329226334069a2424acb1b11af7f61bacddba162fb518d3ac02120840ada
---

# HPC and cluster runs

PyAutoLens fits are CPU-bound (and increasingly GPU-bound with JAX). For
publication-quality runs — pixelised sources, SLaM pipelines, large parameter spaces —
runtimes are hours to days. Running on a cluster shortens that and lets you batch many
lenses in parallel.

This page is the high-level guide. The canonical worked example is
`autolens_workspace:scripts/guides/hpc/example_cpu_and_gpu.py` and the `batch_cpu/` /
`batch_gpu/` subfolders beside it.

## Compute setup — let `setup="auto"` choose

How a likelihood is computed (backend, device, operator, precision) is its **compute setup**,
named by a setup_id `<backend>_<device>_<operator>_<precision>[_<transformer>]`, for example
`numba_cpu_sparse_fp64`. On a cluster it is the biggest runtime lever after the model itself,
and the right choice depends on the **source model** and the **hardware**. Choosing wrong on
CPU costs days.

Give every analysis `setup="auto"` and every search `number_of_cores="auto"`, and let the
libraries choose when each fit starts:

```python
analysis = al.AnalysisImaging(dataset=dataset, setup="auto")
settings_search = af.SettingsSearch(
    path_prefix="...", unique_tag="...", session=None, number_of_cores="auto"
)
```

`setup="auto"` looks up the designated setup in the rule table
(`PyAutoArray:autoarray/config/setup_rules.yaml`, chosen from profiling evidence; do not
hand-edit it) by three keys:

- **Likelihood**: the dataset type and a variant read from the model
  (`PyAutoGalaxy:autogalaxy/analysis/setup_util.py`): `mge` when the model has no
  pixelization (parametric, linear and MGE light profiles), else the mesh, `rectangular`,
  `delaunay` or `delaunay_nn`.
- **Hardware class**: `gpu_a100` when the fit sees a GPU, else `cpu_many_core`. A GPU that
  is not an A100, or a CPU machine with fewer than 16 cores (a laptop), uses the same rule
  and the setup is marked `extrapolated`.
- **Regime**: only `standard` is designated so far.

For imaging the rules are:

| Imaging source model | CPU node (`cpu_many_core`) | A100 node (`gpu_a100`) |
|---|---|---|
| Parametric / MGE (e.g. SOURCE LP) | `jax_cpu_dense_fp64` | `jax_gpu_dense_fp64` |
| Rectangular or Delaunay pixelization (SOURCE PIX, LIGHT, MASS) | `numba_cpu_sparse_fp64` | `jax_gpu_dense_fp64` |

Each pixelized rule also names a second choice, on the JAX sparse operator:
`jax_cpu_sparse_fp64` on a CPU node and `jax_gpu_sparse_fp64` on an A100. `setup="auto"`
picks the first; pass the second as a setup_id to use it. Interferometer, group,
multi-galaxy, datacube and point-source likelihoods have rows of their own in the same
table.

The resolved setup is applied for you: it sets the analysis backend (JAX or not) and
attaches the operator it names to the dataset (`dataset.apply_setup`,
`PyAutoArray:autoarray/dataset/imaging/dataset.py`). For a `sparse` setup that is
`apply_sparse_operator()` on the JAX backend and `apply_sparse_operator_cpu()` on the numba
backend, so no script calls either by hand. Each fit logs its choice as a `Setup:` line and
writes it to `files/setup.json`.

**`number_of_cores="auto"`** is resolved by PyAutoFit after the setup
(`PyAutoFit:autofit/non_linear/parallel/pool.py`): one process for a JAX analysis (JAX
parallelises inside the likelihood and disables Python multiprocessing), otherwise the cores
the job may use (`SLURM_CPUS_PER_TASK`, then CPU affinity, then `os.cpu_count()`). An int is
honoured, except that a JAX analysis still runs one process. The fit logs a `Parallel:` line
and writes `files/parallel.json`.

So on a CPU node a parametric fit runs JAX in one process, and a pixelized fit runs the numba
sparse operator with one serial likelihood per core. On an A100 both run JAX on the device in
one process.

A **SLaM pipeline spans both regimes**: SOURCE LP is parametric, every stage after it is
pixelized. With `setup="auto"` each stage resolves its own setup from its model, so one
dataset and one `af.SettingsSearch(..., number_of_cores="auto")` serve every stage.

**Which release.** From release 2026.11.26.1 `setup="auto"` and `number_of_cores="auto"`
are the defaults, and an explicit `use_jax=` with no `setup` opts out. Up to release
2026.11.25.1 the analyses default to `setup=None` (JAX on, nothing chosen automatically),
so pass `setup="auto"` explicitly on those.

**Overrides.** `setup="<setup_id>"` uses that setup as given. The `PYAUTO_SETUP` environment
variable steers `setup="auto"`: `cpu` or `gpu` forces that hardware class, and a full
setup_id replaces the rule for every analysis. The assistant's HPC scripts expose the same
values as `--setup <auto|cpu|gpu|setup_id>` (see
[`operations/hpc_infrastructure`](./hpc_infrastructure.md)). The explicit route without a
setup still works: `dataset.apply_sparse_operator_cpu()`, `use_jax=False` and
`number_of_cores=N` for the pixelized stages, as in
`autolens_workspace:scripts/imaging/features/pixelization/cpu_fast_modeling.py`.

## JAX on GPU

With JAX installed against CUDA, the likelihood evaluations and array ops run on the GPU.
`setup="auto"` sees the GPU and picks the `gpu_a100` rules. A modern consumer GPU (24 GB
VRAM) handles galaxy-scale fits comfortably. Cluster-scale or pixelized fits with large
meshes need 40+ GB.

Set `XLA_PYTHON_CLIENT_PREALLOCATE=false` if running multiple JAX processes on the
same node (e.g. one per lens in a batch) to prevent each one from pre-allocating
all available VRAM.

## Batch submission

Most HPC sites use SLURM. One lens is one job; a sample is a **job array**, one lens per
array task, because lenses are independent and every pipeline stage takes
`--sample`/`--dataset` arguments. The assistant ships array templates
(`hpc/batch_cpu/template`, `hpc/batch_gpu/template`) for that.

A skeleton job script, for reference:

```bash
#!/bin/bash
#SBATCH --job-name=lens_fit
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --array=0-99
#SBATCH --output=slurm-%A_%a.out

source /path/to/venv/bin/activate
export NUMBA_CACHE_DIR=$TMPDIR/numba_cache
export MPLCONFIGDIR=$TMPDIR/matplotlib

python scripts/run_fit.py --lens-index=$SLURM_ARRAY_TASK_ID
```

Cache dirs go to `$TMPDIR` so each job gets its own scratch space.

## Running a campaign

Once a sample runs through several stages (SOURCE LP → SOURCE PIX → MASS) with hundreds of
lenses, the hard part is no longer one job script. It is knowing what to ask for, what
failed and why, what to resubmit, and what it all cost. A **campaign** handles that: one
`hpc/campaign.yaml` declares the manifest, the stages, their resources and how each stage
waits for the one before, and `hpc/sync` drives PyAutoFit's campaign tools on the cluster.

1. **Plan before you submit.** `hpc/sync plan hpc/campaign.yaml` proposes CPUs, memory,
   wall time and an ETA per stage from profiling evidence and, once you have one, a pilot.
   Every number carries a grade saying how good its evidence is.
2. **Pilot a small slice first** (1–2 % of the manifest, spread over object sizes), then
   plan again from what the pilot measured. Most failures of a big campaign (memory asked
   for and never used, wall times too short) show up in a pilot.
3. **Submit** the campaign once the plan is agreed.
4. **Check in** with `hpc/sync status hpc/campaign.yaml`: a short digest of counts, wall
   time and memory against what was asked, timeouts, out-of-memory kills and other
   failures, each failed task listed by class.
5. **Triage**: `hpc/sync resubmit ... --stage S --class timeout` writes a resubmit
   *proposal* sized from the failed tasks' own measurements (a timeout gets p95 + 25 % wall
   time, an out-of-memory kill 1.5× its peak). Nothing is resubmitted until someone
   approves it and runs `hpc/sync act resubmit`.
6. **Report**: `hpc/sync report hpc/campaign.yaml --site ral` writes the compute, failure
   census and an energy and carbon *estimate* (Green Algorithms model, with a range) with a
   paragraph you can put in a paper.

Every change to jobs already queued (`hold`, `release`, `throttle`, `update-pending`,
`resubmit`, `cancel`) goes through `hpc/sync act` and is written to the campaign's
`actions.log`. The machinery is documented in
[`operations/hpc_infrastructure`](./hpc_infrastructure.md); the
[`hpc_campaign`](../../../skills/hpc_campaign.md) skill walks through it.

## Persisting outputs

The `output/` folder is written incrementally during the fit. If your scheduler
kills the job, you can resume from the same path — PyAutoFit detects the existing
output via the `unique_id` hash and continues.

For long-running fits, write `output/` to a persistent filesystem (`/scratch` or
`/data`), not to `$TMPDIR` which is purged at job end.

## Multi-node

For very expensive single fits (high-D inversions, many-galaxy clusters), MPI
parallelism is available via PyAutoFit's MPI integration. Less common than
single-node multi-core; see the workspace HPC guide for the exact incantation.

## Common gotchas

- **Numba cache collisions.** Two jobs sharing `$NUMBA_CACHE_DIR` will corrupt each
  other. Always use `$TMPDIR` or a PID-suffixed directory.
- **Matplotlib font cache.** Same issue. Same fix.
- **`output/` clashes.** If you launch the same script twice with the same
  `path_prefix` + `name` + model + dataset, they share a `unique_id` folder. Use a
  per-job `unique_tag` to distinguish them.
- **Memory pressure during inversions.** Pixelised inversions allocate dense matrices
  that grow with the source mesh resolution. For (50, 50) meshes budget ~32 GB.

## See also

- `autolens_workspace:scripts/guides/hpc/` — canonical recipes and batch templates.
- [`operations/hpc_infrastructure`](./hpc_infrastructure.md) — the `hpc/` kit and `hpc/sync`
  commands shipped with the assistant.
- [`operations/sandbox`](./sandbox.md) — env vars to set.
- [`operations/installation`](./installation.md) — JAX with GPU support.
