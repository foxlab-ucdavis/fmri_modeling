#!/bin/bash
#SBATCH -p production
#SBATCH --array=1-7  # Update to the number of data chunks you have
#SBATCH --job-name=firstlvl_timeseries
#SBATCH --output=slurm_logs/firstlvl_%A_%a.out
#SBATCH --error=slurm_logs/firstlvl_%A_%a.err
#SBATCH --time=30:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G

# Print environment information
env

# === CONFIGURATION ===
BASE_DIR="/share/foxlab-backedup/kaline_fconn"
CHUNK_DIR="${BASE_DIR}/data/external/timeseries_hires_allfiles/chunk_${SLURM_ARRAY_TASK_ID}"
MASK_DIR="${BASE_DIR}/anterior_insula_fconn/masks"
SCRIPT_DIR="${BASE_DIR}/modeling_scripts"
SCRIPT_NAME="first_level_analysis_maskdir.py"  # change if needed

# === EXECUTION ===
cd "$SCRIPT_DIR" || { echo "Failed to cd into $SCRIPT_DIR"; exit 1; }
echo "Running on chunk directory: $CHUNK_DIR"
echo "Using masks from: $MASK_DIR"
echo "Executing: python $SCRIPT_NAME $MASK_DIR $CHUNK_DIR"

python "$SCRIPT_NAME" "$MASK_DIR" "$CHUNK_DIR"
