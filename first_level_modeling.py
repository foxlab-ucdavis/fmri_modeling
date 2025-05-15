# first_level_analysis.py

import numpy as np
import pandas as pd
import nibabel as nib
from pathlib import Path
import typer
from nilearn.input_data import NiftiLabelsMasker
from nilearn.glm.first_level import FirstLevelModel, make_first_level_design_matrix

app = typer.Typer(help="First-level fMRI GLM analysis using custom masks and BOLD files.")

def extract_timeseries(bold_file: Path, mask_img, subject_id: str) -> np.ndarray:
    bold_img = nib.load(str(bold_file))
    masker = NiftiLabelsMasker(labels_img=mask_img, background_label=0, standardize=False)
    return masker.fit_transform(bold_img), bold_img

def make_design_matrix(time_series: np.ndarray, n_scans: int, t_r: float = 2.0) -> pd.DataFrame:
    frametimes = np.linspace(0, (n_scans - 1) * t_r, n_scans)
    return make_first_level_design_matrix(
        frametimes,
        hrf_model='spm',
        add_regs=time_series,
        add_reg_names=['seed_regressor']
    )

def run_glm_and_save_output(bold_img, design_matrix, output_path: Path):
    model = FirstLevelModel(t_r=2, slice_time_ref=0, mask_img=False)
    model = model.fit(run_imgs=bold_img, design_matrices=design_matrix)

    contrast = np.array([1] + [0] * (design_matrix.shape[1] - 1))
    effect_map = model.compute_contrast(contrast, output_type='effect_size')
    effect_map.to_filename(str(output_path))

def process_subject(bold_file: Path, mask_img, mask_tag: str,
                    timeseries_dir: Path, betavalues_dir: Path):
    subject_id = bold_file.stem.split('_')[1]

    ts_filename = timeseries_dir / f"timeseries_{subject_id}_{mask_tag}_mask.npy"
    beta_filename = betavalues_dir / f"beta_values_{subject_id}_{mask_tag}_seed.nii.gz"

    time_series, bold_img = extract_timeseries(bold_file, mask_img, subject_id)
    np.save(ts_filename, time_series)

    design_matrix = make_design_matrix(time_series, bold_img.shape[-1])
    run_glm_and_save_output(bold_img, design_matrix, beta_filename)

@app.command()
def pipeline(
    mask_dir: Path = typer.Argument(..., help="Directory of .nii mask files."),
    data_dir: Path = typer.Argument(..., help="Directory with BOLD .nii.gz files.")
):
    for mask_file in mask_dir.glob("*.nii*"):
        mask_img = nib.load(str(mask_file))
        mask_tag = mask_file.stem

        base_dir = mask_file.parent.parent
        timeseries_dir = base_dir / "timeseries_output"
        betavalues_dir = base_dir / "betavalues_output"
        timeseries_dir.mkdir(parents=True, exist_ok=True)
        betavalues_dir.mkdir(parents=True, exist_ok=True)

        for bold_file in data_dir.glob("*processed.nii.gz"):
            process_subject(bold_file, mask_img, mask_tag, timeseries_dir, betavalues_dir)

if __name__ == "__main__":
    app()
