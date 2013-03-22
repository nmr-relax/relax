# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
from os import sep

# relax module imports.
from lib.errors import RelaxError
from specific_analyses.setup import n_state_model_obj
from status import Status; status = Status()

# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'population_model'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='orig', pipe_type='N-state')

# Load the structures.
NUM_STR = 3
i = 1
for model in [1, 3, 2]:
    self._execute_uf(uf_name='structure.read_pdb', file='lactose_MCMM4_S1_%i.pdb' % i, dir=str_path, set_model_num=model, set_mol_name='LE')
    i += 1

# Load the sequence information.
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@H*', ave_pos=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H6')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H7')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H17')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H18')

## Define the magnetic dipole-dipole relaxation interaction.
#self._execute_uf(uf_name='dipole_pair.define', spin_id1='@C*', spin_id2='@H*', direct_bond=True)
#self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@C*', spin_id2='@H*', ave_dist=1.10 * 1e-10)
#self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)
#
## Set the nuclear isotope type.
#self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
#self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in range(len(align_list)):
    # The RDC (skip the list at index 1, as this has zero data and now causes a RelaxError).
    if i != 1:
        self._execute_uf(uf_name='rdc.read', align_id=align_list[i], file='missing_rdc_%i' % i, dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=None)

    # The PCS.
    self._execute_uf(uf_name='pcs.read', align_id=align_list[i], file='missing_pcs_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)

    # The temperature.
    self._execute_uf(uf_name='temperature', id=align_list[i], temp=298)

    # The frequency.
    self._execute_uf(uf_name='frq.set', id=align_list[i], frq=799.75376122 * 1e6)

# Create a new data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='new', pipe_type='N-state')

# Copy the data.
self._execute_uf(uf_name='sequence.copy', pipe_from='orig', pipe_to='new')
self._execute_uf(uf_name='interatomic.copy', pipe_from='orig', pipe_to='new')
self._execute_uf(uf_name='rdc.copy', pipe_from='orig', pipe_to='new')
self._execute_uf(uf_name='pcs.copy', pipe_from='orig', pipe_to='new')

# Copy the data again (test that data can be overwritten).
self._execute_uf(uf_name='rdc.copy', pipe_from='orig', pipe_to='new')
self._execute_uf(uf_name='pcs.copy', pipe_from='orig', pipe_to='new')
