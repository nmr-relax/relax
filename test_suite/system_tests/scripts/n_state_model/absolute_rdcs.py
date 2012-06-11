"""Script for testing the fitting of signless RDCs."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create a data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='abs', pipe_type='N-state')

# Load the CaM structure.
self._execute_uf(uf_name='structure.read_pdb', file='bax_C_1J7P_N_H_Ca', dir=STRUCT_PATH)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins')

# Load the NH vectors.
self._execute_uf(uf_name='structure.vectors', spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
self._execute_uf(1.041 * 1e-10, 'r', spin_id="@N", uf_name='value.set')
self._execute_uf('15N', 'heteronuc_type', spin_id="@N", uf_name='value.set')
self._execute_uf('1H', 'proton_type', spin_id="@N", uf_name='value.set')

# Load the RDCs (both a signed and absolute value version).
self._execute_uf(uf_name='rdc.read', align_id='signed', file='synth_rdc', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)
#self._execute_uf(uf_name='rdc.read', align_id='abs', file='synth_rdc_abs', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, absolute=True)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='grid_search', inc=3)
self._execute_uf('simplex', constraints=False, max_iter=500, uf_name='minimise')

# Write out a results file.
self._execute_uf('devnull', force=True, uf_name='results.write')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print((cdp.align_tensors[0]))
