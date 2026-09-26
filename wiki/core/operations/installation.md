---
title: Installation
sources:
  - project: PyAutoNerves
    paths: [pyproject.toml]
    pinned_commit: 8021c41dd110e7f3a70e3c650234e138a05cfb8a  # release tag 2026.9.26.1
  - project: PyAutoArray
    paths: [pyproject.toml]
    pinned_commit: 0f870c38712cd4124fb44c5626dbc78b1391c531  # release tag 2026.9.26.1
  - project: PyAutoFit
    paths: [pyproject.toml]
    pinned_commit: 326f611b1b40afd89bb73956441faa7379328407  # release tag 2026.9.26.1
  - project: PyAutoGalaxy
    paths: [pyproject.toml]
    pinned_commit: 6bf0bb40a194abed2366190695d9b37268c00a5d  # release tag 2026.9.26.1
  - project: PyAutoLens
    paths: [pyproject.toml]
    pinned_commit: 33e41eaecaa159ea2c159806e0535b7bb5705f9b  # release tag 2026.9.26.1
last_updated: 2026-09-26
content_sha256: fe95b626301c5848f2cd1727778f920b5b5eefa8c3f3418862f467a30801f175
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
python3.12 -m venv .venv
source .venv/bin/activate
pip install "autolens[jax]" numba
```

**Python 3.12 or newer is required.** Every library in the stack declares
`requires-python = ">=3.12"` in its `pyproject.toml` (checked at release tag
2026.9.26.1 for PyAutoNerves, PyAutoArray, PyAutoFit, PyAutoGalaxy and
PyAutoLens), and PyPI's metadata for `autolens` reports `requires_python >=3.12`
for every current release (all of 2026.8.x and 2026.9.x, including 2026.9.19.1 and
the current 2026.9.26.1). On Python 3.11 or older, `pip install autolens` fails
with "autolens requires Python 3.12 or later"; releases at or below 2026.7.29.1
still declare `>=3.9` but are unsupported and ship without JAX, so do not pin one
to dodge the floor. Create the environment with an explicit `python3.12` (or
3.13 / 3.14, which the classifiers also list), as above and in
[`al_setup_environment`](../../../skills/al_setup_environment.md).

JAX is a base dependency of the stack (via `autonerves`, on every platform except
Intel macOS, which has no `jaxlib` wheels); the `[jax]` extra is kept as a no-op so
the command above keeps resolving. JAX provides large speedups on CPU multithreading and
order-of-magnitude speedups on GPU. `numba` is optional but accelerates the
JIT-compiled geometry kernels in PyAutoArray.

## Editable-clone install (developers / contributors)

```bash
mkdir -p sources && cd sources
git clone https://github.com/PyAutoLabs/PyAutoNerves.git
git clone https://github.com/PyAutoLabs/PyAutoArray.git
git clone https://github.com/PyAutoLabs/PyAutoFit.git
git clone https://github.com/PyAutoLabs/PyAutoGalaxy.git
git clone https://github.com/PyAutoLabs/PyAutoLens.git
cd ..

for repo in PyAutoNerves PyAutoArray PyAutoFit PyAutoGalaxy PyAutoLens; do
    pip install -e "sources/$repo"
done
```

Order matters — install bottom-up so each pip install can resolve its previous
dependency.

Resolve git URLs via [`../../../sources.yaml`](../../../sources.yaml) rather than the inline
hard-coded URLs above; the YAML is the source of truth and accommodates URL changes.

## Version pins worth knowing

The PyAuto\* stack pins several deps strictly to keep numerical reproducibility. The
ones that bite users most often:

- `numpy >= 1.24.0, < 3.0.0` and `jax` / `jaxlib >= 0.7.0, < 0.12.0`,
  `jaxnnls == 1.0.1` — PyAutoNerves (JAX 0.11 in turn needs `numpy >= 2.1` and
  `scipy >= 1.15`)
- `scipy <= 1.17.1` — PyAutoArray + PyAutoFit
- `scikit-image <= 0.26.0`, `scikit-learn <= 1.8.0` — PyAutoArray
- `dynesty == 2.1.5`, `emcee >= 3.1.6` — PyAutoFit; `nautilus-sampler == 1.0.5` —
  PyAutoFit + PyAutoLens

If you're upgrading one of these manually (e.g. trying `scipy 1.18`), expect things
to break in non-obvious places. Stick to the pinned ranges unless you specifically
need the new behaviour and you've checked that the stack supports it.

## JAX details

The stack uses JAX for accelerated linear algebra and (optionally) GPU offloading.
A few notes:

- Importing JAX-using PyAuto\* code requires the JAX environment variables to be set
  *before* the import. Every workspace script begins with
  `from autonerves import jax_wrapper` for exactly this reason — it sets the env then
  imports JAX in a fixed order.
- For GPU support, install `jax[cuda12]` (or whatever your CUDA version requires)
  *instead of* the default CPU JAX. PyAutoLens picks it up automatically.
- On Google Colab, the workspace scripts use `autonerves.setup_colab.for_autolens` to
  configure the environment. See `PyAutoNerves:autonerves/setup_colab.py`.

## Verifying the install

```bash
python -c "import autolens, autofit, autogalaxy, autoarray, autonerves; print(autolens.__version__)"
```

If this prints a version without a traceback, the install is ready. For a more
thorough check, run the verification script from
[`al_setup_environment`](../../../skills/al_setup_environment.md).

## See also

- [`operations/sandbox`](./sandbox.md) — cache directory and env-var overrides for
  restricted environments.
- [`operations/hpc`](./hpc.md) — running fits on a cluster.
- [`stack/overview`](../stack/overview.md) — what each library does.
