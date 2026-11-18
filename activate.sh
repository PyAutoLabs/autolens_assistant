# Activate the Python environment that has PyAutoLens installed.
#
# Most users just `pip install autolens` (see the al_setup_environment skill) into a
# virtual environment. By default this looks for a `.venv` created inside the project
# (what al_setup_environment makes); edit VENV to point elsewhere, e.g. ~/venv/PyAuto.
#
# Resolving relative to this file (not the current directory) means it works both for a
# local `source activate.sh` and for the HPC scripts' `source $PROJECT_PATH/activate.sh`.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV=$HERE/.venv

if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
elif [ -n "${PYAUTO_HPC_BASE:-}" ] && [ -f "$PYAUTO_HPC_BASE/PyAuto/bin/activate" ]; then
    # Shared / HPC checkout: point PYAUTO_HPC_BASE at the directory that holds a
    # `PyAuto/` virtualenv alongside editable PyAuto* source checkouts, e.g.
    #   export PYAUTO_HPC_BASE=/path/to/your/PyAuto
    BASE="$PYAUTO_HPC_BASE"
    source "$BASE/PyAuto/bin/activate"
    export PYTHONPATH=$BASE:\
$BASE/PyAutoNerves:\
$BASE/PyAutoFit:\
$BASE/PyAutoArray:\
$BASE/PyAutoGalaxy:\
$BASE/PyAutoLens
    # --- Keep caches OFF $HOME on HPC ---------------------------------------
    # On many clusters (RAL: every node) /home sits on a small root disk, so tools that
    # default to ~/.cache — the PyAutoNerves JAX compile cache (~/.cache/pyauto_jax), pip,
    # matplotlib, numba, CUDA/Triton kernels — fill it and break the node (RAL admin,
    # 2026-09-25). Send them to the shared project filesystem instead: by default a
    # `.cache/` next to PYAUTO_HPC_BASE (override with PYAUTO_HPC_CACHE). Only unset
    # variables are filled, so a submit script's own JAX_COMPILATION_CACHE_DIR still wins
    # (and an explicitly EMPTY one still disables the JAX cache). Laptop `.venv` users
    # never reach this branch.
    export PYAUTO_HPC_CACHE="${PYAUTO_HPC_CACHE:-$(dirname "$PYAUTO_HPC_BASE")/.cache}"
    mkdir -p "$PYAUTO_HPC_CACHE" 2>/dev/null || true
    export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$PYAUTO_HPC_CACHE}"
    export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$PYAUTO_HPC_CACHE/pip}"
    export MPLCONFIGDIR="${MPLCONFIGDIR:-$PYAUTO_HPC_CACHE/matplotlib}"
    export NUMBA_CACHE_DIR="${NUMBA_CACHE_DIR:-$PYAUTO_HPC_CACHE/numba}"
    export CUDA_CACHE_PATH="${CUDA_CACHE_PATH:-$PYAUTO_HPC_CACHE/nv}"
    export TRITON_CACHE_DIR="${TRITON_CACHE_DIR:-$PYAUTO_HPC_CACHE/triton}"
    export JAX_COMPILATION_CACHE_DIR="${JAX_COMPILATION_CACHE_DIR-$PYAUTO_HPC_CACHE/pyauto_jax}"
    export ASTROPY_CACHE_DIR="${ASTROPY_CACHE_DIR:-$PYAUTO_HPC_CACHE/astropy}"
    # Temp files too: Python's tempfile, JAX and numba default to /tmp, which on RAL
    # compute nodes sits on the same small local disk (RAL admin, 2026-11-12). Use a
    # `tmp/` next to the cache instead.
    # Slurm sets TMPDIR=/tmp itself when the job environment has none, so /tmp counts
    # as unset here; any other TMPDIR (e.g. a job's own scratch dir) wins.
    if [ -z "${TMPDIR:-}" ] || [ "$TMPDIR" = /tmp ]; then
        export TMPDIR="$(dirname "$PYAUTO_HPC_CACHE")/tmp"
    fi
    mkdir -p "$TMPDIR" 2>/dev/null || true
    # CPU jobs: the shared venv ships JAX's CUDA plugin, which on a GPU-less node fails
    # cuInit and logs an ERROR + traceback before JAX falls back to the CPU (RAL,
    # 2026-11-13). Pin the CPU when the job holds no GPU — Slurm sets SLURM_JOB_GPUS,
    # SLURM_GPUS_ON_NODE and CUDA_VISIBLE_DEVICES for a --gres=gpu job — and an
    # explicit JAX_PLATFORMS always wins.
    if [ -z "${JAX_PLATFORMS:-}" ] && [ -z "${SLURM_JOB_GPUS:-}${SLURM_GPUS_ON_NODE:-}${CUDA_VISIBLE_DEVICES:-}" ]; then
        export JAX_PLATFORMS=cpu
        echo "activate.sh: no GPU in this job, JAX_PLATFORMS=cpu" >&2
    fi
else
    echo "No local .venv found (set PYAUTO_HPC_BASE for a shared/HPC PyAuto checkout)." >&2
fi

# Developer setup only: if you run against editable source checkouts of the PyAuto*
# libraries instead of a pip install, drop the line above and add their parent directory
# to PYTHONPATH, e.g.:
#
#   SRC=~/Code/PyAutoLabs
#   export PYTHONPATH=$SRC:\
#   $SRC/PyAutoNerves:\
#   $SRC/PyAutoFit:\
#   $SRC/PyAutoArray:\
#   $SRC/PyAutoGalaxy:\
#   $SRC/PyAutoLens
