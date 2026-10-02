# Hidden reference posterior

`make_truth.py simulate` regenerates the seeded 100x100 FITS dataset and four
positions. It writes the true tracer only here. `make_truth.py reference`
runs the 13-dimensional, broad-prior Nautilus posterior (400 live points,
`n_eff=1200`, default `f_live=0.01`, fixed seed). It uses the library's
`AnalysisImaging` and supported JAX-vectorised search; no replacement
likelihood, optimisation covariance or artificial posterior is used.

From the repository root, activate a released PyAuto stack, clear test-mode
flags, select four physical CPU cores (check `lscpu -e` on SMT machines), then:

```bash
JAX_PLATFORMS=cpu JAX_ENABLE_X64=true OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  taskset -c 0,2,4,6 python benchmarks/truth/positions_initialised_inference/make_truth.py all
```

CPU IDs above match the calibration laptop; select appropriate IDs elsewhere.
The script forces CPU/fp64 and caps inherited affinity to four CPUs. The
reference may take much longer than the five-minute agent compute budget.
Runtime outputs go through the library's `output/benchmark_reference/` paths.
`posterior/` contains the genuine library model, samples, sample metadata,
summary and search configuration. `truth.json` records their hashes, dataset
hashes, library versions, seed, posterior widths and maximum likelihood.

The initial NumPy attempt was stopped after the supported JAX path was proved
on a separate 1,000-call feasibility probe. That truncated probe is **not** the
reference. Setup logs preserve both attempts. The production JAX reference
keeps the same priors, model, seed and convergence settings. During early
exploration its affinity was corrected from logical CPUs 0–3 (two physical
cores with SMT) to 0,2,4,6 (four physical cores). This affects timing, not the
posterior target. Calibration repeats start with four physical cores.

The harness strips this entire directory from every agent workdir. Do not move
its simulator, reference values, posterior or logs into the public dataset.
