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
from correlation_time_comps import *
from correlation_time import *
from jw_mf_comps import *
from jw_mf import *
from ri_comps import *
from ri_prime import *
from ri import *
from chi2 import *


class Mf:
    def __init__(self, total_num_params=0, param_set=None, diff_type=None, diff_params=None, scaling_matrix=None, num_res=None, equations=None, param_types=None, relax_data=None, errors=None, bond_length=None, csa=None, num_frq=0, frq=None, num_ri=None, remap_table=None, noe_r1_table=None, ri_labels=None, gx=0, gh=0, g_ratio=0, h_bar=0, mu0=0, num_params=None, vectors=None):
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

        # Set the function for packaging diffusion tensor parameters.
        if self.diff_data.params:
            self.pack_diff_params = None
            self.param_index = 0
        elif self.diff_data.type == 'iso':
            self.pack_diff_params = self.pack_diff_params_iso
            self.param_index = 1
        elif self.diff_data.type == 'axial':
            self.pack_diff_params = self.pack_diff_params_axial
            self.param_index = 4
        elif self.diff_data.type == 'aniso':
            self.pack_diff_params = self.pack_diff_params_aniso
            self.param_index = 6

        # Create the data array used to store data.
        self.data = []
        for i in xrange(self.num_res):
            # Append the class instance Data to the data array.
            self.data.append(Data())

            # Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
            self.data[i].frq_list = zeros((num_frq[i], 5), Float64)
            self.data[i].frq_list_ext = zeros((num_frq[i], 5, self.diff_data.num_indecies), Float64)
            self.data[i].frq_sqrd_list_ext = zeros((num_frq[i], 5, self.diff_data.num_indecies), Float64)
            for j in xrange(num_frq[i]):
                frqH = 2.0 * pi * frq[i][j]
                frqX = frqH / g_ratio
                self.data[i].frq_list[j, 1] = frqX
                self.data[i].frq_list[j, 2] = frqH - frqX
                self.data[i].frq_list[j, 3] = frqH
                self.data[i].frq_list[j, 4] = frqH + frqX
            self.data[i].frq_sqrd_list = self.data[i].frq_list ** 2
            for j in xrange(self.diff_data.num_indecies):
                self.data[i].frq_list_ext[:, :, j] = self.data[i].frq_list
                self.data[i].frq_sqrd_list_ext[:, :, j] = self.data[i].frq_sqrd_list

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

            # Indecies for constructing the global generic model-free gradient and Hessian kite.
            if i == 0:
                self.data[i].start_index = self.diff_data.num_params
            else:
                self.data[i].start_index = self.data[i-1].end_index
            self.data[i].end_index = self.data[i].start_index + self.data[i].num_params

            # Total number of parameters.
            if self.param_set == 'mf':
                self.data[i].total_num_params = self.data[i].num_params
            else:
                self.data[i].total_num_params = self.data[i].num_params + self.diff_data.num_params

            # Initialise the residue specific data.
            self.init_res_data(self.data[i], self.diff_data)

            # Setup the residue specific equations.
            if not self.setup_equations(self.data[i]):
                raise RelaxError, "The model-free equations could not be setup."

            # Diffusion tensor parameters.
            if self.pack_diff_params:
                self.pack_diff_params()

            # Calculate the correlation time components.
            if self.diff_data.calc_ti_comps:
                self.diff_data.calc_ti_comps(self.diff_data)

            # Calculate the correlation times ti.
            self.diff_data.calc_ti(self.data[i], self.diff_data)

            # Print out the contents of self.data[i].
            if 0:
                print "Contents of self.data[i]."
                for name in dir(self.data[i]):
                    print name + ": " + `type(getattr(self.data[i], name))`
                    #print name + ": " + `getattr(self.data[i], name)`

            # ti spectral density components.
            if self.param_set == 'mf':
                self.data[i].w_ti_sqrd = self.data[i].frq_sqrd_list_ext * self.data[i].ti ** 2
                self.data[i].fact_ti = 1.0 / (1.0 + self.data[i].w_ti_sqrd)

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

        # Initialise the total chi2 value, gradient, and Hessian data structures.
        self.total_chi2 = 0.0
        self.total_dchi2 = zeros((self.total_num_params), Float64)
        self.total_d2chi2 = zeros((self.total_num_params, self.total_num_params), Float64)

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


    def func_all(self, params):
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

        # Diffusion tensor parameters.
        if self.pack_diff_params:
            self.pack_diff_params()

        # Test if the function has already been calculated with these parameter values.
        if sum(self.params == self.func_test) == self.total_num_params:
            return self.total_chi2

        # Store the parameter values in self.func_test for testing on next call if the function has already been calculated.
        self.func_test = self.params * 1.0

        # Set the total chi2 to zero.
        self.total_chi2 = 0.0

        # Loop over the residues.
        for i in xrange(self.num_res):
            # Set self.data[i] to data.
            data = self.data[i]

            # Diffusion tensor geometry calculations.
            if self.diff_data.calc_geom:
                self.diff_data.calc_geom(data, self.diff_data)

            # Diffusion tensor weight calculations.
            self.diff_data.calc_ci(data)

            # Diffusion tensor correlation time components.
            if self.diff_data.calc_ti_comps:
                self.diff_data.calc_ti_comps(self.diff_data)

            # Diffusion tensor correlation times.
            self.diff_data.calc_ti(data, self.diff_data)

            # ti spectral density components.
            data.w_ti_sqrd = data.frq_sqrd_list_ext * data.ti ** 2
            data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

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

            # Add the residue specific chi2 to the total chi2.
            self.total_chi2 = self.total_chi2 + data.chi2

        return self.total_chi2


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

        # Store the parameter values in self.func_test for testing on next call if the function has already been calculated.
        self.func_test = self.params * 1.0

        # Diffusion tensor geometry calculations.
        if self.diff_data.calc_geom:
            self.diff_data.calc_geom(data, self.diff_data)

        # Diffusion tensor weight calculations.
        self.diff_data.calc_ci(data)

        # Diffusion tensor correlation time components.
        if self.diff_data.calc_ti_comps:
            self.diff_data.calc_ti_comps(self.diff_data)

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


    def dfunc_all(self, params):
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

        # Diffusion tensor parameters.
        if self.pack_diff_params:
            self.pack_diff_params()

        # Test if the gradient has already been calculated with these parameter values.
        if sum(self.params == self.grad_test) == self.total_num_params:
            return self.total_dchi2

        # Test if the function has already been called, otherwise run self.func_mf.
        if sum(self.params == self.func_test) != self.total_num_params:
            self.func_all(params)

        # Store the parameter values in self.grad_test for testing on next call if the gradient has already been calculated.
        self.grad_test = self.params * 1.0

        # Set the total chi2 gradient to zero.
        self.total_dchi2 = self.total_dchi2 * 0.0

        # Loop over the residues.
        for i in xrange(self.num_res):
            # Set self.data[i] to data.
            data = self.data[i]

            # Diffusion tensor geometry calculations.
            if self.diff_data.calc_dgeom:
                self.diff_data.calc_dgeom(data, self.diff_data)

            # Diffusion tensor weight calculations.
            if self.diff_data.calc_dci:
                self.diff_data.calc_dci(data)

            # Diffusion tensor correlation time gradient components.
            if self.diff_data.calc_dti_comps:
                self.diff_data.calc_dti_comps(self.diff_data)

            # Diffusion tensor correlation times.
            self.diff_data.calc_dti(data, self.diff_data)

            # Calculate the spectral density gradient components.
            if data.calc_djw_comps:
                data.calc_djw_comps(data, self.params)

            # Calculate the spectral density gradients.
            for i in xrange(data.total_num_params):
                if data.calc_djw[i]:
                    data.djw[:, :, i] = data.calc_djw[i](data, self.params)

            # Calculate the relaxation gradient components.
            data.create_dri_comps(data, self.params)

            # Calculate the R1, R2, and sigma_noe gradients.
            for i in xrange(data.total_num_params):
                data.create_dri_prime[i](data, i)

            # Calculate the R1, R2, and NOE gradients.
            data.dri = data.dri_prime * 1.0
            dri(data, self.params)

            # Calculate the chi-squared gradient.
            data.dchi2 = dchi2(data.relax_data, data.ri, data.dri, data.errors)


            # Index for the construction of the global generic model-free gradient.
            index = self.diff_data.num_params

            # Diffusion parameter part of the global generic model-free gradient.
            self.total_dchi2[0:index] = self.total_dchi2[0:index] + data.dchi2[0:index]

            # Model-free parameter part of the global generic model-free gradient.
            self.total_dchi2[data.start_index:data.end_index] = self.total_dchi2[data.start_index:data.end_index] + data.dchi2[index:]

        # Diagonal scaling.
        if self.scaling_flag:
            self.total_dchi2 = self.scale_gradient(self.total_dchi2)

        return self.total_dchi2


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

        # Set self.data[0] to data.
        data = self.data[0]

        # Arguments
        self.set_params(params)

        # Test if the gradient has already been calculated with these parameter values.
        if sum(self.params == self.grad_test) == self.total_num_params:
            return data.dchi2

        # Test if the function has already been called, otherwise run self.func_mf.
        if sum(self.params == self.func_test) != self.total_num_params:
            self.func_mf(params)

        # Store the parameter values in self.grad_test for testing on next call if the gradient has already been calculated.
        self.grad_test = self.params * 1.0

        # Diffusion tensor geometry calculations.
        #self.diff_data.calc_dgeom(data, self.diff_data)

        # Diffusion tensor weight calculations.
        #self.diff_data.calc_dci(data)

        # Diffusion tensor correlation times.
        #self.diff_data.calc_dti(data, self.diff_data)

        # Calculate the spectral density gradient components.
        if data.calc_djw_comps:
            data.calc_djw_comps(data, self.params)

        # Calculate the spectral density gradients.
        for i in xrange(data.num_params):
            if data.calc_djw[i]:
                data.djw[:, :, i] = data.calc_djw[i](data, self.params)

        # Calculate the relaxation gradient components.
        data.create_dri_comps(data, self.params)

        # Calculate the R1, R2, and sigma_noe gradients.
        for i in xrange(data.num_params):
            data.create_dri_prime[i](data, i)

        # Calculate the R1, R2, and NOE gradients.
        data.dri = data.dri_prime * 1.0
        dri(data, self.params)

        # Calculate the chi-squared gradient.
        data.dchi2 = dchi2(data.relax_data, data.ri, data.dri, data.errors)

        #print "djw:\n" + `data.djw`
        #print "dri_prime:\n" + `data.dri_prime`
        #print "dri:\n" + `data.dri`
        #print "dchi2:\n" + `data.dchi2`

        # Diagonal scaling.
        if self.scaling_flag:
            data.dchi2 = self.scale_gradient(data.dchi2)

        #import sys; sys.exit()
        return data.dchi2


    def d2func_all(self, params):
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

        # Diffusion tensor parameters.
        if self.pack_diff_params:
            self.pack_diff_params()

        # Test if the Hessian has already been calculated with these parameter values.
        if sum(self.params == self.hess_test) == self.total_num_params:
            return self.total_d2chi2

        # Test if the gradient has already been called, otherwise run self.dfunc_mf.
        if sum(self.params == self.grad_test) != self.total_num_params:
            self.dfunc_mf(params)

        # Store the parameter values in self.hess_test for testing on next call if the Hessian has already been calculated.
        self.hess_test = self.params * 1.0

        # Set the total chi2 Hessian to zero.
        self.total_d2chi2 = self.total_d2chi2 * 0.0

        # Loop over the residues.
        for i in xrange(self.num_res):
            # Set self.data[i] to data.
            data = self.data[i]

            # Diffusion tensor geometry calculations.
            if self.diff_data.calc_d2geom:
               self.diff_data.calc_d2geom(data, self.diff_data)

            # Diffusion tensor weight calculations.
            if self.diff_data.calc_d2ci:
                self.diff_data.calc_d2ci(data)

            # Diffusion tensor correlation times.
            if self.diff_data.calc_d2ti:
               self.diff_data.calc_d2ti(data, self.diff_data)

            # Calculate the spectral density Hessians.
            for i in xrange(data.total_num_params):
                for j in xrange(i + 1):
                    if data.calc_d2jw[i][j]:
                        data.d2jw[:, :, i, j] = data.d2jw[:, :, j, i] = data.calc_d2jw[i][j](data, self.params)

            # Calculate the relaxation Hessian components.
            data.create_d2ri_comps(data, self.params)

            # Calculate the R1, R2, and sigma_noe Hessians.
            for i in xrange(data.total_num_params):
                for j in xrange(i + 1):
                    if data.create_d2ri_prime[i][j]:
                        data.create_d2ri_prime[i][j](data, i, j)

            # Calculate the R1, R2, and NOE Hessians.
            data.d2ri = data.d2ri_prime * 1.0
            d2ri(data, self.params)

            # Calculate the chi-squared Hessian.
            data.d2chi2 = d2chi2(data.relax_data, data.ri, data.dri, data.d2ri, data.errors)


            # Index for the construction of the global generic model-free Hessian.
            index = self.diff_data.num_params

            # Pure diffusion parameter part of the global generic model-free Hessian.
            self.total_d2chi2[0:index, 0:index] = self.total_d2chi2[0:index, 0:index] + data.d2chi2[0:index, 0:index]

            # Pure model-free parameter part of the global generic model-free Hessian.
            self.total_d2chi2[data.start_index:data.end_index, data.start_index:data.end_index] = self.total_d2chi2[data.start_index:data.end_index, data.start_index:data.end_index] + data.d2chi2[index:, index:]

            # Off diagonal diffusion and model-free parameter parts of the global generic model-free Hessian.
            self.total_d2chi2[0:index, data.start_index:data.end_index] = self.total_d2chi2[0:index, data.start_index:data.end_index] + data.d2chi2[0:index, index:]
            self.total_d2chi2[data.start_index:data.end_index, 0:index] = self.total_d2chi2[data.start_index:data.end_index, 0:index] + data.d2chi2[index:, 0:index]

        # Diagonal scaling.
        if self.scaling_flag:
            self.total_d2chi2 = self.scale_hessian(self.total_d2chi2)

        return self.total_d2chi2


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

        # Set self.data[0] to data.
        data = self.data[0]

        # Arguments
        self.set_params(params)

        # Test if the Hessian has already been calculated with these parameter values.
        if sum(self.params == self.hess_test) == self.total_num_params:
            return data.d2chi2

        # Test if the gradient has already been called, otherwise run self.dfunc_mf.
        if sum(self.params == self.grad_test) != self.total_num_params:
            self.dfunc_mf(params)

        # Store the parameter values in self.hess_test for testing on next call if the Hessian has already been calculated.
        self.hess_test = self.params * 1.0

        # Diffusion tensor geometry calculations.
        #if self.diff_data.calc_d2geom:
        #   self.diff_data.calc_d2geom(data, self.diff_data)

        # Diffusion tensor weight calculations.
        #self.diff_data.calc_d2ci(data)

        # Diffusion tensor correlation times.
        #if self.diff_data.calc_d2ti:
        #   self.diff_data.calc_d2ti(data, self.diff_data)

        # Calculate the spectral density Hessians.
        for i in xrange(data.num_params):
            for j in xrange(i + 1):
                if data.calc_d2jw[i][j]:
                    data.d2jw[:, :, i, j] = data.d2jw[:, :, j, i] = data.calc_d2jw[i][j](data, self.params)

        # Calculate the relaxation Hessian components.
        data.create_d2ri_comps(data, self.params)

        # Calculate the R1, R2, and sigma_noe Hessians.
        for i in xrange(data.num_params):
            for j in xrange(i + 1):
                if data.create_d2ri_prime[i][j]:
                    data.create_d2ri_prime[i][j](data, i, j)

        # Calculate the R1, R2, and NOE Hessians.
        data.d2ri = data.d2ri_prime * 1.0
        d2ri(data, self.params)

        # Calculate the chi-squared Hessian.
        data.d2chi2 = d2chi2(data.relax_data, data.ri, data.dri, data.d2ri, data.errors)

        # Diagonal scaling.
        if self.scaling_flag:
            data.d2chi2 = self.scale_hessian(data.d2chi2)

        return data.d2chi2


    def init_diff_data(self, diff_data):
        """Function for the initialisation of diffusion tensor specific data."""

        # Isotropic diffusion.
        if diff_data.type == 'iso':
            # Number of diffusion parameters.
            diff_data.num_params = 1

            # Number of indecies in the generic equations.
            diff_data.num_indecies = 1

            # Geometry function, gradient, and Hessian.
            diff_data.calc_geom = None
            diff_data.calc_dgeom = None
            diff_data.calc_d2geom = None

            # Weight function, gradient, and Hessian.
            diff_data.calc_ci = calc_iso_ci
            diff_data.calc_dci = None
            diff_data.calc_d2ci = None

            # Global correlation time function, gradient, and Hessian components.
            diff_data.calc_ti_comps = None
            diff_data.calc_dti_comps = None
            diff_data.calc_d2ti_comps = None

            # Global correlation time function, gradient, and Hessian.
            diff_data.calc_ti = calc_iso_ti
            diff_data.calc_dti = calc_iso_dti
            diff_data.calc_d2ti = None


        # Axially symmetric diffusion.
        elif diff_data.type == 'axial':
            # Number of diffusion parameters.
            diff_data.num_params = 4

            # Number of indecies in the generic equations.
            diff_data.num_indecies = 3

            # Geometry function, gradient, and Hessian.
            diff_data.calc_geom = calc_axial_geom
            diff_data.calc_dgeom = calc_axial_dgeom
            diff_data.calc_d2geom = calc_axial_d2geom

            # Weight function, gradient, and Hessian.
            diff_data.calc_ci = calc_axial_ci
            diff_data.calc_dci = calc_axial_dci
            diff_data.calc_d2ci = calc_axial_d2ci

            # Global correlation time function, gradient, and Hessian components.
            diff_data.calc_ti_comps = calc_axial_ti_comps
            diff_data.calc_dti_comps = calc_axial_dti_comps
            diff_data.calc_d2ti_comps = calc_axial_d2ti_comps

            # Global correlation time function, gradient, and Hessian.
            diff_data.calc_ti = calc_axial_ti
            diff_data.calc_dti = calc_axial_dti
            diff_data.calc_d2ti = calc_axial_d2ti

            # Unit vectors.
            diff_data.dpar_unit_vector = zeros(3, Float64)

            # Unit vector gradient.
            diff_data.dpar_unit_vector_dtheta = zeros(3, Float64)
            diff_data.dpar_unit_vector_dphi = zeros(3, Float64)

        # Anisotropic diffusion.
        elif diff_type == 'aniso':
            # Number of diffusion parameters.
            diff_data.num_params = 6

            # Number of indecies in the generic equations.
            diff_data.num_indecies = 5

            # Geometry function, gradient, and Hessian.
            diff_data.calc_geom = calc_aniso_geom
            diff_data.calc_dgeom = calc_aniso_dgeom
            diff_data.calc_d2geom = calc_aniso_d2geom

            # Weight function, gradient, and Hessian.
            diff_data.calc_ci = calc_aniso_ci
            diff_data.calc_dci = calc_aniso_dci
            diff_data.calc_d2ci = calc_aniso_d2ci

            # Global correlation time function, gradient, and Hessian components.
            diff_data.calc_ti_comps = calc_aniso_ti_comps
            diff_data.calc_dti_comps = calc_aniso_dti_comps
            diff_data.calc_d2ti_comps = calc_aniso_d2ti_comps

            # Global correlation time function, gradient, and Hessian.
            diff_data.calc_ti = calc_aniso_ti
            diff_data.calc_dti = calc_aniso_dti
            diff_data.calc_d2ti = calc_aniso_d2ti


    def init_res_data(self, data, diff_data):
        """Function for the initialisation of the residue specific data."""

        # Weights and global correlation time values.
        data.ci = zeros(diff_data.num_indecies, Float64)
        data.ti = zeros(diff_data.num_indecies, Float64)

        # Isotropic diffusion.
        if self.diff_data.type == 'iso':
            # Global correlation time gradient and Hessian.
            data.dti = zeros((1, diff_data.num_indecies), Float64)
            data.d2ti = zeros((1, 1, diff_data.num_indecies), Float64)

        # Axially symmetric diffusion.
        elif self.diff_data.type == 'axial':
            # Weight gradient and Hessian.
            data.dci = zeros((2, diff_data.num_indecies), Float64)
            data.d2ci = zeros((2, 2, diff_data.num_indecies), Float64)

            # Global correlation time gradient and Hessian.
            data.dti = zeros((2, diff_data.num_indecies), Float64)
            data.d2ti = zeros((2, 2, diff_data.num_indecies), Float64)

            # Dot product.
            data.delta = 0

            # Dot product gradient.
            data.ddelta_dtheta = zeros(3, Float64)
            data.ddelta_dphi = zeros(3, Float64)
            data.ddelta_dpsi = zeros(2, Float64)

        # Anisotropic diffusion.
        elif self.diff_data.type == 'aniso':
            # Weight gradient and Hessian.
            data.dci = zeros((6, diff_data.num_indecies), Float64)
            data.d2ci = zeros((6, 6, diff_data.num_indecies), Float64)

            # Global correlation time gradient and Hessian.
            data.dti = zeros((3, diff_data.num_indecies), Float64)
            data.d2ti = zeros((3, 3, diff_data.num_indecies), Float64)

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
        data.djw = zeros((data.num_frq, 5, data.total_num_params), Float64)
        data.d2jw = zeros((data.num_frq, 5, data.total_num_params, data.total_num_params), Float64)

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
        data.dip_jw_comps_grad = zeros((data.num_ri, data.total_num_params), Float64)
        data.csa_jw_comps_grad = zeros((data.num_ri, data.total_num_params), Float64)

        # First partial derivative components of the transformed relaxation equations.
        data.dip_comps_hess = zeros((data.num_ri), Float64)
        data.csa_comps_hess = zeros((data.num_ri), Float64)
        data.rex_comps_hess = zeros((data.num_ri), Float64)
        data.dip_jw_comps_hess = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)
        data.csa_jw_comps_hess = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)

        # Transformed relaxation values, gradients, and Hessians.
        data.ri_prime = zeros((data.num_ri), Float64)
        data.dri_prime = zeros((data.num_ri, data.total_num_params), Float64)
        data.d2ri_prime = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)

        # Data structures containing the Ri values.
        data.ri = zeros((data.num_ri), Float64)
        data.dri = zeros((data.num_ri, data.total_num_params), Float64)
        data.d2ri = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)

        # Data structures containing the R1 values at the position of and corresponding to the NOE.
        data.r1 = zeros((data.num_ri), Float64)
        data.dr1 = zeros((data.num_ri, data.total_num_params), Float64)
        data.d2r1 = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)

        # Data structures containing the chi-squared values.
        data.chi2 = 0.0
        data.dchi2 = zeros((data.total_num_params), Float64)
        data.d2chi2 = zeros((data.total_num_params, data.total_num_params), Float64)


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
        r1_data.dip_jw_comps_grad = zeros((data.num_ri, data.total_num_params), Float64)
        r1_data.csa_jw_comps_grad = zeros((data.num_ri, data.total_num_params), Float64)

        # Initialise the first partial derivative components of the transformed relaxation equations.
        r1_data.dip_comps_hess = zeros(data.num_ri, Float64)
        r1_data.csa_comps_hess = zeros(data.num_ri, Float64)
        r1_data.rex_comps_hess = zeros(data.num_ri, Float64)
        r1_data.dip_jw_comps_hess = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)
        r1_data.csa_jw_comps_hess = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)

        # Initialise the transformed relaxation values, gradients, and Hessians.
        r1_data.ri_prime = zeros(data.num_ri, Float64)
        r1_data.dri_prime = zeros((data.num_ri, data.total_num_params), Float64)
        r1_data.d2ri_prime = zeros((data.num_ri, data.total_num_params, data.total_num_params), Float64)

        # Place a few function arrays in the data class for the calculation of the R1 value when an NOE data set exists but the R1 set does not.
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


    def pack_diff_params_iso(self):
        """Function for extracting the iso diffusion parameters from the parameter vector."""

        self.diff_data.params = self.params[0:1]


    def pack_diff_params_axial(self):
        """Function for extracting the axial diffusion parameters from the parameter vector."""

        self.diff_data.params = self.params[0:4]


    def pack_diff_params_aniso(self):
        """Function for extracting the aniso diffusion parameters from the parameter vector."""

        self.diff_data.params = self.params[0:6]


    def scale_gradient(self, dchi2):
        """Function for the diagonal scaling of the chi-squared gradient."""

        return matrixmultiply(dchi2, self.scaling_matrix)


    def scale_hessian(self, d2chi2):
        """Function for the diagonal scaling of the chi-squared Hessian."""

        return matrixmultiply(self.scaling_matrix, matrixmultiply(d2chi2, self.scaling_matrix))


    def set_params_scaled(self, params):
        """Function for setting self.params to the parameter vector times the scaling vector."""

        self.params = matrixmultiply(params, self.scaling_matrix)


    def set_params_unscaled(self, params):
        """Function for setting self.params to the parameter vector."""

        self.params = params * 1.0


    def setup_equations(self, data):
        """Setup all the residue specific equations."""

        # Initialisation.
        #################

        # The number of diffusion parameters.
        if self.param_set == 'mf':
            num_diff_params = 0
        elif self.diff_data.type == 'iso':
            num_diff_params = 1
        elif self.diff_data.type == 'axial':
            num_diff_params = 4
        elif self.diff_data.type == 'aniso':
            num_diff_params = 6

        # Indecies.
        data.tm_index, data.tm_local_index = None, None
        data.s2_index, data.s2_local_index = None, None
        data.s2f_index, data.s2f_local_index = None, None
        data.s2s_index, data.s2s_local_index = None, None
        data.te_index, data.te_local_index = None, None
        data.tf_index, data.tf_local_index = None, None
        data.ts_index, data.ts_local_index = None, None
        data.rex_index, data.rex_local_index = None, None
        data.r_index, data.r_local_index = None, None
        data.csa_index, data.csa_local_index = None, None

        # Set up the spectral density functions.
        ########################################

        # Create empty spectral density gradient and Hessian function data structures.
        data.calc_djw = []
        data.calc_d2jw = []
        for i in xrange(data.total_num_params):
            data.calc_djw.append(None)
            data.calc_d2jw.append([])
            for j in xrange(data.total_num_params):
                data.calc_d2jw[i].append(None)


        # The original model-free equations {S2, te, Rex, r, CSA}.
        ##########################################################

        if data.equations == 'mf_orig':
            # Find the indecies of the model-free parameters.
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2':
                    data.s2_local_index = num_diff_params + i
                    data.s2_index = self.param_index + i
                elif data.param_types[i] == 'te':
                    data.te_local_index = num_diff_params + i
                    data.te_index = self.param_index + i
                elif data.param_types[i] == 'Rex':
                    data.rex_local_index = num_diff_params + i
                    data.rex_index = self.param_index + i
                elif data.param_types[i] == 'r':
                    data.r_local_index = num_diff_params + i
                    data.r_index = self.param_index + i
                elif data.param_types[i] == 'CSA':
                    data.csa_local_index = num_diff_params + i
                    data.csa_index = self.param_index + i
                else:
                    print "Unknown parameter."
                    return 0

            # Increment the parameter index.
            self.param_index = self.param_index + data.num_params

            # Single residue minimisation with fixed diffusion parameters.
            if self.param_set == 'mf':
                # No model-free parameters {}.
                if data.s2_index == None and data.te_index == None:
                    # Equation.
                    data.calc_jw_comps = None
                    data.calc_jw = calc_jw

                    # Gradient.
                    data.calc_djw_comps = None

                # Model-free parameters {S2}.
                elif data.s2_index != None and data.te_index == None:
                    # Equation.
                    data.calc_jw_comps = None
                    data.calc_jw = calc_S2_jw

                    # Gradient.
                    data.calc_djw_comps = None
                    data.calc_djw[data.s2_local_index] = calc_S2_djw_dS2

                # Model-free parameters {S2, te}.
                elif data.s2_index != None and data.te_index != None:
                    # Equation.
                    data.calc_jw_comps = calc_S2_te_jw_comps
                    data.calc_jw = calc_S2_te_jw

                    # Gradient.
                    data.calc_djw_comps = calc_S2_te_djw_comps
                    data.calc_djw[data.s2_local_index] = calc_S2_te_djw_dS2
                    data.calc_djw[data.te_local_index] = calc_S2_te_djw_dte

                    # Hessian.
                    data.calc_d2jw[data.s2_local_index][data.te_local_index] = data.calc_d2jw[data.te_local_index][data.s2_local_index] = calc_S2_te_d2jw_dS2dte
                    data.calc_d2jw[data.te_local_index][data.te_local_index] = calc_S2_te_d2jw_dte2

                # Bad parameter combination.
                else:
                    print "Invalid combination of parameters for the extended model-free equation."
                    return 0

            # Minimisation with variable diffusion parameters.
            else:
                # Diffusion parameters and no model-free parameters {}.
                if data.s2_index == None and data.te_index == None:
                    # Equation.
                    data.calc_jw_comps = None
                    data.calc_jw = calc_jw

                    # Gradient.
                    data.calc_djw_comps = calc_tm_djw_comps
                    data.calc_djw[0] = calc_tm_djw_dDj

                    # Hessian.
                    data.calc_d2jw[0][0] = calc_tm_d2jw_dDjdDk
                    #if self.diff_data.type == 'iso':
                    #    data.calc_d2jw[0][0] = calc_tm_d2jw_dDjdDk
                    #elif self.diff_data.type == 'axial':
                    #    data.calc_d2jw[0][0] = calc_tm_d2jw_dDjdDk
                    #    data.calc_d2jw[0][1] = data.calc_d2jw[1][0] = calc_tm_d2jw_dDjdDk
                    #    data.calc_d2jw[1][1] = calc_tm_d2jw_dDjdDk

                # Diffusion parameters and model-free parameters {S2}.
                elif data.s2_index != None and data.te_index == None:
                    # Equation.
                    data.calc_jw_comps = None
                    data.calc_jw = calc_S2_jw

                    # Gradient.
                    data.calc_djw_comps = calc_tm_djw_comps
                    data.calc_djw[0] = calc_tm_S2_djw_dDj
                    data.calc_djw[data.s2_local_index] = calc_S2_djw_dS2

                    # Hessian.
                    data.calc_d2jw[0][0] = calc_tm_S2_d2jw_dDjdDk
                    data.calc_d2jw[0][data.s2_local_index] = data.calc_d2jw[data.s2_local_index][0] = calc_tm_S2_d2jw_dDjdS2

                # Diffusion parameters and model-free parameters {S2, te}.
                elif data.s2_index != None and data.te_index != None:
                    # Equation.
                    data.calc_jw_comps = calc_S2_te_jw_comps
                    data.calc_jw = calc_S2_te_jw

                    # Gradient.
                    data.calc_djw_comps = calc_tm_S2_te_djw_comps
                    data.calc_djw[0] = calc_tm_S2_te_djw_dDj
                    data.calc_djw[data.s2_local_index] = calc_S2_te_djw_dS2
                    data.calc_djw[data.te_local_index] = calc_S2_te_djw_dte

                    # Hessian.
                    data.calc_d2jw[0][0] = calc_tm_S2_te_d2jw_dDjdDk
                    data.calc_d2jw[0][data.s2_local_index] = data.calc_d2jw[data.s2_local_index][0] = calc_tm_S2_te_d2jw_dDjdS2
                    data.calc_d2jw[0][data.te_local_index] = data.calc_d2jw[data.te_local_index][0] = calc_tm_S2_te_d2jw_dDjdte
                    data.calc_d2jw[data.s2_local_index][data.te_local_index] = data.calc_d2jw[data.te_local_index][data.s2_local_index] = calc_S2_te_d2jw_dS2dte
                    data.calc_d2jw[data.te_local_index][data.te_local_index] = calc_S2_te_d2jw_dte2

                # Bad parameter combination.
                else:
                    print "Invalid combination of parameters for the extended model-free equation."
                    return 0



        # The extended model-free equations {S2f, tf, S2, ts, Rex, r, CSA}.
        ###################################################################

        elif data.equations == 'mf_ext':
            # Find the indecies of the model-free parameters.
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2f':
                    data.s2f_local_index = num_diff_params + i
                    data.s2f_index = self.param_index + i
                elif data.param_types[i] == 'tf':
                    data.tf_local_index = num_diff_params + i
                    data.tf_index = self.param_index + i
                elif data.param_types[i] == 'S2':
                    data.s2_local_index = num_diff_params + i
                    data.s2_index = self.param_index + i
                elif data.param_types[i] == 'ts':
                    data.ts_local_index = num_diff_params + i
                    data.ts_index = self.param_index + i
                elif data.param_types[i] == 'Rex':
                    data.rex_local_index = num_diff_params + i
                    data.rex_index = self.param_index + i
                elif data.param_types[i] == 'r':
                    data.r_local_index = num_diff_params + i
                    data.r_index = self.param_index + i
                elif data.param_types[i] == 'CSA':
                    data.csa_local_index = num_diff_params + i
                    data.csa_index = self.param_index + i
                else:
                    print "Unknown parameter."
                    return 0

            # Increment the parameter index.
            self.param_index = self.param_index + data.num_params

            # Model-free parameters {S2f, S2, ts}.
            if self.param_set == 'mf' and data.s2f_index != None and data.tf_index == None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_S2_ts_jw_comps
                data.calc_jw = calc_S2f_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_S2_ts_djw_comps
                data.calc_djw[data.s2f_local_index] = calc_S2f_S2_ts_djw_dS2f
                data.calc_djw[data.s2_local_index] = calc_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_local_index] = calc_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2_local_index] = calc_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_S2f_S2_ts_d2jw_dts2

            # Model-free parameters {S2f, tf, S2, ts}.
            elif self.param_set == 'mf' and data.s2f_index != None and data.tf_index != None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_tf_S2_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_tf_S2_ts_djw_comps
                data.calc_djw[data.s2f_local_index] = calc_S2f_tf_S2_ts_djw_dS2f
                data.calc_djw[data.tf_local_index] = calc_S2f_tf_S2_ts_djw_dtf
                data.calc_djw[data.s2_local_index] = calc_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_local_index] = calc_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_local_index][data.tf_local_index] = data.calc_d2jw[data.tf_local_index][data.s2f_local_index] = calc_S2f_tf_S2_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2_local_index] = calc_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.tf_local_index][data.tf_local_index] = calc_S2f_tf_S2_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_S2f_S2_ts_d2jw_dts2

            # Diffusion parameters and model-free parameters {S2f, S2, ts}.
            elif data.s2f_index != None and data.tf_index == None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_S2_ts_jw_comps
                data.calc_jw = calc_S2f_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_S2_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_S2_ts_djw_dDj
                data.calc_djw[data.s2f_local_index] = calc_S2f_S2_ts_djw_dS2f
                data.calc_djw[data.s2_local_index] = calc_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_local_index] = calc_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_S2_ts_d2jw_dDjdDk
                data.calc_d2jw[0][data.s2f_local_index] = data.calc_d2jw[data.s2f_local_index][0] = calc_tm_S2f_S2_ts_d2jw_dDjdS2f
                data.calc_d2jw[0][data.s2_local_index] = data.calc_d2jw[data.s2_local_index][0] = calc_tm_S2f_S2_ts_d2jw_dDjdS2
                data.calc_d2jw[0][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][0] = calc_tm_S2f_S2_ts_d2jw_dDjdts
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2_local_index] = calc_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_S2f_S2_ts_d2jw_dts2

            # Diffusion parameters and model-free parameters {S2f, tf, S2, ts}.
            elif data.s2f_index != None and data.tf_index != None and data.s2_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_tf_S2_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_tf_S2_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_tf_S2_ts_djw_dDj
                data.calc_djw[data.s2f_local_index] = calc_S2f_tf_S2_ts_djw_dS2f
                data.calc_djw[data.tf_local_index] = calc_S2f_tf_S2_ts_djw_dtf
                data.calc_djw[data.s2_local_index] = calc_S2f_S2_ts_djw_dS2
                data.calc_djw[data.ts_local_index] = calc_S2f_S2_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_tf_S2_ts_d2jw_dDjdDk
                data.calc_d2jw[0][data.s2f_local_index] = data.calc_d2jw[data.s2f_local_index][0] = calc_tm_S2f_S2_ts_d2jw_dDjdS2f
                data.calc_d2jw[0][data.s2_local_index] = data.calc_d2jw[data.s2_local_index][0] = calc_tm_S2f_S2_ts_d2jw_dDjdS2
                data.calc_d2jw[0][data.tf_local_index] = data.calc_d2jw[data.tf_local_index][0] = calc_tm_S2f_tf_S2_ts_d2jw_dDjdtf
                data.calc_d2jw[0][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][0] = calc_tm_S2f_S2_ts_d2jw_dDjdts
                data.calc_d2jw[data.s2f_local_index][data.tf_local_index] = data.calc_d2jw[data.tf_local_index][data.s2f_local_index] = calc_S2f_tf_S2_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_S2f_S2_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2_local_index] = calc_S2f_S2_ts_d2jw_dS2dts
                data.calc_d2jw[data.tf_local_index][data.tf_local_index] = calc_S2f_tf_S2_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_S2f_S2_ts_d2jw_dts2

            # Bad parameter combination.
            else:
                print "Invalid combination of parameters for the extended model-free equation."
                return 0


        # The extended 2 model-free equations {tm, S2f, tf, S2s, ts, Rex, r, CSA}.
        #########################################################################

        elif data.equations == 'mf_ext2':
            # Find the indecies of the model-free parameters.
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2f':
                    data.s2f_local_index = num_diff_params + i
                    data.s2f_index = self.param_index + i
                elif data.param_types[i] == 'tf':
                    data.tf_local_index = num_diff_params + i
                    data.tf_index = self.param_index + i
                elif data.param_types[i] == 'S2s':
                    data.s2s_local_index = num_diff_params + i
                    data.s2s_index = self.param_index + i
                elif data.param_types[i] == 'ts':
                    data.ts_local_index = num_diff_params + i
                    data.ts_index = self.param_index + i
                elif data.param_types[i] == 'Rex':
                    data.rex_local_index = num_diff_params + i
                    data.rex_index = self.param_index + i
                elif data.param_types[i] == 'r':
                    data.r_local_index = num_diff_params + i
                    data.r_index = self.param_index + i
                elif data.param_types[i] == 'CSA':
                    data.csa_local_index = num_diff_params + i
                    data.csa_index = self.param_index + i
                else:
                    print "Unknown parameter."
                    return 0

            # Increment the parameter index.
            self.param_index = self.param_index + data.num_params

            # Model-free parameters {S2f, S2s, ts}.
            if self.param_set == 'mf' and data.s2f_index != None and data.tf_index == None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_S2s_ts_djw_comps
                data.calc_djw[data.s2f_local_index] = calc_S2f_S2s_ts_djw_dS2f
                data.calc_djw[data.s2s_local_index] = calc_S2f_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_local_index] = calc_S2f_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_S2f_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2s_local_index] = calc_S2f_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_S2f_S2s_ts_d2jw_dts2

            # Model-free parameters {S2f, tf, S2s, ts}.
            elif self.param_set == 'mf' and data.s2f_index != None and data.tf_index != None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_S2f_tf_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_S2f_tf_S2s_ts_djw_comps
                data.calc_djw[data.s2f_local_index] = calc_S2f_tf_S2s_ts_djw_dS2f
                data.calc_djw[data.tf_local_index] = calc_S2f_tf_S2s_ts_djw_dtf
                data.calc_djw[data.s2s_local_index] = calc_S2f_tf_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_local_index] = calc_S2f_tf_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[data.s2f_local_index][data.tf_local_index] = data.calc_d2jw[data.tf_local_index][data.s2f_local_index] = calc_S2f_tf_S2s_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_S2f_tf_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2s_local_index] = calc_S2f_tf_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.tf_local_index][data.tf_local_index] = calc_S2f_tf_S2s_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_S2f_tf_S2s_ts_d2jw_dts2

            # Diffusion parameters and model-free parameters {S2f, S2s, ts}.
            elif data.s2f_index != None and data.tf_index == None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2f_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_S2s_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_S2s_ts_djw_dDj
                data.calc_djw[data.s2f_local_index] = calc_tm_S2f_S2s_ts_djw_dS2f
                data.calc_djw[data.s2s_local_index] = calc_tm_S2f_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_local_index] = calc_tm_S2f_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_S2s_ts_d2jw_dDjdDk
                data.calc_d2jw[0][data.s2f_local_index] = data.calc_d2jw[data.s2f_local_index][0] = calc_tm_S2f_S2s_ts_d2jw_dDjdS2f
                data.calc_d2jw[0][data.s2s_local_index] = data.calc_d2jw[data.s2s_local_index][0] = calc_tm_S2f_S2s_ts_d2jw_dDjdS2s
                data.calc_d2jw[0][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][0] = calc_tm_S2f_S2s_ts_d2jw_dDjdts
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_tm_S2f_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2s_local_index] = calc_tm_S2f_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_tm_S2f_S2s_ts_d2jw_dts2

            # Diffusion parameters and model-free parameters {S2f, tf, S2s, ts}.
            elif data.s2f_index != None and data.tf_index != None and data.s2s_index != None and data.ts_index != None:
                # Equation.
                data.calc_jw_comps = calc_tm_S2f_tf_S2s_ts_jw_comps
                data.calc_jw = calc_S2f_tf_S2s_ts_jw

                # Gradient.
                data.calc_djw_comps = calc_tm_S2f_tf_S2s_ts_djw_comps
                data.calc_djw[0] = calc_tm_S2f_tf_S2s_ts_djw_dDj
                data.calc_djw[data.s2f_local_index] = calc_tm_S2f_tf_S2s_ts_djw_dS2f
                data.calc_djw[data.tf_local_index] = calc_tm_S2f_tf_S2s_ts_djw_dtf
                data.calc_djw[data.s2s_local_index] = calc_tm_S2f_tf_S2s_ts_djw_dS2s
                data.calc_djw[data.ts_local_index] = calc_tm_S2f_tf_S2s_ts_djw_dts

                # Hessian.
                data.calc_d2jw[0][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dDjdDk
                data.calc_d2jw[0][data.s2f_local_index] = data.calc_d2jw[data.s2f_local_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dDjdS2f
                data.calc_d2jw[0][data.s2s_local_index] = data.calc_d2jw[data.s2s_local_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dDjdS2s
                data.calc_d2jw[0][data.tf_local_index] = data.calc_d2jw[data.tf_local_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dDjdtf
                data.calc_d2jw[0][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][0] = calc_tm_S2f_tf_S2s_ts_d2jw_dDjdts
                data.calc_d2jw[data.s2f_local_index][data.tf_local_index] = data.calc_d2jw[data.tf_local_index][data.s2f_local_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2fdtf
                data.calc_d2jw[data.s2f_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2f_local_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2fdts
                data.calc_d2jw[data.s2s_local_index][data.ts_local_index] = data.calc_d2jw[data.ts_local_index][data.s2s_local_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dS2sdts
                data.calc_d2jw[data.tf_local_index][data.tf_local_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dtf2
                data.calc_d2jw[data.ts_local_index][data.ts_local_index] = calc_tm_S2f_tf_S2s_ts_d2jw_dts2

            # Bad parameter combination.
            else:
                print "Invalid combination of parameters for the extended model-free equation."
                return 0

        # Unknown model-free equation.
        else:
            print "Unknown model-free equation."
            return 0


        # Initialise function data structures.
        ######################################

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
        for i in xrange(data.total_num_params):
            # Residue specific parameter index.
            index = i - num_diff_params
            if index < 0:
                index = None

            # Rex.
            if index != None and data.param_types[index] == 'Rex':
                # Gradient.
                data.create_dri_prime.append(func_dri_drex_prime)

                # Hessian.
                data.create_d2ri_prime.append([])
                for j in xrange(data.total_num_params):
                    # Residue specific parameter index.
                    index2 = j - num_diff_params
                    if index2 < 0:
                        index2 = None

                    # Rex.
                    if index2 != None and data.param_types[index2] == 'Rex':
                        data.create_d2ri_prime[i].append(None)

                    # Bond length.
                    elif index2 != None and data.param_types[index2] == 'r':
                        data.create_d2ri_prime[i].append(None)

                    # CSA.
                    elif index2 != None and data.param_types[index2] == 'CSA':
                        data.create_d2ri_prime[i].append(None)

                    # Any other parameter.
                    else:
                        data.create_d2ri_prime[i].append(None)

            # Bond length.
            elif index != None and data.param_types[index] == 'r':
                # Gradient.
                data.create_dri_prime.append(func_dri_dr_prime)

                # Hessian.
                data.create_d2ri_prime.append([])
                for j in xrange(data.total_num_params):
                    # Residue specific parameter index.
                    index2 = j - num_diff_params
                    if index2 < 0:
                        index2 = None

                    # Rex.
                    if index2 != None and data.param_types[index2] == 'Rex':
                        data.create_d2ri_prime[i].append(None)

                    # Bond length.
                    elif index2 != None and data.param_types[index2] == 'r':
                        data.create_d2ri_prime[i].append(func_d2ri_dr2_prime)

                    # CSA.
                    elif index2 != None and data.param_types[index2] == 'CSA':
                        data.create_d2ri_prime[i].append(None)

                    # Any other parameter.
                    else:
                        data.create_d2ri_prime[i].append(func_d2ri_drdjw_prime)

            # CSA.
            elif index != None and data.param_types[index] == 'CSA':
                # Gradient.
                data.create_dri_prime.append(func_dri_dcsa_prime)

                # Hessian.
                data.create_d2ri_prime.append([])
                for j in xrange(data.total_num_params):
                    # Residue specific parameter index.
                    index2 = j - num_diff_params
                    if index2 < 0:
                        index2 = None

                    # Rex.
                    if index2 != None and data.param_types[index2] == 'Rex':
                        data.create_d2ri_prime[i].append(None)

                    # Bond length.
                    elif index2 != None and data.param_types[index2] == 'r':
                        data.create_d2ri_prime[i].append(None)

                    # CSA.
                    elif index2 != None and data.param_types[index2] == 'CSA':
                        data.create_d2ri_prime[i].append(func_d2ri_dcsa2_prime)

                    # Any other parameter.
                    else:
                        data.create_d2ri_prime[i].append(func_d2ri_dcsadjw_prime)

            # Any other parameter.
            else:
                # Gradient.
                data.create_dri_prime.append(func_dri_djw_prime)

                # Hessian.
                data.create_d2ri_prime.append([])
                for j in xrange(data.total_num_params):
                    # Residue specific parameter index.
                    index2 = j - num_diff_params
                    if index2 < 0:
                        index2 = None

                    # Rex.
                    if index2 != None and data.param_types[index2] == 'Rex':
                        data.create_d2ri_prime[i].append(None)

                    # Bond length.
                    elif index2 != None and data.param_types[index2] == 'r':
                        data.create_d2ri_prime[i].append(func_d2ri_djwdr_prime)

                    # CSA.
                    elif index2 != None and data.param_types[index2] == 'CSA':
                        data.create_d2ri_prime[i].append(func_d2ri_djwdcsa_prime)

                    # Any other parameter.
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
