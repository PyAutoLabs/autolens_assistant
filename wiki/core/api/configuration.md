---
title: Configuration — config/*.yaml files
sources:
  - project: PyAutoConf
    paths: [autoconf/conf.py]
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
last_updated: 2026-05-22
---

# Configuration files

Every PyAuto\* package ships a `<pkg>/config/` directory of YAML files. PyAutoConf
loads them (with override layering); the other packages query them via
`Conf.instance`.

You rarely write code that calls `Conf.instance` directly — but you will edit YAMLs
when you want to change default priors, plotting defaults, or output paths.

## The five `general.yaml` / `notation.yaml` / `output.yaml` triads

Each package's `config/` has a `general.yaml` (runtime flags), `notation.yaml` (plot
label conventions and unit strings), and `output.yaml` (where results are written).

- `PyAutoArray:autoarray/config/general.yaml` — grid layout defaults, numba flags.
- `PyAutoArray:autoarray/config/notation.yaml` — `y, x` arcsecond axis labels.
- `PyAutoArray:autoarray/config/output.yaml` — array-output filename conventions.
- `PyAutoFit:autofit/config/general.yaml` — search runtime defaults.
- `PyAutoFit:autofit/config/logging.yaml` — log levels.
- `PyAutoFit:autofit/config/notation.yaml` — parameter symbol/LaTeX strings.
- `PyAutoFit:autofit/config/output.yaml` — `output/` folder structure.
- `PyAutoGalaxy:autogalaxy/config/...` — galaxy + profile defaults.
- `PyAutoLens:autolens/config/...` — lensing-specific overrides.

## Priors

Default priors are how you say "a Sersic's `effective_radius` should be a
log-uniform between 0.01 and 8 arcseconds by default". Lives in
`<pkg>/config/priors/`.

`PyAutoFit:autofit/config/priors/` ships the meta-templates (`template.yaml`,
`model.yaml`, `profile.yaml`).

`PyAutoGalaxy:autogalaxy/config/priors/` ships per-class priors:

- `Sersic.yaml` — defaults for all Sersic-family classes.
- `Isothermal.yaml` / `PowerLaw.yaml` / `NFW.yaml` — defaults per mass profile.
- `cosmology.yaml` — cosmology constructor defaults.
- `mesh/` — pixelisation mesh defaults.
- `basis.yaml` — basis-expansion defaults.

`PyAutoLens:autolens/config/priors/` adds lensing-specific overrides.

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
formats. Two sub-flavours per package:

- `plots.yaml` / `plots_settings.yaml` — per-figure defaults (title, axis labels,
  whether to log-scale).
- `mat_wrap_1d/` and `mat_wrap_2d/` — matplotlib wrapper defaults (cmap, figure
  size, etc.).

Edit these to change plotting defaults workspace-wide.

## Layering

`Conf.instance` searches in this order:

1. `<pkg>/config/` (per-library defaults, the ones shipped in the source repo).
2. The path in `WORKSPACE_CONFIG_PATH` if set.
3. `~/.autoconf/` if present.

Later entries override earlier ones, so workspace-level config wins over library
defaults, and user-level config wins over both.

For workspace-level overrides, drop YAMLs into the project's own `config/`
directory at the repo root and `export WORKSPACE_CONFIG_PATH=$(pwd)/config`. The
`autolens_base_project` template ships a `config/` already populated with project
defaults — extend or override entries there rather than editing the library YAMLs.

## Common tweaks

- **Tighten a default prior** — edit the relevant YAML under `<pkg>/config/priors/`,
  workspace-overlay or in-place.
- **Change the default colormap** — edit `<pkg>/config/visualize/mat_wrap_2d/Cmap.yaml`.
- **Change output filenames** — edit `<pkg>/config/output.yaml`.
- **Suppress noisy logs** — edit `PyAutoFit:autofit/config/logging.yaml`.

## See also

- [`../stack/autoconf`](../stack/autoconf.md) — the loader.
- [`../../../skills/al_setup_environment.md`](../../../skills/al_setup_environment.md) —
  the env-var setup that includes `WORKSPACE_CONFIG_PATH`.
