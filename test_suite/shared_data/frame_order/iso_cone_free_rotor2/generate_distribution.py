# Script for generating the distribution of PDB structures.

# Python module imports.
from math import acos
from numpy import array, cross, dot, float64, zeros
from numpy.linalg import norm

# relax module imports.
from maths_fns.rotation_matrix import axis_angle_to_R, R_random_hypersphere


# The number of structures.
N = 5000

# Create a data pipe.
pipe.create('generate', 'N-state')

# The axis for the rotations (the pivot point to CoM axis).
pivot = array([ 37.254, 0.5, 16.7465])
com = array([ 26.83678091, -12.37906417,  28.34154128])
axis = com - pivot
axis = axis / norm(axis)

# Init a rotation matrix.
R = zeros((3, 3), float64)

# Tilt the rotation axis by x degrees.
tilt_axis = cross(axis, array([0, 0, 1]))
tilt_axis = tilt_axis / norm(tilt_axis)
axis_angle_to_R(tilt_axis, 15.0 * 2.0 * pi / 360.0, R)
print("Tilt axis: %s, norm = %s" % (repr(tilt_axis), norm(tilt_axis)))
print("CoM-pivot axis: %s, norm = %s" % (repr(axis), norm(axis)))
rot_axis = dot(R, axis)
print("Rotation axis: %s, norm = %s" % (repr(rot_axis), norm(rot_axis)))

# Generate N random rotations within the cone.
i = 0
while True:
    # The random rotation matrix.
    R_random_hypersphere(R)

    # Skip the rotation if the angle is violated.
    new_axis = dot(R, axis)
    angle = acos(dot(rot_axis, new_axis))
    if angle > (20.0 * 2.0 * pi / 360.0):
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
end_pt = rot_axis * norm(pivot - com) + pivot
structure.delete()
structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=pivot, element='C')
structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt, element='N')
structure.connect_atom(index1=0, index2=1)
structure.write_pdb('axis.pdb', compress_type=0, force=True)
