# Script for shifting the C-domain to be out of the average rigid body position.

# Python module imports.
from numpy import array, dot, float64, zeros
from numpy.linalg import norm
from sys import stdout

# relax module imports.
from float import floatAsByteArray
from maths_fns.rotation_matrix import axis_angle_to_R, R_random_axis


def to_ieee_754(R):
    """Convert and return the rotation matrix as the full precision IEEE 754 byte array."""

    array = []

    for i in range(3):
        array.append([])
        for j in range(3):
            array[i].append(floatAsByteArray(R[i, j]))

    return array


# Init.
PIVOT_ANGLE = 200.0 / 3.0
PIVOT_ANGLE = PIVOT_ANGLE * (2.0*pi) / 360
PIVOT = array([ 37.254, 0.5, 16.7465])
R_PIVOT = zeros((3, 3), float64)

TORSION_ANGLE = 100 / 3.0
COM_C = array([ 26.83678091, -12.37906417,  28.34154128])
R_TORSION = zeros((3, 3), float64)
VECT_TORSION = COM_C - PIVOT
VECT_TORSION = VECT_TORSION / norm(VECT_TORSION)


# Generate a random pivot rotation.
R_random_axis(R_PIVOT, PIVOT_ANGLE)

# Print out.
print("\nThe pivot rotation angle is: %20.40f" % PIVOT_ANGLE)
print("The pivot rotation angle is: %s" % floatAsByteArray(PIVOT_ANGLE))
print("\nThe pivot rotation matrix is:\n%s" % R_PIVOT)
print("Or:")
float_array = to_ieee_754(R_PIVOT)
for i in range(3):
    print(float_array[i])

# Generate the torsion angle rotation.
axis_angle_to_R(VECT_TORSION, TORSION_ANGLE, R_TORSION)

# Print out.
print("\nThe torsion rotation matrix is:\n%s" % R_TORSION)
print("Or:")
float_array = to_ieee_754(R_TORSION)
for i in range(3):
    print(float_array[i])

# Combine the rotations.
R = dot(R_TORSION, R_PIVOT)

# Print out.
print("\nThe full rotation matrix is:\n%s" % R)
print("Or:")
float_array = to_ieee_754(R)
for i in range(3):
    print(float_array[i])

# Create a data pipe.
pipe.create('rot', 'N-state')

# Load the C-domain PDB file.
structure.read_pdb('1J7P_1st_NH.pdb')

# Rotate all atoms.
structure.rotate(R=R, origin=PIVOT)

# Save the rotated PDB file.
structure.write_pdb('1J7P_1st_NH_rot_new.pdb', force=True)
