"""Script for testing the loading of phthalic acid NOEs from a generically formatted file."""

# Python module imports.
import sys

# Path of the relaxation data.
DATA_PATH = sys.path[-1] + '/test_suite/shared_data/'

# Pseudo-atoms.
PSEUDO = [
['Q7', ['@H16', '@H17', '@H18']],
['Q9', ['@H20', '@H21', '@H22']],
['Q10', ['@H23', '@H24', '@H25']]
]

# Clear out the data store.
reset()

# Create the data pipe.
pipe.create('test', 'N-state')

# Read the structure.
structure.read_pdb('gromacs_phthalic_acid.pdb', dir=DATA_PATH+'/structures')

# Load all protons as the sequence.
structure.load_spins('@*H*', ave_pos=False)

# Create the pseudo-atoms.
for i in range(len(PSEUDO)):
    spin.create_pseudo(spin_name=PSEUDO[i][0], res_id=None, mol_id=None, members=PSEUDO[i][1], averaging='linear')

# Read the NOE restraints.
noe.read_restraints(file='phthalic_acid', dir=DATA_PATH+'noe_restraints')


