---
name: al_custom_analysis
description: Subclass `al.AnalysisImaging` / `al.AnalysisInterferometer` / `al.AnalysisPoint` to add a custom likelihood term — kinematic constraints, external priors, joint probes (stellar dynamics + lensing), or any data that isn't natively a pixel grid or visibility set. The subclass overrides `log_likelihood_function(...)` (or a helper called from it). Lighter than `al_custom_profile` (which extends the *model*); this extends the *fit*. Writes a runnable Python script in ./work/. **Status: stub.**
---

# Custom analysis — extending the likelihood

PyAutoLens's stock analysis classes assume a single data type and a
standard residual likelihood. When you need a *non-standard* likelihood
term — kinematic dispersion measurements, external H0 priors, joint
strong+weak fits with shared mass, anything that isn't a 2D residual —
you subclass the relevant analysis class and add the term.

Workspace path: `autolens_workspace:scripts/guides/advanced/custom_analysis.py`.

## Ask

- *"What's the extra likelihood term — a single measurement (e.g. velocity
  dispersion + uncertainty), a dataset (a shear catalogue), a prior on a
  derived quantity (Einstein mass)?"*
- *"Does the extra term depend on the lens parameters only, or also on
  the source / inversion?"* This decides whether you can reuse fit
  outputs or need to recompute.
- *"Are you combining analyses (one per dataset) or adding a term to one
  analysis?"* Both patterns are valid.

## Branch — adding a single-measurement prior

> TODO: recipe. Pattern: `class AnalysisWithSigma(al.AnalysisImaging):
>     def log_likelihood_function(self, instance):
>         base = super().log_likelihood_function(instance)
>         sigma_model = derive_sigma(instance.galaxies.lens)
>         penalty = -0.5 * ((sigma_model - SIGMA_OBS) / SIGMA_ERR) ** 2
>         return base + penalty`. See
> `PyAutoLens:autolens/imaging/model/analysis.py` for the base class.

## Branch — combining analyses

> TODO: recipe. Use `AnalysisImaging + AnalysisInterferometer` (operator
> overload sums log-likelihoods) when both datasets share a model.

## Combine

- [`al_custom_profile`](./al_custom_profile.md) — when the gap is in the
  model, not the likelihood.
- [`al_time_delay_cosmography`](./al_time_delay_cosmography.md) — a
  classic use case (kinematic mass-sheet breaker).
- [`al_multi_dataset`](./al_multi_dataset.md) — combined analyses are a
  superset of multi-dataset fitting.

## Further reading

- **Student / new to lensing** — _ (advanced PyAutoFit topic).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  analysis customisation in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: guides/advanced/custom_analysis.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/advanced/custom_analysis.py):
  the canonical custom-analysis walkthrough.

See also [`wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md)
for the standard analysis surface this skill extends.
