"""Load a number of spin systems for a small molecule."""

from os import sep
import sys


# Read in the small molecule.
structure.read_pdb(file='gromacs.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid')

# Load all protons.
structure.load_spins(spin_id='@*H*')

# Load a few carbons.
structure.load_spins(spin_id='@C5')
structure.load_spins(spin_id='@C6')
structure.load_spins(spin_id='@C19')
structure.load_spins(spin_id='@C23')
