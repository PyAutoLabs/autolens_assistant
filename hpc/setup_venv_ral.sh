#!/bin/bash
#
# setup_venv_ral.sh — rebuild the PyAuto_JAX virtual environment on RAL with Python 3.12
#
# Why: the PyAuto source checkouts declare requires-python >= 3.12. On the old Python 3.9 venv
# every job failed on `import autolens` with
#     TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
# from PyAutoArray/autoarray/inversion/mesh/mesh/delaunay_nn.py:52 (`zeroed_pixels: int | None`,
# added 2026-08-09, commit ab5cc66d) — currently the only construct in the five repos that
# Python 3.9 cannot import, but the project now targets 3.12 and more will follow.
#
# The interpreter must live on the SHARED disk. A venv's bin/python is only a link to the
# Python it was built from; a venv built from the login node's /usr/bin/python3.12 works on
# the login node, but on the GPU nodes that file does not exist, bash falls through to the
# node's system python, and every job fails with `No module named 'jax'`.
#
# What it does (run ONCE, on the LOGIN node, which has internet access):
#   1. Installs a standalone Python 3.12 with uv under /mnt/ral/c4072114/.local/python (no
#      root needed; visible from every node), or uses $PYTHON if that is on the shared disk.
#   2. If the venv already runs Python >= 3.12 from an interpreter on the shared disk it is
#      reused (a re-run only tops up packages, from the pip cache). Otherwise the old venv is
#      moved aside to <venv>_py<old version>_backup and a new one is created at the SAME path,
#      so mgl_batch.sh, submit_mgl and subhalo_multiband_batch.sh need no edits.
#   3. Installs the third-party dependencies read from the five PyAuto pyproject.toml files
#      (the PyAuto packages themselves stay on PYTHONPATH as source checkouts, as before),
#      plus JAX with CUDA 12 GPU support and numba.
#   4. Appends the PYTHONPATH block to the venv's bin/activate (once).
#   5. Imports autolens and JAX on the CPU as a check. The first import reads thousands of
#      files from the network disk and can take several minutes; let it finish.
#
# Every cache and temporary file goes to the shared disk, never to /home or /tmp.
#
# Usage:
#   bash hpc/setup_venv_ral.sh
#   PYTHON=/mnt/ral/.../python3.12 bash hpc/setup_venv_ral.sh   # a specific shared-disk Python
#
set -euo pipefail

BASE="${BASE:-/mnt/ral/c4072114}"
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

# True when the interpreter a path finally resolves to (following the venv's symlinks) is on
# the shared disk, i.e. reachable from the GPU nodes as well as the login node.
on_shared_disk() {
    case "$(readlink -f "$1")" in
        "$BASE"/*) return 0 ;;
        *) return 1 ;;
    esac
}

REUSE_VENV=0
if [ -x "$VENV/bin/python" ] && is_new_enough "$VENV/bin/python" && on_shared_disk "$VENV/bin/python"; then
    REUSE_VENV=1
fi

# -------------------------------
# 1. A Python >= 3.12 on the shared disk (only needed when the venv has to be created)
# -------------------------------
PY=""
if [ "$REUSE_VENV" -eq 1 ]; then
    PY="$VENV/bin/python"
elif [ -n "${PYTHON:-}" ]; then
    PY="$PYTHON"
    if ! on_shared_disk "$PY"; then
        echo "$PY resolves to $(readlink -f "$PY"), which is not under $BASE."
        echo "The GPU nodes cannot run it. Unset PYTHON to install a standalone Python with uv."
        exit 1
    fi
else
    echo "Installing a standalone Python $PY_VERSION with uv under $BASE/.local/python"
    UV="$BASE/.local/bin/uv"
    if [ ! -x "$UV" ]; then
        curl -LsSf https://astral.sh/uv/install.sh | \
            env UV_INSTALL_DIR="$BASE/.local/bin" UV_NO_MODIFY_PATH=1 sh
    fi
    export UV_PYTHON_INSTALL_DIR="$BASE/.local/python"
    # only-managed: never pick the login node's /usr/bin/python3.12.
    export UV_PYTHON_PREFERENCE=only-managed
    "$UV" python install "$PY_VERSION"
    PY="$("$UV" python find "$PY_VERSION")"
fi

if ! is_new_enough "$PY"; then
    echo "$PY is $("$PY" --version 2>&1); Python >= 3.12 is required."
    exit 1
fi
if ! on_shared_disk "$PY"; then
    echo "$PY resolves to $(readlink -f "$PY"), which is not under $BASE; the GPU nodes cannot run it."
    exit 1
fi
echo "Using $PY -> $(readlink -f "$PY") ($("$PY" --version 2>&1))"

# -------------------------------
# 2. Reuse a shared-disk Python >= 3.12 venv, or move the old venv aside and create a new one
# -------------------------------
if [ "$REUSE_VENV" -eq 1 ]; then
    echo "Reusing the existing venv at $VENV (Python >= 3.12 on the shared disk)"
elif [ -d "$VENV" ]; then
    if [ -x "$VENV/bin/python" ] && is_new_enough "$VENV/bin/python"; then
        echo "The existing venv uses $(readlink -f "$VENV/bin/python"), which the GPU nodes cannot run; rebuilding it."
    fi
    old_version="$("$VENV/bin/python" -c 'import sys; print(f"{sys.version_info[0]}{sys.version_info[1]}")' 2>/dev/null || echo old)"
    backup="${VENV}_py${old_version}_backup"
    if [ -e "$backup" ]; then
        backup="${backup}_$(date +%Y%m%d%H%M%S)"
    fi
    echo "Moving the existing venv to $backup"
    mv "$VENV" "$backup"
fi

if [ "$REUSE_VENV" -eq 0 ]; then
    "$PY" -m venv "$VENV"
fi
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
if ! grep -q "added by hpc/setup_venv_ral.sh" "$VENV/bin/activate"; then
    cat >> "$VENV/bin/activate" <<EOF

# PyAuto source checkouts (added by hpc/setup_venv_ral.sh)
export PYTHONPATH=$PYAUTO_SRC/autolens_workspace:$PYAUTO_SRC/PyAutoNerves:$PYAUTO_SRC/PyAutoFit:$PYAUTO_SRC/PyAutoArray:$PYAUTO_SRC/PyAutoGalaxy:$PYAUTO_SRC/PyAutoLens
EOF
fi

# -------------------------------
# 5. Check, on the CPU: the login node has no GPU, and JAX_PLATFORMS=cpu stops the CUDA plugin
#    searching for one. The first import reads thousands of files (numpy, scipy, JAX and its
#    CUDA libraries, the PyAuto source) from the network disk and can take several minutes.
# -------------------------------
# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "Checking the install (the first import on the shared disk can take several minutes)..."
SECONDS=0
JAX_PLATFORMS=cpu python - <<'EOF'
import sys
import jax
import autolens as al
print(f"Python {sys.version.split()[0]}, autolens {al.__version__}, jax {jax.__version__}")
print("JAX devices (CPU-only check):", jax.devices())
EOF
echo "Import check took ${SECONDS}s"

echo "Done. New venv: $VENV"
echo "Check JAX sees the GPU on a GPU node with:"
echo "  srun --partition=gpu --gres=gpu:1 --time=00:10:00 bash -c 'export XDG_CACHE_HOME=$CACHE_ROOT; source $VENV/bin/activate && python -c \"import jax; print(jax.devices())\"'"
