---
name: al_custom_analysis
description: Subclass `al.AnalysisImaging` / `al.AnalysisInterferometer` / `al.AnalysisPoint` to add a custom likelihood term — kinematic constraints, external priors, joint probes (stellar dynamics + lensing), or any data that isn't natively a pixel grid or visibility set. The subclass overrides `log_likelihood_function(...)` (or a helper called from it). Combining whole datasets is a factor graph, not a subclass (see `al_multi_dataset`). Lighter than `al_custom_profile` (which extends the *model*); this extends the *fit*. Writes a runnable Python script in scripts/.
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

Subclass the stock analysis and add the term to its log-likelihood. The base
`log_likelihood_function` returns the data-residual likelihood; you add a
penalty derived from the model instance.

```python
import autolens as al

SIGMA_OBS = 250.0   # measured velocity dispersion (km/s)
SIGMA_ERR = 15.0

class AnalysisWithSigma(al.AnalysisImaging):
    def log_likelihood_function(self, instance):
        log_likelihood = super().log_likelihood_function(instance)
        sigma_model = derive_sigma(instance.galaxies.lens)  # your forward model
        penalty = -0.5 * ((sigma_model - SIGMA_OBS) / SIGMA_ERR) ** 2
        return log_likelihood + penalty

analysis = AnalysisWithSigma(dataset=dataset)
```

The base class is `PyAutoLens:autolens/imaging/model/analysis.py` (likewise
`interferometer/model/analysis.py`, `point/model/analysis.py`). The `instance`
is a fully-instantiated model — read lens/source parameters off it to compute
your term. Keep the term additive in log-space so it composes with the search.

## Branch — combining whole datasets

If the extra "term" is actually a *second dataset* (a shear catalogue, an ALMA
visibility set, a second band), don't fold it into one analysis subclass — build
one `Analysis` per dataset and combine them with a **factor graph**:

```python
import autofit as af

analysis_factor_list = [
    af.AnalysisFactor(prior_model=model.copy(), analysis=analysis)
    for analysis in [analysis_imaging, analysis_interferometer]
]
factor_graph = af.FactorGraphModel(*analysis_factor_list)
result_list = search.fit(
    model=factor_graph.global_prior_model, analysis=factor_graph
)
```

The graph sums the per-factor log-likelihoods and shares whichever priors you
leave un-overridden across factors. This is the full subject of
[`al_multi_dataset`](./al_multi_dataset.md); use a custom-analysis subclass only
when the extra constraint is *not* its own dataset (a scalar measurement, an
external prior on a derived quantity). Source:
`PyAutoFit:autofit/graphical/declarative/collection.py`.

## Combine

- [`al_custom_profile`](./al_custom_profile.md) — when the gap is in the
  model, not the likelihood.
- [`al_time_delay_cosmography`](./al_time_delay_cosmography.md) — a
  classic use case (kinematic mass-sheet breaker).
- [`al_multi_dataset`](./al_multi_dataset.md) — combining whole datasets is a
  factor graph; this skill is for non-dataset likelihood terms.

## Further reading

- **Student / new to lensing** — _ (advanced PyAutoFit topic).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  analysis customisation in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: guides/advanced/custom_analysis.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/advanced/custom_analysis.py):
  the canonical custom-analysis walkthrough.

See also [`wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md)
for the standard analysis surface this skill extends.
