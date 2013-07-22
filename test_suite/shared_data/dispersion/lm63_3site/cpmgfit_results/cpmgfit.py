"""Script for calculating R2eff values, generating input files for CPMGFit, and executing CPMGFit.

To run:

$ ../../../../../relax --tee cpmgfit.log cpmgfit.py
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Load the saved state.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'lm63_3site'
state.load(data_path+sep+'r2eff_values')

# Set up the model.
relax_disp.select_model('LM63 3-site')

# Generate the input files.
relax_disp.cpmgfit_input(dir='.', force=True)

# Execute CPMGFit.
relax_disp.cpmgfit_execute(dir='.')
