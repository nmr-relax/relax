import sys


# Read the sequence.
sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/system_tests/data')

# Read a PDB file.
structure.read_pdb(file='test.pdb', dir=sys.path[-1] + '/test_suite/system_tests/data', model=1)

# Load the spins.
structure.load_spins('@N')

# Set the NH vector.
structure.vectors(heteronuc='N', proton='H')

# Initialise a diffusion tensor.
diffusion_tensor.init((1.698e7, 1.417e7, 67.174, -83.718), param_types=3)

# Calculate the angles.
angles()
