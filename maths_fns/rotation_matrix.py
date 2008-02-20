###############################################################################
#                                                                             #
# Copyright (C) 2004-2005, 2008 Edward d'Auvergne                             #
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

# Python module imports.
from numpy import dot
from math import cos, sin


def rotation_matrix_zyz(matrix, alpha, beta, gamma):
    """Function for calculating the z-y-z Euler angle convention rotation matrix.

    Unit vectors
    ============

    The unit mux vector is

                | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        mux  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                |                    cos(alpha) * sin(beta)                      |

    The unit muy vector is

                | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        muy  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                |                   sin(alpha) * sin(beta)                      |

    The unit muz vector is

                | -sin(beta) * cos(gamma) |
        muz  =  |  sin(beta) * sin(gamma) |.
                |        cos(beta)        |

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors

        R = [mux, muy, muz].


    @param matrix:  The 3x3 rotation matrix to update.
    @type matrix:   3x3 numpy array
    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    """

    # Trig.
    sin_a = sin(alpha)
    sin_b = sin(beta)
    sin_g = sin(gamma)

    cos_a = cos(alpha)
    cos_b = cos(beta)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    matrix[0,0] = -sin_a * sin_g + cos_a * cos_b * cos_g
    matrix[1,0] = -sin_a * cos_g - cos_a * cos_b * sin_g
    matrix[2,0] =  cos_a * sin_b

    # The unit muy vector component of the rotation matrix.
    matrix[0,1] = cos_a * sin_g + sin_a * cos_b * cos_g
    matrix[1,1] = cos_a * cos_g - sin_a * cos_b * sin_g
    matrix[2,1] = sin_a * sin_b

    # The unit muz vector component of the rotation matrix.
    matrix[0,2] = -sin_b * cos_g
    matrix[1,2] =  sin_b * sin_g
    matrix[2,2] =  cos_b
