#!/bin/bash -l

#SBATCH -J subhalo_mb
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32gb
#SBATCH --time=70:00:00
#SBATCH -o output/output.%A_%a.out
#SBATCH -e error/error.%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=c4072114@newcastle.ac.uk

# One arm of the multi-band subhalo experiment per SLURM array task:
# scripts/subhalo_multiband/subhalo_multiband_slam.py runs every stage for one
# (dataset type, band set) — source_lp[1], source_pix[1], source_pix[2], light[1],
# mass_total[1], subhalo[1], the subhalo[2] grid search and subhalo[3] — and writes
# output/subhalo_multiband/<dataset>/<dataset_type>/<bands>/detection/detection_summary.json.
#
# Don't sbatch this file directly. submit_subhalo_multiband.sh writes the arm list
# and submits this script with `--array` and `--export=...,DATASET=...,ARM_LIST=...`,
# then queues the MODE=compare task that tabulates every arm once the array ends.
#
# Every search is resumable: if a task hits the time limit, resubmitting the same
# arm continues from the completed searches and the last sampler checkpoint.

PROJECT_DIR="${PROJECT_DIR:-/mnt/ral/c4072114/PyAuto/autolens_assistant}"
VENV="${VENV:-/mnt/ral/c4072114/venvs/PyAuto_JAX}"
CACHE_ROOT="${CACHE_ROOT:-/mnt/ral/c4072114/.cache}"
SCRIPT="$PROJECT_DIR/scripts/subhalo_multiband/subhalo_multiband_slam.py"

# The pipeline reads dataset/, config/ and writes output/ relative to the project root.
cd "$PROJECT_DIR"

# -------------------------------
# Environment
# -------------------------------
source "$VENV/bin/activate"
export JAX_ENABLE_X64=True

# -------------------------------
# Caches and temporary files on the shared disk, never on the node's OS disk.
#
# The worker nodes have tiny OS disks, which hold both /home and /tmp. Every tool
# that defaults to ~/.cache, ~/.config or /tmp (pip, matplotlib, numba, CUDA,
# Triton, the PyAuto JAX compile cache, astropy) is sent to $CACHE_ROOT on the
# shared disk instead. The JAX compile cache is shared between jobs, so later
# arms reuse earlier compilations. TMPDIR is private to this job and removed on
# exit.
# -------------------------------
export XDG_CACHE_HOME="$CACHE_ROOT"
export XDG_CONFIG_HOME="$CACHE_ROOT/config"
export PIP_CACHE_DIR="$CACHE_ROOT/pip"
export MPLCONFIGDIR="$CACHE_ROOT/matplotlib"
export NUMBA_CACHE_DIR="$CACHE_ROOT/numba"
export CUDA_CACHE_PATH="$CACHE_ROOT/nv"
export TRITON_CACHE_DIR="$CACHE_ROOT/triton"
export JAX_COMPILATION_CACHE_DIR="$CACHE_ROOT/pyauto_jax"
export ASTROPY_CACHE_DIR="$CACHE_ROOT/astropy"
export TMPDIR="$CACHE_ROOT/tmp/${SLURM_JOB_ID:-$$}"

mkdir -p "$XDG_CONFIG_HOME" "$PIP_CACHE_DIR" "$MPLCONFIGDIR" "$NUMBA_CACHE_DIR" \
    "$CUDA_CACHE_PATH" "$TRITON_CACHE_DIR" "$JAX_COMPILATION_CACHE_DIR" \
    "$ASTROPY_CACHE_DIR" "$TMPDIR"
trap 'rm -rf "$TMPDIR"' EXIT

DATASET="${DATASET:-jwst_pl_sersic_two_band}"

# -------------------------------
# Compare task: tabulate every completed arm and exit.
# -------------------------------
if [ "${MODE:-arm}" = "compare" ]; then
    echo "Comparing detection summaries for $DATASET"
    python3 "$SCRIPT" --dataset="$DATASET" --compare
    exit $?
fi

# -------------------------------
# Look up which arm this array task runs
# -------------------------------
if [ -z "${ARM_LIST:-}" ] || [ ! -f "$ARM_LIST" ]; then
    echo "ARM_LIST is not set or missing. Submit via submit_subhalo_multiband.sh <dataset_name>."
    exit 1
fi

# SLURM_ARRAY_TASK_ID is 0-indexed, sed lines are 1-indexed. Each line is
# "<dataset_type> <bands>", e.g. "subhalo_m10 F150W,F444W".
entry=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$ARM_LIST")

if [ -z "$entry" ]; then
    echo "No arm found for array index $SLURM_ARRAY_TASK_ID in $ARM_LIST"
    exit 1
fi

read -r dataset_type bands <<< "$entry"

echo "=========================================="
echo "Array job index: $SLURM_ARRAY_TASK_ID"
echo "Dataset: $DATASET"
echo "Dataset type: $dataset_type"
echo "Bands: $bands"
echo "Extra arguments: ${EXTRA_ARGS:-<none>}"
echo "Cache root: $CACHE_ROOT"
date
nvidia-smi

# Name the task "<dataset_type>-<bands>" so squeue shows which arm is running.
scontrol update JobId="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}" \
    JobName="${dataset_type}-${bands//,/+}" || true

# EXTRA_ARGS passes options such as --max_rotation=5 or --fixed_alignment through
# to the pipeline, identically for every arm. It is deliberately unquoted so that
# several options split into separate arguments.
# shellcheck disable=SC2086
python3 "$SCRIPT" \
    --dataset="$DATASET" \
    --dataset_type="$dataset_type" \
    --bands="$bands" \
    ${EXTRA_ARGS:-}

status=$?

echo "Finished arm: $dataset_type $bands (exit $status)"
date

exit $status
