---
title: PyAutoLens RTD — page map
type: external_index
audience: all
source: https://pyautolens.readthedocs.io/en/latest/
---

# PyAutoLens RTD

The Read-The-Docs site is the canonical PyAutoLens documentation: an overview
series for newcomers, general docs covering features and configuration,
installation guides, and the API reference. Audience varies by section.

**When to cite RTD:**

- The user wants the canonical "what is this feature and when do I use it?" page.
- The user is PyAutoLens-fluent and needs the API surface.
- The user has finished HowToLens chapters 1–2 and is ready for the feature tour.

**URL template:** `https://pyautolens.readthedocs.io/en/latest/<path>.html`

## Overview series

### overview_1_start_here — Start here

Introductory page demonstrating core PyAutoLens concepts via practical examples:
grids, light/mass profiles, ray-tracing with the `Tracer` object. Showcases
JAX-accelerated computation with optional GPU support. Best for newcomers
evaluating the framework.

- URL: https://pyautolens.readthedocs.io/en/latest/overview/overview_1_start_here.html
- Audience: newcomer

### overview_2_new_user_guide — New user guide

Structured decision-tree guide routing the user by lens scale (galaxy / group /
cluster) and data type (CCD imaging / interferometry / point sources). Offers
GitHub-notebook and Google-Colab entry points alongside HowToLens.

- URL: https://pyautolens.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html
- Audience: general — recommended first page after install

### overview_3_features — Features overview

Tour of nine advanced capabilities: pixelizations, point sources, interferometry,
multi-Gaussian expansion, group lensing, multi-wavelength, ellipse fitting,
shapelets, operated light profiles, sky background modeling. Links into deeper
docs and workspace examples.

- URL: https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html
- Audience: experienced — picking features for a specific science case

## General docs

### Configs — Configuration files

How PyAutoLens uses config files to customize searches, visualization, system
behavior. Covers default locations (workspace `config/`), PyAutoConf overrides,
output paths.

- URL: https://pyautolens.readthedocs.io/en/latest/general/configs.html
- Audience: general

### Model cookbook — Model composition

Systematic reference for building lens models with `Model` and `Collection`
objects. Two-component up through multi-galaxy systems, prior customization,
parameter pairing, multi-Gaussian expansions, shapelets, chaining.

- URL: https://pyautolens.readthedocs.io/en/latest/general/model_cookbook.html
- Audience: general

### Likelihood function — Fitting methodology

Documents how PyAutoLens computes likelihoods. Points at workspace notebooks that
demystify the analysis step by step. Citations for academic context.

- URL: https://pyautolens.readthedocs.io/en/latest/general/likelihood_function.html
- Audience: advanced

### Demagnified solutions — Unphysical-solution handling

Explains how demagnified source reconstructions produce unphysical lens models
in pixelized fitting. Describes the `PositionsLH` class and position-thresholding
penalty.

- URL: https://pyautolens.readthedocs.io/en/latest/general/demagnified_solutions.html
- Audience: advanced

### Citations — How to cite PyAutoLens

BibTeX entries and attribution requirements. Core references (Nightingale et al.
MNRAS), JOSS, specialized dependencies, domain-specific references for mass
models and structure.

- URL: https://pyautolens.readthedocs.io/en/latest/general/citations.html
- Audience: general

### Papers — Research using PyAutoLens

Catalog of papers using PyAutoLens, organised by domain (dark matter, cosmology,
galaxy formation, lens modeling theory, ML, surveys). Useful for the user
searching for prior art.

- URL: https://pyautolens.readthedocs.io/en/latest/general/papers.html
- Audience: advanced

## Installation

### Overview

High-level installation introduction. Python 3.12–3.13. ~50× GPU acceleration
via JAX. Four foundational deps (PyAutoConf, PyAutoFit, PyAutoArray,
PyAutoGalaxy).

- URL: https://pyautolens.readthedocs.io/en/latest/installation/overview.html
- Audience: newcomer

### Conda

Step-by-step conda environment setup. Python 3.12, pip-into-conda install,
workspace clone, optional Numba/pynufft.

- URL: https://pyautolens.readthedocs.io/en/latest/installation/conda.html
- Audience: newcomer

### Pip

Pip-based install with venv, JAX/GPU configuration, workspace setup, legacy
Python pinning, troubleshooting.

- URL: https://pyautolens.readthedocs.io/en/latest/installation/pip.html
- Audience: newcomer

### From source

Cloning the GitHub repo and installing deps for development. Builds the whole
PyAutoLabs ecosystem; PYTHONPATH/conda configuration and unit-test validation.

- URL: https://pyautolens.readthedocs.io/en/latest/installation/source.html
- Audience: advanced

### Troubleshooting

Common install problems: pip/conda conflicts, working-directory requirements
(must run from `autolens_workspace`), matplotlib backend alternatives.

- URL: https://pyautolens.readthedocs.io/en/latest/installation/troubleshooting.html
- Audience: newcomer

## Tutorials

### HowToLens lectures index

Top-level entry point to the four-chapter HowToLens series. Each chapter takes
~3–6 hours; assumes minimal prior astronomy / statistics knowledge.

- URL: https://pyautolens.readthedocs.io/en/latest/howtolens/howtolens.html
- Audience: newcomer
- See also: [`howtolens.md`](./howtolens.md) — per-tutorial map

## API reference

The full API is browsable at https://pyautolens.readthedocs.io/en/latest/ under
the API Reference section, with module and class indices. Don't enumerate
classes here — deep API lookups are better done via `sources.yaml` paths
(project-name + repo-relative path) so the user can read the source itself.

Functional sections (for navigation):

- **Data structures** — `Mask2D`, `Array2D`, `Grid2D`, `Grid2DIrregular`, imaging
  / interferometer data, convolution, DFT/NUFFT.
- **Light profiles** — `Gaussian`, `Sersic`, `Exponential`, `DevVaucouleurs`,
  linear variants, PSF-operated profiles, basis decompositions.
- **Mass profiles** — power-law, isothermal, PIE, NFW / gNFW / cNFW, shear,
  potential, light-and-mass hybrids.
- **Galaxy & tracer** — `Galaxy`, `Tracer`, `Redshift`.
- **Fitting** — `FitImaging`, `FitInterferometer`, result classes.
- **Lens modeling** — `AnalysisImaging`, `AnalysisInterferometer`, searches
  (Nautilus, LBFGS, BFGS, Dynesty, Emcee), priors.
- **Pixelizations** — `Pixelization`, meshes, regularization, `Mapper`,
  settings.
- **Point sources** — `PointDataset`, `PointSolver`, `AnalysisPoint`.
- **Plotting** — array / grid / tracer / fit / interferometer plotters, corner
  plots.

## Features (per-page, where directly linkable)

Individual feature pages under `overview/features/` may 404 on some links;
the canonical entry is `overview_3_features.html` above. When a feature has a
dedicated docs page accessible from there, prefer that URL; otherwise cite the
workspace example (see [`workspace.md`](./workspace.md)) instead.
