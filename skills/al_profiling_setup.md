---
name: al_profiling_setup
description: Look up recorded PyAutoLens likelihood timings and bounded setup advice for imaging, interferometer and other dataset/model families. Match dataset size, masked pixels, source resolution, PSF, precision, hardware and software against a pinned profiling catalogue, distinguishing exact matches, approximate analogues and absent evidence. Use for setup/performance questions, not for launching profiling jobs, choosing accepted baselines or predicting sampler convergence.
---

# Choose a setup using recorded profiling evidence

## Orient

Your source model and masked data determine the work done by each likelihood evaluation;
the sampler determines how many evaluations a fit needs. A recorded likelihood timing can
inform a setup choice, but it cannot by itself predict when your posterior exploration will
finish. For an ALMA pixelized fit, masked pixels and source resolution matter as well as
visibility count; an instrument label alone does not establish a match.

Read the project's [catalogue contract](https://github.com/PyAutoLabs/autolens_profiling/blob/main/catalogue/README.md)
and setup wiki in the **same pinned checkout** used below. Campaign journals remain the
cross-cutting scientific account; follow them for rationale and exceptions. The transport
and method distinctions are defined in `autolens_profiling:catalogue/README.md`.
For the statistical distinction, see [non-linear search](../wiki/core/concepts/non_linear_search.md).

## Ask

Use context already supplied. Otherwise ask for the dataset/model family, instrument,
image shape or visibility count, masked pixels, source pixels/resolution, PSF shape,
precision and actual hardware. Ask for solver, regularization, oversampling, transformer,
preloads and software revisions when relevant. Unknowns are `null`, never guessed from
current defaults. Do not load or fit real data for this lookup.

Use `axis` and optionally `metric` to select the measurement kind; the example asks
for runtime, not compile or component totals.

Use the exact configuration keys recorded in the catalogue, including additional
configuration dimensions not in this short list. The reader checks every supplied key
and every recorded key before claiming an exact match. Hardware class `a100` or `cpu`
is insufficient without recorded hardware details. A version label does not replace
library commit identities when those are available.

## Branch: find evidence for your setup

Use a local git checkout of `autolens_profiling` at an explicit commit. Do not refresh it
silently. The reader verifies committed bytes for the index, each loaded shard and cited
artifact and checks shard hashes and measurement JSON pointers. A dirty, absent or invalid
snapshot returns an explicit error; it is not an empty successful search. The index's
`producer_revision` is publication metadata, not the commit containing the snapshot and
not necessarily the measured library revision.

Save a query such as the committed [ALMA example](../examples/profiling/alma_delaunay.json),
replacing its unknowns only with your actual settings. From the assistant root:

```bash
python -m autoassistant.profiling \
  --catalogue /path/to/autolens_profiling/dashboard/catalogue.json \
  --query examples/profiling/alma_delaunay.json --limit 5
```

This runs standard-library lookup only. It never imports PyAutoLens or submits jobs.
The equivalent Python recipe is in [scripts/profiling_lookup.py](../scripts/profiling_lookup.py);
adapt that script for a reproducible query. Source: `autolens_assistant:autoassistant/profiling.py`.

Report one of these outcomes, then cite each concrete record's immutable `citation.url`
and its separate `json_pointer` (a JSON pointer is not a GitHub heading):

- **Exact match:** all compared configuration, hardware and software fields match and
  there are no identity limitations. Still state acceptance status, measured revisions,
  timing method, missing provenance and whether evidence is suitable for the intended use.
- **Approximate analogue:** list the differing size dimensions and unknowns. Quote the
  recorded timing for the recorded configuration; do not scale or extrapolate it to the
  user's configuration. Candidates are ordered by match completeness, never by speed.
- **No applicable evidence:** the indexed evidence is absent or has known incompatible
  settings. This does not mean the setup is impossible or its runtime is zero.

Always state the candidate count and truncation (`--limit`). Inspect records individually:
runtime, compile, component breakdown, host RSS and VRAM are separate axes. A vmap
per-call throughput is not single-call latency, and host RSS or a device snapshot is not
peak VRAM. Do not join timings across solvers, revisions, precision or hardware.

Recommendations returned by the reader are **historical context**, not automatic setting
changes. Read their `applies_to.constraints`, exact setup/record/version support,
`validation` and limitations before suggesting anything. They may encode additional
unmatched conditions. Unreviewed recommendations must be described as draft historical
observations; never call them accepted. The interferometer decision matrix has bounded
solver/revision caveats and does not authorize extrapolating a NUFFT choice to an unmeasured
configuration. Also inspect setup hazards and the catalogue's unbound findings, whose
applicability is unknown. Invite the user to explore a relevant caveat if it affects their choice.

## Branch: conditional time per fit

If the user asks for fit time, first state the assumed evaluation count, effective
concurrency, setup cost, compilation cost and other overhead. Unknown assumptions mean
no numerical fit-time estimate. For a full-likelihood mean/median single-call latency,
`conditional_fit_time` computes:

`setup + compile + ceil(evaluations / concurrency) * likelihood_seconds + overhead`

It accepts only `runtime` records with `full_call.mean_s` or `full_call.median_s`, seconds,
known mean/median statistics and an explicit integer `method.batch_size: 1`; it rejects component totals and vmap metrics. All five
assumptions are mandatory keyword arguments. Missing batching metadata is unavailable, not assumed to be one. This conservative subset leaves other timing
methods unavailable for arithmetic rather than guessing their semantics. Cite the record
and report the returned assumptions and qualification. Inspect configuration batching too;
never feed a batched measurement to the helper.

This is ideal scheduling arithmetic, **not a calibrated fit-time predictor**. Nested sampling
and MCMC can have serial work, variable likelihood cost and unknown evaluation counts;
contention can invalidate the concurrency assumption. An unreviewed input remains unreviewed.
Do not sum setup and compile from unrelated records or infer missing costs to be zero.

## Combine

Use [al_run_search](al_run_search.md) for an already chosen inference workflow, or
[HPC guidance](../wiki/core/operations/hpc.md) for execution planning when that skill applies. Neither
lookup nor an archived recommendation authorizes a profiling campaign, baseline promotion,
HPC submission or model change. Save the query, snapshot revision and cited record IDs with
any later scientific decision.
