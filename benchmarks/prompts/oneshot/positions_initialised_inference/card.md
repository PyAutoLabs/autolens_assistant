---
id: positions_initialised_inference
version: 1
kind: oneshot
prompt_sha256: f80d6a80f6bbf4dada023afae0a50264576db5dda05c71f4b51c8f794186c84c
budget:
  compute_seconds: 300
  run_seconds: 1200
datasets:
  - benchmarks/datasets/positions_initialised_inference
workspace_packages:
  - point_source
  - imaging
added: 2026-10-02
result_schema:
  parameters: {"<library.parameter.path>": {median: float, sigma: positive_float}}
  einstein_radius: float
  log_likelihood_max: float
  positions_fit: {einstein_radius: float, search_output: path}
  fit_figure: path
  imaging_search: path
---

# Positions-initialised imaging inference

## Prompt

```text
I am a researcher who wants executable code and a fitted lens model. Model the simulated lens in benchmarks/datasets/positions_initialised_inference (data.fits, noise_map.fits, psf.fits, positions.json). The imaging is 100x100 pixels at 0.1 arcsec/pixel. Lens/source redshifts are 0.5/1.0. Use an Isothermal lens mass at the fixed centre (0,0), a separate ExternalShear field, and one circular Sersic light profile each for the lens and source. Fix the lens light centre to (0,0) and both light ellipticities to zero; fit both intensities, effective radii and Sersic indices, the source light centre, mass ellipticity/Einstein radius and both shear components (13 free imaging parameters). Include lens light. Name the model components galaxies.lens.mass, galaxies.lens.bulge, galaxies.source.bulge and fields.shear so parameter paths are unambiguous. Use a 2.5 arcsec circular imaging mask and uniform light-profile oversampling 2, matching the simulator.

The four positions in positions.json are the lensed images of the same source centre with 0.05 arcsec errors. Fit these first with a genuine posterior search, then use that posterior to initialise the imaging search: keep all five mass/shear parameters free but narrow their priors below the workspace defaults, centred on the positions posterior. Use the point_source and imaging examples as appropriate. Use Nautilus for both posterior searches, not just an optimiser, and do not use test mode or fix free parameters to best-fit estimates. For the imaging search use at least 50 live points and retain at least 200 weighted posterior rows with effective sample size at least 100. Keep compute under five minutes on four CPU cores (no GPU); you have twenty minutes elapsed time to read, write and finish. Report honestly if the compute target cannot be met.

Write result.json with exactly these keys: "parameters" (an object mapping every free imaging parameter's library dot-separated path to {"median": float, "sigma": float}, where sigma is half the 15.8655–84.1345 percentile interval from the weighted posterior); "einstein_radius" (the imaging posterior median of the Isothermal einstein_radius parameter, arcsec); "log_likelihood_max" (the maximum imaging sample log likelihood); "positions_fit" ({"einstein_radius": the positions posterior median of the same parameter, "search_output": its search output directory}); "fit_figure" (a fit-subplot PNG path); "imaging_search" (the imaging search output directory). Paths must be relative to this repository. Preserve each search's model.json, search.json, samples.csv and samples_info.json in its library output files/ directory so the posterior and initialisation can be inspected. Save the fit subplot from the imaging result. Finish both searches and write the result in this session.
```

## What this measures

A positions posterior should put imaging in the right basin before sampling.
The fixed lens centre and circular light profiles define a deliberately small,
13-dimensional problem; light intensity, radius, index and source centre remain
inferred. Four noiseless model positions carry stated 0.05 arcsec uncertainties;
imaging includes seeded Poisson sky/source noise at a 565-second exposure.
The positions fit may solve the point source centre analytically.

The hidden reference is a **real broad-prior Nautilus posterior**, with 400 live
points and target effective sample size 1200. The bank contains its model,
weighted samples, search configuration and convergence information; the
simulator, seed, versions and hashes are under `benchmarks/truth/` and are
excluded from the agent checkout. No simulator parameter values occur here.
The reference is allowed to run longer than the agent's compute budget.

## Score

The harness gates completion, schema, <=300 seconds of interpreter wall time
and <=1200 seconds elapsed time. Interpreter wall time includes imports and
scripts, not CPU-seconds summed over cores. The operator restricts affinity to
four CPU cores and forces CPU execution. Scores should only compare timings
on the same hardware.

Additional gates require:

- Both saved search models/configurations and finite weighted sample tables.
- Each of the five imaging mass/shear priors remains free, narrower than its
  workspace default width, and centred within three positions-posterior sigma.
  Gaussian widths are sigma; uniform widths are range/sqrt(12). Defaults are
  0.3 for mass ellipticity, 8/sqrt(12) for radius and 0.6/sqrt(12) for shear.
- At least 200 imaging rows, effective sample size >=100, >=50 live points in
  both search configuration and samples metadata, and all 13 expected paths.
- Reported estimates match the weighted saved samples within 1% (absolute
  floor 1e-6), and maximum likelihood within 0.1. Fixing parameters, dummy
  uncertainty reports and test-mode outputs cannot satisfy these gates.
- Maximum imaging log likelihood no more than 50 below the reference.

Five equally weighted [0,1] metrics:

| Metric | Frozen mapping |
|---|---|
| Recovery | Fraction of true parameters inside median +/-3 sigma, with any sigma >5x reference sigma counting zero |
| Imaging Einstein radius | max(0, 1-relative_error/0.05) |
| Maximum likelihood | 1 when <=5 below reference, linearly falling to 0 at 50 below |
| Positions Einstein radius | max(0, 1-relative_error/0.05) |
| Figure | Decodable PNG, >=10000 bytes, both dimensions >=200 pixels |

The scorer copies raw search files and the figure into `search_evidence/`
before workdir cleanup. Re-scoring recomputes every posterior check from those
bytes. Missing, escaped or malformed paths fail closed. These are synthetic
data; inspecting a real-data mask with a human is unnecessary.

## Calibration

Three independent Claude Code 2.1.287 runs on 2026-10-02 resolved the current
default model to `claude-fable-5-1`. **0/3 passed; median 0, range 0–0. The
five-minute compute target was not demonstrated.**

| Repeat | Wall seconds | Recorded compute seconds | Outcome |
|---|---:|---:|---|
| 1 | 1260.1 | 280.2 (incomplete) | No result; wall timeout |
| 2 | 1260.1 | 42.3 (incomplete) | No result; wall timeout |
| 3 | 1020.2 | 566.2 | Valid posterior and result; compute budget failed |

**Timing limitation:** the inherited interpreter shim records an invocation only
after it exits. Killed/background invocations are therefore missing from repeats
1 and 2; their raw `compute_budget: true` gates are invalid measurements, not
budget successes. The generated records remain untouched. Both runs independently
fail the finished/wall gates. Repeat 3 records more than 300 seconds and correctly
fails compute. No repetition establishes a budget success. Timeout cleanup left
own-session descendants; these were stopped before the next repeat.

Repeat 3 passes every scientific gate, including saved-search consistency,
positions-initialised priors, posterior sample floor and likelihood convergence.
Its metrics are recovery 1, imaging radius 0.9978, likelihood 1, positions radius
0 and figure 1. The positions radius discriminates (1.3231 versus 1.25 arcsec);
imaging radius is nearly saturated. Recovery, likelihood and figure saturate at
one for this one completed fit; the two incomplete runs cannot establish their
discriminatory power. The aggregate is saturated at zero by the budget/finished
gates, so this calibration does not establish useful aggregate discrimination.

All repeats used the released 2026.9.27.2 PyAuto stack, Python 3.12.10, CPU JAX
with fp64 (`JAX_PLATFORMS=cpu`, `JAX_ENABLE_X64=true`), single-thread BLAS/OpenMP,
and affinity 0,2,4,6: four physical cores on the Intel i9-10885H laptop. The host
exposes eight logical CPUs, which explains the harness metadata's `cpu_count: 8`.
Reference/test compute did not overlap these repeats; unrelated host workloads
were not controlled, so timings are measurements of this shared host.

Repeats 2–3 archived `abafd86`. Repeat 1 archived `0a828fa`; while it ran, the
hidden reference CSV index was corrected in `abafd86` to preserve its raw bytes.
The runner records HEAD at completion, so its generated metadata says `abafd86`.
Agent-visible tracked trees (excluding `benchmarks/truth/` and `benchmarks/runs/`)
are identical: 596 records with SHA256
`bf7288203e42660e8f2c0801c17cab5c487d9ebd64e104d2a876f838ab4bae6d`.
The truth and previous runs were absent from each live agent checkout. HEAD was
held fixed for repeats 2–3; no hints or workdir edits were supplied.

Raw transcripts, timings, results and scores are retained under
`benchmarks/runs/positions_initialised_inference/`. Repeat 3 also retains both
raw search outputs and its PNG under `search_evidence/`, allowing re-scoring
after workdir cleanup. The frozen prompt and score mappings were not changed
in response to calibration outcomes.
