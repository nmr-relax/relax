# Script for checking the loading of bond vectors in the correct order.

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'


# Create the data pipe.
self._execute_uf('populations', 'N-state', uf_name='pipe.create')

# Load the structures.
for i in range(3):
    self._execute_uf(uf_name='structure.read_pdb', file='lactose_MCMM4_S1_%i.pdb' % (ds.order_struct[i]+1), dir=str_path, set_model_num=ds.order_model[i]+1, set_mol_name='LE')

# Load the sequence information.
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@C1', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@H1', ave_pos=False)

# Load the CH vectors for the C atoms.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@C1', spin_id2='@H1', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)
