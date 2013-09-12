"""Script for generating input files for CATIA and running CATIA.

To run:

$ ../../../../../relax --tee catia.log catia.py
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Load the saved state.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'
state.load(data_path+sep+'r2eff_values')

# Set up the spin isotope information.
spin.isotope('15N')

# Generate the CATIA input files.
relax_disp.catia_input(dir='.', force=True)

# Execute CATIA.
relax_disp.catia_execute()
