---
title: Configuration — config/*.yaml files
sources:
  - project: PyAutoNerves
    paths: [autonerves/conf.py]
    pinned_commit: main
  - project: PyAutoArray
    paths: [autoarray/config/]
    pinned_commit: main
  - project: PyAutoFit
    paths: [autofit/config/]
    pinned_commit: main
  - project: PyAutoGalaxy
    paths: [autogalaxy/config/]
    pinned_commit: main
  - project: PyAutoLens
    paths: [autolens/config/]
    pinned_commit: main
last_updated: 2026-07-09
---

# Configuration files

Every PyAuto\* package ships a `<pkg>/config/` directory of YAML files. PyAutoNerves
loads them (with override layering); the other packages query them via
`Conf.instance`.

You rarely write code that calls `Conf.instance` directly — but you will edit YAMLs
when you want to change default priors, plotting defaults, or output paths.

## What each package's `config/` ships

The file set differs per package — not every package has every YAML:

- `PyAutoArray:autoarray/config/` — `general.yaml` (grid/runtime flags),
  `logging.yaml`, `visualize/`.
- `PyAutoFit:autofit/config/` — `general.yaml` (search runtime defaults),
  `logging.yaml`, `notation.yaml` (parameter symbol/LaTeX strings),
  `output.yaml` (`output/` folder structure), `non_linear/` (per-search
  defaults), `priors/`, `visualize/`.
- `PyAutoGalaxy:autogalaxy/config/` — `general.yaml`, `latent.yaml`,
  `notation.yaml`, `output.yaml`, `priors/`, `visualize/`.
- `PyAutoLens:autolens/config/` — `general.yaml`, `latent.yaml`,
  `non_linear.yaml`, `output.yaml`, `visualize/` (its priors ride on
  PyAutoGalaxy's — there is no `autolens/config/priors/`).

## Priors

Default priors are how you say "a Sersic's `effective_radius` should be a
log-uniform between 0.01 and 8 arcseconds by default". Lives in
`<pkg>/config/priors/`.

`PyAutoFit:autofit/config/priors/` ships the meta-templates (`template.yaml`,
`model.yaml`, `profile.yaml`).

`PyAutoGalaxy:autogalaxy/config/priors/` ships per-class priors, organised by
family:

- `light/` and `mass/` — one YAML per profile class (Sersic family,
  Isothermal, PowerLaw, NFW, …).
- `galaxy/`, `ellipse/`, `point_sources.yaml` — composite-object defaults.
- `cosmology.yaml` — cosmology constructor defaults.
- `mesh/` — pixelisation mesh defaults.
- `basis.yaml` — basis-expansion defaults; `dataset_model.yaml` — the
  `DatasetModel` nuisance parameters (sky level, grid offset).

PyAutoLens no longer ships its own `config/priors/` — lensing classes take
their defaults from the PyAutoGalaxy priors above.

When you compose `af.Model(al.lp.Sersic)`, the constructor parameters get their
default priors from these YAMLs.

To override a default permanently in your workspace: copy the relevant YAML into a
workspace `config/` directory and point `WORKSPACE_CONFIG_PATH` at it. To override
per-fit: set the prior on the `af.Model` instance:

```python
sersic = af.Model(al.lp.Sersic)
sersic.intensity = af.UniformPrior(lower_limit=0.01, upper_limit=10.0)
```

## Visualize

`<pkg>/config/visualize/` controls plot styling — colour maps, axis labels, output
formats — via a `plots.yaml` (per-figure defaults) and, in PyAutoGalaxy, a
`general.yaml`. The old `mat_wrap_1d/` / `mat_wrap_2d/` wrapper folders belonged
to the removed object-oriented plot system and no longer exist.

Edit these to change plotting defaults workspace-wide.

## Layering

`Conf.instance` searches in this order:

1. `<pkg>/config/` (per-library defaults, the ones shipped in the source repo).
2. The path in `WORKSPACE_CONFIG_PATH` if set.
3. `~/.autonerves/` if present.

Later entries override earlier ones, so workspace-level config wins over library
defaults, and user-level config wins over both.

For workspace-level overrides, drop YAMLs into the project's own `config/`
directory at the repo root and `export WORKSPACE_CONFIG_PATH=$(pwd)/config`. The
`autolens_assistant` repo ships a `config/` already populated with project
defaults — extend or override entries there rather than editing the library YAMLs.

## Common tweaks

- **Tighten a default prior** — edit the relevant YAML under
  `PyAutoGalaxy:autogalaxy/config/priors/` (or `PyAutoFit:autofit/config/priors/`
  for the templates), workspace-overlay or in-place.
- **Change plot styling / colormaps** — edit `<pkg>/config/visualize/plots.yaml`.
- **Change output filenames** — edit `<pkg>/config/output.yaml` (PyAutoFit,
  PyAutoGalaxy, PyAutoLens).
- **Suppress noisy logs** — edit `PyAutoFit:autofit/config/logging.yaml`.

## See also

- [`../stack/autonerves`](../stack/autonerves.md) — the loader.
- [`../../../skills/al_setup_environment.md`](../../../skills/al_setup_environment.md) —
  the env-var setup that includes `WORKSPACE_CONFIG_PATH`.
