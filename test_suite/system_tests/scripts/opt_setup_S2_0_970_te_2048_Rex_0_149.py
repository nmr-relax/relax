"""Script for setting up the data pipe for testing optimisation.

The data set is:
    S2 = 0.970.
    te = 2048 ps.
    Rex = 0.149 s^-1.
"""

# Python module imports.
import sys


# Path of the files.
path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

# Load the sequence.
sequence.read('noe.500.out', dir=path)

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

# Setup other values.
diffusion_tensor.init(10e-9, fixed=1)
value.set(1.02 * 1e-10, 'bond_length')
value.set(-160 * 1e-6, 'csa')
value.set('N', 'nucleus')

# Select the model-free model.
model_free.select_model(model='m4')
