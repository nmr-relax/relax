###############################################################################
#                                                                             #
# Copyright (C) 2009-2015 Edward d'Auvergne                                   #
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
from math import cos, pi
from numpy import divide, dot, eye, float64, multiply, swapaxes, tensordot
try:
    from scipy.integrate import dblquad
except ImportError:
    pass

# relax module imports.
from lib.frame_order.matrix_ops import pcs_pivot_motion_torsionless_qr_int, pcs_pivot_motion_torsionless_quad_int, rotate_daeg


def compile_1st_matrix_iso_cone_torsionless(matrix, R_eigen, cone_theta):
    """Generate the 1st degree Frame Order matrix for the torsionless isotropic cone.

    @param matrix:      The Frame Order matrix, 1st degree to be populated.
    @type matrix:       numpy 3D, rank-2 array
    @param R_eigen:     The eigenframe rotation matrix.
    @type R_eigen:      numpy 3D, rank-2 array
    @param cone_theta:  The cone opening angle.
    @type cone_theta:   float
    """

    # Zeros.
    matrix[:] = 0.0

    # Pre-calculate trig values.
    cos_theta = cos(cone_theta)

    # Diagonal values.
    matrix[0, 0] = cos_theta + 3.0
    matrix[1, 1] = matrix[0, 0]
    matrix[2, 2] = 2.0*cos_theta + 2.0

    # Rotate and return the frame order matrix.
    return 0.25 * rotate_daeg(matrix, R_eigen)


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
    matrix[:] = 0.0

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


def pcs_numeric_qr_int_iso_cone_torsionless(points=None, max_points=None, theta_max=None, c=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None):
    """Determine the averaged PCS value via numerical integration.

    @keyword points:            The Sobol points in the torsion-tilt angle space.
    @type points:               numpy rank-2, 3D array
    @keyword max_points:        The maximum number of Sobol' points to use.  Once this number is reached, the loop over the Sobol' torsion-tilt angles is terminated.
    @type max_points:           int
    @keyword theta_max:         The half cone angle.
    @type theta_max:            float
    @keyword c:                 The PCS constant (without the interatomic distance and in Angstrom units).
    @type c:                    numpy rank-1 array
    @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
    @type full_in_ref_frame:    numpy rank-1 array
    @keyword r_pivot_atom:      The pivot point to atom vector.
    @type r_pivot_atom:         numpy rank-2, 3D array
    @keyword r_pivot_atom_rev:  The reversed pivot point to atom vector.
    @type r_pivot_atom_rev:     numpy rank-2, 3D array
    @keyword r_ln_pivot:        The lanthanide position to pivot point vector.
    @type r_ln_pivot:           numpy rank-2, 3D array
    @keyword A:                 The full alignment tensor of the non-moving domain.
    @type A:                    numpy rank-2, 3D array
    @keyword R_eigen:           The eigenframe rotation matrix.
    @type R_eigen:              numpy rank-2, 3D array
    @keyword RT_eigen:          The transpose of the eigenframe rotation matrix (for faster calculations).
    @type RT_eigen:             numpy rank-2, 3D array
    @keyword Ri_prime:          The array of pre-calculated rotation matrices for the in-frame torsionless isotropic cone motion, used to calculate the PCS for each state i in the numerical integration.
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
    theta, phi = points

    # Loop over the samples.
    num = 0
    for i in range(len(points[0])):
        # The maximum number of points has been reached (well, surpassed by one so exit the loop before it is used).
        if num == max_points:
            break

        # Outside of the distribution, so skip the point.
        if theta[i] > theta_max:
            continue

        # Calculate the PCSs for this state.
        pcs_pivot_motion_torsionless_qr_int(full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, A=A, Ri=Ri[i], pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Increment the number of points.
        num += 1

    # Default to the rigid state if no points lie in the distribution.
    if num == 0:
        # Fast identity frame shift.
        Ri_prime = eye(3, dtype=float64)
        Ri = dot(R_eigen, tensordot(Ri_prime, RT_eigen, axes=1))
        Ri = swapaxes(Ri, 0, 1)

        # Calculate the PCSs for this state.
        pcs_pivot_motion_torsionless_qr_int(full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, A=A, Ri=Ri, pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Multiply the constant.
        multiply(c, pcs_theta, pcs_theta)

    # Average the PCS.
    else:
        multiply(c, pcs_theta, pcs_theta)
        divide(pcs_theta, float(num), pcs_theta)


def pcs_numeric_quad_int_iso_cone_torsionless(theta_max=None, c=None, r_pivot_atom=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None):
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
    result = dblquad(pcs_pivot_motion_torsionless_quad_int, -pi, pi, lambda phi: 0.0, lambda phi: theta_max, args=(r_pivot_atom, r_ln_pivot, A, R_eigen, RT_eigen, Ri_prime))

    # The surface area normalisation factor.
    SA = 2.0 * pi * (1.0 - cos(theta_max))

    # Return the value.
    return c * result[0] / SA
