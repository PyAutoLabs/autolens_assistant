#!/bin/bash -l

#SBATCH -J mgl_q1
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

# NOTE: --array is deliberately NOT set here. It is set at submit time by
# submit_mgl_batch.sh (via `sbatch --array=0-N-1%MAX_CONCURRENT`), because N
# depends on how many datasets currently exist in dataset/euclid_q1.

cd /mnt/ral/c4072114/PyAuto/autolens_base_project

# -------------------------------
# Environment
# -------------------------------
source /mnt/ral/c4072114/venvs/PyAuto_JAX/bin/activate
export JAX_ENABLE_X64=True

# -------------------------------
# Look up which dataset this array task should run
# -------------------------------
DATASET_LIST="dataset_lists/euclid_q1_datasets.txt"

if [ ! -f "$DATASET_LIST" ]; then
    echo "Dataset list $DATASET_LIST not found. Run submit_mgl_batch.sh first."
    exit 1
fi

# SLURM_ARRAY_TASK_ID is 0-indexed, sed lines are 1-indexed
dataset=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$DATASET_LIST")

if [ -z "$dataset" ]; then
    echo "No dataset found for array index $SLURM_ARRAY_TASK_ID in $DATASET_LIST"
    exit 1
fi

echo "=========================================="
echo "Array job index: $SLURM_ARRAY_TASK_ID"
echo "Dataset: $dataset"
date
nvidia-smi

# -------------------------------
# Run the analysis script for this dataset.
#
# pixel_scale, mask_radius and mask_centre are read from
# dataset/euclid_q1/$dataset/info.json automatically inside mgl_slam.py.
# -------------------------------
python3 /mnt/ral/c4072114/PyAuto/autolens_base_project/scripts/group/mgl_slam.py --dataset=$dataset

echo "Finished dataset: $dataset"
date
