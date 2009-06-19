###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
from math import cos
from numpy import dot, transpose

# relax module imports.
from maths_fns.kronecker_product import kron_prod, transpose_14
from maths_fns.rotation_matrix import R_euler_zyz


def compile_2nd_matrix_iso_cone(matrix, R, alpha, beta, gamma, theta):
    """Generate the rotated 2nd degree Frame Order matrix.

    @param matrix:  The Frame Order matrix, 2nd degree to be populated.
    @type matrix:   numpy 9D, rank-2 array
    @param R:       The rotation matrix to be populated.
    @type R:        numpy 3D, rank-2 array
    @param alpha:   The alpha Euler angle in radians.
    @type alpha:    float
    @param beta:    The beta Euler angle in radians.
    @type beta:     float
    @param gamma:   The gamma Euler angle in radians.
    @type gamma:    float
    @param theta:   The cone angle in radians.
    @type theta:    float
    """

    # Generate the rotation matrix.
    R_euler_zyz(R, alpha, beta, gamma)

    # The outer product of R.
    R_kron = kron_prod(R, R)

    # Populate the Frame Order matrix in the eigenframe.
    populate_2nd_eigenframe_iso_cone(matrix, theta)

    # Perform the T14 transpose to obtain the Kronecker product matrix!
    matrix = transpose_14(matrix)

    # Rotate.
    matrix = dot(R_kron, dot(matrix, transpose(R_kron)))

    # Perform T14 again to return back.
    matrix = transpose_14(matrix)

    # Return the matrix.
    return matrix


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


def populate_2nd_eigenframe_iso_cone(matrix, angle):
    """Populate the 2nd degree Frame Order matrix in the eigenframe for an isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.

    @param matrix:  The Frame Order matrix, 2nd degree.
    @type matrix:   numpy 9D, rank-2 array
    @param angle:   The cone angle.
    @type angle:    float
    """

    # Zeros.
    for i in range(9):
        for j in range(9):
            matrix[i, j] = 0.0

    # Trigonometric terms.
    cos_theta = cos(angle)
    cos2_theta = cos_theta**2

    # The c11^2, c22^2, c12^2, and c21^2 elements.
    matrix[0, 0] = (4.0 + cos_theta + cos2_theta) / 12.0
    matrix[4, 4] = matrix[0, 0]
    matrix[1, 1] = matrix[0, 0]
    matrix[3, 3] = matrix[0, 0]

    # The c33^2 element.
    matrix[8, 8] = (1.0 + cos_theta + cos2_theta) / 3.0

    # The c13^2, c31^2, c23^2, c32^2 elements.
    matrix[2, 2] = (2.0 + cos_theta)*(1.0 - cos_theta) / 6.0
    matrix[6, 6] = matrix[2, 2]
    matrix[5, 5] = matrix[2, 2]
    matrix[7, 7] = matrix[2, 2]

    # The c11.c22 and c12.c21 elements.
    matrix[0, 4] = matrix[4, 0] = (cos_theta + 1.0) / 4.0
    matrix[1, 3] = matrix[3, 1] = -(cos_theta + 1.0) / 4.0


def reduce_alignment_tensor(D, A, red_tensor)
    """Calculate the reduction in the alignment tensor caused by the Frame Order matrix.

    @param D:           The Frame Order matrix, 2nd degree to be populated.
    @type D:            numpy 9D, rank-2 array
    @param A:           The full alignment tensor in {Axx, Ayy, Axy, Axz, Ayz} notation.
    @type A:            numpy 5D, rank-1 array
    @param red_tensor:  The structure in {Axx, Ayy, Axy, Axz, Ayz} notation to place the reduced
                        alignment tensor.
    @type red_tensor:   numpy 5D, rank-1 array
    """

    # Azz.
    Azz = -full_tensor[0] - full_tensor[1]

    # The reduced tensor elements.
    red_tensor[0] = D[0,0]*A[0] + D[3,3]*A[1] + D[6,6]*Azz + 2.0*D[0,3]*A[2] + 2.0*D[0,6]*A[3] + 2.0*D[3,6]*A[4]
    red_tensor[0] = D[1,1]*A[0] + D[4,4]*A[1] + D[7,7]*Azz + 2.0*D[1,4]*A[2] + 2.0*D[1,7]*A[3] + 2.0*D[4,7]*A[4]
    red_tensor[0] = D[0,1]*A[0] + D[3,4]*A[1] + D[6,7]*Azz + 2.0*D[0,4]*A[2] + 2.0*D[0,7]*A[3] + 2.0*D[3,7]*A[4]
    red_tensor[0] = D[0,2]*A[0] + D[3,5]*A[1] + D[6,8]*Azz + 2.0*D[0,5]*A[2] + 2.0*D[0,8]*A[3] + 2.0*D[3,8]*A[4]
    red_tensor[0] = D[1,2]*A[0] + D[4,5]*A[1] + D[7,8]*Azz + 2.0*D[1,5]*A[2] + 2.0*D[1,8]*A[3] + 2.0*D[4,8]*A[4]
