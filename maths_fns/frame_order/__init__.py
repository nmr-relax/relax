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
"""Module containing the target functions of the Frame Order theories."""

# Python module imports.
from copy import deepcopy
from math import acos, ceil, pi, sqrt
from numpy import array, dot, float32, float64, ones, transpose, uint8, zeros
from numpy.linalg import norm

# relax module imports.
from float import isNaN
from generic_fns.frame_order import print_frame_order_2nd_degree
from extern.sobol.sobol_lib import i4_sobol
from maths_fns.alignment_tensor import to_5D, to_tensor
from maths_fns.chi2 import chi2
from maths_fns.coord_transform import spherical_to_cartesian
from maths_fns.frame_order.matrix_ops import Data, reduce_alignment_tensor
from maths_fns.frame_order.rotor import compile_2nd_matrix_rotor, pcs_numeric_int_rotor, pcs_numeric_int_rotor_qrint
from maths_fns.frame_order.free_rotor import compile_2nd_matrix_free_rotor
from maths_fns.frame_order.iso_cone import compile_2nd_matrix_iso_cone, pcs_numeric_int_iso_cone, pcs_numeric_int_iso_cone_qrint
from maths_fns.frame_order.iso_cone_free_rotor import compile_2nd_matrix_iso_cone_free_rotor
from maths_fns.frame_order.iso_cone_torsionless import compile_2nd_matrix_iso_cone_torsionless, pcs_numeric_int_iso_cone_torsionless, pcs_numeric_int_iso_cone_torsionless_qrint
from maths_fns.frame_order.pseudo_ellipse import compile_2nd_matrix_pseudo_ellipse, pcs_numeric_int_pseudo_ellipse, pcs_numeric_int_pseudo_ellipse_qrint
from maths_fns.frame_order.pseudo_ellipse_free_rotor import compile_2nd_matrix_pseudo_ellipse_free_rotor
from maths_fns.frame_order.pseudo_ellipse_torsionless import compile_2nd_matrix_pseudo_ellipse_torsionless, pcs_numeric_int_pseudo_ellipse_torsionless, pcs_numeric_int_pseudo_ellipse_torsionless_qrint
from maths_fns.kronecker_product import kron_prod
from maths_fns import order_parameters
from maths_fns.pcs import pcs_tensor
from maths_fns.rotation_matrix import euler_to_R_zyz
from maths_fns.rotation_matrix import two_vect_to_R
from maths_fns.rdc import rdc_tensor
from physical_constants import pcs_constant
from lib.errors import RelaxError


class Frame_order:
    """Class containing the target function of the optimisation of Frame Order matrix components."""

    def __init__(self, model=None, init_params=None, full_tensors=None, full_in_ref_frame=None, rdcs=None, rdc_errors=None, rdc_weights=None, rdc_vect=None, dip_const=None, pcs=None, pcs_errors=None, pcs_weights=None, atomic_pos=None, temp=None, frq=None, paramag_centre=zeros(3), scaling_matrix=None, num_int_pts=500, ave_pos_pivot=zeros(3), ave_pos_piv_sync=True, translation_opt=False, pivot=zeros(3), pivot_opt=False, quad_int=True):
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
        @keyword dip_const:         The dipolar constants for each RDC.  The indices correspond to the spin systems j.
        @type dip_const:            numpy rank-1 array
        @keyword pcs:               The PCS lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type pcs:                  numpy rank-2 array
        @keyword pcs_errors:        The PCS error lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_errors:           numpy rank-2 array
        @keyword pcs_weights:       The PCS weight lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_weights:          numpy rank-2 array
        @keyword atomic_pos:        The atomic positions of all spins for the PCS and PRE data.  The first index is the spin systems j and the second is the structure or state c.
        @type atomic_pos:           numpy rank-3 array
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
        @keyword ave_pos_pivot:     The pivot point to rotate all atoms about to the average domain position.  For example this can be the centre of mass of the moving domain.
        @type ave_pos_pivot:        numpy 3D rank-1 array
        @keyword ave_pos_piv_sync:  A flag which if True will cause pivot point to rotate to the average domain position to be synchronised with the motional pivot.  This will cause ave_pos_pivot argument to be ignored.
        @type ave_pos_piv_sync:     bool
        @keyword translation_opt:   A flag which if True will allow the pivot point of the motion to be optimised.
        @type translation_opt:      bool
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
        self.dip_const = dip_const
        self.pcs = pcs
        self.pcs_weights = pcs_weights
        self.atomic_pos = atomic_pos
        self.temp = temp
        self.frq = frq
        self.paramag_centre = paramag_centre
        self.total_num_params = len(init_params)
        self.num_int_pts = num_int_pts
        self.ave_pos_pivot = ave_pos_pivot
        self.ave_pos_piv_sync = ave_pos_piv_sync
        self.translation_opt = translation_opt
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

        # The total number of alignments.
        self.num_align = 0
        if rdcs != None:
            self.num_align = len(rdcs)
        elif pcs != None:
            self.num_align = len(pcs)

        # Set the RDC and PCS flags (indicating the presence of data).
        self.rdc_flag = [True] * self.num_align
        self.pcs_flag = [True] * self.num_align
        for align_index in range(self.num_align):
            if rdcs == None or len(rdcs[align_index]) == 0:
                self.rdc_flag[align_index] = False
            if pcs == None or len(pcs[align_index]) == 0:
                self.pcs_flag[align_index] = False
        self.rdc_flag_sum = sum(self.rdc_flag)
        self.pcs_flag_sum = sum(self.pcs_flag)

        # Default translation vector (if not optimised).
        self._translation_vector = zeros(3, float64)

        # Some checks.
        if self.rdc_flag_sum and (rdc_vect == None or not len(rdc_vect)):
            raise RelaxError("The rdc_vect argument " + repr(rdc_vect) + " must be supplied.")
        if self.pcs_flag_sum and (atomic_pos == None or not len(atomic_pos)):
            raise RelaxError("The atomic_pos argument " + repr(atomic_pos) + " must be supplied.")

        # The total number of spins.
        self.num_spins = 0
        if self.pcs_flag_sum:
            self.num_spins = len(pcs[0])

        # The total number of interatomic connections.
        self.num_interatom = 0
        if self.rdc_flag_sum:
            self.num_interatom = len(rdcs[0])

        # Set up the alignment data.
        for align_index in range(self.num_align):
            to_tensor(self.A_3D[align_index], self.full_tensors[5*align_index:5*align_index+5])

        # PCS errors.
        if self.pcs_flag_sum:
            err = False
            for i in range(len(pcs_errors)):
                for j in range(len(pcs_errors[i])):
                    if not isNaN(pcs_errors[i, j]):
                        err = True
            if err:
                self.pcs_error = pcs_errors
            else:
                # Missing errors (default to 0.1 ppm errors).
                self.pcs_error = 0.1 * 1e-6 * ones((self.num_align, self.num_spins), float64)

        # RDC errors.
        if self.rdc_flag_sum:
            err = False
            for i in range(len(rdc_errors)):
                for j in range(len(rdc_errors[i])):
                    if not isNaN(rdc_errors[i, j]):
                        err = True
            if err:
                self.rdc_error = rdc_errors
            else:
                # Missing errors (default to 1 Hz errors).
                self.rdc_error = ones((self.num_align, self.num_interatom), float64)

        # Missing data matrices (RDC).
        if self.rdc_flag_sum:
            self.missing_rdc = zeros((self.num_align, self.num_interatom), uint8)

        # Missing data matrices (PCS).
        if self.pcs_flag_sum:
            self.missing_pcs = zeros((self.num_align, self.num_spins), uint8)

        # Clean up problematic data and put the weights into the errors..
        if self.rdc_flag_sum or self.pcs_flag_sum:
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                if self.rdc_flag_sum:
                    for j in range(self.num_interatom):
                        if isNaN(self.rdc[align_index, j]):
                            # Set the flag.
                            self.missing_rdc[align_index, j] = 1

                            # Change the NaN to zero.
                            self.rdc[align_index, j] = 0.0

                            # Change the error to one (to avoid zero division).
                            self.rdc_error[align_index, j] = 1.0

                            # Change the weight to one.
                            rdc_weights[align_index, j] = 1.0

                    # The RDC weights.
                    if self.rdc_flag_sum:
                        self.rdc_error[align_index, j] = self.rdc_error[align_index, j] / sqrt(rdc_weights[align_index, j])

                # Loop over the PCSs.
                if self.pcs_flag_sum:
                    for j in range(self.num_spins):
                        if isNaN(self.pcs[align_index, j]):
                            # Set the flag.
                            self.missing_pcs[align_index, j] = 1

                            # Change the NaN to zero.
                            self.pcs[align_index, j] = 0.0

                            # Change the error to one (to avoid zero division).
                            self.pcs_error[align_index, j] = 1.0

                            # Change the weight to one.
                            pcs_weights[align_index, j] = 1.0

                    # The PCS weights.
                    if self.pcs_flag_sum:
                        self.pcs_error[align_index, j] = self.pcs_error[align_index, j] / sqrt(pcs_weights[align_index, j])

        # The paramagnetic centre vectors and distances.
        if self.pcs_flag_sum:
            # Initialise the data structures.
            self.paramag_unit_vect = zeros(atomic_pos.shape, float64)
            self.paramag_dist = zeros(self.num_spins, float64)
            self.pcs_const = zeros(self.num_align, float64)
            self.r_pivot_atom = zeros((3, self.num_spins), float32)
            self.r_pivot_atom_rev = zeros((3, self.num_spins), float32)
            self.r_ln_pivot = zeros((3, self.num_spins), float32)
            for j in range(self.num_spins):
                self.r_ln_pivot[:, j] = pivot - self.paramag_centre
            if self.paramag_centre == None:
                self.paramag_centre = zeros(3, float32)

            # Set up the paramagnetic constant (without the interatomic distance and in Angstrom units).
            for align_index in range(self.num_align):
                self.pcs_const[align_index] = pcs_constant(self.temp[align_index], self.frq[align_index], 1.0) * 1e30

        # PCS function, gradient, and Hessian matrices.
        if self.pcs_flag_sum:
            self.pcs_theta = zeros((self.num_align, self.num_spins), float64)
            self.pcs_theta_err = zeros((self.num_align, self.num_spins), float64)
            self.dpcs_theta = zeros((self.total_num_params, self.num_align, self.num_spins), float64)
            self.d2pcs_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_spins), float64)

        # RDC function, gradient, and Hessian matrices.
        if self.rdc_flag_sum:
            self.rdc_theta = zeros((self.num_align, self.num_interatom), float64)
            self.drdc_theta = zeros((self.total_num_params, self.num_align, self.num_interatom), float64)
            self.d2rdc_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_interatom), float64)

        # The quasi-random integration.
        if not quad_int and self.pcs_flag_sum and model not in ['rigid']:
            # The Sobol' sequence data and target function aliases (quasi-random integration).
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
        self.num_tensors = int(len(self.full_tensors) / 5)
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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_rotor(sigma_max=pi, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_free_rotor_qrint(self, params):
        """Target function for free rotor model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_rotor_qrint(points=self.sobol_angles, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])


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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_iso_cone(theta_max=cone_theta, sigma_max=sigma_max, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_qrint(self, params):
        """Target function for isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, theta, phi, cone_theta, sigma_max} where the first 3 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, cone_theta is the cone opening half angle, and sigma_max is the torsion angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_iso_cone_qrint(points=self.sobol_angles, theta_max=cone_theta, sigma_max=sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_iso_cone(theta_max=theta_max, sigma_max=pi, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_free_rotor_qrint(self, params):
        """Target function for free rotor isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_iso_cone_qrint(points=self.sobol_angles, theta_max=theta_max, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_iso_cone_torsionless(theta_max=cone_theta, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_torsionless_qrint(self, params):
        """Target function for torsionless isotropic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, cone_theta} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and cone_theta is cone opening angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_iso_cone_torsionless_qrint(points=self.sobol_angles, theta_max=cone_theta, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_pseudo_ellipse(theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=cone_sigma_max, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_pseudo_ellipse_qrint(points=self.sobol_angles, theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=cone_sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_pseudo_ellipse(theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=pi, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_free_rotor_qrint(self, params):
        """Target function for free_rotor pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the free_rotor pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_pseudo_ellipse_qrint(points=self.sobol_angles, theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_pseudo_ellipse_torsionless(theta_x=cone_theta_x, theta_y=cone_theta_y, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_torsionless_qrint(self, params):
        """Target function for torsionless pseudo-elliptic cone model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the torsionless pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_pseudo_ellipse_torsionless_qrint(points=self.sobol_angles, theta_x=cone_theta_x, theta_y=cone_theta_y, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma = params[3:6]
        else:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The PCS calculation.
                        vect = self.r_ln_pivot[:, 0] + r_pivot_atom
                        length = norm(vect)
                        self.pcs_theta[align_index, j] = pcs_tensor(self.pcs_const[align_index] / length**5, vect, self.A_3D[align_index])

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

            # PCS.
            if self.pcs_flag[align_index]:
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[:, j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[:, j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_int_rotor(sigma_max=sigma_max, c=self.pcs_const[align_index], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[:, 0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

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
        if self.translation_opt and self.pivot_opt:
            self._param_pivot = params[:3]
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params[6:]
        elif self.translation_opt:
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, sigma_max = params[3:]
        elif self.pivot_opt:
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
        for align_index in range(self.num_align):
            # RDCs.
            if self.rdc_flag[align_index]:
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag_sum:
            # Numerical integration of the PCSs.
            pcs_numeric_int_rotor_qrint(points=self.sobol_angles, sigma_max=sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs, error_flag=False)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def calc_vectors(self, pivot=None, R_ave=None, RT_ave=None):
        """Calculate the pivot to atom and lanthanide to pivot vectors for the target functions.

        @keyword pivot:     The pivot point.
        @type pivot:        numpy rank-1, 3D array
        @keyword R_ave:     The rotation matrix for rotating from the reference frame to the average position.
        @type R_ave:        numpy rank-2, 3D array
        @keyword RT_ave:    The transpose of R_ave.
        @type RT_ave:       numpy rank-2, 3D array
        """

        # The rotational pivot.
        if self.ave_pos_piv_sync:
            ave_pos_pivot = self._param_pivot
        else:
            ave_pos_pivot = self.ave_pos_pivot

        # The pivot to atom vectors.
        for j in range(self.num_spins):
            # The lanthanide to pivot vector.
            if self.pivot_opt:
                self.r_ln_pivot[:, j] = pivot - self.paramag_centre

            # Rotate then translate the atomic positions, then calculate the pivot to atom vector.
            self.r_pivot_atom[:, j] = dot(R_ave, self.atomic_pos[j] - ave_pos_pivot) + ave_pos_pivot
            self.r_pivot_atom[:, j] += self._translation_vector
            self.r_pivot_atom[:, j] -= pivot
            self.r_pivot_atom_rev[:, j] = dot(RT_ave, self.atomic_pos[j] - ave_pos_pivot) + ave_pos_pivot
            self.r_pivot_atom_rev[:, j] += self._translation_vector
            self.r_pivot_atom_rev[:, j] -= pivot


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
        self.sobol_angles = zeros((n, m), float32)

        # Loop over the points.
        for i in range(n):
            # The raw point.
            point, seed = i4_sobol(m, i)

            # Loop over the dimensions, converting the points to angles.
            for j in range(m):
                # The tilt angle - the angle of rotation about the x-y plane rotation axis.
                if dims[j] in ['theta']:
                    self.sobol_angles[i, j] = acos(2.0*point[j] - 1.0)

                # The angle defining the x-y plane rotation axis.
                if dims[j] in ['phi']:
                    self.sobol_angles[i, j] = 2.0 * pi * point[j]

                # The torsion angle - the angle of rotation about the z' axis.
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
        for align_index in range(self.num_tensors):
            # Tensor indices.
            index1 = align_index*5
            index2 = align_index*5+5

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
            if self.full_in_ref_frame[align_index]:
                self.A_3D_bc[align_index] = dot(transpose(self.R_ave), dot(self.tensor_3D, self.R_ave))

            # Rotate the tensor (inverse RT.X.R rotation).
            else:
                self.A_3D_bc[align_index] = dot(self.R_ave, dot(self.tensor_3D, transpose(self.R_ave)))

            # Convert the tensor back to 5D, rank-1 form, as the back-calculated reduced tensor.
            to_5D(self.A_5D_bc[index1:index2], self.A_3D_bc[align_index])
