#!/bin/bash
#
# setup_venv_ral.sh — rebuild the PyAuto_JAX virtual environment on RAL with Python 3.12
#
# Why: the PyAuto source checkouts under /mnt/ral/c4072114/PyAuto require Python >= 3.12
# (every pyproject.toml declares requires-python >= 3.12 and the code uses `int | None`
# annotations), but /mnt/ral/c4072114/venvs/PyAuto_JAX was built with Python 3.9, so every
# job failed on `import autolens` with
#     TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
#
# What it does (run ONCE, on the LOGIN node, which has internet access):
#   1. Finds a Python >= 3.12: $PYTHON if set, else python3.12/3.13 on PATH (load a module
#      first if the cluster provides one), else installs a standalone 3.12 with uv under
#      /mnt/ral/c4072114/.local (no root needed).
#   2. Moves the old venv aside to <venv>_py<old version>_backup and creates a new venv at
#      the SAME path, so mgl_batch.sh, submit_mgl and subhalo_multiband_batch.sh need no edits.
#   3. Installs the third-party dependencies read from the five PyAuto pyproject.toml files
#      (the PyAuto packages themselves stay on PYTHONPATH as source checkouts, as before),
#      plus JAX with CUDA 12 GPU support and numba.
#   4. Appends the PYTHONPATH block to the new venv's bin/activate.
#   5. Imports autolens and prints the JAX version as a check.
#
# Every cache and temporary file goes to the shared disk, never to /home or /tmp.
#
# Usage:
#   bash hpc/setup_venv_ral.sh
#   PYTHON=/path/to/python3.12 bash hpc/setup_venv_ral.sh    # use a specific interpreter
#
set -euo pipefail

BASE=/mnt/ral/c4072114
PYAUTO_SRC="${PYAUTO_SRC:-$BASE/PyAuto}"
VENV="${VENV:-$BASE/venvs/PyAuto_JAX}"
CACHE_ROOT="${CACHE_ROOT:-$BASE/.cache}"
PY_VERSION="${PY_VERSION:-3.12}"
JAX_SPEC='jax[cuda12]>=0.7.0,<0.12.0,!=0.10.*,!=0.11.0'

export XDG_CACHE_HOME="$CACHE_ROOT"
export PIP_CACHE_DIR="$CACHE_ROOT/pip"
export UV_CACHE_DIR="$CACHE_ROOT/uv"
export TMPDIR="$CACHE_ROOT/tmp/setup_venv_$$"
mkdir -p "$PIP_CACHE_DIR" "$UV_CACHE_DIR" "$TMPDIR"
trap 'rm -rf "$TMPDIR"' EXIT

for repo in PyAutoNerves PyAutoFit PyAutoArray PyAutoGalaxy PyAutoLens; do
    if [ ! -f "$PYAUTO_SRC/$repo/pyproject.toml" ]; then
        echo "Missing $PYAUTO_SRC/$repo/pyproject.toml — set PYAUTO_SRC to the folder holding the PyAuto checkouts."
        exit 1
    fi
done

is_new_enough() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null
}

# -------------------------------
# 1. A Python >= 3.12
# -------------------------------
PY=""
if [ -n "${PYTHON:-}" ]; then
    PY="$PYTHON"
else
    for candidate in python3.12 python3.13 python3.14; do
        if command -v "$candidate" >/dev/null 2>&1; then
            PY="$(command -v "$candidate")"
            break
        fi
    done
fi

if [ -z "$PY" ]; then
    echo "No python3.12+ on PATH; installing a standalone Python $PY_VERSION with uv under $BASE/.local"
    UV="$BASE/.local/bin/uv"
    if [ ! -x "$UV" ]; then
        curl -LsSf https://astral.sh/uv/install.sh | \
            env UV_INSTALL_DIR="$BASE/.local/bin" UV_NO_MODIFY_PATH=1 sh
    fi
    export UV_PYTHON_INSTALL_DIR="$BASE/.local/python"
    "$UV" python install "$PY_VERSION"
    PY="$("$UV" python find "$PY_VERSION")"
fi

if ! is_new_enough "$PY"; then
    echo "$PY is $("$PY" --version 2>&1); Python >= 3.12 is required."
    exit 1
fi
echo "Using $PY ($("$PY" --version 2>&1))"

# -------------------------------
# 2. Move the old venv aside and create the new one at the same path
# -------------------------------
if [ -d "$VENV" ]; then
    old_version="$("$VENV/bin/python" -c 'import sys; print(f"{sys.version_info[0]}{sys.version_info[1]}")' 2>/dev/null || echo old)"
    backup="${VENV}_py${old_version}_backup"
    if [ -e "$backup" ]; then
        backup="${backup}_$(date +%Y%m%d%H%M%S)"
    fi
    echo "Moving the existing venv to $backup"
    mv "$VENV" "$backup"
fi

"$PY" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip

# -------------------------------
# 3. Dependencies: read from the PyAuto pyproject.toml files, PyAuto packages excluded
# -------------------------------
"$VENV/bin/python" - "$PYAUTO_SRC" "$TMPDIR/requirements.txt" <<'EOF'
import re
import sys
import tomllib
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
deps = []
for repo in ["PyAutoNerves", "PyAutoFit", "PyAutoArray", "PyAutoGalaxy", "PyAutoLens"]:
    project = tomllib.loads((src / repo / "pyproject.toml").read_text())["project"]
    for dep in project.get("dependencies", []):
        if not re.match(r"auto(nerves|conf|fit|array|galaxy|lens)\b", dep, re.IGNORECASE):
            if dep not in deps:
                deps.append(dep)
out.write_text("\n".join(deps) + "\n")
print(f"{len(deps)} third-party dependencies written to {out}")
EOF

"$VENV/bin/python" -m pip install "$JAX_SPEC"
"$VENV/bin/python" -m pip install -r "$TMPDIR/requirements.txt" numba

# -------------------------------
# 4. PYTHONPATH block in bin/activate (the PyAuto packages run from the source checkouts)
# -------------------------------
cat >> "$VENV/bin/activate" <<EOF

# PyAuto source checkouts (added by hpc/setup_venv_ral.sh)
export PYTHONPATH=$PYAUTO_SRC/autolens_workspace:$PYAUTO_SRC/PyAutoNerves:$PYAUTO_SRC/PyAutoFit:$PYAUTO_SRC/PyAutoArray:$PYAUTO_SRC/PyAutoGalaxy:$PYAUTO_SRC/PyAutoLens
EOF

# -------------------------------
# 5. Check
# -------------------------------
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python - <<'EOF'
import sys
import jax
import autolens as al
print(f"Python {sys.version.split()[0]}, autolens {al.__version__}, jax {jax.__version__}")
print("JAX devices here (CPU on the login node; a GPU node lists cuda devices):", jax.devices())
EOF

echo "Done. New venv: $VENV"
echo "Check JAX sees the GPU on a GPU node with:"
echo "  srun --partition=gpu --gres=gpu:1 --time=00:10:00 bash -c 'export XDG_CACHE_HOME=$CACHE_ROOT; source $VENV/bin/activate && python -c \"import jax; print(jax.devices())\"'"
