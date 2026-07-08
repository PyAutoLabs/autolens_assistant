---
name: al_run_slam_pipeline
description: Run a Source-Light-Mass (SLaM) pipeline — the canonical automated multi-stage lens-modelling workflow. Stages a parametric source fit, a pixelised source fit, a lens-light fit, and a total-mass fit, chaining priors between them. The right starting point for any production-quality lens model, especially with pixelised sources. Prereq: understand `al_chain_searches` and pixelisations.
---

# Running a SLaM pipeline

SLaM (Source, Light, Mass) is the canonical automated lens-modelling pipeline. It
chains four or more searches:

1. **SOURCE LP** — fit a parametric (light-profile) source with a simple lens mass to
   initialise.
2. **SOURCE PIX** — switch the source to a pixelised inversion, refining everything.
3. **LIGHT LP** — fit a complex lens-light model (e.g. MGE) on top, holding mass + source
   close to the SOURCE PIX result.
4. **MASS TOTAL** — fit a more complex mass model (PowerLaw, MGE, multipole) with
   light + source held close.

It is the most reliable route to a publication-quality lens model. The trade-off is
runtime — a SLaM run typically takes 4–24 hours on a modern CPU.

Canonical reference: `autolens_workspace:scripts/guides/modeling/slam_start_here.py`.
Treat this file as the structural template; all other SLaM scripts in the workspace
are documented relative to it ("identical to slam_start_here.py except…").

## Prerequisites

Before running SLaM, the user should be comfortable with:

- **Pixelisations** — [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md).
- **Search chaining** — [`al_chain_searches`](./al_chain_searches.md) and
  [`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md).
- **Adapt images** — adaptive regularisation that uses the lens-light-subtracted image
  to scale source-plane reconstruction smoothness. Covered in the SLaM concept page.
- **Real-data preprocessing** — for observational imaging, they should already have
  made explicit decisions about mask radius, contaminating objects, and any manual
  exclusion regions that should not enter the likelihood.

If they're newer than that, route them through `al_build_imaging_model` +
`al_run_search` first; SLaM is overkill for a first-fit.

For the full conceptual treatment of SLaM,
[`wiki/core/concepts/slam_pipeline.md`](../wiki/core/concepts/slam_pipeline.md).

## Ask

- *"Imaging or interferometer?"* — both supported; the pipelines differ in the analysis
  classes and inversion settings.
- *"If this is real imaging data, have you already settled the preprocessing choices:
  mask extent, contaminant masking, and any regions that should be excluded from the
  model?"* — if not, route back to [`al_prepare_imaging_data`](./al_prepare_imaging_data.md)
  before starting SLaM.
- *"Does the lens galaxy have noticeable lens light to model, or are you doing a
  mass-only fit?"* — controls whether LIGHT LP is included.
- *"What's the final mass model you want?"* — Isothermal+Shear (default), PowerLaw,
  PowerLawMultipole, decomposed Light+Dark, etc. Controls the MASS TOTAL phase.
- *"Have you measured image positions for the lensed source?"* — recommended for
  pixelised-source fits to avoid unphysical demagnification solutions.

## Branch — galaxy-scale imaging SLaM

The SLaM API lives in `autolens_workspace:slam/` (a sibling module in the workspace
that ships SLaM pipeline functions). The workspace doesn't ship its own copy; the recipe
below mirrors `slam_start_here.py` and depends on the workspace pipelines being
available.

```python
# scripts/slam_pipeline.py
from autoconf import jax_wrapper
from pathlib import Path
import autofit as af
import autolens as al
from autolens_workspace.slam import slam_pipeline_main  # workspace dep

dataset_path = Path("dataset/imaging/<your_lens>")
dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,
)
mask = al.Mask2D.circular(
    shape_native=dataset.shape_native, pixel_scales=dataset.pixel_scales, radius=3.0
)
dataset = dataset.apply_mask(mask=mask)

# Optional: image positions to penalise unphysical mass models.
positions = al.from_json(file_path=dataset_path / "positions.json")  # returns a Grid2DIrregular
positions_likelihood = al.PositionsLH(positions=positions, threshold=0.5)

# Driver — the actual SLaM pipeline functions live in autolens_workspace/slam/.
# See slam_start_here.py for the canonical invocation: SOURCE LP → SOURCE PIX →
# LIGHT LP → MASS TOTAL with their chaining of `result_*` objects.
slam_pipeline_main(
    dataset=dataset,
    redshift_lens=0.5,
    redshift_source=1.0,
    path_prefix="imaging/<your_lens>/slam",
    positions_likelihood=positions_likelihood,
    mesh_shape=(35, 35),
    # ... per-stage settings; defer to slam_start_here.py for the full list.
)
```

Source citations:
- `autolens_workspace:scripts/guides/modeling/slam_start_here.py` — canonical invocation.
- `autolens_workspace:slam/` — pipeline function definitions (the actual SLaM code is
  in the workspace, not in PyAutoLens itself).
- `PyAutoLens:autolens/analysis/positions.py` — `PositionsLH`.

## Branch — interferometer SLaM

Analogous pipelines exist at `autolens_workspace:scripts/interferometer/features/*/slam.py`.
Substitute `AnalysisInterferometer` and the visibility-plane SLaM driver.

## Running and monitoring

SLaM writes one output subfolder per phase. Tail the latest phase's search log:

```bash
ls -td output/imaging/<your_lens>/slam/*/ | head -1 | xargs -I{} tail -f {}search.log
```

Smoke test the wiring with `PYAUTO_TEST_MODE=1` before launching the real run —
all 4+ phases will short-circuit, but you'll catch import / config errors fast.

## Combine

- [`al_load_results`](./al_load_results.md) — load each phase's results separately;
  the MASS TOTAL phase usually holds the final answer.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) — the
  SOURCE PIX phase produces the pixelised source you'd want to inspect.
- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — SLaM failures usually point to
  one specific phase; the debug skill walks the post-mortem.

## Further reading

- **Student / new to lensing** — [HowToLens: Standard Lens Analysis Method
  (SLaM)](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_6_slam.ipynb):
  what SLaM is and why it works — best-practice multi-stage chaining encoded as a
  ready-made pipeline.
- **General reference** — [RTD: Features overview](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  SLaM sits alongside pixelization, MGE, subhalo detection and multi-wavelength on
  the feature tour.
- **Experienced PyAutoLens user** — [workspace/lens: guides/modeling/slam_start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/modeling/slam_start_here.py):
  the canonical SLaM invocation script — all other SLaM scripts in the workspace are
  documented relative to it.
