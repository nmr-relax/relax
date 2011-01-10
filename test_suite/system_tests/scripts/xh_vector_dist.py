# System test for creating a PDB representation of the distribution of XH bond vectors.

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# The paths to the data files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

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
