###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from Numeric import Float64, matrixmultiply, ones, sum, zeros
from math import pi

from data import Data

from jw_mf_comps import *
from jw_mf import *
from ri_comps import *
from ri_prime import *
from ri import *
from chi2 import *


class Mf:
    def __init__(self, param_set, num_data_sets, equations, param_types, init_params, relax_data, errors, bond_length, csa, diff_type, diff_params, scaling_matrix, num_frq, frq, num_ri, remap_table, noe_r1_table, ri_labels, gx, gh, g_ratio, h_bar, mu0, num_params):
        """The model-free minimisation class.

        This class should be initialised before every calculation.

        Arguments
        ~~~~~~~~~

        equation:  The model-free equation string which should be either 'mf_orig' or 'mf_ext'.

        param_types:  An array of the parameter types used in minimisation.

        relax_data:  An array containing the experimental relaxation values.

        errors:  An array containing the experimental errors.

        bond_length:  The fixed bond length in meters.

        csa:  The fixed CSA value.

        diff_type:  The diffusion tensor string which should be either 'iso', 'axial', or 'aniso'.

        diff_params:  An array with the diffusion parameters.

        scaling_matrix:  A diagonal matrix of scaling factors.
        """

        # Initialise the data class used to store data.
        self.data = Data()

        # Loop over the data sets.
        for i in xrange(num_data_sets):
            # Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
            self.data.frq_list.append(zeros((num_frq[i], 5), Float64))
            for j in xrange(num_frq[i]):
                frqH = 2.0 * pi * frq[i][j]
                frqX = frqH * g_ratio
                self.data.frq_list[i][j, 1] = frqX
                self.data.frq_list[i][j, 2] = frqH - frqX
                self.data.frq_list[i][j, 3] = frqH
                self.data.frq_list[i][j, 4] = frqH + frqX
            self.data.frq_sqrd_list.append(self.data.frq_list[i] ** 2)

        # Store supplied data in self.data
        self.data.param_set = param_set
        self.data.num_data_sets = num_data_sets
        self.data.equations = equations
        self.data.param_types = param_types
        self.data.params = zeros(len(init_params), Float64)
        self.data.total_num_params = len(init_params)
        self.data.func_test = pi * ones(len(init_params), Float64)    # Some random array.
        self.data.grad_test = pi * ones(len(init_params), Float64)    # Some random array.
        self.data.hess_test = pi * ones(len(init_params), Float64)    # Some random array.
        self.data.relax_data = relax_data
        self.data.errors = errors
        self.data.bond_length = bond_length
        self.data.csa = csa
        self.data.diff_type = diff_type
        self.data.diff_params = diff_params
        self.data.gh = gh
        self.data.gx = gx
        self.data.g_ratio = g_ratio
        self.data.h_bar = h_bar
        self.data.mu0 = mu0
        self.data.num_ri = num_ri
        self.data.num_frq = num_frq
        self.data.frq = frq
        self.data.remap_table = remap_table
        self.data.noe_r1_table = noe_r1_table
        self.data.ri_labels = ri_labels
        self.data.scaling_matrix = scaling_matrix
        self.data.num_params = num_params

        # Number of indecies in the generic equations.
        if diff_type == 'iso':
            self.data.num_indecies = 1
        elif diff_type == 'axial':
            self.data.num_indecies = 3
        elif diff_type == 'aniso':
            self.data.num_indecies = 5

        # Initialise the data.
        self.init_data()

        # Scaling initialisation.
        if self.data.scaling_matrix:
            self.scaling_flag = 1
            self.set_params = self.set_params_scaled
        else:
            self.scaling_flag = 0
            self.set_params = self.set_params_unscaled

        # Setup the residue specific equations.
        if not self.setup_equations():
            raise NameError, "The model-free equations could not be setup."

        # Initialise the R1 data class.  This is used only if an NOE data set is collected but the R1 data of the same frequency has not.
        self.init_r1_data()

        # Set the functions self.func, self.dfunc, and self.d2func for minimising model-free parameter for a single residue.
        if param_set == 'mf':
            # Set the index self.data.i to 0.
            self.data.i = 0

            # Alias the functions
            self.func = self.func_mf
            self.dfunc = self.dfunc_mf
            self.d2func = self.d2func_mf

        # Set the functions self.func, self.dfunc, and self.d2func for minimising diffusion tensor parameters.
        if param_set == 'diff':
            self.func = self.func_diff
            self.dfunc = self.dfunc_diff
            self.d2func = self.d2func_diff

        # Set the functions self.func, self.dfunc, and self.d2func for minimising diffusion tensor together with all model-free parameters.
        if param_set == 'all':
            self.func = self.func_all
            self.dfunc = self.dfunc_all
            self.d2func = self.d2func_all


    def func_mf(self, params):
        """The function for calculating the model-free chi-squared value.

        The chi-sqared equation
        ~~~~~~~~~~~~~~~~~~~~~~~
                _n_
                \    (Ri - Ri()) ** 2
        Chi2  =  >   ----------------
                /__    sigma_i ** 2
                i=1

        where:
            Ri are the values of the measured relaxation data set.
            Ri() are the values of the back calculated relaxation data set.
            sigma_i are the values of the error set.
        """

        # Arguments
        self.set_params(params)

        # Test if the function has already been calculated with these parameter values.
        if sum(self.data.params == self.data.func_test) == self.data.total_num_params:
            #if len(self.data.params):
            return self.data.chi2

        # Store the parameter values in self.data.func_test for testing on next call if the function has already been calculated.
        self.data.func_test = self.data.params * 1.0

        # Calculate the spectral density values.
        if self.calc_jw_comps[0]:
            self.calc_jw_comps[0](self.data)
        create_jw_struct(self.data, self.calc_jw[0])

        # Calculate the relaxation formula components.
        self.create_ri_comps[0](self.data, self.create_dip_func[0], self.create_dip_jw_func[0], self.create_csa_func[0], self.create_csa_jw_func[0], self.create_rex_func[0])

        # Calculate the R1, R2, and sigma_noe values.
        self.create_ri_prime[0](self.data)

        # Calculate the R1, R2, and NOE values.
        self.data.ri[0] = self.data.ri_prime[0] * 1.0
        ri(self.data, self.create_ri[0], self.get_r1[0])

        # Calculate the chi-squared value.
        self.data.chi2[0] = chi2(self.data.relax_data[0], self.data.ri[0], self.data.errors[0])

        return self.data.chi2


    def dfunc_mf(self, params):
        """The function for calculating the model-free chi-squared gradient vector.

        The chi-sqared gradient
        ~~~~~~~~~~~~~~~~~~~~~~~
                       _n_
         dChi2         \   /  Ri - Ri()      dRi()  \ 
        -------  =  -2  >  | ----------  .  ------- |
        dthetaj        /__ \ sigma_i**2     dthetaj /
                       i=1

        where:
            Ri are the values of the measured relaxation data set.
            Ri() are the values of the back calculated relaxation data set.
            sigma_i are the values of the error set.
        """

        # Arguments
        self.set_params(params)

        # Test if the gradient has already been calculated with these parameter values.
        if sum(self.data.params == self.data.grad_test) == self.data.total_num_params:
            #if len(self.data.params):
            return self.data.dchi2

        # Test if the function has already been called
        if sum(self.data.params == self.data.func_test) != self.data.total_num_params:
            raise RelaxError, "Should not be here."

        # Store the parameter values in self.data.grad_test for testing on next call if the gradient has already been calculated.
        self.data.grad_test = self.data.params * 1.0

        # Calculate the spectral density gradients.
        if self.calc_djw_comps[0]:
            self.calc_djw_comps[0](self.data)
        create_djw_struct(self.data, self.calc_djw[0])

        # Calculate the relaxation gradient components.
        self.create_dri_comps[0](self.data, self.create_dip_grad[0], self.create_dip_jw_grad[0], self.create_csa_grad[0], self.create_csa_jw_grad[0], self.create_rex_grad[0])

        # Calculate the R1, R2, and sigma_noe gradients.
        for i in xrange(self.data.total_num_params):
            self.create_dri_prime[0][i](self.data, i)

        # Calculate the R1, R2, and NOE gradients.
        self.data.dri[0] = self.data.dri_prime[0] * 1.0
        dri(self.data, self.create_dri[0], self.get_dr1[0])

        # Calculate the chi-squared gradient.
        self.data.dchi2[0] = dchi2(self.data.relax_data[0], self.data.ri[0], self.data.dri[0], self.data.errors[0])

        # Diagonal scaling.
        if self.scaling_flag:
            self.scale_gradient()

        return self.data.dchi2


    def d2func_mf(self, params):
        """The function for calculating the model-free chi-squared Hessian matrix.

        The chi-sqared Hessian
        ~~~~~~~~~~~~~~~~~~~~~~
                             _n_
             d2chi2          \       1      /  dRi()     dRi()                         d2Ri()     \ 
        ---------------  = 2  >  ---------- | ------- . -------  -  (Ri - Ri()) . --------------- |
        dthetaj.dthetak      /__ sigma_i**2 \ dthetaj   dthetak                   dthetaj.dthetak /
                             i=1

        where:
            Ri are the values of the measured relaxation data set.
            Ri() are the values of the back calculated relaxation data set.
            sigma_i are the values of the error set.
        """

        # Arguments
        self.set_params(params)

        # Test if the Hessian has already been calculated with these parameter values.
        if sum(self.data.params == self.data.hess_test) == self.data.total_num_params:
            #if len(self.data.params):
            return self.data.d2chi2

        # Test if the gradient has already been called
        if sum(self.data.params == self.data.grad_test) != self.data.total_num_params:
            raise RelaxError, "Should not be here."

        # Store the parameter values in self.data.hess_test for testing on next call if the Hessian has already been calculated.
        self.data.hess_test = self.data.params * 1.0

        # Calculate the spectral density Hessians.
        create_d2jw_struct(self.data, self.calc_d2jw[0])

        # Calculate the relaxation Hessian components.
        self.create_d2ri_comps[0](self.data, self.create_dip_hess[0], self.create_dip_jw_hess[0], self.create_csa_hess[0], self.create_csa_jw_hess[0], None)

        # Calculate the R1, R2, and sigma_noe Hessians.
        for i in xrange(self.data.total_num_params):
            for j in xrange(i + 1):
                if self.create_d2ri_prime[0][i][j]:
                    self.create_d2ri_prime[0][i][j](self.data, i, j)

                    # Make the Hessian symmetric.
                    if i != j:
                        self.data.d2ri_prime[0][:, j, i] = self.data.d2ri_prime[0][:, i, j]

        # Calculate the R1, R2, and NOE Hessians.
        self.data.d2ri[0] = self.data.d2ri_prime[0] * 1.0
        d2ri(self.data, self.create_d2ri[0], self.get_d2r1[0])

        # Calculate the chi-squared Hessian.
        self.data.d2chi2[0] = d2chi2(self.data.relax_data[0], self.data.ri[0], self.data.dri[0], self.data.d2ri[0], self.data.errors[0])

        # Diagonal scaling.
        if self.scaling_flag:
            self.scale_hessian()

        return self.data.d2chi2


    def init_data(self):
        """Function for initialisation of the data."""

        # Initialise spectral density components.
        self.data.w_tm_sqrd = []
        self.data.fact_tm = []
        #self.data.w_te_tm_sqrd = []
        self.data.te_denom = []
        self.data.two_fifths_tm = []
        self.data.two_fifths_tm_sqrd = []

        # Initialise spectral density values, gradients, and Hessians.
        self.data.jw = []
        self.data.djw = []
        self.data.d2jw = []

        # Initialise the fixed components of the dipolar and CSA constants.
        self.data.csa_const_fixed = []
        self.data.dip_const_fixed = []

        # Initialise the dipolar and CSA constants.
        self.data.dip_const_func = []
        self.data.dip_const_grad = []
        self.data.dip_const_hess = []
        self.data.csa_const_func = []
        self.data.csa_const_grad = []
        self.data.csa_const_hess = []

        # Initialise the components of the transformed relaxation equations.
        self.data.dip_comps_func = []
        self.data.csa_comps_func = []
        self.data.rex_comps_func = []
        self.data.dip_jw_comps_func = []
        self.data.csa_jw_comps_func = []

        # Initialise the first partial derivative components of the transformed relaxation equations.
        self.data.dip_comps_grad = []
        self.data.csa_comps_grad = []
        self.data.rex_comps_grad = []
        self.data.dip_jw_comps_grad = []
        self.data.csa_jw_comps_grad = []

        # Initialise the first partial derivative components of the transformed relaxation equations.
        self.data.dip_comps_hess = []
        self.data.csa_comps_hess = []
        self.data.rex_comps_hess = []
        self.data.dip_jw_comps_hess = []
        self.data.csa_jw_comps_hess = []

        # Initialise the transformed relaxation values, gradients, and Hessians.
        self.data.ri_prime = []
        self.data.dri_prime = []
        self.data.d2ri_prime = []

        # Initialise the data structures containing the R1 values at the position of and corresponding to the NOE.
        self.data.r1 = []
        self.data.dr1 = []
        self.data.d2r1 = []

        # Loop over the data sets.
        for self.data.i in xrange(self.data.num_data_sets):
            # Fixed spectral density components, ie tm is not a parameter.
            if self.data.param_set == 'mf' and 'tm' not in self.data.param_types[self.data.i]:
                self.data.w_tm_sqrd.append(self.data.frq_sqrd_list[self.data.i] * self.data.diff_params[0] ** 2)
                self.data.fact_tm.append(1.0 / (1.0 + self.data.w_tm_sqrd[self.data.i]))
                self.data.two_fifths_tm.append(0.4 * self.data.diff_params[0])
                self.data.two_fifths_tm_sqrd.append(0.4 * self.data.diff_params[0] ** 2)

            # Else empty spectral density components.
            else:
                self.data.w_tm_sqrd.append(zeros((self.data.num_frq[self.data.i], 5), Float64))
                self.data.fact_tm.append(zeros((self.data.num_frq[self.data.i], 5), Float64))
                #self.data.w_te_tm_sqrd.append(zeros((self.data.num_frq[self.data.i], 5), Float64))
                #self.data.te_denom.append(zeros((self.data.num_frq[self.data.i], 5), Float64))


            # Empty spectral density values, gradients, and Hessians.
            self.data.jw.append(zeros((self.data.num_frq[self.data.i], 5), Float64))
            self.data.djw.append(zeros((self.data.num_frq[self.data.i], 5, self.data.num_params[self.data.i]), Float64))
            self.data.d2jw.append(zeros((self.data.num_frq[self.data.i], 5, self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64))

            # Calculate the fixed components of the dipolar and CSA constants.
            self.data.csa_const_fixed.append(zeros(self.data.num_frq[self.data.i], Float64))
            self.data.dip_const_fixed.append(None)
            calc_fixed_csa(self.data)
            calc_fixed_dip(self.data)

            # Dipolar and CSA constants.
            self.data.dip_const_func.append(0.0)
            self.data.dip_const_grad.append(0.0)
            self.data.dip_const_hess.append(0.0)
            self.data.csa_const_func.append(zeros((self.data.num_frq[self.data.i]), Float64))
            self.data.csa_const_grad.append(zeros((self.data.num_frq[self.data.i]), Float64))
            self.data.csa_const_hess.append(zeros((self.data.num_frq[self.data.i]), Float64))

            # Components of the transformed relaxation equations.
            self.data.dip_comps_func.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.csa_comps_func.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.rex_comps_func.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.dip_jw_comps_func.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.csa_jw_comps_func.append(zeros((self.data.num_ri[self.data.i]), Float64))

            # First partial derivative components of the transformed relaxation equations.
            self.data.dip_comps_grad.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.csa_comps_grad.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.rex_comps_grad.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.dip_jw_comps_grad.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64))
            self.data.csa_jw_comps_grad.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64))

            # First partial derivative components of the transformed relaxation equations.
            self.data.dip_comps_hess.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.csa_comps_hess.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.rex_comps_hess.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.dip_jw_comps_hess.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64))
            self.data.csa_jw_comps_hess.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64))

            # Transformed relaxation values, gradients, and Hessians.
            self.data.ri_prime.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.dri_prime.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64))
            self.data.d2ri_prime.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64))

            # Data structures containing the R1 values at the position of and corresponding to the NOE.
            self.data.r1.append(zeros((self.data.num_ri[self.data.i]), Float64))
            self.data.dr1.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64))
            self.data.d2r1.append(zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64))


    def init_r1_data(self):
        """Function for initialisation of the R1 data class.

        This data class is only used if an NOE data set is collected but no R1 data set
        corresponding to the same frequency exists.
        """

        self.data.r1_data = Data()
        self.data.r1_data.num_frq = self.data.num_frq
        self.data.r1_data.dip_const_fixed = self.data.dip_const_fixed
        self.data.r1_data.csa_const_fixed = self.data.csa_const_fixed

        # Loop over the data sets.
        for self.data.i in xrange(self.data.num_data_sets):
            # Components of the transformed relaxation equations.
            self.data.r1_data.dip_comps_func = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.csa_comps_func = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.dip_jw_comps_func = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.csa_jw_comps_func = zeros(self.data.num_ri[self.data.i], Float64)

            # Initialise the first partial derivative components of the transformed relaxation equations.
            self.data.r1_data.dip_comps_grad = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.csa_comps_grad = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.rex_comps_grad = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.dip_jw_comps_grad = zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64)
            self.data.r1_data.csa_jw_comps_grad = zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64)

            # Initialise the first partial derivative components of the transformed relaxation equations.
            self.data.r1_data.dip_comps_hess = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.csa_comps_hess = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.rex_comps_hess = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.dip_jw_comps_hess = zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64)
            self.data.r1_data.csa_jw_comps_hess = zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64)

            # Initialise the transformed relaxation values, gradients, and Hessians.
            self.data.r1_data.ri_prime = zeros(self.data.num_ri[self.data.i], Float64)
            self.data.r1_data.dri_prime = zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i]), Float64)
            self.data.r1_data.d2ri_prime = zeros((self.data.num_ri[self.data.i], self.data.num_params[self.data.i], self.data.num_params[self.data.i]), Float64)

            # Place a few function pointer arrays in the data class for the calculation of the R1 value when an NOE data set exists but the R1 set does not.
            self.data.r1_data.create_dri_prime = self.create_dri_prime
            self.data.r1_data.create_d2ri_prime = self.create_d2ri_prime

            self.data.r1_data.csa_index = self.data.csa_index
            self.data.r1_data.r_index = self.data.r_index
            self.data.r1_data.rex_index = self.data.rex_index


    def lm_dri(self):
        """Return the function used for Levenberg-Marquardt minimisation."""

        # Diagonal scaling.
        if self.scaling_flag:
            return matrixmultiply(self.data.dri, self.data.scaling_matrix)
        else:
            return self.data.dri


    def scale_gradient(self):
        """Function for the diagonal scaling of the chi-squared gradient."""

        self.data.dchi2 = matrixmultiply(self.data.dchi2, self.data.scaling_matrix)


    def scale_hessian(self):
        """Function for the diagonal scaling of the chi-squared Hessian."""

        self.data.d2chi2 = matrixmultiply(self.data.scaling_matrix, matrixmultiply(self.data.d2chi2, self.data.scaling_matrix))


    def set_params_scaled(self, params):
        """Function for setting self.data.params to the parameter vector times the scaling vector."""

        self.data.params = matrixmultiply(params, self.data.scaling_matrix)


    def set_params_unscaled(self, params):
        """Function for setting self.data.params to the parameter vector."""

        self.data.params = params * 1.0


    def setup_equations(self):
        """Setup the equations used to calculate the chi-squared statistic."""

        # Initialisation code.
        ######################

        # Initialise function data structures.
        self.calc_jw, self.calc_djw, self.calc_d2jw = [], [], []
        self.calc_jw_comps, self.calc_djw_comps = [], []

        # Initialise the index data structures.
        self.data.tm_index = []
        self.data.s2_index, self.data.s2f_index, self.data.s2s_index = [], [], []
        self.data.te_index, self.data.tf_index, self.data.ts_index = [], [], []
        self.data.rex_index, self.data.r_index, self.data.csa_index = [], [], []

        # Initialise relaxation equation components.
        self.create_dip_func, self.create_dip_grad, self.create_dip_hess = [], [], []
        self.create_csa_func, self.create_csa_grad, self.create_csa_hess = [], [], []
        self.create_rex_func, self.create_rex_grad = [], []

        self.create_dip_jw_func, self.create_dip_jw_grad, self.create_dip_jw_hess = [], [], []
        self.create_csa_jw_func, self.create_csa_jw_grad, self.create_csa_jw_hess = [], [], []

        # Initialise the Ri' function data structures.
        self.create_ri_prime, self.create_dri_prime, self.create_d2ri_prime = [], [], []

        # Initialise the Ri function data structures.
        self.create_ri, self.create_dri, self.create_d2ri = [], [], []
        self.get_r1, self.get_dr1, self.get_d2r1 = [], [], []

        # Initialise the Ri component data structures.
        self.create_ri_comps, self.create_dri_comps, self.create_d2ri_comps = [], [], []

        # Loop over the data sets.
        for i in xrange(self.data.num_data_sets):
            # Fill function data structures with None or an empty array.
            self.calc_jw.append(None)
            self.calc_djw.append([])
            self.calc_d2jw.append([])
            self.calc_jw_comps.append(None)
            self.calc_djw_comps.append(None)

            # Fill the index data structures with None.
            self.data.tm_index.append(None)
            self.data.s2_index.append(None)
            self.data.s2f_index.append(None)
            self.data.s2s_index.append(None)
            self.data.te_index.append(None)
            self.data.tf_index.append(None)
            self.data.ts_index.append(None)
            self.data.rex_index.append(None)
            self.data.r_index.append(None)
            self.data.csa_index.append(None)

            # Fill the relaxation equation components with empty arrays.
            self.create_dip_func.append([])
            self.create_dip_grad.append([])
            self.create_dip_hess.append([])

            self.create_csa_func.append([])
            self.create_csa_grad.append([])
            self.create_csa_hess.append([])

            self.create_rex_func.append([])
            self.create_rex_grad.append([])

            self.create_dip_jw_func.append([])
            self.create_dip_jw_grad.append([])
            self.create_dip_jw_hess.append([])

            self.create_csa_jw_func.append([])
            self.create_csa_jw_grad.append([])
            self.create_csa_jw_hess.append([])

            # Fill the Ri' function data structures with empty arrays and None.
            self.create_ri_prime.append(None)
            self.create_dri_prime.append([])
            self.create_d2ri_prime.append([])

            # Fill the Ri function data structures with empty arrays.
            self.create_ri.append([])
            self.create_dri.append([])
            self.create_d2ri.append([])
            self.get_r1.append([])
            self.get_dr1.append([])
            self.get_d2r1.append([])

            # Fill the Ri function data structures with empty arrays.
            self.create_ri.append([])
            self.create_dri.append([])
            self.create_d2ri.append([])

            # Fill the Ri component data structures with empty arrays.
            self.create_ri_comps.append([])
            self.create_dri_comps.append([])
            self.create_d2ri_comps.append([])

            # Fill the relaxation data data structures with None.
            for j in xrange(self.data.num_ri[i]):
                self.create_dip_func[i].append(None)
                self.create_dip_grad[i].append(None)
                self.create_dip_hess[i].append(None)
                self.create_csa_func[i].append(None)
                self.create_csa_grad[i].append(None)
                self.create_csa_hess[i].append(None)
                self.create_rex_func[i].append(None)
                self.create_rex_grad[i].append(None)
                self.create_dip_jw_func[i].append(None)
                self.create_dip_jw_grad[i].append(None)
                self.create_dip_jw_hess[i].append(None)
                self.create_csa_jw_func[i].append(None)
                self.create_csa_jw_grad[i].append(None)
                self.create_csa_jw_hess[i].append(None)
                self.create_ri[i].append(None)
                self.create_dri[i].append(None)
                self.create_d2ri[i].append(None)
                self.get_r1[i].append(None)
                self.get_dr1[i].append(None)
                self.get_d2r1[i].append(None)

        # Loop over the data sets.
        for i in xrange(self.data.num_data_sets):
            # Set self.data.i to i.
            self.data.i = i

            # Set up the spectral density functions.
            ########################################

            # Create empty spectral density gradient and Hessian function data structures.
            for j in xrange(self.data.num_params[i]):
                self.calc_djw[i].append(None)
                self.calc_d2jw[i].append([])
                for k in xrange(self.data.num_params[i]):
                    self.calc_d2jw[i][j].append(None)


            # The original model-free equations {tm, S2, te, Rex, r, CSA}.
            ##############################################################

            if self.data.equations[i] == 'mf_orig':
                # Find the indecies of the model-free parameters.
                for j in xrange(self.data.num_params[i]):
                    if self.data.param_types[i][j] == 'tm':
                        self.data.tm_index[i] = j
                    elif self.data.param_types[i][j] == 'S2':
                        self.data.s2_index[i] = j
                    elif self.data.param_types[i][j] == 'te':
                        self.data.te_index[i] = j
                    elif self.data.param_types[i][j] == 'Rex':
                        self.data.rex_index[i] = j
                    elif self.data.param_types[i][j] == 'r':
                        self.data.r_index[i] = j
                    elif self.data.param_types[i][j] == 'CSA':
                        self.data.csa_index[i] = j
                    else:
                        print "Unknown parameter."
                        return 0

                # No spectral density parameters {}.
                if self.data.tm_index[i] == None and self.data.s2_index[i] == None and self.data.te_index[i] == None:
                    # Equation.
                    self.calc_jw_comps[i] = None
                    self.calc_jw[i] = calc_jw

                    # Gradient.
                    self.calc_djw_comps[i] = None

                # Spectral density parameters {S2}.
                elif self.data.tm_index[i] == None and self.data.s2_index[i] != None and self.data.te_index[i] == None:
                    # Equation.
                    self.calc_jw_comps[i] = None
                    self.calc_jw[i] = calc_S2_jw

                    # Gradient.
                    self.calc_djw_comps[i] = None
                    self.calc_djw[i][self.data.s2_index[i]] = calc_S2_djw_dS2

                # Spectral density parameters {S2, te}.
                elif self.data.tm_index[i] == None and self.data.s2_index[i] != None and self.data.te_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_S2_te_jw_comps
                    self.calc_jw[i] = calc_S2_te_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_S2_te_djw_comps
                    self.calc_djw[i][self.data.s2_index[i]] = calc_S2_te_djw_dS2
                    self.calc_djw[i][self.data.te_index[i]] = calc_S2_te_djw_dte

                    # Hessian.
                    self.calc_d2jw[i][self.data.s2_index[i]][self.data.te_index[i]] = self.calc_d2jw[i][self.data.te_index[i]][self.data.s2_index[i]] = calc_S2_te_d2jw_dS2dte
                    self.calc_d2jw[i][self.data.te_index[i]][self.data.te_index[i]] = calc_S2_te_d2jw_dte2

                # Spectral density parameters {tm}.
                elif self.data.tm_index[i] != None and self.data.s2_index[i] == None and self.data.te_index[i] == None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_jw_comps
                    self.calc_jw[i] = calc_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_djw_comps
                    self.calc_djw[i][self.data.tm_index[i]] = calc_tm_djw_dtm

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_d2jw_dtm2

                # Spectral density parameters {tm, S2}.
                elif self.data.tm_index[i] != None and self.data.s2_index[i] != None and self.data.te_index[i] == None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_jw_comps
                    self.calc_jw[i] = calc_S2_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_djw_comps
                    self.calc_djw[i][self.data.tm_index[i]] = calc_tm_S2_djw_dtm
                    self.calc_djw[i][self.data.s2_index[i]] = calc_S2_djw_dS2

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_S2_d2jw_dtm2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2_index[i]] = self.calc_d2jw[i][self.data.s2_index[i]][self.data.tm_index[i]] = calc_tm_S2_d2jw_dtmdS2

                # Spectral density parameters {tm, S2, te}.
                elif self.data.tm_index[i] != None and self.data.s2_index[i] != None and self.data.te_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_S2_te_jw_comps
                    self.calc_jw[i] = calc_S2_te_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_S2_te_djw_comps
                    self.calc_djw[i][self.data.tm_index[i]] = calc_tm_S2_te_djw_dtm
                    self.calc_djw[i][self.data.s2_index[i]] = calc_S2_te_djw_dS2
                    self.calc_djw[i][self.data.te_index[i]] = calc_tm_S2_te_djw_dte

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_S2_te_d2jw_dtm2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2_index[i]] = self.calc_d2jw[i][self.data.s2_index[i]][self.data.tm_index[i]] = calc_tm_S2_te_d2jw_dtmdS2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.te_index[i]] = self.calc_d2jw[i][self.data.te_index[i]][self.data.tm_index[i]] = calc_tm_S2_te_d2jw_dtmdte
                    self.calc_d2jw[i][self.data.s2_index[i]][self.data.te_index[i]] = self.calc_d2jw[i][self.data.te_index[i]][self.data.s2_index[i]] = calc_tm_S2_te_d2jw_dS2dte
                    self.calc_d2jw[i][self.data.te_index[i]][self.data.te_index[i]] = calc_tm_S2_te_d2jw_dte2

                # Bad parameter combination.
                else:
                    print "Invalid combination of parameters for the extended model-free equation."
                    return 0


            # The extended model-free equations {tm, S2f, tf, S2, ts, Rex, r, CSA}.
            #######################################################################

            elif self.data.equations[i] == 'mf_ext':
                # Find the indecies of the model-free parameters.
                for j in xrange(self.data.num_params[i]):
                    if self.data.param_types[i][j] == 'tm':
                        self.data.tm_index[i] = j
                    elif self.data.param_types[i][j] == 'S2f':
                        self.data.s2f_index[i] = j
                    elif self.data.param_types[i][j] == 'tf':
                        self.data.tf_index[i] = j
                    elif self.data.param_types[i][j] == 'S2':
                        self.data.s2_index[i] = j
                    elif self.data.param_types[i][j] == 'ts':
                        self.data.ts_index[i] = j
                    elif self.data.param_types[i][j] == 'Rex':
                        self.data.rex_index[i] = j
                    elif self.data.param_types[i][j] == 'r':
                        self.data.r_index[i] = j
                    elif self.data.param_types[i][j] == 'CSA':
                        self.data.csa_index[i] = j
                    else:
                        print "Unknown parameter."
                        return 0

                # Spectral density parameters {S2f, S2, ts}.
                if self.data.tm_index[i] == None and self.data.s2f_index[i] != None and self.data.tf_index[i] == None and self.data.s2_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_S2f_S2_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_S2_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_S2f_S2_ts_djw_comps
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_S2f_S2_ts_djw_dS2f
                    self.calc_djw[i][self.data.s2_index[i]] = calc_S2f_S2_ts_djw_dS2
                    self.calc_djw[i][self.data.ts_index[i]] = calc_S2f_S2_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_S2f_S2_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2_index[i]] = calc_S2f_S2_ts_d2jw_dS2dts
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_S2f_S2_ts_d2jw_dts2

                # Spectral density parameters {S2f, tf, S2, ts}.
                elif self.data.tm_index[i] == None and self.data.s2f_index[i] != None and self.data.tf_index[i] != None and self.data.s2_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_S2f_tf_S2_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_tf_S2_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_S2f_tf_S2_ts_djw_comps
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_S2f_tf_S2_ts_djw_dS2f
                    self.calc_djw[i][self.data.tf_index[i]] = calc_S2f_tf_S2_ts_djw_dtf
                    self.calc_djw[i][self.data.s2_index[i]] = calc_S2f_S2_ts_djw_dS2
                    self.calc_djw[i][self.data.ts_index[i]] = calc_S2f_S2_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tf_index[i]] = self.calc_d2jw[i][self.data.tf_index[i]][self.data.s2f_index[i]] = calc_S2f_tf_S2_ts_d2jw_dS2fdtf
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_S2f_S2_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2_index[i]] = calc_S2f_S2_ts_d2jw_dS2dts
                    self.calc_d2jw[i][self.data.tf_index[i]][self.data.tf_index[i]] = calc_S2f_tf_S2_ts_d2jw_dtf2
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_S2f_S2_ts_d2jw_dts2

                # Spectral density parameters {tm, S2f, S2, ts}.
                elif self.data.tm_index[i] != None and self.data.s2f_index[i] != None and self.data.tf_index[i] == None and self.data.s2_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_S2f_S2_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_S2_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_S2f_S2_ts_djw_comps
                    self.calc_djw[i][self.data.tm_index] = calc_tm_S2f_S2_ts_djw_dtm
                    self.calc_djw[i][self.data.s2f_index] = calc_tm_S2f_S2_ts_djw_dS2f
                    self.calc_djw[i][self.data.s2_index] = calc_tm_S2f_S2_ts_djw_dS2
                    self.calc_djw[i][self.data.ts_index] = calc_tm_S2f_S2_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2_ts_d2jw_dtm2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2f_index[i]] = self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2_ts_d2jw_dtmdS2f
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2_index[i]] = self.calc_d2jw[i][self.data.s2_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2_ts_d2jw_dtmdS2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2_ts_d2jw_dtmdts
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_tm_S2f_S2_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2_index[i]] = calc_tm_S2f_S2_ts_d2jw_dS2dts
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_tm_S2f_S2_ts_d2jw_dts2

                # Spectral density parameters {tm, S2f, tf, S2, ts}.
                elif self.data.tm_index[i] != None and self.data.s2f_index[i] != None and self.data.tf_index[i] != None and self.data.s2_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_S2f_tf_S2_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_tf_S2_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_S2f_tf_S2_ts_djw_comps
                    self.calc_djw[i][self.data.tm_index[i]] = calc_tm_S2f_tf_S2_ts_djw_dtm
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_tm_S2f_tf_S2_ts_djw_dS2f
                    self.calc_djw[i][self.data.tf_index[i]] = calc_tm_S2f_tf_S2_ts_djw_dtf
                    self.calc_djw[i][self.data.s2_index[i]] = calc_tm_S2f_tf_S2_ts_djw_dS2
                    self.calc_djw[i][self.data.ts_index[i]] = calc_tm_S2f_tf_S2_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dtm2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2f_index[i]] = self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdS2f
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2_index[i]] = self.calc_d2jw[i][self.data.s2_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdS2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tf_index[i]] = self.calc_d2jw[i][self.data.tf_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdtf
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdts
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tf_index[i]] = self.calc_d2jw[i][self.data.tf_index[i]][self.data.s2f_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dS2fdtf
                    self.calc_d2jw[i][self.data.s2f_index[i][i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dS2dts
                    self.calc_d2jw[i][self.data.tf_index[i]][self.data.tf_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dtf2
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_tm_S2f_tf_S2_ts_d2jw_dts2

                # Bad parameter combination.
                else:
                    print "Invalid combination of parameters for the extended model-free equation."
                    return 0


            # The extended 2 model-free equations {tm, S2f, tf, S2s, ts, Rex, r, CSA}.
            #########################################################################

            elif self.data.equations[i] == 'mf_ext2':
                # Find the indecies of the model-free parameters.
                for j in xrange(self.data.num_params[i]):
                    if self.data.param_types[i][j] == 'tm':
                        self.data.tm_index[i] = j
                    elif self.data.param_types[i][j] == 'S2f':
                        self.data.s2f_index[i] = j
                    elif self.data.param_types[i][j] == 'tf':
                        self.data.tf_index[i] = j
                    elif self.data.param_types[i][j] == 'S2s':
                        self.data.s2s_index[i] = j
                    elif self.data.param_types[i][j] == 'ts':
                        self.data.ts_index[i] = j
                    elif self.data.param_types[i][j] == 'Rex':
                        self.data.rex_index[i] = j
                    elif self.data.param_types[i][j] == 'r':
                        self.data.r_index[i] = j
                    elif self.data.param_types[i][j] == 'CSA':
                        self.data.csa_index[i] = j
                    else:
                        print "Unknown parameter."
                        return 0

                # Spectral density parameters {S2f, S2s, ts}.
                if self.data.tm_index[i] == None and self.data.s2f_index[i] != None and self.data.tf_index[i] == None and self.data.s2s_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_S2f_S2s_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_S2s_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_S2f_S2s_ts_djw_comps
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_S2f_S2s_ts_djw_dS2f
                    self.calc_djw[i][self.data.s2s_index[i]] = calc_S2f_S2s_ts_djw_dS2s
                    self.calc_djw[i][self.data.ts_index[i]] = calc_S2f_S2s_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_S2f_S2s_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2s_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2s_index[i]] = calc_S2f_S2s_ts_d2jw_dS2sdts
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_S2f_S2s_ts_d2jw_dts2

                # Spectral density parameters {S2f, tf, S2s, ts}.
                elif self.data.tm_index[i] == None and self.data.s2f_index[i] != None and self.data.tf_index[i] != None and self.data.s2s_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_S2f_tf_S2s_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_tf_S2s_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_S2f_tf_S2s_ts_djw_comps
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_S2f_tf_S2s_ts_djw_dS2f
                    self.calc_djw[i][self.data.tf_index[i]] = calc_S2f_tf_S2s_ts_djw_dtf
                    self.calc_djw[i][self.data.s2s_index[i]] = calc_S2f_tf_S2s_ts_djw_dS2s
                    self.calc_djw[i][self.data.ts_index[i]] = calc_S2f_tf_S2s_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tf_index[i]] = self.calc_d2jw[i][self.data.tf_index[i]][self.data.s2f_index[i]] = calc_S2f_tf_S2s_ts_d2jw_dS2fdtf
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_S2f_tf_S2s_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2s_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2s_index[i]] = calc_S2f_tf_S2s_ts_d2jw_dS2sdts
                    self.calc_d2jw[i][self.data.tf_index[i]][self.data.tf_index[i]] = calc_S2f_tf_S2s_ts_d2jw_dtf2
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_S2f_tf_S2s_ts_d2jw_dts2

                # Spectral density parameters {tm, S2f, S2s, ts}.
                elif self.data.tm_index[i] != None and self.data.s2f_index[i] != None and self.data.tf_index[i] == None and self.data.s2s_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_S2f_S2s_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_S2s_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_S2f_S2s_ts_djw_comps
                    self.calc_djw[i][self.data.tm_index[i]] = calc_tm_S2f_S2s_ts_djw_dtm
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_tm_S2f_S2s_ts_djw_dS2f
                    self.calc_djw[i][self.data.s2s_index[i]] = calc_tm_S2f_S2s_ts_djw_dS2s
                    self.calc_djw[i][self.data.ts_index[i]] = calc_tm_S2f_S2s_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dtm2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2f_index[i]] = self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dtmdS2f
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2s_index[i]] = self.calc_d2jw[i][self.data.s2s_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dtmdS2s
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.tm_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dtmdts
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2s_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2s_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dS2sdts
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_tm_S2f_S2s_ts_d2jw_dts2

                # Spectral density parameters {tm, S2f, tf, S2s, ts}.
                elif self.data.tm_index[i] != None and self.data.s2f_index[i] != None and self.data.tf_index[i] != None and self.data.s2s_index[i] != None and self.data.ts_index[i] != None:
                    # Equation.
                    self.calc_jw_comps[i] = calc_tm_S2f_tf_S2s_ts_jw_comps
                    self.calc_jw[i] = calc_S2f_tf_S2s_ts_jw

                    # Gradient.
                    self.calc_djw_comps[i] = calc_tm_S2f_tf_S2s_ts_djw_comps
                    self.calc_djw[i][self.data.tm_index[i]] = calc_tm_S2f_tf_S2s_ts_djw_dtm
                    self.calc_djw[i][self.data.s2f_index[i]] = calc_tm_S2f_tf_S2s_ts_djw_dS2f
                    self.calc_djw[i][self.data.tf_index[i]] = calc_tm_S2f_tf_S2s_ts_djw_dtf
                    self.calc_djw[i][self.data.s2s_index[i]] = calc_tm_S2f_tf_S2s_ts_djw_dS2s
                    self.calc_djw[i][self.data.ts_index[i]] = calc_tm_S2f_tf_S2s_ts_djw_dts

                    # Hessian.
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dtm2
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2f_index[i]] = self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdS2f
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.s2s_index[i]] = self.calc_d2jw[i][self.data.s2s_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdS2s
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.tf_index[i]] = self.calc_d2jw[i][self.data.tf_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdtf
                    self.calc_d2jw[i][self.data.tm_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.tm_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdts
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.tf_index[i]] = self.calc_d2jw[i][self.data.tf_index[i]][self.data.s2f_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2fdtf
                    self.calc_d2jw[i][self.data.s2f_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2f_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2fdts
                    self.calc_d2jw[i][self.data.s2s_index[i]][self.data.ts_index[i]] = self.calc_d2jw[i][self.data.ts_index[i]][self.data.s2s_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2sdts
                    self.calc_d2jw[i][self.data.tf_index[i]][self.data.tf_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dtf2
                    self.calc_d2jw[i][self.data.ts_index[i]][self.data.ts_index[i]] = calc_tm_S2f_tf_S2s_ts_d2jw_dts2

                # Bad parameter combination.
                else:
                    print "Invalid combination of parameters for the extended model-free equation."
                    return 0

            # Unknown model-free equation.
            else:
                print "Unknown model-free equation."
                return 0


            # Select the functions for the calculation of ri_prime, dri_prime, and d2ri_prime components.
            #############################################################################################

            for j in xrange(self.data.num_ri[i]):
                # The R1 equations.
                if self.data.ri_labels[i][j] == 'R1':
                    self.create_csa_func[i][j] = comp_r1_csa_const
                    self.create_csa_grad[i][j] = comp_r1_csa_const
                    self.create_csa_hess[i][j] = comp_r1_csa_const
                    self.create_dip_jw_func[i][j] = comp_r1_dip_jw
                    self.create_dip_jw_grad[i][j] = comp_r1_dip_jw
                    self.create_dip_jw_hess[i][j] = comp_r1_dip_jw
                    self.create_csa_jw_func[i][j] = comp_r1_csa_jw
                    self.create_csa_jw_grad[i][j] = comp_r1_csa_jw
                    self.create_csa_jw_hess[i][j] = comp_r1_csa_jw

                # The R2 equations.
                elif self.data.ri_labels[i][j] == 'R2':
                    self.create_dip_func[i][j] = comp_r2_dip_const
                    self.create_dip_grad[i][j] = comp_r2_dip_const
                    self.create_dip_hess[i][j] = comp_r2_dip_const
                    self.create_csa_func[i][j] = comp_r2_csa_const
                    self.create_csa_grad[i][j] = comp_r2_csa_const
                    self.create_csa_hess[i][j] = comp_r2_csa_const
                    self.create_rex_func[i][j] = comp_rex_const_func
                    self.create_rex_grad[i][j] = comp_rex_const_grad
                    self.create_dip_jw_func[i][j] = comp_r2_dip_jw
                    self.create_dip_jw_grad[i][j] = comp_r2_dip_jw
                    self.create_dip_jw_hess[i][j] = comp_r2_dip_jw
                    self.create_csa_jw_func[i][j] = comp_r2_csa_jw
                    self.create_csa_jw_grad[i][j] = comp_r2_csa_jw
                    self.create_csa_jw_hess[i][j] = comp_r2_csa_jw

                # The NOE equations.
                elif self.data.ri_labels[i][j] == 'NOE':
                    self.create_dip_jw_func[i][j] = comp_sigma_noe_dip_jw
                    self.create_dip_jw_grad[i][j] = comp_sigma_noe_dip_jw
                    self.create_dip_jw_hess[i][j] = comp_sigma_noe_dip_jw
                    self.create_ri[i][j] = calc_noe
                    self.create_dri[i][j] = calc_dnoe
                    self.create_d2ri[i][j] = calc_d2noe
                    if self.data.noe_r1_table[i][j] == None:
                        self.get_r1[i][j] = calc_r1
                        self.get_dr1[i][j] = calc_dr1
                        self.get_d2r1[i][j] = calc_d2r1
                    else:
                        self.get_r1[i][j] = extract_r1
                        self.get_dr1[i][j] = extract_dr1
                        self.get_d2r1[i][j] = extract_d2r1


            # Select the functions for the calculation of ri_prime, dri_prime, and d2ri_prime.
            ##################################################################################

            # ri_prime.
            if self.data.rex_index[i] == None:
                self.create_ri_prime[i] = func_ri_prime
            else:
                self.create_ri_prime[i] = func_ri_prime_rex

            # dri_prime and d2ri_prime.
            for j in xrange(self.data.num_params[i]):
                if self.data.param_types[i][j] == 'Rex':
                    self.create_dri_prime[i].append(func_dri_drex_prime)
                    self.create_d2ri_prime[i].append([])
                    for k in xrange(self.data.num_params[i]):
                        if self.data.param_types[i][k] == 'Rex':
                            self.create_d2ri_prime[i][j].append(None)
                        elif self.data.param_types[i][k] == 'r':
                            self.create_d2ri_prime[i][j].append(None)
                        elif self.data.param_types[i][k] == 'CSA':
                            self.create_d2ri_prime[i][j].append(None)
                        else:
                            self.create_d2ri_prime[i][j].append(None)
                elif self.data.param_types[i][j] == 'r':
                    self.create_dri_prime[i].append(func_dri_dr_prime)
                    self.create_d2ri_prime[i].append([])
                    for k in xrange(self.data.num_params[i]):
                        if self.data.param_types[i][k] == 'Rex':
                            self.create_d2ri_prime[i][j].append(None)
                        elif self.data.param_types[i][k] == 'r':
                            self.create_d2ri_prime[i][j].append(func_d2ri_dr2_prime)
                        elif self.data.param_types[i][k] == 'CSA':
                            self.create_d2ri_prime[i][j].append(None)
                        else:
                            self.create_d2ri_prime[i][j].append(func_d2ri_drdjw_prime)
                elif self.data.param_types[i][j] == 'CSA':
                    self.create_dri_prime[i].append(func_dri_dcsa_prime)
                    self.create_d2ri_prime[i].append([])
                    for k in xrange(self.data.num_params[i]):
                        if self.data.param_types[i][k] == 'Rex':
                            self.create_d2ri_prime[i][j].append(None)
                        elif self.data.param_types[i][k] == 'r':
                            self.create_d2ri_prime[i][j].append(None)
                        elif self.data.param_types[i][k] == 'CSA':
                            self.create_d2ri_prime[i][j].append(func_d2ri_dcsa2_prime)
                        else:
                            self.create_d2ri_prime[i][j].append(func_d2ri_dcsadjw_prime)
                else:
                    self.create_dri_prime[i].append(func_dri_djw_prime)
                    self.create_d2ri_prime[i].append([])
                    for k in xrange(self.data.num_params[i]):
                        if self.data.param_types[i][k] == 'Rex':
                            self.create_d2ri_prime[i][j].append(None)
                        elif self.data.param_types[i][k] == 'r':
                            self.create_d2ri_prime[i][j].append(func_d2ri_djwdr_prime)
                        elif self.data.param_types[i][k] == 'CSA':
                            self.create_d2ri_prime[i][j].append(func_d2ri_djwdcsa_prime)
                        else:
                            self.create_d2ri_prime[i][j].append(func_d2ri_djwidjwj_prime)


            # Both the bond length and CSA are fixed {}.
            ############################################

            if self.data.r_index[i] == None and self.data.csa_index[i] == None:
                # The main ri component functions
                if self.data.rex_index[i] == None:
                    self.create_ri_comps[i] = ri_comps
                    self.create_dri_comps[i] = dri_comps
                    self.create_d2ri_comps[i] = d2ri_comps
                else:
                    self.create_ri_comps[i] = ri_comps_rex
                    self.create_dri_comps[i] = dri_comps_rex
                    self.create_d2ri_comps[i] = d2ri_comps

                # Calculate the dipolar and CSA constant components.
                comp_dip_const_func(self.data, self.data.bond_length[i])
                comp_csa_const_func(self.data, self.data.csa[i])
                for j in xrange(self.data.num_ri[i]):
                    self.data.dip_comps_func[i][j] = self.data.dip_const_func[i]
                    if self.create_dip_func[i][j]:
                        self.data.dip_comps_func[i][j] = self.create_dip_func[i][j](self.data.dip_const_func[i])
                    if self.create_csa_func[i][j]:
                        self.data.csa_comps_func[i][j] = self.create_csa_func[i][j](self.data.csa_const_func[i][self.data.remap_table[i][j]])


            # The bond length is a parameter {r}.
            #####################################

            elif self.data.r_index[i] != None and self.data.csa_index[i] == None:
                # The main ri component functions
                if self.data.rex_index[i] == None:
                    self.create_ri_comps[i] = ri_comps_r
                    self.create_dri_comps[i] = dri_comps_r
                    self.create_d2ri_comps[i] = d2ri_comps_r
                else:
                    self.create_ri_comps[i] = ri_comps_r_rex
                    self.create_dri_comps[i] = dri_comps_r_rex
                    self.create_d2ri_comps[i] = d2ri_comps_r

                # Calculate the CSA constant.
                comp_csa_const_func(self.data, self.data.csa[i])
                for j in xrange(self.data.num_ri[i]):
                    if self.create_csa_func[i][j]:
                        self.data.csa_comps_func[i][j] = self.create_csa_func[i][j](self.data.csa_const_func[i][self.data.remap_table[i][j]])


            # The CSA is a parameter {CSA}.
            ###############################

            elif self.data.r_index[i] == None and self.data.csa_index[i] != None:
                # The main ri component functions
                if self.data.rex_index[i] == None:
                    self.create_ri_comps[i] = ri_comps_csa
                    self.create_dri_comps[i] = dri_comps_csa
                    self.create_d2ri_comps[i] = d2ri_comps_csa
                else:
                    self.create_ri_comps[i] = ri_comps_csa_rex
                    self.create_dri_comps[i] = dri_comps_csa_rex
                    self.create_d2ri_comps[i] = d2ri_comps_csa

                # Calculate the dipolar constant.
                comp_dip_const_func(self.data, self.data.bond_length[i])
                for j in xrange(self.data.num_ri[i]):
                    self.data.dip_comps_func[i][j] = self.data.dip_const_func[i]
                    if self.create_dip_func[i][j]:
                        self.data.dip_comps_func[i][j] = self.create_dip_func[i][j](self.data.dip_const_func[i])


            # Both the bond length and CSA are parameters {r, CSA}.
            #######################################################

            elif self.data.r_index[i] != None and self.data.csa_index[i] != None:
                # The main ri component functions
                if self.data.rex_index[i] == None:
                    self.create_ri_comps[i] = ri_comps_r_csa
                    self.create_dri_comps[i] = dri_comps_r_csa
                    self.create_d2ri_comps[i] = d2ri_comps_r_csa
                else:
                    self.create_ri_comps[i] = ri_comps_r_csa_rex
                    self.create_dri_comps[i] = dri_comps_r_csa_rex
                    self.create_d2ri_comps[i] = d2ri_comps_r_csa


            # Invalid combination of parameters.
            ####################################

            else:
                print "Invalid combination of parameters for the model-free equations."
                return 0

            return 1
