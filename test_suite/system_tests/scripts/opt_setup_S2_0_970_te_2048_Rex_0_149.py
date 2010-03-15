"""Script for setting up the data pipe for testing optimisation.

The data set is:
    S2 = 0.970.
    te = 2048 ps.
    Rex = 0.149 s^-1.
"""

# Python module imports.
import __main__
from os import sep
import sys


# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Load the sequence.
sequence.read('noe.500.out', dir=path, res_num_col=1, res_name_col=2)

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Setup other values.
diffusion_tensor.init(10e-9, fixed=True)
value.set(1.02 * 1e-10, 'bond_length')
value.set(-160 * 1e-6, 'csa')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model='m4')
