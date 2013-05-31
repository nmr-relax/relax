"""Script for calculating R2eff values, generating input files for CPMGFit, and executing CPMGFit.

To run:

$ ../../../../../relax --tee cpmgfit.log cpmgfit.py
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Load the saved state.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'
state.load(data_path+sep+'r2eff_values')

# Loop over the models.
for model in ['LM63', 'CR72']:
    # Set up the model.
    relax_disp.select_model(model)

    # Generate the input files.
    relax_disp.cpmgfit_input(force=True)

    # Execute CPMGFit.
    relax_disp.cpmgfit_execute()
