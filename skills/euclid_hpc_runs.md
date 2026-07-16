---
name: euclid_hpc_runs
description: Run the Euclid pipeline on a supercomputer — configure hpc/sync (push code/data, pull results), adapt the batch_cpu / batch_gpu SLURM array templates (one dataset per array task), submit, monitor, and pull results back. Use when a Euclid lens sample outgrows the local machine; NOT for single interactive fits (euclid_setup_pipeline) or generic HPC concepts (wiki/core/operations/hpc.md).
---

# Running Euclid samples on HPC

One lens is a laptop job; a sample is not. The pipeline ships an HPC workflow built on
two pieces: a **sync CLI** that mirrors the project to the cluster and pulls results
back, and **SLURM array templates** that run one dataset per array task — the natural
unit, since every pipeline stage takes `--sample`/`--dataset` arguments and lenses are
independent. GPU nodes are the fast path (JAX accelerates the likelihood ~50×; one GPU
per task is enough); CPU templates exist for clusters without them. Generic
HPC/JAX/SLURM concepts live in
[`wiki/core/operations/hpc.md`](../wiki/core/operations/hpc.md) — this skill is the
Euclid-pipeline application of them.

## Ask

- *"Which cluster, and is sync configured?"* — `hpc/sync.conf` is per-machine and
  gitignored; first-time setup is the first branch.
- *"GPU or CPU partition?"* — picks `batch_gpu/` vs `batch_cpu/` templates.
- *"Which stage over which lenses?"* — each template pairs with a pipeline stage
  (`submit_start_here`, `submit_full_model`); the dataset list defines the array.

## Branch — configure sync (once per machine)

```bash
cp hpc/sync.conf.example hpc/sync.conf
# edit: HPC_HOST (ssh alias or user@host), HPC_BASE (remote project root),
#       PROJECT_NAME (defaults to the folder name)
```

`$HPC_BASE/$PROJECT_NAME` becomes `$PROJECT_PATH` inside the batch scripts, so
activation and paths stay consistent between local and remote. Then:

```bash
hpc/sync push      # code + dataset/ up to the cluster
hpc/sync pull      # results (output/, dataset products) back down
hpc/sync sync      # push then pull (default)
hpc/sync status    # dry run — show what would transfer
```

Citation: `euclid_strong_lens_modeling_pipeline:hpc/sync`.

## Branch — adapt a batch template and submit

The templates (`hpc/batch_gpu/submit_start_here`, `hpc/batch_gpu/submit_full_model`,
CPU twins under `hpc/batch_cpu/`) are SLURM array jobs: a `datasets=( … )` list, the
`--array=0-N` range to match, `sample=` for the dataset folder, and per-task resources
(`--partition=gpu --gres=gpu:1`, 32 GB, 2 h for the initial fit — raise the time limit
for `full_model`, which chains five searches). Edit the list, the array range, and the
mail address, then on the cluster:

```bash
cd $PROJECT_PATH && sbatch hpc/batch_gpu/submit_start_here
```

Logs land in `output/output.%A_%a.out` / `error/error.%A_%a.err` per array task —
`tail -f` the newest to watch a fit, and check the error file first when a task dies.
After completion, `hpc/sync pull` locally brings `output/` home, and
[`euclid_workflow_products`](./euclid_workflow_products.md) turns it into catalogues
and summaries.

Two habits that save cluster time: smoke the exact submission path once with
`PYAUTO_TEST_MODE=1` on a single-lens array before a big run, and remember completed
fits resume/skip — resubmitting an array over partly-finished lenses only runs what's
missing.

## Combine

- [`euclid_model_lens`](./euclid_model_lens.md) — what each stage does and which to
  batch.
- [`euclid_workflow_products`](./euclid_workflow_products.md) — sample-scale inspection
  once results are pulled.
- [`wiki/core/operations/hpc_infrastructure.md`](../wiki/core/operations/hpc_infrastructure.md)
  — the assistant's generic HPC template/sync machinery, of which the pipeline's
  `hpc/` folder is the Euclid instance.

## Further reading

- **General reference** — [euclid_strong_lens_modeling_pipeline README](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline#readme):
  the repo the batch templates run from.
