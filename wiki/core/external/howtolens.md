---
title: HowToLens — tutorial map
type: external_index
audience: student
source: https://github.com/PyAutoLabs/HowToLens
---

# HowToLens

HowToLens teaches strong lensing **from first principles**, assuming minimal prior
astronomy or statistics knowledge. Four chapters of ~30 tutorials plus an optional
chapter, delivered as parallel Jupyter notebooks and Python scripts. Primary
audience: students.

**When to cite HowToLens:** the user is new to gravitational lensing, or new to
Bayesian non-linear inference, or wants the physics derivation behind a concept the
skill is using. Lead with the notebook URL (more interactive); offer the script URL
if the user prefers reading.

**URL templates:**

- Notebook: `https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/<chapter>/<tutorial>.ipynb`
- Script: `https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/<chapter>/<tutorial>.py`

## Chapter 1 — Introduction to strong gravitational lensing and PyAutoLens

Introduces foundational concepts: grids, light and mass profiles, galaxies,
ray-tracing, and simulated imaging data. Assumes minimal prior knowledge and builds
understanding of how PyAutoLens represents and manipulates lens systems.

### tutorial_0_visualization — Visualization setup and display configuration

Sets up PyAutoLens's visualization library to display images in Jupyter notebooks
and on screen. Demonstrates loading and plotting strong-lens datasets and creating
multi-panel subplots.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_0_visualization.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_0_visualization.py

### tutorial_1_grids_and_galaxies — Grids, light profiles, and galaxy objects

Introduces the core PyAutoLens API: 2D `(y,x)` grids, light profiles describing
galaxy brightness distributions, and `Galaxy` objects combining profiles.
Establishes the conceptual foundation for understanding lensing as light deflection
through foreground mass.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_1_grids_and_galaxies.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_1_grids_and_galaxies.py

### tutorial_2_ray_tracing — Ray tracing and deflection angles

Explains how ray tracing calculates the deflection of light rays through a
foreground galaxy's mass. Demonstrates tracing light paths backward from Earth
through the lens mass to determine the source's distorted appearance.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_2_ray_tracing.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_2_ray_tracing.py

### tutorial_3_more_ray_tracing — Critical curves, caustics, cosmological coordinates

Reinforces ray-tracing concepts and introduces critical curves (where
magnification diverges) and their source-plane counterparts (caustics). Shows how
redshift + cosmology converts arcseconds to kiloparsecs.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_3_more_ray_tracing.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_3_more_ray_tracing.py

### tutorial_4_point_sources — Point source lensing (incomplete)

Intended to cover point source lensing (quasars). Not yet written; not necessary
for core PyAutoLens usage.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_4_point_sources.ipynb

### tutorial_5_lensing_formalism — Formal lensing equations (incomplete)

Intended to provide the algebraic formalism of lensing quantities. Not yet
written; tutorial 8 (Summary) is recommended instead.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_5_lensing_formalism.ipynb

### tutorial_6_data — Real telescope imaging and instrumental effects

Introduces realistic CCD imaging from instruments like HST. Covers instrumental
effects — telescope optics, exposure time, detector noise — that affect observed
lens images.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_6_data.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_6_data.py

### tutorial_7_fitting — Fitting lens models to observational data

Transitions from forward-modeling (simulating lenses) to the inverse problem:
inferring lens and source from observed images. Demonstrates basic lens-model
fitting in PyAutoLens.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_7_fitting.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_7_fitting.py

### tutorial_8_summary — Chapter 1 summary and next steps

Reviews chapter 1 concepts: coordinate grids, light/mass profiles, galaxies,
planes, tracers. Sets up chapter 2's Bayesian model-fitting.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_8_summary.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_1_introduction/tutorial_8_summary.py

## Chapter 2 — Lens modeling with Bayesian inference and non-linear searches

Teaches Bayesian inference, non-linear search algorithms, and practical lens
modeling. Covers parameter spaces, likelihood functions, priors, local-maxima
avoidance, and complexity vs. data balance.

### tutorial_1_non_linear_search — Non-linear searches and parameter inference

Introduces how non-linear searches find the best-fit lens model by exploring
parameter spaces, evaluating likelihoods, and using priors. Fundamental
statistical concepts for model fitting.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_1_non_linear_search.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_1_non_linear_search.py

### tutorial_2_practicalities — Output management and result interpretation

Covers the practical side of running fits: output structure, reviewing results,
interpreting fit quality, and managing run times.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_2_practicalities.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_2_practicalities.py

### tutorial_3_realism_and_complexity — Realism vs. parametric complexity

Adds physically realistic features (elliptical mass profiles, lens galaxy light)
while managing parameter count. Balances complexity against data constraints and
computation.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_3_realism_and_complexity.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_3_realism_and_complexity.py

### tutorial_4_dealing_with_failure — Recovering from local maxima

Addresses non-linear searches finding suboptimal local maxima. Introduces three
approaches: prior tuning, multi-start, and model simplification.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_4_dealing_with_failure.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_4_dealing_with_failure.py

### tutorial_5_linear_profiles — Linear expansion profiles

Introduces linear profiles solvable analytically during the search, reducing
parameter-space dimensionality while preserving flexibility for complex light
distributions.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_5_linear_profiles.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_5_linear_profiles.py

### tutorial_6_masking_and_positions — Data masking and position constraints

Masking (excluding unreliable regions) and using image positions (multiple
Einstein-ring images) to tighten constraints and accelerate fits.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_6_masking_and_positions.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_6_masking_and_positions.py

### tutorial_7_results — Accessing fit results and samples

Examines the `Result` object: maximum-likelihood fit, tracer, lens model,
posterior samples. How to extract parameter values and uncertainties.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_7_results.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_7_results.py

### tutorial_8_need_for_speed — Computational efficiency

Strategies for keeping fits tractable on complex models and high-res data.
Optimization without sacrificing accuracy.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_2_lens_modeling/tutorial_8_need_for_speed.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_2_lens_modeling/tutorial_8_need_for_speed.py

## Chapter 3 — Search chaining and automated lens modeling pipelines

Introduces non-linear search chaining: multiple sequential searches fit
progressively more complex models, passing results as informed priors. Dramatically
improves efficiency and reduces failure rates.

### tutorial_1_search_chaining — Breaking modeling into sequential searches

Chains multiple searches: simpler models first, then their results constrain more
complex models. Reduces parameter-space dimensionality and improves convergence.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_1_search_chaining.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_3_search_chaining/tutorial_1_search_chaining.py

### tutorial_2_prior_passing — Automated prior passing between searches

Automatically passes results from one search to the next, tuning priors based on
prior results. Automates the workflow previously done manually.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_2_prior_passing.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_3_search_chaining/tutorial_2_prior_passing.py

### tutorial_3_lens_and_source — Three-stage pipeline (light → mass → source)

Practical three-stage chain: fit lens light first (subtract), then lens mass, then
source. Exploits physical structure to maximize efficiency.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_3_lens_and_source.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_3_search_chaining/tutorial_3_lens_and_source.py

### tutorial_4_x2_lens_galaxies — Multiple lens galaxies

Modelling lenses with two lens galaxies. Uses chaining to handle the
high-dimensional parameter space and degeneracies arising from multiple lens
masses.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_4_x2_lens_galaxies.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_3_search_chaining/tutorial_4_x2_lens_galaxies.py

### tutorial_5_complex_source — Multi-component source modelling

Sources with multiple components (bulges, disks, knots) or multiple source
galaxies built up progressively via chained searches.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_5_complex_source.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_3_search_chaining/tutorial_5_complex_source.py

### tutorial_6_slam — Standard Lens Analysis Method (SLaM)

Introduces SLaM: a standardised pipeline template encoding best-practice search
chains. Ready-made workflows for common scenarios; the user applies proven
pipelines without writing chaining code from scratch.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_3_search_chaining/tutorial_6_slam.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_3_search_chaining/tutorial_6_slam.py

## Chapter 4 — Pixelized source reconstructions and adaptive inversions

Pixelization-based source reconstruction (inversions): sources reconstructed on
flexible pixel grids instead of analytic light profiles. Covers mappers,
regularization, adaptive techniques, and Bayesian model comparison.

### tutorial_1_pixelizations — Source-plane pixel grids

Introduces pixelizations: a grid of source-plane pixels reconstructing source
light. Contrasts the flexible approach with parametric profiles.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_1_pixelizations.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_1_pixelizations.py

### tutorial_2_mappers — Mapping between source and image pixels

`Mapper` objects describe the source-to-image pixel relationship encoded by
lensing. Essential for understanding the forward problem inversions solve.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_2_mappers.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_2_mappers.py

### tutorial_3_inversions — Reconstructing source light via least-squares

Inverts the mapper to reconstruct source light on the pixelization, solving a
least-squares problem. Shows how inversions achieve excellent fits with flexible
non-parametric reconstructions.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_3_inversions.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_3_inversions.py

### tutorial_4_bayesian_regularization — Regularization within a Bayesian framework

Regularization prevents overfitting by penalising unphysically clumpy
reconstructions. Treated as a Bayesian prior on source smoothness with a
hyperparameter trading fidelity against regularization.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_4_bayesian_regularization.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_4_bayesian_regularization.py

### tutorial_5_borders — Border handling and grid sizing

Pixelization-grid sizing and borders that prevent highly demagnified image pixels
(far from the lens) from unduly constraining the inversion.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_5_borders.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_5_borders.py

### tutorial_6_lens_modeling — Lens modeling using inversions

Combines inversions with non-linear lens-model fitting. Overcomes the
parameter-count limitations of parametric source profiles.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_6_lens_modeling.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_6_lens_modeling.py

### tutorial_7_adaptive_pixelization — Delaunay triangulation, adaptive grids

Adaptive pixelizations using Delaunay triangulation in place of uniform grids.
Concentrates pixels in data-rich regions, improving reconstruction and reducing
overfitting.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_7_adaptive_pixelization.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_7_adaptive_pixelization.py

### tutorial_8_model_fit — Practical pixelization-based pipeline

A worked example pipeline using pixelizations. Points at the workspace for
complete production-style workflows.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_8_model_fit.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_8_model_fit.py

### tutorial_9_fit_problems — Inversion failure modes

Analyzes overfitting and underfitting in pixelized fits. Motivates the adaptive
techniques in tutorials 10–11.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_9_fit_problems.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_9_fit_problems.py

### tutorial_10_brightness_adaption — Brightness-adapted pixelization

Concentrate pixels in the bright regions of the reconstructed source, improving
quality regardless of source position. Iterative refinement handles the
chicken-and-egg of adapting before reconstruction is finished.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_10_brightness_adaption.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_10_brightness_adaption.py

### tutorial_11_adaptive_regularization — Spatially varying regularization

Stronger smoothing in faint regions, weaker in bright. Improves reconstructions
by matching regularization to local source properties.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_4_pixelizations/tutorial_11_adaptive_regularization.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_4_pixelizations/tutorial_11_adaptive_regularization.py

## Optional chapter — Advanced topics and alternative searches

### tutorial_searches — Alternative non-linear search algorithms

Non-linear search algorithms beyond the default Nautilus sampler: MCMC,
optimizers. Tuning to balance convergence speed and robustness.

- Notebook: https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_optional/tutorial_searches.ipynb
- Script: https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/chapter_optional/tutorial_searches.py
