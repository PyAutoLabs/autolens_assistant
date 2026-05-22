---
title: autolens_workspace/lens — script map
type: external_index
audience: experienced
source: https://github.com/Jammy2211/autolens_workspace
---

# autolens_workspace / lens

The `Jammy2211/autolens_workspace` repo is the production-style example library:
~744 scripts and notebooks organised by science case (imaging, group,
interferometer, point-source, cluster, multi-wavelength, weak) and difficulty
(`start_here` → modeling → features → advanced → results → simulators).
Audience: experienced lensing scientists, returning PyAutoLens users.

**When to cite the workspace:**

- The user knows lensing and wants a working example to fork from.
- The user is mid-project and needs a concrete recipe for a feature (pixelization,
  MGE, subhalo search, multi-wavelength fit).
- The skill produces a script that's a direct adaptation of a workspace example.

**URL template:** `https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/<relative-path>`

When the file also exists in this fork's `context/` folder, **cite both** — the
URL for the upstream canonical version, the `context/` path for the local copy.

## Imaging

CCD-data lensing (HST, JWST, Euclid, ground-based). The deepest and most-developed
top-level case.

### imaging/start_here.py

Strong-lens modeling of CCD imaging using minimal setup. Data load, mask, model,
fit, visualize. ~15 minutes on GPU.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/start_here.py

### imaging/data_preparation/start_here.py

Data preparation standards for CCD: pixel-scale, image, noise maps, PSF. The
canonical reference for getting telescope data analysis-ready.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/data_preparation/start_here.py

### imaging/modeling/start_here.py

Lens-modeling API for imaging: model composition, light-profile selection
(Sersic vs. MGE), non-linear-search configuration, JAX/GPU fitting.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/modeling/start_here.py

### imaging/results/start_here.py

Inspect a completed fit: `FitImaging`, residuals, chi-squared maps, sample-
based uncertainties, FITS export.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/results/start_here.py

### imaging/simulators/start_here.py

Simulating CCD imaging from a ground-truth model — instrument-realistic noise,
PSF, exposure. The canonical pattern when no real data are on hand.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/simulators/start_here.py

### imaging/features/pixelization/modeling.py

Pixelised extended-source reconstruction. Rectangular mesh + constant
regularization; fast and accurate when parametric profiles aren't enough.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/pixelization/modeling.py

### imaging/features/extra_galaxies/modeling.py

Handling nearby companion galaxies whose light/mass blend with the lens or
source. Masking strategies and fixed-centre inclusion.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/extra_galaxies/modeling.py

### imaging/features/no_lens_light/modeling.py

When the lens light has been pre-subtracted: fewer free parameters, faster
convergence.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/features/no_lens_light/modeling.py

### imaging/advanced/subhalo/detect/start_here.py

Dark-matter subhalo detection via Bayesian model comparison and a SLaM pipeline.
Grid searches over subhalo position/mass; residual comparison with/without
subhalo.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/advanced/subhalo/detect/start_here.py

## Interferometer

Direct uv-plane fitting (ALMA, JVLA, LOFAR).

### interferometer/start_here.py

Strong-lens modeling of radio/mm interferometer data. NUFFT-based forward model;
scales to millions of visibilities.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/interferometer/start_here.py

### interferometer/data_preparation.py

Data standards for visibilities: pixel scale, noise, uv-baselines, real-space
masking, optional position constraints.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/interferometer/data_preparation.py

### interferometer/features/datacube/start_here.py

Datacube modeling (e.g. ALMA CO emission). Shared lens geometry across channels;
per-channel source reconstruction.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/interferometer/features/datacube/start_here.py

### interferometer/features/subhalo/detect/start_here.py

Subhalo detection in interferometer data via SLaM pipelines and pixelized source
reconstruction.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/interferometer/features/subhalo/detect/start_here.py

## Group

Multi-galaxy lens systems where two or more galaxies contribute to the deflection.

### group/start_here.py

Group-scale modeling: fit 2+ lens galaxies' light and mass against Euclid CCD
data. ~10 minutes on GPU.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/group/start_here.py

### group/data_preparation/start_here.py

Extends galaxy-scale data prep with main-lens, extra-galaxy, scaling-galaxy
centre specifications.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/group/data_preparation/start_here.py

### group/features/pixelization/modeling.py

Pixelized source reconstruction for groups using Delaunay triangulation with
adaptive regularization. Especially valuable for multi-arc sources.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/group/features/pixelization/modeling.py

### group/advanced/subhalo/detect/start_here.py

Subhalo detection in group-scale systems via SLaM + grid-search.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/group/advanced/subhalo/detect/start_here.py

## Point source

### point_source/start_here.py

Lensed point-sources (quasars / lensed SNe) appearing as multiple distinct
images. Image-plane positions, optional fluxes and time delays. Useful for H0
inference and small-scale dark matter.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/point_source/start_here.py

## Cluster

### cluster/start_here.py

Cluster-scale modeling: BCGs + tens-to-hundreds of scaling-relation members +
cluster DM halos (NFW) + multiple background sources at distinct redshifts.
Multi-plane ray-tracing; ~15 minutes on GPU.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/cluster/start_here.py

## Multi-wavelength

### multi/start_here.py

Same lens, multiple wavelengths/telescopes. Shared mass model with per-band
source reconstruction.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/multi/start_here.py

### multi/features/slam/independent.py

Multi-wavelength SLaM: fit highest-resolution dataset first, then fix the mass
model and update lens light + source per additional band via linear algebra.
Ideal for Euclid-like multi-band surveys.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/multi/features/slam/independent.py

## Weak

### weak/fit.py

Weak-lensing shear-catalogue fitting (`gamma_1`, `gamma_2` at background source
positions). No PSF, no masking, no source light — simpler than imaging.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/weak/fit.py

## Guides — cross-cutting topics

### guides/data_structures.py

`Grid2D`, `Array2D`, vector objects; `slim` vs `native` representations.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/data_structures.py

### guides/galaxies.py

Per-galaxy property computation from a fitted model: source-plane image,
per-component light, etc.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/galaxies.py

### guides/lens_calc.py

Lensing-quantity calculations from deflection: convergence, shear, magnification,
critical curves, caustics, Einstein radius, Fermat potential.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/lens_calc.py

### guides/tracer.py

`Tracer` inspection: ray-tracing, light/mass profiles, visualization, results as
numpy arrays.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/tracer.py

### guides/plot/start_here.py

PyAutoLens plotting API: `aplt.plot_array()`, `aplt.subplot_tracer()`, etc.
Config-driven customisation.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/plot/start_here.py

### guides/results/start_here.py

Loading fit results from disk: JSON for tracer/model/samples, FITS for images,
aggregator pattern for hundreds of fits.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/results/start_here.py

### guides/modeling/slam_start_here.py

SLaM-pipeline overview: source-light → pixelized-source → lens-light → mass.
Each stage feeds the next.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/modeling/slam_start_here.py

### guides/profiles/light.py

Catalog of light profiles in `al.lp`: Sersic, MGE, linear, operated, basis.
Construction, evaluation, model composition.

- URL: https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/profiles/light.py
