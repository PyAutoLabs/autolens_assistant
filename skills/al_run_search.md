---
name: al_run_search
description: Execute a non-linear search on a configured model + analysis. Calls `search.fit(model=model, analysis=analysis)` and monitors progress to the search's `path_prefix/name/unique_id/` output folder. Includes the sandbox / test-mode wrapper so smoke tests don't burn hours on real sampling. Use after `al_build_imaging_model` (or interferometer) and `al_configure_search` have produced `model`, `analysis`, and `search` objects.
---

# Running a non-linear search

The actual fit. Inputs: a model, an analysis (which knows the dataset and how to
compute a log-likelihood), and a search (which knows how to explore parameter space).
The single call `search.fit(model=model, analysis=analysis)` does the work.

This skill assembles those three pieces into a runnable script, then runs it — either
in `PYAUTO_TEST_MODE=1` for a smoke test or in production mode for the real fit.

## Ask

- *"Have you built `model` and `analysis` (from `al_build_imaging_model`) and
  configured `search` (from `al_configure_search`)?"* If not, route to those first.
- *"Smoke test or production run?"* Smoke test runs in seconds with `PYAUTO_TEST_MODE=1`
  and a tiny dataset, just to prove the wiring is correct. Production run takes hours
  to a day depending on model complexity and number of likelihood evals.
- *"How long can the fit run?"* Sets expectations and decides whether to launch it as
  a foreground or backgrounded process.

## Branch — production run

Operational reminder: if the search was configured with `live_visual_update=True`
(`al_configure_search` "Live visual updates"), a foreground script opens a matplotlib viewer
and a notebook cell refreshes in place — don't re-ask when the search configuration already
records the choice, and keep it `False` for HPC/headless/background runs. `fit.png` is
written to disk on every quick update either way.

Assemble everything into one script (`scripts/run_fit.py`):

```python
# scripts/run_fit.py
from autonerves import jax_wrapper
from pathlib import Path
import autofit as af
import autolens as al

# --- Dataset (from al_prepare_imaging_data) ---
dataset_path = Path("dataset/imaging/<your_lens>")
dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,
)
mask = al.Mask2D.circular(
    shape_native=dataset.shape_native, pixel_scales=dataset.pixel_scales, radius=2.5
)
dataset = dataset.apply_mask(mask=mask)

# --- Model (from al_build_imaging_model) ---
lens = af.Model(
    al.Galaxy,
    redshift=0.5,
    bulge=af.Model(al.lp.Sersic),
    mass=af.Model(al.mp.Isothermal),
    shear=af.Model(al.mp.ExternalShear),
)
source = af.Model(al.Galaxy, redshift=1.0, bulge=af.Model(al.lp.SersicCore))
model = af.Collection(galaxies=af.Collection(lens=lens, source=source))

# --- Analysis ---
analysis = al.AnalysisImaging(dataset=dataset)

# --- Search (from al_configure_search) ---
search = af.Nautilus(
    path_prefix="imaging/<your_lens>",
    name="sie_sersic",
    n_live=200,
    number_of_cores=4,
)

# --- Fit ---
result = search.fit(model=model, analysis=analysis)
print(result.max_log_likelihood_instance)
```

Run with sandbox cache overrides if needed:

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python scripts/run_fit.py
```

Source: `PyAutoFit:autofit/non_linear/search/abstract_search.py` (the `fit` method).
The returned `Result` object is documented in `PyAutoFit:autofit/non_linear/result.py`.

## Branch — smoke test (`PYAUTO_TEST_MODE=1`)

When you've just written the script and want to know it runs end-to-end *without*
waiting for real sampling, set `PYAUTO_TEST_MODE=1`:

```bash
PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/run_fit.py
```

The search will short-circuit after a small number of likelihood evaluations and
return a `Result` so the script completes. Use this on every script you write, before
launching a real run.

For an even faster smoke (sub-second per step), combine with PyAutoLens's small-dataset
flags:

```bash
PYAUTO_TEST_MODE=2 PYAUTO_SKIP_FIT_OUTPUT=1 PYAUTO_SKIP_VISUALIZATION=1 \
  PYAUTO_SMALL_DATASETS=1 PYAUTO_FAST_PLOTS=1 python scripts/run_fit.py
```

See [`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md) for the full flag list.

## Output

The fit writes to `output/<path_prefix>/<name>/<unique_id>/` (see
`al_configure_search` for the layout). Tail the search log live:

```bash
tail -f output/imaging/<your_lens>/sie_sersic/*/search.log
```

## Combine

- [`al_load_results`](./al_load_results.md) — once the fit completes (or even mid-run),
  load and inspect.
- [`al_plot_fit_residuals`](./al_plot_fit_residuals.md) — visualise model vs data.
- [`al_chain_searches`](./al_chain_searches.md) — feed the result into a follow-up
  search with tighter priors.
- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — if the fit converged badly.

## Further reading

- **Student / new to lensing** — [HowToLens: Output management and result
  interpretation](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_2_practicalities.ipynb):
  the practical side of running fits — output structure, reviewing results,
  managing run times.
- **General reference** — [RTD: New user guide](https://pyautolens.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html):
  decision-tree routing for a new user about which fit to run first.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/imaging/start_here.py):
  the minimal end-to-end imaging fit on GPU — production pattern this skill mirrors.
