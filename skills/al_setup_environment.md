---
name: al_setup_environment
description: Detect, install, and configure a Python environment for the PyAuto* lensing stack. First checks the active interpreter and distinguishes an absent, broken, or ready stack; then offers pip in a venv (the normal user path) or editable clones (contributors). Sets sandbox cache env vars and verifies imports. Use when PyAutoLens is unavailable, imports fail, or a new machine needs setup.
---

# Setting up an environment for the PyAuto\* stack

This skill installs the libraries the workspace targets — PyAutoConf, PyAutoArray, PyAutoFit,
PyAutoGalaxy, PyAutoLens — and prepares the sandbox so the rest of the skills will run.
The user picks one of two install modes only if the active environment is not already usable:
pip (fastest path to "import autolens works") or editable-clone (source-level access, slower
but lets you read and modify the libraries). Never install automatically without confirmation.

## Orient — inspect before installing

If the project has an `activate.sh`, source it first. Then run the cheap structured preflight:

```bash
python autoassistant/audit_skill_apis.py --check-install
```

It reports the active Python executable and environment prefix, installed versions, the loaded
`autolens` path, and a best-effort install type. Its exit codes are:

- `0` — all five PyAuto\* roots import; do not reinstall.
- `2` — packages are absent from this interpreter. The user may only need to activate the right
  environment, so check that before creating another one.
- `3` — packages were found but imports failed. Fix the reported dependency, cache, or partial
  installation error rather than treating it as ordinary version drift.

The probe supplies writable temporary defaults for numba and matplotlib caches when the user has
not configured them, preventing a read-only cache from being misreported as a missing install.
If the install is ready, continue to the user's actual lensing task. Only continue below when
setup or repair is genuinely required.

## Ask

Before changing the environment, confirm with the user:

- Are you running on macOS, Linux, or Windows / WSL?
- Do you already have a Python environment manager (venv, conda, mamba)? If yes, will
  you use it for this workspace too?
- Do you need to *read or modify* the PyAuto\* source while you work (editable clone
  mode), or just *use* the libraries (pip mode)?

Recommend a venv plus pip for most users. If they already use conda or mamba, it is fine to
create/activate the environment with that tool and then install PyAutoLens with pip inside it;
do not introduce conda solely for this package. Use editable clones only when they need source
access. If they pick pip, branch into "Pip install". If they want editable clones, branch into
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

Python ≥ 3.9 works in principle (all five repos declare `requires-python = ">=3.9"`)
and JAX runs on every supported version including 3.10. 3.11 is the recommended
baseline — it's what the workspace tooling targets and what the JAX wheels are
best-tested against, so 3.10 works but is suboptimal. If an env on 3.10 reports
JAX as unavailable, treat it as a wheel mismatch in that env, not a stack-wide
incompatibility.

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
# URLs come from ../sources.yaml (the PyAutoLabs org is canonical; the old
# rhayes777/Jammy2211 URLs still redirect but should not be written anew).
git clone https://github.com/PyAutoLabs/PyAutoConf.git
git clone https://github.com/PyAutoLabs/PyAutoArray.git
git clone https://github.com/PyAutoLabs/PyAutoFit.git
git clone https://github.com/PyAutoLabs/PyAutoGalaxy.git
git clone https://github.com/PyAutoLabs/PyAutoLens.git

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

Save this to `scripts/verify_environment.py` and run it:

```python
import autoconf
import autoarray
import autofit as af
import autogalaxy as ag
import autolens as al
import autolens.plot as aplt

print("autoconf   :", autoconf.__version__)
print("autoarray  :", autoarray.__version__)
print("autofit    :", af.__version__)
print("autogalaxy :", ag.__version__)
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
  python scripts/verify_environment.py
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
