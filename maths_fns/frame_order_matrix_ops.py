###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the handling of Frame Order."""

# Python module imports.
from math import cos, sin
from numpy import cross, dot, transpose
from numpy.linalg import norm

# relax module imports.
from float import isNaN
from maths_fns import order_parameters
from maths_fns.kronecker_product import kron_prod, transpose_23
from maths_fns.rotation_matrix import two_vect_to_R


def compile_2nd_matrix_iso_cone(matrix, R, z_axis, cone_axis, theta_axis, phi_axis, s1):
    """Generate the rotated 2nd degree Frame Order matrix.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.  In this model, the three order parameters are defined as::

        S1 = S2,
        S3 = 0


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param R:           The rotation matrix to be populated.
    @type R:            numpy 3D, rank-2 array
    @param z_axis:      The molecular frame z-axis from which the cone axis is rotated from.
    @type z_axis:       numpy 3D, rank-1 array
    @param cone_axis:   The storage structure for the cone axis.
    @type cone_axis:    numpy 3D, rank-1 array
    @param theta_axis:  The cone axis polar angle.
    @type theta_axis:   float
    @param phi_axis:    The cone axis azimuthal angle.
    @type phi_axis:     float
    @param s1:          The cone order parameter.
    @type s1:           float
    """

    # Generate the cone axis from the spherical angles.
    generate_vector(cone_axis, theta_axis, phi_axis)

    # Generate the rotation matrix.
    two_vect_to_R(z_axis, cone_axis, R)

    # The outer product of R.
    R_kron = kron_prod(R, R)

    # Populate the Frame Order matrix in the eigenframe.
    populate_2nd_eigenframe_iso_cone(matrix, s1)

    # Perform the T23 transpose to obtain the Kronecker product matrix!
    transpose_23(matrix)

    # Rotate.
    matrix = dot(R_kron, dot(matrix, transpose(R_kron)))

    # Perform T23 again to return back.
    transpose_23(matrix)

    # Return the matrix.
    return matrix


def daeg_to_rotational_superoperator(daeg, Rsuper):
    """Convert the frame order matrix (daeg) to the rotational superoperator.

    @param daeg:    The second degree frame order matrix, daeg.
    @type daeg:     numpy 9D, rank-2 array or numpy 3D, rank-4 array
    @param Rsuper:  The rotational superoperator structure to be populated.
    @type Rsuper:   numpy 5D, rank-2 array
    """

    # Convert to rank-4.
    orig_shape = daeg.shape
    daeg.shape = (3, 3, 3, 3)

    # First column of the superoperator.
    Rsuper[0, 0] = daeg[0, 0, 0, 0] - daeg[2, 0, 2, 0]
    Rsuper[1, 0] = daeg[0, 1, 0, 1] - daeg[2, 1, 2, 1]
    Rsuper[2, 0] = daeg[0, 0, 0, 1] - daeg[2, 0, 2, 1]
    Rsuper[3, 0] = daeg[0, 0, 0, 2] - daeg[2, 0, 2, 2]
    Rsuper[4, 0] = daeg[0, 1, 0, 2] - daeg[2, 1, 2, 2]

    # Second column of the superoperator.
    Rsuper[0, 1] = daeg[1, 0, 1, 0] - daeg[2, 0, 2, 0]
    Rsuper[1, 1] = daeg[1, 1, 1, 1] - daeg[2, 1, 2, 1]
    Rsuper[2, 1] = daeg[1, 0, 1, 1] - daeg[2, 0, 2, 1]
    Rsuper[3, 1] = daeg[1, 0, 1, 2] - daeg[2, 0, 2, 2]
    Rsuper[4, 1] = daeg[1, 1, 1, 2] - daeg[2, 1, 2, 2]

    # Third column of the superoperator.
    Rsuper[0, 2] = daeg[0, 0, 1, 0] + daeg[1, 0, 0, 0]
    Rsuper[1, 2] = daeg[0, 1, 1, 1] + daeg[1, 1, 0, 1]
    Rsuper[2, 2] = daeg[0, 0, 1, 1] + daeg[1, 0, 0, 1]
    Rsuper[3, 2] = daeg[0, 0, 1, 2] + daeg[1, 0, 0, 2]
    Rsuper[4, 2] = daeg[0, 1, 1, 2] + daeg[1, 1, 0, 2]

    # Fourth column of the superoperator.
    Rsuper[0, 3] = daeg[0, 0, 2, 0] + daeg[2, 0, 0, 0]
    Rsuper[1, 3] = daeg[0, 1, 2, 1] + daeg[2, 1, 0, 1]
    Rsuper[2, 3] = daeg[0, 0, 2, 1] + daeg[2, 0, 0, 1]
    Rsuper[3, 3] = daeg[0, 0, 2, 2] + daeg[2, 0, 0, 2]
    Rsuper[4, 3] = daeg[0, 1, 2, 2] + daeg[2, 1, 0, 2]

    # Fifth column of the superoperator.
    Rsuper[0, 4] = daeg[1, 0, 2, 0] + daeg[2, 0, 1, 0]
    Rsuper[1, 4] = daeg[1, 1, 2, 1] + daeg[2, 1, 1, 1]
    Rsuper[2, 4] = daeg[1, 0, 2, 1] + daeg[2, 0, 1, 1]
    Rsuper[3, 4] = daeg[1, 0, 2, 2] + daeg[2, 0, 1, 2]
    Rsuper[4, 4] = daeg[1, 1, 2, 2] + daeg[2, 1, 1, 2]

    # Revert the shape.
    daeg.shape = orig_shape


def generate_vector(vector, theta, phi):
    """Generate a unit vector from the polar angle theta and azimuthal angle phi.

    @param vector:  The storage structure for the vector.
    @type vector:   numpy 3D, rank-1 array
    @param theta:   The polar angle.
    @type theta:    float
    @param phi:     The azimuthal angle.
    @type phi:      float
    """

    # Trig alias.
    sin_theta = sin(theta)

    # The vector.
    vector[0] = cos(phi) * sin_theta
    vector[1] = sin(phi) * sin_theta
    vector[2] = cos(theta)


def populate_1st_eigenframe_iso_cone(matrix, angle):
    """Populate the 1st degree Frame Order matrix in the eigenframe for an isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.

    @param matrix:  The Frame Order matrix, 1st degree.
    @type matrix:   numpy 3D, rank-2 array
    @param angle:   The cone angle.
    @type angle:    float
    """

    # Zeros.
    for i in range(3):
        for j in range(3):
            matrix[i, j] = 0.0

    # The c33 element.
    matrix[2, 2] = (cos(angle) + 1.0) / 2.0


def populate_2nd_eigenframe_iso_cone(matrix, s1):
    """Populate the 2nd degree Frame Order matrix in the eigenframe for an isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.  In this model, the three order parameters are defined as::

        S1 = S2,
        S3 = 0


    @param matrix:  The Frame Order matrix, 2nd degree.
    @type matrix:   numpy 9D, rank-2 array
    @param s1:      The cone order parameter.
    @type s1:       float
    """

    # Zeros.
    for i in range(9):
        for j in range(9):
            matrix[i, j] = 0.0

    # The c11^2, c22^2, c12^2, and c21^2 elements.
    matrix[0, 0] = (s1 + 2.0) / 6.0
    matrix[4, 4] = matrix[0, 0]
    matrix[1, 1] = matrix[0, 0]
    matrix[3, 3] = matrix[0, 0]

    # The c33^2 element.
    matrix[8, 8] = (2.0*s1 + 1.0) / 3.0

    # The c13^2, c31^2, c23^2, c32^2 elements.
    matrix[2, 2] = (1.0 - s1) / 3.0
    matrix[6, 6] = matrix[2, 2]
    matrix[5, 5] = matrix[2, 2]
    matrix[7, 7] = matrix[2, 2]

    # Calculate the cone angle.
    cos_theta = order_parameters.iso_cone_S_to_cos_theta(s1)

    # The c11.c22 and c12.c21 elements.
    matrix[0, 4] = matrix[4, 0] = (cos_theta + 1.0) / 4.0
    matrix[1, 3] = matrix[3, 1] = -(cos_theta + 1.0) / 4.0


def reduce_alignment_tensor(D, A, red_tensor):
    """Calculate the reduction in the alignment tensor caused by the Frame Order matrix.

    This is the forward rotation notation.

    @param D:           The Frame Order matrix, 2nd degree to be populated.
    @type D:            numpy 9D, rank-2 array
    @param A:           The full alignment tensor in {Axx, Ayy, Axy, Axz, Ayz} notation.
    @type A:            numpy 5D, rank-1 array
    @param red_tensor:  The structure in {Axx, Ayy, Axy, Axz, Ayz} notation to place the reduced
                        alignment tensor.
    @type red_tensor:   numpy 5D, rank-1 array
    """

    # The reduced tensor element A0.
    red_tensor[0] =                 (D[0, 0] - D[2, 2])*A[0]
    red_tensor[0] = red_tensor[0] + (D[1, 1] - D[2, 2])*A[1]
    red_tensor[0] = red_tensor[0] + 2.0*D[0, 1]*A[2]
    red_tensor[0] = red_tensor[0] + 2.0*D[0, 2]*A[3]
    red_tensor[0] = red_tensor[0] + 2.0*D[1, 2]*A[4]

    # The reduced tensor element A1.
    red_tensor[1] =                 (D[3, 3] - D[5, 5])*A[0]
    red_tensor[1] = red_tensor[1] + (D[4, 4] - D[5, 5])*A[1]
    red_tensor[1] = red_tensor[1] + 2.0*D[3, 4]*A[2]
    red_tensor[1] = red_tensor[1] + 2.0*D[3, 5]*A[3]
    red_tensor[1] = red_tensor[1] + 2.0*D[4, 5]*A[4]

    # The reduced tensor element A2.
    red_tensor[2] =                 (D[0, 3] - D[2, 5])*A[0] 
    red_tensor[2] = red_tensor[2] + (D[1, 4] - D[2, 5])*A[1] 
    red_tensor[2] = red_tensor[2] + (D[0, 4] + D[1, 3])*A[2] 
    red_tensor[2] = red_tensor[2] + (D[0, 5] + D[2, 3])*A[3] 
    red_tensor[2] = red_tensor[2] + (D[1, 5] + D[2, 4])*A[4]

    # The reduced tensor element A3.
    red_tensor[3] =                 (D[0, 6] - D[2, 8])*A[0] 
    red_tensor[3] = red_tensor[3] + (D[1, 7] - D[2, 8])*A[1] 
    red_tensor[3] = red_tensor[3] + (D[0, 7] + D[1, 6])*A[2] 
    red_tensor[3] = red_tensor[3] + (D[0, 8] + D[2, 6])*A[3] 
    red_tensor[3] = red_tensor[3] + (D[1, 8] + D[2, 7])*A[4]

    # The reduced tensor element A4.
    red_tensor[4] =                 (D[3, 6] - D[5, 8])*A[0] 
    red_tensor[4] = red_tensor[4] + (D[4, 7] - D[5, 8])*A[1] 
    red_tensor[4] = red_tensor[4] + (D[3, 7] + D[4, 6])*A[2] 
    red_tensor[4] = red_tensor[4] + (D[3, 8] + D[5, 6])*A[3] 
    red_tensor[4] = red_tensor[4] + (D[4, 8] + D[5, 7])*A[4]


def reduce_alignment_tensor_reverse(D, A, red_tensor):
    """Calculate the reduction in the alignment tensor caused by the Frame Order matrix.

    This is the reverse rotation notation.

    @param D:           The Frame Order matrix, 2nd degree to be populated.
    @type D:            numpy 9D, rank-2 array
    @param A:           The full alignment tensor in {Axx, Ayy, Axy, Axz, Ayz} notation.
    @type A:            numpy 5D, rank-1 array
    @param red_tensor:  The structure in {Axx, Ayy, Axy, Axz, Ayz} notation to place the reduced
                        alignment tensor.
    @type red_tensor:   numpy 5D, rank-1 array
    """

    # The reduced tensor element A0.
    red_tensor[0] =                 (D[0, 0] - D[6, 6])*A[0]
    red_tensor[0] = red_tensor[0] + (D[3, 3] - D[6, 6])*A[1]
    red_tensor[0] = red_tensor[0] + 2.0*D[0, 3]*A[2]
    red_tensor[0] = red_tensor[0] + 2.0*D[0, 6]*A[3]
    red_tensor[0] = red_tensor[0] + 2.0*D[3, 6]*A[4]

    # The reduced tensor element A1.
    red_tensor[1] =                 (D[1, 1] - D[7, 7])*A[0]
    red_tensor[1] = red_tensor[1] + (D[4, 4] - D[7, 7])*A[1]
    red_tensor[1] = red_tensor[1] + 2.0*D[1, 4]*A[2]
    red_tensor[1] = red_tensor[1] + 2.0*D[1, 7]*A[3]
    red_tensor[1] = red_tensor[1] + 2.0*D[4, 7]*A[4]

    # The reduced tensor element A2.
    red_tensor[2] =                 (D[0, 1] - D[6, 7])*A[0] 
    red_tensor[2] = red_tensor[2] + (D[3, 4] - D[6, 7])*A[1] 
    red_tensor[2] = red_tensor[2] + (D[0, 4] + D[1, 3])*A[2] 
    red_tensor[2] = red_tensor[2] + (D[0, 7] + D[1, 6])*A[3] 
    red_tensor[2] = red_tensor[2] + (D[3, 7] + D[4, 6])*A[4]

    # The reduced tensor element A3.
    red_tensor[3] =                 (D[0, 2] - D[6, 8])*A[0] 
    red_tensor[3] = red_tensor[3] + (D[3, 5] - D[6, 8])*A[1] 
    red_tensor[3] = red_tensor[3] + (D[0, 5] + D[2, 3])*A[2] 
    red_tensor[3] = red_tensor[3] + (D[0, 8] + D[2, 6])*A[3] 
    red_tensor[3] = red_tensor[3] + (D[3, 8] + D[5, 6])*A[4]

    # The reduced tensor element A4.
    red_tensor[4] =                 (D[1, 2] - D[7, 8])*A[0] 
    red_tensor[4] = red_tensor[4] + (D[4, 5] - D[7, 8])*A[1] 
    red_tensor[4] = red_tensor[4] + (D[1, 5] + D[2, 4])*A[2] 
    red_tensor[4] = red_tensor[4] + (D[1, 8] + D[2, 7])*A[3] 
    red_tensor[4] = red_tensor[4] + (D[4, 8] + D[5, 7])*A[4]
