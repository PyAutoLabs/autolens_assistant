---
title: PyAutoConf (autoconf)
sources:
  - project: PyAutoConf
    paths:
      - autoconf/conf.py
      - autoconf/dictable.py
      - autoconf/json_prior/
      - README.rst
    pinned_commit: main
last_updated: 2026-05-22
---

# PyAutoConf — the configuration layer

Project: [`PyAutoConf`](https://github.com/PyAutoLabs/PyAutoConf). Import: `autoconf`.

PyAutoConf is the configuration loader the rest of the stack reads from. Every
PyAutoArray / PyAutoFit / PyAutoGalaxy / PyAutoLens package ships its own
`<pkg>/config/` directory of YAML files; autoconf is the machinery that finds,
merges, and queries them.

You rarely call autoconf directly. You call `Conf.instance` to read a setting, or you
edit a YAML file under one of the other packages' `config/` folders, or you use
`from_json` / `to_json` for serialising model objects to disk.

## What lives in autoconf

- **`autoconf/conf.py`** — `Conf.instance` global accessor; loads YAML config from
  the per-package `config/` directories with override layering (project config →
  workspace config → user config).
- **`autoconf/dictable.py`** — the `Dictable` mixin and `from_json` / `to_json`
  helpers. PyAutoLens uses these to serialise `Tracer` / `Galaxy` / profile objects
  to `tracer.json` so a finished fit can be loaded later.
- **`autoconf/json_prior/`** — the JSON representation of priors for the autofit
  model system.
- **`autoconf/setup_colab.py`** — Google Colab environment setup helper used by
  workspace `start_here.py` scripts.
- **`autoconf/jax_wrapper.py`** — imported first in every workspace script to set
  JAX environment variables before anything else loads.

## Configuration layering

When a package looks up a config key, autoconf walks a search path:

1. Per-package `<pkg>/config/`.
2. Any directory exported via `WORKSPACE_CONFIG_PATH` environment variable.
3. The user's `~/.autoconf/` directory if present.

Later entries override earlier ones, so workspace-level config beats library
defaults, and user-level config beats both.

Source: `PyAutoConf:autoconf/conf.py`.

## Dictable — JSON serialisation

`Dictable` is the mixin that gives objects round-trippable JSON. A `Tracer` is
Dictable; a `LightProfile` subclass that includes `Dictable` in its inheritance
becomes serialisable too.

```python
from autoconf.dictable import to_json, from_json
to_json(obj=tracer, file_path="tracer.json")
tracer2 = from_json(file_path="tracer.json")
```

When you write a custom profile ([`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md))
and want it to survive being written to `tracer.json`, inherit from `Dictable`.

## Dependencies

`autoconf` pulls in JAX (`jax >= 0.4.13`), `jaxnnls`, `typing-inspect`, `PyYAML`, and
`numpy`. JAX is the surprise: it's a config-layer dep because the JAX environment
variables need to be set *before* any other PyAuto\* import, which is why every
workspace script begins with `from autoconf import jax_wrapper` as the very first
line.

## See also

- [`api/configuration`](../api/configuration.md) — what each `<pkg>/config/` YAML file controls.
- [`stack/overview`](./overview.md) — where autoconf sits in the dependency chain.
