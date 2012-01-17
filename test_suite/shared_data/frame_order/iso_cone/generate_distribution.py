# Script for generating the distribution of PDB structures.

# Python module imports.
from numpy import array, cross, dot, float64, transpose, zeros
from numpy.linalg import norm

# relax module imports.
from generic_fns.angles import wrap_angles
from maths_fns.rotation_matrix import R_random_hypersphere, R_to_tilt_torsion


# Init.
N = 20000
THETA_MAX = 0.2
SIGMA_MAX = 0.3

# Create a data pipe.
pipe.create('generate', 'N-state')

# The z-axis for the rotations (the pivot point to CoM axis).
pivot = array([ 37.254, 0.5, 16.7465])
com = array([ 26.83678091, -12.37906417,  28.34154128])
axis_z = pivot - com
axis_z = axis_z / norm(axis_z)

# A perpendicular axis to check the torsion angle.
axis_x = cross(axis_z, array([0, 0, 1]))
axis_x = axis_x / norm(axis_x)

# Complete the frame.
axis_y = cross(axis_z, axis_x)
axis_y = axis_y / norm(axis_y)
eigen_frame = transpose(array([axis_x, axis_y, axis_z]))

# Init a rotation matrix.
R = zeros((3, 3), float64)

# File for storing the rotation matrices.
rot_file = open('rotation_matrices.py', 'w')
rot_file.write('R = []\n')

# Generate N random rotations within the cone.
i = 0
while 1:
    # The random rotation matrix.
    R_random_hypersphere(R)

    # Rotation in the eigenframe.
    R_eigen = dot(transpose(eigen_frame), dot(R, eigen_frame))

    # The angles.
    phi, theta, sigma = R_to_tilt_torsion(R_eigen)
    sigma = wrap_angles(sigma, -pi, pi)

    # Skip the rotation if the cone angle is violated.
    if theta > THETA_MAX:
        continue

    # Skip the rotation if the torsion angle is violated.
    if sigma > SIGMA_MAX or sigma < -SIGMA_MAX:
        continue

    # Load the PDB as a new model.
    structure.read_pdb('1J7P_1st_NH.pdb', dir='..', set_model_num=i+1)

    # Rotate.
    structure.rotate(R=R, origin=pivot, model=i+1)

    # Save the rotation.
    rot_file.write('R.append(%s)\n' % repr(R))

    # Increment the index.
    i += 1

    # Termination.
    if i >= N:
        break

# Save the PDB file.
structure.write_pdb('distribution.pdb', compress_type=2, force=True)

# Create a PDB for the motional axis system.
end_pt = axis * norm(pivot - com) + pivot
structure.delete()
structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=pivot, element='C')
structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt, element='N')
structure.connect_atom(index1=0, index2=1)
structure.write_pdb('axis.pdb', compress_type=0, force=True)
