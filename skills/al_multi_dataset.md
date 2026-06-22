---
name: al_multi_dataset
description: Fit a strong lens to multiple datasets jointly — multi-band imaging (same target, different filters), joint imaging + interferometer, time-series, or any combination where one lens is observed by multiple instruments. Builds a PyAutoFit factor graph (`af.AnalysisFactor` per dataset, combined with `af.FactorGraphModel`). Supports wavelength-dependent source morphologies, dataset-level astrometric offsets, and shared/independent parameters between datasets. Pairs with `al_hierarchical_inference` (when datasets are independent lenses, not independent observations of the same lens). Writes a runnable Python script in scripts/.
---

# Multi-dataset joint fitting

Many real lensing analyses observe the same lens in more than one band, or
combine imaging with interferometric visibilities, or follow up a
candidate over time. The wins are scientific: chromatic source structure
constrains stellar populations, joint imaging+visibility breaks degeneracies
the visibilities alone leave, and dataset-level nuisance parameters
(astrometric offsets, PSF errors) become marginalisable.

Workspace path: `autolens_workspace:scripts/multi/start_here.py`,
`scripts/multi/features/wavelength_dependence/modeling.py`,
`scripts/multi/features/imaging_and_interferometer/modeling.py`.

## Ask

- *"What datasets — N bands of the same imaging, imaging + ALMA visibilities,
  multi-epoch, or something else?"* Picks the analysis composition.
- *"What's shared between datasets — the mass model, the source morphology,
  both, or neither?"* Almost always the mass is shared.
- *"Is the source wavelength-dependent (colour gradient, different
  morphology per band)?"* If yes, you parametrise that explicitly.
- *"Astrometric offsets between datasets — known or free?"* Free offsets
  are common with HST vs. ground-based stacks.

## How combining works — the factor graph

Every branch below is the same four-step factor graph; only the per-factor
model overrides differ. You never combine the `Analysis` objects directly —
you wrap each in an `af.AnalysisFactor` and combine the *factors*:

1. one `Analysis` per dataset;
2. wrap each in `af.AnalysisFactor(prior_model=model.copy(), analysis=analysis)`;
3. combine with `af.FactorGraphModel(*analysis_factor_list)`;
4. fit with `result_list = search.fit(model=factor_graph.global_prior_model,
   analysis=factor_graph)` — one `Result` per factor.

With a bare `model.copy()` and no overrides, the graph *identifies*
(deduplicates) every prior across factors, so the whole model is shared and
its dimensionality equals the single-dataset model. To free a parameter per
dataset, override that prior on the `model.copy()` *before* wrapping it.
Source: `PyAutoFit:autofit/graphical/declarative/factor/analysis.py`,
`PyAutoFit:autofit/graphical/declarative/collection.py`.

## Branch — multi-band imaging, shared mass + per-band source

The mass is shared across bands; the source brightness is free per band.

```python
import autofit as af
import autolens as al

# Base model, composed once: shared lens mass + source geometry.
lens = af.Model(al.Galaxy, redshift=0.5, mass=al.mp.Isothermal)
source = af.Model(al.Galaxy, redshift=1.0, bulge=al.lp.Sersic)
model = af.Collection(galaxies=af.Collection(lens=lens, source=source))

analysis_list = [al.AnalysisImaging(dataset=dataset) for dataset in dataset_list]

# Free the source intensity per band; mass + geometry stay shared (identified).
analysis_factor_list = []
for analysis in analysis_list:
    model_band = model.copy()
    model_band.galaxies.source.bulge.intensity = af.LogUniformPrior(
        lower_limit=1e-2, upper_limit=1e2
    )
    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_band, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list)

search = af.Nautilus(path_prefix="multi", name="multiband")
result_list = search.fit(
    model=factor_graph.global_prior_model, analysis=factor_graph
)
```

Canonical: `autolens_workspace:scripts/multi/start_here.py` (and
`scripts/multi/features/wavelength_dependence/modeling.py` for the relation form).

## Branch — imaging + interferometer joint

One mass model must satisfy both views. Build one analysis of each type and
combine them with the same factor graph; the visibilities pin compact source
structure the imaging can't resolve.

```python
analysis_list = [
    al.AnalysisImaging(dataset=imaging),
    al.AnalysisInterferometer(dataset=interferometer),
]

analysis_factor_list = [
    af.AnalysisFactor(prior_model=model.copy(), analysis=analysis)
    for analysis in analysis_list
]

factor_graph = af.FactorGraphModel(*analysis_factor_list)
result_list = search.fit(
    model=factor_graph.global_prior_model, analysis=factor_graph
)
```

Canonical: `autolens_workspace:scripts/multi/features/imaging_and_interferometer/modeling.py`.

## Branch — wavelength-dependent source

Source parameters (e.g. Sersic `intensity`, `effective_radius`) depend
explicitly on wavelength via a parametric relation — useful for distinguishing
star formation from old stellar populations. The mechanism is identical: build
the per-band `model.copy()`, but instead of an independent free prior per band,
set the wavelength-varying parameter from a shared relation (e.g. a linear
`y = m * wavelength + c` whose `m`, `c` priors are shared across factors). See
`autolens_workspace:scripts/multi/features/wavelength_dependence/modeling.py`.

## Combine

- [`al_build_imaging_model`](./al_build_imaging_model.md) and
  [`al_build_interferometer_model`](./al_build_interferometer_model.md) —
  the single-dataset building blocks.
- [`al_hierarchical_inference`](./al_hierarchical_inference.md) — when
  the goal is *population* inference from many lenses, not joint fit of
  one lens.

## Further reading

- **Student / new to lensing** — _ (no direct HowToLens chapter).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  multi-dataset section.
- **Experienced PyAutoLens user** — [workspace/lens: multi/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/multi/start_here.py):
  the canonical multi-dataset walkthrough; features/ folder has
  per-scenario examples.

See also [`wiki/core/concepts/multi_wavelength.md`](../wiki/core/concepts/multi_wavelength.md)
for the chromatic-source physics.
