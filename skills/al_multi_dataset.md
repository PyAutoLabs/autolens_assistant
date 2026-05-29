---
name: al_multi_dataset
description: Fit a strong lens to multiple datasets jointly — multi-band imaging (same target, different filters), joint imaging + interferometer, time-series, or any combination where one lens is observed by multiple instruments. Supports wavelength-dependent source morphologies, dataset-level astrometric offsets, and shared/independent parameters between datasets. Pairs with `al_hierarchical_inference` (when datasets are independent lenses, not independent observations of the same lens). Writes a runnable Python script in ./work/. **Status: stub.**
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

## Branch — multi-band imaging, shared mass + per-band source

> TODO: recipe. Pattern: one `AnalysisImaging` per dataset, summed via
> `af.AnalysisFactor` objects inside an `af.FactorGraphModel`, one shared
> `mass` model, per-band `source` models. See
> `PyAutoLens:autolens/imaging/model/...`.

## Branch — imaging + interferometer joint

> TODO: recipe. Mix `AnalysisImaging` + `AnalysisInterferometer`; sum
> log-likelihoods. The visibilities pin source structure on small scales
> the imaging can't resolve.

## Branch — wavelength-dependent source

Source parameters (e.g. Sersic intensity, half-light radius) depend
explicitly on wavelength via a parametric relation. Useful for distinguishing
star formation from old stellar populations.

> TODO: recipe.

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
