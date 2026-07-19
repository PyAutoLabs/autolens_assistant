---
name: al_debug_fit_failure
description: Diagnose a non-linear search that didn't converge, returned unphysical parameters, or produced an inversion that fitted noise rather than signal. Walks the canonical post-mortem checks — log inspection, residual maps, prior coverage, multimodality, inversion regularisation, position penalties — and proposes targeted fixes (tighten priors, switch search, add positions, increase live points). Use after `al_run_search` returns a result that looks wrong.
---

# Debugging a fit that went wrong

A finished search isn't automatically a successful one. PyAutoFit will return a
`Result` regardless of whether the posterior is sensible. This skill walks the user
through the symptom → diagnosis → fix loop for common lens-fit failures.

Reference reading: `autolens_workspace:scripts/guides/modeling/bug_fix.py`.

## Ask

Before diagnosing, get the user to describe the failure mode:

- *"Did the search complete, or did it crash with an exception?"* — different
  branches.
- *"What looks wrong — the residuals, the parameter values, the chi-squared, the
  source reconstruction?"* — picks the diagnostic.
- *"Have you compared against an `PYAUTO_TEST_MODE=1` smoke run?"* — sometimes the
  symptom is just a bug in the script that the smoke test would have caught.

## Branch — search crashed mid-run

Read the search log: `output/<path>/.../search.log`. Common causes:

- **Likelihood evaluation crashed.** Read the traceback. Often a profile parameter
  has gone unphysical (negative effective radius, zero einstein radius). Tighten the
  prior bounds with `af.UniformPrior(lower_limit=..., upper_limit=...)`.
- **Numba cache write failure.** Set `NUMBA_CACHE_DIR=/tmp/numba_cache` and rerun.
- **JAX out-of-memory.** Reduce `n_live`, mask radius, or pixelisation resolution; or
  disable JAX for this run.

## Branch — search completed but residuals are huge

Load the result and look at the fit (same pattern as
[`al_load_results`](./al_load_results.md) — load the max-log-likelihood tracer from
JSON, reload the dataset, rebuild the fit):

```python
from pathlib import Path
from autonerves.dictable import from_json
import autolens as al
import autolens.plot as aplt

out = Path("output/imaging/<your_lens>/<name>/<hash>")
tracer = from_json(file_path=out / "files" / "tracer.json")

# Reload the dataset exactly as the fit script did (path, pixel_scales, mask).
dataset = ...  # see al_prepare_imaging_data

fit = al.FitImaging(dataset=dataset, tracer=tracer)
aplt.subplot_fit_imaging(
    fit=fit, output_path="scripts/scratch/debug/", output_filename="fit",
    output_format="png",
)
```

Look at the residual map. Common signatures:

- **Mass model off-axis.** Residuals form a "double-image" pattern where the model
  positions don't match the data positions. Fix: add image positions and a
  `PositionsLH` (see `al_run_slam_pipeline` for the pattern).
- **Source too constrained.** The source reconstruction looks like a single Sersic
  but the data shows a complex arc. Fix: switch to a pixelised source via
  [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md).
- **Lens light leaking into source plane.** Residuals show systematic structure at
  the lens centre. Fix: add or refine the lens light model.

## Branch — search completed but converged to a clearly wrong mode

Symptoms: parameter posteriors are tight but at unphysical values (einstein radius
~0.01", lens at the edge of the mask, source at the lens centre).

- **Multi-modal posterior, picked the wrong mode.** Switch to or rerun with more live
  points: `af.Nautilus(n_live=400)`. Nested sampling handles multimodality better
  than MCMC.
- **Prior pulling the search into a bad region.** Widen or recentre priors on the
  parameters that look wrong. Inspect with `model.info` before fitting.
- **Mask cropping out part of the lensed signal.** Widen the mask radius and refit.

## Branch — pixelised source looks like noise

The inversion has over-fitted background noise into the source plane.

- **Regularisation too low.** Bump the regularisation coefficient range — see
  `PyAutoArray:autoarray/inversion/regularization/`. The `ConstantSplit` regularisation
  with sensible coefficients usually works.
- **No positions penalty.** Add a `PositionsLH` to prevent the inversion from
  demagnifying the source into infinity.
- **Pixelisation grid too fine.** Coarsen the `mesh_shape` (e.g. from (50, 50) to
  (30, 30)).

[`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md)
covers regularisation and pixelisation theory.

## Branch — fit looks fine but evidence is much worse than a competing model

The fit may have converged to a local maximum. Run again with different priors or
a different `unique_tag` so the search starts fresh, and compare evidences.

## Generic fixes that often help

- **Add positions.** `al.PositionsLH` (with the user's measured image
  positions) eliminates a large class of mass-model failures.
- **Tighten the prior on the lens centre.** It's often the parameter with the worst
  multi-modality.
- **Smoke-test with `PYAUTO_TEST_MODE=1`** to confirm there's no scripting bug masquerading
  as a fit bug.
- **Run with a coarser model first** (single Sersic source, SIE mass) before adding
  pixelisations. Use [`al_chain_searches`](./al_chain_searches.md) to chain.

## Combine

Once you've identified the issue, the fix usually means re-running with adjusted
inputs — [`al_run_search`](./al_run_search.md) — and re-loading the new result —
[`al_load_results`](./al_load_results.md). If the diagnosis was wrong, iterate.

## Further reading

- **Student / new to lensing** — [HowToLens: Recovering from local maxima](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_4_dealing_with_failure.ipynb):
  the three canonical recoveries — prior tuning, multi-start, model simplification.
- **General reference** — [RTD: Demagnified solutions](https://pyautolens.readthedocs.io/en/latest/general/demagnified_solutions.html):
  how unphysical demagnified-source reconstructions arise in pixelised fits, and how
  `PositionsLH` penalties prevent them.
- **Experienced PyAutoLens user** — [workspace/lens: guides/tracer.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/tracer.py):
  inspecting an inferred model via `Tracer` — the patterns this skill uses to
  pull apart a failed fit.
