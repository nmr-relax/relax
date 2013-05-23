"""Script for testing the fitting an alignment tensor to RDCs or PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control import pipes
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'paramagnetic'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
self._execute_uf('paramagnetic alignment', 'N-state', uf_name='pipe.create')

# Load the CaM structure.
self._execute_uf(uf_name='structure.read_pdb', file='bax_C_1J7P_N_H_Ca', dir=STRUCT_PATH, set_mol_name='CaM')

# Load the spins.
self._execute_uf(uf_name='structure.load_spins')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)

# Set the nuclear isotope.
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# RDCs.
self._execute_uf(uf_name='rdc.read', align_id='Dy', file='dy_700_rdc', dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=None)
self._execute_uf(uf_name='rdc.read', align_id='Er', file='er_900_rdc', dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=None)

# The frequency.
self._execute_uf(uf_name='spectrometer.frequency', id='Dy', frq=700.0 * 1e6)
self._execute_uf(uf_name='spectrometer.frequency', id='Er', frq=900.0 * 1e6)

# PCSs.
self._execute_uf(uf_name='pcs.read', align_id='Dy', file='dy_pcs', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)
self._execute_uf(uf_name='pcs.read', align_id='Er', file='er_pcs', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

# Set the paramagnetic centre.
self._execute_uf(uf_name='paramag.centre', atom_id=':1000@CA')

# The temperature.
self._execute_uf(uf_name='spectrometer.temperature', id='Dy', temp=303)
self._execute_uf(uf_name='spectrometer.temperature', id='Er', temp=303)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Set up the alignment tensors (for faster optimisation in the test suite)
self._execute_uf(uf_name='align_tensor.init', tensor='Dy', align_id='Dy', params=(0.00037, -0.00017, 0.00016, 0.00060, -0.00019))
self._execute_uf(uf_name='align_tensor.init', tensor='Er', align_id='Er', params=(0.00141,  0.00153, 0.00169, 0.00084, -0.00098))

# Minimisation of only the Er tensor.
self._execute_uf(uf_name='align_tensor.fix', id='Dy', fixed=True)
self._execute_uf('simplex', constraints=False, max_iter=500, uf_name='minimise')

# Write out a results file.
self._execute_uf('devnull', dir=None, force=True, uf_name='results.write')

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
