###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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

# Python module imports.
from math import sqrt
from numpy import array, dot, eye, float64, ones, rank, transpose, zeros

# relax module imports.
from float import isNaN
from maths_fns.alignment_tensor import dAi_dAxx, dAi_dAyy, dAi_dAxy, dAi_dAxz, dAi_dAyz, to_tensor
from maths_fns.chi2 import chi2, dchi2_element, d2chi2_element
from maths_fns.paramag_centre import vectors_single_centre, vectors_centre_per_state
from maths_fns.pcs import ave_pcs_tensor, ave_pcs_tensor_ddeltaij_dAmn, ave_pcs_tensor_ddeltaij_dc, pcs_constant_grad, pcs_tensor
from maths_fns.rdc import ave_rdc_tensor, ave_rdc_tensor_dDij_dAmn, rdc_tensor
from maths_fns.rotation_matrix import euler_to_R_zyz
from physical_constants import pcs_constant
from relax_errors import RelaxError, RelaxImplementError


class N_state_opt:
    """Class containing the target function of the optimisation of the N-state model."""

    def __init__(self, model=None, N=None, init_params=None, probs=None, full_tensors=None, red_data=None, red_errors=None, full_in_ref_frame=None, fixed_tensors=None, pcs=None, pcs_errors=None, pcs_weights=None, rdcs=None, rdc_errors=None, rdc_weights=None, rdc_vect=None, temp=None, frq=None, dip_const=None, absolute_rdc=None, atomic_pos=None, paramag_centre=None, scaling_matrix=None, centre_fixed=True):
        """Set up the class instance for optimisation.

        The N-state models
        ==================

        All constant data required for the N-state model are initialised here.  Depending on the base data used for optimisation, different data structures can be supplied.  However a number of structures must be provided for the N-state model.  These are:

            - model, the type of N-state model.  This can be '2-domain', 'population', or 'fixed'.
            - N, the number of states (or structures).
            - init_params, the initial parameter values.
            - scaling_matrix, the matrix used for parameter scaling during optimisation.


        2-domain N-state model
        ----------------------

        If the model type is set to '2-domain', then the following data structures should be supplied:

            - full_tensors, the alignment tensors in matrix form.
            - red_data, the alignment tensors in 5D form in a rank-1 array.
            - red_errors, the alignment tensor errors in 5D form in a rank-1 array.  This data is not obligatory.
            - full_in_ref_frame, an array of flags specifying if the tensor in the reference frame is the full or reduced tensor.


        The population N-state model
        ============================

        In this model, populations are optimised for each state.  Additionally the alignment tensors for anisotropic data can also be optimised if they have not been supplied (through the full_tensors arg).


        PCS base data
        -------------

        If pseudocontact shift data is to be used for optimisation, then the following should be supplied:

            - pcs, the pseudocontact shifts.
            - pcs_errors, the optional pseudocontact shift error values.
            - temp, the temperatures of the experiments.
            - frq, the frequencies of the experiments.


        PCS and PRE base data
        ---------------------

        If either pseudocontact shift or PRE data is to be used for optimisation, then the following should be supplied:

            - atomic_pos, the positions of all atoms.
            - paramag_centre, the paramagnetic centre position.


        RDC base data
        -------------

        If residual dipolar coupling data is to be used for optimisation, then the following should be supplied:

            - rdcs, the residual dipolar couplings.
            - rdc_errors, the optional residual dipolar coupling errors.
            - rdc_vect, the interatomic vectors.
            - dip_const, the dipolar constants.
            - absolute_rdc, the flags specifying whether each RDC is signless.


        @keyword model:             The N-state model type.  This can be one of '2-domain', 'population' or 'fixed'.
        @type model:                str
        @keyword N:                 The number of states.
        @type N:                    int
        @keyword init_params:       The initial parameter values.  Optimisation must start at some point!
        @type init_params:          numpy float64 array
        @keyword probs:             The probabilities for each state c.  The length of this list should be equal to N.
        @type probs:                list of float
        @keyword full_tensors:      An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all full tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2, Syy2, Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn]
        @type full_tensors:         list of rank-2, 3D numpy arrays
        @keyword red_data:          An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced tensors.  The format is the same as for full_tensors.
        @type red_data:             numpy float64 array
        @keyword red_errors:        An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced tensors.  The array format is the same as for full_tensors.
        @type red_errors:           numpy float64 array
        @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
        @type full_in_ref_frame:    numpy rank-1 array
        @keyword fixed_tensors:     An array of flags specifying if the tensor is fixed or will be optimised.
        @type fixed_tensors:        list of bool
        @keyword pcs:               The PCS lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type pcs:                  numpy rank-2 array
        @keyword pcs_errors:        The PCS error lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_errors:           numpy rank-2 array
        @keyword pcs_weights:       The PCS weight lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_weights:          numpy rank-2 array
        @keyword rdcs:              The RDC lists.  The first index must correspond to the different alignment media i and the second index to the spin pairs k.
        @type rdcs:                 numpy rank-2 array
        @keyword rdc_errors:        The RDC error lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_errors:           numpy rank-2 array
        @keyword rdc_weights:       The RDC weight lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_weights:          numpy rank-2 array
        @keyword rdc_vect:          The unit vector lists for the RDC.  The first index must correspond to the spin pair and the second index to each structure (its size being equal to the number of states).
        @type rdc_vect:             numpy rank-2 array
        @keyword temp:              The temperature of each experiment, used for the PCS.
        @type temp:                 numpy rank-1 array
        @keyword frq:               The frequency of each alignment, used for the PCS.
        @type frq:                  numpy rank-1 array
        @keyword dip_const:         The dipolar constants for each spin pair.  The indices correspond to the spin pairs k.
        @type dip_const:            numpy rank-1 array
        @keyword absolute_rdc:      The signless or absolute value flags for the RDCs.
        @type absolute_rdc:         numpy rank-2 array
        @keyword atomic_pos:        The atomic positions of all spins for the PCS and PRE data.  The first index is the spin systems j and the second is the structure or state c.
        @type atomic_pos:           numpy rank-3 array
        @keyword paramag_centre:    The paramagnetic centre position (or positions).
        @type paramag_centre:       numpy rank-1, 3D array or rank-2, Nx3 array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 array
        @keyword centre_fixed:      A flag which if False will cause the paramagnetic centre to be optimised.
        @type centre_fixed:         bool
        """

        # Store the data inside the class instance namespace.
        self.N = N
        self.params = 1.0 * init_params    # Force a copy of the data to be stored.
        self.fixed_tensors = fixed_tensors
        self.deltaij = pcs
        self.rdc = rdcs
        self.dip_vect = rdc_vect
        self.dip_const = dip_const
        self.absolute_rdc = absolute_rdc
        self.temp = temp
        self.frq = frq
        self.atomic_pos = atomic_pos
        self.paramag_centre = paramag_centre
        self.centre_fixed = centre_fixed
        self.total_num_params = len(init_params)

        # Initialise the function value, gradient, and Hessian.
        self.chi2 = 0.0
        self.dchi2 = zeros((self.total_num_params), float64)
        self.d2chi2 = zeros((self.total_num_params, self.total_num_params), float64)

        # Scaling initialisation.
        self.scaling_matrix = scaling_matrix
        if self.scaling_matrix != None:
            self.scaling_flag = True
        else:
            self.scaling_flag = False

        # The 2-domain N-state model.
        if model == '2-domain':
            # Some checks.
            if red_data == None or not len(red_data):
                raise RelaxError("The red_data argument " + repr(red_data) + " must be supplied.")
            if red_errors == None or not len(red_errors):
                raise RelaxError("The red_errors argument " + repr(red_errors) + " must be supplied.")
            if full_in_ref_frame == None or not len(full_in_ref_frame):
                raise RelaxError("The full_in_ref_frame argument " + repr(full_in_ref_frame) + " must be supplied.")

            # Tensor set up.
            self.full_tensors = array(full_tensors, float64)
            self.num_tensors = int(len(self.full_tensors) / 5)
            self.red_data = red_data
            self.red_errors = red_errors
            self.full_in_ref_frame = full_in_ref_frame

            # Alignment tensor in rank-2, 3D form.
            self.A = zeros((self.num_tensors, 3, 3), float64)
            for align_index in range(self.num_tensors):
                to_tensor(self.A[align_index], self.full_tensors[5*align_index:5*align_index+5])

            # Initialise some empty numpy objects for storage of:
            # R:  the transient rotation matricies.
            # RT:  the transposes of the rotation matricies.
            # red_bc:  the back-calculated reduced alignment tensors.
            # red_bc_vector:  the back-calculated reduced alignment tensors in vector form {Sxx, Syy, Sxy, Sxz, Syz}.
            self.R = zeros((self.N, 3, 3), float64)
            self.RT = zeros((self.N, 3, 3), float64)
            self.red_bc = zeros((self.num_tensors, 3, 3), float64)
            self.red_bc_vector = zeros(self.num_tensors*5, float64)

            # Set the target function.
            self.func = self.func_2domain
            self.dfunc = None
            self.d2func = None

        # The flexible population or equal probability N-state models.
        elif model in ['population', 'fixed']:
            # The total number of alignments (must be the same for the RDC and PCS data).
            self.num_align = 0
            if rdcs != None:
                self.num_align = len(rdcs)
            if pcs != None:
                self.num_align = max(self.num_align, len(pcs))

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

            # Alignment tensor function and gradient matrices.
            self.A = zeros((self.num_align, 3, 3), float64)
            self.dA = zeros((5, 3, 3), float64)

            # Fixed alignment tensors.
            if full_tensors != None:
                # Convert to numpy.
                self.full_tensors = array(full_tensors, float64)

            # Set up the alignment data.
            self.num_align_params = 0
            index = 0
            for align_index in range(self.num_align):
                # Fill the alignment tensor object with the fixed tensors.
                if fixed_tensors[align_index]:
                    to_tensor(self.A[align_index], self.full_tensors[5*index:5*index+5])
                    index += 1

                # The number of alignment parameters.
                if not fixed_tensors[align_index]:
                    self.num_align_params += 5

            # Optimised alignment tensors.
            else:
                # The alignment tensor gradients don't change, so pre-calculate them.
                dAi_dAxx(self.dA[0])
                dAi_dAyy(self.dA[1])
                dAi_dAxy(self.dA[2])
                dAi_dAxz(self.dA[3])
                dAi_dAyz(self.dA[4])

            # PCS errors.
            if self.pcs_flag_sum:
                err = False
                for i in range(len(pcs_errors)):
                    for j in range(len(pcs_errors[i])):
                        if not isNaN(pcs_errors[i, j]):
                            err = True
                if err:
                    self.pcs_errors = pcs_errors
                else:
                    # Missing errors (the values need to be small, close to ppm units, so the chi-squared value is comparable to the RDC).
                    self.pcs_errors = 0.03 * 1e-6 * ones((self.num_align, self.num_spins), float64)

            # RDC errors.
            if self.rdc_flag_sum:
                err = False
                for i in range(len(rdc_errors)):
                    for j in range(len(rdc_errors[i])):
                        if not isNaN(rdc_errors[i, j]):
                            err = True
                if err:
                    self.rdc_errors = rdc_errors
                else:
                    # Missing errors.
                    self.rdc_errors = ones((self.num_align, self.num_interatom), float64)

            # Missing data matrices (RDC).
            if self.rdc_flag_sum:
                self.missing_rdc = zeros((self.num_align, self.num_interatom), float64)

            # Missing data matrices (PCS).
            if self.pcs_flag_sum:
                self.missing_deltaij = zeros((self.num_align, self.num_spins), float64)

            # Clean up problematic data and put the weights into the errors..
            if self.rdc_flag_sum or self.pcs_flag_sum:
                for align_index in range(self.num_align):
                    if self.rdc_flag_sum:
                        for j in range(self.num_interatom):
                            if isNaN(self.rdc[align_index, j]):
                                # Set the flag.
                                self.missing_rdc[align_index, j] = 1

                                # Change the NaN to zero.
                                self.rdc[align_index, j] = 0.0

                                # Change the error to one (to avoid zero division).
                                self.rdc_errors[align_index, j] = 1.0

                                # Change the weight to one.
                                rdc_weights[align_index, j] = 1.0

                            # The RDC weights.
                            self.rdc_errors[align_index, j] = self.rdc_errors[align_index, j] / sqrt(rdc_weights[align_index, j])


                    if self.pcs_flag_sum:
                        for j in range(self.num_spins):
                            if isNaN(self.deltaij[align_index, j]):
                                # Set the flag.
                                self.missing_deltaij[align_index, j] = 1

                                # Change the NaN to zero.
                                self.deltaij[align_index, j] = 0.0

                                # Change the error to one (to avoid zero division).
                                self.pcs_errors[align_index, j] = 1.0

                                # Change the weight to one.
                                pcs_weights[align_index, j] = 1.0

                            # The PCS weights.
                            self.pcs_errors[align_index, j] = self.pcs_errors[align_index, j] / sqrt(pcs_weights[align_index, j])

            # The paramagnetic centre vectors and distances.
            if self.pcs_flag_sum:
                # Initialise the data structures.
                self.paramag_unit_vect = zeros(atomic_pos.shape, float64)
                self.paramag_dist = zeros((self.num_spins, self.N), float64)
                self.pcs_const = zeros((self.num_align, self.num_spins, self.N), float64)
                if self.paramag_centre == None:
                    self.paramag_centre = zeros(3, float64)

                # The gradient structures.
                if not self.centre_fixed:
                    self.dpcs_const_theta = zeros((self.num_align, self.num_spins, self.N, 3), float64)
                    self.dr_theta = -eye(3)

                # Set up the paramagnetic info.
                self.paramag_info()

            # PCS function, gradient, and Hessian matrices.
            self.deltaij_theta = zeros((self.num_align, self.num_spins), float64)
            self.ddeltaij_theta = zeros((self.total_num_params, self.num_align, self.num_spins), float64)
            self.d2deltaij_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_spins), float64)

            # RDC function, gradient, and Hessian matrices.
            self.rdc_theta = zeros((self.num_align, self.num_interatom), float64)
            self.drdc_theta = zeros((self.total_num_params, self.num_align, self.num_interatom), float64)
            self.d2rdc_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_interatom), float64)

            # Set the target function, gradient, and Hessian.
            self.func = self.func_standard
            self.dfunc = self.dfunc_standard
            self.d2func = self.d2func_standard

        # Variable probabilities.
        self.probs_fixed = True
        if model == 'population':
            self.probs_fixed = False

        # Fixed probabilities.
        if model == 'fixed':
            # The zero Hessian.
            self.zero_hessian_rdc = zeros(self.num_interatom, float64)
            self.zero_hessian_pcs = zeros(self.num_spins, float64)

            # The probability array.
            if probs:
                self.probs = probs

            # All structures have initial equal probability.
            else:
                self.probs = ones(self.N, float64) / self.N


    def func_2domain(self, params):
        """The target function for optimisation of the 2-domain N-state model.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a vector of parameter values and, using these, returns the single chi-squared value corresponding to that coordinate in the parameter space.  If no tensor errors are supplied, then the SSE (the sum of squares error) value is returned instead.  The chi-squared is simply the SSE normalised to unit variance (the SSE divided by the error squared).

        @param params:  The vector of parameter values.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Reset the back-calculated the reduced tensor structure.
        self.red_bc = self.red_bc * 0.0

        # Loop over the N states.
        for c in range(self.N):
            # The rotation matrix.
            euler_to_R_zyz(params[self.N-1+3*c], params[self.N-1+3*c+1], params[self.N-1+3*c+2], self.R[c])

            # Its transpose.
            self.RT[c] = transpose(self.R[c])

            # The probability of state c.
            if c < self.N-1:
                pc = params[c]

            # The probability of state N (1 minus the pc of all other states).
            else:
                pc = 1.0
                for c2 in range(self.N-1):
                    pc = pc - params[c2]

            # Back-calculate the reduced tensors for sum element c and add these to red_bc.
            for align_index in range(self.num_tensors):
                # Normal RT.X.R rotation.
                if self.full_in_ref_frame[align_index]:
                    self.red_bc[align_index] = self.red_bc[align_index]  +  pc * dot(self.RT[c], dot(self.A[align_index], self.R[c]))

                # Inverse R.X.RT rotation.
                else:
                    self.red_bc[align_index] = self.red_bc[align_index]  +  pc * dot(self.R[c], dot(self.A[align_index], self.RT[c]))

        # 5D vectorise the back-calculated tensors (create red_bc_vector from red_bc).
        for align_index in range(self.num_tensors):
            self.red_bc_vector[5*align_index]   = self.red_bc[align_index, 0, 0]    # Sxx.
            self.red_bc_vector[5*align_index+1] = self.red_bc[align_index, 1, 1]    # Syy.
            self.red_bc_vector[5*align_index+2] = self.red_bc[align_index, 0, 1]    # Sxy.
            self.red_bc_vector[5*align_index+3] = self.red_bc[align_index, 0, 2]    # Sxz.
            self.red_bc_vector[5*align_index+4] = self.red_bc[align_index, 1, 2]    # Syz.

        # Return the chi-squared value.
        return chi2(self.red_data, self.red_bc_vector, self.red_errors)


    def func_standard(self, params):
        """The target function for optimisation of the standard N-state model.

        Description
        ===========

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a vector of parameter values and, using these, returns the single chi-squared value corresponding to that coordinate in the parameter space.  If no RDC or PCS errors errors are supplied, then the SSE (the sum of squares error) value is returned instead.  The chi-squared is simply the SSE normalised to unit variance (the SSE divided by the error squared).


        Indices
        =======

        For this calculation, five indices are looped over and used in the various data structures.  These include:
            - i, the index over alignments,
            - j, the index over spin systems,
            - c, the index over the N-states (or over the structures),
            - n, the index over the first dimension of the alignment tensor n = {x, y, z},
            - m, the index over the second dimension of the alignment tensor m = {x, y, z}.


        Equations
        =========

        To calculate the function value, a chain of equations are used.  This includes the chi-squared equation and the RDC and PCS equations.


        The chi-squared equation
        ------------------------

        The equations are::

                         ___
                         \    (Dij - Dij(theta)) ** 2
         chi^2(theta)  =  >   ----------------------- ,
                         /__       sigma_ij ** 2
                          ij

                         ___
                         \    (delta_ij - delta_ij(theta)) ** 2
         chi^2(theta)  =  >   --------------------------------- ,
                         /__             sigma_ij ** 2
                          ij

        where:
            - theta is the parameter vector,
            - Dij are the measured RDCs for alignment i, spin j,
            - Dij(theta) are the back calculated RDCs for alignment i, spin j,
            - delta_ij are the measured PCSs for alignment i, spin j,
            - delta_ij(theta) are the back calculated PCSs for alignment i, spin j,
            - sigma_ij are the RDC or PCS errors.

        Both chi-squared values sum.


        The RDC equation
        ----------------

        The RDC equation is::

                           _N_
                           \              T
         Dij(theta)  =  dj  >   pc . mu_jc . Ai . mu_jc,
                           /__
                           c=1

        where:
            - dj is the dipolar constant for spin j,
            - N is the total number of states or structures,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        In the fixed and equal probability case, the equation is::

                           _N_
                        dj \         T
         Dij(theta)  =  --  >   mu_jc . Ai . mu_jc,
                        N  /__
                           c=1

        The dipolar constant is henceforth defined as::

            dj = 3 / (2pi) d',

        where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is associated with the alignment tensor and the pure dipolar constant in SI units is::

                   mu0 gI.gS.h_bar
            d' = - --- ----------- ,
                   4pi    r**3

        where:
            - mu0 is the permeability of free space,
            - gI and gS are the gyromagnetic ratios of the I and S spins,
            - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
            - r is the distance between the two spins.


        The PCS equation
        ----------------

        The PCS equation is::

                               _N_
                               \                    T
            delta_ij(theta)  =  >  pc . dijc . mu_jc . Ai . mu_jc,
                               /__
                               c=1

        where:
            - djci is the PCS constant for spin j, state c and experiment or alignment i,
            - N is the total number of states or structures,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        In the fixed and equal probability case, the equation is::

                                 _N_
                               1 \               T
            delta_ij(theta)  = -  >  dijc . mu_jc . Ai . mu_jc,
                               N /__
                                 c=1

        The PCS constant is defined as::

                   mu0 15kT   1
            dijc = --- ----- ---- ,
                   4pi Bo**2 r**3

        where:
            - mu0 is the permeability of free space,
            - k is Boltzmann's constant,
            - T is the absolute temperature (different for each experiment),
            - Bo is the magnetic field strength (different for each experiment),
            - r is the distance between the paramagnetic centre (electron spin) and the nuclear spin (different for each spin and state).


        Stored data structures
        ======================

        There are a number of data structures calculated by this function and stored for subsequent use in the gradient and Hessian functions.  This include the back calculated RDCs and PCSs and the alignment tensors.

        Dij(theta)
        ----------

        The back calculated RDCs.  This is a rank-2 tensor with indices {i, j}.

        delta_ij(theta)
        ---------------

        The back calculated PCS.  This is a rank-2 tensor with indices {i, j}.

        Ai
        --

        The alignment tensors.  This is a rank-3 tensor with indices {i, n, m}.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Unpack both the probabilities (when the paramagnetic centre is also optimised).
        if not self.probs_fixed and not self.centre_fixed:
            # The probabilities.
            self.probs = params[-(self.N-1)-3:-3]

        # Unpack the probabilities (located at the end of the parameter array).
        elif not self.probs_fixed:
            self.probs = params[-(self.N-1):]

        # Unpack the paramagnetic centre (also update the paramagnetic info).
        if not self.centre_fixed:
            self.paramag_centre = params[-3:]
            self.paramag_info()

        # Loop over each alignment.
        index = 0
        for align_index in range(self.num_align):
            # Create tensor i from the parameters.
            if not self.fixed_tensors[align_index]:
                to_tensor(self.A[align_index], params[5*index:5*index + 5])
                index += 1

            # The back calculated RDC.
            if self.rdc_flag[align_index]:
                # Loop over the spin pairs k.
                for j in range(self.num_interatom):
                    # Calculate the average RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = ave_rdc_tensor(self.dip_const[j], self.dip_vect[j], self.N, self.A[align_index], weights=self.probs, absolute=self.absolute_rdc[align_index, j])

            # The back calculated PCS.
            if self.pcs_flag[align_index]:
                # Loop over the spin systems j.
                for j in range(self.num_spins):
                    # Calculate the average PCS.
                    if not self.missing_deltaij[align_index, j]:
                        self.deltaij_theta[align_index, j] = ave_pcs_tensor(self.pcs_const[align_index, j], self.paramag_unit_vect[j], self.N, self.A[align_index], weights=self.probs)

            # Calculate and sum the single alignment chi-squared value (for the RDC).
            if self.rdc_flag[align_index]:
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_errors[align_index])

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            if self.pcs_flag[align_index]:
                chi2_sum = chi2_sum + chi2(self.deltaij[align_index], self.deltaij_theta[align_index], self.pcs_errors[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def dfunc_standard(self, params):
        """The gradient function for optimisation of the standard N-state model.

        Description
        ===========

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a vector of parameter values and, using these, returns the chi-squared gradient corresponding to that coordinate in the parameter space.  If no RDC or PCS errors are supplied, then the SSE (the sum of squares error) gradient is returned instead.  The chi-squared gradient is simply the SSE gradient normalised to unit variance (the SSE divided by the error squared).


        Indices
        =======

        For this calculation, six indices are looped over and used in the various data structures.  These include:
            - k, the index over all parameters,
            - i, the index over alignments,
            - j, the index over spin systems,
            - c, the index over the N-states (or over the structures),
            - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
            - n, the index over the second dimension of the alignment tensor n = {x, y, z},


        Equations
        =========

        To calculate the chi-squared gradient, a chain of equations are used.  This includes the chi-squared gradient, the RDC gradient and the alignment tensor gradient.


        The chi-squared gradient
        ------------------------

        The equation is::
                              ___
         dchi^2(theta)        \   / Dij - Dij(theta)     dDij(theta) \ 
         -------------  =  -2  >  | ----------------  .  ----------- |
            dthetak           /__ \   sigma_ij**2         dthetak    /
                              ij

        where:
            - theta is the parameter vector,
            - Dij are the measured RDCs or PCSs,
            - Dij(theta) are the back calculated RDCs or PCSs,
            - sigma_ij are the RDC or PCS errors,
            - dDij(theta)/dthetak is the RDC or PCS gradient for parameter k.


        The RDC gradient
        ----------------

        This gradient is different for the various parameter types.

        pc partial derivative
        ~~~~~~~~~~~~~~~~~~~~~

        The population parameter partial derivative is::

             dDij(theta)               T
             -----------  =  dj . mu_jc . Ai . mu_jc,
                 dpc

        where:
            - dj is the dipolar constant for spin j,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        Amn partial derivative
        ~~~~~~~~~~~~~~~~~~~~~~

        The alignment tensor element partial derivative is::

                            _N_
         dDij(theta)        \              T   dAi
         -----------  =  dj  >   pc . mu_jc . ---- . mu_jc,
            dAmn            /__               dAmn
                            c=1

        where:
            - dj is the dipolar constant for spin j,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - dAi/dAmn is the partial derivative of the alignment tensor with respect to element Amn.

        In the case of fixed and equal populations, the equation is::

                            _N_
         dDij(theta)     dj \         T   dAi
         -----------  =  --  >   mu_jc . ---- . mu_jc,
            dAmn         N  /__          dAmn
                            c=1


        The PCS gradient
        ----------------

        This gradient is also different for the various parameter types.

        pc partial derivative
        ~~~~~~~~~~~~~~~~~~~~~

        The population parameter partial derivative is::

             ddeltaij(theta)                 T
             ---------------  =  dijc . mu_jc . Ai . mu_jc,
                  dpc

        where:
            - djc is the pseudocontact shift constant for spin j and state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        Amn partial derivative
        ~~~~~~~~~~~~~~~~~~~~~~

        The alignment tensor element partial derivative is::

                                _N_
            ddelta_ij(theta)    \                   T   dAi
            ----------------  =  >  pc . djc . mu_jc . ---- . mu_jc,
                  dAmn          /__                    dAmn
                                c=1

        where:
            - djc is the pseudocontact shift constant for spin j and state c,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - dAi/dAmn is the partial derivative of the alignment tensor with respect to element Amn.

        In the case of fixed and equal populations, the equation is::

                                  _N_
            ddelta_ij(theta)    1 \              T   dAi
            ----------------  = -  >  djc . mu_jc . ---- . mu_jc,
                  dAmn          N /__               dAmn
                                  c=1

        xi partial derivative
        ~~~~~~~~~~~~~~~~~~~~~

        The paramagnetic position partial derivative is::

                                _N_
            ddelta_ij(theta)    \        / ddjc                       dr_jcT                          dr_jc \ 
            ----------------  =  >  pc . | ----.r_jcT.Ai.r_jc  +  djc.------.Ai.r_jc  +  djc.r_jcT.Ai.----- | ,
                  dxi           /__      \ dxi                         dxi                             dxi  /
                                c=1

        where xi are the paramagnetic position coordinates {x0, x1, x2} and the last two terms in the sum are equal due to the symmetry of the alignment tensor, and::

            ddjc    mu0 15kT                 5 (si - xi)
            ----  = --- ----- ---------------------------------------------  ,
            dxi     4pi Bo**2 ((sx-x0)**2 + (sy-x1)**2 + (sz-x2)**2)**(7/2)

        and::

            dr      | 1 |   dr      | 0 |   dr      | 0 |
            --  = - | 0 | , --  = - | 1 | , --  = - | 0 | .
            dx      | 0 |   dy      | 0 |   dy      | 1 |

        The pseudocontact shift constant is defined here as::

                  mu0 15kT    1
            djc = --- ----- ------ ,
                  4pi Bo**2 rjc**5


        The alignment tensor gradient
        -----------------------------

        The five unique elements of the tensor {Axx, Ayy, Axy, Axz, Ayz} give five different partial derivatives.  These are::

             dAi   | 1  0  0 |
            ---- = | 0  0  0 |,
            dAxx   | 0  0 -1 |

             dAi   | 0  0  0 |
            ---- = | 0  1  0 |,
            dAyy   | 0  0 -1 |

             dAi   | 0  1  0 |
            ---- = | 1  0  0 |,
            dAxy   | 0  0  0 |

             dAi   | 0  0  1 |
            ---- = | 0  0  0 |,
            dAxz   | 1  0  0 |

             dAi   | 0  0  0 |
            ---- = | 0  0  1 |.
            dAyz   | 0  1  0 |

        As these are invariant, they can be pre-calculated.


        Stored data structures
        ======================

        There are a number of data structures calculated by this function and stored for subsequent use in the Hessian function.  This include the back calculated RDC and PCS gradients and the alignment tensor gradients.

        dDij(theta)/dthetak
        -------------------

        The back calculated RDC gradient.  This is a rank-3 tensor with indices {k, i, j}.

        ddeltaij(theta)/dthetak
        -----------------------

        The back calculated PCS gradient.  This is a rank-3 tensor with indices {k, i, j}.

        dAi/dAmn
        --------

        The alignment tensor gradients.  This is a rank-3 tensor with indices {5, n, m}.


        @param params:  The vector of parameter values.  This is unused as it is assumed that func() was called first.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE gradient.
        @rtype:         numpy rank-1 array
        """

        # Initial chi-squared (or SSE) gradient.
        self.dchi2 = self.dchi2 * 0.0

        # Loop over each alignment.
        for align_index in range(self.num_align):
            # Construct the Amn partial derivative components for the RDC.
            if not self.fixed_tensors[align_index]:
                for j in range(self.num_interatom):
                    if self.rdc_flag[align_index] and not self.missing_rdc[align_index, j]:
                        self.drdc_theta[align_index*5,   align_index, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.dip_vect[j], self.N, self.dA[0], weights=self.probs, absolute=self.absolute_rdc[align_index, j])
                        self.drdc_theta[align_index*5+1, align_index, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.dip_vect[j], self.N, self.dA[1], weights=self.probs, absolute=self.absolute_rdc[align_index, j])
                        self.drdc_theta[align_index*5+2, align_index, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.dip_vect[j], self.N, self.dA[2], weights=self.probs, absolute=self.absolute_rdc[align_index, j])
                        self.drdc_theta[align_index*5+3, align_index, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.dip_vect[j], self.N, self.dA[3], weights=self.probs, absolute=self.absolute_rdc[align_index, j])
                        self.drdc_theta[align_index*5+4, align_index, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.dip_vect[j], self.N, self.dA[4], weights=self.probs, absolute=self.absolute_rdc[align_index, j])

            # Construct the Amn partial derivative components for the PCS.
            if not self.fixed_tensors[align_index]:
                for j in range(self.num_spins):
                    if self.pcs_flag[align_index] and not self.missing_deltaij[align_index, j]:
                        self.ddeltaij_theta[align_index*5, align_index, j] = ave_pcs_tensor_ddeltaij_dAmn(self.pcs_const[align_index, j], self.paramag_unit_vect[j], self.N, self.dA[0], weights=self.probs)
                        self.ddeltaij_theta[align_index*5+1, align_index, j] = ave_pcs_tensor_ddeltaij_dAmn(self.pcs_const[align_index, j], self.paramag_unit_vect[j], self.N, self.dA[1], weights=self.probs)
                        self.ddeltaij_theta[align_index*5+2, align_index, j] = ave_pcs_tensor_ddeltaij_dAmn(self.pcs_const[align_index, j], self.paramag_unit_vect[j], self.N, self.dA[2], weights=self.probs)
                        self.ddeltaij_theta[align_index*5+3, align_index, j] = ave_pcs_tensor_ddeltaij_dAmn(self.pcs_const[align_index, j], self.paramag_unit_vect[j], self.N, self.dA[3], weights=self.probs)
                        self.ddeltaij_theta[align_index*5+4, align_index, j] = ave_pcs_tensor_ddeltaij_dAmn(self.pcs_const[align_index, j], self.paramag_unit_vect[j], self.N, self.dA[4], weights=self.probs)

            # Construct the pc partial derivative gradient components, looping over each state.
            if not self.probs_fixed:
                # Shift the parameter index if the paramagnetic position is optimised.
                x = 0
                if not self.centre_fixed:
                    x = 3

                # Loop over each state.
                for c in range(self.N - 1 - x):
                    # Index in the parameter array.
                    param_index = self.num_align_params + c

                    # Calculate the RDC for state c (this is the pc partial derivative).
                    for j in range(self.num_interatom):
                        if self.rdc_flag[align_index] and not self.missing_rdc[align_index, j]:
                            self.drdc_theta[param_index, align_index, j] = rdc_tensor(self.dip_const[j], self.dip_vect[j, c], self.A[align_index], absolute=self.absolute_rdc[align_index, j])

                    # Calculate the PCS for state c (this is the pc partial derivative).
                    for j in range(self.num_spins):
                        if self.pcs_flag[align_index] and not self.missing_deltaij[align_index, j]:
                            self.ddeltaij_theta[param_index, align_index, j] = pcs_tensor(self.pcs_const[align_index, j, c], self.paramag_unit_vect[j, c], self.A[align_index])

            # Construct the paramagnetic centre c partial derivative components for the PCS.
            if not self.centre_fixed:
                for j in range(self.num_spins):
                    if self.pcs_flag[align_index] and not self.missing_deltaij[align_index, j]:
                        self.ddeltaij_theta[-3, align_index, j] = ave_pcs_tensor_ddeltaij_dc(ddj=self.dpcs_const_theta[align_index, j, :, 0], dj=self.pcs_const[align_index, j], r=self.paramag_dist[j], unit_vect=self.paramag_unit_vect[j], N=self.N, Ai=self.A[align_index], dr_dc=self.dr_theta[0], weights=self.probs)
                        self.ddeltaij_theta[-2, align_index, j] = ave_pcs_tensor_ddeltaij_dc(ddj=self.dpcs_const_theta[align_index, j, :, 1], dj=self.pcs_const[align_index, j], r=self.paramag_dist[j], unit_vect=self.paramag_unit_vect[j], N=self.N, Ai=self.A[align_index], dr_dc=self.dr_theta[1], weights=self.probs)
                        self.ddeltaij_theta[-1, align_index, j] = ave_pcs_tensor_ddeltaij_dc(ddj=self.dpcs_const_theta[align_index, j, :, 2], dj=self.pcs_const[align_index, j], r=self.paramag_dist[j], unit_vect=self.paramag_unit_vect[j], N=self.N, Ai=self.A[align_index], dr_dc=self.dr_theta[2], weights=self.probs)

            # Construct the chi-squared gradient element for parameter k, alignment i.
            for k in range(self.total_num_params):
                # RDC part of the chi-squared gradient.
                if self.rdc_flag[align_index]:
                    self.dchi2[k] = self.dchi2[k] + dchi2_element(self.rdc[align_index], self.rdc_theta[align_index], self.drdc_theta[k, align_index], self.rdc_errors[align_index])

                # PCS part of the chi-squared gradient.
                if self.pcs_flag[align_index]:
                    self.dchi2[k] = self.dchi2[k] + dchi2_element(self.deltaij[align_index], self.deltaij_theta[align_index], self.ddeltaij_theta[k, align_index], self.pcs_errors[align_index])

        # Diagonal scaling.
        if self.scaling_flag:
            self.dchi2 = dot(self.dchi2, self.scaling_matrix)

        # Return a copy of the gradient.
        return self.dchi2 * 1.0


    def d2func_standard(self, params):
        """The Hessian function for optimisation of the standard N-state model.

        Description
        ===========

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a vector of parameter values and, using these, returns the chi-squared Hessian corresponding to that coordinate in the parameter space.  If no RDC/PCS errors are supplied, then the SSE (the sum of squares error) Hessian is returned instead.  The chi-squared Hessian is simply the SSE Hessian normalised to unit variance (the SSE divided by the error squared).


        Indices
        =======

        For this calculation, six indices are looped over and used in the various data structures.  These include:
            - k, the index over all parameters,
            - i, the index over alignments,
            - j, the index over spin systems,
            - c, the index over the N-states (or over the structures),
            - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
            - n, the index over the second dimension of the alignment tensor n = {x, y, z},


        Equations
        =========

        To calculate the chi-squared gradient, a chain of equations are used.  This includes the chi-squared gradient, the RDC gradient and the alignment tensor gradient.


        The chi-squared Hessian
        -----------------------

        The equation is::
                               ___
         d2chi^2(theta)        \       1      / dDij(theta)   dDij(theta)                         d2Dij(theta)   \ 
         ---------------  =  2  >  ---------- | ----------- . -----------  -  (Dij-Dij(theta)) . --------------- |.
         dthetaj.dthetak       /__ sigma_i**2 \  dthetaj       dthetak                           dthetaj.dthetak /
                               ij

        where:
            - theta is the parameter vector,
            - Dij are the measured RDCs or PCSs,
            - Dij(theta) are the back calculated RDCs or PCSs,
            - sigma_ij are the RDC or PCS errors,
            - dDij(theta)/dthetak is the RDC or PCS gradient for parameter k.
            - d2Dij(theta)/dthetaj.dthetak is the RDC or PCS Hessian for parameters j and k.


        The RDC Hessian
        ---------------

        pc-pd second partial derivatives
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The probability parameter second partial derivative is::

         d2Dij(theta)
         ------------  =  0.
           dpc.dpd


        pc-Anm second partial derivatives
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The probability parameter-tensor element second partial derivative is::

         d2Dij(theta)               T   dAi
         ------------  =  dj . mu_jc . ---- . mu_jc.
           dpc.dAmn                    dAmn


        Amn-Aop second partial derivatives
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The alignment tensor element second partial derivative is::

         d2Dij(theta)
         ------------  =  0.
          dAmn.dAop


        The PCS Hessian
        ---------------

        pc-pd second partial derivatives
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The probability parameter second partial derivative is::

         d2delta_ij(theta)
         -----------------  =  0.
              dpc.dpd


        pc-Anm second partial derivatives
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The probability parameter-tensor element second partial derivative is::

         d2delta_ij(theta)                T   dAi
         -----------------  =  djc . mu_jc . ---- . mu_jc.
             dpc.dAmn                        dAmn


        Amn-Aop second partial derivatives
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The alignment tensor element second partial derivative is::

            d2delta_ij(theta)
            -----------------  =  0
                dAmn.dAop


        The alignment tensor Hessian
        ----------------------------

        The five unique elements of the tensor {Axx, Ayy, Axy, Axz, Ayz} all have the same second partial derivative of::

              d2Ai      | 0  0  0 |
            --------- = | 0  0  0 |.
            dAmn.dAop   | 0  0  0 |


        @param params:  The vector of parameter values.  This is unused as it is assumed that func() was called first.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE Hessian.
        @rtype:         numpy rank-2 array
        """

        # Initial chi-squared (or SSE) Hessian.
        self.d2chi2 = self.d2chi2 * 0.0

        # Loop over each alignment.
        for align_index in range(self.num_align):
            # Construct the pc-Amn second partial derivative Hessian components.
            if not self.probs_fixed:
                for c in range(self.N - 1):
                    # Index in the parameter array.
                    pc_index = self.num_align_params + c

                    # Calculate the RDC Hessian component.
                    for j in range(self.num_interatom):
                        if self.fixed_tensors[align_index] and self.rdc_flag[align_index] and not self.missing_rdc[align_index, j]:
                            self.d2rdc_theta[pc_index, align_index*5+0, align_index, j] = self.d2rdc_theta[align_index*5+0, pc_index, align_index, j] = rdc_tensor(self.dip_const[j], self.dip_vect[j, c], self.dA[0], absolute=self.absolute_rdc[align_index, j])
                            self.d2rdc_theta[pc_index, align_index*5+1, align_index, j] = self.d2rdc_theta[align_index*5+1, pc_index, align_index, j] = rdc_tensor(self.dip_const[j], self.dip_vect[j, c], self.dA[1], absolute=self.absolute_rdc[align_index, j])
                            self.d2rdc_theta[pc_index, align_index*5+2, align_index, j] = self.d2rdc_theta[align_index*5+2, pc_index, align_index, j] = rdc_tensor(self.dip_const[j], self.dip_vect[j, c], self.dA[2], absolute=self.absolute_rdc[align_index, j])
                            self.d2rdc_theta[pc_index, align_index*5+3, align_index, j] = self.d2rdc_theta[align_index*5+3, pc_index, align_index, j] = rdc_tensor(self.dip_const[j], self.dip_vect[j, c], self.dA[3], absolute=self.absolute_rdc[align_index, j])
                            self.d2rdc_theta[pc_index, align_index*5+4, align_index, j] = self.d2rdc_theta[align_index*5+4, pc_index, align_index, j] = rdc_tensor(self.dip_const[j], self.dip_vect[j, c], self.dA[4], absolute=self.absolute_rdc[align_index, j])

                    # Calculate the PCS Hessian component.
                    for j in range(self.num_spins):
                        if self.fixed_tensors[align_index] and self.pcs_flag[align_index] and not self.missing_deltaij[align_index, j]:
                            self.d2deltaij_theta[pc_index, align_index*5+0, align_index, j] = self.d2deltaij_theta[align_index*5+0, pc_index, align_index, j] = pcs_tensor(self.pcs_const[align_index, j, c], self.paramag_unit_vect[j, c], self.dA[0])
                            self.d2deltaij_theta[pc_index, align_index*5+1, align_index, j] = self.d2deltaij_theta[align_index*5+1, pc_index, align_index, j] = pcs_tensor(self.pcs_const[align_index, j, c], self.paramag_unit_vect[j, c], self.dA[1])
                            self.d2deltaij_theta[pc_index, align_index*5+2, align_index, j] = self.d2deltaij_theta[align_index*5+2, pc_index, align_index, j] = pcs_tensor(self.pcs_const[align_index, j, c], self.paramag_unit_vect[j, c], self.dA[2])
                            self.d2deltaij_theta[pc_index, align_index*5+3, align_index, j] = self.d2deltaij_theta[align_index*5+3, pc_index, align_index, j] = pcs_tensor(self.pcs_const[align_index, j, c], self.paramag_unit_vect[j, c], self.dA[3])
                            self.d2deltaij_theta[pc_index, align_index*5+4, align_index, j] = self.d2deltaij_theta[align_index*5+4, pc_index, align_index, j] = pcs_tensor(self.pcs_const[align_index, j, c], self.paramag_unit_vect[j, c], self.dA[4])

            # Construct the paramagnetic centre c partial derivative components for the PCS.
            if not self.centre_fixed:
                raise RelaxError("The Hessian equations for optimising the paramagnetic centre position are not yet implemented.")

            # Construct the chi-squared Hessian element for parameters j and k, alignment i.
            for j in range(self.total_num_params):
                for k in range(self.total_num_params):
                    # RDC part of the chi-squared gradient.
                    if self.rdc_flag[align_index]:
                        self.d2chi2[j, k] = self.d2chi2[j, k] + d2chi2_element(self.rdc[align_index], self.rdc_theta[align_index], self.drdc_theta[j, align_index], self.drdc_theta[k, align_index], self.d2rdc_theta[j, k, align_index], self.rdc_errors[align_index])

                    # PCS part of the chi-squared gradient.
                    if self.pcs_flag[align_index]:
                        self.d2chi2[j, k] = self.d2chi2[j, k] + d2chi2_element(self.deltaij[align_index], self.deltaij_theta[align_index], self.ddeltaij_theta[j, align_index], self.ddeltaij_theta[k, align_index], self.d2deltaij_theta[j, k, align_index], self.pcs_errors[align_index])

        # Diagonal scaling.
        if self.scaling_flag:
            self.d2chi2 = dot(self.d2chi2, self.scaling_matrix)

        # Return a copy of the Hessian.
        return self.d2chi2 * 1.0


    def paramag_info(self):
        """Calculate the paramagnetic centre to spin vectors, distances and constants."""

        # Get the vectors and distances.
        if rank(self.paramag_centre) == 1:
            vectors_single_centre(self.atomic_pos, self.paramag_centre, self.paramag_unit_vect, self.paramag_dist)
        else:
            vectors_centre_per_state(self.atomic_pos, self.paramag_centre, self.paramag_unit_vect, self.paramag_dist)

        # The PCS constants.
        for align_index in range(self.num_align):
            for j in range(self.num_spins):
                for c in range(self.N):
                    self.pcs_const[align_index, j, c] = pcs_constant(self.temp[align_index], self.frq[align_index], self.paramag_dist[j, c])

                    # The PCS constant gradient components.
                    if not self.centre_fixed:
                        pcs_constant_grad(T=self.temp[align_index], Bo=self.frq[align_index], r=self.paramag_dist[j, c], unit_vect=self.paramag_unit_vect[j, c], grad=self.dpcs_const_theta[align_index, j, c])
