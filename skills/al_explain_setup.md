---
name: al_explain_setup
description: Explain which compute setup (numba or JAX, CPU or GPU, sparse or dense operator, precision, interferometer transformer), how many parallel workers and what run-time estimate a PyAutoLens fit used or will use, and why. For a fit that ran or is running it reads files/setup.json and files/parallel.json (plus the fit-start banner), matches the setup to its row in the rule table, quotes the rule sentence, links the autolens_profiling day-zero page and PyAutoPulse decision, explains the estimate and flags untested branches. For a planned fit it uses al.estimate_runtime. Use for "why did my fit pick numba / the GPU / 8 workers?" or "can I trust this estimate?"; NOT for choosing search settings (al_configure_search) or detailed profiling or sampler evidence (al_profiling_setup, al_inference_setup).
---

# Explaining a fit's compute setup

## Orient

The **compute setup** decides how each likelihood evaluation is computed: the backend
(numba or JAX), the device (CPU or GPU), whether the pixelized-source linear algebra uses
a sparse operator or dense matrices, the floating-point precision and, for interferometry,
the transformer (w-tilde or NUFFT). It never changes the model, the priors or the
posterior. Every designated setup was checked to give the same log likelihood as the
others (a parity check), so a different setup changes only how long the fit takes.

With `setup="auto"` on the analysis, the setup is chosen when the fit starts. The choice
depends on the dataset type, the source model (its mesh: rectangular, delaunay or
delaunay_nn; no mesh means MGE) and the hardware class (an A100 GPU node or a many-core CPU node).
Each choice comes from a chain of evidence: a row of the rule table
`PyAutoArray:autoarray/config/setup_rules.yaml`, then the human designation it was generated
from (`PyAutoPulse:decisions/`), then the profiling page that holds the measurements
(`autolens_profiling:wiki/day_zero.md`). For a Euclid lens with a rectangular source on
an 8-core laptop, this chain explains the choice of numba and the
"extrapolated" flag in the banner. The wider HPC background is in
[`wiki/core/operations/hpc.md`](../wiki/core/operations/hpc.md).

## Ask

*"Has this fit already run (or is it running), or are you planning it?"* Then ask what
worries them: the setup itself, the worker count, or whether the estimate is believable.
Skip the first question when they hand you an output folder.

## Branch A — a fit that ran or is running

The setup is resolved before sampling starts, so a running fit already has its records.
`files/setup.json` (written only when the analysis was given a `setup`) holds the setup
fields plus `chosen_by`. `files/parallel.json` holds the worker resolution and the estimate
line. The same facts were printed at fit start:

```
Automatic compute setup (CPU/GPU choice from setup="auto"; override with PYAUTO_SETUP or setup=...):
Setup:    numba · CPU · sparse operator · fp64   (rule imaging/rectangular · extrapolated: 8 cores, rules measured on ≥16-core nodes)
Parallel: 8 workers (auto: detected cores)
Estimate: ~6.4 min on this hardware   (283 ms/eval, euclid cell · Nautilus n_live=50 ≈ 4.6e3 evals, heuristic · η=0.55)
```

Read the records and the rule row (standard library plus PyYAML, which PyAutoLens installs):

```python
import json
from pathlib import Path

import autoarray
import yaml

FIT = Path("output/imaging/<your_lens>/<name>/<unique_hash>")
setup = json.loads((FIT / "files" / "setup.json").read_text())
parallel = json.loads((FIT / "files" / "parallel.json").read_text())
print(setup["setup_id"], setup["chosen_by"], setup["hardware_class"], setup["extrapolated"])
print(parallel["number_of_cores"], parallel["reason"], parallel["estimate_line"])

rules = yaml.safe_load(
    (Path(autoarray.__file__).parent / "config" / "setup_rules.yaml").read_text()
)["rules"]
row = next((r for r in rules if r["decision_id"] == setup["decision_id"]), None)
if row:
    print(row["likelihood"], row["optimal"], row["secondary"])
    print(row["rule"])
```

Explain the records in this order:

- **What was chosen, and by whom.** `chosen_by` is `auto` (the rule table chose),
  `explicit` (the script passed a setup_id or `aa.Setup`) or `PYAUTO_SETUP` (the
  environment variable named a setup_id). Only `auto` has a rule. For the other two, say
  it was the user's choice and compare it with what auto would pick. If there is no
  `setup.json`, no setup was given: the log has the line `Compute setup: not set (auto
  would choose …; pass setup="auto")`.
- **The rule.** Quote the row's `rule` sentence word for word. Name `optimal` and
  `secondary`, which is the fallback when the optimal setup cannot run.
- **The evidence.** Link the likelihood's day-zero page,
  `autolens_profiling:wiki/campaigns/<dataset_type>/<variant>/day_zero.md` (for example
  `autolens_profiling:wiki/campaigns/imaging/rectangular/day_zero.md`), which has the
  per-instrument timings, and the Pulse decision named by `decision_id`, for example
  `PyAutoPulse:decisions/imaging-rectangular-standard-cpu-many-core.md` (public:
  `https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/<decision_id>.md`). The
  decision records who made the designation, the separation test and the revisit
  conditions.
- **The worker count.** `reason` is `requested` (an integer was passed),
  `detected_cores` (`"auto"`: `SLURM_CPUS_PER_TASK`, then CPU affinity, then
  `os.cpu_count()`), `jax` (a JAX likelihood never forks, so it runs 1 worker and gets its
  parallelism from `jax.vmap`), `expectation_propagation` (factor searches never fork),
  `cores_per_eval` or `memory` (capped by cores per evaluation or by
  `available_memory_gb` over peak memory). Source:
  `PyAutoFit:autofit/non_linear/parallel/pool.py`.
- **The estimate.** The `ms/eval` figure is the measured cost of the profiling cell
  (instrument) nearest your data in size: masked pixels for imaging, visibilities for
  interferometry. The evaluation count is the Nautilus heuristic of the calibrated wall
  model (`PyAutoLens:autolens/analysis/wall_model.py`); other searches print `Estimate:
  none for <Search>`. `η` is numba's parallel efficiency, read from the measured curve in
  the header of `PyAutoLens:autolens/config/runtime_estimates.yaml` (1 core 1.0, 8 cores
  0.55, 32 cores 0.28). A JAX fit shows `1 worker (JAX)` instead. A `range across
  instruments` band means no size matched. In-sample the model reads 0.56–1.59× of
  measured wall time. Interferometer (held-out 0.19–0.45×), weak lensing (0.50–0.52×) and
  datacubes are labelled `uncalibrated`. Treat those as order-of-magnitude figures. The
  wall-time validation behind this is `autolens_inference:INFERENCE_SUMMARY.md`.
- **Untested branches.** Read the day-zero page's "Untested branches" section and name
  the ones that apply. `extrapolated: true` means a CPU with fewer than 16 cores (a laptop),
  a GPU that is not an A100, or no rule for this hardware class. Also check for an
  instrument or data size outside the measured cells, a non-standard size regime, mixed
  precision (experimental), and the designation's assumed parallel efficiency of 1.0.
  An extrapolated setup is still a reasonable default, but nobody has measured it on
  hardware like yours.

Invite a follow-up: *"want me to open the day-zero page and walk through the timings
for your instrument?"*

## Branch B — a planned fit

Before the fit runs, `al.estimate_runtime` gives the same `Estimate:` line. It does not
accept `setup="auto"` or `number_of_cores="auto"` yet, so pass the concrete setup_id that
auto would choose. Find it in the rule table for your likelihood and hardware class
(the `Compute setup: not set` line also names it). Pass your real worker count too.

```python
import autofit as af
import autolens as al

# dataset and model as in your fit script (al_build_imaging_model)
search = af.Nautilus(path_prefix="imaging/<your_lens>", name="pix", n_live=150)

estimate = al.estimate_runtime(
    dataset=dataset,
    model=model,
    search=search,
    setup="numba_cpu_sparse_fp64",  # the imaging/rectangular rule on a many-core CPU
    number_of_cores=8,
)
print(estimate.line())
```

For an HST-sized imaging dataset with a 30×30 rectangular source this prints
`Estimate: ~40 min on this hardware   (697 ms/eval, hst cell · Nautilus n_live=150 ≈
1.4e4 evals, heuristic · η=0.55)`. With `setup="auto"` the fit will print the header, the
`Setup:` line (rule and any extrapolation), the `Parallel:` line and this estimate. Source:
`PyAutoLens:autolens/analysis/runtime_estimate.py`.

For more detail than the rule and the estimate, hand over. Per-cell timings, memory and
compile cost belong to [`al_profiling_setup`](./al_profiling_setup.md). Sampler choice and
measured fit wall times belong to [`al_inference_setup`](./al_inference_setup.md).

## Combine

- [`al_configure_search`](./al_configure_search.md) "Compute setup: auto unless…" is where
  you override the choice (pin a setup_id, cap workers, force numba or JAX).
- [`hpc_campaign`](./hpc_campaign.md): the campaign `plan` grades its numbers
  (`measured-current`, `analogue`, `estimated`, …) against the same evidence. Read those
  grades together with the rule and the untested branches here.
- [`al_load_results`](./al_load_results.md) lists every file in the output folder;
  [`al_debug_fit_failure`](./al_debug_fit_failure.md) covers fits that are slow for other
  reasons.

## Further reading

- **Experienced PyAutoLens user** — [workspace/lens: guides/advanced/auto_setup.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/advanced/auto_setup.py):
  the automatic setup, its overrides and the estimate, runnable in test mode.
- **General reference** — [autolens_profiling: Day zero](https://github.com/PyAutoLabs/autolens_profiling/blob/main/wiki/day_zero.md):
  the optimal setup per likelihood and hardware class, with links to every page and decision.
