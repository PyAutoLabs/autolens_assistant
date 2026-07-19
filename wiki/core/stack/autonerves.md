---
title: PyAutoNerves (autonerves)
sources:
  - project: PyAutoNerves
    paths:
      - autonerves/conf.py
      - autonerves/dictable.py
      - autonerves/json_prior/
      - README.md
    pinned_commit: main
last_updated: 2026-07-09
---

# PyAutoNerves — the configuration layer

Project: [`PyAutoNerves`](https://github.com/PyAutoLabs/PyAutoNerves). Import: `autonerves`.

PyAutoNerves is the configuration loader the rest of the stack reads from. Every
PyAutoArray / PyAutoFit / PyAutoGalaxy / PyAutoLens package ships its own
`<pkg>/config/` directory of YAML files; autonerves is the machinery that finds,
merges, and queries them.

You rarely call autonerves directly. You call `Conf.instance` to read a setting, or you
edit a YAML file under one of the other packages' `config/` folders, or you use
`from_json` / `to_json` for serialising model objects to disk.

## What lives in autonerves

- **`autonerves/conf.py`** — `Conf.instance` global accessor; loads YAML config from
  the per-package `config/` directories with override layering (project config →
  workspace config → user config).
- **`autonerves/dictable.py`** — the `Dictable` mixin and `from_json` / `to_json`
  helpers. PyAutoLens uses these to serialise `Tracer` / `Galaxy` / profile objects
  to `tracer.json` so a finished fit can be loaded later.
- **`autonerves/json_prior/`** — the JSON representation of priors for the autofit
  model system.
- **`autonerves/setup_colab.py`** — Google Colab environment setup helper used by
  workspace `start_here.py` scripts.
- **`autonerves/jax_wrapper.py`** — imported first in every workspace script to set
  JAX environment variables before anything else loads.

## Configuration layering

When a package looks up a config key, autonerves walks a search path:

1. Per-package `<pkg>/config/`.
2. Any directory exported via `WORKSPACE_CONFIG_PATH` environment variable.
3. The user's `~/.autonerves/` directory if present.

Later entries override earlier ones, so workspace-level config beats library
defaults, and user-level config beats both.

Source: `PyAutoNerves:autonerves/conf.py`.

## Dictable — JSON serialisation

`Dictable` is the mixin that gives objects round-trippable JSON. A `Tracer` is
Dictable; a `LightProfile` subclass that includes `Dictable` in its inheritance
becomes serialisable too.

```python
from autonerves.dictable import to_json, from_json
to_json(obj=tracer, file_path="tracer.json")
tracer2 = from_json(file_path="tracer.json")
```

When you write a custom profile ([`../../../skills/al_custom_profile.md`](../../../skills/al_custom_profile.md))
and want it to survive being written to `tracer.json`, inherit from `Dictable`.

## Dependencies

`autonerves` pulls in JAX (`jax >= 0.4.13`), `jaxnnls`, `typing-inspect`, `PyYAML`, and
`numpy`. JAX is the surprise: it's a config-layer dep because the JAX environment
variables need to be set *before* any other PyAuto\* import, which is why every
workspace script begins with `from autonerves import jax_wrapper` as the very first
line.

## See also

- [`api/configuration`](../api/configuration.md) — what each `<pkg>/config/` YAML file controls.
- [`stack/overview`](./overview.md) — where autonerves sits in the dependency chain.
