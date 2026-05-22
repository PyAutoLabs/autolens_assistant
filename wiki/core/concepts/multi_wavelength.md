---
title: Multi-wavelength and multi-dataset strong lensing
sources:
  - project: PyAutoLens
    paths:
      - autolens/imaging/model/analysis.py
      - autolens/interferometer/model/analysis.py
    pinned_commit: main
last_updated: 2026-05-22
---

# Multi-wavelength / multi-dataset modelling

**Status: stub — content to be filled out.** Most science cases that
graduate from a single image fit eventually involve multiple datasets:
N bands of the same lens, joint imaging + interferometry, multi-epoch
follow-up. The lens is one thing; the views of it are many. PyAutoLens's
multi-dataset framework lets the model state which parameters are
shared and which are per-dataset.

## Shared vs. per-dataset parameters

> TODO: typical sharing — mass model always shared; source morphology
> shared up to wavelength-dependent intensity; PSFs / backgrounds
> per-dataset; astrometric offsets free per-dataset.

## Wavelength-dependent source morphology

> TODO: parametric form (Sersic with intensity = f(λ)), pixelised
> per-band, or hybrid. The chromatic information constrains the
> source's stellar populations / SED.

## Joint imaging + interferometer

> TODO: visibility constraints pin small-scale source structure; imaging
> pins extended low-surface-brightness emission. The two together break
> degeneracies neither has alone.

## Analysis composition pattern

> TODO: PyAutoLens's pattern is `analysis = sum(per_dataset_analyses)`
> (the `+` operator on analysis objects sums log-likelihoods). Document
> the convention and how `AnalysisFactor` / `FactorGraph` extend it.

## Astrometric offset nuisance parameters

> TODO: real multi-instrument data is rarely co-registered to
> sub-pixel; per-dataset shift parameters absorb the offset.

## Related pages

- [`api/datasets.md`](../api/datasets.md) — per-dataset classes.
- [`api/analysis_objects.md`](../api/analysis_objects.md) — analysis
  combination operator.
- [`concepts/interferometer_theory.md`](./interferometer_theory.md) —
  for the visibility side of joint fits.
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) —
  population-level fits across *independent* lenses, not the same lens
  seen multiply.
