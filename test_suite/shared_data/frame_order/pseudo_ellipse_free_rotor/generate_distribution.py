# Script for generating the distribution of PDB structures.

# Python module imports.
from math import acos, atan2, cos, sin, sqrt
from numpy import array, cross, dot, float64, transpose, zeros
from numpy.linalg import inv, norm

# relax module imports.
from generic_fns.angles import wrap_angles
from maths_fns.rotation_matrix import R_random_hypersphere, R_to_tilt_torsion


# Init.
N = 25000
THETA_X = 0.5
THETA_Y = 0.1
SIGMA_MAX = pi

# Create a data pipe.
pipe.create('generate', 'N-state')

# The z-axis for the rotations (the pivot point to CoM axis).
pivot = array([ 37.254, 0.5, 16.7465])
com = array([ 26.83678091, -12.37906417,  28.34154128])
axis_z = com - pivot
axis_z = axis_z / norm(axis_z)

# The y-axis (to check the torsion angle).
axis_y = cross(axis_z, array([0, 0, 1]))
axis_y = axis_y / norm(axis_y)

# The x-axis.
axis_x = cross(axis_y, axis_z)
axis_x = axis_x / norm(axis_x)

# The eigenframe.
eigen_frame = transpose(array([axis_x, axis_y, axis_z]))

# Init a rotation matrix.
R = zeros((3, 3), float64)

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

    # Determine theta_max.
    theta_max = 1.0 / sqrt((cos(phi) / THETA_X)**2 + (sin(phi) / THETA_Y)**2)

    # Skip the rotation if the cone angle is violated.
    if theta > theta_max:
        continue

    # Skip the rotation if the torsion angle is violated.
    if sigma > SIGMA_MAX or sigma < -SIGMA_MAX:
        continue

    # Load the PDB as a new model.
    structure.read_pdb('1J7P_1st_NH.pdb', dir='..', set_model_num=i+1)

    # Rotate.
    structure.rotate(R=R, origin=pivot, model=i+1)

    # Increment the index.
    i += 1

    # Termination.
    if i > N:
        break

# Save the PDB file.
structure.write_pdb('distribution.pdb', compress_type=2, force=True)

# Create a PDB for the motional axis system.
end_pt_x = axis_x * norm(pivot - com) + pivot
end_pt_y = axis_y * norm(pivot - com) + pivot
end_pt_z = axis_z * norm(pivot - com) + pivot
structure.delete()
structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=pivot, element='C')
structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_x, element='N')
structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_y, element='N')
structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_z, element='N')
structure.connect_atom(index1=0, index2=1)
structure.connect_atom(index1=0, index2=2)
structure.connect_atom(index1=0, index2=3)
structure.write_pdb('axis.pdb', compress_type=0, force=True)
