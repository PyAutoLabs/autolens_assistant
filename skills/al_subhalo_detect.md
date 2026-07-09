---
name: al_subhalo_detect
description: Detect (or rule out) dark-matter subhaloes in a strong lens via Bayesian model comparison. Compares a base fit (smooth lens mass) against fits with an added perturbing subhalo at a grid of (y, x, mass) positions; the Bayesian evidence ratio is the detection statistic. Requires a converged base fit, typically with a pixelised source (subhalo signatures appear as small residuals only a flexible source can reveal). Pairs with `al_sensitivity_mapping` (what mass could you have detected?). Writes a runnable Python script in scripts/. **Status: stub.**
---

# Subhalo detection in strong lenses

A strong lens whose smooth mass model leaves coherent residuals around a
specific point in the image plane is a subhalo candidate. Detection is a
**model-comparison** problem: fit the lens with vs. without an extra mass
perturber, and let the Bayesian evidence pick the winner. Vegetti & Koopmans
2009 set the template; PyAutoLens automates the grid search.

The workspace path is
`autolens_workspace:scripts/imaging/features/advanced/subhalo/detect/start_here.py`.

## Ask

- *"Do you have a converged base fit already?"* If not, run a SLaM
  pipeline first ([`al_run_slam_pipeline`](./al_run_slam_pipeline.md));
  detection assumes the smooth model is reasonable.
- *"Pixelised or parametric source?"* Pixelised is strongly recommended —
  a parametric source can absorb subhalo-shaped residuals.
- *"Grid resolution — how finely do you want to scan (y, x)?"* Trade-off
  between coverage and compute. A 10×10 grid with one search per cell is
  ~100 fits.
- *"Subhalo mass parameterisation — NFW (with a mass-concentration
  relation) or a tNFW / point mass?"*

## Branch — base + perturber grid

> TODO: recipe. The standard pattern: load the base fit, then iterate over
> a `Grid2D` of subhalo positions, refitting at each cell with an added
> `al.mp.NFW` (or similar). Compare per-cell log evidence to the base
> evidence; significant gains flag detections. See
> `PyAutoLens:autolens/lens/subhalo.py` for the subhalo helper module
> if one exists, otherwise compose by hand.

## Branch — followup on a detection candidate

If a cell shows Δlog-evidence > threshold (commonly ~5–10), run a finer
local grid + a free-mass fit to pin down the subhalo's parameters.

> TODO: recipe.

## Combine

- [`al_sensitivity_mapping`](./al_sensitivity_mapping.md) — calibrate
  "how detectable was this subhalo, given my data?"
- [`al_run_slam_pipeline`](./al_run_slam_pipeline.md) — produces the
  base fit this skill assumes.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) —
  inspect pixelised-source residuals before launching the grid.

## Further reading

- **Student / new to lensing** — [HowToLens: chapter_4_pixelizations](https://github.com/PyAutoLabs/HowToLens/tree/main/notebooks/chapter_4_pixelizations):
  pixelised sources are the foundation for substructure detection.
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  subhalo detection in the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/features/advanced/subhalo/detect/start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/imaging/features/advanced/subhalo/detect/start_here.py):
  the canonical detection pipeline — base fit, grid search, evidence
  comparison.

See also [`wiki/core/concepts/substructure_and_subhalos.md`](../wiki/core/concepts/substructure_and_subhalos.md)
for the physics motivation (CDM vs. WDM, free-streaming length, halo mass
function).
