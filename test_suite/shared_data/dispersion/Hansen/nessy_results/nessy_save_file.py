"""Script for generating a NESSY save file from within relax.

To run:

$ ../../../../../relax nessy_save_file.py --tee nessy_save_file.log
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Load the saved state.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'
state.load(data_path+sep+'r2eff_values')

# Generate the input files.
relax_disp.nessy_input(force=True)
