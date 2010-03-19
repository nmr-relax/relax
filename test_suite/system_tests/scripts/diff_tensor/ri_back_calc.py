"""Script for testing diffusion tensor optimisation."""

# Python module imports.
import __main__
from numpy import array, float64
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Stand alone operation.
if not hasattr(ds, 'diff_type'):
    ds.diff_type = 'ellipsoid'

# A data pipe.
pipe.create('back_calc', 'mf')

# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'+sep+ds.diff_type

# Load the sequence.
sequence.read('NOE.500.out', dir=path, res_num_col=1)

# Load a PDB file.
structure.read_pdb('uniform.pdb', dir=path)

# Set the spin name and then load the NH vectors.
spin.name(name='N')
structure.vectors(spin_id='@N', attached='H*', ave=False)

# Initialise the diffusion tensors.
if ds.diff_type == 'sphere':
    diffusion_tensor.init(1.0/(6.0*2e7), fixed=False)
elif ds.diff_type == 'spheroid':
    diffusion_tensor.init((1.0/(6.0*5e7/3.0), -1e7, 2.0, 0.5), fixed=False)
elif ds.diff_type == 'ellipsoid':
    diffusion_tensor.init((8.3333333333333335e-09, 15000000.0, 0.33333333333333331, 1.0, 2.0, 0.5), fixed=False)
else:
    raise RelaxError, "The diffusion type '%s' is unknown." % ds.diff_type

# Setup other values.
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model='m0')

# Back-calculate.
frq = array([500], float64)
#frq = array([500, 600, 700, 800], float64)
for i in range(len(frq)):
    relax_data.back_calc(ri_label='R1', frq_label=str(int(frq[i])), frq=frq[i] * 1e6)
    relax_data.back_calc(ri_label='R2', frq_label=str(int(frq[i])), frq=frq[i] * 1e6)
    relax_data.back_calc(ri_label='NOE', frq_label=str(int(frq[i])), frq=frq[i] * 1e6)

relax_data.display(ri_label='R1', frq_label='500')

# Load the original relaxation data into another data pipe.
pipe.create('orig_data', 'mf')
sequence.read('NOE.500.out', dir=path, res_num_col=1)
for i in range(len(frq)):
    relax_data.read('R1', str(int(frq[i])), frq[i] * 1e6, 'R1.%s.out'%str(int(frq[i])), dir=path, res_num_col=1, data_col=2, error_col=3)
    relax_data.read('R2', str(int(frq[i])), frq[i] * 1e6, 'R2.%s.out'%str(int(frq[i])), dir=path, res_num_col=1, data_col=2, error_col=3)
    relax_data.read('NOE', str(int(frq[i])), frq[i] * 1e6, 'NOE.%s.out'%str(int(frq[i])), dir=path, res_num_col=1, data_col=2, error_col=3)
relax_data.display(ri_label='R1', frq_label='500')


