# relax script for regenerating the 'peak_heights_T2_ncyc1.bz2' saved state.  This is necessary when
# the saved state becomes incompatible with relax during development.

# Python module imports.
import sys

# The relax data store.
from data import Relax_data_store; ds = Relax_data_store()


# Add a data pipe to the data store.
ds.add(pipe_name='rx', pipe_type='relax_fit')

# Load the Lupin Ap4Aase sequence.
sequence.read(file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/system_tests/data")

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Read the peak heights.
relax_fit.read(file="T2_ncyc1_ave.list", dir=sys.path[-1] + "/test_suite/shared_data/curve_fitting", relax_time=0.0176)

# Save the state.
state.save('basic_heights_T2_ncyc1', force=True)
