---
name: al_datacube_modeling
description: Fit a strong-lens model to a 3D spectral datacube — typically ALMA / JVLA / NOEMA, where each frequency channel is a 2D visibility plane and the source's spatial morphology can change across channels (rotating disk, outflow, line-emission region). Reuses `al_build_interferometer_model` per channel but ties parameters across the cube. Pairs with `al_adaptive_pixelization` (Delaunay mesh is the standard datacube pixelisation). Writes a runnable Python script in scripts/. **Status: stub.**
---

# Datacube modeling — spectral interferometric strong lensing

A 2D fit treats one image of the source. A datacube fit treats the
source as a stack of 2D maps over frequency or velocity — what a rotating
disk looks like in CO, what an outflow looks like in [OIII]. The lens
parameters are shared across channels; the source morphology is
per-channel (or parametrically frequency-dependent).

Workspace path:
`autolens_workspace:scripts/interferometer/features/datacube/start_here.py`
(and sibling files: `delaunay.py`, parametric source variants).

## Ask

- *"What's the cube — N frequency channels of visibilities (ALMA
  spectral) or a hyperspectral imaging cube?"* The interferometer path
  is the workspace default.
- *"Source representation per channel — parametric (Sersic per channel,
  potentially with tied parameters), pixelised Delaunay (per channel
  reconstruction), or hybrid?"*
- *"Lens model — assumed channel-independent (the standard) or do you
  expect chromatic mass effects?"*
- *"Compute scale — how many channels and how many visibilities per
  channel?"* Datacubes are the heaviest interferometer workloads.

## Branch — Delaunay-per-channel pixelised source

> TODO: recipe. Pattern: build a list of `AnalysisInterferometer`
> instances (one per channel), each with a Delaunay-pixelised source;
> the same lens galaxy is shared across all analyses; wrap each channel in
> `af.AnalysisFactor` and combine with `af.FactorGraphModel`. See
> `PyAutoLens:autolens/interferometer/...`.

## Branch — parametric source with frequency-dependent intensity

A single source profile per channel with tied geometry and free
intensities — useful for line-emission morphology.

> TODO: recipe.

## Combine

- [`al_build_interferometer_model`](./al_build_interferometer_model.md)
  — single-channel building block.
- [`al_adaptive_pixelization`](./al_adaptive_pixelization.md) — Delaunay
  is the standard datacube mesh.
- [`al_multi_dataset`](./al_multi_dataset.md) — datacube is a
  many-dataset problem under the hood.

## Further reading

- **Student / new to lensing** — _ (specialist workflow).
- **General reference** — [RTD: overview_3_features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html):
  interferometer / datacube feature section.
- **Experienced PyAutoLens user** — [workspace/lens: interferometer/features/datacube/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/interferometer/features/datacube/start_here.py):
  the canonical datacube walkthrough.

See also [`wiki/core/api/datacube.md`](../wiki/core/api/datacube.md) for
the API surface and
[`wiki/core/concepts/interferometer_theory.md`](../wiki/core/concepts/interferometer_theory.md)
for visibility / uv-plane fundamentals.
