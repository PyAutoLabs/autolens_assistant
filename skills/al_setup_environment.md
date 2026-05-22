---
name: al_setup_environment
description: Install and configure a Python environment for the PyAuto* lensing stack. Two modes — pip install (fast, for users who just want to run code) or editable clone of all five source repos (for users who want to read, modify, or contribute to the libraries). Sets sandbox cache env vars on restricted filesystems and verifies the install by importing autolens. Use this skill once per machine before invoking any other lensing skill.
---

# Setting up an environment for the PyAuto\* stack

This skill installs the libraries the workspace targets — PyAutoConf, PyAutoArray, PyAutoFit,
PyAutoGalaxy, PyAutoLens — and prepares the sandbox so the rest of the skills will run.
The user picks one of two install modes: pip (read-only, fastest path to "import autolens
works") or editable-clone (source-level access, slower but lets you read and modify the
libraries).

## Ask

Before touching anything, confirm with the user:

- Are you running on macOS, Linux, or Windows / WSL?
- Do you already have a Python environment manager (venv, conda, mamba)? If yes, will
  you use it for this workspace too?
- Do you need to *read or modify* the PyAuto\* source while you work (editable clone
  mode), or just *use* the libraries (pip mode)?

If they pick pip, branch into "Pip install". If they want editable clones, branch into
"Editable clone of all five repos".

For background on what each library does, point at
[`wiki/core/stack/overview.md`](../wiki/core/stack/overview.md). For sandbox env var details, point
at [`wiki/core/operations/installation.md`](../wiki/core/operations/installation.md) and
[`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md).

## Branch — Pip install

The simplest path. PyAutoLens declares the rest of the stack as transitive deps, so a
single `pip install` pulls everything in.

```bash
# Create or activate a Python 3.11 env (use whatever env manager you have)
python3.11 -m venv .venv
source .venv/bin/activate

# Core stack + JAX-accelerated array ops + numba JIT
pip install --upgrade pip
pip install "autolens[jax]" numba
```

Python ≥ 3.9 works in principle (all five repos declare `requires-python = ">=3.9"`),
but 3.11 is the recommended baseline — it's what the workspace tooling targets.

Verify:

```bash
python -c "import autolens, autofit, autogalaxy, autoarray, autoconf; print(autolens.__version__)"
```

If that prints a version (no traceback), the install is good.

## Branch — Editable clone of all five repos

Use this when you want to read or modify the PyAuto\* source. Each repo is cloned, then
installed with `pip install -e .` in dependency order.

```bash
# Pick a parent directory for the source clones. The workspace's .gitignore excludes
# ./sources/ — clone there if you want the repos co-located with the workspace.
mkdir -p sources && cd sources

# Order matters — install from the bottom of the dependency chain up.
git clone https://github.com/rhayes777/PyAutoConf.git
git clone https://github.com/Jammy2211/PyAutoArray.git
git clone https://github.com/rhayes777/PyAutoFit.git
git clone https://github.com/Jammy2211/PyAutoGalaxy.git
git clone https://github.com/Jammy2211/PyAutoLens.git

cd ..

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

for repo in PyAutoConf PyAutoArray PyAutoFit PyAutoGalaxy PyAutoLens; do
    pip install -e "sources/$repo"
done

# Optional accelerators
pip install numba
```

Resolve git URLs from [`../sources.yaml`](../sources.yaml) so the workspace stays the
source of truth; if you want to change a URL or add a repo, edit `sources.yaml` rather
than hand-editing this skill.

Verify the same way as for pip:

```bash
python -c "import autolens, autofit, autogalaxy, autoarray, autoconf; print(autolens.__version__)"
```

## Sandbox / restricted-filesystem environments

If you're in Codex, a CI container, or anywhere `numba` cannot write to its default
cache, override the cache locations once per shell:

```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache
export MPLCONFIGDIR=/tmp/matplotlib
```

You can also bake them into the venv activation script. See
[`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md) for the full list of env
vars (`PYAUTO_TEST_MODE`, `PYAUTO_SKIP_FIT_OUTPUT`, etc.) and when each one matters.

## Verification — write a one-off script

Save this to `./work/verify_environment.py` and run it:

```python
import autofit as af
import autolens as al
import autolens.plot as aplt

print("autoconf   :", al.aconf.__version__ if hasattr(al, 'aconf') else "ok")
print("autoarray  :", al.__version__)
print("autofit    :", af.__version__)
print("autolens   :", al.__version__)

# A minimal Tracer build — proves the modelling stack is wired up.
tracer = al.Tracer(
    galaxies=[
        al.Galaxy(redshift=0.5, mass=al.mp.Isothermal(centre=(0.0, 0.0), einstein_radius=1.2)),
        al.Galaxy(redshift=1.0, bulge=al.lp.SersicSph(centre=(0.0, 0.0), intensity=1.0, effective_radius=0.5, sersic_index=2.5)),
    ]
)
print("Tracer galaxies:", [g.redshift for g in tracer.galaxies])
```

Run with sandbox env vars set if you need them:

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python work/verify_environment.py
```

If that prints versions and a list of galaxy redshifts (no traceback), the environment
is ready for the rest of the skills.

## Combine — what to do next

Now you can:

- Build a model end-to-end with [`al_build_imaging_model`](./al_build_imaging_model.md)
  (or `al_build_interferometer_model` for visibilities).
- Synthesise a test dataset with [`al_simulate_dataset`](./al_simulate_dataset.md).
- Load and inspect an existing fit's results with
  [`al_load_results`](./al_load_results.md).
- Refresh the wiki against installed sources with
  [`al_update_wiki`](./al_update_wiki.md).

## Further reading

- **General reference** — [RTD: Installation overview](https://pyautolens.readthedocs.io/en/latest/installation/overview.html):
  canonical PyAutoLens installation guide — Python version, JAX/GPU setup,
  dependencies. The conda/pip/source/troubleshooting sub-pages each link from here.
