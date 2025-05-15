# second_level_modeling.py

import numpy as np
import pandas as pd
import nibabel as nib
from pathlib import Path
import typer
from nilearn.glm.second_level import SecondLevelModel

app = typer.Typer(help="Second-level fMRI GLM analysis across subjects.")

def collect_beta_files(data_dir: Path) -> list[Path]:
    """Collects all beta value files from the specified directory."""
    return sorted(data_dir.glob("beta_values_*_seed.nii.gz"))

def build_design_matrix(n_subjects: int) -> pd.DataFrame:
    """Creates a simple design matrix with only an intercept."""
    return pd.DataFrame({'intercept': np.ones(n_subjects)})

def run_second_level_glm(beta_files: list[Path], output_path: Path):
    """Fits the second-level model and saves the resulting z-map."""
    model = SecondLevelModel(smoothing_fwhm=0.0)
    design_matrix = build_design_matrix(len(beta_files))
    model = model.fit(beta_files, design_matrix=design_matrix)
    z_map = model.compute_contrast(output_type='z_score')
    z_map.to_filename(str(output_path))

@app.command()
def pipeline(
    output_tag: str = typer.Argument(..., help="Tag to append to the output filename"),
    data_dir: Path = typer.Argument(..., help="Directory containing beta value NIfTI files")
):
    beta_files = collect_beta_files(data_dir)
    if len(beta_files) == 0:
        typer.echo("No beta files found. Please check the input directory.")
        raise typer.Exit(code=1)

    zmap_output_dir = data_dir.parent / "zmap_output"
    zmap_output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = zmap_output_dir / f"zmap_{output_tag}_seeded.nii.gz"
    run_second_level_glm(beta_files, output_file)

    typer.echo(f"Second-level z-map saved to: {output_file}")

if __name__ == "__main__":
    app()
