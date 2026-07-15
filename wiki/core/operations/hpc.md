---
title: HPC and cluster runs
sources:
  - project: autolens_workspace
    paths:
      - scripts/guides/hpc/README.md
      - scripts/guides/hpc/example_cpu.py
      - scripts/imaging/features/pixelization/cpu_fast_modeling.py
    pinned_commit: main
last_updated: 2026-07-15
---

# HPC and cluster runs

PyAutoLens fits are CPU-bound (and increasingly GPU-bound with JAX). For
publication-quality runs — pixelised sources, SLaM pipelines, large parameter spaces —
runtimes are hours to days. Running on a cluster shortens that and lets you batch many
lenses in parallel.

This page is the high-level guide. The canonical worked example is
`autolens_workspace:scripts/guides/hpc/example_cpu.py` and the `batch/` subfolder
beside it.

## CPU acceleration — two regimes

On CPU there are **two different accelerators**, and which one is correct depends on the
**source model**. This is the biggest CPU runtime lever; choosing wrong costs days.

| Fit type | Accelerator | `use_jax` | `number_of_cores` | Dataset |
|---|---|---|---|---|
| Parametric source (e.g. SOURCE LP) | JAX | `True` | leave unset | plain |
| Pixelised source (SOURCE PIX, LIGHT, MASS) | Sparse operators (numba) | `False` | node core count | `apply_sparse_operator_cpu()` |

**JAX is not GPU-only.** For *parametric* fits it vectorises the likelihood and parallelises
efficiently on CPU, and it is the right choice there even with no GPU present. Because JAX
disables Python multiprocessing, such a fit gains nothing from `number_of_cores` — leave it
unset (it defaults to 1).

**Pixelised sources use sparse operators instead.** Pixelised reconstruction leans on sparse
linear algebra; `dataset.apply_sparse_operator_cpu()` precomputes operator matrices once
(seconds to minutes) which every later pixelised fit reuses, for a large CPU speed-up. The
implementation is numba-based and does **not** support JAX, so pair it with `use_jax=False`
and multiprocessing:

```python
# Parametric source on CPU — JAX, no number_of_cores.
analysis = al.AnalysisImaging(dataset=dataset, use_jax=True)
settings_search = af.SettingsSearch(path_prefix="...", unique_tag="...", session=None)

# Pixelised source on CPU — sparse operators, JAX off, multiprocessing on.
dataset = dataset.apply_sparse_operator_cpu()
analysis = al.AnalysisImaging(dataset=dataset, use_jax=False)
settings_search = af.SettingsSearch(
    path_prefix="...", unique_tag="...", session=None, number_of_cores=16
)
```

`number_of_cores` reaches the search via `af.SettingsSearch` (one of `search_dict`'s fixed
keys). PyAutoFit then dispatches likelihood evaluations across those cores.

A **SLaM pipeline spans both regimes**: SOURCE LP is parametric (JAX), every stage after it is
pixelised (sparse/CPU) — so build two `SettingsSearch` objects and two datasets. Worked example:
`autolens_workspace:scripts/imaging/features/pixelization/cpu_fast_modeling.py`.

## JAX on GPU

With JAX installed against CUDA, the likelihood evaluations and array ops will run
on the GPU automatically. A modern consumer GPU (24 GB VRAM) handles galaxy-scale
fits comfortably. Cluster-scale or pixelised fits with large meshes need 40+ GB.
On GPU, JAX is used throughout the pipeline and the sparse operator is not applied
(it is CPU/numba-only).

Set `XLA_PYTHON_CLIENT_PREALLOCATE=false` if running multiple JAX processes on the
same node (e.g. one per lens in a batch) to prevent each one from pre-allocating
all available VRAM.

## Batch submission

Most HPC sites use SLURM. A skeleton `submit.sbatch`:

```bash
#!/bin/bash
#SBATCH --job-name=lens_fit
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=slurm-%j.out

source /path/to/venv/bin/activate
export NUMBA_CACHE_DIR=$TMPDIR/numba_cache
export MPLCONFIGDIR=$TMPDIR/matplotlib

python scripts/run_fit.py
```

Cache dirs go to `$TMPDIR` so each job gets its own scratch space.

For per-lens batches:

```bash
#SBATCH --array=0-99
python scripts/run_fit.py --lens-index=$SLURM_ARRAY_TASK_ID
```

The workspace `scripts/guides/hpc/batch/` folder has fuller templates.

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
- [`operations/sandbox`](./sandbox.md) — env vars to set.
- [`operations/installation`](./installation.md) — JAX with GPU support.
