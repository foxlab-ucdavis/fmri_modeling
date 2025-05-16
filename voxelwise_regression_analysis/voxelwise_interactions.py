import pandas as pd
from pathlib import Path
from collections import defaultdict
from nilearn.glm.second_level import SecondLevelModel

def read_behavioral_data(behavioral_data_path):
    return pd.read_csv(behavioral_data_path)

def preprocess_behavioral_data(inhibition_df, main_effect_1, main_effect_2):
    # Extract nuisance variables for the design matrix
    inhibition_df['reg_sophis'] = inhibition_df['Study'].apply(lambda x: 1 if x == 'Typo2/Soph' else 0)
    inhibition_df['reg_site'] = inhibition_df['site'].apply(lambda x: 1 if x.startswith('L') else 0)
    inhibition_df['reg_sex'] = inhibition_df['Sex'].apply(lambda x: 1 if x.startswith('M') else -1)
    inhibition_df['constant'] = 1

    # Define nuisance variables and create the design matrix
    nuisance_vars = [main_effect_1, 'constant', 'reg_sophis', 'reg_site', 'reg_sex', 'age', 'scanner', 'scanOrder', 'unique_mri_id']
    design_matrix = inhibition_df[nuisance_vars]

    # Create the interaction term based on the main effects specified above
    # Put it in the first column of the design matrix
    interaction_term = f'{main_effect_1}by{main_effect_2}'
    design_matrix.insert(0, interaction_term, inhibition_df[main_effect_1] * inhibition_df[main_effect_2])

    return design_matrix, interaction_term

def load_files_for_regression(data_dir):
    files_for_regression = defaultdict(list)
    for betavals in data_dir.glob('beta*.nii'):
        subject_id = betavals.stem.split('_')[2]
        files_for_regression[subject_id].append(str(betavals))
    return sorted(file for files_list in files_for_regression.values() for file in files_list)

def preprocess_design_matrix(design_matrix, subject_list):
    return design_matrix[design_matrix['unique_mri_id'].isin(subject_list)].sort_values(by='unique_mri_id').drop(['unique_mri_id'], axis=1)

def fit_second_level_model(second_level_model, filename_list, design_matrix):
    return second_level_model.fit(filename_list, design_matrix=design_matrix)

def rearrange_columns(final_design_matrix_for_model, main_effect_1, main_effect_2, interaction_term):
    # Create a list of columns in the desired order
    new_column_order = [main_effect_1, main_effect_2, interaction_term] + [col for col in final_design_matrix_for_model.columns if col not in [main_effect_1, main_effect_2, interaction_term]]
    # Reassign the columns of the existing DataFrame with the new order
    final_design_matrix_for_model = final_design_matrix_for_model[new_column_order]
    return final_design_matrix_for_model

def define_contrasts(final_design_matrix_for_model, main_effect_1, main_effect_2, interaction_term):
    contrast_main_effect_1 = [1] + [0] * (final_design_matrix_for_model.shape[1] - 1)
    contrast_main_effect_2 = [0, 1] + [0] * (final_design_matrix_for_model.shape[1] - 2)
    contrast_interaction = [0, 0, 1] + [0] * (final_design_matrix_for_model.shape[1] - 3)

    contrasts = {
        main_effect_1 : contrast_main_effect_1,
        main_effect_2 : contrast_main_effect_2,
        interaction_term : contrast_interaction
    }

    return contrasts

def compute_and_save_z_maps(second_level_model, contrasts, output_dir, zmap_output_filename):
    z_maps = {}
    for contrast_name, contrast_vector in contrasts.items():
        z_map = second_level_model.compute_contrast(contrast_vector, output_type='z_score')
        output_path = output_dir / f"{zmap_output_filename}_{contrast_name}_voxelwise.nii.gz"
        z_map.to_filename(output_path)
        z_maps[contrast_name] = output_path
    return z_maps

if __name__ == "__main__":
    import typer

    app = typer.Typer()

    @app.command()
    def pipeline(data_dir: str, behavioral_data: str, main_effect_1: str, main_effect_2: str, zmap_output_filename: str):
        data_dir = Path(data_dir)
        behavioral_data_path = Path(behavioral_data)
        output_dir = behavioral_data_path.parent

        # Read behavioral data
        inhibition_df = read_behavioral_data(behavioral_data_path)

        # Preprocess behavioral data
        design_matrix, interaction_term = preprocess_behavioral_data(inhibition_df, main_effect_1, main_effect_2)

        # Load filenames for regression
        filename_list = load_files_for_regression(data_dir)

        # Filter design matrix based on subject list
        subject_list = list({betavals.stem.split('_')[2] for betavals in data_dir.glob('beta*.nii')})        
#subject_list = [betavals.stem.split('_')[2] for betavals in data_dir.glob('beta*.nii')]
        final_design_matrix_for_model = preprocess_design_matrix(design_matrix, subject_list)
        
        # Rearrange columns
        final_design_matrix_for_model = rearrange_columns(final_design_matrix_for_model, main_effect_1, main_effect_2, interaction_term)

        # Fit second level model
        second_level_model = SecondLevelModel(smoothing_fwhm=0.0)
        second_level_model = fit_second_level_model(second_level_model, filename_list, final_design_matrix_for_model)

        # Define contrasts
        contrasts = define_contrasts(final_design_matrix_for_model, main_effect_1, main_effect_2, interaction_term)

        # Compute and save z-maps for each contrast
        z_maps = compute_and_save_z_maps(second_level_model, contrasts, output_dir, zmap_output_filename)
        print("Pipeline execution completed.")

    app()

