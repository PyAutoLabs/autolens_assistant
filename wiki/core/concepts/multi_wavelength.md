---
title: Multi-wavelength and multi-dataset strong lensing
sources:
  - project: PyAutoFit
    paths:
      - autofit/graphical/declarative/factor/analysis.py
      - autofit/graphical/declarative/collection.py
      - autofit/graphical/declarative/abstract.py
    pinned_commit: ce2baa2b6611de99922e04d44b272de1be3ceb8e
  - project: PyAutoLens
    paths:
      - autolens/imaging/model/analysis.py
      - autolens/interferometer/model/analysis.py
    pinned_commit: ae4a27afc0fe7ad712777807d4269759c1a2b6ed
last_updated: 2026-06-22
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

## Analysis composition pattern — the factor graph

At the API level, multi-dataset fitting is a factor graph. Each dataset
gets its own `AnalysisImaging` or `AnalysisInterferometer`; each analysis
is wrapped in an `af.AnalysisFactor` that pairs it with a model; and the
factors are combined into an `af.FactorGraphModel` whose log-likelihood is
the sum of the per-factor log-likelihoods.

```python
import autofit as af

analysis_list = [al.AnalysisImaging(dataset=dataset) for dataset in dataset_list]

analysis_factor_list = [
    af.AnalysisFactor(prior_model=model.copy(), analysis=analysis)
    for analysis in analysis_list
]

factor_graph = af.FactorGraphModel(*analysis_factor_list)

result_list = search.fit(
    model=factor_graph.global_prior_model, analysis=factor_graph
)
```

Shared vs. free parameters are expressed through the model, not by
special-casing the datasets. With a bare `model.copy()` and no overrides,
the graph *identifies* (deduplicates) every prior across factors, so the
whole model is shared. Free a parameter per dataset — a per-band source
`intensity`, a per-dataset astrometric offset — by overriding that prior on
the `model.copy()` before wrapping it in its `AnalysisFactor`. The same
machinery scales smoothly to genuinely hierarchical graphs (population
priors over many lenses) via `af.HierarchicalFactor`, without changing the
composition pattern. See `autolens_workspace:scripts/multi/start_here.py`
and [`api/analysis_objects.md`](../api/analysis_objects.md).

## Astrometric offset nuisance parameters

Real datasets are rarely co-registered perfectly. Small sub-pixel shifts
between HST, AO, ALMA, or catalog-based cutouts can otherwise leak into
the lens model. Per-dataset offset parameters are therefore standard
nuisance parameters in serious joint fits. They let the data align in the
source plane without forcing the mass model to fake the registration.

## Related pages

- [`api/datasets.md`](../api/datasets.md) — per-dataset classes.
- [`api/analysis_objects.md`](../api/analysis_objects.md) — the
  `AnalysisFactor` / `FactorGraphModel` combination API.
- [`concepts/interferometer_theory.md`](./interferometer_theory.md) —
  for the visibility side of joint fits.
- [`concepts/hierarchical_models.md`](./hierarchical_models.md) —
  population-level fits across *independent* lenses, not the same lens
  seen multiply.
