---
name: al_inference_setup
description: Look up pinned inference-summary v2 records for a dataset/model setup and prepared problem. Distinguish exact matches, qualified analogues and absent evidence while retaining baseline acceptance, archived status, priors, SLaM stage, cold/warm/resumed sampler starts, hardware, compilation/cache, costs, work units, seed diagnostics and sample availability. Use for evidence-based sampler/setup questions, never for launching jobs, ranking samplers or predicting runtime from parameter count.
---

# Choose an inference setup using recorded evidence

## Orient

A sampler choice depends on the prepared scientific problem and measured conditions.
Read the [public v2 contract](https://github.com/PyAutoLabs/PyAutoInsight/blob/52c637f5a2dfc1bd361cf4fcedee2fbf374998ea/REFERENCE.md)
and the producer's setup documentation at the explicit checkout revision you use.
Evidence is owned by the project. This assistant reads the producer catalogue; it
has no duplicate campaign summary and does not consult personal Memory material.

Use this skill for inference records and [al_profiling_setup](al_profiling_setup.md)
for likelihood timings. Neither measurement predicts posterior convergence.

## Ask

Use already supplied context. Otherwise ask for the dataset/model families and
instrument, setup/prepared-problem identities, frozen dataset/model/prior IDs,
actual SLaM stage and the target. Capture sampler/configuration, seed/protocol,
backend/precision, hardware and dependency revisions. If start conditions matter,
ask whether this is cold, warm or resumed and which pinned artifacts are reused.
Track compilation and cache independently. Unknown metadata stays null.

Frozen prior/model IDs describe scientific definitions, not a parameter count or
a display name. Changed priors or adapt products require a different problem;
changing a sampler alone need not. Never choose a search from dimensionality alone.

## Branch: read the pinned catalogue

Use an explicitly chosen full git commit of `autolens_inference`. Do not refresh
it silently. The checkout must have that HEAD and committed catalogue/evidence
bytes. The reader validates `inference-summary@2` using pinned public contract
rules, all setup/problem/start references and original public evidence paths.
It checks the source capture revision separately from the publication commit.
An invalid or dirty snapshot is an error, never an empty successful search.

Start with the [HST example query](../docs/inference/hst_delaunay.json), replacing
nulls only with settings actually supplied or recorded. From the assistant root:

```bash
python -m autoassistant.inference \
  --catalogue /path/to/autolens_inference/dashboard/catalogue.json \
  --revision FULL_40_CHARACTER_COMMIT \
  --query docs/inference/hst_delaunay.json --limit 5
```

The equivalent entry script is [scripts/inference_lookup.py](../scripts/inference_lookup.py).
This is standard-library lookup: no PyAutoLens imports, fits, installs or jobs.
The reader reports candidate count and returned count so truncation is explicit.

- **Exact match:** every compared scientific identity and run condition is known
  and matches. This says nothing about convergence or acceptance.
- **Approximate analogue:** list unknown identities/conditions and quote evidence
  for its recorded configuration. Known incompatible conditions exclude records;
  incomplete matches remain qualified. No size scaling or runtime extrapolation.
- **No applicable evidence:** no indexed compatible family/conditions. It does
  not mean the setup is impossible or runtime is zero.

Cite each record's immutable `citation.url` and separate `json_pointer`;
`evidence_citations` identify verified original bytes and their capture commit.
Producer revision, snapshot revision and measured dependency revisions differ.
Generation time is not measurement time; quote freshness limits/unknowns and
coverage exclusions. Returned records preserve failed/incomplete runs and seeds;
do not select the fastest or best seed.

## Branch: baseline and conditions

A prepared problem's `baseline` can be archived or unassessed. Only the producer's
explicit `selected_reference` declares an accepted current reference; the reader
validates its current/completed/accepted and frozen-identity requirements. If it is
absent, state the setup's recorded reason. Never select or promote one yourself.
Read scientific acceptance/convergence, archived flag, execution, samples and
maximum-likelihood/posterior diagnostics individually. A matching maximum
likelihood does not establish recovered posteriors or available samples.

Prepared artifacts and sampler-start sources retain revision/digest declarations.
They may be private/gitignored: the lookup does **not** fetch or verify them for
reuse and does not claim they are downloadable. Their bytes require separate
verification before any later execution. Cold initialization can still reuse
prepared SLaM adapt products. Warm starts reuse pinned sampler information;
resume means continuing a checkpoint, not a fresh run. Unknown is never cold.
Sampler starts do not determine compilation/cache states.

## Branch: recorded cost and diagnostics

Quote clocks with their definitions: preparation, initialization, setup,
compilation, sampling and total time can overlap. Never sum clocks or stages or
fill missing times with zero. Resume clocks may describe a segment or cumulative
work: preserve the producer's scope. Retain likelihood evaluations, gradient
evaluations, iterations, retained samples and effective sample size as separate
work units, with definitions and unknown reasons. Never convert iterations into
evaluations or compare ESS without its estimator/aggregation definition.

This lookup does not certify comparison parity, compute speed ratios, rank
samplers or predict runtime. Read records individually and retain hardware,
concurrency, revisions, seed, diagnostics and experiment-protocol qualifications.

## Combine

For an already chosen workflow use [al_run_search](al_run_search.md),
[al_configure_search](al_configure_search.md) and applicable
[HPC guidance](../wiki/core/operations/hpc.md). The lookup authorizes no science
run, HPC submission, baseline promotion or model change. Save the query, commit
and cited record IDs with any later decision.
