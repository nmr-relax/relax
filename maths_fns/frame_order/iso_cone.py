###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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

# Dependency check module.
import dep_check

# Python module imports.
from math import cos, pi, sqrt
from numpy import sinc
if dep_check.scipy_module:
    from scipy.integrate import tplquad

# relax module imports.
from maths_fns.frame_order.matrix_ops import pcs_pivot_motion_full, pcs_pivot_motion_full_qrint, rotate_daeg
from multi import Memo, Result_command, Slave_command


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


def pcs_numeric_int_iso_cone_qrint(points=None, theta_max=None, sigma_max=None, c=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None, error_flag=False):
    """Determine the averaged PCS value via numerical integration.

    @keyword points:            The Sobol points in the torsion-tilt angle space.
    @type points:               numpy rank-2, 3D array
    @keyword theta_max:         The half cone angle.
    @type theta_max:            float
    @keyword sigma_max:         The maximum torsion angle.
    @type sigma_max:            float
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
    @keyword Ri_prime:          The empty rotation matrix for the in-frame isotropic cone motion, used to calculate the PCS for each state i in the numerical integration.
    @type Ri_prime:             numpy rank-2, 3D array
    @keyword pcs_theta:         The storage structure for the back-calculated PCS values.
    @type pcs_theta:            numpy rank-2 array
    @keyword pcs_theta_err:     The storage structure for the back-calculated PCS errors.
    @type pcs_theta_err:        numpy rank-2 array
    @keyword missing_pcs:       A structure used to indicate which PCS values are missing.
    @type missing_pcs:          numpy rank-2 array
    @keyword error_flag:        A flag which if True will cause the PCS errors to be estimated and stored in pcs_theta_err.
    @type error_flag:           bool
    """

    # Clear the data structures.
    for i in range(len(pcs_theta)):
        for j in range(len(pcs_theta[i])):
            pcs_theta[i, j] = 0.0
            pcs_theta_err[i, j] = 0.0

    # Loop over the samples.
    num = 0
    for i in range(len(points)):
        # Unpack the point.
        theta, phi, sigma = points[i]

        # Outside of the distribution, so skip the point.
        if theta > theta_max:
            continue
        if sigma > sigma_max or sigma < -sigma_max:
            continue

        # Calculate the PCSs for this state.
        pcs_pivot_motion_full_qrint(theta_i=theta, phi_i=phi, sigma_i=sigma, full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, A=A, R_eigen=R_eigen, RT_eigen=RT_eigen, Ri_prime=Ri_prime, pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

        # Increment the number of points.
        num += 1

    # Calculate the PCS and error.
    for i in range(len(pcs_theta)):
        for j in range(len(pcs_theta[i])):
            # The average PCS.
            pcs_theta[i, j] = c[i] * pcs_theta[i, j] / float(num)

            # The error.
            if error_flag:
                pcs_theta_err[i, j] = abs(pcs_theta_err[i, j] / float(num)  -  pcs_theta[i, j]**2) / float(num)
                pcs_theta_err[i, j] = c[i] * sqrt(pcs_theta_err[i, j])
                print("%8.3f +/- %-8.3f" % (pcs_theta[i, j]*1e6, pcs_theta_err[i, j]*1e6))


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
