# Script for generating the distribution of PDB structures.

# Python module imports.
from numpy import array, float64, zeros
from numpy.linalg import norm

# relax module imports.
from maths_fns.rotation_matrix import axis_angle_to_R


# The number of structures.
INC = 5
N = 360 / INC

# Create a data pipe.
pipe.create('generate', 'N-state')

# The axis for the rotations (the pivot point to CoM axis).
pivot = array([ 37.254, 0.5, 16.7465])
com = array([ 26.83678091, -12.37906417,  28.34154128])
axis = pivot - com
axis = axis / norm(axis)

# Init a rotation matrix.
R = zeros((3, 3), float64)

# Load N copies of the original C-domain, rotating them by 1 degree about the rotation axis.
for i in range(N):
    # Load the PDB as a new model.
    structure.read_pdb('1J7P_1st_NH.pdb', dir='..', set_model_num=i)

    # The rotation angle.
    angle = i * INC / 360.0 * 2.0 * pi
    print("Rotation angle: %s" % angle)

    # The rotation matrix.
    axis_angle_to_R(axis, angle, R)
    print("Rotation matrix:\n%s\n" % R)

    # Rotate.
    structure.rotate(R=R, origin=pivot, model=i)

# Save the PDB file.
structure.write_pdb('distribution.pdb', compress_type=2, force=True)
