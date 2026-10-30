---
name: hpc_campaign
description: Run a lens sample on an HPC cluster as a campaign — write hpc/campaign.yaml and a manifest, plan resources from evidence, pilot a small slice, submit, check in on the digest, triage failures into approved resubmits, and report compute, failures and an energy/carbon estimate. Drives python -m autofit.campaign through hpc/sync (status, plan, resubmit, report, act). Use when many lenses run through several pipeline stages on a cluster; NOT for one fit (al_run_search), generic HPC concepts (wiki/core/operations/hpc.md) or the Euclid pipeline's own arrays (euclid_hpc_runs).
---

# Running a lens sample as an HPC campaign

A sample of lenses through a SLaM pipeline is hundreds or thousands of fits in several
stages: SOURCE LP first, then SOURCE PIX, LIGHT and MASS, each one waiting for the one
before it, lens by lens. The modelling is the easy part to describe. What goes wrong at
scale is everything around it: memory asked for and never used, wall times that are too
short for the big lenses, a stage that failed for 3 % of objects and nobody noticed, and no
idea afterwards what the run cost.

A **campaign** is the answer the assistant ships. One file, `hpc/campaign.yaml`, declares
the manifest (one lens per line), the stages and their resources, how each stage waits for
the one before (index by index), and the check that says a stage succeeded. PyAutoFit's
campaign tools (`python -m autofit.campaign`) plan it, submit it, follow it and report on
it, and `hpc/sync` runs them on the cluster for you in one ssh call each. The ideas are in
[`wiki/core/operations/hpc.md`](../wiki/core/operations/hpc.md) ("Running a campaign") and
the machinery in
[`wiki/core/operations/hpc_infrastructure.md`](../wiki/core/operations/hpc_infrastructure.md).

**Two rules hold throughout.** You never submit, resubmit, hold, throttle or cancel
anything without the user saying so in this conversation; and CPU-only work never goes on
a GPU partition (`gpu`, `ral,gpu`, `gpu,ral`), which PyAutoFit refuses anyway.

## Ask

- *"Is `hpc/sync` set up for this cluster?"* — `hpc/sync check`. If not, start with the
  sync setup in [`hpc_infrastructure`](../wiki/core/operations/hpc_infrastructure.md).
- *"Which lenses, and which stages?"* — the manifest is one `<sample> <dataset>` per line;
  the stages are the pipeline scripts in `scripts/` (one per SLaM stage, written with
  [`init-slam`](./init-slam.md)).
- *"Which site?"* — `site: ral` loads the PyAutoNerves site file (partitions, array-size
  limit, power and carbon constants). Values it marks unverified are used as ranges.

## Branch — write the campaign file

Copy `hpc/campaign.yaml.example` to `hpc/campaign.yaml` and fill it in with the user:
`campaign:` (a short name), `project_root:` (exactly `$HPC_BASE/$PROJECT_NAME` from
`hpc/sync.conf`), `manifest:`, and one block per stage with `script: hpc/batch_cpu/stage`
and `env: {STAGE_SCRIPT: <your stage script>.py}`. Each stage after the first gets
`after: {<previous stage>: aftercorr}`, so lens *i* of SOURCE PIX starts as soon as lens *i*
of SOURCE LP has succeeded. Give each stage a `success:` check (its result zip with a
`.completed` member and `files/samples_summary.json`) so "done" means a usable result, not
just exit code 0.

Then validate it on the cluster after a push: `hpc/sync push --no-data` and
`hpc/sync plan hpc/campaign.yaml` (which validates first).

### Evidence keys for the standard SLaM stages

`plan` matches each stage against the profiling and inference summaries by the stage's
`evidence: keys:`. They are plain labels; use the ones the summaries use:

| Stage | `dataset_type` | `variant` | notes |
|---|---|---|---|
| SOURCE LP (parametric source) | `imaging` | `mge` | JAX on CPU is the fast path |
| SOURCE PIX, LIGHT, MASS (pixelised) | `imaging` | `delaunay` or `rectangular` | sparse operators on CPU |

Add `instrument` (`hst`, `jwst`, `euclid`, ...) and, if the user knows it, `regime`,
`setup_id` or `host_class`. A missing key widens the match; the grade on each number says
how close the evidence really is.

## Branch — plan, then pilot

```bash
hpc/sync plan hpc/campaign.yaml --idle-cpus ral=2000 --capacity-source "squeue/sinfo today"
```

The plan (`hpc/campaign/<name>/plan.md`) proposes CPUs, memory per CPU, wall time,
throttle and an ETA per stage. Read the **grades** with the user: `measured-current` is
evidence on exactly these keys; `provisional`, `analogue` (another instrument or regime),
`estimated` and `unsupported` are progressively weaker. Never call a setting "optimal"
unless the plan says a designation exists.

Before the full submit, propose a **pilot**: `python -m autofit.campaign pilot` on the
cluster (run it through `hpc/sync` by asking the user) writes a stratified 1–2 % of the
manifest, spread over lens sizes. Submit only that slice, wait for it, then plan again with
the pilot's measurements (`plan ... --pilot campaign/<name>/tasks.jsonl`). This is where
memory and wall-time mistakes are caught for the price of a few dozen fits.

## Branch — submit (only on the user's go)

Show the user the final plan and the exact command, and wait for a yes:

```bash
hpc/sync push
ssh <host> 'cd $HPC_BASE/$PROJECT_NAME && python -m autofit.campaign submit hpc/campaign.yaml --dry-run'
```

The dry run prints every batch script with the partition check's verdict. The real submit
is the same command without `--dry-run`, run by the user or by you after their explicit
yes. Every stage runs `hpc/batch_cpu/stage`, which writes a small task record before the
fit starts, so a lens that fails before Python runs is still counted.

## Branch — check in

```bash
hpc/sync status hpc/campaign.yaml
```

prints the digest (at most 2 KB) and pulls it into `hpc/campaign/<name>/`: counts per stage
and state, wall time and memory against what was asked, CPU efficiency, timeouts,
out-of-memory kills, node failures and Python failures by class, each with a
`failed_<class>.txt` list, plus drift flags (memory far below the request, timeouts
climbing, CPU-only work on a GPU partition). One call, one short read — do not poll; the
user asks again when they want an update.

If the project is tracked in PyAutoCortex, record the run's progress from the digest with
`cortex sync-runs <project> --digest hpc/campaign/<name>/digest.json`: it moves the run line
from open to running, or to done with finished and failed counts. Results and lessons stay
the user's to write.

## Branch — triage

For each failure class, explain what it means and propose the fix; act only on a yes.

- **timeout** — `hpc/sync resubmit hpc/campaign.yaml --stage S --class timeout` writes a
  proposal with p95 + 25 % wall time, sized from those tasks' own measurements. If a task
  already hit the partition's maximum time, the proposal says so: it should resume from its
  checkpoint rather than ask for more time.
- **oom** — the same with `--class oom` (1.5× the peak memory).
- **exception / bad_input / missing_seed** — Python failures are never resubmitted
  blindly. Open the task's log (`hpc/sync logs`), find the cause with the user (often
  [`al_debug_fit_failure`](./al_debug_fit_failure.md)), fix it, then resubmit.

Once the user approves a proposal:

```bash
hpc/sync act resubmit hpc/campaign.yaml resubmit_<stage>_<class>.json
```

Other changes to queued jobs go the same way, each logged to
`campaign/<name>/actions.log` with who, when and the exit status:
`act hold|release <job>`, `act throttle <array_job> <N>`,
`act update-pending <job> TimeLimit=... MinMemoryCPU=...`, `act cancel <job>`. Never run
`sbatch`, `scontrol` or `scancel` over ssh yourself; `hpc/sync act` and `submit` are the
only ways in.

## Branch — report

```bash
hpc/sync report hpc/campaign.yaml --site ral --objects <number of lenses>
```

writes `report.md`: compute used (and how much went on failed or repeated work), per-stage
tables, the failure census and an **estimate** of energy and carbon with a range, from the
Green Algorithms model and the site's power, PUE and grid-intensity values. It ends with a
paragraph for a paper. Read it with the user; the numbers are estimates and the paragraph
says so.

## Combine

- [`init-slam`](./init-slam.md) writes the per-stage pipeline scripts a campaign runs.
- [`al_profiling_setup`](./al_profiling_setup.md) explains the profiling evidence `plan`
  grades against.
- [`al_aggregator_bulk_analysis`](./al_aggregator_bulk_analysis.md) turns the finished
  results into tables and figures.
- [`euclid_hpc_runs`](./euclid_hpc_runs.md) is the Euclid pipeline's own array workflow.

When a campaign finishes, offer (default yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md`
entry: the science question the sample answers, the stages and searches it ran, and the
campaign's numbers from the report (objects, CPU-hours, failure rate, energy estimate).
