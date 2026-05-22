---
title: Interferometer theory — visibilities, uv-plane, FFT
sources:
  - project: PyAutoLens
    paths:
      - autolens/interferometer/model/analysis.py
    pinned_commit: main
  - project: PyAutoArray
    paths:
      - autoarray/dataset/interferometer
    pinned_commit: main
last_updated: 2026-05-22
---

# Interferometer theory (companion to `api/datasets.md`)

**Status: stub — content to be filled out.** PyAutoLens fits ALMA / JVLA
/ NOEMA visibilities directly — no image-plane deconvolution. This page
covers the physics and numerics of why visibility-plane fitting is
preferred for interferometric data and what knobs the user has.

## The visibility plane

> TODO: V(u, v) as the Fourier transform of the source brightness.
> Interferometers sample V(u, v) at the antenna baselines and times;
> the dirty image is the FFT of this sparse uv coverage convolved with
> the dirty beam.

## Why fit visibilities not dirty images

> TODO: visibilities have independent (well, less correlated) Gaussian
> noise; dirty images have heavily correlated noise from the dirty
> beam. The likelihood is much better behaved in visibility space.

## Real-space mask + visibility computation

> TODO: PyAutoLens computes a model image on a real-space grid (masked),
> FFTs to visibilities, evaluates Gaussian residuals against the
> measured visibilities. Document the masking convention and the
> `real_space_shape` knob.

## NUFFT vs. direct FFT

> TODO: when antennas sit on non-regular uv positions a direct FFT
> can't be used; PyAutoArray's NUFFT (non-uniform FFT) handles
> arbitrary uv coverage. Cite the relevant `PyAutoArray` module.

## Memory and runtime considerations

> TODO: visibility datasets are big — ALMA observations routinely have
> >1M visibilities. Discuss subsampling, the `transformer_class`
> choice, and GPU acceleration if available.

## Datacubes — frequency × visibility

> TODO: spectral cubes are stacks of 2D visibility planes. Cross-link
> [`api/datacube.md`](../api/datacube.md).

## Related pages

- [`api/datasets.md`](../api/datasets.md) — `Interferometer` dataset
  row.
- [`api/datacube.md`](../api/datacube.md) — spectral cubes.
- [`stack/autoarray.md`](../stack/autoarray.md) — Fourier / NUFFT
  primitives.
