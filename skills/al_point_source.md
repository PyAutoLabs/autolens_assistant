---
name: al_point_source
description: Fit a strong-lens model to point-source data — multiple-image positions of a lensed quasar / QSO, optionally with flux ratios and time delays. Use when the user has positions (sky coordinates of multiple images) rather than extended-arc imaging, or when imaging is so poor the lensed source is effectively a point. Pairs with `al_time_delay_cosmography` (H0 from delays) and `al_build_imaging_model` (when the same system also has resolved imaging). Writes a runnable Python script in scripts/. **Status: stub — recipe sections need filling in.**
---

# Fitting point-source lens data

Most strong-lens skills assume an extended source (arcs, rings). Point-source
data is different: the *observable* is a small set of image-plane positions
(and optionally fluxes / time delays), not pixel values. Likelihood is built
in the source plane (do all images map back to one point?) rather than the
image plane. Quasar lenses, supernova lenses, and faint compact sources sit
in this regime.

The canonical workspace entry point is
`autolens_workspace:scripts/point_source/modeling.py`. This skill produces
the equivalent for the user's lens.

## Ask

- *"What data do you have — image positions only, positions + flux ratios,
  positions + time delays, or all three?"* Each adds a likelihood term.
- *"How many lensed images — double, quad, or more (cluster-scale)?"*
- *"Lens mass parameterisation — SIE + ExternalShear is the standard
  starting point; PowerLaw if the slope is interesting."*
- *"Are positions associated with one source or several (multi-source
  systems)?"* Workspace covers both.

## Branch — quad lens, positions only

The minimum viable point-source fit. Save to `scripts/point_source.py`.

> TODO: recipe. Pattern is `al.PointDataset` + `al.AnalysisPoint` +
> `model = af.Collection(galaxies=...)` where `source = af.Model(al.Galaxy,
> redshift=..., point_0=af.Model(al.ps.Point))`. See
> `PyAutoLens:autolens/point/dataset.py`,
> `PyAutoLens:autolens/point/model/analysis.py`, and
> `PyAutoGalaxy:autogalaxy/profiles/point/*` for the API surface.

## Branch — positions + fluxes (flux-ratio anomalies)

Adds magnification-ratio constraints that are sensitive to subhalo
substructure along the line of sight. See [`al_subhalo_detect`](./al_subhalo_detect.md)
for the follow-up.

> TODO: recipe.

## Branch — positions + time delays

Folds in temporal delays between images. See
[`al_time_delay_cosmography`](./al_time_delay_cosmography.md) for the
H0-inference workflow built on top of this.

> TODO: recipe.

## Combine

- [`al_time_delay_cosmography`](./al_time_delay_cosmography.md) — H0 from
  joint delay + mass model.
- [`al_subhalo_detect`](./al_subhalo_detect.md) — flux-ratio anomalies as a
  substructure probe.
- [`al_build_imaging_model`](./al_build_imaging_model.md) — when the same
  system has resolved arcs in addition to point images.

## Further reading

- **Student / new to lensing** — [HowToLens: chapter_2 tutorial_3 positions](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_3_positions.ipynb):
  why positions help even when you have extended imaging — and what
  positions-only fitting looks like in isolation.
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  short PointDataset / AnalysisPoint section in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: point_source/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/point_source/start_here.py):
  full point-source fitting walkthrough — dataset, model, analysis, fit
  inspection.

See also [`wiki/core/concepts/point_source.md`](../wiki/core/concepts/point_source.md)
for the physics framing.
