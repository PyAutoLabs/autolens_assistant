---
title: Deep learning for strong lensing
type: concept
topics: [methods]
sources:
  - Strong_Lens/Pearson2020MLAndParametric.pdf
  - Strong_Lens/Pearson2024StrongLensJWST.pdf
  - Strong_Lens/Morningstar2019DeepLearnGalaxyRecon.pdf
  - Strong_Lens/WagnerCarena2021BNNHierachical.pdf
  - Strong_Lens/Brehmer2019MiningDMSub.pdf
status: drafted
---

# Deep learning for strong lensing

## TL;DR

Neural networks are used in three roles:

1. **Lens finding** ([[lens-finding]]) — well-established.
2. **Lens-model parameter estimation** — Pearson 2020, 2024; Wagner-Carena
   2021 (Bayesian neural networks with hierarchical posteriors).
3. **Source reconstruction** — Morningstar 2019; recurrent inference
   machines; diffusion-based source priors (2024–2026).
4. **Substructure detection** — Brehmer 2019 mining the latent
   information; Diaz Rivero 2019; simulation-based inference for the
   subhalo population.

## What works and what doesn't

- Lens finders: production-ready.
- Point-estimate parameter inference: 10–100× faster than MCMC but with
  uncalibrated uncertainties unless explicitly Bayesian.
- BNNs with hierarchical priors (Wagner-Carena 2021): calibrated
  uncertainties on lens-population parameters.
- Simulation-based inference (SBI / amortised inference) — increasingly
  used for substructure-population inference where direct likelihood is
  intractable.

## Limitations

- Out-of-distribution failure: a network trained on power-law lenses
  fails on composite ones, and vice versa.
- PSF/noise/calibration shifts between training simulations and real
  surveys.
- Substructure detection NNs report population statistics but rarely
  identifiable individual detections.

## Why it matters for PyAutoLens

PyAutoLens is a likelihood-based code; it does not itself train NNs but
is widely used for **simulator-truth generation** for NN training
(Pearson 2024 used PyAutoLens-style mocks). Hybrid pipelines (NN for
initial estimate → PyAutoLens refinement) are common.

## See also

- [[lens-finding]]
- [[bayesian-inference-lensing]]
- [[dark-matter-substructure]]
- [[sources-deep-learning-lensing]]
