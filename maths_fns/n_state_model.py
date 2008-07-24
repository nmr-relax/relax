###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
from copy import deepcopy
from numpy import array, dot, float64, ones, transpose, zeros

# relax module imports.
from alignment_tensor import dAi_dAxx, dAi_dAyy, dAi_dAxy, dAi_dAxz, dAi_dAyz, to_tensor
from chi2 import chi2, dchi2, d2chi2
from rdc import average_rdc_tensor
from rotation_matrix import R_euler_zyz


class N_state_opt:
    """Class containing the target function of the optimisation of the N-state model."""

    def __init__(self, model=None, N=None, init_params=None, full_tensors=None, red_data=None, red_errors=None, full_in_ref_frame=None, rdcs=None, rdc_errors=None, xh_vect=None, dip_const=None, scaling_matrix=None):
        """Set up the class instance for optimisation.

        All constant data required for the N-state model are initialised here.


        @keyword model:         The N-state model type.  This can be one of '2-domain', 'population'
                                or 'fixed'.
        @type model:            str
        @keyword N:             The number of states.
        @type N:                int
        @keyword init_params:   The initial parameter values.  Optimisation must start at some
                                point!
        @type init_params:      numpy float64 array
        @keyword full_tensors:  A list of the full alignment tensors in matrix form.
        @type full_tensors:     list of 3x3 numpy matricies
        @keyword red_data:      An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced
                                tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2, Syy2,
                                Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn]
        @type red_data:         numpy float64 array
        @keyword red_errors:    An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced
                                tensors.  The array format is the same as for red_data.
        @type red_errors:       numpy float64 array
        @keyword rdcs:          The RDC lists.  The first index must correspond to the different
                                alignment media i and the second index to the spin systems j.
        @type rdcs:             numpy matrix
        @keyword rdc_errors:    The RDC error lists.  The dimensions of this argument are the same
                                as for 'rdcs'.
        @type rdc_errors:       numpy matrix
        @keyword xh_vect:       The unit XH vector lists.  The first index must correspond to the
                                spin systems and the second index to each structure (its size being
                                equal to the number of states).
        @type xh_vect:          numpy matrix
        @keyword dip_const:     The dipolar constants for each XH vector.  The indices correspond to
                                the spin systems j.
        @scaling_matrix:        The square and diagonal scaling matrix.
        @scaling_matrix:        numpy rank-2 array
        """

        # Store the data inside the class instance namespace.
        self.N = N
        self.params = 1.0 * init_params    # Force a copy of the data to be stored.
        self.Dij = rdcs
        self.mu = xh_vect
        self.dip_const = dip_const
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
            if red_data == None and not len(red_data):
                raise RelaxError, "The red_data argument " + `red_data` + " must be supplied."
            if red_errors == None and not len(red_errors):
                raise RelaxError, "The red_errors argument " + `red_errors` + " must be supplied."
            if full_in_ref_frame == None and not len(full_in_ref_frame):
                raise RelaxError, "The full_in_ref_frame argument " + `full_in_ref_frame` + " must be supplied."

            # Tensor set up.
            self.full_tensors = array(full_tensors, float64)
            self.num_tensors = len(self.full_tensors)
            self.red_data = red_data
            self.red_errors = red_errors
            self.full_in_ref_frame = full_in_ref_frame

            # Initialise some empty numpy objects for storage of:
            # R:  the transient rotation matricies.
            # RT:  the transposes of the rotation matricies.
            # red_bc:  the back-calculated reduced alignment tensors.
            # red_bc_vector:  the back-calculated reduced alignment tensors in vector form {Sxx, Syy, Sxy, Sxz, Syz}.
            self.R = zeros((self.N,3,3), float64)
            self.RT = zeros((self.N,3,3), float64)
            self.red_bc = zeros((self.num_tensors,3,3), float64)
            self.red_bc_vector = zeros(self.num_tensors*5, float64)

            # Set the target function.
            self.func = self.func_2domain

        # The flexible population N-state model.
        elif model == 'population':
            # Some checks.
            if xh_vect == None and not len(xh_vect):
                raise RelaxError, "The xh_vect argument " + `xh_vect` + " must be supplied."

            # The total number of spins.
            self.num_spins = len(rdcs[0])

            # The total number of alignments.
            self.num_align = len(rdcs)
            self.num_align_params = len(self.rdcs)*5

            # RDC errors.
            if rdc_errors == None:
                # Missing errors.
                self.sigma_ij = ones((self.num_align, self.num_spins)), float64)
            else:
                self.sigma_ij = rdc_errors

            # Alignment tensor function, gradient, and Hessian matrices.
            self.A = zeros((self.num_align, 3, 3), float64)
            self.dA = zeros((self.total_num_params, self.num_align, 3, 3), float64)

            # RDC function, gradient, and Hessian matrices.
            self.Dij_theta = zeros((self.num_align, self.num_spins)), float64)
            self.dDij_theta = zeros((self.total_num_params, self.num_align, self.num_spins)), float64)
            self.d2Dij_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_spins)), float64)

            # Set the target function, gradient, and Hessian.
            self.func = self.func_population
            self.dfunc = self.dfunc_population
            self.d2func = self.d2func_population

            # Parameter specific functions.
            self.setup_population_eqi()


    def func_2domain(self, params):
        """The target function for optimisation of the 2-domain N-state model.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the single chi-squared value
        corresponding to that coordinate in the parameter space.  If no tensor errors are supplied,
        then the SSE (the sum of squares error) value is returned instead.  The chi-squared is
        simply the SSE normalised to unit variance (the SSE divided by the error squared).

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
        for c in xrange(self.N):
            # The rotation matrix.
            R_euler_zyz(self.R[c], params[self.N-1+3*c], params[self.N-1+3*c+1], params[self.N-1+3*c+2])

            # Its transpose.
            self.RT[c] = transpose(self.R[c])

            # The probability of state c.
            if c < self.N-1:
                pc = params[c]

            # The probability of state N (1 minus the pc of all other states).
            else:
                pc = 1.0
                for c2 in xrange(self.N-1):
                    pc = pc - params[c2]

            # Back-calculate the reduced tensors for sum element c and add these to red_bc.
            for i in xrange(self.num_tensors):
                # Normal RT.X.R rotation.
                if self.full_in_ref_frame[i]:
                    self.red_bc[i] = self.red_bc[i]  +  pc * dot(self.RT[c], dot(self.full_tensors[i], self.R[c]))

                # Inverse R.X.RT rotation.
                else:
                    self.red_bc[i] = self.red_bc[i]  +  pc * dot(self.R[c], dot(self.full_tensors[i], self.RT[c]))

        # 5D vectorise the back-calculated tensors (create red_bc_vector from red_bc).
        for i in xrange(self.num_tensors):
            self.red_bc_vector[5*i]   = self.red_bc[i,0,0]    # Sxx.
            self.red_bc_vector[5*i+1] = self.red_bc[i,1,1]    # Syy.
            self.red_bc_vector[5*i+2] = self.red_bc[i,0,1]    # Sxy.
            self.red_bc_vector[5*i+3] = self.red_bc[i,0,2]    # Sxz.
            self.red_bc_vector[5*i+4] = self.red_bc[i,1,2]    # Syz.

        # Return the chi-squared value.
        return chi2(self.red_data, self.red_bc_vector, self.red_errors)


    def func_population(self, params):
        """The target function for optimisation of the flexible population N-state model.

        Description
        ===========

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the single chi-squared value
        corresponding to that coordinate in the parameter space.  If no RDC errors are supplied,
        then the SSE (the sum of squares error) value is returned instead.  The chi-squared is
        simply the SSE normalised to unit variance (the SSE divided by the error squared).


        Indices
        =======

        For this calculation, five indices are looped over and used in the various data structures.
        These include:
            - i, the index over alignments,
            - j, the index over spin systems,
            - c, the index over the N-states (or over the structures),
            - n, the index over the first dimension of the alignment tensor n = {x, y, z},
            - m, the index over the second dimension of the alignment tensor m = {x, y, z}.


        Equations
        =========

        To calculate the function value, a chain of equations are used.  This includes the
        chi-squared equation and the RDC equation.


        The chi-squared equation
        ------------------------

        The equation is::

                         ___
                         \    (Dij - Dij(theta)) ** 2
         chi^2(theta)  =  >   ----------------------- ,
                         /__       sigma_ij ** 2
                          ij

        where:
            - theta is the parameter vector,
            - Dij are the measured RDCs,
            - Dij(theta) are the back calculated RDCs,
            - sigma_ij are the RDC errors.


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
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        The dipolar constant is henceforth defined as::

            dj = 3 / (2pi) d',

        where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is
        associated with the alignment tensor and the pure dipolar constant in SI units is::

                   mu0 gI.gS.h_bar
            d' = - --- ----------- ,
                   4pi    r**3

        where:
            - mu0 is the permeability of free space,
            - gI and gS are the gyromagnetic ratios of the I and S spins,
            - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
            - r is the distance between the two spins.


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

        # Unpack the probabilities (located at the end of the parameter array).
        probs = params[-(self.N-1):]

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # Create tensor i from the parameters.
            to_tensor(self.A[i], params[5*i:5*i + 5])

            # Loop over the spin systems j.
            for j in xrange(self.num_spins):
                # Calculate the average RDC.
                self.rdcs_back_calc[i, j] = average_rdc_tensor(self.xh_vect[j], self.N, self.A[i], weights=probs)

            # Calculate and sum the single alignment chi-squared value.
            chi2_sum = chi2_sum + chi2(self.rdcs[i], self.rdcs_back_calc[i], self.rdc_errors[i])

        # Return the chi-squared value.
        return chi2_sum


    def dfunc_population(self, params):
        """The gradient function for optimisation of the flexible population N-state model.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the chi-squared gradient corresponding
        to that coordinate in the parameter space.  If no RDC errors are supplied, then the SSE (the
        sum of squares error) gradient is returned instead.  The chi-squared gradient is simply the
        SSE gradient normalised to unit variance (the SSE divided by the error squared).

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE gradient.
        @rtype:         numpy rank-1 array
        """

        print "\nGrad call"
        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Initial chi-squared (or SSE) gradient.
        chi2_sum = 0.0

        # Unpack the probabilities (located at the end of the parameter array).
        probs = params[-(self.N-1):]

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # Loop over the gradient.
            for k in xrange(self.total_num_params):
                print "\nParam: " + `k`
                # The alignment tensor gradient.
                if self.calc_dA[k]:
                    self.calc_dA[k](self.dA)
                else:
                    self.dA = self.dA * 0.0

                # The RDC gradient.
                # Loop over spins.
                for j in xrange(self.num_spins):
                    # The RDC index.
                    rdc_index = i*self.num_spins + j
                    print rdc_index

        # Loop over each alignment.
        for n in xrange(self.num_align):
            # Extract tensor n from the parameters.
            tensor_5D = params[5*n:5*n + 5]

            # Loop over the spin systems i.
            for i in xrange(self.num_spins):
                # Calculate the average RDC.
                self.rdcs_back_calc[n, i] = average_rdc_5D(self.xh_vect[i], self.N, tensor_5D, weights=probs)

            # Calculate and sum the single alignment chi-squared value.
            chi2_sum = chi2_sum + chi2(self.rdcs[n], self.rdcs_back_calc[n], self.rdc_errors[n])

        # Diagonal scaling.
        if self.scaling_flag:
            self.dchi2 = dot(self.dchi2, self.scaling_matrix)

        # Return a copy of the gradient.
        return self.dchi2 * 1.0


    def d2func_population(self, params):
        """The Hessian function for optimisation of the flexible population N-state model.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the chi-squared Hessian corresponding
        to that coordinate in the parameter space.  If no RDC errors are supplied, then the SSE (the
        sum of squares error) Hessian is returned instead.  The chi-squared Hessian is simply the
        SSE Hessian normalised to unit variance (the SSE divided by the error squared).

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE Hessian.
        @rtype:         numpy rank-2 array
        """


    def setup_population_eqi(self):
        """Set up all the functions for the population N-state model."""

        # Empty gradient and Hessian data structures.
        self.calc_dA = []
        for i in xrange(self.total_num_params):
            self.calc_dA.append(None)

        # The alignment tensor gradients.
        for i in xrange(self.num_align):
            self.calc_dA[i*5] =   dAi_dAxx
            self.calc_dA[i*5+1] = dAi_dAyy
            self.calc_dA[i*5+2] = dAi_dAxy
            self.calc_dA[i*5+3] = dAi_dAxz
            self.calc_dA[i*5+4] = dAi_dAyz

        for i in xrange(self.total_num_params):
            # Alignment tensor parameter.
            if i < self.num_align_params:
                print "Anm: " + `i`

            # Probability parameter.
            else:
                print "pc: " + `i`

        print self.calc_dA
