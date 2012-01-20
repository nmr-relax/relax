"""Script for testing the Monte Carlo simulations of fitting an alignment tensor to RDCs and PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'monte_carlo_testing'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'sphere'

# Create the data pipe.
pipe.create('MC test', 'N-state')

# Load the test structure.
structure.read_pdb(file='sphere', dir=STRUCT_PATH)

# Load the spins.
structure.load_spins()

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.041 * 1e-10, 'r', spin_id="@N")
value.set('15N', 'heteronuc_type', spin_id="@N")
value.set('1H', 'proton_type', spin_id="@N")

# RDCs.
rdc.read(align_id='synth', file='synth_rdc', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# PCSs.
pcs.read(align_id='synth', file='synth_pcs', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Set the paramagnetic centre.
paramag.centre(pos=[10.0, 0.0, 0.0])

# The temperature.
temperature(id='synth', temp=303)

# The frequency.
frq.set(id='synth', frq=600.0 * 1e6)

# Set up the model.
n_state_model.select_model(model='fixed')

# Minimisation.
grid_search(inc=3)
minimise('simplex', constraints=False, max_iter=500)

# Monte Carlo simulations.
monte_carlo.setup(3)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False, max_iter=500)
monte_carlo.error_analysis()

# Write out a results file.
results.write('devnull', force=True)

# Show the tensors.
align_tensor.display()

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print((cdp.align_tensors[0]))
