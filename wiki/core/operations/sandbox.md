---
title: Sandbox and restricted-environment configuration
sources:
  - project: PyAutoNerves
    paths: [autonerves/jax_wrapper.py]
    pinned_commit: main
  - project: autolens_workspace
    paths: [CLAUDE.md, README.md]
    pinned_commit: main
last_updated: 2026-05-22
---

# Sandbox / restricted-environment configuration

PyAuto\* libraries write cache files (numba JIT compilation, matplotlib config) to
the user's home directory by default. In sandboxed environments — Codex, CI
containers, read-only home filesystems, the `/mnt/c/` Windows mount under WSL — those
default paths fail, often with confusing messages buried inside numba traces.

The fix is a handful of environment variables.

## Mandatory in sandboxed environments

```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache
export MPLCONFIGDIR=/tmp/matplotlib
```

`NUMBA_CACHE_DIR` controls where numba puts its compiled function cache. Default is
inside each module's `__pycache__/` directory, which fails when the install lives on
a read-only or unwritable filesystem.

`MPLCONFIGDIR` controls where matplotlib puts its config (font cache, style sheets).
Default is `~/.config/matplotlib` (Linux) or equivalent.

Set them once per shell or bake into your venv activation script.

## Smoke testing without real sampling — `PYAUTO_TEST_MODE`

PyAutoLens (and the workspace) honour `PYAUTO_TEST_MODE` to short-circuit
non-linear sampling for fast end-to-end script verification:

```bash
PYAUTO_TEST_MODE=1 python scripts/your_script.py
```

In test mode 1, the search returns after a small number of likelihood evaluations,
so the script completes and you can verify it ran. The returned `Result` is not
physically meaningful — don't trust the parameter values.

For even faster smokes when iterating on the script itself:

```bash
PYAUTO_TEST_MODE=2 \
  PYAUTO_SKIP_FIT_OUTPUT=1 \
  PYAUTO_SKIP_VISUALIZATION=1 \
  PYAUTO_SKIP_CHECKS=1 \
  PYAUTO_SMALL_DATASETS=1 \
  PYAUTO_FAST_PLOTS=1 \
  python scripts/your_script.py
```

Flags:

- **`PYAUTO_TEST_MODE=2`** — even more aggressive short-circuit than mode 1.
- **`PYAUTO_SKIP_FIT_OUTPUT=1`** — don't write the FITS / JSON / CSV products at
  end-of-fit. Use when you only care that the fit ran.
- **`PYAUTO_SKIP_VISUALIZATION=1`** — don't render diagnostic plots during the fit.
- **`PYAUTO_SKIP_CHECKS=1`** — skip runtime sanity checks (e.g. that a mask is
  non-empty).
- **`PYAUTO_SMALL_DATASETS=1`** — cap all grids / masks to 15×15 pixels at 0.6"/px,
  making simulators and downstream computations dramatically faster. **Delete
  `dataset/` when toggling this flag** so old large datasets don't get re-used.
- **`PYAUTO_FAST_PLOTS=1`** — skip `plt.tight_layout()` and critical-curve / caustic
  overlay computation in subplot functions.

In a real lensing run, leave all six unset. They're for the inner loop of "is this
script syntactically correct?", not for production fits.

## Workspace skip-flag

When running scripts inside a `workspace/lens`-style clone, a separate flag exists:

```bash
PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1 python work/your_script.py
```

This silences the "your workspace version doesn't match the installed PyAutoLens"
warning, which becomes noise in CI but is informative locally.

## When environment isolation matters

If multiple agents (Claude Code, Codex, GitHub Actions) might run in the same
working directory concurrently, point each at its own cache and output directory:

```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache_$$
export MPLCONFIGDIR=/tmp/matplotlib_$$
```

The `$$` expands to the process PID so each shell gets a unique cache. Without this
two agents can race to write the same numba JIT artefact and corrupt each other's
caches.

## See also

- [`al_setup_environment`](../../../skills/al_setup_environment.md) — the skill that
  applies these env vars.
- [`operations/installation`](./installation.md).
- [`operations/hpc`](./hpc.md).
