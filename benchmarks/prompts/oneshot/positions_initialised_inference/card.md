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

Pending three independent Claude Code runs after the card and hidden posterior
are committed. All outcomes, including failures and budget overruns, are kept.
