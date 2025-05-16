#!/bin/bash
#SBATCH -p production
#SBATCH --array=1 # Replace with number of chunk_n folders
#SBATCH --job-name=secondlvl
#SBATCH --output=regression_output.log
#SBATCH --error=regression_error.log
#SBATCH --time=00:20:00  # Set the maximum run time
#SBATCH --ntasks=1      # Number of CPU tasks needed (1 in this example)
#SBATCH --cpus-per-task=4  # Number of CPU cores per task (4 in this example)
#SBATCH --mem=64000       # Memory per node

#export environment info
env
BASE="/share/foxlab-backedup/kaline_fconn/sobp_2024"
DATA_DIR="/share/foxlab-backedup/kaline_fconn/area25_bst_paper/area25_voxelwise_analysis/betavalues_output"
BEHAV_DATA="$BASE/AT_database.csv"
MAIN_EFFECT_1_COL="cort_resid"
MAIN_EFFECT_2_COL="reg_sex"
OUTPUT_FILENAME="area25_zmap"

# Change to the directory where your Python script is located
cd "$BASE"
which python

# Run your Python script
python voxelwise_interactions.py $DATA_DIR $BEHAV_DATA $MAIN_EFFECT_1_COL $MAIN_EFFECT_2_COL $OUTPUT_FILENAME
