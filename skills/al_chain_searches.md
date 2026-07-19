---
name: al_chain_searches
description: Run a sequence of non-linear searches where each later search inherits priors from the previous result. Standard pattern for moving from simple parametric models (fast, easy) to complex pixelised or chained models (slow, sensitive to initial position). Pairs with `al_run_slam_pipeline` (which is itself the canonical multi-stage chain) and `al_build_imaging_model`.
---

# Chaining searches

A lens model with 20+ free parameters and a pixelised source is hard to fit from
broad priors. The robust approach is to run a *sequence* of searches: a fast simple
fit first (Sersic source, broad priors), then a more complex fit (pixelised source)
whose priors are seeded from the earlier result.

PyAutoFit's prior-chaining API lets the second search reuse the first's posterior as
its prior, narrowing parameter space dramatically.

Canonical reference: `autolens_workspace:scripts/guides/modeling/chaining.py`.

## Ask

- *"What's the simple-first model that you trust to converge?"* — usually a Sersic
  source + SIE lens.
- *"What's the more complex model you ultimately want?"* — pixelised source, MGE lens
  light, PowerLaw mass, etc.
- *"How much do you want to lock down between phases?"* — full posterior inheritance
  (tight) vs. mean-only with widened uncertainties (loose).

## Branch — two-phase chain (parametric → pixelised source)

```python
# scripts/chain.py
"""
Chain Searches: Parametric -> Pixelised Source
==============================================

Chain two non-linear searches: a fast parametric fit that locks down the lens mass, then a
pixelised-source fit that inherits the mass posterior as its prior. Chaining keeps the
expensive flexible model from having to explore the full prior volume from scratch.

__Contents__

- **Setup:** Imports (assumes `dataset` is already loaded — see al_prepare_imaging_data).
- **Phase 1:** SIE + Sersic source, fast initial fit.
- **Phase 2:** Pixelised source, priors inherited from phase 1.
"""

"""
__Setup__

Assumes `dataset` is already loaded (see al_prepare_imaging_data). The `jax_wrapper` import
must precede the other PyAuto* imports so the JAX environment is configured first.
"""
from autonerves import jax_wrapper
import autofit as af
import autolens as al

"""
__Phase 1__

A fast initial fit with an SIE + external-shear mass and a parametric Sersic source
(`al.mp.Isothermal`, `al.mp.ExternalShear`, `al.lp.SersicCore`). This pins down the lens
mass cheaply before we pay for a pixelised source.
"""
lens_1 = af.Model(
    al.Galaxy,
    redshift=0.5,
    mass=af.Model(al.mp.Isothermal),
    shear=af.Model(al.mp.ExternalShear),
)
source_1 = af.Model(al.Galaxy, redshift=1.0, bulge=af.Model(al.lp.SersicCore))
model_1 = af.Collection(galaxies=af.Collection(lens=lens_1, source=source_1))

analysis = al.AnalysisImaging(dataset=dataset)
search_1 = af.Nautilus(path_prefix="chain_demo", name="phase_1_parametric", n_live=100)

result_1 = search_1.fit(model=model_1, analysis=analysis)

"""
__Phase 2__

Swap in a pixelised source for maximum source flexibility,
inheriting the lens mass and shear from phase 1's posterior so the search
starts from a good region of parameter space rather than the prior. `result_1.model`
returns a new `af.Model` whose priors are the previous search's posterior, keeping the
parameters free to vary.
"""
lens_2 = af.Model(
    al.Galaxy,
    redshift=0.5,
    mass=result_1.model.galaxies.lens.mass,   # inherits the posterior as prior
    shear=result_1.model.galaxies.lens.shear,
)

source_2 = af.Model(
    al.Galaxy,
    redshift=1.0,
    pixelization=af.Model(
        al.Pixelization,
        # NOTE: Delaunay + ConstantSplit is the standard production choice, but a
        # known regression (PyAutoArray #332, still open) crashes Delaunay inside
        # FitImaging and breaks ConstantSplit on RectangularUniform. Until it is
        # fixed, use the combination below.
        mesh=al.mesh.RectangularUniform,
        regularization=al.reg.Constant,
    ),
)
model_2 = af.Collection(galaxies=af.Collection(lens=lens_2, source=source_2))

search_2 = af.Nautilus(path_prefix="chain_demo", name="phase_2_pixelized", n_live=150)
result_2 = search_2.fit(model=model_2, analysis=analysis)
```

The key line is `mass=result_1.model.galaxies.lens.mass`. `result_1.model` returns a
new `af.Model` whose priors are the previous search's posterior — Gaussian-bounded
around the maximum likelihood, with widths from the posterior. To use the
*instance* values (locked) instead of the model: `result_1.instance.galaxies.lens.mass`.

Source citations:
- `PyAutoFit:autofit/non_linear/result.py` — `result.model` vs `result.instance`.
- `PyAutoFit:autofit/mapper/prior_model/prior_model.py` — `af.Model` with inherited
  priors.

Wiki:
- [`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md) — what
  prior inheritance does mechanically.
- [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md)
  — the pixelised-source side of phase 2.

## Branch — N-phase pipeline

For 3+ phases, the same pattern repeats: each phase inherits selectively from earlier
ones. The fully-automated version of this is the SLaM (Source-Light-Mass) pipeline —
see [`al_run_slam_pipeline`](./al_run_slam_pipeline.md). Roll your own chain when SLaM
doesn't match your problem.

## Combine

- [`al_run_slam_pipeline`](./al_run_slam_pipeline.md) — the canonical 4–6 phase chain.
- [`al_load_results`](./al_load_results.md) — load any phase's results independently.
- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — if a later phase fails because
  earlier-phase priors were too tight.

## Further reading

- **Student / new to lensing** — [HowToLens: Breaking modeling into sequential
  searches](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_1_search_chaining.ipynb):
  introduces chaining — why a sequence of fits beats a single high-dimensional one.
  Chapter 3 as a whole develops the pattern.
- **General reference** — [RTD: Model cookbook](https://pyautolens.readthedocs.io/en/latest/general/model_cookbook.html):
  systematic reference for inheriting and adjusting priors between models, the
  mechanical core of chaining.
- **Experienced PyAutoLens user** — [workspace/lens: guides/modeling/slam_start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/modeling/slam_start_here.py):
  SLaM is the canonical multi-phase chain; this script overviews it stage-by-stage.
