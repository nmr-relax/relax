"""Script for testing the fitting of signless RDCs using menthol data."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()



# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'menthol'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='long-range RDC', pipe_type='N-state')

# Load the structure.
self._execute_uf(uf_name='structure.read_pdb', file='menthol_1R2S5R.pdb', dir=STRUCT_PATH)

# Set up the 13C and 1H spins information.
self._execute_uf(uf_name='structure.load_spins', spin_id='@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H*', ave_pos=False)

# Set up the pseudo-atoms.
self._execute_uf(uf_name='spin.create_pseudo', spin_name='Q7', members=['@H10', '@H11', '@H12'], averaging="linear")
self._execute_uf(uf_name='spin.create_pseudo', spin_name='Q9', members=['@H14', '@H15', '@H16'], averaging="linear")
self._execute_uf(uf_name='spin.create_pseudo', spin_name='Q10', members=['@H17', '@H18', '@H19'], averaging="linear")
self._execute_uf(uf_name='sequence.display')

# Define the nuclear isotopes of all spins and pseudo-spins.
self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@Q*')

# Load the RDC data.
self._execute_uf(uf_name='rdc.read', align_id='Gel', file='long_range_rdc', dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4, absolute=True)

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.read_dist', file='long_range_rdc', dir=DATA_PATH, unit='Angstrom', spin_id1_col=1, spin_id2_col=2, data_col=5)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='minimise', min_algor='newton')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Save the state.
self._execute_uf(uf_name='state.save', file='devnull')
