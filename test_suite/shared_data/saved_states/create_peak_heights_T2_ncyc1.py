# relax script for regenerating the 'peak_heights_T2_ncyc1.bz2' saved state.  This is necessary when
# the saved state becomes incompatible with relax during development.

# Python module imports.
from os import sep
import sys

# The relax data store.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Add a data pipe to the data store.
ds.add(pipe_name='rx', pipe_type='relax_fit')

# Load the Lupin Ap4Aase sequence.
sequence.read(file="Ap4Aase.seq", dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Read the peak heights.
spectrum.read_intensities(file="T2_ncyc1_ave.list", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting', spectrum_id='0.0176')

# Save the state.
state.save('basic_heights_T2_ncyc1', force=True)
