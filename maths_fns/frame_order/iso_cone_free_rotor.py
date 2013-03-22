###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the handling of Frame Order."""

# Python module imports.
from math import cos

# relax module imports.
from maths_fns.frame_order.matrix_ops import rotate_daeg
from maths_fns import order_parameters


def compile_2nd_matrix_iso_cone_free_rotor(matrix, Rx2_eigen, s1):
    """Generate the rotated 2nd degree Frame Order matrix for the free rotor isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.  In this model, the three order parameters are defined as::

        S1 = S2,
        S3 = 0


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param s1:          The cone order parameter.
    @type s1:           float
    """

    # Populate the Frame Order matrix in the eigenframe.
    populate_2nd_eigenframe_iso_cone_free_rotor(matrix, s1)

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def populate_2nd_eigenframe_iso_cone_free_rotor(matrix, s1):
    """Populate the 2nd degree Frame Order matrix in the eigenframe for the free rotor isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.  In this model, the three order parameters are defined as::

        S1 = S2,
        S3 = 0

    This is in the Kronecker product form.


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
    matrix[0, 0] = matrix[4, 4] = (s1 + 2.0) / 6.0
    matrix[0, 4] = matrix[4, 0] = matrix[0, 0]

    # The c33^2 element.
    matrix[8, 8] = (2.0*s1 + 1.0) / 3.0

    # The c13^2, c31^2, c23^2, c32^2 elements.
    matrix[0, 8] = matrix[8, 0] = (1.0 - s1) / 3.0
    matrix[4, 8] = matrix[8, 4] = matrix[0, 8]

    # Calculate the cone angle.
    theta = order_parameters.iso_cone_S_to_theta(s1)

    # The c11.c22 and c12.c21 elements.
    matrix[1, 1] = matrix[3, 3] = (cos(theta) + 1.0) / 4.0
    matrix[1, 3] = matrix[3, 1] = -matrix[1, 1]
