###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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

# relax module imports.
from lib.frame_order.matrix_ops import rotate_daeg


def compile_1st_matrix_free_rotor(matrix, R_eigen):
    """Generate the 1st degree Frame Order matrix for the free rotor model.

    @param matrix:      The Frame Order matrix, 1st degree to be populated.
    @type matrix:       numpy 3D, rank-2 array
    @param R_eigen:     The eigenframe rotation matrix.
    @type R_eigen:      numpy 3D, rank-2 array
    """

    # Zeros.
    matrix[:] = 0.0

    # The single value.
    matrix[2, 2] = 1.0

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, R_eigen)


def compile_2nd_matrix_free_rotor(matrix, Rx2_eigen):
    """Generate the rotated 2nd degree Frame Order matrix for the free rotor model.

    The rotor axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    """

    # Zeros.
    matrix[:] = 0.0

    # Diagonal.
    matrix[0, 0] = 0.5
    matrix[1, 1] = 0.5
    matrix[3, 3] = 0.5
    matrix[4, 4] = 0.5
    matrix[8, 8] = 1

    # Off diagonal set 1.
    matrix[0, 4] = matrix[4, 0] = 0.5

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = -0.5

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)
