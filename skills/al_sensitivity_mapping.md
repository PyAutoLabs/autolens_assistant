---
name: al_sensitivity_mapping
description: Map the substructure-detection sensitivity of a strong lens by injecting synthetic subhaloes into simulated datasets matched to the user's data, fitting each with and without a subhalo, and measuring the Bayesian-evidence gain. Produces a (y, x, mass) map of "what could you have detected?" Calibrates non-detections from `al_subhalo_detect` and constrains the subhalo mass function. Writes a runnable Python script in ./work/. **Status: stub.**
---

# Sensitivity mapping for substructure

A null result from [`al_subhalo_detect`](./al_subhalo_detect.md) is only
informative if you know what the data *could* have detected. Sensitivity
mapping answers that: simulate the same dataset with a subhalo injected at
many (y, x, mass) positions, refit each, and record the evidence gain.
The result is a map of detectability thresholds.

Workspace path:
`autolens_workspace:scripts/imaging/features/advanced/subhalo/sensitivity/start_here.py`.

## Ask

- *"What's the base model — the result of the same SLaM run that fed
  `al_subhalo_detect`?"*
- *"Grid range — over what (y, x) extent and what mass range should we
  scan?"* Defaults are dataset-dependent; usually a few arcsec around the
  arcs, masses 1e8–1e10 M_sun.
- *"How many simulations per cell — 1 is fast and informative, ~5–10
  averages out noise realisations?"*
- *"Compute budget?"* Sensitivity mapping is the most expensive workflow
  in the workspace; expect HPC.

## Branch — full grid sensitivity map

> TODO: recipe. The pattern: define a `SensitivityMapping` job that takes
> the base fit + grid of perturber parameters; per cell, simulate, fit
> base + fit perturbed, store Δlog-evidence. Aggregate into a map. See
> `PyAutoFit:autofit/non_linear/grid/sensitivity.py` for the framework
> and `PyAutoLens:autolens/lens/sensitivity.py` (if present) for the
> lensing wrapper.

## Branch — combining with a non-detection

Pair a sensitivity map with a population model of subhaloes (CDM HMF or
WDM-suppressed) to translate "no detection" into a constraint on, e.g.,
WDM particle mass or the subhalo mass function normalisation.

> TODO: recipe — likely requires a custom analysis chained to the
> sensitivity output.

## Combine

- [`al_subhalo_detect`](./al_subhalo_detect.md) — the detection pipeline
  this calibrates.
- [`al_hierarchical_inference`](./al_hierarchical_inference.md) — stacking
  sensitivity maps across a sample for population-level constraints.
- [`al_simulate_dataset`](./al_simulate_dataset.md) — the per-cell
  simulation primitive.

## Further reading

- **Student / new to lensing** — _ (no HowToLens equivalent — sensitivity
  mapping is a research-grade workflow).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  brief mention of sensitivity mapping under subhalo features.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/features/advanced/subhalo/sensitivity/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/advanced/subhalo/sensitivity/start_here.py):
  the canonical sensitivity workflow — simulator config, fit-pair loop,
  evidence-map output.

See also [`wiki/core/concepts/sensitivity_mapping.md`](../wiki/core/concepts/sensitivity_mapping.md)
for the Bayesian framing and the relation to upper limits.
