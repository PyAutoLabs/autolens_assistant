---
title: The PyAuto* stack at a glance
sources:
  - project: PyAutoNerves
    paths: [pyproject.toml]
    pinned_commit: main
  - project: PyAutoArray
    paths: [pyproject.toml]
    pinned_commit: main
  - project: PyAutoFit
    paths: [pyproject.toml]
    pinned_commit: main
  - project: PyAutoGalaxy
    paths: [pyproject.toml]
    pinned_commit: main
  - project: PyAutoLens
    paths: [pyproject.toml]
    pinned_commit: main
last_updated: 2026-05-22
---

# The PyAuto\* stack at a glance

Five libraries, one chain. Each builds on the one below it; PyAutoLens is the umbrella
user-facing library, and the layers below surface only when you need to understand
something specific.

```
autonerves       configuration: YAML loader, prior + class registry
   ↓
autoarray      data: arrays, grids, masks, geometry, structures
   ↓
autofit        modelling: af.Model / af.Collection, non-linear searches, samples
   ↓
autogalaxy     galaxies: light profiles, mass profiles, plane, cosmology
   ↓
autolens       lensing: Tracer (multi-plane ray tracing), lensing analysis
```

## Who does what

- **autonerves** ([page](./autonerves.md)) — reads `<pkg>/config/*.yaml` files for
  default priors, plotting defaults, output paths. Every other library uses it.
- **autoarray** ([page](./autoarray.md)) — defines `Array2D`, `Grid2D`, `Mask2D`,
  `Imaging`, `Interferometer`, plus the geometry / over-sampling / inversion
  utilities the lensing analyses rely on.
- **autofit** ([page](./autofit.md)) — model composition via `af.Model` /
  `af.Collection`, a catalogue of non-linear searches, a `Samples` API for the
  posterior, and an aggregator for bulk results.
- **autogalaxy** ([page](./autogalaxy.md)) — the physics of an individual galaxy: a
  catalogue of light profiles (Sersic, Exponential, MGE, Shapelets…) and mass
  profiles (Isothermal, NFW, PowerLaw, multipole, external shear…), composed into
  `Galaxy` objects with redshifts.
- **autolens** ([page](./autolens.md)) — multi-plane ray tracing (`Tracer`), the
  lensing-specific analysis objects (`AnalysisImaging`, `AnalysisInterferometer`,
  `AnalysisPoint`), and lensing-specific plotting.

## Imports you see everywhere

```python
import autofit as af
import autolens as al
import autolens.plot as aplt
```

The aliases are conventional — every workspace script uses them, and so do the
skills here.

## Cross-package dependencies

| Package | Depends on |
|---|---|
| autonerves | (none from this stack) |
| autoarray | autonerves |
| autofit | autonerves, array_api_compat |
| autogalaxy | autofit, autoarray |
| autolens | autogalaxy |

Installing PyAutoLens via pip pulls in the four below it automatically.

## When to look at which page

- *"What is a `Mask2D`?"* → autoarray, [arrays page](./autoarray.md).
- *"How do I configure default priors for my new profile?"* → autonerves,
  [config page](./autonerves.md), and [api/configuration](../api/configuration.md).
- *"Which non-linear searches can I use?"* → autofit,
  [api/searches](../api/searches.md).
- *"What light profiles ship out of the box?"* → autogalaxy,
  [api/light_profile_catalog](../api/light_profile_catalog.md).
- *"How does multi-plane ray tracing work?"* → autolens, and
  [concepts/tracer](../concepts/tracer.md).

## See also

- [Installation](../operations/installation.md) — getting all five installed.
- [Configuration](../api/configuration.md) — the YAML files each package ships.
