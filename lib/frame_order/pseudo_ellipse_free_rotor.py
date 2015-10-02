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

# Python module imports.
from math import cos, pi, sin
try:
    from scipy.integrate import quad
except ImportError:
    pass

# relax module imports.
from lib.geometry.pec import pec
from lib.frame_order.matrix_ops import rotate_daeg
from lib.frame_order.pseudo_ellipse import tmax_pseudo_ellipse


def compile_1st_matrix_pseudo_ellipse_free_rotor(matrix, R_eigen, theta_x, theta_y):
    """Generate the 1st degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param matrix:      The Frame Order matrix, 1st degree to be populated.
    @type matrix:       numpy 3D, rank-2 array
    @param R_eigen:     The eigenframe rotation matrix.
    @type R_eigen:      numpy 3D, rank-2 array
    @param theta_x:     The cone opening angle along x.
    @type theta_x:      float
    @param theta_y:     The cone opening angle along y.
    @type theta_y:      float
    """

    # The surface area normalisation factor.
    fact = 2.0 * pec(theta_x, theta_y)

    # Invert.
    if fact == 0.0:
        fact = 1e100
    else:
        fact = 1.0 / fact

    # Numerical integration of phi of each element.
    matrix[2, 2] = fact * quad(part_int_daeg1_pseudo_ellipse_free_rotor_22, -pi, pi, args=(theta_x, theta_y), full_output=1)[0]

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, R_eigen)


def compile_2nd_matrix_pseudo_ellipse_free_rotor(matrix, Rx2_eigen, theta_x, theta_y):
    """Generate the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param theta_x:     The cone opening angle along x.
    @type theta_x:      float
    @param theta_y:     The cone opening angle along y.
    @type theta_y:      float
    """

    # The surface area normalisation factor.
    fact3 = 3.0 * pec(theta_x, theta_y)
    fact4 = 4.0 * pec(theta_x, theta_y)
    fact6 = 6.0 * pec(theta_x, theta_y)

    # Invert.
    if fact3 == 0.0:
        fact3 = 1e100
        fact4 = 1e100
        fact6 = 1e100
    else:
        fact3 = 1.0 / fact3
        fact4 = 1.0 / fact4
        fact6 = 1.0 / fact6

    # Diagonal.
    matrix[0, 0] = fact6 * (4.0*pi - quad(part_int_daeg2_pseudo_ellipse_free_rotor_00, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[1, 1] = matrix[3, 3] = fact4 * quad(part_int_daeg2_pseudo_ellipse_free_rotor_11, -pi, pi, args=(theta_x, theta_y), full_output=1)[0]
    matrix[4, 4] = fact6 * (4.0*pi - quad(part_int_daeg2_pseudo_ellipse_free_rotor_44, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[8, 8] = fact3 * (2.0*pi - quad(part_int_daeg2_pseudo_ellipse_free_rotor_88, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])

    # Off diagonal set 1.
    matrix[0, 4] = matrix[0, 0]
    matrix[4, 0] = matrix[4, 4]
    matrix[0, 8] = fact3 * (2.0*pi + quad(part_int_daeg2_pseudo_ellipse_free_rotor_08, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[8, 0] = fact6 * (4.0*pi + quad(part_int_daeg2_pseudo_ellipse_free_rotor_80, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[4, 8] = fact3 * (2.0*pi + quad(part_int_daeg2_pseudo_ellipse_free_rotor_48, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[8, 4] = matrix[8, 0]

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = -matrix[1, 1]

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def part_int_daeg1_pseudo_ellipse_free_rotor_22(phi, x, y):
    """The theta-sigma partial integral of the 1st degree Frame Order matrix element zz for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return sin(tmax)**2


def part_int_daeg2_pseudo_ellipse_free_rotor_00(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)

    # The theta-sigma integral.
    return cos(phi)**2 * cos_tmax**3  +  3.0*sin(phi)**2 * cos_tmax


def part_int_daeg2_pseudo_ellipse_free_rotor_08(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)

    # The theta-sigma integral.
    return cos(phi)**2 * (cos_tmax**3 - 3.0*cos_tmax)


def part_int_daeg2_pseudo_ellipse_free_rotor_11(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return sin(tmax)**2


def part_int_daeg2_pseudo_ellipse_free_rotor_44(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)

    # The theta-sigma integral.
    return sin(phi)**2 * cos_tmax**3  +  3.0*cos(phi)**2 * cos_tmax


def part_int_daeg2_pseudo_ellipse_free_rotor_48(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)

    # The theta-sigma integral.
    return sin(phi)**2 * (cos_tmax**3 - 3.0*cos_tmax)


def part_int_daeg2_pseudo_ellipse_free_rotor_80(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)

    # The theta-sigma integral.
    return cos_tmax**3 - 3.0*cos_tmax


def part_int_daeg2_pseudo_ellipse_free_rotor_88(phi, x, y):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the free rotor pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return cos(tmax)**3
