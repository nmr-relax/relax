import __main__
from os import sep
import sys


# Create the data pipe.
pipe.create('mf', 'mf')

# Read a PDB file.
structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

# Load the spins.
structure.load_spins('@N')

# Set the NH vector.
structure.vectors(attached='H')

# Initialise a diffusion tensor.
diffusion_tensor.init((1.698e7, 1.417e7, 67.174, -83.718), param_types=3)

# Display the sequence.
sequence.display()

# Calculate the angles.
angle_diff_frame()
