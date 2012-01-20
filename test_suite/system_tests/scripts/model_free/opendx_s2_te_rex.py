"""Script for mapping the {S2, te, Rex} chi2 space for visualisation using OpenDX."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from physical_constants import N15_CSA, NH_BOND_LENGTH
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Read the sequence.
sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

# Read the relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Setup other values.
diffusion_tensor.init(1e-8, fixed=True)
value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'r'])
value.set('15N', 'heteronuc_type')
value.set('1H', 'proton_type')

# Select the model.
model_free.select_model(model='m4')

# Map the space.
dx.map(params=['s2', 'te', 'rex'], spin_id=':2', inc=2, lower=[0.0, 0, 0], upper=[1.0, 10000e-12, 3.0 / (2.0 * pi * 600000000.0)**2], point=[0.970, 2048.0e-12, 0.149 / (2.0 * pi * 600000000.0)**2], file_prefix='devnull', point_file='devnull')
