#!/bin/bash
#SBATCH -J subhalo_mb_submit
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --time=00:10:00
#SBATCH -o output/submit.%j.out
#SBATCH -e error/submit.%j.err
#
# submit_subhalo_multiband.sh
#
# Submits the whole multi-band subhalo experiment for one simulated dataset:
#
#   1. Lists every arm = (dataset type) x (band set) into an arm-list file. By
#      default the dataset types are every subdirectory of
#      dataset/imaging/<dataset_name>/ that holds a wavebands/ folder (e.g.
#      subhalo_m10, no_subhalo), and the band sets are each band on its own plus
#      all bands jointly (e.g. F150W, F444W, F150W,F444W).
#   2. Submits subhalo_multiband_batch.sh as a SLURM array, one GPU task per arm.
#      Each task runs every pipeline stage (SLaM + SUBHALO PIPELINE) for its arm.
#   3. Queues one MODE=compare task with --dependency=afterany on the array, which
#      prints the Delta ln Z table of every arm that completed.
#
# It does no modelling itself, so it needs no GPU (--gres is deliberately not
# set). Like submit_mgl_batch.sh it can be run directly or through sbatch.
#
# Usage (from hpc/batch_gpu/, so the #SBATCH -o/-e paths above resolve):
#   sbatch submit_subhalo_multiband.sh <dataset_name> [dataset_type ...]
#   bash   submit_subhalo_multiband.sh <dataset_name> [dataset_type ...]
#
# Examples:
#   sbatch submit_subhalo_multiband.sh jwst_pl_sersic_two_band
#   sbatch submit_subhalo_multiband.sh jwst_pl_sersic_two_band subhalo_m10
#
# From your local machine, through hpc/sync (which places sbatch options before
# the script name, so the dataset is passed as an environment variable instead):
#   hpc/sync push-submit gpu submit_subhalo_multiband.sh --export=ALL,DATASET=jwst_pl_sersic_two_band
#
# Optional environment overrides (pass with `sbatch --export=ALL,NAME=...` or
# set them before `bash`):
#   DATASET         dataset name, used when no positional argument is given
#   DATASET_TYPES   space-separated dataset types, used when none are given as
#                   arguments (default: every subdirectory with a wavebands/ folder)
#   BAND_SETS       space-separated band sets, the first band of each set being its
#                   astrometric reference, e.g. "F150W F444W F150W,F444W"
#   EXTRA_ARGS      options passed to every arm, e.g. "--max_rotation=5" or
#                   "--fixed_alignment --grid_steps=4"
#   MAX_CONCURRENT  maximum arms running at once (default 6)
#   PROJECT_DIR     project root on the cluster
#
set -euo pipefail

if [ $# -ge 1 ]; then
    DATASET="${1%/}"
    shift
elif [ -n "${DATASET:-}" ]; then
    DATASET="${DATASET%/}"
    # Dataset types from the environment, when submitted through hpc/sync.
    if [ -n "${DATASET_TYPES:-}" ]; then
        read -r -a _types <<< "$DATASET_TYPES"
        set -- "${_types[@]}"
    fi
else
    echo "Usage: $0 <dataset_name> [dataset_type ...]   (or set DATASET / DATASET_TYPES)"
    echo "  e.g. $0 jwst_pl_sersic_two_band"
    exit 1
fi

if [ $# -gt 0 ]; then
    set -- "${@%/}"
fi

PROJECT_DIR="${PROJECT_DIR:-/mnt/ral/c4072114/PyAuto/autolens_assistant}"
DATASET_ROOT="$PROJECT_DIR/dataset/imaging/$DATASET"
LIST_DIR="$PROJECT_DIR/hpc/batch_gpu/output/arm_lists"
ARRAY_SCRIPT="$PROJECT_DIR/hpc/batch_gpu/subhalo_multiband_batch.sh"
LOG_DIR="$PROJECT_DIR/hpc/batch_gpu"
MAX_CONCURRENT="${MAX_CONCURRENT:-6}"

if [ ! -d "$DATASET_ROOT" ]; then
    echo "Dataset directory not found: $DATASET_ROOT"
    exit 1
fi

mkdir -p "$LIST_DIR" "$LOG_DIR/output" "$LOG_DIR/error"

# -------------------------------
# Dataset types
# -------------------------------
if [ $# -gt 0 ]; then
    DATASET_TYPES=("$@")
else
    DATASET_TYPES=()
    for d in "$DATASET_ROOT"/*/; do
        [ -d "$d/wavebands" ] && DATASET_TYPES+=("$(basename "$d")")
    done
fi

if [ ${#DATASET_TYPES[@]} -eq 0 ]; then
    echo "No dataset types (subdirectories with a wavebands/ folder) in $DATASET_ROOT"
    exit 1
fi

# -------------------------------
# Band sets: each band alone, plus all bands jointly (bands sorted by name, so
# the first is the reference band of the joint fit). Override with BAND_SETS.
# -------------------------------
if [ -n "${BAND_SETS:-}" ]; then
    read -r -a BAND_SET_LIST <<< "$BAND_SETS"
else
    BANDS=()
    for d in "$DATASET_ROOT/${DATASET_TYPES[0]}/wavebands"/*/; do
        [ -d "$d" ] && BANDS+=("$(basename "$d")")
    done
    BAND_SET_LIST=("${BANDS[@]}")
    if [ ${#BANDS[@]} -gt 1 ]; then
        BAND_SET_LIST+=("$(IFS=,; echo "${BANDS[*]}")")
    fi
fi

# -------------------------------
# Arm list. An arm is kept only if every band of its set has the files the
# pipeline loads; the reference (first) band also needs positions.json.
# -------------------------------
TAG="$DATASET$(printf "_%s" "${DATASET_TYPES[@]}")"
LIST_FILE="$LIST_DIR/${TAG}_arms.txt"
: > "$LIST_FILE"

for dataset_type in "${DATASET_TYPES[@]}"; do
    for band_set in "${BAND_SET_LIST[@]}"; do
        ok=1
        IFS=, read -r -a set_bands <<< "$band_set"
        for band in "${set_bands[@]}"; do
            band_dir="$DATASET_ROOT/$dataset_type/wavebands/$band"
            for f in data.fits noise_map.fits psf.fits info.json; do
                [ -f "$band_dir/$f" ] || ok=0
            done
        done
        [ -f "$DATASET_ROOT/$dataset_type/wavebands/${set_bands[0]}/positions.json" ] || ok=0

        if [ $ok -eq 1 ]; then
            echo "$dataset_type $band_set" >> "$LIST_FILE"
        else
            echo "Skipping $dataset_type $band_set: missing data/noise_map/psf/info.json or positions.json"
        fi
    done
done

N=$(wc -l < "$LIST_FILE")

if [ "$N" -eq 0 ]; then
    echo "No runnable arms for $DATASET"
    exit 1
fi

echo "Arms for $DATASET (see $LIST_FILE):"
cat "$LIST_FILE"
echo "Extra arguments: ${EXTRA_ARGS:-<none>}"
echo "=========================================="
echo "Submitting array 0-$((N - 1))%${MAX_CONCURRENT}"

# EXTRA_ARGS reaches the tasks through --export=ALL rather than as a NAME=value
# entry, because sbatch splits --export values on commas.
export EXTRA_ARGS="${EXTRA_ARGS:-}"

ARRAY_JOB_ID=$(sbatch --parsable \
    --array=0-$((N - 1))%${MAX_CONCURRENT} \
    --output="$LOG_DIR/output/output.%A_%a.out" \
    --error="$LOG_DIR/error/error.%A_%a.err" \
    --export=ALL,PROJECT_DIR="$PROJECT_DIR",DATASET="$DATASET",ARM_LIST="$LIST_FILE",MODE=arm \
    "$ARRAY_SCRIPT")

ARRAY_JOB_ID="${ARRAY_JOB_ID%%;*}"
echo "Array job: $ARRAY_JOB_ID"

# The compare task runs after every arm has ended (afterany: also when some
# failed), and only reads the detection summaries, so it needs little time or
# memory.
COMPARE_JOB_ID=$(sbatch --parsable \
    --dependency=afterany:"$ARRAY_JOB_ID" \
    -J subhalo_mb_compare \
    --time=00:15:00 \
    --mem=4gb \
    --output="$LOG_DIR/output/compare.%j.out" \
    --error="$LOG_DIR/error/compare.%j.err" \
    --export=ALL,PROJECT_DIR="$PROJECT_DIR",DATASET="$DATASET",MODE=compare \
    "$ARRAY_SCRIPT")

echo "Compare job: ${COMPARE_JOB_ID%%;*} (runs after array $ARRAY_JOB_ID; table in $LOG_DIR/output/compare.${COMPARE_JOB_ID%%;*}.out)"
