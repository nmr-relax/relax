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
"""Module for the double rotor frame order model."""

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import dot, inner, sinc, transpose

# relax module imports.
from lib.frame_order.matrix_ops import rotate_daeg


def compile_2nd_matrix_double_rotor(matrix, Rx2_eigen, smax, smaxb):
    """Generate the rotated 2nd degree Frame Order matrix for the double rotor model.

    The cone axis is assumed to be parallel to the z-axis in the eigenframe.


    @param matrix:      The Frame Order matrix, 2nd degree to be populated.
    @type matrix:       numpy 9D, rank-2 array
    @param Rx2_eigen:   The Kronecker product of the eigenframe rotation matrix with itself.
    @type Rx2_eigen:    numpy 9D, rank-2 array
    @param smax:        The maximum torsion angle for the first rotor.
    @type smax:         float
    @param smaxb:       The maximum torsion angle for the second rotor.
    @type smaxb:        float
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


def pcs_numeric_int_double_rotor(points=None, sigma_max=None, sigma_max_2=None, c=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None, error_flag=False):
    """The averaged PCS value via numerical integration for the double rotor frame order model.

    @keyword points:            The Sobol points in the torsion-tilt angle space.
    @type points:               numpy rank-2, 3D array
    @keyword sigma_max:         The maximum opening angle for the first rotor.
    @type sigma_max:            float
    @keyword sigma_max_2:       The maximum opening angle for the second rotor.
    @type sigma_max_2:          float
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
    @keyword Ri_prime:          The empty rotation matrix for the in-frame rotor motion, used to calculate the PCS for each state i in the numerical integration.
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
        sigma, sigma2 = points[i]

        # Outside of the distribution, so skip the point.
        if sigma > sigma_max or sigma < -sigma_max:
            continue

        # Calculate the PCSs for this state.
        pcs_pivot_motion_double_rotor(sigma_i=sigma, full_in_ref_frame=full_in_ref_frame, r_pivot_atom=r_pivot_atom, r_pivot_atom_rev=r_pivot_atom_rev, r_ln_pivot=r_ln_pivot, A=A, R_eigen=R_eigen, RT_eigen=RT_eigen, Ri_prime=Ri_prime, pcs_theta=pcs_theta, pcs_theta_err=pcs_theta_err, missing_pcs=missing_pcs)

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


def pcs_pivot_motion_double_rotor(sigma_i=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None, error_flag=False):
    """Calculate the PCS value after a pivoted motion for the double rotor model.

    @keyword sigma_i:           The rotor angle for state i.
    @type sigma_i:              float
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
    @keyword Ri_prime:          The empty rotation matrix for the in-frame rotor motion for state i.
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

    # The rotation matrix.
    c_sigma = cos(sigma_i)
    s_sigma = sin(sigma_i)
    Ri_prime[0, 0] =  c_sigma
    Ri_prime[0, 1] = -s_sigma
    Ri_prime[0, 2] = 0.0
    Ri_prime[1, 0] =  s_sigma
    Ri_prime[1, 1] =  c_sigma
    Ri_prime[1, 2] = 0.0
    Ri_prime[2, 0] = 0.0
    Ri_prime[2, 1] = 0.0
    Ri_prime[2, 2] = 1.0

    # The rotation.
    R_i = dot(R_eigen, dot(Ri_prime, RT_eigen))

    # Pre-calculate all the new vectors (forwards and reverse).
    rot_vect_rev = transpose(dot(R_i, r_pivot_atom_rev) + r_ln_pivot)
    rot_vect = transpose(dot(R_i, r_pivot_atom) + r_ln_pivot)

    # Loop over the atoms.
    for j in range(len(r_pivot_atom[0])):
        # The vector length (to the 5th power).
        length_rev = 1.0 / sqrt(inner(rot_vect_rev[j], rot_vect_rev[j]))**5
        length = 1.0 / sqrt(inner(rot_vect[j], rot_vect[j]))**5

        # Loop over the alignments.
        for i in range(len(pcs_theta)):
            # Skip missing data.
            if missing_pcs[i, j]:
                continue

            # The projection.
            if full_in_ref_frame[i]:
                proj = dot(rot_vect[j], dot(A[i], rot_vect[j]))
                length_i = length
            else:
                proj = dot(rot_vect_rev[j], dot(A[i], rot_vect_rev[j]))
                length_i = length_rev

            # The PCS.
            pcs_theta[i, j] += proj * length_i

            # The square.
            if error_flag:
                pcs_theta_err[i, j] += (proj * length_i)**2
