"""Script for testing diffusion tensor optimisation."""

# Python module imports.
import __main__
from numpy import array, float64
from os import sep
import sys


# A data pipe.
pipe.create('diff_opt', 'mf')

# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'

# Load the sequence.
sequence.read('NOE.500.out', dir=path, res_num_col=1)

# Load a PDB file.
structure.read_pdb('uniform.pdb', dir=path)

# Set the spin name and then load the NH vectors.
spin.name(name='N')
structure.vectors(spin_id='@N', attached='H*', ave=False)

# Load the relaxation data.
frq = array([500, 600, 700, 800], float64)
for i in range(len(frq)):
    relax_data.read('R1', str(int(frq[i])), frq[i] * 1e6, 'R1.%s.out'%str(int(frq[i])), dir=path, res_num_col=1, data_col=2, error_col=3)
    relax_data.read('R2', str(int(frq[i])), frq[i] * 1e6, 'R2.%s.out'%str(int(frq[i])), dir=path, res_num_col=1, data_col=2, error_col=3)
    relax_data.read('NOE', str(int(frq[i])), frq[i] * 1e6, 'NOE.%s.out'%str(int(frq[i])), dir=path, res_num_col=1, data_col=2, error_col=3)

# Setup other values.
diffusion_tensor.init((8.3333333333333335e-09, 15000000.0, 0.33333333333333331, 1.0, 2.0, 0.5), fixed=False)
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model='m0')

# Optimisation.
minimise('newton')
