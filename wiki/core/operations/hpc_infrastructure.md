---
title: HPC infrastructure shipped with the assistant
sources:
  - project: autolens_assistant
    paths:
      - hpc/template.py
      - hpc/batch_gpu/template
      - hpc/batch_cpu/template
      - hpc/batch_cpu/stage
      - hpc/campaign.yaml.example
      - hpc/sync
    pinned_commit: main
last_updated: 2026-10-30
---

# HPC infrastructure shipped with the assistant

This page documents the concrete HPC machinery that ships in `autolens_assistant:hpc/`:
the pipeline template, the SLURM batch submit templates, the campaign stage entry and
example campaign file, and the `sync` script that drives all of it from your machine. For the *science* of cluster runs (CPU parallelism, JAX on GPU, memory budgeting),
see [`operations/hpc`](./hpc.md). For dataset layout and `info.json`, see
[`operations/dataset`](./dataset.md).

## Directory structure

```
hpc/
├── template.py            # Python pipeline template (HPC arg-parsing interface)
├── batch_gpu/             # GPU submit template + SLURM log dirs (output/, error/)
│   └── template
├── batch_cpu/             # CPU submit template + SLURM log dirs (output/, error/)
│   ├── template
│   └── stage              # one campaign stage for one manifest line (see Campaigns)
├── campaign.yaml.example  # an example campaign: three SLaM stages over a manifest
├── campaign/<name>/       # created by `hpc/sync status|plan|report`: the pulled digest
├── sync                   # sync, job control and campaign verbs (local ↔ HPC)
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

### Partition rule — CPU arrays never go on `gpu` (human rule, 2026-09-30)

- Bulk/production CPU-only arrays use the cluster's CPU partition only (on RAL:
  `--partition=ral`) — never `gpu`, `ral,gpu` or `gpu,ral`, even when the CPU nodes are
  drained or busy; the jobs wait for them instead. On 2026-09-30 euclid_dr1 CPU arrays
  submitted with `ral,gpu` took all 124 CPUs on euclid-ral-gpu-1/-2, leaving all 8 A100s
  idle but unschedulable for hours with 3,938 CPU tasks queued eligible for those nodes.
- Only exemption: small bounded CPU timing legs (e.g. autolens_profiling quiet-node timing)
  may use `gpu` without `--gres` when **all** hold: ≤8 CPUs/task, array throttle ≤`%2`, and
  `squeue -p gpu -t PD` shows no pending job requesting gres/gpu.
- A partition name is not a device: before calling a job a "GPU run", check its TRES for
  `gres/gpu` in `scontrol show job <id>`; for a stuck A100 job compare the node's
  `AllocTRES` cpu against `CfgTRES`.
- Never reorder, hold or cancel another campaign's jobs without the human's OK.

Source: human instruction, 2026-09-30 (RAL `gpu`-partition incident).

### Checklist after copying (edit both `batch_gpu/template` and `batch_cpu/template`)

1. `#SBATCH -J <job_name>` — SLURM queue name.
2. `#SBATCH --array=0-N` — N = number of datasets minus 1.
3. `SCRIPT=<filename>.py` — the pipeline in `scripts/` to run.
4. `sample=<sample_name>` — matches the subdirectory under `dataset/`.
5. `datasets=(...)` — one dataset name per line, in array-index order.

To test a single lens, set `--array=0-0` and put just that lens in `datasets=(...)`.

## Campaigns — many lenses, several stages, one file

For a sample (tens to thousands of lenses through several pipeline stages) the hand-edited
array templates above stop scaling: every stage needs its own array, resubmits are done by
hand and nobody knows what failed where. A **campaign** puts all of that in one file and
lets PyAutoFit (`python -m autofit.campaign`) submit it, follow it and report on it.

- **`hpc/campaign.yaml`** (copy `campaign.yaml.example`): the manifest (one object per line;
  its 0-based line number is the object's *campaign index*), the stages in order, each
  stage's resources, its dependency on the stage before (`aftercorr`, index by index), the
  check that says a stage succeeded, and the site (`site: ral`, the PyAutoNerves site file
  with partitions, limits and power/carbon constants). `project_root` must be the project's
  path on the cluster, `$HPC_BASE/$PROJECT_NAME`.
- **`hpc/batch_cpu/stage`**: what each stage runs. It reads its manifest line, calls
  `scripts/<STAGE_SCRIPT>` with `--sample=... --dataset=...` (names from
  `MANIFEST_FIELDS`), pins threads, forwards the pre-timeout `USR1` signal to the fit so it
  saves its checkpoint, and writes a small **task record**
  (`output/.campaign_tasks/<campaign>/<stage>/<index>.status.json`) before Python starts.
  The record is removed when the stage succeeds and becomes a `failed` record when it does
  not, so a task that died before the fit could write its own status (a missing manifest
  line, a broken environment) still shows up in the digest.
- **The digest**: `hpc/sync status hpc/campaign.yaml` asks the cluster for the scheduler's
  accounting and the fits' status records, joins them, and pulls back a summary of at most
  2 KB (`digest.md`) plus `failed_<class>.txt` lists into `hpc/campaign/<name>/`.

PyAutoFit writes every batch script itself, with the partition check built in: CPU-only
work never goes on a GPU partition (rule below), and a resubmit is only ever a
*proposal* that a person approves.

## `hpc/sync` — drive the project on the cluster without typing ssh

A single script for transfer, jobs and campaigns. Set up with
`cp hpc/sync.conf.example hpc/sync.conf` and edit `HPC_HOST`, `HPC_BASE`, `PROJECT_NAME`
(remote path is `$HPC_HOST:$HPC_BASE/$PROJECT_NAME`). `sync.conf` is gitignored.
`hpc/sync help` works before it exists.

**Transfer:** `push` (code+config+data), `push --no-data`, `pull [dir ...]` (logs then
results; name result roots to pull only those, `PYAUTO_PULL_DIRS` adds roots), `logs`
(logs only, fast mid-run), `sync` (push then pull), `push-data-init` (fast first dataset
upload via tar), `pull-full` (fast full output download), `status [dir ...]` (dry run).

**Jobs:** `submit [gpu|cpu] <script> [sbatch arg ...]` (extra arguments go to `sbatch`,
e.g. `--export=ALL,SAMPLE=my_sample`), `push-submit ...`, `jobs` (squeue), `sacct`,
`cancel <job_id>`, `wait-and-pull [secs]`.

**Campaigns** (each one ssh call running `python -m autofit.campaign` on the cluster, then a
pull of the campaign's small files into `hpc/campaign/<name>/`):

| Command | What it does | Changes the queue? |
|---|---|---|
| `status hpc/campaign.yaml` | collect accounting + status records, print the digest | no |
| `plan hpc/campaign.yaml [--evidence ... --idle-cpus ral=N]` | propose CPUs, memory, wall time, throttle, ETA from a pilot and profiling evidence, every number graded | no |
| `resubmit hpc/campaign.yaml --stage S --class C` | write a resubmit proposal sized from the failed tasks' own measurements | no |
| `report hpc/campaign.yaml [--site ral]` | end-of-campaign report: compute, energy and carbon estimate, failures, a paper paragraph | no |
| `act <action> <campaign.yaml\|name> <arg ...>` | `hold`, `release`, `throttle`, `update-pending`, `resubmit <proposal>`, `cancel` | **yes** |

`act` is the only verb that changes jobs already in the queue, and `submit`/`push-submit`
are the only ones that start jobs. Every `act` (and the old `cancel`, which is `act cancel`
under the campaign `adhoc`) appends one JSON line `{utc, user, campaign, action, args,
exit}` to `campaign/<name>/actions.log` on the cluster and prints it. It refuses anything
outside its list: `update-pending` may change only `TimeLimit`, `MinMemoryCPU`,
`ArrayTaskThrottle` and `Nice` (a partition change goes through PyAutoFit, which checks it),
and every argument must be one plain word. On the cluster the verbs source the project's
`activate.sh` first; set `HPC_ENV` / `HPC_PYTHON` in `sync.conf` to use another environment.

**Inspect:** `tail [gpu|cpu]`, `du`, `check`, `clear-logs [gpu|cpu]`.

**What syncs:** push code = `config/`, `hpc/`, `scripts/` + root files; push data =
`dataset/` (with `--ignore-existing`, so FITS already on the HPC are never re-sent); pull =
SLURM logs + `output/` (excluding `search_internal/`); a result root that is not on the HPC
yet is skipped. Always excluded: `__pycache__/`, `*.pyc`, `.git/`, `*.egg-info/`,
`sync.conf`.

> **Concurrency caution.** `remove_search_internal()` in PyAutoFit uses an unguarded
> `shutil.rmtree`; two concurrent SLURM array tasks chaining off the same cached base SLaM
> result can race on cleanup and one crashes with `FileNotFoundError`. Submit such chained
> jobs serially.

## See also

- [`operations/hpc`](./hpc.md) — the science of cluster runs.
- The [`hpc_campaign`](../../../skills/hpc_campaign.md) skill — plan, pilot, submit,
  check in, triage and report on a campaign, step by step.
- [`operations/dataset`](./dataset.md) — dataset layout and `info.json`.
- The [`start-new-project`](../../../skills/start-new-project.md) skill — full new-project
  workflow including HPC template setup.
