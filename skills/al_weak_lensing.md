---
name: al_weak_lensing
description: Fit a shear catalogue with PyAutoLens's weak-lensing module — `al.WeakDataset` + `al.FitWeak`. Use when the observable is a per-source shear estimate (γ1, γ2) at a known sky position, not an extended-arc image. Lighter than strong lensing: no PSF, no inversion, no positions likelihood — just a residual model in shear space. Complements strong-lensing fits when the same cluster has both regimes. Writes a runnable Python script in ./work/. **Status: stub.**
---

# Weak lensing — shear catalogue fits

Weak lensing is the statistical regime: each background source is barely
distorted, and you fit a mass model to the *ensemble* shear field across
many sources. The PyAutoLens weak module is intentionally narrow — it
gives you a `WeakDataset` (positions + shear estimates + their errors) and
a `FitWeak` that compares them to a model-predicted shear field.

Workspace path: `autolens_workspace:scripts/weak/fit.py`.

## Ask

- *"What's the source — a shear catalogue (one row per source: ra, dec,
  γ1, γ2, σ), or something coarser like a tangential-shear profile?"*
- *"Is this standalone or combined with strong lensing on the same
  system?"* Cluster cosmology often combines both.
- *"Mass parameterisation — NFW for a cluster halo, scaled NFW + member
  contributions, or something custom?"*

## Branch — single-halo NFW fit

> TODO: recipe. Pattern: `dataset = al.WeakDataset.from_csv(...)`,
> `analysis = al.AnalysisWeak(dataset=dataset)`, model is a `Galaxy` with
> an NFW mass profile, run the standard search. See
> `PyAutoLens:autolens/weak/...` for the dataset + analysis classes.

## Branch — joint strong + weak

Sum the strong-lens log-likelihood and the weak-lens log-likelihood;
shared mass model across both. Powerful for clusters where the arcs pin
the inner profile and the shear field pins the outer.

> TODO: recipe.

## Combine

- [`al_group_lensing`](./al_group_lensing.md) / [`al_cluster_csv_api`](./al_cluster_csv_api.md) — when the weak-lensing signal sits on top of a multi-galaxy strong-lens model.
- [`al_build_imaging_model`](./al_build_imaging_model.md) — strong-lens
  side of a joint fit.

## Further reading

- **Student / new to lensing** — _ (HowToLens focuses on strong lensing;
  weak is covered only in passing).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  weak lensing in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: weak/fit.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/weak/fit.py):
  the canonical weak-lensing fit.

See also [`wiki/core/concepts/weak_lensing.md`](../wiki/core/concepts/weak_lensing.md)
for the physics (cosmic shear vs. cluster shear, intrinsic alignments,
shear measurement systematics).
