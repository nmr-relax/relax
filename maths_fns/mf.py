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

from geometry import *
from weights import *
from correlation_time import *
from jw_mf_comps import *
from jw_mf import *
from ri_comps import *
from ri_prime import *
from ri import *
from chi2 import *


class Mf:
    def __init__(self, total_num_params=0, param_set=None, diff_type=None, diff_params=None, scaling_matrix=None, num_res=None, equations=None, param_types=None, relax_data=None, errors=None, bond_length=None, csa=None, num_frq=0, frq=None, num_ri=None, remap_table=None, noe_r1_table=None, ri_labels=None, gx=0, gh=0, g_ratio=0, h_bar=0, mu0=0, num_params=0, vectors=None):
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

        # Arguments.
        self.params = zeros(total_num_params, Float64)
        self.param_set = param_set
        self.total_num_params = total_num_params
        self.scaling_matrix = scaling_matrix
        self.num_res = num_res

        # Data structures for tests set to some random array (in this case all pi).
        self.func_test = pi * ones(total_num_params, Float64)
        self.grad_test = pi * ones(total_num_params, Float64)
        self.hess_test = pi * ones(total_num_params, Float64)

        # Initialise the data class for storing diffusion tensor data.
        self.diff_data = Data()
        self.diff_data.type = diff_type
        self.diff_data.params = diff_params
        self.init_diff_data(self.diff_data)

        # Create the data array used to store data.
        self.data = []
        for i in xrange(self.num_res):
            # Append the class instance Data to the data array.
            self.data.append(Data())

            # Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
            self.data[i].frq_list = zeros((num_frq[i], 5), Float64)
            for j in xrange(num_frq[i]):
                frqH = 2.0 * pi * frq[i][j]
                frqX = frqH / g_ratio
                self.data[i].frq_list[j, 1] = frqX
                self.data[i].frq_list[j, 2] = frqH - frqX
                self.data[i].frq_list[j, 3] = frqH
                self.data[i].frq_list[j, 4] = frqH + frqX
            self.data[i].frq_sqrd_list = self.data[i].frq_list ** 2

            # Store supplied data in self.data
            self.data[i].gh = gh
            self.data[i].gx = gx
            self.data[i].g_ratio = g_ratio
            self.data[i].h_bar = h_bar
            self.data[i].mu0 = mu0
            self.data[i].equations = equations[i]
            self.data[i].param_types = param_types[i]
            self.data[i].relax_data = relax_data[i]
            self.data[i].errors = errors[i]
            self.data[i].bond_length = bond_length[i]
            self.data[i].csa = csa[i]
            self.data[i].num_ri = num_ri[i]
            self.data[i].num_frq = num_frq[i]
            self.data[i].frq = frq[i]
            self.data[i].remap_table = remap_table[i]
            self.data[i].noe_r1_table = noe_r1_table[i]
            self.data[i].ri_labels = ri_labels[i]
            self.data[i].num_params = num_params[i]
            self.data[i].xh_unit_vector = vectors[i]

            # Initialise the residue specific data.
            self.init_res_data(self.data[i], self.diff_data)

            # Setup the residue specific equations.
            if not self.setup_equations(self.data[i]):
                raise RelaxError, "The model-free equations could not be setup."

            # Calculate the correlation times ti.
            self.diff_data.calc_ti(self.data[i], self.diff_data)

            # Print out the contents of self.data[i].
            if 0:
                print "Contents of self.data[i]."
                for name in dir(self.data[i]):
                    print name + ": " + `type(getattr(self.data[i], name))`
                    #print name + ": " + `getattr(self.data[i], name)`

            # Fixed spectral density components, ie tm is not a parameter.
            if self.param_set == 'mf' and 'tm' not in self.data[i].param_types:
                # Loop over the indecies of the generic model-free equations.
                for j in xrange(self.diff_data.num_indecies):
                    self.data[i].w_ti_sqrd[:, :, j] = self.data[i].frq_sqrd_list * self.data[i].ti[j] ** 2
                    self.data[i].fact_ti[:, :, j] = 1.0 / (1.0 + self.data[i].w_ti_sqrd[:, :, j])

            # Initialise the R1 data class.  This is used only if an NOE data set is collected but the R1 data of the same frequency has not.
            missing_r1 = 0
            for j in xrange(self.data[i].num_ri):
                if self.data[i].ri_labels[j] == 'NOE' and self.data[i].noe_r1_table[j] == None:
                    missing_r1 = 1
            if missing_r1:
                self.init_res_r1_data(self.data[i])

        # Scaling initialisation.
        if self.scaling_matrix:
            self.scaling_flag = 1
            self.set_params = self.set_params_scaled
        else:
            self.scaling_flag = 0
            self.set_params = self.set_params_unscaled

        # Set the function for packaging diffusion tensor parameters.
        if self.diff_data.params:
            self.pack_diff_params = None
        elif self.diff_data.type == 'iso':
            self.pack_diff_params = self.pack_diff_params_iso
        elif self.diff_data.type == 'axial':
            self.pack_diff_params = self.pack_diff_params_axial
        elif self.diff_data.type == 'aniso':
            self.pack_diff_params = self.pack_diff_params_aniso

        # Set the functions self.func, self.dfunc, and self.d2func for minimising model-free parameter for a single residue.
        if param_set == 'mf':
            self.func = self.func_mf
            self.dfunc = self.dfunc_mf
            self.d2func = self.d2func_mf

        # Set the functions self.func, self.dfunc, and self.d2func for minimising diffusion tensor parameters.
        elif param_set == 'diff':
            self.func = self.func_diff
            self.dfunc = self.dfunc_diff
            self.d2func = self.d2func_diff

        # Set the functions self.func, self.dfunc, and self.d2func for minimising diffusion tensor together with all model-free parameters.
        elif param_set == 'all':
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

        # Set self.data[0] to data.
        data = self.data[0]

        # Arguments
        self.set_params(params)

        # Diffusion tensor parameters.
        if self.pack_diff_params:
            self.pack_diff_params()

        # Test if the function has already been calculated with these parameter values.
        if sum(self.params == self.func_test) == self.total_num_params:
            return data.chi2

        # Store the parameter values in self.data.func_test for testing on next call if the function has already been calculated.
        self.func_test = self.params * 1.0

        # Diffusion tensor geometry calculations.
        if self.diff_data.calc_geom:
            self.diff_data.calc_geom(data, self.diff_data)

        # Diffusion tensor weight calculations.
        self.diff_data.calc_ci(data)

        # Diffusion tensor correlation times.
        self.diff_data.calc_ti(data, self.diff_data)

        # Calculate the components of the spectral densities.
        if data.calc_jw_comps:
            data.calc_jw_comps(data, self.params)

        # Calculate the spectral density values.
        data.jw = data.calc_jw(data, self.params)

        # Calculate the relaxation formula components.
        data.create_ri_comps(data, self.params)

        # Calculate the R1, R2, and sigma_noe values.
        data.create_ri_prime(data)

        # Calculate the R1, R2, and NOE values.
        data.ri = data.ri_prime * 1.0
        ri(data, self.params)

        # Calculate the chi-squared value.
        data.chi2 = chi2(data.relax_data, data.ri, data.errors)

        return data.chi2


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
        if sum(self.params == self.data.grad_test) == self.data.total_num_params:
            #if len(self.params):
            return self.data.dchi2

        # Test if the function has already been called
        if sum(self.params == self.data.func_test) != self.data.total_num_params:
            raise RelaxError, "Should not be here."

        # Store the parameter values in self.data.grad_test for testing on next call if the gradient has already been calculated.
        self.data.grad_test = self.params * 1.0

        # Calculate the spectral density gradient components.
        if self.calc_djw_comps[0]:
            self.calc_djw_comps[0](self.data)

        # Calculate the spectral density gradients.
        for i in xrange(self.data.total_num_params):
            if self.calc_djw[0]:
                self.data.djw[0][:, :, i] = self.calc_djw[0][i](self.data)

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
        if sum(self.params == self.data.hess_test) == self.data.total_num_params:
            #if len(self.params):
            return self.data.d2chi2

        # Test if the gradient has already been called
        if sum(self.params == self.data.grad_test) != self.data.total_num_params:
            raise RelaxError, "Should not be here."

        # Store the parameter values in self.data.hess_test for testing on next call if the Hessian has already been calculated.
        self.data.hess_test = self.params * 1.0

        # Calculate the spectral density Hessians.
        for i in xrange(self.data.total_num_params):
            for j in xrange(i + 1):
                if self.calc_d2jw[0][i][j]:
                    self.data.d2jw[0][:, :, i, j] = self.calc_d2jw[0][i][j](self.data)

                    # Make the Hessian symmetric.
                    if i != j:
                        self.data.d2jw[0][:, :, j, i] = self.data.d2jw[0][:, :, i, j]

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


    def init_diff_data(self, diff_data):
        """Function for the initialisation of diffusion tensor specific data."""

        # Isotropic diffusion.
        if diff_data.type == 'iso':
            # Number of indecies in the generic equations.
            diff_data.num_indecies = 1

            # Set up the weight functions.
            diff_data.calc_geom = None
            diff_data.calc_ci = calc_ci_iso
            diff_data.calc_ti = calc_ti_iso

        # Axially symmetric diffusion.
        elif diff_data.type == 'axial':
            # Number of indecies in the generic equations.
            diff_data.num_indecies = 3

            # Set up the weight functions.
            diff_data.calc_geom = calc_geom_axial
            diff_data.calc_ci = calc_ci_axial
            diff_data.calc_ti = calc_ti_axial

            # Unit vectors.
            diff_data.dpar_unit_vector = zeros(3, Float64)

        # Anisotropic diffusion.
        elif diff_type == 'aniso':
            # Number of indecies in the generic equations.
            diff_data.num_indecies = 5

            # Set up the weight functions.
            diff_data.calc_geom = calc_geom_aniso
            diff_data.calc_ci = calc_ci_aniso
            diff_data.calc_ti = calc_ti_aniso


    def init_res_data(self, data, diff_data):
        """Function for the initialisation of the residue specific data."""

        # Weights and global correlation times for the model-free equations.
        data.ci = zeros(diff_data.num_indecies, Float64)
        data.ti = zeros(diff_data.num_indecies, Float64)

        # Empty spectral density components.
        data.w_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.fact_ti = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.w_te_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.w_tf_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.w_ts_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.inv_te_denom = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.inv_tf_denom = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)
        data.inv_ts_denom = zeros((data.num_frq, 5, diff_data.num_indecies), Float64)

        # Empty spectral density values, gradients, and Hessians.
        data.jw = zeros((data.num_frq, 5), Float64)
        data.djw = zeros((data.num_frq, 5, data.num_params), Float64)
        data.d2jw = zeros((data.num_frq, 5, data.num_params, data.num_params), Float64)

        # Calculate the fixed components of the dipolar and CSA constants.
        data.csa_const_fixed = zeros(data.num_frq, Float64)
        data.dip_const_fixed = None
        calc_fixed_csa(data)
        calc_fixed_dip(data)

        # Dipolar and CSA constants.
        data.dip_const_func = 0.0
        data.dip_const_grad = 0.0
        data.dip_const_hess = 0.0
        data.csa_const_func = zeros((data.num_frq), Float64)
        data.csa_const_grad = zeros((data.num_frq), Float64)
        data.csa_const_hess = zeros((data.num_frq), Float64)

        # Components of the transformed relaxation equations.
        data.dip_comps_func = zeros((data.num_ri), Float64)
        data.csa_comps_func = zeros((data.num_ri), Float64)
        data.rex_comps_func = zeros((data.num_ri), Float64)
        data.dip_jw_comps_func = zeros((data.num_ri), Float64)
        data.csa_jw_comps_func = zeros((data.num_ri), Float64)

        # First partial derivative components of the transformed relaxation equations.
        data.dip_comps_grad = zeros((data.num_ri), Float64)
        data.csa_comps_grad = zeros((data.num_ri), Float64)
        data.rex_comps_grad = zeros((data.num_ri), Float64)
        data.dip_jw_comps_grad = zeros((data.num_ri, data.num_params), Float64)
        data.csa_jw_comps_grad = zeros((data.num_ri, data.num_params), Float64)

        # First partial derivative components of the transformed relaxation equations.
        data.dip_comps_hess = zeros((data.num_ri), Float64)
        data.csa_comps_hess = zeros((data.num_ri), Float64)
        data.rex_comps_hess = zeros((data.num_ri), Float64)
        data.dip_jw_comps_hess = zeros((data.num_ri, data.num_params, data.num_params), Float64)
        data.csa_jw_comps_hess = zeros((data.num_ri, data.num_params, data.num_params), Float64)

        # Transformed relaxation values, gradients, and Hessians.
        data.ri_prime = zeros((data.num_ri), Float64)
        data.dri_prime = zeros((data.num_ri, data.num_params), Float64)
        data.d2ri_prime = zeros((data.num_ri, data.num_params, data.num_params), Float64)

        # Data structures containing the Ri values.
        data.ri = zeros((data.num_ri), Float64)
        data.dri = zeros((data.num_ri, data.num_params), Float64)
        data.d2ri = zeros((data.num_ri, data.num_params, data.num_params), Float64)

        # Data structures containing the R1 values at the position of and corresponding to the NOE.
        data.r1 = zeros((data.num_ri), Float64)
        data.dr1 = zeros((data.num_ri, data.num_params), Float64)
        data.d2r1 = zeros((data.num_ri, data.num_params, data.num_params), Float64)

        # Data structures containing the chi-squared values.
        data.chi2 = 0.0
        data.dchi2 = zeros((data.num_params), Float64)
        data.d2chi2 = zeros((data.num_params, data.num_params), Float64)


    def init_res_r1_data(self, data):
        """Function for initialisation of the R1 data class.

        This data class is only used if an NOE data set is collected but no R1 data set
        corresponding to the same frequency exists.
        """

        # Initialise an instance of Data.
        r1_data = Data()

        # Copy a few things from 'data' to 'r1_data'
        r1_data.num_frq = data.num_frq
        r1_data.dip_const_fixed = data.dip_const_fixed
        r1_data.csa_const_fixed = data.csa_const_fixed

        # Components of the transformed relaxation equations.
        r1_data.dip_comps_func = zeros(data.num_ri, Float64)
        r1_data.csa_comps_func = zeros(data.num_ri, Float64)
        r1_data.dip_jw_comps_func = zeros(data.num_ri, Float64)
        r1_data.csa_jw_comps_func = zeros(data.num_ri, Float64)

        # Initialise the first partial derivative components of the transformed relaxation equations.
        r1_data.dip_comps_grad = zeros(data.num_ri, Float64)
        r1_data.csa_comps_grad = zeros(data.num_ri, Float64)
        r1_data.rex_comps_grad = zeros(data.num_ri, Float64)
        r1_data.dip_jw_comps_grad = zeros((data.num_ri, data.num_params), Float64)
        r1_data.csa_jw_comps_grad = zeros((data.num_ri, data.num_params), Float64)

        # Initialise the first partial derivative components of the transformed relaxation equations.
        r1_data.dip_comps_hess = zeros(data.num_ri, Float64)
        r1_data.csa_comps_hess = zeros(data.num_ri, Float64)
        r1_data.rex_comps_hess = zeros(data.num_ri, Float64)
        r1_data.dip_jw_comps_hess = zeros((data.num_ri, data.num_params, data.num_params), Float64)
        r1_data.csa_jw_comps_hess = zeros((data.num_ri, data.num_params, data.num_params), Float64)

        # Initialise the transformed relaxation values, gradients, and Hessians.
        r1_data.ri_prime = zeros(data.num_ri, Float64)
        r1_data.dri_prime = zeros((data.num_ri, data.num_params), Float64)
        r1_data.d2ri_prime = zeros((data.num_ri, data.num_params, data.num_params), Float64)

        # Place a few function pointer arrays in the data class for the calculation of the R1 value when an NOE data set exists but the R1 set does not.
        r1_data.create_dri_prime = data.create_dri_prime
        r1_data.create_d2ri_prime = data.create_d2ri_prime

        # CSA, bond length, and Rex indecies.
        r1_data.csa_index = data.csa_index
        r1_data.r_index = data.r_index
        r1_data.rex_index = data.rex_index

        # Place 'r1_data' into 'data'.
        data.r1_data = r1_data


    def lm_dri(self):
        """Return the function used for Levenberg-Marquardt minimisation."""

        # Diagonal scaling.
        if self.scaling_flag:
            return matrixmultiply(self.data.dri, self.scaling_matrix)
        else:
            return self.data.dri


    def pack_difF_params_iso(self):
        """Function for extracting the iso diffusion parameters from the parameter vector."""

        self.data.diff_params = self.params[0:1]


    def pack_difF_params_axial(self):
        """Function for extracting the axial diffusion parameters from the parameter vector."""

        self.data.diff_params = self.params[0:4]


    def pack_difF_params_iso(self):
        """Function for extracting the aniso diffusion parameters from the parameter vector."""

        self.data.diff_params = self.params[0:6]


    def scale_gradient(self):
        """Function for the diagonal scaling of the chi-squared gradient."""

        self.data.dchi2 = matrixmultiply(self.data.dchi2, self.scaling_matrix)


    def scale_hessian(self):
        """Function for the diagonal scaling of the chi-squared Hessian."""

        self.data.d2chi2 = matrixmultiply(self.scaling_matrix, matrixmultiply(self.data.d2chi2, self.scaling_matrix))


    def set_params_scaled(self, params):
        """Function for setting self.params to the parameter vector times the scaling vector."""

        self.params = matrixmultiply(params, self.scaling_matrix)


    def set_params_unscaled(self, params):
        """Function for setting self.params to the parameter vector."""

        self.params = params * 1.0


    def setup_equations(self, data):
        """Setup all the residue specific equations."""

        # Set up the spectral density functions.
        ########################################

        # Create empty spectral density gradient and Hessian function data structures.
        data.calc_djw = []
        data.calc_d2jw = []
        for i in xrange(data.num_params):
            data.calc_djw.append(None)
            data.calc_d2jw.append([])
            for j in xrange(data.num_params):
                data.calc_d2jw[i].append(None)


        # The original model-free equations {tm, S2, te, Rex, r, CSA}.
        ##############################################################

        if data.equations == 'mf_orig':
            # Find the indecies of the model-free parameters.
            data.tm_index, data.s2_index, data.te_index, data.rex_index, data.r_index, data.csa_index = None, None, None, None, None, None
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2':
                    data.s2_index = i
                elif data.param_types[i] == 'te':
                    data.te_index = i
                elif data.param_types[i] == 'Rex':
                    data.rex_index = i
                elif data.param_types[i] == 'r':
                    data.r_index = i
                elif data.param_types[i] == 'CSA':
                    data.csa_index = i
                else:
                    print "Unknown parameter."
                    return 0

            # No spectral density parameters {}.
            if data.s2_index == None and data.te_index == None:
                # Equation.
                data.calc_jw_comps = None
                data.calc_jw = calc_jw

                # Gradient.
                data.calc_djw_comps = None

            # Spectral density parameters {S2}.
            elif data.s2_index != None and data.te_index == None:
                # Equation.
                data.calc_jw_comps = None
                data.calc_jw = calc_S2_jw

                # Gradient.
                data.calc_djw_comps = None
                data.calc_djw[data.s2_index] = calc_S2_djw_dS2

            # Spectral density parameters {S2, te}.
            elif data.s2_index != None and data.te_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2_te_jw_comps
                data.calc_jw = calc_S2_te_jw

                # Gradient.
                data.calc_djw_comps = calc_S2_te_djw_comps
                data.calc_djw[data.s2_index] = calc_S2_te_djw_dS2
                data.calc_djw[data.te_index] = calc_S2_te_djw_dte

                # Hessian.
                data.calc_d2jw[data.s2_index][data.te_index] = data.calc_d2jw[data.te_index][data.s2_index] = calc_S2_te_d2jw_dS2dte
                data.calc_d2jw[data.te_index][data.te_index] = calc_S2_te_d2jw_dte2

            # Spectral density parameters {tm}.
            elif data.s2_index == None and data.te_index == None:
                # Equation.
                data.calc_jw_comps = calc_tm_jw_comps
                data.calc_jw = calc_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_djw_comps
                data.calc_djw[0] = calc_tm_djw_dtm

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_d2jw_dtm2

            # Spectral density parameters {tm, S2}.
            elif data.s2_index != None and data.te_index == None:
                # Equation.
                data.calc_jw_comps = calc_tm_jw_comps
                data.calc_jw = calc_S2_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_djw_comps
                data.calc_djw[0] = calc_tm_S2_djw_dtm
                data.calc_djw[data.s2_index] = calc_S2_djw_dS2

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2_d2jw_dtm2
                data.calc_d2jw[0][data.s2_index] = data.calc_d2jw[data.s2_index][0] = calc_tm_S2_d2jw_dtmdS2

            # Spectral density parameters {tm, S2, te}.
            elif data.s2_index != None and data.te_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2_te_jw_comps
                data.calc_jw = calc_S2_te_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2_te_djw_comps
                data.calc_djw[0] = calc_tm_S2_te_djw_dtm
                data.calc_djw[data.s2_index] = calc_S2_te_djw_dS2
                data.calc_djw[data.te_index] = calc_tm_S2_te_djw_dte

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2_te_d2jw_dtm2
                data.calc_d2jw[0][data.s2_index] = data.calc_d2jw[data.s2_index][0] = calc_tm_S2_te_d2jw_dtmdS2
                data.calc_d2jw[0][data.te_index] = data.calc_d2jw[data.te_index][0] = calc_tm_S2_te_d2jw_dtmdte
                data.calc_d2jw[data.s2_index][data.te_index] = data.calc_d2jw[data.te_index][data.s2_index] = calc_tm_S2_te_d2jw_dS2dte
                data.calc_d2jw[data.te_index][data.te_index] = calc_tm_S2_te_d2jw_dte2

            # Bad parameter combination.
            else:
                print "Invalid combination of parameters for the extended model-free equation."
                return 0


        # The extended model-free equations {tm, S2f, tf, S2, ts, Rex, r, CSA}.
        #######################################################################

        elif data.equations == 'mf_ext':
            # Find the indecies of the model-free parameters.
            data.tm_index, data.s2f_index, data.tf_index, data.s2_index, data.ts_index, data.rex_index, data.r_index, data.csa_index,  = None, None, None, None, None, None, None, None
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2f':
                    data.s2f_index = i
                elif data.param_types[i] == 'tf':
                    data.tf_index = i
                elif data.param_types[i] == 'S2':
                    data.s2_index = i
                elif data.param_types[i] == 'ts':
                    data.ts_index = i
                elif data.param_types[i] == 'Rex':
                    data.rex_index = i
                elif data.param_types[i] == 'r':
                    data.r_index = i
                elif data.param_types[i] == 'CSA':
                    data.csa_index = i
                else:
                    print "Unknown parameter."
                    return 0

            # Spectral density parameters {S2f, S2, ts}.
            if data.s2f_index != None and data.tf_index == None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_S2_ts_jw_comps
                data.calc_jw = calc_S2f_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_S2_ts_djw_comps
                data.calc_djw[data.s2f_index] = calc_S2f_S2_ts_djw_dS2f
                data.calc_djw[data.s2_index] = calc_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_index] = calc_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2_index] = calc_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_S2f_S2_ts_d2jw_dts2

            # Spectral density parameters {S2f, tf, S2, ts}.
            elif data.s2f_index != None and data.tf_index != None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_tf_S2_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_tf_S2_ts_djw_comps
                data.calc_djw[data.s2f_index] = calc_S2f_tf_S2_ts_djw_dS2f
                data.calc_djw[data.tf_index] = calc_S2f_tf_S2_ts_djw_dtf
                data.calc_djw[data.s2_index] = calc_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_index] = calc_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_index][data.tf_index] = data.calc_d2jw[data.tf_index][data.s2f_index] = calc_S2f_tf_S2_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2_index] = calc_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.tf_index][data.tf_index] = calc_S2f_tf_S2_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_S2f_S2_ts_d2jw_dts2

            # Spectral density parameters {tm, S2f, S2, ts}.
            elif data.s2f_index != None and data.tf_index == None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2f_S2_ts_jw_comps
                data.calc_jw = calc_S2f_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_S2_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_S2_ts_djw_dtm
                data.calc_djw[data.s2f_index] = calc_tm_S2f_S2_ts_djw_dS2f
                data.calc_djw[data.s2_index] = calc_tm_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_index] = calc_tm_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_S2_ts_d2jw_dtm2
                data.calc_d2jw[0][data.s2f_index] = data.calc_d2jw[data.s2f_index][0] = calc_tm_S2f_S2_ts_d2jw_dtmdS2f
                data.calc_d2jw[0][data.s2_index] = data.calc_d2jw[data.s2_index][0] = calc_tm_S2f_S2_ts_d2jw_dtmdS2
                data.calc_d2jw[0][data.ts_index] = data.calc_d2jw[data.ts_index][0] = calc_tm_S2f_S2_ts_d2jw_dtmdts
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[ts_index][data.s2f_index] = calc_tm_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2_index] = calc_tm_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_tm_S2f_S2_ts_d2jw_dts2

            # Spectral density parameters {tm, S2f, tf, S2, ts}.
            elif data.s2f_index != None and data.tf_index != None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2f_tf_S2_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_tf_S2_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_tf_S2_ts_djw_dtm
                data.calc_djw[data.s2f_index] = calc_tm_S2f_tf_S2_ts_djw_dS2f
                data.calc_djw[data.tf_index] = calc_tm_S2f_tf_S2_ts_djw_dtf
                data.calc_djw[data.s2_index] = calc_tm_S2f_tf_S2_ts_djw_dS2
                data.calc_djw[data.ts_index] = calc_tm_S2f_tf_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_tf_S2_ts_d2jw_dtm2
                data.calc_d2jw[0][data.s2f_index] = data.calc_d2jw[data.s2f_index][0] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdS2f
                data.calc_d2jw[0][data.s2_index] = data.calc_d2jw[data.s2_index][0] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdS2
                data.calc_d2jw[0][data.tf_index] = data.calc_d2jw[data.tf_index][0] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdtf
                data.calc_d2jw[0][data.ts_index] = data.calc_d2jw[data.ts_index][0] = calc_tm_S2f_tf_S2_ts_d2jw_dtmdts
                data.calc_d2jw[data.s2f_index][data.tf_index] = data.calc_d2jw[data.tf_index][data.s2f_index] = calc_tm_S2f_tf_S2_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_tm_S2f_tf_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2_index] = calc_tm_S2f_tf_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.tf_index][data.tf_index] = calc_tm_S2f_tf_S2_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_tm_S2f_tf_S2_ts_d2jw_dts2

            # Bad parameter combination.
            else:
                print "Invalid combination of parameters for the extended model-free equation."
                return 0


        # The extended 2 model-free equations {tm, S2f, tf, S2s, ts, Rex, r, CSA}.
        #########################################################################

        elif data.equations == 'mf_ext2':
            # Find the indecies of the model-free parameters.
            data.tm_index, data.s2f_index, data.tf_index, data.s2s_index, data.ts_index, data.rex_index, data.r_index, data.csa_index,  = None, None, None, None, None, None, None, None
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2f':
                    data.s2f_index = i
                elif data.param_types[i] == 'tf':
                    data.tf_index = i
                elif data.param_types[i] == 'S2s':
                    data.s2s_index = i
                elif data.param_types[i] == 'ts':
                    data.ts_index = i
                elif data.param_types[i] == 'Rex':
                    data.rex_index = i
                elif data.param_types[i] == 'r':
                    data.r_index = i
                elif data.param_types[i] == 'CSA':
                    data.csa_index = i
                else:
                    print "Unknown parameter."
                    return 0

            # Spectral density parameters {S2f, S2s, ts}.
            if data.s2f_index != None and data.tf_index == None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_S2s_ts_djw_comps
                data.calc_djw[data.s2f_index] = calc_S2f_S2s_ts_djw_dS2f
                data.calc_djw[data.s2s_index] = calc_S2f_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_index] = calc_S2f_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_S2f_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2s_index] = calc_S2f_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_S2f_S2s_ts_d2jw_dts2

            # Spectral density parameters {S2f, tf, S2s, ts}.
            elif data.s2f_index != None and data.tf_index != None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_tf_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_tf_S2s_ts_djw_comps
                data.calc_djw[data.s2f_index] = calc_S2f_tf_S2s_ts_djw_dS2f
                data.calc_djw[data.tf_index] = calc_S2f_tf_S2s_ts_djw_dtf
                data.calc_djw[data.s2s_index] = calc_S2f_tf_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_index] = calc_S2f_tf_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_index][data.tf_index] = data.calc_d2jw[data.tf_index][data.s2f_index] = calc_S2f_tf_S2s_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_S2f_tf_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2s_index] = calc_S2f_tf_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.tf_index][data.tf_index] = calc_S2f_tf_S2s_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_S2f_tf_S2s_ts_d2jw_dts2

            # Spectral density parameters {tm, S2f, S2s, ts}.
            elif data.s2f_index != None and data.tf_index == None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2f_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_S2s_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_S2s_ts_djw_dtm
                data.calc_djw[data.s2f_index] = calc_tm_S2f_S2s_ts_djw_dS2f
                data.calc_djw[data.s2s_index] = calc_tm_S2f_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_index] = calc_tm_S2f_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_S2s_ts_d2jw_dtm2
                data.calc_d2jw[0][data.s2f_index] = data.calc_d2jw[data.s2f_index][0] = calc_tm_S2f_S2s_ts_d2jw_dtmdS2f
                data.calc_d2jw[0][data.s2s_index] = data.calc_d2jw[data.s2s_index][0] = calc_tm_S2f_S2s_ts_d2jw_dtmdS2s
                data.calc_d2jw[0][data.ts_index] = data.calc_d2jw[data.ts_index][0] = calc_tm_S2f_S2s_ts_d2jw_dtmdts
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_tm_S2f_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2s_index] = calc_tm_S2f_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_tm_S2f_S2s_ts_d2jw_dts2

            # Spectral density parameters {tm, S2f, tf, S2s, ts}.
            elif data.s2f_index != None and data.tf_index != None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2f_tf_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_tf_S2s_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_tf_S2s_ts_djw_dtm
                data.calc_djw[data.s2f_index] = calc_tm_S2f_tf_S2s_ts_djw_dS2f
                data.calc_djw[data.tf_index] = calc_tm_S2f_tf_S2s_ts_djw_dtf
                data.calc_djw[data.s2s_index] = calc_tm_S2f_tf_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_index] = calc_tm_S2f_tf_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dtm2
                data.calc_d2jw[0][data.s2f_index] = data.calc_d2jw[data.s2f_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdS2f
                data.calc_d2jw[0][data.s2s_index] = data.calc_d2jw[data.s2s_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdS2s
                data.calc_d2jw[0][data.tf_index] = data.calc_d2jw[data.tf_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdtf
                data.calc_d2jw[0][data.ts_index] = data.calc_d2jw[data.ts_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dtmdts
                data.calc_d2jw[data.s2f_index][data.tf_index] = data.calc_d2jw[data.tf_index][data.s2f_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2f_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_index][data.ts_index] = data.calc_d2jw[data.ts_index][data.s2s_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.tf_index][data.tf_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_index][data.ts_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dts2

            # Bad parameter combination.
            else:
                print "Invalid combination of parameters for the extended model-free equation."
                return 0

        # Unknown model-free equation.
        else:
            print "Unknown model-free equation."
            return 0


        # Initialise function pointer data structures.
        ##############################################

        # Relaxation equation components.
        data.create_dip_func, data.create_dip_grad, data.create_dip_hess = [], [], []
        data.create_csa_func, data.create_csa_grad, data.create_csa_hess = [], [], []
        data.create_rex_func, data.create_rex_grad = [], []

        data.create_dip_jw_func, data.create_dip_jw_grad, data.create_dip_jw_hess = [], [], []
        data.create_csa_jw_func, data.create_csa_jw_grad, data.create_csa_jw_hess = [], [], []

        # Ri'
        data.create_ri_prime = None
        data.create_dri_prime = []
        data.create_d2ri_prime = []

        # Ri
        data.create_ri, data.create_dri, data.create_d2ri = [], [], []
        data.get_r1, data.get_dr1, data.get_d2r1 = [], [], []

        # Fill the structures with None.
        for i in xrange(data.num_ri):
            data.create_dip_func.append(None)
            data.create_dip_grad.append(None)
            data.create_dip_hess.append(None)
            data.create_csa_func.append(None)
            data.create_csa_grad.append(None)
            data.create_csa_hess.append(None)
            data.create_rex_func.append(None)
            data.create_rex_grad.append(None)
            data.create_dip_jw_func.append(None)
            data.create_dip_jw_grad.append(None)
            data.create_dip_jw_hess.append(None)
            data.create_csa_jw_func.append(None)
            data.create_csa_jw_grad.append(None)
            data.create_csa_jw_hess.append(None)
            data.create_ri.append(None)
            data.create_dri.append(None)
            data.create_d2ri.append(None)
            data.get_r1.append(None)
            data.get_dr1.append(None)
            data.get_d2r1.append(None)


        # Select the functions for the calculation of ri_prime, dri_prime, and d2ri_prime components.
        #############################################################################################

        for i in xrange(data.num_ri):
            # The R1 equations.
            if data.ri_labels[i] == 'R1':
                data.create_csa_func[i] = comp_r1_csa_const
                data.create_csa_grad[i] = comp_r1_csa_const
                data.create_csa_hess[i] = comp_r1_csa_const
                data.create_dip_jw_func[i] = comp_r1_dip_jw
                data.create_dip_jw_grad[i] = comp_r1_dip_jw
                data.create_dip_jw_hess[i] = comp_r1_dip_jw
                data.create_csa_jw_func[i] = comp_r1_csa_jw
                data.create_csa_jw_grad[i] = comp_r1_csa_jw
                data.create_csa_jw_hess[i] = comp_r1_csa_jw

            # The R2 equations.
            elif data.ri_labels[i] == 'R2':
                data.create_dip_func[i] = comp_r2_dip_const
                data.create_dip_grad[i] = comp_r2_dip_const
                data.create_dip_hess[i] = comp_r2_dip_const
                data.create_csa_func[i] = comp_r2_csa_const
                data.create_csa_grad[i] = comp_r2_csa_const
                data.create_csa_hess[i] = comp_r2_csa_const
                data.create_rex_func[i] = comp_rex_const_func
                data.create_rex_grad[i] = comp_rex_const_grad
                data.create_dip_jw_func[i] = comp_r2_dip_jw
                data.create_dip_jw_grad[i] = comp_r2_dip_jw
                data.create_dip_jw_hess[i] = comp_r2_dip_jw
                data.create_csa_jw_func[i] = comp_r2_csa_jw
                data.create_csa_jw_grad[i] = comp_r2_csa_jw
                data.create_csa_jw_hess[i] = comp_r2_csa_jw

            # The NOE equations.
            elif data.ri_labels[i] == 'NOE':
                data.create_dip_jw_func[i] = comp_sigma_noe_dip_jw
                data.create_dip_jw_grad[i] = comp_sigma_noe_dip_jw
                data.create_dip_jw_hess[i] = comp_sigma_noe_dip_jw
                data.create_ri[i] = calc_noe
                data.create_dri[i] = calc_dnoe
                data.create_d2ri[i] = calc_d2noe
                if data.noe_r1_table[i] == None:
                    data.get_r1[i] = calc_r1
                    data.get_dr1[i] = calc_dr1
                    data.get_d2r1[i] = calc_d2r1
                else:
                    data.get_r1[i] = extract_r1
                    data.get_dr1[i] = extract_dr1
                    data.get_d2r1[i] = extract_d2r1


        # Select the functions for the calculation of ri_prime, dri_prime, and d2ri_prime.
        ##################################################################################

        # ri_prime.
        if data.rex_index == None:
            data.create_ri_prime = func_ri_prime
        else:
            data.create_ri_prime = func_ri_prime_rex

        # dri_prime and d2ri_prime.
        for i in xrange(data.num_params):
            if data.param_types[i] == 'Rex':
                data.create_dri_prime.append(func_dri_drex_prime)
                data.create_d2ri_prime.append([])
                for k in xrange(data.num_params):
                    if data.param_types[k] == 'Rex':
                        data.create_d2ri_prime[i].append(None)
                    elif data.param_types[k] == 'r':
                        data.create_d2ri_prime[i].append(None)
                    elif data.param_types[k] == 'CSA':
                        data.create_d2ri_prime[i].append(None)
                    else:
                        data.create_d2ri_prime[i].append(None)
            elif data.param_types[i] == 'r':
                data.create_dri_prime.append(func_dri_dr_prime)
                data.create_d2ri_prime.append([])
                for k in xrange(data.num_params):
                    if data.param_types[k] == 'Rex':
                        data.create_d2ri_prime[i].append(None)
                    elif data.param_types[k] == 'r':
                        data.create_d2ri_prime[i].append(func_d2ri_dr2_prime)
                    elif data.param_types[k] == 'CSA':
                        data.create_d2ri_prime[i].append(None)
                    else:
                        data.create_d2ri_prime[i].append(func_d2ri_drdjw_prime)
            elif data.param_types[i] == 'CSA':
                data.create_dri_prime.append(func_dri_dcsa_prime)
                data.create_d2ri_prime.append([])
                for k in xrange(data.num_params):
                    if data.param_types[k] == 'Rex':
                        data.create_d2ri_prime[i].append(None)
                    elif data.param_types[k] == 'r':
                        data.create_d2ri_prime[i].append(None)
                    elif data.param_types[k] == 'CSA':
                        data.create_d2ri_prime[i].append(func_d2ri_dcsa2_prime)
                    else:
                        data.create_d2ri_prime[i].append(func_d2ri_dcsadjw_prime)
            else:
                data.create_dri_prime.append(func_dri_djw_prime)
                data.create_d2ri_prime.append([])
                for k in xrange(data.num_params):
                    if data.param_types[k] == 'Rex':
                        data.create_d2ri_prime[i].append(None)
                    elif data.param_types[k] == 'r':
                        data.create_d2ri_prime[i].append(func_d2ri_djwdr_prime)
                    elif data.param_types[k] == 'CSA':
                        data.create_d2ri_prime[i].append(func_d2ri_djwdcsa_prime)
                    else:
                        data.create_d2ri_prime[i].append(func_d2ri_djwidjwj_prime)


        # Both the bond length and CSA are fixed {}.
        ############################################

        if data.r_index == None and data.csa_index == None:
            # The main ri component functions
            if data.rex_index == None:
                data.create_ri_comps = ri_comps
                data.create_dri_comps = dri_comps
                data.create_d2ri_comps = d2ri_comps
            else:
                data.create_ri_comps = ri_comps_rex
                data.create_dri_comps = dri_comps_rex
                data.create_d2ri_comps = d2ri_comps

            # Calculate the dipolar and CSA constant components.
            comp_dip_const_func(data, data.bond_length)
            comp_csa_const_func(data, data.csa)
            for i in xrange(data.num_ri):
                data.dip_comps_func[i] = data.dip_const_func
                if data.create_dip_func[i]:
                    data.dip_comps_func[i] = data.create_dip_func[i](data.dip_const_func)
                if data.create_csa_func[i]:
                    data.csa_comps_func[i] = data.create_csa_func[i](data.csa_const_func[data.remap_table[i]])


        # The bond length is a parameter {r}.
        #####################################

        elif data.r_index != None and data.csa_index == None:
            # The main ri component functions
            if data.rex_index == None:
                data.create_ri_comps = ri_comps_r
                data.create_dri_comps = dri_comps_r
                data.create_d2ri_comps = d2ri_comps_r
            else:
                data.create_ri_comps = ri_comps_r_rex
                data.create_dri_comps = dri_comps_r_rex
                data.create_d2ri_comps = d2ri_comps_r

            # Calculate the CSA constant.
            comp_csa_const_func(data, data.csa)
            for i in xrange(data.num_ri):
                if data.create_csa_func[i]:
                    data.csa_comps_func[i] = data.create_csa_func[i](data.csa_const_func[data.remap_table[i]])


        # The CSA is a parameter {CSA}.
        ###############################

        elif data.r_index == None and data.csa_index != None:
            # The main ri component functions
            if data.rex_index == None:
                data.create_ri_comps = ri_comps_csa
                data.create_dri_comps = dri_comps_csa
                data.create_d2ri_comps = d2ri_comps_csa
            else:
                data.create_ri_comps = ri_comps_csa_rex
                data.create_dri_comps = dri_comps_csa_rex
                data.create_d2ri_comps = d2ri_comps_csa

            # Calculate the dipolar constant.
            comp_dip_const_func(data, data.bond_length)
            for i in xrange(data.num_ri):
                data.dip_comps_func[i] = data.dip_const_func
                if data.create_dip_func[i]:
                    data.dip_comps_func[i] = data.create_dip_func[i](data.dip_const_func)


        # Both the bond length and CSA are parameters {r, CSA}.
        #######################################################

        elif data.r_index != None and data.csa_index != None:
            # The main ri component functions
            if data.rex_index == None:
                data.create_ri_comps = ri_comps_r_csa
                data.create_dri_comps = dri_comps_r_csa
                data.create_d2ri_comps = d2ri_comps_r_csa
            else:
                data.create_ri_comps = ri_comps_r_csa_rex
                data.create_dri_comps = dri_comps_r_csa_rex
                data.create_d2ri_comps = d2ri_comps_r_csa


        # Invalid combination of parameters.
        ####################################

        else:
            print "Invalid combination of parameters for the model-free equations."
            return 0

        return 1


class Data:
    def __init__(self):
        """Empty container for storing data."""
