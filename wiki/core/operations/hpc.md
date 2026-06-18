---
title: HPC and cluster runs
sources:
  - project: autolens_workspace
    paths:
      - scripts/guides/hpc/README.md
      - scripts/guides/hpc/example_cpu.py
    pinned_commit: main
last_updated: 2026-05-22
---

# HPC and cluster runs

PyAutoLens fits are CPU-bound (and increasingly GPU-bound with JAX). For
publication-quality runs — pixelised sources, SLaM pipelines, large parameter spaces —
runtimes are hours to days. Running on a cluster shortens that and lets you batch many
lenses in parallel.

This page is the high-level guide. The canonical worked example is
`autolens_workspace:scripts/guides/hpc/example_cpu.py` and the `batch/` subfolder
beside it.

## CPU parallelism

PyAutoFit's non-linear searches accept a `number_of_cores` argument:

```python
search = af.Nautilus(
    path_prefix="...",
    name="...",
    n_live=200,
    number_of_cores=16,  # parallel likelihood evaluations
)
```

Set this to the number of CPU cores on your node. PyAutoFit dispatches likelihood
evaluations across them via multiprocessing.

## JAX on GPU

With JAX installed against CUDA, the likelihood evaluations and array ops will run
on the GPU automatically. A modern consumer GPU (24 GB VRAM) handles galaxy-scale
fits comfortably. Cluster-scale or pixelised fits with large meshes need 40+ GB.

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
