"""Script for checking operations on interatomic data containers."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

# Create a data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name="interatom testing", pipe_type='N-state')

# Load the structures.
NUM_STR = 4
for i in range(NUM_STR):
    self._execute_uf(uf_name='structure.read_pdb', file='lactose_MCMM4_S1_'+repr(i+1), dir=str_path, parser='internal', set_model_num=i+1, set_mol_name='lactose_MCMM4_S1')

# Load the sequence information.
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@H*', ave_pos=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H6')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H7')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H17')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H18')

# Create the interatomic data containers.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@C*', spin_id2='@H*', direct_bond=True)

# Deselect all.
self._execute_uf(uf_name='deselect.interatom')

# Select the non-CH2 bonds.
for i in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]:
    self._execute_uf(uf_name='select.interatom', spin_id1=':UNK@C%i'%i)

# Some more selection changes.
self._execute_uf(uf_name='deselect.interatom', spin_id1='@C2')

# Create a new molecule with 2 interatomic data containers.
self._execute_uf(uf_name='spin.create', spin_name='N', res_name='Gly', res_num=1, mol_name='Poly-gly')
self._execute_uf(uf_name='spin.create', spin_name='H', res_name='Gly', res_num=1, mol_name='Poly-gly')
self._execute_uf(uf_name='spin.create', spin_name='N', res_name='Gly', res_num=2, mol_name='Poly-gly')
self._execute_uf(uf_name='spin.create', spin_name='H', res_name='Gly', res_num=2, mol_name='Poly-gly')
self._execute_uf(uf_name='spin.element', spin_id='#Poly-gly@N', element='N')
self._execute_uf(uf_name='spin.element', spin_id='#Poly-gly@H', element='H')
self._execute_uf(uf_name='dipole_pair.define', spin_id1='#Poly-gly@N', spin_id2='#Poly-gly@H', direct_bond=True)
self._execute_uf(uf_name='deselect.interatom', spin_id1=':2')
