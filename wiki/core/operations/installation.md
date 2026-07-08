---
title: Installation
sources:
  - project: PyAutoConf
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

# Installation

The PyAuto\* stack is published to PyPI. For most users, `pip install autolens`
pulls in the four lower libraries via transitive deps.

For users who need to read or modify the libraries (writing a new profile, debugging
an internal, contributing upstream), an editable-clone install is the right path.

The [`al_setup_environment`](../../../skills/al_setup_environment.md) skill drives both
paths in code. This page is the rationale and reference.

## Pip install (most users)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install "autolens[jax]" numba
```

Python ≥ 3.9 is the minimum across the stack and JAX runs on every supported
version including 3.10. 3.11 is the recommended baseline (it's what
`autolens_workspace`'s `runtime.txt` targets and what the JAX wheels are
best-tested against), so 3.10 works but is suboptimal — prefer 3.11 for new
environments. Treat any "JAX unavailable on Python 3.10" message as a wheel
mismatch in that specific env, not a stack-wide constraint.

`autolens[jax]` includes JAX, which provides large speedups on CPU multithreading and
order-of-magnitude speedups on GPU. `numba` is optional but accelerates the
JIT-compiled geometry kernels in PyAutoArray.

## Editable-clone install (developers / contributors)

```bash
mkdir -p sources && cd sources
git clone https://github.com/PyAutoLabs/PyAutoConf.git
git clone https://github.com/PyAutoLabs/PyAutoArray.git
git clone https://github.com/PyAutoLabs/PyAutoFit.git
git clone https://github.com/PyAutoLabs/PyAutoGalaxy.git
git clone https://github.com/PyAutoLabs/PyAutoLens.git
cd ..

for repo in PyAutoConf PyAutoArray PyAutoFit PyAutoGalaxy PyAutoLens; do
    pip install -e "sources/$repo"
done
```

Order matters — install bottom-up so each pip install can resolve its previous
dependency.

Resolve git URLs via [`../../sources.yaml`](../../sources.yaml) rather than the inline
hard-coded URLs above; the YAML is the source of truth and accommodates URL changes.

## Version pins worth knowing

The PyAuto\* stack pins several deps strictly to keep numerical reproducibility. The
ones that bite users most often:

- `numpy >= 1.24.0, <= 2.0.1` — PyAutoConf
- `scipy <= 1.14.0` — PyAutoArray + PyAutoFit
- `scikit-image <= 0.24.0`, `scikit-learn <= 1.5.1` — PyAutoArray
- `dynesty == 2.1.4`, `emcee >= 3.1.6`, `Nautilus == 1.0.5` — PyAutoFit + downstream
- `JAX 0.4.13 <= x < 0.5.0`

If you're upgrading one of these manually (e.g. trying `numpy 2.1`), expect things
to break in non-obvious places. Stick to the pinned ranges unless you specifically
need the new behaviour and you've checked that the stack supports it.

## JAX details

The stack uses JAX for accelerated linear algebra and (optionally) GPU offloading.
A few notes:

- Importing JAX-using PyAuto\* code requires the JAX environment variables to be set
  *before* the import. Every workspace script begins with
  `from autoconf import jax_wrapper` for exactly this reason — it sets the env then
  imports JAX in a fixed order.
- For GPU support, install `jax[cuda12]` (or whatever your CUDA version requires)
  *instead of* the default CPU JAX. PyAutoLens picks it up automatically.
- On Google Colab, the workspace scripts use `autoconf.setup_colab.for_autolens` to
  configure the environment. See `PyAutoConf:autoconf/setup_colab.py`.

## Verifying the install

```bash
python -c "import autolens, autofit, autogalaxy, autoarray, autoconf; print(autolens.__version__)"
```

If this prints a version without a traceback, the install is ready. For a more
thorough check, run the verification script from
[`al_setup_environment`](../../../skills/al_setup_environment.md).

## See also

- [`operations/sandbox`](./sandbox.md) — cache directory and env-var overrides for
  restricted environments.
- [`operations/hpc`](./hpc.md) — running fits on a cluster.
- [`stack/overview`](../stack/overview.md) — what each library does.
