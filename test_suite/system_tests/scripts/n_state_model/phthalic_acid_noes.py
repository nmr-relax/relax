"""Script for testing the loading of phthalic acid NOEs from a generically formatted file."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Add a date pipe if one doesn't already exist.
if not ds.keys():
    self._execute_uf(uf_name='pipe.create', pipe_name='test', pipe_type='N-state')

# NOE restraint file.
if not hasattr(ds, 'file_name'):
    ds.file_name = 'phthalic_acid'

# Path of the relaxation data.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

# Pseudo-atoms.
PSEUDO = [
['Q7', ['@H16', '@H17', '@H18']],
['Q9', ['@H20', '@H21', '@H22']],
['Q10', ['@H23', '@H24', '@H25']]
]

# Read the structure.
self._execute_uf(uf_name='structure.read_pdb', file='gromacs.pdb', dir=DATA_PATH+sep+'structures'+sep+'phthalic_acid')

# Load all protons as the sequence.
self._execute_uf(uf_name='structure.load_spins', spin_id='@*H*', ave_pos=False)

# Create the pseudo-atoms.
for i in range(len(PSEUDO)):
    self._execute_uf(uf_name='spin.create_pseudo', spin_name=PSEUDO[i][0], res_id=None, members=PSEUDO[i][1], averaging='linear')

# Read the NOE restraints.
self._execute_uf(uf_name='noe.read_restraints', file=ds.file_name, dir=DATA_PATH+'noe_restraints')

# Set the type of N-state model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Calculate the average NOE potential.
self._execute_uf(uf_name='calc')


