###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Edward d'Auvergne                                   #
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

# Dependency check module.
import dep_check

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import cross, dot, sinc, transpose
from numpy.linalg import norm
if dep_check.scipy_module:
    from scipy.integrate import dblquad, quad, tplquad

# relax module imports.
from float import isNaN
from maths_fns import order_parameters
from maths_fns.coord_transform import spherical_to_cartesian
from maths_fns.kronecker_product import kron_prod, transpose_23
from maths_fns.pseudo_ellipse import pec
from maths_fns.rotation_matrix import euler_to_R_zyz, two_vect_to_R


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


def compile_2nd_matrix_free_rotor(matrix, Rx2_eigen):
    """Generate the rotated 2nd degree Frame Order matrix for the free rotor model.

    The rotor axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    """

    # Zeros.
    for i in range(9):
        for j in range(9):
            matrix[i, j] = 0.0

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


def compile_2nd_matrix_iso_cone(matrix, Rx2_eigen, cone_theta, sigma_max):
    """Generate the rotated 2nd degree Frame Order matrix for the isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.

    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param cone_theta:  The cone opening angle.
    @type cone_theta:   float
    @param sigma_max:   The maximum torsion angle.
    @type sigma_max:    float
    """

    # Populate the Frame Order matrix in the eigenframe.
    populate_2nd_eigenframe_iso_cone(matrix, cone_theta, sigma_max)

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


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


def compile_2nd_matrix_iso_cone_torsionless(matrix, Rx2_eigen, cone_theta):
    """Generate the rotated 2nd degree Frame Order matrix for the torsionless isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param cone_theta:  The cone opening angle.
    @type cone_theta:   float
    """

    # Zeros.
    for i in range(9):
        for j in range(9):
            matrix[i, j] = 0.0

    # Repetitive trig calculations.
    cos_tmax = cos(cone_theta)
    cos_tmax2 = cos_tmax**2

    # Diagonal.
    matrix[0, 0] = (3.0*cos_tmax2 + 6.0*cos_tmax + 15.0) / 24.0
    matrix[1, 1] = (cos_tmax2 + 10.0*cos_tmax + 13.0) / 24.0
    matrix[2, 2] = (4.0*cos_tmax2 + 10.0*cos_tmax + 10.0) / 24.0
    matrix[3, 3] = matrix[1, 1]
    matrix[4, 4] = matrix[0, 0]
    matrix[5, 5] = matrix[2, 2]
    matrix[6, 6] = matrix[2, 2]
    matrix[7, 7] = matrix[2, 2]
    matrix[8, 8] = (cos_tmax2 + cos_tmax + 1.0) / 3.0

    # Off diagonal set 1.
    matrix[0, 4] = matrix[4, 0] = (cos_tmax2 - 2.0*cos_tmax + 1.0) / 24.0
    matrix[0, 8] = matrix[8, 0] = -(cos_tmax2 + cos_tmax - 2.0) / 6.0
    matrix[4, 8] = matrix[8, 4] = matrix[0, 8]

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = matrix[0, 4]
    matrix[2, 6] = matrix[6, 2] = -matrix[0, 8]
    matrix[5, 7] = matrix[7, 5] = -matrix[0, 8]

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


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
    fact = 1.0 / (6.0 * pec(theta_x, theta_y))

    # Diagonal.
    matrix[0, 0] = fact * (4.0*pi - quad(part_int_daeg2_pseudo_ellipse_free_rotor_00, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[1, 1] = matrix[3, 3] = fact * 3.0/2.0 * quad(part_int_daeg2_pseudo_ellipse_free_rotor_11, -pi, pi, args=(theta_x, theta_y), full_output=1)[0]
    matrix[4, 4] = fact * (4.0*pi - quad(part_int_daeg2_pseudo_ellipse_free_rotor_44, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[8, 8] = fact * (4.0*pi - 2.0*quad(part_int_daeg2_pseudo_ellipse_free_rotor_88, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])

    # Off diagonal set 1.
    matrix[0, 4] = matrix[0, 0]
    matrix[4, 0] = matrix[4, 4]
    matrix[0, 8] = fact * (4.0*pi + quad(part_int_daeg2_pseudo_ellipse_free_rotor_08, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[8, 0] = fact * (4.0*pi + quad(part_int_daeg2_pseudo_ellipse_free_rotor_80, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[4, 8] = fact * (4.0*pi + quad(part_int_daeg2_pseudo_ellipse_free_rotor_48, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[8, 4] = matrix[8, 0]

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = -matrix[1, 1]

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def compile_2nd_matrix_pseudo_ellipse_torsionless(matrix, Rx2_eigen, theta_x, theta_y):
    """Generate the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

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
    fact = 1.0 / (6.0 * pec(theta_x, theta_y))

    # Diagonal.
    matrix[0, 0] = fact * (6.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_00, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[1, 1] = fact * (2.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_11, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[2, 2] = fact * (5.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_22, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[3, 3] = matrix[1, 1]
    matrix[4, 4] = fact * (6.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_44, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[5, 5] = fact * (5.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_55, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[6, 6] = matrix[2, 2]
    matrix[7, 7] = matrix[5, 5]
    matrix[8, 8] = fact * quad(part_int_daeg2_pseudo_ellipse_torsionless_88, -pi, pi, args=(theta_x, theta_y), full_output=1)[0]

    # Off diagonal set 1.
    matrix[0, 4] = matrix[4, 0] = fact * (2.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_04, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[0, 8] = matrix[8, 0] = fact * (4.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_08, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])
    matrix[4, 8] = matrix[8, 4] = fact * (4.0*pi + quad(part_int_daeg2_pseudo_ellipse_torsionless_48, -pi, pi, args=(theta_x, theta_y), full_output=1)[0])

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = matrix[0, 4]
    matrix[2, 6] = matrix[6, 2] = -matrix[0, 8]
    matrix[5, 7] = matrix[7, 5] = -matrix[4, 8]

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def compile_2nd_matrix_rotor(matrix, Rx2_eigen, smax):
    """Generate the rotated 2nd degree Frame Order matrix for the rotor model.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param smax:        The maximum torsion angle.
    @type smax:         float
    """

    # Zeros.
    for i in range(9):
        for j in range(9):
            matrix[i, j] = 0.0

    # Repetitive trig calculations.
    sinc_smax = sinc(smax/pi)
    sinc_2smax = sinc(2.0*smax/pi)

    # Diagonal.
    matrix[0, 0] = (sinc_2smax + 1.0) / 2.0
    matrix[1, 1] = matrix[0, 0]
    matrix[2, 2] = sinc_smax
    matrix[3, 3] = matrix[0, 0]
    matrix[4, 4] = matrix[0, 0]
    matrix[5, 5] = matrix[2, 2]
    matrix[6, 6] = matrix[2, 2]
    matrix[7, 7] = matrix[2, 2]
    matrix[8, 8] = 1.0

    # Off diagonal set 1.
    matrix[0, 4] = matrix[4, 0] = -(sinc_2smax - 1.0) / 2.0

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = -matrix[0, 4]

    # Rotate and return the frame order matrix.
    return rotate_daeg(matrix, Rx2_eigen)


def daeg_to_rotational_superoperator(daeg, Rsuper):
    """Convert the frame order matrix (daeg) to the rotational superoperator.

    @param daeg:    The second degree frame order matrix, daeg.  This must be in the Kronecker product layout.
    @type daeg:     numpy 9D, rank-2 array or numpy 3D, rank-4 array
    @param Rsuper:  The rotational superoperator structure to be populated.
    @type Rsuper:   numpy 5D, rank-2 array
    """

    # First perform the T23 transpose.
    transpose_23(daeg)

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

    # Undo the T23 transpose.
    transpose_23(daeg)


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

    # The theta-sigma integral.
    return cos(phi)**2*cos(tmax)**3 + 3.0*sin(phi)**2*cos(tmax)


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

    # The theta-sigma integral.
    return cos(phi)**2*(2.0*cos(tmax)**3 - 6.0*cos(tmax))


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

    # The theta-sigma integral.
    return sin(phi)**2*cos(tmax)**3 + 3*cos(phi)**2*cos(tmax)


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

    # The theta-sigma integral.
    return sin(phi)**2*(2.0*cos(tmax)**3 - 6.0*cos(tmax))


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

    # The theta-sigma integral.
    return cos(tmax)**3 - 3.0*cos(tmax)


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


def part_int_daeg2_pseudo_ellipse_torsionless_00(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return (2*cos(phi)**4*cos(tmax) + 6*cos(phi)**2*sin(phi)**2)*sin(tmax)**2 - (6*sin(phi)**4 + 2*cos(phi)**4)*cos(tmax)


def part_int_daeg2_pseudo_ellipse_torsionless_04(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return (2*cos(phi)**2*sin(phi)**2*cos(tmax) - 6*cos(phi)**2*sin(phi)**2)*sin(tmax)**2 - 8*cos(phi)**2*sin(phi)**2*cos(tmax)


def part_int_daeg2_pseudo_ellipse_torsionless_08(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return 2*cos(phi)**2*cos(tmax)**3 - 6*cos(phi)**2*cos(tmax)


def part_int_daeg2_pseudo_ellipse_torsionless_11(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return (2*cos(phi)**2*sin(phi)**2*cos(tmax) + 3*sin(phi)**4 + 3*cos(phi)**4)*sin(tmax)**2 - 8*cos(phi)**2*sin(phi)**2*cos(tmax)


def part_int_daeg2_pseudo_ellipse_torsionless_22(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return (2*sin(phi)**2 - 2)*cos(tmax)**3 - 3*sin(phi)**2*cos(tmax)**2


def part_int_daeg2_pseudo_ellipse_torsionless_44(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return (2*sin(phi)**4*cos(tmax) + 6*cos(phi)**2*sin(phi)**2)*sin(tmax)**2 - (2*sin(phi)**4 + 6*cos(phi)**4)*cos(tmax)


def part_int_daeg2_pseudo_ellipse_torsionless_48(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return 2*sin(phi)**2*cos(tmax)**3 - 6*sin(phi)**2*cos(tmax)


def part_int_daeg2_pseudo_ellipse_torsionless_55(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return (2*cos(phi)**2 - 2)*cos(tmax)**3 - 3*cos(phi)**2*cos(tmax)**2


def part_int_daeg2_pseudo_ellipse_torsionless_88(phi, x, y):
    """The theta partial integral of the 2nd degree Frame Order matrix for the torsionless pseudo-ellipse.

    @param phi:     The azimuthal tilt-torsion angle.
    @type phi:      float
    @param x:       The cone opening angle along x.
    @type x:        float
    @param y:       The cone opening angle along y.
    @type y:        float
    @return:        The theta partial integral.
    @rtype:         float
    """

    # Theta max.
    tmax = tmax_pseudo_ellipse(phi, x, y)

    # The theta integral.
    return 2 - 2*cos(tmax)**3


def pcs_numeric_int_iso_cone(theta_max=None, sigma_max=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword theta_max:     The half cone angle.
    @type theta_max:        float
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

    # Perform numerical integration.
    result = tplquad(pcs_pivot_motion_full, -sigma_max, sigma_max, lambda phi: -pi, lambda phi: pi, lambda theta, phi: 0.0, lambda theta, phi: theta_max, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = 4.0 * pi * sigma_max * (1.0 - cos(theta_max))

    # Return the value.
    return c * result[0] / SA


def pcs_numeric_int_iso_cone_torsionless(theta_max=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword theta_max:     The half cone angle.
    @type theta_max:        float
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

    # Perform numerical integration.
    result = dblquad(pcs_pivot_motion_torsionless, -pi, pi, lambda phi: 0.0, lambda phi: theta_max, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = 2.0 * pi * (1.0 - cos(theta_max))

    # Return the value.
    return c * result[0] / SA


def pcs_numeric_int_pseudo_ellipse(theta_x=None, theta_y=None, sigma_max=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
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
    result = tplquad(pcs_pivot_motion_full, -sigma_max, sigma_max, lambda phi: -pi, lambda phi: pi, lambda theta, phi: 0.0, pseudo_ellipse, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = 2.0 * sigma_max * pec(theta_x, theta_y)

    # Return the value.
    return c * result[0] / SA


def pcs_numeric_int_pseudo_ellipse_torsionless(theta_x=None, theta_y=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword theta_x:       The x-axis half cone angle.
    @type theta_x:          float
    @keyword theta_y:       The y-axis half cone angle.
    @type theta_y:          float
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

    def pseudo_ellipse(phi):
        """The pseudo-ellipse wrapper formula."""

        return tmax_pseudo_ellipse(phi, theta_x, theta_y)

    # Perform numerical integration.
    result = dblquad(pcs_pivot_motion_torsionless, -pi, pi, lambda phi: 0.0, pseudo_ellipse, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = pec(theta_x, theta_y)

    # Return the value.
    return c * result[0] / SA


def pcs_numeric_int_rotor(sigma_max=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword sigma_max:     The maximum rotor angle.
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
    @keyword Ri_prime:      The empty rotation matrix for the in-frame rotor motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri_prime:         numpy rank-2, 3D array
    @return:                The averaged PCS value.
    @rtype:                 float
    """

    # Preset the rotation matrix elements for state i.
    Ri_prime[0, 2] = 0.0
    Ri_prime[1, 2] = 0.0
    Ri_prime[2, 0] = 0.0
    Ri_prime[2, 1] = 0.0
    Ri_prime[2, 2] = 1.0

    # Perform numerical integration.
    result = quad(pcs_pivot_motion_rotor, -sigma_max, sigma_max, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = 2.0 * sigma_max

    # Return the value.
    return c * result[0] / SA


def pcs_pivot_motion_full(theta_i, phi_i, sigma_i, r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime):
    """Calculate the PCS value after a pivoted motion for the isotropic cone model.

    @param theta_i:             The half cone opening angle (polar angle).
    @type theta_i:              float
    @param phi_i:               The cone azimuthal angle.
    @type phi_i:                float
    @param sigma_i:             The torsion angle for state i.
    @type sigma_i:              float
    @param r_pivot_atom:        The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-1, 3D array
    @param r_ln_pivot:          The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-1, 3D array
    @param A:                   The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @param R_eigen:             The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @param RT_eigen:            The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @param Ri_prime:            The empty rotation matrix for the in-frame isotropic cone motion for state i.
    @type Ri_prime:             numpy rank-2, 3D array
    @return:                    The PCS value for the changed position.
    @rtype:                     float
    """

    # The rotation matrix.
    c_theta = cos(theta_i)
    s_theta = sin(theta_i)
    c_phi = cos(phi_i)
    s_phi = sin(phi_i)
    c_sigma_phi = cos(sigma_i - phi_i)
    s_sigma_phi = sin(sigma_i - phi_i)
    c_phi_c_theta = c_phi * c_theta
    s_phi_c_theta = s_phi * c_theta
    Ri_prime[0, 0] =  c_phi_c_theta*c_sigma_phi - s_phi*s_sigma_phi
    Ri_prime[0, 1] = -c_phi_c_theta*s_sigma_phi - s_phi*c_sigma_phi
    Ri_prime[0, 2] =  c_phi*s_theta
    Ri_prime[1, 0] =  s_phi_c_theta*c_sigma_phi + c_phi*s_sigma_phi
    Ri_prime[1, 1] = -s_phi_c_theta*s_sigma_phi + c_phi*c_sigma_phi
    Ri_prime[1, 2] =  s_phi*s_theta
    Ri_prime[2, 0] = -s_theta*c_sigma_phi
    Ri_prime[2, 1] =  s_theta*s_sigma_phi
    Ri_prime[2, 2] =  c_theta

    # The rotation.
    R_i = dot(R_eigen, dot(Ri_prime, RT_eigen))

    # Calculate the new vector.
    vect = dot(R_i, r_pivot_atom) + r_ln_pivot

    # The vector length.
    length = norm(vect)

    # The projection.
    proj = dot(vect, dot(A, vect))

    # The PCS (with sine surface normalisation).
    pcs = proj / length**5 * s_theta

    # Return the PCS value (without the PCS constant).
    return pcs


def pcs_pivot_motion_rotor(sigma_i, r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime):
    """Calculate the PCS value after a pivoted motion for the rotor model.

    @param sigma_i:             The rotor angle for state i.
    @type sigma_i:              float
    @param r_pivot_atom:        The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-1, 3D array
    @param r_ln_pivot:          The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-1, 3D array
    @param A:                   The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @param R_eigen:             The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @param RT_eigen:            The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @param Ri_prime:            The empty rotation matrix for the in-frame rotor motion for state i.
    @type Ri_prime:             numpy rank-2, 3D array
    @return:                    The PCS value for the changed position.
    @rtype:                     float
    """

    # The rotation matrix.
    c_sigma = cos(sigma_i)
    s_sigma = sin(sigma_i)
    Ri_prime[0, 0] =  c_sigma
    Ri_prime[0, 1] = -s_sigma
    Ri_prime[1, 0] =  s_sigma
    Ri_prime[1, 1] =  c_sigma

    # The rotation.
    R_i = dot(R_eigen, dot(Ri_prime, RT_eigen))

    # Calculate the new vector.
    vect = dot(R_i, r_pivot_atom) + r_ln_pivot

    # The vector length.
    length = norm(vect)

    # The projection.
    proj = dot(vect, dot(A, vect))

    # The PCS.
    pcs = proj / length**5

    # Return the PCS value (without the PCS constant).
    return pcs


def pcs_pivot_motion_torsionless(theta_i, phi_i, r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime):
    """Calculate the PCS value after a pivoted motion for the isotropic cone model.

    @param theta_i:             The half cone opening angle (polar angle).
    @type theta_i:              float
    @param phi_i:               The cone azimuthal angle.
    @type phi_i:                float
    @param r_pivot_atom:        The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-1, 3D array
    @param r_ln_pivot:          The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-1, 3D array
    @param A:                   The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @param R_eigen:             The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @param RT_eigen:            The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @param Ri_prime:            The empty rotation matrix for the in-frame isotropic cone motion for state i.
    @type Ri_prime:             numpy rank-2, 3D array
    @return:                    The PCS value for the changed position.
    @rtype:                     float
    """

    # The rotation matrix.
    c_theta = cos(theta_i)
    s_theta = sin(theta_i)
    c_phi = cos(phi_i)
    s_phi = sin(phi_i)
    c_phi_c_theta = c_phi * c_theta
    s_phi_c_theta = s_phi * c_theta
    Ri_prime[0, 0] =  c_phi_c_theta*c_phi + s_phi**2
    Ri_prime[0, 1] =  c_phi_c_theta*s_phi - c_phi*s_phi
    Ri_prime[0, 2] =  c_phi*s_theta
    Ri_prime[1, 0] =  s_phi_c_theta*c_phi - c_phi*s_phi
    Ri_prime[1, 1] =  s_phi_c_theta*s_phi + c_phi**2
    Ri_prime[1, 2] =  s_phi*s_theta
    Ri_prime[2, 0] = -s_theta*c_phi
    Ri_prime[2, 1] = -s_theta*s_phi
    Ri_prime[2, 2] =  c_theta

    # The rotation.
    R_i = dot(R_eigen, dot(Ri_prime, RT_eigen))

    # Calculate the new vector.
    vect = dot(R_i, r_pivot_atom) + r_ln_pivot

    # The vector length.
    length = norm(vect)

    # The projection.
    proj = dot(vect, dot(A, vect))

    # The PCS (with sine surface normalisation).
    pcs = proj / length**5 * s_theta

    # Return the PCS value (without the PCS constant).
    return pcs


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


def populate_2nd_eigenframe_iso_cone(matrix, tmax, smax):
    """Populate the 2nd degree Frame Order matrix in the eigenframe for the isotropic cone.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:  The Frame Order matrix, 2nd degree.
    @type matrix:   numpy 9D, rank-2 array
    @param tmax:    The cone opening angle.
    @type tmax:     float
    @param smax:    The maximum torsion angle.
    @type smax:     float
    """

    # Zeros.
    for i in range(9):
        for j in range(9):
            matrix[i, j] = 0.0

    # Repetitive trig calculations.
    sinc_smax = sinc(smax/pi)
    sinc_2smax = sinc(2.0*smax/pi)
    cos_tmax = cos(tmax)
    cos_tmax2 = cos_tmax**2

    # Larger factors.
    fact_sinc_2smax = sinc_2smax*(cos_tmax2 + 4.0*cos_tmax + 7.0) / 24.0
    fact_cos_tmax2 = (cos_tmax2 + cos_tmax + 4.0) / 12.0
    fact_cos_tmax = (cos_tmax + 1.0) / 4.0

    # Diagonal.
    matrix[0, 0] = fact_sinc_2smax  +  fact_cos_tmax2
    matrix[1, 1] = fact_sinc_2smax  +  fact_cos_tmax
    matrix[2, 2] = sinc_smax * (2.0*cos_tmax2 + 5.0*cos_tmax + 5.0) / 12.0
    matrix[3, 3] = matrix[1, 1]
    matrix[4, 4] = matrix[0, 0]
    matrix[5, 5] = matrix[2, 2]
    matrix[6, 6] = matrix[2, 2]
    matrix[7, 7] = matrix[2, 2]
    matrix[8, 8] = (cos_tmax2 + cos_tmax + 1.0) / 3.0

    # Off diagonal set 1.
    matrix[0, 4] = matrix[4, 0] = -fact_sinc_2smax  +  fact_cos_tmax2
    matrix[0, 8] = matrix[8, 0] = -(cos_tmax2 + cos_tmax - 2.0) / 6.0
    matrix[4, 8] = matrix[8, 4] = matrix[0, 8]

    # Off diagonal set 2.
    matrix[1, 3] = matrix[3, 1] = fact_sinc_2smax  -  fact_cos_tmax
    matrix[2, 6] = matrix[6, 2] = sinc_smax * (cos_tmax2 + cos_tmax - 2.0) / 6.0
    matrix[5, 7] = matrix[7, 5] = matrix[2, 6]


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


def reduce_alignment_tensor(D, A, red_tensor):
    """Calculate the reduction in the alignment tensor caused by the Frame Order matrix.

    This is both the forward rotation notation and Kronecker product arrangement.

    @param D:           The Frame Order matrix, 2nd degree to be populated.
    @type D:            numpy 9D, rank-2 array
    @param A:           The full alignment tensor in {Axx, Ayy, Axy, Axz, Ayz} notation.
    @type A:            numpy 5D, rank-1 array
    @param red_tensor:  The structure in {Axx, Ayy, Axy, Axz, Ayz} notation to place the reduced
                        alignment tensor.
    @type red_tensor:   numpy 5D, rank-1 array
    """

    # The reduced tensor element A0.
    red_tensor[0] =                 (D[0, 0] - D[0, 8])*A[0]
    red_tensor[0] = red_tensor[0] + (D[0, 4] - D[0, 8])*A[1]
    red_tensor[0] = red_tensor[0] + (D[0, 1] + D[0, 3])*A[2]
    red_tensor[0] = red_tensor[0] + (D[0, 2] + D[0, 6])*A[3]
    red_tensor[0] = red_tensor[0] + (D[0, 5] + D[0, 7])*A[4]
                                                     
    # The reduced tensor element A1.                 
    red_tensor[1] =                 (D[4, 0] - D[4, 8])*A[0]
    red_tensor[1] = red_tensor[1] + (D[4, 4] - D[4, 8])*A[1]
    red_tensor[1] = red_tensor[1] + (D[4, 1] + D[4, 3])*A[2]
    red_tensor[1] = red_tensor[1] + (D[4, 2] + D[4, 6])*A[3]
    red_tensor[1] = red_tensor[1] + (D[4, 5] + D[4, 7])*A[4]
                                                     
    # The reduced tensor element A2.                 
    red_tensor[2] =                 (D[1, 0] - D[1, 8])*A[0]
    red_tensor[2] = red_tensor[2] + (D[1, 4] - D[1, 8])*A[1]
    red_tensor[2] = red_tensor[2] + (D[1, 1] + D[1, 3])*A[2]
    red_tensor[2] = red_tensor[2] + (D[1, 2] + D[1, 6])*A[3]
    red_tensor[2] = red_tensor[2] + (D[1, 5] + D[1, 7])*A[4]
                                                     
    # The reduced tensor element A3.                 
    red_tensor[3] =                 (D[2, 0] - D[2, 8])*A[0]
    red_tensor[3] = red_tensor[3] + (D[2, 4] - D[2, 8])*A[1]
    red_tensor[3] = red_tensor[3] + (D[2, 1] + D[2, 3])*A[2]
    red_tensor[3] = red_tensor[3] + (D[2, 2] + D[2, 6])*A[3]
    red_tensor[3] = red_tensor[3] + (D[2, 5] + D[2, 7])*A[4]
                                                     
    # The reduced tensor element A4.                 
    red_tensor[4] =                 (D[5, 0] - D[5, 8])*A[0]
    red_tensor[4] = red_tensor[4] + (D[5, 4] - D[5, 8])*A[1]
    red_tensor[4] = red_tensor[4] + (D[5, 1] + D[5, 3])*A[2]
    red_tensor[4] = red_tensor[4] + (D[5, 2] + D[5, 6])*A[3]
    red_tensor[4] = red_tensor[4] + (D[5, 5] + D[5, 7])*A[4]


def reduce_alignment_tensor_symmetric(D, A, red_tensor):
    """Calculate the reduction in the alignment tensor caused by the Frame Order matrix.

    This is both the forward rotation notation and Kronecker product arrangement.  This simplification is due to the symmetry in motion of the pseudo-elliptic and isotropic cones.  All element of the frame order matrix where an index appears only once are zero.

    @param D:           The Frame Order matrix, 2nd degree to be populated.
    @type D:            numpy 9D, rank-2 array
    @param A:           The full alignment tensor in {Axx, Ayy, Axy, Axz, Ayz} notation.
    @type A:            numpy 5D, rank-1 array
    @param red_tensor:  The structure in {Axx, Ayy, Axy, Axz, Ayz} notation to place the reduced
                        alignment tensor.
    @type red_tensor:   numpy 5D, rank-1 array
    """

    # The reduced tensor elements.
    red_tensor[0] = (D[0, 0] - D[0, 8])*A[0]  +  (D[0, 4] - D[0, 8])*A[1]
    red_tensor[1] = (D[4, 0] - D[4, 8])*A[0]  +  (D[4, 4] - D[4, 8])*A[1]
    red_tensor[2] = (D[1, 1] + D[1, 3])*A[2]
    red_tensor[3] = (D[2, 2] + D[2, 6])*A[3]
    red_tensor[4] = (D[5, 5] + D[5, 7])*A[4]


def rotate_daeg(matrix, Rx2_eigen):
    """Rotate the given frame order matrix.

    It is assumed that the frame order matrix is in the Kronecker product form.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    """

    # Rotate.
    matrix_rot = dot(Rx2_eigen, dot(matrix, transpose(Rx2_eigen)))

    # Return the matrix.
    return matrix_rot


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
