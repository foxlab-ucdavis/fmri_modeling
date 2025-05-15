import numpy as np
import pandas as pd 
import os

from nilearn import datasets, plotting, input_data
from nilearn.input_data import NiftiLabelsMasker

from nilearn.glm.first_level import FirstLevelModel, make_first_level_design_matrix


from nilearn.glm.second_level import SecondLevelModel

from pathlib import Path
import nibabel as nib

###### ----------- PIPELINE ---------- #####
if __name__ == "__main__":
    import typer

    app = typer.Typer()

    @app.command()
    def pipeline(output_tag: str = typer.Argument(...,help="Tag to append to the output filename"),
             data_dir: str = typer.Argument(..., help="Path to the directory containing the beta values."
        )):

        data_dir = Path(data_dir)
        # Second level analysis
        # Dictionary for file paths
        files_for_second_level_dict = {}
        # Put all the files ina  dictionary
        for subject_data in data_dir.glob("beta*"):
            # Get the key for the dictionary (subject id)
            subject_id = subject_data.stem.split('_')[2]
            # Add the subject_id and corresponding file_list to the dictionary
            files_for_second_level_dict[subject_id] = [str(subject_data)]
        # Create a list of all file paths
        all_files = []
        # Add files from the dictionary to the list... (tbh this is redundant)
        for files_list in files_for_second_level_dict.values():
            all_files.extend(files_list)
        design_matrix_second = pd.DataFrame([1] * len(all_files),
                        columns=['intercept'])
        second_level_model = SecondLevelModel(smoothing_fwhm=0.0)
        #creating a second level model
        second_level_model = second_level_model.fit(all_files,
                                    design_matrix=design_matrix_second)
        z_map = second_level_model.compute_contrast(output_type='z_score')
        # Create a directory for the z_map
        zmap_output_dir = data_dir.parent / "zmap_output"
        if not zmap_output_dir.exists():
            zmap_output_dir.mkdir(exist_ok=True)
        zmap_output_filename = f"zmap_{output_tag}_seeded"
        # Save the z_map
        z_map.to_filename(f"{zmap_output_dir}/{zmap_output_filename}")

app()



