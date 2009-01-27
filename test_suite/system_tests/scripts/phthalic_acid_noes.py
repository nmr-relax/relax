"""Script for testing the loading of phthalic acid NOEs from a generically formatted file."""

# Python module imports.
import sys

# Path of the relaxation data.
DATA_PATH = sys.path[-1] + '/test_suite/shared_data/'

# Create the data pipe.
pipe.create('test', 'N-state')

# Read the structure.
structure.read_pdb('gromacs_phthalic_acid.pdb', dir=DATA_PATH+'/structures')

# Load all protons as the sequence.
structure.load_spins('@*H*', ave_pos=False)

# Read the NOE restraints.
noe.read_restraints(file='phthalic_acid', dir=DATA_PATH+'noe_restraints')


