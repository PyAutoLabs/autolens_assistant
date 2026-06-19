---
title: HPC infrastructure shipped with the assistant
sources:
  - project: autolens_assistant
    paths:
      - hpc/template.py
      - hpc/batch_gpu/template
      - hpc/batch_cpu/template
      - hpc/sync
    pinned_commit: main
last_updated: 2026-06-19
---

# HPC infrastructure shipped with the assistant

This page documents the concrete HPC machinery that ships in `autolens_assistant:hpc/`:
the pipeline template, the SLURM batch submit templates, and the bidirectional `sync`
script. For the *science* of cluster runs (CPU parallelism, JAX on GPU, memory budgeting),
see [`operations/hpc`](./hpc.md). For dataset layout and `info.json`, see
[`operations/dataset`](./dataset.md).

## Directory structure

```
hpc/
├── template.py            # Python pipeline template (HPC arg-parsing interface)
├── batch_gpu/             # GPU submit template + SLURM log dirs (output/, error/)
│   └── template
├── batch_cpu/             # CPU submit template + SLURM log dirs (output/, error/)
│   └── template
├── sync                   # bidirectional sync + job-control script (local ↔ HPC)
├── sync.conf.example      # template config for sync (copy to sync.conf, gitignored)
├── sync_jump.conf.example # example two-hop / relay-host config
└── .gitignore             # ignores sync.conf, sync_jump.conf, subhalo/
```

## Pipeline template — `hpc/template.py`

The interface between the batch scripts and PyAutoLens modeling code. Copy it into
`scripts/` (e.g. `scripts/imaging.py`) and fill in the `Model, Analysis & Search` section
of `fit()`; the [`init-slam`](../../../skills/init-slam.md) skill automates this. It parses
`--sample`, `--dataset`, `--iterations_per_quick_update`, `--number_of_cores`, `--use_cpu`,
loads `config/`+`output/` paths, and reads the dataset's `info.json` via
`info.get(key, default)` (see [`operations/dataset`](./dataset.md)). The HPC interface
(`parse_fit_args`, `__main__`, `--use_cpu`, `--number_of_cores`) must be preserved — the
batch templates depend on it.

## Submit templates — GPU vs CPU

Each batch folder ships one generic `template`. Both run one dataset per SLURM array task
and call `python3 $PROJECT_PATH/scripts/$SCRIPT` (set `SCRIPT` to your pipeline filename).
Differences:

| | GPU (`batch_gpu/template`) | CPU (`batch_cpu/template`) |
|---|---|---|
| Partition | `--partition=gpu` | `--partition=cpu` |
| GPU | `--gres=gpu:1` | none |
| CPUs | `--cpus-per-task=1` | `--cpus-per-task=4` |
| Memory | `--mem=32gb` | `--mem=64gb` |
| Wall time | `--time=08:00:00` | `-t 18:00:00` |
| JAX | uses GPU by default | forces `JAX_PLATFORM_NAME=cpu` |
| Thread pinning | none | `OPENBLAS/MKL/OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK` |
| Echo block | includes `nvidia-smi` | no `nvidia-smi` |
| Python args | `--sample --dataset` | adds `--use_cpu --number_of_cores=$THREADS` |

The CPU template also exports `JAX_PLATFORMS=cpu`, `VECLIB_MAXIMUM_THREADS`,
`NUMEXPR_NUM_THREADS`, and `NPROC`, all pinned to `$SLURM_CPUS_PER_TASK`.

### Checklist after copying (edit both `batch_gpu/template` and `batch_cpu/template`)

1. `#SBATCH -J <job_name>` — SLURM queue name.
2. `#SBATCH --array=0-N` — N = number of datasets minus 1.
3. `SCRIPT=<filename>.py` — the pipeline in `scripts/` to run.
4. `sample=<sample_name>` — matches the subdirectory under `dataset/`.
5. `datasets=(...)` — one dataset name per line, in array-index order.

To test a single lens, set `--array=0-0` and put just that lens in `datasets=(...)`.

## `hpc/sync` — bidirectional project sync

A single script for all transfer and job management between local and HPC. Set up with
`cp hpc/sync.conf.example hpc/sync.conf` and edit `HPC_HOST`, `HPC_BASE`, `PROJECT_NAME`
(remote path is `$HPC_HOST:$HPC_BASE/$PROJECT_NAME`). `sync.conf` is gitignored.

**Transfer:** `push` (code+config+data), `push --no-data`, `pull` (logs then results),
`logs` (logs only, fast mid-run), `sync` (push then pull), `push-data-init` (fast first
dataset upload via tar), `pull-full` (fast full output download), `status` (dry run).

**Jobs:** `submit [gpu|cpu] <script>`, `push-submit [gpu|cpu] <script>`, `jobs` (squeue),
`sacct`, `cancel <job_id>`, `wait-and-pull [secs]`.

**Inspect:** `tail [gpu|cpu]`, `du`, `check`, `clear-logs [gpu|cpu]`.

**What syncs:** push code = `config/`, `hpc/`, `scripts/` + root files; push data =
`dataset/` (with `--ignore-existing`, so FITS already on the HPC are never re-sent); pull =
SLURM logs + `output/` (excluding `search_internal/`). Always excluded: `__pycache__/`,
`*.pyc`, `.git/`, `*.egg-info/`, `sync.conf`.

> **Concurrency caution.** `remove_search_internal()` in PyAutoFit uses an unguarded
> `shutil.rmtree`; two concurrent SLURM array tasks chaining off the same cached base SLaM
> result can race on cleanup and one crashes with `FileNotFoundError`. Submit such chained
> jobs serially.

## See also

- [`operations/hpc`](./hpc.md) — the science of cluster runs.
- [`operations/dataset`](./dataset.md) — dataset layout and `info.json`.
- The [`start-new-project`](../../../skills/start-new-project.md) skill — full new-project
  workflow including HPC template setup.
