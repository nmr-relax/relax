# System test for creating a PDB representation of the distribution of XH bond vectors.

import sys


# The paths to the data files.
path = sys.path[-1] + '/test_suite/shared_data/'

# Create the data pipe.
pipe.create('vectors', 'mf')

# Load the PDB file.
structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path+'structures')

# Load the backbone amide 15N spins from the structure.
structure.load_spins(spin_id='@N')

# Set the XH vectors.
structure.vectors()

# Create the PDB file.
structure.create_vector_dist(file='devnull', force=True)

# PyMOL.
pymol.view()
pymol.cartoon()
pymol.vector_dist()
