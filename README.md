# fmri_modeling

## First and Second Level fMRI Models for Resting-State Functional Connectivity

This repository contains example Python scripts and SLURM job submission files for performing first- and second-level fMRI analyses. The modeling is designed for resting-state functional connectivity analysis and is intended to be used on a high-performance computing (HPC) cluster.

---

## 📁 Contents

- `first_level_analysis_maskdir.py` – Python script to run first-level GLMs using subject-specific masks.
- `submit_firstlevel_jobs.sh` – SLURM batch script to submit first-level jobs across chunked data directories.
- `second_level_analysis.py` – Python script to run second-level group analysis on beta images.
- `submit_secondlevel_job.sh` – SLURM batch script for running second-level analysis.

---

## 🧠 First-Level Analysis
Each subject's resting-state time series is modeled using one or more ROI masks provided as .nii or .nii.gz files. For each ROI, the script extracts the average timeseries and fits a GLM to estimate voxelwise beta coefficients across the brain. The output includes:
- A beta image for each ROI, per subject (reflecting voxelwise connectivity).
- The extracted timeseries for each ROI

## 🧠 Second-Level Analysis
This step uses Nilearn’s SecondLevelModel to combine individual subjects’ whole brain beta images for the ROI used in the first level model. It creates a group-level z-map showing resting state functional connectivity.


