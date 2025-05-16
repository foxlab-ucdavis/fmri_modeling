#!/bin/bash
#SBATCH -p production
#SBATCH --array=1  # Only 1 task now, update if splitting across chunks
#SBATCH --job-name=secondlvl_modeling
#SBATCH --output=slurm_logs/secondlvl_%A_%a.out
#SBATCH --error=slurm_logs/secondlvl_%A_%a.err
#SBATCH --time=30:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G

# Print environment information
env

# === CONFIGURATION ===
BASE_DIR="/share/foxlab-backedup/kaline_fconn"
DATA_DIR="${BASE_DIR}/anterior_insula_fconn/betavalues_output"
SCRIPT_DIR="${BASE_DIR}/modeling_scripts"
SCRIPT_NAME="second_level_modeling.py"
OUTPUT_TAG="AI"

# === EXECUTION ===
cd "$SCRIPT_DIR" || { echo "Failed to cd into $SCRIPT_DIR"; exit 1; }
echo "Running second-level model with data from: $DATA_DIR"
echo "Executing: python $SCRIPT_NAME pipeline $OUTPUT_TAG $DATA_DIR"

python "$SCRIPT_NAME" "$OUTPUT_TAG" "$DATA_DIR"
