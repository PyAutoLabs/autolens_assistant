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

**Status: stub — content to be filled out.** A datacube is a stack of
2D visibility planes indexed by frequency (or velocity). Common with
ALMA / NOEMA observations of line emission — CO, [OIII], Lyα. PyAutoLens
fits the cube as a multi-dataset problem: one analysis per channel, with
shared lens parameters and per-channel (or parametrically
frequency-dependent) source parameters.

## Cube structure

> TODO: `(n_channels, n_visibilities)` real and imaginary visibility
> stacks; per-channel uv coverage; per-channel noise.

## Source representations

> TODO:
> - **Per-channel pixelised** (Delaunay) — each channel reconstructed
>   independently with a shared mesh template; the cube reveals
>   velocity structure.
> - **Parametric with frequency-dependent intensity** — single source
>   profile, intensity = f(channel). Useful for line-emission
>   morphology.

## Composing the multi-analysis

> TODO: list-of-analyses pattern (one `AnalysisInterferometer` per
> channel); sum log-likelihoods via the standard `+` operator (verify).
> Lens parameters tied via `af.Model` shared references.

## Compute scale

> TODO: datacubes are the heaviest workloads; expect HPC. Cross-link
> [`operations/hpc.md`](../operations/hpc.md).

## Related pages

- [`concepts/interferometer_theory.md`](../concepts/interferometer_theory.md)
  — visibility-plane fundamentals.
- [`api/datasets.md`](./datasets.md) — `Interferometer` dataset row.
- [`api/analysis_objects.md`](./analysis_objects.md) —
  `AnalysisInterferometer` composition.
