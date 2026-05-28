---
title: Inversions and pixelisations
sources:
  - project: PyAutoArray
    paths:
      - autoarray/inversion/inversion/
      - autoarray/inversion/mesh/
      - autoarray/inversion/regularization/
    pinned_commit: bd18a76996183aed01cab820878d763e5513a13f
  - project: PyAutoLens
    paths:
      - autolens/lens/to_inversion.py
      - autolens/analysis/positions.py
    pinned_commit: a91febcb1aa12797f9d5ece54c1cbbac528cd087
last_updated: 2026-05-22
---

# Inversions and pixelisations

When the source is more complex than a Sersic (clumpy arcs, multiple bright
components, irregular morphology), you reconstruct it on a **pixel grid** in the
source plane rather than as a parametric profile. The reconstruction is a linear
inversion: the pixel-grid values are solved for given the data, noise, and a
regularisation prior.

Sources: `PyAutoArray:autoarray/inversion/` and
`PyAutoLens:autolens/lens/to_inversion.py`.

## Three pieces — mesh, regularisation, mapper

A pixelisation is composed of three things:

- **Mesh** — the discretisation of the source plane. Delaunay (triangular),
  Voronoi (irregular polygons), or rectangular (uniform grid). Adaptive variants
  refine the mesh where the image-plane signal is brightest.
- **Regularisation** — the smoothness prior that prevents the inversion from fitting
  the noise. Constant, ConstantSplit, AdaptiveBrightness, …
- **Mapper** — the linear operator that connects image-plane pixels (via ray tracing
  back through the lens) to source-plane mesh elements.

```python
pixelization = al.Pixelization(
    mesh=al.mesh.Delaunay(),
    regularization=al.reg.ConstantSplit(),
)
source = al.Galaxy(redshift=1.0, pixelization=pixelization)
```

Source: `PyAutoArray:autoarray/inversion/pixelization/` and
`PyAutoLens:autolens/lens/to_inversion.py`.

## Mesh choices

| Mesh | When |
|---|---|
| `al.mesh.RectangularUniform(shape=(N, N))` | Uniform, simplest, debug |
| `al.mesh.Delaunay(pixels=N)` | Adaptive Delaunay triangulation in the source plane |
| `al.mesh.KNNBarycentric(pixels=N)` | k-nearest-neighbour barycentric interpolant in the source plane |
| `al.mesh.RectangularAdaptImage(shape=(N, N), weight_power=…, weight_floor=…)` | Adaptive — denser mesh where the unlensed source image is bright |
| `al.mesh.RectangularAdaptDensity` / `RectangularRotatedAdaptImage` / `RectangularSplineAdapt*` | Other adaptive families |

The API is one mesh class per (image-plane mesh + source-plane mesh)
combination; mesh selection is done entirely by choosing the `mesh` class —
there is no separate `image_mesh=` kwarg on `Pixelization`.

> ⚠️ **Known regression in `2026.5.21.1`.** `Delaunay` and `KNNBarycentric`
> currently crash inside `FitImaging` with
> `AttributeError: 'NoneType' object has no attribute 'array'`. Use
> `RectangularUniform` (or one of the `RectangularAdapt*` variants) until the
> upstream fix lands. Tracking issue:
> <https://github.com/Jammy2211/PyAutoArray/issues/332>.

Adaptive meshes are the right choice for production fits but need a parametric
initial fit to seed the adapt image. The [`../../../skills/al_run_slam_pipeline.md`](../../../skills/al_run_slam_pipeline.md)
SLaM pipeline handles this automatically.

Sources: `PyAutoArray:autoarray/inversion/mesh/`.

## Regularisation

Without a smoothness prior, the inversion has more degrees of freedom than the data
constrains and overfits the noise. Regularisation penalises rough source-plane
solutions.

- **`al.reg.Constant`** — uniform smoothness penalty across the source plane.
- **`al.reg.ConstantSplit`** — separate penalties for high-signal and low-signal
  regions. Usually a better default than `Constant`.
- **`al.reg.AdaptiveBrightness`** — penalty varies with the adapt image. Lets the
  bright source centre take complex shapes while keeping the faint outskirts smooth.

Sources: `PyAutoArray:autoarray/inversion/regularization/`.

The regularisation coefficient is a free parameter the search varies (subject to a
prior, typically log-uniform over a few orders of magnitude).

## Positions likelihood penalty

The inversion can converge on a pathological solution where the source has been
demagnified to a single bright point. To prevent this, supply image positions of
the source (measured manually or from a parametric pre-fit) and add a positions
likelihood penalty:

```python
positions = al.Grid2DIrregular(values=[(0.5, 0.0), (-0.5, 0.0), (0.0, 0.4), (0.0, -0.4)])
positions_lh = al.PositionsLH(positions=positions, threshold=0.5)

analysis = al.AnalysisImaging(
    dataset=dataset,
    positions_likelihood_list=[positions_lh],
)
```

`threshold=0.5"` means models that fail to trace the positions to within 0.5
arcsecond in the source plane get an extra log-likelihood penalty. This eliminates
the demagnified-source mode without locking the parametric mass model.

Source: `PyAutoLens:autolens/analysis/positions.py`.

## What lives where

A pixelised source's reconstruction is computed *during* the fit, not stored in the
saved `tracer.json`. To inspect a finished pixelised fit, rebuild the `FitImaging`
from the saved tracer + dataset, then access `fit.inversion.reconstruction` and
friends. See [`../../../skills/al_inspect_source_reconstruction.md`](../../../skills/al_inspect_source_reconstruction.md).

## When to use a pixelised source

- Complex morphology (multiple knots, asymmetric arcs, partial Einstein rings).
- ALMA / JVLA interferometer data with sparse uv coverage.
- Anywhere a Sersic source leaves visible structured residuals.

When *not* to:

- First-fit exploratory runs. Use a parametric source first, then chain into a
  pixelised one. See [`../../../skills/al_chain_searches.md`](../../../skills/al_chain_searches.md).
- Cases where the source is genuinely a single smooth Sersic. Pixelising adds free
  parameters and runtime without adding fidelity.

## See also

- [`../../../skills/al_inspect_source_reconstruction.md`](../../../skills/al_inspect_source_reconstruction.md)
- [`../../../skills/al_chain_searches.md`](../../../skills/al_chain_searches.md)
- [`../../../skills/al_run_slam_pipeline.md`](../../../skills/al_run_slam_pipeline.md)
- [`slam_pipeline`](./slam_pipeline.md) — SLaM is the canonical workflow for moving
  to a pixelised source.
