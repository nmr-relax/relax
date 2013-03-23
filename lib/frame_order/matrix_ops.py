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
from math import cos, sin, sqrt
from numpy import dot, inner, transpose
from numpy.linalg import norm

# relax module imports.
from lib.algebra.kronecker_product import transpose_23
from lib.geometry.rotations import tilt_torsion_to_R


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


def pcs_pivot_motion_full_qrint(theta_i=None, phi_i=None, sigma_i=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None, error_flag=False):
    """Calculate the PCS value after a pivoted motion for the isotropic cone model.

    @keyword theta_i:           The half cone opening angle (polar angle).
    @type theta_i:              float
    @keyword phi_i:             The cone azimuthal angle.
    @type phi_i:                float
    @keyword sigma_i:           The torsion angle for state i.
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
    @keyword Ri_prime:          The empty rotation matrix for the in-frame isotropic cone motion for state i.
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
    tilt_torsion_to_R(phi_i, theta_i, sigma_i, Ri_prime)

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


def pcs_pivot_motion_torsionless_qrint(theta_i=None, phi_i=None, full_in_ref_frame=None, r_pivot_atom=None, r_pivot_atom_rev=None, r_ln_pivot=None, A=None, R_eigen=None, RT_eigen=None, Ri_prime=None, pcs_theta=None, pcs_theta_err=None, missing_pcs=None, error_flag=False):
    """Calculate the PCS value after a pivoted motion for the isotropic cone model.

    @keyword theta_i:           The half cone opening angle (polar angle).
    @type theta_i:              float
    @keyword phi_i:             The cone azimuthal angle.
    @type phi_i:                float
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
    @keyword Ri_prime:          The empty rotation matrix for the in-frame isotropic cone motion for state i.
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
    red_tensor[0] =                 (D[0, 0] - D[8, 0])*A[0]
    red_tensor[0] = red_tensor[0] + (D[4, 0] - D[8, 0])*A[1]
    red_tensor[0] = red_tensor[0] + (D[1, 0] + D[3, 0])*A[2]
    red_tensor[0] = red_tensor[0] + (D[2, 0] + D[6, 0])*A[3]
    red_tensor[0] = red_tensor[0] + (D[5, 0] + D[7, 0])*A[4]

    # The reduced tensor element A1.
    red_tensor[1] =                 (D[0, 4] - D[8, 4])*A[0]
    red_tensor[1] = red_tensor[1] + (D[4, 4] - D[8, 4])*A[1]
    red_tensor[1] = red_tensor[1] + (D[1, 4] + D[3, 4])*A[2]
    red_tensor[1] = red_tensor[1] + (D[2, 4] + D[6, 4])*A[3]
    red_tensor[1] = red_tensor[1] + (D[5, 4] + D[7, 4])*A[4]

    # The reduced tensor element A2.
    red_tensor[2] =                 (D[0, 1] - D[8, 1])*A[0]
    red_tensor[2] = red_tensor[2] + (D[4, 1] - D[8, 1])*A[1]
    red_tensor[2] = red_tensor[2] + (D[1, 1] + D[3, 1])*A[2]
    red_tensor[2] = red_tensor[2] + (D[2, 1] + D[6, 1])*A[3]
    red_tensor[2] = red_tensor[2] + (D[5, 1] + D[7, 1])*A[4]

    # The reduced tensor element A3.
    red_tensor[3] =                 (D[0, 2] - D[8, 2])*A[0]
    red_tensor[3] = red_tensor[3] + (D[4, 2] - D[8, 2])*A[1]
    red_tensor[3] = red_tensor[3] + (D[1, 2] + D[3, 2])*A[2]
    red_tensor[3] = red_tensor[3] + (D[2, 2] + D[6, 2])*A[3]
    red_tensor[3] = red_tensor[3] + (D[5, 2] + D[7, 2])*A[4]

    # The reduced tensor element A4.
    red_tensor[4] =                 (D[0, 5] - D[8, 5])*A[0]
    red_tensor[4] = red_tensor[4] + (D[4, 5] - D[8, 5])*A[1]
    red_tensor[4] = red_tensor[4] + (D[1, 5] + D[3, 5])*A[2]
    red_tensor[4] = red_tensor[4] + (D[2, 5] + D[6, 5])*A[3]
    red_tensor[4] = red_tensor[4] + (D[5, 5] + D[7, 5])*A[4]


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
    red_tensor[0] = (D[0, 0] - D[8, 0])*A[0]  +  (D[4, 0] - D[8, 0])*A[1]
    red_tensor[1] = (D[0, 4] - D[8, 4])*A[0]  +  (D[4, 4] - D[8, 4])*A[1]
    red_tensor[2] = (D[1, 1] + D[3, 1])*A[2]
    red_tensor[3] = (D[2, 2] + D[6, 2])*A[3]
    red_tensor[4] = (D[5, 5] + D[7, 5])*A[4]


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


class Data:
    """A data container stored in the memo objects for use by the Result_command class."""
