"""Script for testing out the N-state model alignment tensor optimisation using pyrotarctic anhydride.

This is for testing both the optimisation of long range RDCs (2J and 3J) to pseudo-atoms and for testing the absolute T and absolute J data type.
"""

# Python module imports.
from os import sep

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Setup for stand-alone operation.
if not hasattr(ds, 'abs_data'):
    ds.abs_data = 'mix'

# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'pyrotartaric_anhydride'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='pyrotartaric anhydride', pipe_type='N-state')

# Load the structure.
self._execute_uf(uf_name='structure.read_pdb', file='pyrotartaric_anhydride.pdb', dir=str_path)

# Set up the 13C and 1H spins information.
self._execute_uf(uf_name='structure.load_spins', spin_id='@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H*', ave_pos=False)

# Set up the pseudo-atoms.
self._execute_uf(uf_name='spin.create_pseudo', spin_name='Q9', members=['@10', '@11', '@12'], averaging="linear")
self._execute_uf(uf_name='sequence.display')

# Define the nuclear isotopes of all spins and pseudo-spins.
self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@Q*')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.read_dist', file='R_rdcs', dir=data_path, unit='Angstrom', spin_id1_col=1, spin_id2_col=2, data_col=7)
self._execute_uf(uf_name='interatom.unit_vectors', ave=False)

# Load the short range RDC data and long range J and J+D data.
if ds.abs_data == 'mix':
    # Short range RDCs.
    self._execute_uf(uf_name='rdc.read', align_id='test', file='R_rdcs_short_range', dir=data_path, data_type='D', spin_id1_col=1, spin_id2_col=2, data_col=4, absolute=False)

    # Long range J and J+D data.
    self._execute_uf(uf_name='rdc.read', align_id='test', file='R_rdcs_long_range', dir=data_path, data_type='T', spin_id1_col=1, spin_id2_col=2, data_col=4, absolute=True)
    self._execute_uf(uf_name='j_coupling.read', file='R_rdcs_long_range', dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=5, sign_col=6)

# Load the J and J+D data.
elif ds.abs_data == 'T':
    self._execute_uf(uf_name='rdc.read', align_id='test', file='R_rdcs', dir=data_path, data_type='T', spin_id1_col=1, spin_id2_col=2, data_col=4, absolute=True)
    self._execute_uf(uf_name='j_coupling.read', file='R_rdcs', dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=5, sign_col=6)

# Load the RDC data.
elif ds.abs_data == 'D':
    self._execute_uf(uf_name='rdc.read', align_id='test', file='R_rdcs', dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=3)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Deselect the pseudo-atom protons.
self._execute_uf(uf_name='deselect.spin', spin_id='@10')
self._execute_uf(uf_name='deselect.spin', spin_id='@11')
self._execute_uf(uf_name='deselect.spin', spin_id='@12')

# Minimisation.
self._execute_uf(uf_name='grid_search', inc=4)
self._execute_uf(uf_name='minimise', min_algor='simplex')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Create a correlation plot.
self._execute_uf(uf_name='rdc.corr_plot', file='devnull', force=True)

# Save the state.
self._execute_uf(uf_name='state.save', state='devnull', force=True)
