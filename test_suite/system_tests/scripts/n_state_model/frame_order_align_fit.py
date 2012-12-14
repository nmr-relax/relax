# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'dna'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'missing_data'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='orig', pipe_type='frame order')

# Load the structure.
self._execute_uf(uf_name='structure.read_pdb', file='LE_trunc.pdb', dir=str_path, set_mol_name='LE')

# Load the sequence information.
self._execute_uf(uf_name='structure.load_spins', spin_id='@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H*', ave_pos=False)

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@C*', spin_id2='@H*', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@C*', spin_id2='@H*', ave_dist=1.10 * 1e-10)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)

# Set the nuclear isotope type.
self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in range(len(align_list)):
    # The RDC.
    if i != 1:
        self._execute_uf(uf_name='rdc.read', align_id=align_list[i], file='missing_rdc_%i' % i, dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=None)
        self._execute_uf(uf_name='rdc.display', align_id=align_list[i])

    # The PCS.
    if i != 2:
        self._execute_uf(uf_name='pcs.read', align_id=align_list[i], file='missing_pcs_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)
        self._execute_uf(uf_name='pcs.display', align_id=align_list[i])

    # The temperature.
    self._execute_uf(uf_name='temperature', id=align_list[i], temp=298)

    # The frequency.
    self._execute_uf(uf_name='frq.set', id=align_list[i], frq=799.75376122 * 1e6)

    # Initialise an alignment tensor.
    self._execute_uf(uf_name='align_tensor.init', tensor=align_list[i], align_id=align_list[i], params=(0, 0, 0, 0, 0))

# Set the paramagnetic centre.
self._execute_uf(uf_name='paramag.centre', pos=[1, 2, -30])

# Create a new data pipe by copying the old, and switch to it.
self._execute_uf(uf_name='pipe.copy', pipe_to='copy')
self._execute_uf(uf_name='pipe.switch', pipe_name='copy')

# Change the data pipe type.
self._execute_uf(uf_name='pipe.change_type', pipe_type='N-state')

# Delete all the alignment data.
self._execute_uf(uf_name='rdc.delete')
self._execute_uf(uf_name='pcs.delete')
self._execute_uf(uf_name='align_tensor.delete')

# Copy the tensor back.
self._execute_uf(uf_name='align_tensor.copy', pipe_from='orig', tensor_from='Dy')

# Copy the alignment data.
self._execute_uf(uf_name='rdc.copy', pipe_from='orig', align_id='Dy')
self._execute_uf(uf_name='pcs.copy', pipe_from='orig', align_id='Dy')

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='minimise', min_algor='newton', constraints=True)

# Write out a results file.
self._execute_uf(uf_name='results.write', file='devnull', force=True)
