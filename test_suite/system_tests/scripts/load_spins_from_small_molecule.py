"""Load a number of spin systems for a small molecule."""

import sys


# Read in the small molecule.
structure.read_pdb(file='gromacs_phthalic_acid.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures')

# Load all protons.
structure.load_spins(spin_id='@*H*')

# Load a few carbons.
structure.load_spins(spin_id='@C5')
structure.load_spins(spin_id='@C6')
structure.load_spins(spin_id='@C19')
structure.load_spins(spin_id='@C23')
