###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""Module containing the target functions of the Frame Order theories."""

# Python module imports.
from copy import deepcopy
from math import acos, pi, sqrt
from numpy import array, dot, float16, float64, ones, transpose, zeros
from numpy.linalg import norm

# relax module imports.
from float import isNaN
from generic_fns.frame_order import print_frame_order_2nd_degree
from extern.sobol.sobol_lib import i4_sobol
from maths_fns.alignment_tensor import to_5D, to_tensor
from maths_fns.chi2 import chi2
from maths_fns.coord_transform import spherical_to_cartesian
from maths_fns.frame_order_matrix_ops import compile_2nd_matrix_free_rotor, compile_2nd_matrix_iso_cone, compile_2nd_matrix_iso_cone_free_rotor, compile_2nd_matrix_iso_cone_torsionless, compile_2nd_matrix_pseudo_ellipse, compile_2nd_matrix_pseudo_ellipse_free_rotor, compile_2nd_matrix_pseudo_ellipse_torsionless, compile_2nd_matrix_rotor, reduce_alignment_tensor, pcs_numeric_int_iso_cone, pcs_numeric_int_iso_cone_qrint, pcs_numeric_int_iso_cone_torsionless, pcs_numeric_int_iso_cone_torsionless_qrint, pcs_numeric_int_pseudo_ellipse, pcs_numeric_int_pseudo_ellipse_qrint, pcs_numeric_int_pseudo_ellipse_torsionless, pcs_numeric_int_pseudo_ellipse_torsionless_qrint, pcs_numeric_int_rotor, pcs_numeric_int_rotor_qrint
from maths_fns.kronecker_product import kron_prod
from maths_fns import order_parameters
from maths_fns.rotation_matrix import euler_to_R_zyz
from maths_fns.rotation_matrix import two_vect_to_R
from pcs import pcs_tensor
from physical_constants import pcs_constant
from rdc import rdc_tensor
from relax_errors import RelaxError


class Frame_order:
    """Class containing the target function of the optimisation of Frame Order matrix components."""

    def __init__(self, model=None, init_params=None, full_tensors=None, full_in_ref_frame=None, rdcs=None, rdc_errors=None, rdc_weights=None, rdc_vect=None, rdc_const=None, pcs=None, pcs_errors=None, pcs_weights=None, pcs_atoms=None, temp=None, frq=None, paramag_centre=None, scaling_matrix=None, num_int_pts=500, pivot=None, pivot_opt=False, quad_int=True):
        """Set up the target functions for the Frame Order theories.
        
        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword init_params:       The initial parameter values.
        @type init_params:          numpy float64 array
        @keyword full_tensors:      An array of the {Axx, Ayy, Axy, Axz, Ayz} values for all full alignment tensors.  The format is [Axx1, Ayy1, Axy1, Axz1, Ayz1, Axx2, Ayy2, Axy2, Axz2, Ayz2, ..., Axxn, Ayyn, Axyn, Axzn, Ayzn].
        @type full_tensors:         numpy nx5D, rank-1 float64 array
        @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
        @type full_in_ref_frame:    numpy rank-1 array
        @keyword rdcs:              The RDC lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type rdcs:                 numpy rank-2 array
        @keyword rdc_errors:        The RDC error lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_errors:           numpy rank-2 array
        @keyword rdc_weights:       The RDC weight lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_weights:          numpy rank-2 array
        @keyword rdc_vect:          The unit XH vector lists corresponding to the RDC values.  The first index must correspond to the spin systems and the second index to the x, y, z elements.
        @type rdc_vect:             numpy rank-2 array
        @keyword rdc_const:         The dipolar constants for each RDC.  The indices correspond to the spin systems j.
        @type rdc_const:            numpy rank-1 array
        @keyword pcs:               The PCS lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type pcs:                  numpy rank-2 array
        @keyword pcs_errors:        The PCS error lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_errors:           numpy rank-2 array
        @keyword pcs_weights:       The PCS weight lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_weights:          numpy rank-2 array
        @keyword pcs_atoms:         The atomic positions of the spins with PCS values.  The first index is the spin systems j and the second is the coordinate.
        @type pcs_atoms:            numpy rank-2 array
        @keyword temp:              The temperature of each PCS data set.
        @type temp:                 numpy rank-1 array
        @keyword frq:               The frequency of each PCS data set.
        @type frq:                  numpy rank-1 array
        @keyword paramag_centre:    The paramagnetic centre position (or positions).
        @type paramag_centre:       numpy rank-1, 3D array or rank-2, Nx3 array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 array
        @keyword num_int_pts:       The number of points to use for the numerical integration technique.
        @type num_int_pts:          int
        @keyword pivot:             The pivot point for the ball-and-socket joint motion.  This is needed if PCS or PRE values are used.
        @type pivot:                numpy rank-1, 3D array or None
        @keyword pivot_opt:         A flag which if True will allow the pivot point of the motion to be optimised.
        @type pivot_opt:            bool
        @keyword quad_int:          A flag which if True will perform high precision numerical integration via the scipy.integrate quad(), dblquad() and tplquad() integration methods rather than the rough quasi-random numerical integration.
        @type quad_int:             bool
        """

        # Model test.
        if not model:
            raise RelaxError("The type of Frame Order model must be specified.")

        # Store the initial parameter (as a copy).
        self.params = deepcopy(init_params)

        # Store the agrs.
        self.model = model
        self.full_tensors = full_tensors
        self.full_in_ref_frame = full_in_ref_frame
        self.rdc = rdcs
        self.rdc_weights = rdc_weights
        self.rdc_vect = rdc_vect
        self.rdc_const = rdc_const
        self.pcs = pcs
        self.pcs_weights = pcs_weights
        self.pcs_atoms = pcs_atoms
        self.temp = temp
        self.frq = frq
        self.paramag_centre = paramag_centre
        self.total_num_params = len(init_params)
        self.num_int_pts = num_int_pts
        self._param_pivot = pivot
        self.pivot_opt = pivot_opt

        # Tensor setup.
        self._init_tensors()

        # Scaling initialisation.
        self.scaling_matrix = scaling_matrix
        if self.scaling_matrix != None:
            self.scaling_flag = True
        else:
            self.scaling_flag = False

        # Set the RDC and PCS flags (indicating the presence of data).
        self.rdc_flag = True
        self.pcs_flag = True
        if rdcs == None or len(rdcs) == 0:
            self.rdc_flag = False
        if pcs == None or len(pcs) == 0:
            self.pcs_flag = False

        # Some checks.
        if self.rdc_flag and (rdc_vect == None or not len(rdc_vect)):
            raise RelaxError("The rdc_vect argument " + repr(rdc_vect) + " must be supplied.")
        if self.pcs_flag and (pcs_atoms == None or not len(pcs_atoms)):
            raise RelaxError("The pcs_atoms argument " + repr(pcs_atoms) + " must be supplied.")

        # The total number of spins.
        if self.rdc_flag:
            self.num_rdc = len(rdcs[0])
        if self.pcs_flag:
            self.num_pcs = len(pcs[0])

        # The total number of alignments.
        self.num_align = 0
        if self.rdc_flag:
            self.num_align = len(rdcs)
        elif self.pcs_flag:
            self.num_align = len(pcs)

        # Set up the alignment data.
        for i in range(self.num_align):
            to_tensor(self.A_3D[i], self.full_tensors[5*i:5*i+5])

        # PCS errors.
        if self.pcs_flag:
            err = False
            for i in xrange(len(pcs_errors)):
                for j in xrange(len(pcs_errors[i])):
                    if not isNaN(pcs_errors[i, j]):
                        err = True
            if err:
                self.pcs_error = pcs_errors
            else:
                # Missing errors (the values need to be small, close to ppm units, so the chi-squared value is comparable to the RDC).
                self.pcs_error = 0.03 * 1e-6 * ones((self.num_align, self.num_pcs), float64)

        # RDC errors.
        if self.rdc_flag:
            err = False
            for i in xrange(len(rdc_errors)):
                for j in xrange(len(rdc_errors[i])):
                    if not isNaN(rdc_errors[i, j]):
                        err = True
            if err:
                self.rdc_error = rdc_errors
            else:
                # Missing errors.
                self.rdc_error = ones((self.num_align, self.num_rdc), float64)

        # Missing data matrices (RDC).
        if self.rdc_flag:
            self.missing_rdc = zeros((self.num_align, self.num_rdc), float64)

        # Missing data matrices (PCS).
        if self.pcs_flag:
            self.missing_pcs = zeros((self.num_align, self.num_pcs), float64)

        # Clean up problematic data and put the weights into the errors..
        if self.rdc_flag or self.pcs_flag:
            for i in xrange(self.num_align):
                # Loop over the RDCs.
                if self.rdc_flag:
                    for j in xrange(self.num_rdc):
                        if isNaN(self.rdc[i, j]):
                            # Set the flag.
                            self.missing_rdc[i, j] = 1

                            # Change the NaN to zero.
                            self.rdc[i, j] = 0.0

                            # Change the error to one (to avoid zero division).
                            self.rdc_error[i, j] = 1.0

                            # Change the weight to one.
                            rdc_weights[i, j] = 1.0

                    # The RDC weights.
                    if self.rdc_flag:
                        self.rdc_error[i, j] = self.rdc_error[i, j] / sqrt(rdc_weights[i, j])

                # Loop over the PCSs.
                if self.pcs_flag:
                    for j in xrange(self.num_pcs):
                        if isNaN(self.pcs[i, j]):
                            # Set the flag.
                            self.missing_pcs[i, j] = 1

                            # Change the NaN to zero.
                            self.pcs[i, j] = 0.0

                            # Change the error to one (to avoid zero division).
                            self.pcs_error[i, j] = 1.0

                            # Change the weight to one.
                            pcs_weights[i, j] = 1.0

                    # The PCS weights.
                    if self.pcs_flag:
                        self.pcs_error[i, j] = self.pcs_error[i, j] / sqrt(pcs_weights[i, j])

        # The paramagnetic centre vectors and distances.
        if self.pcs_flag:
            # Initialise the data structures.
            self.paramag_unit_vect = zeros(pcs_atoms.shape, float64)
            self.paramag_dist = zeros(self.num_pcs, float64)
            self.pcs_const = zeros(self.num_align, float64)
            self.r_pivot_atom = zeros((3, self.num_pcs), float64)
            self.r_pivot_atom_rev = zeros((3, self.num_pcs), float64)
            self.r_ln_pivot = zeros((3, self.num_pcs), float64)
            if self.paramag_centre == None:
                self.paramag_centre = zeros(3, float64)

            # Set up the paramagnetic constant (without the interatomic distance and in Angstrom units).
            for i in range(self.num_align):
                self.pcs_const[i] = pcs_constant(self.temp[i], self.frq[i], 1.0) * 1e30

        # PCS function, gradient, and Hessian matrices.
        if self.pcs_flag:
            self.pcs_theta = zeros((self.num_align, self.num_pcs), float64)
            self.pcs_theta_err = zeros((self.num_align, self.num_pcs), float64)
            self.dpcs_theta = zeros((self.total_num_params, self.num_align, self.num_pcs), float64)
            self.d2pcs_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_pcs), float64)

        # RDC function, gradient, and Hessian matrices.
        if self.rdc_flag:
            self.rdc_theta = zeros((self.num_align, self.num_rdc), float64)
            self.drdc_theta = zeros((self.total_num_params, self.num_align, self.num_rdc), float64)
            self.d2rdc_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_rdc), float64)

        # The Sobol' sequence data and target function aliases (quasi-random integration).
        if not quad_int:
            if model == 'pseudo-ellipse':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'phi', 'sigma'])
                self.func = self.func_pseudo_ellipse_qrint
            elif model == 'pseudo-ellipse, torsionless':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'phi'])
                self.func = self.func_pseudo_ellipse_torsionless_qrint
            elif model == 'pseudo-ellipse, free rotor':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'phi', 'sigma'])
                self.func = self.func_pseudo_ellipse_free_rotor_qrint
            elif model == 'iso cone':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'phi', 'sigma'])
                self.func = self.func_iso_cone_qrint
            elif model == 'iso cone, torsionless':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'phi'])
                self.func = self.func_iso_cone_torsionless_qrint
            elif model == 'iso cone, free rotor':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'phi', 'sigma'])
                self.func = self.func_iso_cone_free_rotor_qrint
            elif model == 'line':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'sigma'])
                self.func = self.func_line_qrint
            elif model == 'line, torsionless':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta'])
                self.func = self.func_line_torsionless_qrint
            elif model == 'line, free rotor':
                self.create_sobol_data(n=self.num_int_pts, dims=['theta', 'sigma'])
                self.func = self.func_line_free_rotor_qrint
            elif model == 'rotor':
                self.create_sobol_data(n=self.num_int_pts, dims=['sigma'])
                self.func = self.func_rotor_qrint
            elif model == 'rigid':
                self.func = self.func_rigid
            elif model == 'free rotor':
                self.create_sobol_data(n=self.num_int_pts, dims=['sigma'])
                self.func = self.func_free_rotor_qrint

        # The target function aliases (Scipy numerical integration).
        else:
            if model == 'pseudo-ellipse':
                self.func = self.func_pseudo_ellipse
            elif model == 'pseudo-ellipse, torsionless':
                self.func = self.func_pseudo_ellipse_torsionless
            elif model == 'pseudo-ellipse, free rotor':
                self.func = self.func_pseudo_ellipse_free_rotor
            elif model == 'iso cone':
                self.func = self.func_iso_cone
            elif model == 'iso cone, torsionless':
                self.func = self.func_iso_cone_torsionless
            elif model == 'iso cone, free rotor':
                self.func = self.func_iso_cone_free_rotor
            elif model == 'line':
                self.func = self.func_line
            elif model == 'line, torsionless':
                self.func = self.func_line_torsionless
            elif model == 'line, free rotor':
                self.func = self.func_line_free_rotor
            elif model == 'rotor':
                self.func = self.func_rotor
            elif model == 'rigid':
                self.func = self.func_rigid
            elif model == 'free rotor':
                self.func = self.func_free_rotor


    def _init_tensors(self):
        """Set up isotropic cone optimisation against the alignment tensor data."""

        # Some checks.
        if self.full_tensors == None or not len(self.full_tensors):
            raise RelaxError("The full_tensors argument " + repr(self.full_tensors) + " must be supplied.")
        if self.full_in_ref_frame == None or not len(self.full_in_ref_frame):
            raise RelaxError("The full_in_ref_frame argument " + repr(self.full_in_ref_frame) + " must be supplied.")

        # Tensor set up.
        self.num_tensors = len(self.full_tensors) / 5
        self.A_3D = zeros((self.num_tensors, 3, 3), float64)
        self.A_3D_bc = zeros((self.num_tensors, 3, 3), float64)
        self.A_5D_bc = zeros(self.num_tensors*5, float64)

        # The rotation to the Frame Order eigenframe.
        self.R_eigen = zeros((3, 3), float64)
        self.R_ave = zeros((3, 3), float64)
        self.Ri_prime = zeros((3, 3), float64)
        self.tensor_3D = zeros((3, 3), float64)

        # The cone axis storage and molecular frame z-axis.
        self.cone_axis = zeros(3, float64)
        self.z_axis = array([0, 0, 1], float64)

        # Initialise the Frame Order matrices.
        self.frame_order_2nd = zeros((9, 9), float64)


    def func_free_rotor(self, params):
        """Target function for free rotor model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params[3:]
        else:
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_free_rotor(self.frame_order_2nd, Rx2_eigen)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_rotor(sigma_max=pi, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_free_rotor_qrint(self, params):
        """Target function for free rotor model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple Monte Carlo integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params[3:]
        else:
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_free_rotor(self.frame_order_2nd, Rx2_eigen)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_rotor_qrint(points=self.sobol_angles, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])


        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone(self, params):
        """Target function for isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone(self.frame_order_2nd, Rx2_eigen, cone_theta, sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_iso_cone(theta_max=cone_theta, sigma_max=sigma_max, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_qrint(self, params):
        """Target function for isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple Monte Carlo integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, theta, phi, cone_theta, sigma_max} where the first 3 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, cone_theta is the cone opening half angle, and sigma_max is the torsion angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone(self.frame_order_2nd, Rx2_eigen, cone_theta, sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_iso_cone_qrint(points=self.sobol_angles, theta_max=cone_theta, sigma_max=sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_free_rotor(self, params):
        """Target function for free rotor isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params[3:]
        else:
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Calculate the cone angle.
        theta_max = order_parameters.iso_cone_S_to_theta(cone_s1)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_free_rotor(self.frame_order_2nd, Rx2_eigen, cone_s1)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_iso_cone(theta_max=theta_max, sigma_max=pi, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_free_rotor_qrint(self, params):
        """Target function for free rotor isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple Monte Carlo integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params[3:]
        else:
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Calculate the cone angle.
        theta_max = order_parameters.iso_cone_S_to_theta(cone_s1)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_free_rotor(self.frame_order_2nd, Rx2_eigen, cone_s1)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_iso_cone_qrint(points=self.sobol_angles, theta_max=theta_max, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_torsionless(self, params):
        """Target function for torsionless isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, cone_theta} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and cone_theta is cone opening angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_iso_cone_torsionless(theta_max=cone_theta, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_torsionless_qrint(self, params):
        """Target function for torsionless isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple Monte Carlo integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, cone_theta} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and cone_theta is cone opening angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_iso_cone_torsionless_qrint(points=self.sobol_angles, theta_max=cone_theta, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse(self, params):
        """Target function for pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 3 are the pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y, cone_sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_pseudo_ellipse(theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=cone_sigma_max, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_qrint(self, params):
        """Target function for pseudo-elliptic cone model optimisation.

        This function optimises the model parameters using the RDC and PCS base data.  Quasi-random, Sobol' sequence based, numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 3 are the pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y, cone_sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_pseudo_ellipse_qrint(points=self.sobol_angles, theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=cone_sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_free_rotor(self, params):
        """Target function for free_rotor pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the free_rotor pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_pseudo_ellipse(theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=pi, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_free_rotor_qrint(self, params):
        """Target function for free_rotor pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple Monte Carlo integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the free_rotor pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_pseudo_ellipse_qrint(points=self.sobol_angles, theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_torsionless(self, params):
        """Target function for torsionless pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the torsionless pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_pseudo_ellipse_torsionless(theta_x=cone_theta_x, theta_y=cone_theta_y, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_torsionless_qrint(self, params):
        """Target function for torsionless pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple Monte Carlo integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the torsionless pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_pseudo_ellipse_torsionless_qrint(points=self.sobol_angles, theta_x=cone_theta_x, theta_y=cone_theta_y, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_rigid(self, params):
        """Target function for rigid model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        ave_pos_alpha, ave_pos_beta, ave_pos_gamma = params

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma)

        # Pre-transpose matrices for faster calculations.
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The PCS calculation.
                        vect = self.r_ln_pivot[:, 0] + r_pivot_atom
                        length = norm(vect)
                        self.pcs_theta[i, j] = pcs_tensor(self.pcs_const[i] / length**5, vect, self.A_3D[i])

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_rotor(self, params):
        """Target function for rotor model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi, sigma_max}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_rotor(self.frame_order_2nd, Rx2_eigen, sigma_max)

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

            # PCS.
            if self.pcs_flag:
                # Loop over the PCSs.
                for j in xrange(self.num_pcs):
                    # The back calculated PCS.
                    if not self.missing_pcs[i, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[i]:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom[:, j]

                        # The numerical integration.
                        self.pcs_theta[i, j] = pcs_numeric_int_rotor(sigma_max=sigma_max, c=self.pcs_const[i], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[i], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def func_rotor_qrint(self, params):
        """Target function for rotor model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Quasi-random, Sobol' sequence based, numerical integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi, sigma_max}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            self._param_pivot = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params[3:]
        else:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_rotor(self.frame_order_2nd, Rx2_eigen, sigma_max)

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(self._param_pivot, self.R_ave, RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # RDCs.
            if self.rdc_flag:
                # Loop over the RDCs.
                for j in xrange(self.num_rdc):
                    # The back calculated RDC.
                    if not self.missing_rdc[i, j]:
                        self.rdc_theta[i, j] = rdc_tensor(self.rdc_const[j], self.rdc_vect[j], self.A_3D_bc[i])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[i], self.rdc_theta[i], self.rdc_error[i])

        # PCS via Monte Carlo integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_int_rotor_qrint(points=self.sobol_angles, sigma_max=sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for i in xrange(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[i], self.pcs_theta[i], self.pcs_error[i])

        # Return the chi-squared value.
        return chi2_sum


    def calc_vectors(self, pivot, R_ave, RT_ave):
        """Calculate the pivot to atom and lanthanide to pivot vectors for the target functions.

        @param pivot:   The pivot point.
        @type pivot:    numpy rank-1, 3D array
        @param R_ave:   The rotation matrix for rotating from the reference frame to the average position.
        @type R_ave:    numpy rank-2, 3D array
        @param RT_ave:  The transpose of R_ave.
        @type RT_ave:   numpy rank-2, 3D array
        """

        # The pivot to atom vectors.
        for j in xrange(self.num_pcs):
            # The lanthanide to pivot vector.
            self.r_ln_pivot[:, j] = pivot - self.paramag_centre

            # The rotated vectors.
            self.r_pivot_atom[:, j] = dot(R_ave, self.pcs_atoms[j] - pivot)
            self.r_pivot_atom_rev[:, j] = dot(RT_ave, self.pcs_atoms[j] - pivot)


    def create_sobol_data(self, n=10000, dims=None):
        """Create the Sobol' quasi-random data for numerical integration.

        This uses the external sobol_lib module to create the data.  The algorithm is that modified by Antonov and Saleev.


        @keyword n:         The number of points to generate.
        @type n:            int
        @keyword dims:      The list of parameters.
        @type dims:         list of str
        """

        # The number of dimensions.
        m = len(dims)

        # Initialise.
        self.sobol_angles = zeros((n, m), float16)

        # Loop over the points.
        for i in range(n):
            # The raw point.
            point, seed = i4_sobol(m, i)

            # Loop over the dimensions, converting the points to angles.
            for j in range(m):
                if dims[j] in ['theta']:
                    self.sobol_angles[i, j] = 2.0 * pi * point[j]
                if dims[j] in ['phi']:
                    self.sobol_angles[i, j] = acos(2.0*point[j] - 1.0)
                if dims[j] in ['sigma']:
                    self.sobol_angles[i, j] = 2.0 * pi * (point[j] - 0.5)


    def reduce_and_rot(self, ave_pos_alpha=None, ave_pos_beta=None, ave_pos_gamma=None, daeg=None):
        """Reduce and rotate the alignments tensors using the frame order matrix and Euler angles.

        @keyword ave_pos_alpha: The alpha Euler angle describing the average domain position, the tensor rotation.
        @type ave_pos_alpha:    float
        @keyword ave_pos_beta:  The beta Euler angle describing the average domain position, the tensor rotation.
        @type ave_pos_beta:     float
        @keyword ave_pos_gamma: The gamma Euler angle describing the average domain position, the tensor rotation.
        @type ave_pos_gamma:    float
        @keyword daeg:          The 2nd degree frame order matrix.
        @type daeg:             rank-2, 9D array
        """

        # Alignment tensor rotation.
        euler_to_R_zyz(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, self.R_ave)

        # Back calculate the rotated tensors.
        for i in range(self.num_tensors):
            # Tensor indices.
            index1 = i*5
            index2 = i*5+5

            # Reduction.
            if daeg != None:
                # Reduce the tensor.
                reduce_alignment_tensor(daeg, self.full_tensors[index1:index2], self.A_5D_bc[index1:index2])

                # Convert the reduced tensor to 3D, rank-2 form.
                to_tensor(self.tensor_3D, self.A_5D_bc[index1:index2])

            # No reduction:
            else:
                # Convert the original tensor to 3D, rank-2 form.
                to_tensor(self.tensor_3D, self.full_tensors[index1:index2])

            # Rotate the tensor (normal R.X.RT rotation).
            if self.full_in_ref_frame[i]:
                self.A_3D_bc[i] = dot(self.R_ave, dot(self.tensor_3D, transpose(self.R_ave)))

            # Rotate the tensor (inverse RT.X.R rotation).
            else:
                self.A_3D_bc[i] = dot(transpose(self.R_ave), dot(self.tensor_3D, self.R_ave))

            # Convert the tensor back to 5D, rank-1 form, as the back-calculated reduced tensor.
            to_5D(self.A_5D_bc[index1:index2], self.A_3D_bc[i])
