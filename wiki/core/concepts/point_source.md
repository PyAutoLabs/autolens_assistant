---
title: Point-source lensing — positions, fluxes, time delays
sources:
  - project: PyAutoLens
    paths:
      - autolens/point/dataset.py
      - autolens/point/model/analysis.py
    pinned_commit: main
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/point_sources.py
    pinned_commit: main
last_updated: 2026-07-09
---

# Point-source lensing

This page introduces the point-source regime in PyAutoLens: when the lensed source is effectively
a point (a quasar nucleus, an unresolved supernova, a faint compact
source whose extended structure is below the imaging resolution), the
observables are the **image positions** in the lens plane, optionally
augmented with **flux ratios** and **time delays** between images.

## What's different from extended-source lensing

Likelihood is built in the source plane: do all observed image positions
map back to a single source-plane point under the candidate mass model?
There's no PSF convolution, no pixelised inversion, no positions-penalty
trick — the positions *are* the data.

## The `PointDataset` and `AnalysisPoint` API

`al.PointDataset` is the data container. It stores the observed
image-plane positions plus their uncertainties and can optionally carry
fluxes, flux uncertainties, time delays, and time-delay uncertainties.
The dataset `name` is load-bearing: PyAutoLens pairs that name to the
corresponding point-source profile in the model, so a dataset named
`source_1` is fitted to the `source_1` point profile and not to some
other compact source by accident. Source:
`PyAutoLens:autolens/point/dataset.py`.

`al.AnalysisPoint(dataset=..., solver=...)` wraps the dataset in a
PyAutoFit likelihood object. Internally, the fit is delegated to
`FitPointDataset`, which can combine three pieces of evidence:

- image-position consistency
- flux consistency via the model magnifications
- time-delay consistency via the model Fermat potential

The resulting `figure_of_merit` is the summed log likelihood of the
components present in the dataset and supported by the chosen point
profile. Sources:
`PyAutoLens:autolens/point/model/analysis.py` and
`PyAutoLens:autolens/point/fit/dataset.py`.

## Where the positions come from — deblending

The `PointDataset` positions must first be *measured* from imaging.
Reading off the brightest 2 or 4 pixels (ds9, a GUI) is often good
enough, but it gives no sub-pixel precision, ignores the PSF, and blends
the point-source fluxes with the lens galaxy's light.

The **deblending** workflow fixes this by fitting the `Imaging` data
directly, modeling each multiple image as an independent PSF-convolved
light profile **in the image plane** — deliberately *without* a
source-plane point source or ray tracing. The reason is microlensing:
stars in the lens galaxy boost or suppress each image's magnification in
a way no smooth mass model can capture, so tying the image fluxes
together through a source-plane model would bias them. Leaving each
image's `intensity` free absorbs the microlensing, which is also why
fluxes are usually down-weighted or omitted in point-source fits.

The fit simultaneously models the lens galaxy's light, so its output is
sub-pixel image positions, PSF-deblended fluxes *and* lens light
properties — ready to feed into a `PointDataset`. Workspace example:
`autolens_workspace:scripts/point_source/features/deblending/modeling.py`.

## Solving the lens equation for image positions

Unlike extended-source fitting, point-source fitting must explicitly
solve the lens equation to find every image produced by a trial source
position. PyAutoLens does this with a `PointSolver`, which searches the
image plane for coordinates that ray-trace back to the source-plane
point. The current API documentation describes this as tracing triangles
between the image and source planes, rather than relying on a single
local Newton step that could miss extra images. Sources:
`PyAutoLens:autolens/point/model/analysis.py` and
`PyAutoLens:autolens/point/solver/`.

This matters because multiplicity is part of the physics:

- a simple galaxy-scale lens often produces a double or quad
- cluster and group configurations can produce many images
- demagnified central images may exist in principle but be too faint to detect

Once image positions are identified, flux ratios come from the local
magnification matrix evaluated at each image. That makes fluxes a much
more model-sensitive observable than positions: small perturbations in
the potential can change magnifications a lot while leaving image
centroids nearly fixed.

## Flux ratios as a substructure probe

Smooth lens models predict a set of image magnifications, and therefore
flux ratios, once the source flux is fixed. Real systems often disagree
with those smooth predictions. These "flux-ratio anomalies" are a classic
probe of small-scale structure because low-mass perturbers can strongly
change magnification near critical curves without moving the image
positions very much.

In practice, flux ratios are less clean than positions: microlensing by
stars, extinction, variability plus time delays, and finite source size
can all mimic or dilute the signal. PyAutoLens therefore treats fluxes as
an optional extra likelihood term, best used when the observing setup and
astrophysical systematics are understood. For the dark-matter use case,
cross-reference [`substructure_and_subhalos`](./substructure_and_subhalos.md).

## Time delays

For a variable point source, the arrival-time difference between two
images is

`Delta t_ij = (D_dt / c) [phi(theta_i, beta) - phi(theta_j, beta)]`

where `phi` is the Fermat potential and `D_dt` is the time-delay
distance. The mass model controls the Fermat-potential difference; the
cosmology controls `D_dt`. That is why a point-source lens with measured
delays becomes a cosmography experiment rather than only a mass-model fit.

PyAutoLens includes time delays directly in `PointDataset`, so the same
analysis object can fit positions-only data, positions plus fluxes, or
positions plus delays. The cosmology side is described in
[`time_delay_cosmography`](./time_delay_cosmography.md).

## Related pages

- [`api/datasets.md`](../api/datasets.md) — `PointDataset` row.
- [`api/analysis_objects.md`](../api/analysis_objects.md) — `AnalysisPoint` row.
- [`concepts/time_delay_cosmography.md`](./time_delay_cosmography.md).
- [`concepts/substructure_and_subhalos.md`](./substructure_and_subhalos.md).
