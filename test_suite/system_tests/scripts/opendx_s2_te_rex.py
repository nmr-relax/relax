"""Script for mapping the {S2, te, Rex} chi2 space for visualisation using OpenDX."""

# Python module imports.
import __main__
from os import sep
import sys

# relax module imports.
from physical_constants import N15_CSA, NH_BOND_LENGTH


# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Read the sequence.
sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

# Read the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Setup other values.
diffusion_tensor.init(1e-8, fixed=True)
value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'bond_length'])
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Select the model.
model_free.select_model(model='m4')

# Map the space.
dx.map(params=['S2', 'te', 'Rex'], spin_id=':2', inc=2, lower=[0.0, 0, 0], upper=[1.0, 10000e-12, 3.0 / (2.0 * pi * 600000000.0)**2], point=[0.970, 2048.0e-12, 0.149 / (2.0 * pi * 600000000.0)**2], file_prefix='devnull', point_file='devnull')
