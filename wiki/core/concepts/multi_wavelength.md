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

Most science cases that
graduate from a single image fit eventually involve multiple datasets:
N bands of the same lens, joint imaging + interferometry, multi-epoch
follow-up. The lens is one thing; the views of it are many. PyAutoLens's
multi-dataset framework lets the model state which parameters are
shared and which are per-dataset.

## Shared vs. per-dataset parameters

The central design question is what is physically common across datasets
and what is instrument- or band-specific.

Usually shared:

- the lens mass model
- source geometry, at least as a starting point
- lens-galaxy center and orientation

Usually per-dataset:

- PSF or uv sampling
- background level and masking
- photometric normalization
- astrometric offsets

Some source parameters sit in the middle. A galaxy's centroid and shape
may be shared, while its intensity, color, or compact clumps change with
wavelength.

## Wavelength-dependent source morphology

There are three common strategies.

- **Shared morphology, free intensity per band.**
  Good when the same source component is seen in each filter but with
  different brightness.

- **Partially shared parametric models.**
  Geometry is tied while specific parameters, such as effective radius
  or color gradients, are allowed to vary.

- **Per-band pixelized reconstructions.**
  Best when morphology genuinely changes with wavelength or when the data
  quality differs enough that a rigid parametric tie would be misleading.

The choice is scientific as well as technical: chromatic freedom lets you
infer stellar-population or dust structure, but too much freedom can let
one band absorb modeling failures that another band would have exposed.

## Joint imaging + interferometer

Imaging and interferometer data are complementary rather than redundant.
Resolved imaging often captures broad low-surface-brightness structure and
lens-galaxy light cleanly; interferometer visibilities can pin compact
clumps and line-emission structure at high effective resolution. A joint
fit forces one mass model to satisfy both views at once, which is often
more constraining than either dataset individually.

## Analysis composition pattern

At the API level, multi-dataset fitting is just composition of analysis
objects. Each dataset gets its own `AnalysisImaging` or
`AnalysisInterferometer`, and the combined fit is formed with the `+`
operator:

```python
analysis = analysis_g + analysis_r + analysis_alma
```

The combined analysis sums log likelihoods. Shared parameters are created
in the model composition, not by special-casing the datasets. When the
dependency graph becomes more complicated than "sum these analyses",
PyAutoFit's graphical-model framework generalizes the same idea via
`AnalysisFactor` and `FactorGraphModel`.

## Astrometric offset nuisance parameters

Real datasets are rarely co-registered perfectly. Small sub-pixel shifts
between HST, AO, ALMA, or catalog-based cutouts can otherwise leak into
the lens model. Per-dataset offset parameters are therefore standard
nuisance parameters in serious joint fits. They let the data align in the
source plane without forcing the mass model to fake the registration.

## Related pages

- [`api/datasets.md`](../api/datasets.md) — per-dataset classes.
- [`api/analysis_objects.md`](../api/analysis_objects.md) — analysis
  combination operator.
- [`concepts/interferometer_theory.md`](./interferometer_theory.md) —
  for the visibility side of joint fits.
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) —
  population-level fits across *independent* lenses, not the same lens
  seen multiply.
