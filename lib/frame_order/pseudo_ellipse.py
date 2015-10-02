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
"""Module for the pseudo-ellipse frame order model."""

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import divide, dot, eye, float64, multiply, sinc, swapaxes, tensordot
from numpy import cos as np_cos
from numpy import sin as np_sin
from numpy import sqrt as np_sqrt
try:
    from scipy.integrate import quad, tplquad
except ImportError:
    pass

# relax module imports.
from lib.geometry.pec import pec
from lib.frame_order.matrix_ops import pcs_pivot_motion_full_qr_int, pcs_pivot_motion_full_quad_int, rotate_daeg


def compile_1st_matrix_pseudo_ellipse(matrix, theta_x, theta_y, sigma_max):
    """Generate the 1st degree Frame Order matrix for the pseudo-ellipse.

    @param matrix:      The Frame Order matrix, 1st degree to be populated.
    @type matrix:       numpy 3D, rank-2 array
    @param theta_x:     The cone opening angle along x.
    @type theta_x:      float
    @param theta_y:     The cone opening angle along y.
    @type theta_y:      float
    @param sigma_max:   The maximum torsion angle.
    @type sigma_max:    float
    """

    # The surface area normalisation factor.
    fact = 1.0 / (2.0 * sigma_max * pec(theta_x, theta_y))

    # Numerical integration of phi of each element.
    matrix[0, 0] = fact * quad(part_int_daeg1_pseudo_ellipse_xx, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0]
    matrix[1, 1] = fact * quad(part_int_daeg1_pseudo_ellipse_yy, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0]
    matrix[2, 2] = fact * quad(part_int_daeg1_pseudo_ellipse_zz, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0]


def compile_2nd_matrix_pseudo_ellipse(matrix, Rx2_eigen, theta_x, theta_y, sigma_max):
    """Generate the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param theta_x:     The cone opening angle along x.
    @type theta_x:      float
    @param theta_y:     The cone opening angle along y.
    @type theta_y:      float
    @param sigma_max:   The maximum torsion angle.
    @type sigma_max:    float
    """

    # The rigid case.
    if theta_x == 0.0 and sigma_max == 0.0:
        # Set up the matrix as the identity.
        matrix[:] = 0.0
        for i in range(len(matrix)):
            matrix[i, i] = 1.0

        # Rotate and return the frame order matrix.
        return rotate_daeg(matrix, Rx2_eigen)

    # The surface area normalisation factor.
    fact = 12.0 * pec(theta_x, theta_y)

    # Invert.
    if fact == 0.0:
        fact = 1e100
    else:
        fact = 1.0 / fact

    # Sigma_max part.
    if sigma_max == 0.0:
        fact2 = 1e100
    else:
        fact2 = fact / (2.0 * sigma_max)

    # Diagonal.
    matrix[0, 0] = fact * (4.0*pi*(sinc(2.0*sigma_max/pi) + 2.0) + quad(part_int_daeg2_pseudo_ellipse_00, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[1, 1] = fact * (4.0*pi*sinc(2.0*sigma_max/pi) + quad(part_int_daeg2_pseudo_ellipse_11, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[2, 2] = fact * 2.0*sinc(sigma_max/pi) * (5.0*pi - quad(part_int_daeg2_pseudo_ellipse_22, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[3, 3] = matrix[1, 1]
    matrix[4, 4] = fact * (4.0*pi*(sinc(2.0*sigma_max/pi) + 2.0) + quad(part_int_daeg2_pseudo_ellipse_44, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[5, 5] = fact * 2.0*sinc(sigma_max/pi) * (5.0*pi - quad(part_int_daeg2_pseudo_ellipse_55, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[6, 6] = matrix[2, 2]
    matrix[7, 7] = matrix[5, 5]
    matrix[8, 8] = 4.0 * fact * (2.0*pi - quad(part_int_daeg2_pseudo_ellipse_88, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])

    # Off diagonal set 1.
    matrix[0, 4] = fact * (4.0*pi*(2.0 - sinc(2.0*sigma_max/pi)) + quad(part_int_daeg2_pseudo_ellipse_04, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[4, 0] = fact * (4.0*pi*(2.0 - sinc(2.0*sigma_max/pi)) + quad(part_int_daeg2_pseudo_ellipse_40, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[0, 8] = 4.0 * fact * (2.0*pi - quad(part_int_daeg2_pseudo_ellipse_08, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[8, 0] = fact * (8.0*pi + quad(part_int_daeg2_pseudo_ellipse_80, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[4, 8] = 4.0 * fact * (2.0*pi - quad(part_int_daeg2_pseudo_ellipse_48, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[8, 4] = fact * (8.0*pi - quad(part_int_daeg2_pseudo_ellipse_84, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = fact * (4.0*pi*sinc(2.0*sigma_max/pi) + quad(part_int_daeg2_pseudo_ellipse_13, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[2, 6] = matrix[6, 2] = -fact * 4.0 * sinc(sigma_max/pi) * (2.0*pi + quad(part_int_daeg2_pseudo_ellipse_26, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])
    matrix[5, 7] = matrix[7, 5] = -fact * 4.0 * sinc(sigma_max/pi) * (2.0*pi + quad(part_int_daeg2_pseudo_ellipse_57, -pi, pi, args=(theta_x, theta_y, sigma_max), full_output=1)[0])

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def part_int_daeg1_pseudo_ellipse_xx(phi, x, y, smax):
    """The theta-sigma partial integral of the 1st degree Frame Order matrix element xx for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return sin(smax) * (2 * (1 - cos(tmax)) * sin(phi)**2 + cos(phi)**2 * sin(tmax)**2)


def part_int_daeg1_pseudo_ellipse_yy(phi, x, y, smax):
    """The theta-sigma partial integral of the 1st degree Frame Order matrix element yy for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return sin(smax) * (2.0 * cos(phi)**2 * (1.0 - cos(tmax)) + sin(phi)**2 * sin(tmax)**2)


def part_int_daeg1_pseudo_ellipse_zz(phi, x, y, smax):
    """The theta-sigma partial integral of the 1st degree Frame Order matrix element zz for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return smax * sin(tmax)**2


def part_int_daeg2_pseudo_ellipse_00(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix element 11 for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    cos_phi2 = cos(phi)**2

    # Components.
    a = sinc(2.0*smax/pi) * (2.0 * sin_tmax2 * cos_phi2 * ((2.0*cos_phi2 - 1.0)*cos(tmax)  -  6.0*(cos_phi2 - 1.0)) - 2.0*cos_tmax * (2.0*cos_phi2*(4.0*cos_phi2 - 5.0) + 3.0))
    b = 2.0*cos_phi2*cos_tmax*(sin_tmax2 + 2.0) - 6.0*cos_tmax

    # Return the theta-sigma integral.
    return a + b


def part_int_daeg2_pseudo_ellipse_04(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix element 22 for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    cos_phi2 = cos(phi)**2
    sin_phi2 = sin(phi)**2

    # Components.
    a = sinc(2.0*smax/pi) * (2.0 * sin_tmax2 * cos_phi2 * ((2.0*sin_phi2 - 1.0)*cos(tmax)  -  6.0*sin_phi2) + 2.0*cos_tmax * (2.0*cos_phi2*(4.0*cos_phi2 - 5.0) + 3.0))
    b = 2.0*cos_phi2*cos_tmax*(sin_tmax2 + 2.0) - 6.0*cos_tmax

    # Return the theta-sigma integral.
    return a + b


def part_int_daeg2_pseudo_ellipse_08(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix element 33 for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return cos(tmax) * cos(phi)**2 * (sin(tmax)**2 + 2.0)


def part_int_daeg2_pseudo_ellipse_11(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    cos_phi2 = cos(phi)**2
    sin_phi2 = sin(phi)**2

    # The integral.
    a = sinc(2.0*smax/pi) * ((4.0*cos_phi2*((1.0 - cos_phi2)*cos_tmax + 3.0*(cos_phi2-1)) + 3.0)*sin(tmax)**2 - 16.0*cos_phi2*sin_phi2*cos_tmax) + 3.0*sin(tmax)**2

    # The theta-sigma integral.
    return a


def part_int_daeg2_pseudo_ellipse_13(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    sinc_2smax = sinc(2.0*smax/pi)
    cos_sin_phi2 = cos(phi)**2*sin(phi)**2

    # The theta-sigma integral.
    return sinc_2smax * (sin_tmax2 * (4*cos_sin_phi2*cos_tmax - 12*cos_sin_phi2 + 3) - 16*cos_sin_phi2*cos_tmax) - 3.0*sin_tmax2


def part_int_daeg2_pseudo_ellipse_22(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    cos_phi2 = cos(phi)**2

    # Components.
    a = 2.0*cos_phi2*cos_tmax**3 + 3.0*(1.0 - cos_phi2)*cos_tmax**2

    # Return the theta-sigma integral.
    return a


def part_int_daeg2_pseudo_ellipse_26(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return cos(phi)**2 * (cos(tmax)**3 - 3.0*cos(tmax))


def part_int_daeg2_pseudo_ellipse_40(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    cos_phi2 = cos(phi)**2
    sin_phi2 = sin(phi)**2

    # Components.
    a = sinc(2.0*smax/pi) * (2.0 * sin_tmax2 * sin_phi2 * ((2.0*cos_phi2 - 1.0)*cos(tmax) - 6.0*cos_phi2) + 2.0*cos_tmax * (2.0*sin_phi2*(4.0*sin_phi2 - 5.0) + 3.0))
    b = 2.0*sin_phi2*cos_tmax*(sin_tmax2 + 2.0) - 6.0*cos_tmax

    # Return the theta-sigma integral.
    return a + b


def part_int_daeg2_pseudo_ellipse_44(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    cos_phi2 = cos(phi)**2
    sin_phi2 = sin(phi)**2

    # Components.
    a = sinc(2.0*smax/pi) * (2.0 * sin_tmax2 * sin_phi2 * ((2.0*sin_phi2 - 1.0)*cos(tmax)  +  6.0*cos_phi2) - 2.0*cos_tmax * (2.0*sin_phi2*(4.0*sin_phi2 - 5.0) + 3.0))
    b = 2.0*sin_phi2*cos_tmax*(sin_tmax2 + 2.0) - 6.0*cos_tmax

    # Return the theta-sigma integral.
    return a + b


def part_int_daeg2_pseudo_ellipse_48(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return cos(tmax) * sin(phi)**2 * (sin(tmax)**2 + 2.0)


def part_int_daeg2_pseudo_ellipse_55(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_phi2 = sin(phi)**2

    # Return the theta-sigma integral.
    return 2.0*sin_phi2*cos_tmax**3 + 3.0*(1.0 - sin_phi2)*cos_tmax**2


def part_int_daeg2_pseudo_ellipse_57(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return sin(phi)**2 * (cos(tmax)**3 - 3.0*cos(tmax))


def part_int_daeg2_pseudo_ellipse_80(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    cos_phi2 = cos(phi)**2

    # The theta-sigma integral.
    return sinc(2.0*smax/pi) * (2.0*(1.0 - 2.0*cos_phi2)*cos_tmax*(sin_tmax2 + 2.0)) + 2.0*cos_tmax**3 - 6.0*cos_tmax


def part_int_daeg2_pseudo_ellipse_84(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # Repetitive trig.
    cos_tmax = cos(tmax)
    sin_tmax2 = sin(tmax)**2
    cos_phi2 = cos(phi)**2

    # The theta-sigma integral.
    return sinc(2.0*smax/pi) * (2.0*(1.0 - 2.0*cos_phi2)*cos_tmax*(sin_tmax2 + 2.0)) - 2.0*cos_tmax**3 + 6.0*cos_tmax


def part_int_daeg2_pseudo_ellipse_88(phi, x, y, smax):
    """The theta-sigma partial integral of the 2nd degree Frame Order matrix for the pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    @return:        The theta-sigma partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta-sigma integral.
    return cos(tmax)**3


def pcs_numeric_qr_int_pseudo_ellipse(points=None, max_points=None, theta_x=None, theta_y=None, sigma_max=None, c=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword points:            The Sobol points in the torsion-tilt angle space.
    @type points:               numpy rank-2, 3D array
    @keyword max_points:        The maximum number of Sobol' points to use.  Once this number is reached, the loop over the Sobol' torsion-tilt angles is terminated.
    @type max_points:           int
    @keyword theta_x:           The x-axis half cone angle.
    @type theta_x:              float
    @keyword theta_y:           The y-axis half cone angle.
    @type theta_y:              float
    @keyword sigma_max:         The maximum torsion angle.
    @type sigma_max:            float
    @keyword c:                 The PCS constant (without the interatomic distance and in Angstrom units).
    @type c:                    float
    @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
    @type full_in_ref_frame:    numpy rank-1 array
    @keyword r_pivot_atom:      The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-1, 3D array
    @keyword r_pivot_atom_rev:  The reversed pivot point to atom vector.
    @type r_pivot_atom_rev:     numpy rank-2, 3D array
    @keyword r_ln_pivot:        The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-1, 3D array
    @keyword A:                 The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @keyword R_eigen:           The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @keyword RT_eigen:          The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @keyword Ri_prime:          The array of pre-calculated rotation matrices for the in-frame pseudo-elliptic cone motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri_prime:             numpy rank-3, array of 3D arrays
    @keyword pcs_theta:         The storage structure for the back-calculated PCS values.
    @type pcs_theta:            numpy rank-2 array
    @keyword pcs_theta_err:     The storage structure for the back-calculated PCS errors.
    @type pcs_theta_err:        numpy rank-2 array
    @keyword missing_pcs:       A structure used to indicate which PCS values are missing.
    @type missing_pcs:          numpy rank-2 array
    """

    # Clear the data structures.
    pcs_theta[:] = 0.0
    pcs_theta_err[:] = 0.0

    # Fast frame shift.
    Ri = dot(R_eigen, tensordot(Ri_prime, RT_eigen, axes=1))
    Ri = swapaxes(Ri, 0, 1)

    # Unpack the points.
    theta, phi, sigma = points

    # Calculate theta_max.
    theta_max = tmax_pseudo_ellipse_array(phi, theta_x, theta_y)

    # Loop over the samples.
    num = 0
    for i in range(len(points[0])):
        # The maximum number of points has been reached (well, surpassed by one so exit the loop before it is used).
        if num == max_points:
            break

        # Check the torsion angle first, for speed.
        if abs(sigma[i]) > sigma_max:
            continue

        # As theta_x <= theta_y, check if theta is outside of the isotropic cone defined by theta_y to minimise calculations for speed.
        if theta[i] > theta_y:
            continue

        # Outside of the distribution, so skip the point.
        if theta[i] > theta_max[i]:
            continue

        # Calculate the PCSs for this state.
        pcs_pivot_motion_full_qr_int(full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, A=A, Ri=Ri[i], pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Increment the number of points.
        num += 1

    # Default to the rigid state if no points lie in the distribution.
    if num == 0:
        # Fast identity frame shift.
        Ri_prime = eye(3, dtype=float64)
        Ri = dot(R_eigen, tensordot(Ri_prime, RT_eigen, axes=1))
        Ri = swapaxes(Ri, 0, 1)

        # Calculate the PCSs for this state.
        pcs_pivot_motion_full_qr_int(full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, A=A, Ri=Ri, pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Multiply the constant.
        multiply(c, pcs_theta, pcs_theta)

    # Average the PCS.
    else:
        multiply(c, pcs_theta, pcs_theta)
        divide(pcs_theta, float(num), pcs_theta)


def pcs_numeric_quad_int_pseudo_ellipse(theta_x=None, theta_y=None, sigma_max=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword theta_x:       The x-axis half cone angle.
    @type theta_x:          float
    @keyword theta_y:       The y-axis half cone angle.
    @type theta_y:          float
    @keyword sigma_max:     The maximum torsion angle.
    @type sigma_max:        float
    @keyword c:             The PCS constant (without the interatomic distance and in Angstrom units).
    @type c:                float
    @keyword r_pivot_atom:  The pivot point to atom vector.
    @type r_pivot_atom:     numpy rank-1, 3D array
    @keyword r_ln_pivot:    The lanthanide position to pivot point vector.
    @type r_ln_pivot:       numpy rank-1, 3D array
    @keyword A:             The full alignment tensor of the non-moving domain.
    @type A:                numpy rank-2, 3D array
    @keyword R_eigen:       The eigenframe rotation matrix.
    @type R_eigen:          numpy rank-2, 3D array
    @keyword RT_eigen:      The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:         numpy rank-2, 3D array
    @keyword Ri_prime:      The empty rotation matrix for the in-frame isotropic cone motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri_prime:         numpy rank-2, 3D array
    @return:                The averaged PCS value.
    @rtype:                 float
    """

    def pseudo_ellipse(theta, phi):
        """The pseudo-ellipse wrapper formula."""

        return tmax_pseudo_ellipse(phi, theta_x, theta_y)

    # Perform numerical integration.
    result = tplquad(pcs_pivot_motion_full_quad_int, -sigma_max, sigma_max, lambda phi: -pi, lambda phi: pi, lambda theta, phi: 0.0, pseudo_ellipse, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = 2.0 * sigma_max * pec(theta_x, theta_y)

    # Return the value.
    return c * result[0] / SA


def tmax_pseudo_ellipse(phi, theta_x, theta_y):
    """The pseudo-ellipse tilt-torsion polar angle.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param theta_x: The cone opening angle along x.
    @type theta_x:  float
    @param theta_y: The cone opening angle along y.
    @type theta_y:  float
    @return:        The theta max angle for the given phi angle.
    @rtype:         float
    """

    # Zero points.
    if theta_x == 0.0:
        return 0.0
    elif theta_y == 0.0:
        return 0.0

    # Return the maximum angle.
    return theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)


def tmax_pseudo_ellipse_array(phi, theta_x, theta_y):
    """The pseudo-ellipse tilt-torsion polar angle for numpy arrays.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      numpy rank-1 float64 array
    @param theta_x: The cone opening angle along x.
    @type theta_x:  float
    @param theta_y: The cone opening angle along y.
    @type theta_y:  float
    @return:        The array theta max angles for the given phi angle array.
    @rtype:         numpy rank-1 float64 array
    """

    # Zero points.
    if theta_x == 0.0:
        return 0.0 * phi
    elif theta_y == 0.0:
        return 0.0 * phi

    # Return the maximum angle.
    return theta_x * theta_y / np_sqrt((np_cos(phi)*theta_y)**2 + (np_sin(phi)*theta_x)**2)
