---
name: euclid_model_lens
description: Model a Euclid strong lens through the pipeline's staged scripts — the initial MGE + SIE fit (start_here.py), Sersic lens/source photometry for SED fitting (sersic_lens_model.py), lens-only MGE subtraction (mge_lens_only.py), multi-waveband NIR/EXT fits with the VIS model fixed (lens_model_waveband.py), and the full SLaM pixelized-source + PowerLaw model (full_model.py). Use to choose and run the right Euclid pipeline stage for a science goal; NOT for setting up the repo (euclid_setup_pipeline) or hand-composed non-Euclid models (al_build_imaging_model / al_run_slam_pipeline).
---

# Modeling a Euclid lens: the staged pipelines

The pipeline models every Euclid lens through the same staged progression. Each stage
answers a different science need, and each is seeded by the previous stage's result so
convergence stays robust — the same chained-search logic as PyAutoLens's SLaM pipelines
([`wiki/core/concepts/slam_pipeline.md`](../wiki/core/concepts/slam_pipeline.md)),
specialised to Euclid data. All stages run with one CLI:

```bash
python <script> --sample=<sample> --dataset=<dataset_name> --iterations_per_quick_update=50000
```

and every script is also importable (each exposes `fit(...)` functions), so batch
drivers and HPC submissions reuse the same code paths.

The papers behind these choices — why MGE + SIE is the standard Q1/DR1 fit, what the
discovery samples look like — are in
[`wiki/euclid/sources/euclid-strong-lensing.md`](../wiki/euclid/sources/euclid-strong-lensing.md).

## Ask

- *"What do you need from this lens?"* — a first model / photometry for SED fitting /
  a clean arc image / colour information / a publication mass model. The answer picks
  the stage below.
- *"Has the initial fit already run?"* — every later stage fixes parameters to the
  `initial_lens_model` result; run [`euclid_setup_pipeline`](./euclid_setup_pipeline.md)
  first if `output/<sample>/<dataset>/initial_lens_model/` doesn't exist.
- *"One lens interactively, or a sample?"* — for samples, plan the run through
  [`euclid_hpc_runs`](./euclid_hpc_runs.md) and inspect with
  [`euclid_workflow_products`](./euclid_workflow_products.md).

## Branch — initial lens model (`start_here.py`)

The standard first fit: MGE lens light (2×20 Gaussians) + Isothermal + shear + MGE
source, ~15 non-linear parameters, Nautilus. The MGE's linear light profiles keep the
non-linear space small and well-conditioned, which is what makes ~10 min/lens on a GPU
possible. Mass centre is anchored to the brightest central pixel; the MGE intensities
are solved by linear inversion at every likelihood call. Outputs include the deblended
lens/source images and the Euclid latent variables (aperture fluxes → AB magnitudes via
the header MAGZERO, magnification) from
`euclid_strong_lens_modeling_pipeline:util.py` (`LatentEuclid`).
`scripts/initial_lens_model.py` is the same fit as an importable module.

## Branch — Sersic photometry (`scripts/sersic_lens_model.py`)

When the goal is **photometry for SED fitting** (and photometric redshifts), Sersic
profiles beat an MGE: total flux is a model parameter rather than a sum of Gaussians.
`fit_sersic()` fits a linear Sersic bulge to lens and source in VIS with the **mass
model fixed** to the initial result; `fit_waveband()` then carries the Sersic model
across every non-VIS band. The Sersic centre diverges, so the script derives a
higher-order over-sampling scheme from the prior fit's tracer. Multi-band Sersic
fluxes → SEDs → photo-zs is the standard chain
([`wiki/euclid/concepts/euclid-photo-z.md`](../wiki/euclid/concepts/euclid-photo-z.md)).

## Branch — lens-only subtraction (`scripts/mge_lens_only.py`)

Fits an MGE to the **lens light only** — no mass, no source. The residual image is the
cleanest quick view of the lensed arcs, for visual inspection, discovery vetting, or as
input to downstream tools. `fit()` runs VIS; `fit_waveband()` repeats per band with the
VIS lens model fixed, giving lens-subtracted images in every band.

## Branch — multi-waveband model (`scripts/lens_model_waveband.py`)

Carries the full VIS lens model (light + mass + source) onto every non-VIS band, fixed,
with only a per-band sub-pixel astrometric offset (`DatasetModel`) free to absorb
residual band-to-band alignment errors. This is how colour information for the lens and
source is extracted without re-fitting the whole model at lower resolution — the NIR
bands trade resolution for colour ([`wiki/euclid/entities/nisp.md`](../wiki/euclid/entities/nisp.md),
[`wiki/euclid/entities/ext-surveys.md`](../wiki/euclid/entities/ext-surveys.md)).
Called internally by the Sersic and lens-only pipelines' `fit_waveband()` stages.

## Branch — full SLaM model (`scripts/full_model.py`)

The publication-quality model, chaining five searches on VIS:

1. **SOURCE LP** — parametric MGE source + isothermal mass (fast initialisation).
2. **SOURCE PIX 1** — pixelized source on a rectangular adaptive mesh, creating the
   adapt image (`mesh_pixels_yx` is fixed — JAX needs statically shaped arrays).
3. **SOURCE PIX 2** — refined pixelization with adapt-image regularisation.
4. **LIGHT LP** — lens-light refinement with source/mass held.
5. **MASS TOTAL** — final PowerLaw mass model.

Image positions are computed automatically from the SOURCE LP result to penalise
unphysical demagnified reconstructions. Expect hours, not minutes — plan sample-scale
runs on HPC. The generic SLaM concepts are in
[`al_run_slam_pipeline`](./al_run_slam_pipeline.md); the Euclid script is the tuned,
ready-to-run instance.

## Choosing a stage

| Science goal | Stage |
|---|---|
| First model / mass + Einstein radius estimate | `start_here.py` |
| Fluxes and magnitudes for SED fitting / photo-z | `sersic_lens_model.py` |
| Clean image of the arcs | `mge_lens_only.py` |
| Lens + source colours across bands | `lens_model_waveband.py` (or the `fit_waveband` stages) |
| Publication mass model, pixelized source | `full_model.py` |

## Combine

- [`euclid_workflow_products`](./euclid_workflow_products.md) — turn many fits into
  .csv catalogues, .fits stacks and one-line .png summaries.
- [`al_load_results`](./al_load_results.md) / [`al_plot_fit_residuals`](./al_plot_fit_residuals.md)
  — inspect an individual fit in depth; the pipeline's outputs are standard PyAutoLens
  results.
- [`al_debug_fit_failure`](./al_debug_fit_failure.md) — post-mortem for a stage that
  converged badly; check the initial fit before blaming a later stage.
- If key output for your science case is missing from the pipeline, that is by design a
  collaboration conversation — the pipeline grows by request so outputs stay standard
  across the data release (contact James Nightingale on the Euclid Consortium Slack).

## Further reading

- **General reference** — [euclid_strong_lens_modeling_pipeline README](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline#readme):
  the pipeline inventory and run commands.
- **Experienced PyAutoLens user** — [workspace/lens: guides/modeling/slam_start_here.py](https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/guides/modeling/slam_start_here.py):
  the generic SLaM template `full_model.py` specialises for Euclid.
