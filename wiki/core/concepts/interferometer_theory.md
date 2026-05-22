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

PyAutoLens fits ALMA / JVLA
/ NOEMA visibilities directly — no image-plane deconvolution. This page
covers the physics and numerics of why visibility-plane fitting is
preferred for interferometric data and what knobs the user has.

## The visibility plane

An interferometer does not observe sky pixels directly. It samples the
Fourier transform of the sky brightness, `V(u, v)`, at the baseline
coordinates traced out by antenna pairs. Because the sampling is sparse
and irregular, a naive inverse transform gives a **dirty image**
convolved with the dirty beam rather than the true sky.

## Why fit visibilities not dirty images

That is why PyAutoLens fits the visibilities themselves. In visibility
space the noise model is much closer to the measurement process: complex
data points with known uncertainties. In dirty-image space the beam and
sampling pattern induce strong pixel-to-pixel correlations, which make
the likelihood harder to interpret and easier to bias.

## Real-space mask + visibility computation

The lens model is still built in real space. The workflow is:

1. define a `real_space_mask` that sets the image-plane region to model
2. evaluate the lensed source and lens light on that masked grid
3. transform the model image to the observed visibility coordinates
4. compare model and measured visibilities with a Gaussian likelihood

The real-space mask is therefore a major scientific and computational
knob. It sets the domain on which the source is represented before the
Fourier transform and directly affects runtime.

## NUFFT vs. direct FFT

Real interferometers do not sample a rectangular Fourier grid, so a
plain FFT is not enough. PyAutoLens uses a non-uniform FFT via
`autolens.TransformerNUFFT`, documented on RTD and backed by
`PyAutoArray:autoarray/operators/transformer.py`. The RTD autosummary
notes three details worth knowing:

- the transformer is planned from the uv coordinates and real-space mask
- a phase shift accounts for pixel centering in real space
- an adjoint scaling normalizes inverse operations

This is the numerical bridge between a regular real-space model image and
irregular Fourier-space measurements.

## Memory and runtime considerations

Interferometer datasets are often memory-bound before they are
sampler-bound. Large ALMA datasets can contain enormous visibility
tables, and every likelihood call requires repeated forward transforms.
The usual runtime levers are:

- shrinking the real-space mask to the informative region
- reducing channel count or averaging when scientifically acceptable
- choosing the transformer backend explicitly when needed
- using accelerated hardware and conservative inversion settings

Even a modest physical model can therefore be a heavy compute job.

## Datacubes — frequency × visibility

Spectral cubes repeat this same logic over many frequencies or velocities.
Each channel is its own visibility-plane likelihood, while the lens mass
is typically shared. For that extension, see
[`../api/datacube.md`](../api/datacube.md).

## Related pages

- [`api/datasets.md`](../api/datasets.md) — `Interferometer` dataset
  row.
- [`api/datacube.md`](../api/datacube.md) — spectral cubes.
- [`stack/autoarray.md`](../stack/autoarray.md) — Fourier / NUFFT
  primitives.
