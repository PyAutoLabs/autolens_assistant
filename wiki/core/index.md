---
title: Core wiki — PyAuto* reference
sources: []
last_updated: 2026-05-22
---

# Core wiki — PyAuto\* reference

The reference layer for everything an agent needs to know about the PyAuto\* stack
when helping a user write lensing code. Skills in [`../../skills/`](../../skills/) link in
here for the *what* / *which* / *why*.

## Stack

- [The stack at a glance](./stack/overview.md) — dependency chain, who imports whom.
- [PyAutoConf](./stack/autoconf.md) — YAML config loader.
- [PyAutoArray](./stack/autoarray.md) — arrays, grids, masks, geometry.
- [PyAutoFit](./stack/autofit.md) — model composition, non-linear search, samples.
- [PyAutoGalaxy](./stack/autogalaxy.md) — light + mass profiles, galaxies.
- [PyAutoLens](./stack/autolens.md) — tracer, ray tracing, lensing umbrella.

## Concepts

Physics + framework material the skills lean on.

- [Lensing basics](./concepts/lensing_basics.md) — deflection, convergence,
  magnification, caustics.
- [Tracer](./concepts/tracer.md) — multi-plane ray tracing.
- [Light profiles](./concepts/light_profiles.md) — Sersic family, MGE, Shapelets,
  linear vs. operated.
- [Mass profiles](./concepts/mass_profiles.md) — Isothermal, PowerLaw, NFW, external
  shear, multipole.
- [Galaxy and plane](./concepts/galaxy_and_plane.md) — how galaxies, redshifts, and
  the tracer compose.
- [Grids and masks](./concepts/grids_and_masks.md) — slim/native, over-sampling,
  sub-grids.
- [Extra galaxies and noise scaling](./concepts/extra_galaxies_and_noise_scaling.md) —
  masking out contaminating galaxies via `apply_noise_scaling`, vs modelling or shrinking the mask.
- [Inversions and pixelisations](./concepts/inversions_and_pixelizations.md) —
  pixelised source reconstruction, regularisation, mesh choices.
- [Non-linear search](./concepts/non_linear_search.md) — what each sampler does and
  when to use which.
- [Samples and posteriors](./concepts/samples_and_posteriors.md) — Samples API,
  errors, derived quantities.
- [SLaM pipeline](./concepts/slam_pipeline.md) — Source-Light-Mass pipeline anatomy.
- [Cosmology and units](./concepts/cosmology_and_units.md) — angular ↔ physical
  conversions.
- [Point-source lensing](./concepts/point_source.md) — positions, flux
  ratios, image-position solvers.
- [Time-delay cosmography](./concepts/time_delay_cosmography.md) — H0
  from time-delay lenses, Fermat potential, mass-sheet degeneracy.
- [Substructure and subhaloes](./concepts/substructure_and_subhalos.md)
  — Bayesian detection of dark-matter substructure.
- [Sensitivity mapping](./concepts/sensitivity_mapping.md) — calibrating
  non-detections via injection-recovery.
- [Group- and cluster-scale lensing](./concepts/group_and_cluster_lensing.md)
  — extra galaxies, scaling relations, cluster-scale composition.
- [Multi-wavelength / multi-dataset](./concepts/multi_wavelength.md) —
  joint fits across bands and instruments.
- [Weak lensing](./concepts/weak_lensing.md) — `WeakDataset` shear
  catalogue fits.
- [Hierarchical / graphical models](./concepts/hierarchical_models.md)
  — population-level inference, expectation propagation.
- [Interferometer theory](./concepts/interferometer_theory.md) —
  visibilities, uv-plane, FFT/NUFFT.

## API

Task-oriented catalogues — comprehensive lists of what's available, with one-line
"when to use" notes.

- [Non-linear searches](./api/searches.md) — Nautilus, Dynesty (static/dynamic),
  Emcee, Zeus, BFGS/LBFGS, Drawer.
- [Light profile catalogue](./api/light_profile_catalog.md).
- [Mass profile catalogue](./api/mass_profile_catalog.md).
- [Datasets](./api/datasets.md) — Imaging, Interferometer, PointDataset.
- [Plotting](./api/plotting.md) — `aplt` entry points, subplot helpers, direct plotting functions.
- [Configuration](./api/configuration.md) — `<pkg>/config/*.yaml` semantics.
- [Analysis objects](./api/analysis_objects.md) — `AnalysisImaging`,
  `AnalysisInterferometer`, `AnalysisPoint`.
- [Aggregator and result database](./api/aggregator.md) — bulk loading
  of completed fits, derived quantities, optional SQLite backend.
- [CSV API](./api/csv_api.md) — cluster-scale spreadsheet model
  composition.
- [Datacube modelling](./api/datacube.md) — spectral interferometric
  strong lensing.

## Operations

- [Installation](./operations/installation.md) — pip vs. editable clone, version
  pins.
- [Sandbox / restricted environments](./operations/sandbox.md) — `NUMBA_CACHE_DIR`,
  `MPLCONFIGDIR`, `PYAUTO_TEST_MODE` and friends.
- [HPC](./operations/hpc.md) — running fits on a cluster.
