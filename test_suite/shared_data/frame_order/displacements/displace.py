# Rotate and translate the pseudo-molecule.

# Python module imports.
from numpy import array, float64, transpose, zeros

# relax module imports.
from lib.geometry.rotations import euler_to_R_zyz, R_to_euler_zyz


# Create a data pipe for the data.
pipe.create('displace', 'N-state')

# Load the structure.
structure.read_pdb('fancy_mol.pdb')

# First rotate.
R = zeros((3, 3), float64)
euler_to_R_zyz(1, 2, 3, R)
origin = array([1, 1, 1], float64)
structure.rotate(R=R, origin=origin)

# Then translate.
T = array([1, 2, 3], float64)
structure.translate(T=T)

# Write out the new structure.
structure.write_pdb('displaced.pdb', force=True)

# Printout of the inverted Euler angles of rotation (the solution).
a, b, g = R_to_euler_zyz(transpose(R))
print("alpha: %s" % a)
print("beta:  %s" % b)
print("gamma: %s" % g)
