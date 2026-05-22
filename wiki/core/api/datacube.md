---
title: Datacube modelling — spectral interferometric strong lensing
sources:
  - project: PyAutoLens
    paths:
      - autolens/interferometer
    pinned_commit: main
last_updated: 2026-05-22
---

# Datacube modelling

A datacube is a stack of
2D visibility planes indexed by frequency (or velocity). Common with
ALMA / NOEMA observations of line emission — CO, [OIII], Lyα. PyAutoLens
fits the cube as a multi-dataset problem: one analysis per channel, with
shared lens parameters and per-channel (or parametrically
frequency-dependent) source parameters.

## Cube structure

Conceptually, a cube is a list of interferometer datasets sharing one sky
footprint but sampled at different frequencies or velocities. Each
channel carries its own complex visibilities, its own noise properties,
and often its own effective uv weighting. The lens mass is usually shared
across all channels; the source is what changes with frequency.

## Source representations

Two strategies dominate:

- **Per-channel pixelized reconstruction**, often on a Delaunay-like
  mesh, when the goal is to recover resolved kinematics or complex line
  morphology.
- **Parametric source with frequency-dependent amplitudes** when the
  source is morphologically simple enough that geometry can be tied
  across channels and only intensities or a few shape parameters need to
  vary.

## Composing the multi-analysis

Under the hood, datacube fitting is just a many-dataset problem. Each
channel is wrapped in an `AnalysisInterferometer`, and the total fit is a
sum of those analyses. Shared lens parameters come from reusing the same
model components across channels; source parameters are shared or left
free channel by channel according to the science case.

## Compute scale

Datacubes are among the heaviest workloads in the workspace: many
channels, visibility-space likelihoods, and often pixelized sources in
every channel. Treat HPC as normal, not exceptional. Operational guidance
is in [`../operations/hpc.md`](../operations/hpc.md).

## Related pages

- [`concepts/interferometer_theory.md`](../concepts/interferometer_theory.md)
  — visibility-plane fundamentals.
- [`api/datasets.md`](./datasets.md) — `Interferometer` dataset row.
- [`api/analysis_objects.md`](./analysis_objects.md) —
  `AnalysisInterferometer` composition.
