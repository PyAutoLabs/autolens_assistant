---
id: cosmos-web-ring-fit
version: 1
kind: oneshot
prompt_sha256: 4e768e7f230f0438ccb91bec63446fd8c8674a06eeb202e22af4256c322bfdb4
budget:
  compute_seconds: 900
  run_seconds: 1800
datasets:
  - dataset/imaging/cosmos_web_ring
workspace_packages:
  - imaging
added: 2026-09-26
---

# One-shot: fit the COSMOS-Web Ring (F444W)

The one-shot twin of the assistant's public starting prompt: a researcher asks
for a real lens model of the bundled JWST imaging and a machine-readable report
of how good it is. Where `oneshot-smoke` only checks that a harness reads the
repository, this card checks that it can **run the assistant's recommended
fit end to end** — data preparation, model composition, the JAX optimiser,
figures — and land on the right answer. It is run with `oneshot-smoke` for
every model × harness.

## Prompt

```text
I am a researcher who wants the code. Model the JWST F444W imaging of the COSMOS-Web Ring in dataset/imaging/cosmos_web_ring/wavebands/F444W: prepare the data as this assistant recommends (extra-galaxy noise scaling, a 1.8 arcsecond circular mask), fit a lens model with a multi-Gaussian-expansion (MGE) lens light, an isothermal mass plus external shear, and an MGE source using the fast JAX multi-start gradient optimiser this assistant recommends for a maximum-likelihood point estimate, then report how well the model reproduces the observations. Write `result.json` with exactly these keys: "einstein_radius" (arcsec, float), "reduced_chi_squared" (float, chi-squared over the number of masked image pixels), "n_masked_pixels" (int), "noise_scaling_applied" (bool), "mask_radius" (arcsec, float), "search" (the search class name), "figures" (list of repository-relative PNG paths you made, including a fit subplot), "summary" (at most three sentences).
```

The harness appends the one-shot footer (`benchmark.py`'s `ONESHOT_FOOTER`) with
this run's directory; the footer is not part of the hashed prompt. The prompt
states the reader's level ("a researcher who wants the code") because no
operator is present to answer the greeting skill's expertise question.

## What this measures

- **Following the assistant's data preparation.** Extra-galaxy noise scaling
  from the bundled `mask_extra_galaxies.fits` and the 1.8" circular mask are
  gates: a fit that skips either is not the analysis asked for.
- **Landing in the right basin.** With the library's default priors (Isothermal
  `einstein_radius` uniform over 0–8", shear components over ±0.3) and a 1.8"
  mask, `MultiStartProdigy` can converge to a degenerate solution —
  θ_E ≈ 2.4", source outside the caustic, no ring modelled, reduced χ² ≈ 9.3.
  The reference script (`scripts/cosmos_web_ring/fit_cosmos_web_ring.py`)
  bounds the Einstein radius to 0.3–1.5" and the shear to ±0.15 and recovers
  θ_E = 0.80" (the tangential critical curve's effective radius is 0.77",
  matching Mercier et al. 2024). A session that reads and mirrors the
  reference script, or reasons from the image that the ring lies well inside
  the mask, scores; one that copies the defaults blindly usually does not.
- **Honest reporting.** The reduced χ² (χ² over the number of pixels inside the
  mask) must come from the fit the session ran; the figures must be PNGs it
  made. The committed reference figures under `scripts/cosmos_web_ring/results/`
  do not count, and a session that never ran a fit fails `fit_was_run`.

- **Finishing a long job headlessly.** The fit takes minutes, and a session
  that starts it in the background and then ends its turn waiting for a
  notification orphans the fit and never writes `result.json`; `finished`
  catches this (`no_result_json`). `benchmarks/AGENTS.md` tells a session to
  run the fit in the foreground or poll it to completion in the same turn.

The budgets assume a GPU, or a machine whose CPU XLA compile is fast: the
reference good fit takes 448 s wall on an RTX 2060 (`cuda:0`), most of it JAX
compilation, so `compute_seconds` (900) allows about two fits and
`run_seconds` (1800) adds time for reading the skills. On the 8-core WSL2
laptop the reference fits were made on, 8-thread CPU JAX spent more than 22 min
in the first XLA compile of the 48-start objective and was abandoned: a
CPU-only machine may need a larger budget, which a future card version can add.
The recorded runs give the session the GPU.

## Score

Reference values live in `benchmarks/truth/cosmos-web-ring-fit/truth.json`
(hidden from the session): the good fit's θ_E and reduced χ², the poor
(single-Sérsic source) fit's reduced χ², and the tolerance, half the good–poor
θ_E spread floored at 0.03".

Gates (all must pass; any failure scores 0):

| Gate | Meaning |
|------|---------|
| `finished` | `result.json` exists in the run directory and parses as a JSON object |
| `schema` | `validate_result`: the eight keys, correctly typed |
| `compute_budget` | ≤ 900 s of interpreter time |
| `run_budget` | ≤ 1800 s wall clock |
| `fit_was_run` | ≥ 60 s of interpreter time: a real fit of this model needs minutes |
| `noise_scaling_applied` | `noise_scaling_applied` is `true` |
| `mask_radius` | `mask_radius` within 0.2" of 1.8" |

Metrics (each 0–1; `score = 100 × mean`):

| Metric | Mapping |
|--------|---------|
| `einstein_radius_within_tol` | 1 if \|θ_E − 0.80"\| ≤ tol, falling linearly to 0 at 3 × tol (either the isothermal parameter or the effective radius passes) |
| `fit_quality` | 1 if reduced χ² ≤ 1.1 × the good fit's, 0.5 if ≤ the poor fit's, else 0 |
| `figures_exist` | fraction of the listed PNGs the session made that exist (reference figures excluded) |
| `summary_length` | 1 if the summary is 1–3 sentences |

Which figures existed is decided once, while the workdir exists, and recorded
in `figures_found.json` beside `result.json`, so `score-oneshot` re-scores a
recorded run byte for byte after the workdir is gone.
