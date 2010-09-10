###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from math import pi
from numpy import dot, float64, ones, sum, transpose, zeros

# relax module imports.
from relax_errors import RelaxError
from direction_cosine import *
from weights import *
from correlation_time import *
from jw_mf_comps import *
from jw_mf import *
from ri_comps import *
from ri_prime import *
from ri import *
from chi2 import *


class Mf:
    def __init__(self, init_params=None, model_type=None, diff_type=None, diff_params=None, scaling_matrix=None, num_spins=None, equations=None, param_types=None, param_values=None, relax_data=None, errors=None, num_interactions=None, interactions=None, internuclei_distance=None, csa=None, num_frq=0, frq=None, num_ri=None, remap_table=None, noe_r1_table=None, ri_labels=None, gx=0, gh=0, gratio_ext=0, h_bar=0, mu0=0, num_params=None, unit_vector=None):
        """The model-free minimisation class.

        This class should be initialised before every calculation.


        Arguments
        =========

        equation:  The model-free equation string which should be either 'mf_orig' or 'mf_ext'.

        param_types:  An array of the parameter types used in minimisation.

        relax_data:  An array containing the experimental relaxation values.

        errors:  An array containing the experimental errors.

        interactions: An array containing the types of interactions (either dipole-dipole or CSA).

        gratio_ext:  An array containing the gyromagnetic ratios of interacting nuclei (None is included
	in case of CSA interaction)

        internuclei_distance:  An array containing the fixed internuclei_distances in meters. 
	(None is included in case of CSA interaction)

        csa:  An array containing the fixed CSA value. (None is included in case of dipole-dipole
	interaction)

        unit_vector:  An array containing the fixed unit eigenvectors of interactions

        diff_type:  The diffusion tensor string which should be either 'sphere', 'spheroid', or
        'ellipsoid'.

        diff_params:  An array with the diffusion parameters.

        scaling_matrix:  A diagonal matrix of scaling factors.



        Additional layer of equations to simplify the relaxation equations, gradients, and Hessians.
        ============================================================================================

        The R1 and R2 equations are left alone, while the NOE is calculated from the R1 and
        sigma_noe values.


        The relaxation equations
        ========================

        Data structure:  data.ri
        Dimension:  1D, (relaxation data)
        Type:  numpy, float64
        Dependencies:  data.ri_prime
        Required by:  data.chi2, data.dchi2, data.d2chi2

        The equations are::

            R1()  =  R1'()


            R2()  =  R2'()

                           gH   sigma_noe()
            NOE()  =  1 +  -- . -----------
                           gN      R1()



        The relaxation gradients
        ========================

        Data structure:  data.dri
        Dimension:  2D, (parameters, relaxation data)
        Type:  numpy array, float64
        Dependencies:  data.ri_prime, data.dri_prime
        Required by:  data.dchi2, data.d2chi2

        The equations are::

             dR1()       dR1'()
            -------  =  -------
            dthetaj     dthetaj


             dR2()       dR2'()
            -------  =  -------
            dthetaj     dthetaj


             dNOE()     gH      1      /        dsigma_noe()                    dR1()  \ 
            -------  =  -- . ------- . | R1() . ------------  -  sigma_noe() . ------- |
            dthetaj     gN   R1()**2   \          dthetaj                      dthetaj /



        The relaxation Hessians
        =======================

        Data structure:  data.d2ri
        Dimension:  3D, (parameters, parameters, relaxation data)
        Type:  numpy array, float64
        Dependencies:  data.ri_prime, data.dri_prime, data.d2ri_prime
        Required by:  data.d2chi2

        The equations are::

                 d2R1()             d2R1'()
            ---------------  =  ---------------
            dthetai.dthetaj     dthetai.dthetaj


                 d2R2()             d2R2'()
            ---------------  =  ---------------
            dthetai.dthetaj     dthetai.dthetaj


                d2NOE()         gH      1      /               /      dR1()     dR1()                  d2R1()     \ 
            ---------------  =  -- . ------- . | sigma_noe() . | 2 . ------- . -------  -  R1() . --------------- |
            dthetai.dthetaj     gN   R1()**3   \               \     dthetai   dthetaj            dthetai.dthetaj /

                         / dsigma_noe()    dR1()       dR1()    dsigma_noe()             d2sigma_noe()  \ \ 
                - R1() . | ------------ . -------  +  ------- . ------------  -  R1() . --------------- | |
                         \   dthetai      dthetaj     dthetai     dthetaj               dthetai.dthetaj / /



        The chi-sqared equation
        =======================

        The equation is::
                    _n_
                    \    (Ri - Ri()) ** 2
            chi2  =  >   ----------------
                    /__    sigma_i ** 2
                    i=1

        where:
            - Ri are the values of the measured relaxation data set.
            - Ri() are the values of the back calculated relaxation data set.
            - sigma_i are the values of the error set.


        The chi-sqared gradient
        =======================

        The equation is::
                           _n_
             dchi2         \   /  Ri - Ri()      dRi()  \ 
            -------  =  -2  >  | ----------  .  ------- |
            dthetaj        /__ \ sigma_i**2     dthetaj /
                           i=1

        where:
            - Ri are the values of the measured relaxation data set.
            - Ri() are the values of the back calculated relaxation data set.
            - sigma_i are the values of the error set.


        The chi-sqared Hessian
        ======================

        The equation is::
                                 _n_
                 d2chi2          \       1      /  dRi()     dRi()                         d2Ri()     \ 
            ---------------  = 2  >  ---------- | ------- . -------  -  (Ri - Ri()) . --------------- |
            dthetaj.dthetak      /__ sigma_i**2 \ dthetaj   dthetak                   dthetaj.dthetak /
                                 i=1

        where:
            - Ri are the values of the measured relaxation data set.
            - Ri() are the values of the back calculated relaxation data set.
            - sigma_i are the values of the error set.
        """

        # Arguments.
        self.model_type = model_type
        self.total_num_params = len(init_params)
        self.scaling_matrix = scaling_matrix
        self.num_spins = num_spins
        self.params = 1.0 * init_params

        # Data structures for tests set to some random array (in this case all pi).
        self.func_test = pi * ones(self.total_num_params, float64)
        self.grad_test = pi * ones(self.total_num_params, float64)
        self.hess_test = pi * ones(self.total_num_params, float64)

        # Initialise the data class for storing diffusion tensor data.
        self.diff_data = Data()
        self.diff_data.type = diff_type
        self.diff_data.params = diff_params
        self.init_diff_data(self.diff_data)

        # Total number of ri.
        self.total_num_ri = 0

        # Set the function for packaging diffusion tensor parameters.
        if self.diff_data.type == 'sphere':
            self.param_index = 1
            self.diff_end_index = 1
        elif self.diff_data.type == 'spheroid':
            self.param_index = 4
            self.diff_end_index = 4
        elif self.diff_data.type == 'ellipsoid':
            self.param_index = 6
            self.diff_end_index = 6
        if self.model_type != 'all':
            self.param_index = 0

        # Create the data array used to store data.
        self.data = []
        for i in xrange(self.num_spins):
            # Total number of ri.
            self.total_num_ri = self.total_num_ri + num_ri[i]

            self.data.append([])

            # The ratio of gyromagnetic ratios.
            g_ratio = gh[i] / gx[i]


	    # loop over interactions
            for j in xrange(self.num_interactions[i]):
                self.data[i].append(Data())
                self.data[i][j].interactions=interactions[i][j]
                self.data[i][j].internuclei_distance=internuclei_distance[i][j]
                self.data[i][j].gratio_ext=gratio_ext[i][j]
                self.data[i][j].csa=csa[i][j]
                self.data[i][j].unit_vector=unit_vector[i][j]

                # Number of indices.
                self.data[i][j].num_indices = self.diff_data.num_indices

                # Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
                self.data[i][j].frq_list = zeros((num_frq[i], 5), float64)
                self.data[i][j].frq_list_ext = zeros((num_frq[i], 5, self.diff_data.num_indices), float64)
                self.data[i][j].frq_sqrd_list_ext = zeros((num_frq[i], 5, self.diff_data.num_indices), float64)
                for k in xrange(num_frq[i]):
                    frqH = 2.0 * pi * frq[i][k]
                    frqX = frqH / g_ratio
                    frqY = frqH * gratio_ext[i][j] / gh[i]
                    self.data[i][j].frq_list[k, 1] = frqX
                    self.data[i][j].frq_list[k, 2] = frqY - frqX
                    self.data[i][j].frq_list[k, 3] = frqY
                    self.data[i][j].frq_list[k, 4] = frqY + frqX
                self.data[i][j].frq_sqrd_list = self.data[i].frq_list ** 2
                for k in xrange(self.diff_data.num_indices):
                    self.data[i][j].frq_list_ext[:,:, k] = self.data[i][j].frq_list
                    self.data[i][j].frq_sqrd_list_ext[:,:, k] = self.data[i][j].frq_sqrd_list

	        

                # Store supplied data in self.data
                self.data[i][j].gh = gh[i]
                self.data[i][j].gx = gx[i]
                self.data[i][j].g_ratio = g_ratio
                self.data[i][j].h_bar = h_bar
                self.data[i][j].mu0 = mu0
                self.data[i][j].equations = equations[i]
                self.data[i][j].param_types = param_types[i]
                self.data[i][j].relax_data = relax_data[i]
                self.data[i][j].errors = errors[i]
                self.data[i][j].num_ri = num_ri[i]
                self.data[i][j].num_frq = num_frq[i]
                self.data[i][j].frq = frq[i]
                self.data[i][j].remap_table = remap_table[i]
                self.data[i][j].noe_r1_table = noe_r1_table[i]
                self.data[i][j].ri_labels = ri_labels[i]
                self.data[i][j].num_params = num_params[i]

                # Parameter values for minimising solely the diffusion tensor parameters.
                if self.model_type == 'diff':
                    self.data[i][j].param_values = param_values[i]

                # Indices for constructing the global generic model-free gradient and Hessian kite.
                if i == 0:
                    self.data[i][j].start_index = self.diff_data.num_params
                else:
                    self.data[i][j].start_index = self.data[i-1][0].end_index
                self.data[i][j].end_index = self.data[i][j].start_index + self.data[i][j].num_params

                # Total number of parameters.
                if self.model_type == 'mf' or self.model_type == 'local_tm':
                    self.data[i][j].total_num_params = self.data[i][j].num_params
                elif self.model_type == 'diff':
                    self.data[i][j].total_num_params = self.diff_data.num_params
                else:
                    self.data[i][j].total_num_params = self.data[i][j].num_params + self.diff_data.num_params

                # Initialise the residue specific data.
                self.init_res_data(self.data[i][j], self.diff_data)

                # Setup the residue specific equations.
                if not self.setup_equations(self.data[i][j]):
                    raise RelaxError("The model-free equations could not be setup.")

                # Diffusion tensor parameters.
                if self.model_type == 'local_tm':
                    self.diff_data.params = self.params[0:1]
                elif self.model_type == 'diff' or self.model_type == 'all':
                    self.diff_data.params = self.params[0:self.diff_end_index]

                # Calculate the correlation times ti.
                self.diff_data.calc_ti(self.data[i][j], self.diff_data)

                # ti spectral density components.
                self.data[i][j].w_ti_sqrd = self.data[i][j].frq_sqrd_list_ext * self.data[i][j].ti ** 2
                self.data[i][j].fact_ti = 1.0 / (1.0 + self.data[i][j].w_ti_sqrd)

                # Initialise the R1 data class.  This is used only if an NOE data set is collected but the R1 data of the same frequency has not.
                missing_r1 = 0
                for k in xrange(self.data[i][j].num_ri):
                    if self.data[i][j].ri_labels[k] == 'NOE' and self.data[i][j].noe_r1_table[k] == None:
                        missing_r1 = 1
                if missing_r1:
                    self.init_res_r1_data(self.data[i][j])

        # Scaling initialisation.
        if self.scaling_matrix != None:
            self.scaling_flag = 1
        else:
            self.scaling_flag = 0

        # Initialise the total chi2 value, gradient, and Hessian data structures.
        self.total_chi2 = 0.0
        self.total_dchi2 = zeros((self.total_num_params), float64)
        self.total_d2chi2 = zeros((self.total_num_params, self.total_num_params), float64)

        # Initialise the total ri gradient data structure (for Levenberg-Marquardt minimisation).
        self.total_dri = zeros((self.total_num_params, self.total_num_ri), float64)

        # Set the functions self.func, self.dfunc, and self.d2func.
        ###########################################################

        # Functions for minimising model-free parameters for a single residue.
        if self.model_type == 'mf':
            self.func = self.func_mf
            self.dfunc = self.dfunc_mf
            self.d2func = self.d2func_mf

        # Functions for minimising model-free parameters for a single residue with a local tm.
        elif self.model_type == 'local_tm':
            self.func = self.func_local_tm
            self.dfunc = self.dfunc_local_tm
            self.d2func = self.d2func_local_tm

        # Functions for minimising diffusion tensor parameters with all model-free parameters fixed.
        elif self.model_type == 'diff':
            self.func = self.func_diff
            self.dfunc = self.dfunc_diff
            self.d2func = self.d2func_diff

        # Functions for minimising diffusion tensor parameters together with all model-free parameters.
        elif self.model_type == 'all':
            self.func = self.func_all
            self.dfunc = self.dfunc_all
            self.d2func = self.d2func_all


    def func_mf(self, params):
        """Function for calculating the chi-squared value.

        Used in the minimisation of model-free parameters for a single residue.
        """

        # Store the parameter values in self.func_test for testing.
        self.func_test = params * 1.0

        # Set self.data[0] to data.
        data = self.data[0]

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Direction cosine calculations.
        if self.diff_data.calc_di:
            self.diff_data.calc_di(data, self.diff_data)

        # Diffusion tensor weight calculations.
        self.diff_data.calc_ci(data, self.diff_data)

        # Diffusion tensor correlation times.
        self.diff_data.calc_ti(data, self.diff_data)

        # Calculate the components of the spectral densities.
        if data.calc_jw_comps:
            data.calc_jw_comps(data, params)

        # Calculate the spectral density values.
        data.jw = data.calc_jw(data, params)

        # Calculate the relaxation formula components.
        data.create_ri_comps(data, params)

        # Calculate the R1, R2, and sigma_noe values.
        data.ri_prime = data.create_ri_prime(data)

        # Calculate the NOE values.
        data.ri = data.ri_prime * 1.0
        for m in xrange(data.num_ri):
            if data.create_ri[m]:
                data.create_ri[m](data, m, data.remap_table[m], data.get_r1, params)

        # Calculate the chi-squared value.
        data.chi2 = chi2(data.relax_data, data.ri, data.errors)

        return data.chi2


    def func_local_tm(self, params):
        """Function for calculating the chi-squared value.

        Used in the minimisation of model-free parameters for a single residue with a local tm.
        """

        # Store the parameter values in self.func_test for testing.
        self.func_test = params * 1.0

        # Set self.data[0] to data.
        data = self.data[0]

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:1]

        # Diffusion tensor weight calculations.
        self.diff_data.calc_ci(data, self.diff_data)

        # Diffusion tensor correlation times.
        self.diff_data.calc_ti(data, self.diff_data)

        # ti spectral density components.
        data.w_ti_sqrd = data.frq_sqrd_list_ext * data.ti ** 2
        data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

        # Calculate the components of the spectral densities.
        if data.calc_jw_comps:
            data.calc_jw_comps(data, params)

        # Calculate the spectral density values.
        data.jw = data.calc_jw(data, params)

        # Calculate the relaxation formula components.
        data.create_ri_comps(data, params)

        # Calculate the R1, R2, and sigma_noe values.
        data.ri_prime = data.create_ri_prime(data)

        # Calculate the NOE values.
        data.ri = data.ri_prime * 1.0
        for m in xrange(data.num_ri):
            if data.create_ri[m]:
                data.create_ri[m](data, m, data.remap_table[m], data.get_r1, params)

        # Calculate the chi-squared value.
        data.chi2 = chi2(data.relax_data, data.ri, data.errors)

        return data.chi2


    def func_diff(self, params):
        """Function for calculating the chi-squared value.

        Used in the minimisation of diffusion tensor parameters with all model-free parameters
        fixed.
        """

        # Store the parameter values in self.func_test for testing.
        self.func_test = params * 1.0

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:self.diff_end_index]

        # Set the total chi2 to zero.
        self.total_chi2 = 0.0

        # Loop over the residues.
        for i in xrange(self.num_spins):
            # Set self.data[i] to data.
            data = self.data[i]

            # Direction cosine calculations.
            if self.diff_data.calc_di:
                self.diff_data.calc_di(data, self.diff_data)

            # Diffusion tensor weight calculations.
            self.diff_data.calc_ci(data, self.diff_data)

            # Diffusion tensor correlation times.
            self.diff_data.calc_ti(data, self.diff_data)

            # ti spectral density components.
            data.w_ti_sqrd = data.frq_sqrd_list_ext * data.ti ** 2
            data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

            # Calculate the components of the spectral densities.
            if data.calc_jw_comps:
                data.calc_jw_comps(data, data.param_values)

            # Calculate the spectral density values.
            data.jw = data.calc_jw(data, data.param_values)

            # Calculate the relaxation formula components.
            data.create_ri_comps(data, data.param_values)

            # Calculate the R1, R2, and sigma_noe values.
            data.ri_prime = data.create_ri_prime(data)

            # Calculate the NOE values.
            data.ri = data.ri_prime * 1.0
            for m in xrange(data.num_ri):
                if data.create_ri[m]:
                    data.create_ri[m](data, m, data.remap_table[m], data.get_r1, data.param_values)

            # Calculate the chi-squared value.
            data.chi2 = chi2(data.relax_data, data.ri, data.errors)

            # Add the residue specific chi2 to the total chi2.
            self.total_chi2 = self.total_chi2 + data.chi2

        return self.total_chi2


    def func_all(self, params):
        """Function for calculating the chi-squared value.

        Used in the minimisation of diffusion tensor parameters together with all model-free
        parameters.
        """

        # Store the parameter values in self.func_test for testing.
        self.func_test = params * 1.0

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:self.diff_end_index]

        # Set the total chi2 to zero.
        self.total_chi2 = 0.0

        # Loop over the residues.
        for i in xrange(self.num_spins):
            # Set self.data[i] to data.
            data = self.data[i]

            # Direction cosine calculations.
            if self.diff_data.calc_di:
                self.diff_data.calc_di(data, self.diff_data)

            # Diffusion tensor weight calculations.
            self.diff_data.calc_ci(data, self.diff_data)

            # Diffusion tensor correlation times.
            self.diff_data.calc_ti(data, self.diff_data)

            # ti spectral density components.
            data.w_ti_sqrd = data.frq_sqrd_list_ext * data.ti ** 2
            data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

            # Calculate the components of the spectral densities.
            if data.calc_jw_comps:
                data.calc_jw_comps(data, params)

            # Calculate the spectral density values.
            data.jw = data.calc_jw(data, params)

            # Calculate the relaxation formula components.
            data.create_ri_comps(data, params)

            # Calculate the R1, R2, and sigma_noe values.
            data.ri_prime = data.create_ri_prime(data)

            # Calculate the NOE values.
            data.ri = data.ri_prime * 1.0
            for m in xrange(data.num_ri):
                if data.create_ri[m]:
                    data.create_ri[m](data, m, data.remap_table[m], data.get_r1, params)

            # Calculate the chi-squared value.
            data.chi2 = chi2(data.relax_data, data.ri, data.errors)

            # Add the residue specific chi2 to the total chi2.
            self.total_chi2 = self.total_chi2 + data.chi2

        return self.total_chi2


    def dfunc_mf(self, params):
        """Function for calculating the chi-squared gradient.

        Used in the minimisation of model-free parameters for a single residue.
        """

        # Test if the function has already been called, otherwise run self.func.
        if sum(params == self.func_test) != self.total_num_params:
            self.func(params)

        # Store the parameter values in self.grad_test for testing.
        self.grad_test = params * 1.0

        # Set self.data[0] to data.
        data = self.data[0]

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Calculate the spectral density gradient components.
        if data.calc_djw_comps:
            data.calc_djw_comps(data, params)

        # Loop over the gradient.
        for j in xrange(data.total_num_params):
            # Calculate the spectral density gradients.
            if data.calc_djw[j]:
                data.djw = data.calc_djw[j](data, params, j)
            else:
                data.djw = data.djw * 0.0

            # Calculate the relaxation gradient components.
            data.create_dri_comps(data, params)

            # Calculate the R1, R2, and sigma_noe gradients.
            data.dri_prime[j] = data.create_dri_prime[j](data)

            # Loop over the relaxation values and modify the NOE gradients.
            data.dri[j] = data.dri_prime[j]
            for m in xrange(data.num_ri):
                if data.create_dri[m]:
                    data.create_dri[m](data, m, data.remap_table[m], data.get_dr1, params, j)

            # Calculate the chi-squared gradient.
            data.dchi2[j] = dchi2_element(data.relax_data, data.ri, data.dri[j], data.errors)

        # Diagonal scaling.
        if self.scaling_flag:
            data.dchi2 = dot(data.dchi2, self.scaling_matrix)

        # Return a copy of the gradient.
        return data.dchi2 * 1.0


    def dfunc_local_tm(self, params):
        """Function for calculating the chi-squared gradient.

        Used in the minimisation of model-free parameters for a single residue with a local tm.
        """

        # Test if the function has already been called, otherwise run self.func.
        if sum(params == self.func_test) != self.total_num_params:
            self.func(params)

        # Store the parameter values in self.grad_test for testing.
        self.grad_test = params * 1.0

        # Set self.data[0] to data.
        data = self.data[0]

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:1]

        # Calculate the spectral density gradient components.
        if data.calc_djw_comps:
            data.calc_djw_comps(data, params)

        # Diffusion tensor correlation times.
        self.diff_data.calc_dti(data, self.diff_data)

        # Loop over the gradient.
        for j in xrange(data.total_num_params):
            # Calculate the spectral density gradients.
            if data.calc_djw[j]:
                data.djw = data.calc_djw[j](data, params, j)
            else:
                data.djw = data.djw * 0.0

            # Calculate the relaxation gradient components.
            data.create_dri_comps(data, params)

            # Calculate the R1, R2, and sigma_noe gradients.
            data.dri_prime[j] = data.create_dri_prime[j](data)

            # Loop over the relaxation values and modify the NOE gradients.
            data.dri[j] = data.dri_prime[j]
            for m in xrange(data.num_ri):
                if data.create_dri[m]:
                    data.create_dri[m](data, m, data.remap_table[m], data.get_dr1, params, j)

            # Calculate the chi-squared gradient.
            data.dchi2[j] = dchi2_element(data.relax_data, data.ri, data.dri[j], data.errors)

        # Diagonal scaling.
        if self.scaling_flag:
            data.dchi2 = dot(data.dchi2, self.scaling_matrix)

        # Return a copy of the gradient.
        return data.dchi2 * 1.0


    def dfunc_diff(self, params):
        """Function for calculating the chi-squared gradient.

        Used in the minimisation of diffusion tensor parameters with all model-free parameters
        fixed.
        """

        # Test if the function has already been called, otherwise run self.func.
        if sum(params == self.func_test) != self.total_num_params:
            self.func(params)

        # Store the parameter values in self.grad_test for testing.
        self.grad_test = params * 1.0

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:self.diff_end_index]

        # Set the total chi2 gradient to zero.
        self.total_dchi2 = self.total_dchi2 * 0.0

        # Loop over the residues.
        for i in xrange(self.num_spins):

            # Set self.data[i] to data.
            data = self.data[i]

            # Direction cosine calculations.
            if self.diff_data.calc_ddi:
                self.diff_data.calc_ddi(data, self.diff_data)

            # Diffusion tensor weight calculations.
            if self.diff_data.calc_dci:
                self.diff_data.calc_dci(data, self.diff_data)

            # Diffusion tensor correlation times.
            self.diff_data.calc_dti(data, self.diff_data)

            # Calculate the spectral density gradient components.
            if data.calc_djw_comps:
                data.calc_djw_comps(data, data.param_values)

            # Loop over the gradient.
            for j in xrange(data.total_num_params):
                # Calculate the spectral density gradients.
                if data.calc_djw[j]:
                    data.djw = data.calc_djw[j](data, data.param_values, j)
                else:
                    data.djw = data.djw * 0.0

                # Calculate the relaxation gradient components.
                data.create_dri_comps(data, data.param_values)

                # Calculate the R1, R2, and sigma_noe gradients.
                data.dri_prime[j] = data.create_dri_prime[j](data)

                # Loop over the relaxation values and modify the NOE gradients.
                data.dri[j] = data.dri_prime[j]
                for m in xrange(data.num_ri):
                    if data.create_dri[m]:
                        data.create_dri[m](data, m, data.remap_table[m], data.get_dr1, params, j)

                # Calculate the chi-squared gradient.
                data.dchi2[j] = dchi2_element(data.relax_data, data.ri, data.dri[j], data.errors)

            # Index for the construction of the global generic model-free gradient.
            index = self.diff_data.num_params

            # Diffusion parameter part of the global generic model-free gradient.
            self.total_dchi2[0:index] = self.total_dchi2[0:index] + data.dchi2[0:index]

        # Diagonal scaling.
        if self.scaling_flag:
            self.total_dchi2 = dot(self.total_dchi2, self.scaling_matrix)

        # Return a copy of the gradient.
        return self.total_dchi2 * 1.0


    def dfunc_all(self, params):
        """Function for calculating the chi-squared gradient.

        Used in the minimisation of diffusion tensor parameters together with all model-free
        parameters.
        """

        # Test if the function has already been called, otherwise run self.func.
        if sum(params == self.func_test) != self.total_num_params:
            self.func(params)

        # Store the parameter values in self.grad_test for testing.
        self.grad_test = params * 1.0

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:self.diff_end_index]

        # Set the total chi2 gradient to zero.
        self.total_dchi2 = self.total_dchi2 * 0.0

        # Loop over the residues.
        for i in xrange(self.num_spins):
            # Set self.data[i] to data.
            data = self.data[i]

            # Direction cosine calculations.
            if self.diff_data.calc_ddi:
                self.diff_data.calc_ddi(data, self.diff_data)

            # Diffusion tensor weight calculations.
            if self.diff_data.calc_dci:
                self.diff_data.calc_dci(data, self.diff_data)

            # Diffusion tensor correlation times.
            self.diff_data.calc_dti(data, self.diff_data)

            # Calculate the spectral density gradient components.
            if data.calc_djw_comps:
                data.calc_djw_comps(data, params)

            # Loop over the gradient.
            for j in xrange(data.total_num_params):
                # Calculate the spectral density gradients.
                if data.calc_djw[j]:
                    data.djw = data.calc_djw[j](data, params, j)
                else:
                    data.djw = data.djw * 0.0

                # Calculate the relaxation gradient components.
                data.create_dri_comps(data, params)

                # Calculate the R1, R2, and sigma_noe gradients.
                data.dri_prime[j] = data.create_dri_prime[j](data)

                # Loop over the relaxation values and modify the NOE gradients.
                data.dri[j] = data.dri_prime[j]
                for m in xrange(data.num_ri):
                    if data.create_dri[m]:
                        data.create_dri[m](data, m, data.remap_table[m], data.get_dr1, params, j)

                # Calculate the chi-squared gradient.
                data.dchi2[j] = dchi2_element(data.relax_data, data.ri, data.dri[j], data.errors)

            # Index for the construction of the global generic model-free gradient.
            index = self.diff_data.num_params

            # Diffusion parameter part of the global generic model-free gradient.
            self.total_dchi2[0:index] = self.total_dchi2[0:index] + data.dchi2[0:index]

            # Model-free parameter part of the global generic model-free gradient.
            self.total_dchi2[data.start_index:data.end_index] = self.total_dchi2[data.start_index:data.end_index] + data.dchi2[index:]

        # Diagonal scaling.
        if self.scaling_flag:
            self.total_dchi2 = dot(self.total_dchi2, self.scaling_matrix)

        # Return a copy of the gradient.
        return self.total_dchi2 * 1.0


    def d2func_mf(self, params):
        """Function for calculating the chi-squared Hessian.

        Used in the minimisation of model-free parameters for a single residue.
        """

        # Test if the gradient has already been called, otherwise run self.dfunc.
        if sum(params == self.grad_test) != self.total_num_params:
            self.dfunc(params)

        # Set self.data[0] to data.
        data = self.data[0]

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Loop over the lower triangle of the Hessian.
        for j in xrange(data.total_num_params):
            for k in xrange(j + 1):
                # Calculate the spectral density Hessians.
                if data.calc_d2jw[j][k]:
                    data.d2jw = data.calc_d2jw[j][k](data, params, j, k)
                else:
                    data.d2jw = data.d2jw * 0.0

                # Calculate the relaxation Hessian components.
                data.create_d2ri_comps(data, params)

                # Calculate the R1, R2, and sigma_noe Hessians.
                if data.create_d2ri_prime[j][k]:
                    data.d2ri_prime[j, k] = data.create_d2ri_prime[j][k](data)

                # Loop over the relaxation values and modify the NOE Hessians.
                data.d2ri[j, k] = data.d2ri_prime[j, k]
                for m in xrange(data.num_ri):
                    if data.create_d2ri[m]:
                        data.create_d2ri[m](data, m, data.remap_table[m], data.get_d2r1, params, j, k)

                # Calculate the chi-squared Hessian.
                data.d2chi2[j, k] = data.d2chi2[k, j] = d2chi2_element(data.relax_data, data.ri, data.dri[j], data.dri[k], data.d2ri[j, k], data.errors)

        # Diagonal scaling.
        if self.scaling_flag:
            data.d2chi2 = dot(self.scaling_matrix, dot(data.d2chi2, self.scaling_matrix))

        # Return a copy of the Hessian.
        return data.d2chi2 * 1.0


    def d2func_local_tm(self, params):
        """Function for calculating the chi-squared Hessian.

        Used in the minimisation of model-free parameters for a single residue with a local tm.
        """

        # Test if the gradient has already been called, otherwise run self.dfunc.
        if sum(params == self.grad_test) != self.total_num_params:
            self.dfunc(params)

        # Set self.data[0] to data.
        data = self.data[0]

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:1]

        # Loop over the lower triangle of the Hessian.
        for j in xrange(data.total_num_params):
            for k in xrange(j + 1):
                # Calculate the spectral density Hessians.
                if data.calc_d2jw[j][k]:
                    data.d2jw = data.calc_d2jw[j][k](data, params, j, k)
                else:
                    data.d2jw = data.d2jw * 0.0

                # Calculate the relaxation Hessian components.
                data.create_d2ri_comps(data, params)

                # Calculate the R1, R2, and sigma_noe Hessians.
                if data.create_d2ri_prime[j][k]:
                    data.d2ri_prime[j, k] = data.create_d2ri_prime[j][k](data)

                # Loop over the relaxation values and modify the NOE Hessians.
                data.d2ri[j, k] = data.d2ri_prime[j, k]
                for m in xrange(data.num_ri):
                    if data.create_d2ri[m]:
                        data.create_d2ri[m](data, m, data.remap_table[m], data.get_d2r1, params, j, k)

                # Calculate the chi-squared Hessian.
                data.d2chi2[j, k] = data.d2chi2[k, j] = d2chi2_element(data.relax_data, data.ri, data.dri[j], data.dri[k], data.d2ri[j, k], data.errors)

        # Diagonal scaling.
        if self.scaling_flag:
            data.d2chi2 = dot(self.scaling_matrix, dot(data.d2chi2, self.scaling_matrix))

        # Return a copy of the Hessian.
        return data.d2chi2 * 1.0


    def d2func_diff(self, params):
        """Function for calculating the chi-squared Hessian.

        Used in the minimisation of diffusion tensor parameters with all model-free parameters
        fixed.
        """

        # Test if the gradient has already been called, otherwise run self.dfunc.
        if sum(params == self.grad_test) != self.total_num_params:
            self.dfunc(params)

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:self.diff_end_index]

        # Set the total chi2 Hessian to zero.
        self.total_d2chi2 = self.total_d2chi2 * 0.0

        # Loop over the residues.
        for i in xrange(self.num_spins):
            # Set self.data[i] to data.
            data = self.data[i]

            # Direction cosine calculations.
            if self.diff_data.calc_d2di:
               self.diff_data.calc_d2di(data, self.diff_data)

            # Diffusion tensor weight calculations.
            if self.diff_data.calc_d2ci:
                self.diff_data.calc_d2ci(data, self.diff_data)

            # Diffusion tensor correlation times.
            if self.diff_data.calc_d2ti:
               self.diff_data.calc_d2ti(data, self.diff_data)

            # Loop over the lower triangle of the Hessian.
            for j in xrange(data.total_num_params):
                for k in xrange(j + 1):
                    # Calculate the spectral density Hessians.
                    if data.calc_d2jw[j][k]:
                        data.d2jw = data.calc_d2jw[j][k](data, data.param_values, j, k)
                    else:
                        data.d2jw = data.d2jw * 0.0

                    # Calculate the relaxation Hessian components.
                    data.create_d2ri_comps(data, data.param_values)

                    # Calculate the R1, R2, and sigma_noe Hessians.
                    if data.create_d2ri_prime[j][k]:
                        data.d2ri_prime[j, k] = data.create_d2ri_prime[j][k](data)

                    # Loop over the relaxation values and modify the NOE Hessians.
                    data.d2ri[j, k] = data.d2ri_prime[j, k]
                    for m in xrange(data.num_ri):
                        if data.create_d2ri[m]:
                            data.create_d2ri[m](data, m, data.remap_table[m], data.get_d2r1, params, j, k)

                    # Calculate the chi-squared Hessian.
                    data.d2chi2[j, k] = data.d2chi2[k, j] = d2chi2_element(data.relax_data, data.ri, data.dri[j], data.dri[k], data.d2ri[j, k], data.errors)

            # Pure diffusion parameter part of the global generic model-free Hessian.
            self.total_d2chi2 = self.total_d2chi2 + data.d2chi2

        # Diagonal scaling.
        if self.scaling_flag:
            self.total_d2chi2 = dot(self.scaling_matrix, dot(self.total_d2chi2, self.scaling_matrix))

        # Return a copy of the Hessian.
        return self.total_d2chi2 * 1.0


    def d2func_all(self, params):
        """Function for calculating the chi-squared Hessian.

        Used in the minimisation of diffusion tensor parameters together with all model-free
        parameters.
        """

        # Test if the gradient has already been called, otherwise run self.dfunc.
        if sum(params == self.grad_test) != self.total_num_params:
            self.dfunc(params)

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Diffusion tensor parameters.
        self.diff_data.params = params[0:self.diff_end_index]

        # Set the total chi2 Hessian to zero.
        self.total_d2chi2 = self.total_d2chi2 * 0.0

        # Loop over the residues.
        for i in xrange(self.num_spins):
            # Set self.data[i] to data.
            data = self.data[i]

            # Direction cosine calculations.
            if self.diff_data.calc_d2di:
               self.diff_data.calc_d2di(data, self.diff_data)

            # Diffusion tensor weight calculations.
            if self.diff_data.calc_d2ci:
                self.diff_data.calc_d2ci(data, self.diff_data)

            # Diffusion tensor correlation times.
            if self.diff_data.calc_d2ti:
               self.diff_data.calc_d2ti(data, self.diff_data)

            # Loop over the lower triangle of the Hessian.
            for j in xrange(data.total_num_params):
                for k in xrange(j + 1):
                    # Calculate the spectral density Hessians.
                    if data.calc_d2jw[j][k]:
                        data.d2jw = data.calc_d2jw[j][k](data, params, j, k)
                    else:
                        data.d2jw = data.d2jw * 0.0

                    # Calculate the relaxation Hessian components.
                    data.create_d2ri_comps(data, params)

                    # Calculate the R1, R2, and sigma_noe Hessians.
                    if data.create_d2ri_prime[j][k]:
                        data.d2ri_prime[j, k] = data.create_d2ri_prime[j][k](data)

                    # Loop over the relaxation values and modify the NOE Hessians.
                    data.d2ri[j, k] = data.d2ri_prime[j, k]
                    for m in xrange(data.num_ri):
                        if data.create_d2ri[m]:
                            data.create_d2ri[m](data, m, data.remap_table[m], data.get_d2r1, params, j, k)

                    # Calculate the chi-squared Hessian.
                    data.d2chi2[j, k] = data.d2chi2[k, j] = d2chi2_element(data.relax_data, data.ri, data.dri[j], data.dri[k], data.d2ri[j, k], data.errors)

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
            self.total_d2chi2 = dot(self.scaling_matrix, dot(self.total_d2chi2, self.scaling_matrix))

        # Return a copy of the Hessian.
        return self.total_d2chi2 * 1.0


    def calc_ri(self):
        """Function for calculating relaxation values."""

        # Function call.
        chi2 = self.func_mf(self.params)

        # Return the single value.
        return self.data[0].ri[0]


    def init_diff_data(self, diff_data):
        """Function for the initialisation of diffusion tensor specific data."""

        # Diffusion as an sphere.
        if diff_data.type == 'sphere':
            # Number of diffusion parameters.
            diff_data.num_params = 1

            # Number of indices in the generic equations.
            diff_data.num_indices = 1

            # Direction cosine function, gradient, and Hessian.
            diff_data.calc_di = None
            diff_data.calc_ddi = None
            diff_data.calc_d2di = None

            # Weight function, gradient, and Hessian.
            diff_data.calc_ci = calc_sphere_ci
            diff_data.calc_dci = None
            diff_data.calc_d2ci = None

            # Global correlation time function, gradient, and Hessian.
            diff_data.calc_ti = calc_sphere_ti
            diff_data.calc_dti = calc_sphere_dti
            diff_data.calc_d2ti = None


        # Diffusion as an spheroid.
        elif diff_data.type == 'spheroid':
            # Number of diffusion parameters.
            diff_data.num_params = 4

            # Number of indices in the generic equations.
            diff_data.num_indices = 3

            # Direction cosine function, gradient, and Hessian.
            diff_data.calc_di = calc_spheroid_di
            diff_data.calc_ddi = calc_spheroid_ddi
            diff_data.calc_d2di = calc_spheroid_d2di

            # Weight function, gradient, and Hessian.
            diff_data.calc_ci = calc_spheroid_ci
            diff_data.calc_dci = calc_spheroid_dci
            diff_data.calc_d2ci = calc_spheroid_d2ci

            # Global correlation time function, gradient, and Hessian.
            diff_data.calc_ti = calc_spheroid_ti
            diff_data.calc_dti = calc_spheroid_dti
            diff_data.calc_d2ti = calc_spheroid_d2ti

            # Unit vectors.
            diff_data.dpar = zeros(3, float64)

            # Unit vector gradients.
            diff_data.dpar_dtheta = zeros(3, float64)
            diff_data.dpar_dphi = zeros(3, float64)

            # Unit vector Hessians.
            diff_data.dpar_dtheta2 = zeros(3, float64)
            diff_data.dpar_dthetadphi = zeros(3, float64)
            diff_data.dpar_dphi2 = zeros(3, float64)

        # Diffusion as an ellipsoid.
        elif diff_data.type == 'ellipsoid':
            # Number of diffusion parameters.
            diff_data.num_params = 6

            # Number of indices in the generic equations.
            diff_data.num_indices = 5

            # Direction cosine function, gradient, and Hessian.
            diff_data.calc_di = calc_ellipsoid_di
            diff_data.calc_ddi = calc_ellipsoid_ddi
            diff_data.calc_d2di = calc_ellipsoid_d2di

            # Weight function, gradient, and Hessian.
            diff_data.calc_ci = calc_ellipsoid_ci
            diff_data.calc_dci = calc_ellipsoid_dci
            diff_data.calc_d2ci = calc_ellipsoid_d2ci

            # Global correlation time function, gradient, and Hessian.
            diff_data.calc_ti = calc_ellipsoid_ti
            diff_data.calc_dti = calc_ellipsoid_dti
            diff_data.calc_d2ti = calc_ellipsoid_d2ti

            # Unit vectors.
            diff_data.dx = zeros(3, float64)
            diff_data.dy = zeros(3, float64)
            diff_data.dz = zeros(3, float64)

            # Unit vector gradients.
            diff_data.ddx_dalpha = zeros(3, float64)
            diff_data.ddx_dbeta = zeros(3, float64)
            diff_data.ddx_dgamma = zeros(3, float64)

            diff_data.ddy_dalpha = zeros(3, float64)
            diff_data.ddy_dbeta = zeros(3, float64)
            diff_data.ddy_dgamma = zeros(3, float64)

            diff_data.ddz_dalpha = zeros(3, float64)
            diff_data.ddz_dbeta = zeros(3, float64)
            diff_data.ddz_dgamma = zeros(3, float64)

            # Unit vector Hessians.
            diff_data.d2dx_dalpha2 = zeros(3, float64)
            diff_data.d2dx_dalpha_dbeta = zeros(3, float64)
            diff_data.d2dx_dalpha_dgamma = zeros(3, float64)
            diff_data.d2dx_dbeta2 = zeros(3, float64)
            diff_data.d2dx_dbeta_dgamma = zeros(3, float64)
            diff_data.d2dx_dgamma2 = zeros(3, float64)

            diff_data.d2dy_dalpha2 = zeros(3, float64)
            diff_data.d2dy_dalpha_dbeta = zeros(3, float64)
            diff_data.d2dy_dalpha_dgamma = zeros(3, float64)
            diff_data.d2dy_dbeta2 = zeros(3, float64)
            diff_data.d2dy_dbeta_dgamma = zeros(3, float64)
            diff_data.d2dy_dgamma2 = zeros(3, float64)

            diff_data.d2dz_dalpha2 = zeros(3, float64)
            diff_data.d2dz_dalpha_dbeta = zeros(3, float64)
            diff_data.d2dz_dalpha_dgamma = zeros(3, float64)
            diff_data.d2dz_dbeta2 = zeros(3, float64)
            diff_data.d2dz_dbeta_dgamma = zeros(3, float64)
            diff_data.d2dz_dgamma2 = zeros(3, float64)


    def init_res_data(self, data, diff_data):
        """Function for the initialisation of the residue specific data."""

        # Correlation times.
        data.ci = zeros(diff_data.num_indices, float64)
        data.ci_comps = zeros(diff_data.num_indices, float64)

        # Weights.
        data.ti = zeros(diff_data.num_indices, float64)
        data.tau_comps = zeros(diff_data.num_indices, float64)
        data.tau_comps_sqrd = zeros(diff_data.num_indices, float64)
        data.tau_comps_cubed = zeros(diff_data.num_indices, float64)
        data.tau_scale = zeros(diff_data.num_indices, float64)

        # Diffusion as a sphere.
        if self.diff_data.type == 'sphere':
            # Global correlation time gradient and Hessian.
            data.dti = zeros((1, diff_data.num_indices), float64)
            data.d2ti = zeros((1, 1, diff_data.num_indices), float64)

        # Diffusion as a spheroid.
        elif self.diff_data.type == 'spheroid':
            # Weight gradient and Hessian.
            data.dci = zeros((4, diff_data.num_indices), float64)
            data.d2ci = zeros((4, 4, diff_data.num_indices), float64)

            # Global correlation time gradient and Hessian.
            data.dti = zeros((2, diff_data.num_indices), float64)
            data.d2ti = zeros((2, 2, diff_data.num_indices), float64)

            # Dot product.
            data.dz = 0

            # Dot product gradient.
            data.ddz_dO = zeros(2, float64)

            # Dot product Hessian.
            data.d2dz_dO2 = zeros((2, 2), float64)

        # Diffusion as an ellipsoid.
        elif self.diff_data.type == 'ellipsoid':
            # Weight gradient and Hessian.
            data.dci = zeros((6, diff_data.num_indices), float64)
            data.d2ci = zeros((6, 6, diff_data.num_indices), float64)

            # Global correlation time gradient and Hessian.
            data.dti = zeros((3, diff_data.num_indices), float64)
            data.d2ti = zeros((3, 3, diff_data.num_indices), float64)

            # Dot products.
            data.dx = 0.0
            data.dy = 0.0
            data.dz = 0.0

            # Dot product gradients.
            data.ddx_dO = zeros(3, float64)
            data.ddy_dO = zeros(3, float64)
            data.ddz_dO = zeros(3, float64)

            # Dot product Hessians.
            data.d2dx_dO2 = zeros((3, 3), float64)
            data.d2dy_dO2 = zeros((3, 3), float64)
            data.d2dz_dO2 = zeros((3, 3), float64)

        # Empty spectral density components.
        data.w_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.fact_ti = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.w_te_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.w_tf_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.w_ts_ti_sqrd = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.inv_te_denom = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.inv_tf_denom = zeros((data.num_frq, 5, diff_data.num_indices), float64)
        data.inv_ts_denom = zeros((data.num_frq, 5, diff_data.num_indices), float64)

        # Empty spectral density values, gradients, and Hessians.
        data.jw = zeros((data.num_frq, 5), float64)
        data.djw = zeros((data.num_frq, 5), float64)
        data.d2jw = zeros((data.num_frq, 5), float64)

        # Calculate the fixed components of the dipolar and CSA constants.
        data.csa_const_fixed = zeros(data.num_frq, float64)
        data.dip_const_fixed = None
        calc_fixed_csa(data)
        calc_fixed_dip(data)

        # Dipolar and CSA constants.
        data.dip_const_func = 0.0
        data.dip_const_grad = 0.0
        data.dip_const_hess = 0.0
        data.csa_const_func = zeros(data.num_frq, float64)
        data.csa_const_grad = zeros(data.num_frq, float64)
        data.csa_const_hess = zeros(data.num_frq, float64)

        # Components of the transformed relaxation equations.
        data.dip_comps_func = zeros(data.num_ri, float64)
        data.csa_comps_func = zeros(data.num_ri, float64)
        data.rex_comps_func = zeros(data.num_ri, float64)
        data.dip_jw_comps_func = zeros(data.num_ri, float64)
        data.csa_jw_comps_func = zeros(data.num_ri, float64)

        # First partial derivative components of the transformed relaxation equations.
        data.dip_comps_grad = zeros(data.num_ri, float64)
        data.csa_comps_grad = zeros(data.num_ri, float64)
        data.rex_comps_grad = zeros(data.num_ri, float64)
        data.dip_jw_comps_grad = zeros(data.num_ri, float64)
        data.csa_jw_comps_grad = zeros(data.num_ri, float64)

        # First partial derivative components of the transformed relaxation equations.
        data.dip_comps_hess = zeros(data.num_ri, float64)
        data.csa_comps_hess = zeros(data.num_ri, float64)
        data.rex_comps_hess = zeros(data.num_ri, float64)
        data.dip_jw_comps_hess = zeros(data.num_ri, float64)
        data.csa_jw_comps_hess = zeros(data.num_ri, float64)

        # Transformed relaxation values, gradients, and Hessians.
        data.ri_prime = zeros((data.num_ri), float64)
        data.dri_prime = zeros((data.total_num_params, data.num_ri), float64)
        data.d2ri_prime = zeros((data.total_num_params, data.total_num_params, data.num_ri), float64)

        # Data structures containing the Ri values.
        data.ri = zeros(data.num_ri, float64)
        data.dri = zeros((data.total_num_params, data.num_ri), float64)
        data.d2ri = zeros((data.total_num_params, data.total_num_params, data.num_ri), float64)

        # Data structures containing the R1 values at the position of and corresponding to the NOE.
        data.r1 = zeros(data.num_ri, float64)
        data.dr1 = zeros((data.total_num_params, data.num_ri), float64)
        data.d2r1 = zeros((data.total_num_params, data.total_num_params, data.num_ri), float64)

        # Data structures containing the chi-squared values.
        data.chi2 = 0.0
        data.dchi2 = zeros((data.total_num_params), float64)
        data.d2chi2 = zeros((data.total_num_params, data.total_num_params), float64)


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
        r1_data.dip_comps_func = zeros(data.num_ri, float64)
        r1_data.csa_comps_func = zeros(data.num_ri, float64)
        r1_data.dip_jw_comps_func = zeros(data.num_ri, float64)
        r1_data.csa_jw_comps_func = zeros(data.num_ri, float64)

        # Initialise the first partial derivative components of the transformed relaxation equations.
        r1_data.dip_comps_grad = zeros(data.num_ri, float64)
        r1_data.csa_comps_grad = zeros(data.num_ri, float64)
        r1_data.rex_comps_grad = zeros(data.num_ri, float64)
        r1_data.dip_jw_comps_grad = zeros(data.num_ri, float64)
        r1_data.csa_jw_comps_grad = zeros(data.num_ri, float64)

        # Initialise the first partial derivative components of the transformed relaxation equations.
        r1_data.dip_comps_hess = zeros(data.num_ri, float64)
        r1_data.csa_comps_hess = zeros(data.num_ri, float64)
        r1_data.rex_comps_hess = zeros(data.num_ri, float64)
        r1_data.dip_jw_comps_hess = zeros(data.num_ri, float64)
        r1_data.csa_jw_comps_hess = zeros(data.num_ri, float64)

        # Initialise the transformed relaxation values, gradients, and Hessians.
        r1_data.ri_prime = zeros(data.num_ri, float64)
        r1_data.dri_prime = zeros((data.num_ri, data.total_num_params), float64)
        r1_data.d2ri_prime = zeros((data.num_ri, data.total_num_params, data.total_num_params), float64)

        # Place a few function arrays in the data class for the calculation of the R1 value when an NOE data set exists but the R1 set does not.
        r1_data.create_dri_prime = data.create_dri_prime
        r1_data.create_d2ri_prime = data.create_d2ri_prime

        # CSA, bond length, and Rex indices.
        r1_data.csa_i = data.csa_i
        r1_data.r_i = data.r_i
        r1_data.rex_i = data.rex_i

        # Place 'r1_data' into 'data'.
        data.r1_data = r1_data


    def lm_dri(self):
        """Return the function used for Levenberg-Marquardt minimisation."""

        # Create dri.
        if self.model_type == 'mf' or self.model_type == 'local_tm':
            dri = self.data[0].dri
        elif self.model_type == 'diff':
            # Set the total dri gradient to zero.
            self.total_dri = self.total_dri * 0.0

            # Ri indices.
            ri_start_index = 0
            ri_end_index = 0

            # Loop over the residues.
            for i in xrange(self.num_spins):
                # Set self.data[i] to data.
                data = self.data[i]

                # Increment Ri end index.
                ri_end_index = ri_end_index + data.num_ri

                # Diffusion parameter part of the global generic model-free gradient.
                self.total_dri[0:self.diff_data.num_params, ri_start_index:ri_end_index] = self.total_dri[0:self.diff_data.num_params, ri_start_index:ri_end_index] + data.dri[0:self.diff_data.num_params]

                # Increment Ri start index.
                ri_start_index = ri_start_index + data.num_ri

            # dri.
            dri = self.total_dri

        elif self.model_type == 'all':
            # Set the total dri gradient to zero.
            self.total_dri = self.total_dri * 0.0

            # Ri indices.
            ri_start_index = 0
            ri_end_index = 0

            # Loop over the residues.
            for i in xrange(self.num_spins):
                # Set self.data[i] to data.
                data = self.data[i]

                # Increment Ri end index.
                ri_end_index = ri_end_index + data.num_ri

                # Diffusion parameter part of the global generic model-free gradient.
                self.total_dri[0:self.diff_data.num_params, ri_start_index:ri_end_index] = self.total_dri[0:self.diff_data.num_params, ri_start_index:ri_end_index] + data.dri[0:self.diff_data.num_params]

                # Model-free parameter part of the global generic model-free gradient.
                self.total_dri[data.start_index:data.end_index, ri_start_index:ri_end_index] = self.total_dri[data.start_index:data.end_index, ri_start_index:ri_end_index] + data.dri[self.diff_data.num_params:]

                # Increment Ri start index.
                ri_start_index = ri_start_index + data.num_ri

            # dri.
            dri = self.total_dri

        # Make the proper Jacobian.
        dri = transpose(dri)

        # Diagonal scaling.
        if self.scaling_flag:
            dri = dot(dri, self.scaling_matrix)

        # Return dri.
        return dri


    def setup_equations(self, data):
        """Setup all the residue specific equations."""

        # Initialisation.
        #################

        # The number of diffusion parameters.
        if self.model_type != 'all':
            num_diff_params = 0
        elif self.diff_data.type == 'sphere':
            num_diff_params = 1
        elif self.diff_data.type == 'spheroid':
            num_diff_params = 4
        elif self.diff_data.type == 'ellipsoid':
            num_diff_params = 6

        # Indices.
        data.tm_i,  data.tm_li  = None, None
        data.s2_i,  data.s2_li  = None, None
        data.s2f_i, data.s2f_li = None, None
        data.s2s_i, data.s2s_li = None, None
        data.te_i,  data.te_li  = None, None
        data.tf_i,  data.tf_li  = None, None
        data.ts_i,  data.ts_li  = None, None
        data.rex_i, data.rex_li = None, None
        data.r_i,   data.r_li   = None, None
        data.csa_i, data.csa_li = None, None

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
            # Find the indices of the model-free parameters.
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2':
                    data.s2_li = num_diff_params + i
                    data.s2_i = self.param_index + i
                elif data.param_types[i] == 'te':
                    data.te_li = num_diff_params + i
                    data.te_i = self.param_index + i
                elif data.param_types[i] == 'Rex':
                    data.rex_li = num_diff_params + i
                    data.rex_i = self.param_index + i
                elif data.param_types[i] == 'r':
                    data.r_li = num_diff_params + i
                    data.r_i = self.param_index + i
                elif data.param_types[i] == 'CSA':
                    data.csa_li = num_diff_params + i
                    data.csa_i = self.param_index + i
                elif data.param_types[i] == 'local_tm':
                    pass
                else:
                    print("Unknown parameter.")
                    return 0

            # Increment the parameter index.
            self.param_index = self.param_index + data.num_params

            # Single residue minimisation with fixed diffusion parameters.
            if self.model_type == 'mf':
                # No model-free parameters {}.
                if data.s2_i == None and data.te_i == None:
                    # Equation.
                    data.calc_jw_comps =    None
                    data.calc_jw =          calc_jw

                    # Gradient.
                    data.calc_djw_comps = None

                # Model-free parameters {S2}.
                elif data.s2_i != None and data.te_i == None:
                    # Equation.
                    data.calc_jw_comps =    None
                    data.calc_jw =          calc_S2_jw

                    # Gradient.
                    data.calc_djw_comps =       None
                    data.calc_djw[data.s2_li] = calc_S2_djw_dS2

                # Model-free parameters {S2, te}.
                elif data.s2_i != None and data.te_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2_te_jw_comps
                    data.calc_jw =          calc_S2_te_jw

                    # Gradient.
                    data.calc_djw_comps =       calc_S2_te_djw_comps
                    data.calc_djw[data.s2_li] = calc_S2_te_djw_dS2
                    data.calc_djw[data.te_li] = calc_S2_te_djw_dte

                    # Hessian.
                    data.calc_d2jw[data.s2_li][data.te_li] = data.calc_d2jw[data.te_li][data.s2_li] =   calc_S2_te_d2jw_dS2dte
                    data.calc_d2jw[data.te_li][data.te_li] =                                            calc_S2_te_d2jw_dte2

                # Bad parameter combination.
                else:
                    print("Invalid combination of parameters for the extended model-free equation.")
                    return 0

            # Minimisation with variable diffusion parameters.
            else:
                # Diffusion parameters and no model-free parameters {}.
                if data.s2_i == None and data.te_i == None:
                    # Equation.
                    data.calc_jw_comps =    None
                    data.calc_jw =          calc_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_djw_comps

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_d2jw_dGjdGk

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_d2jw_dOjdOk

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_d2jw_dOjdOk

                # Diffusion parameters and model-free parameters {S2}.
                elif data.s2_i != None and data.te_i == None:
                    # Equation.
                    data.calc_jw_comps =    None
                    data.calc_jw =          calc_S2_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_djw_comps

                    if self.model_type != 'diff':
                        # Gradient.
                        data.calc_djw[data.s2_li] = calc_S2_djw_dS2

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_S2_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_S2_d2jw_dGjdGk
                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2_li] = data.calc_d2jw[data.s2_li][0] = calc_diff_S2_d2jw_dGjdS2

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_S2_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_S2_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_S2_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_S2_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_S2_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_S2_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_S2_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_S2_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_S2_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_S2_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2_li] = data.calc_d2jw[data.s2_li][0] = calc_diff_S2_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li] = data.calc_d2jw[data.s2_li][1] = calc_diff_S2_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li] = data.calc_d2jw[data.s2_li][2] = calc_diff_S2_d2jw_dOjdS2
                            data.calc_d2jw[3][data.s2_li] = data.calc_d2jw[data.s2_li][3] = calc_diff_S2_d2jw_dOjdS2

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_S2_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_S2_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_S2_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_S2_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_S2_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_S2_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_S2_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_S2_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_S2_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_S2_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_S2_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_S2_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2_li] = data.calc_d2jw[data.s2_li][0] = calc_ellipsoid_S2_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li] = data.calc_d2jw[data.s2_li][1] = calc_ellipsoid_S2_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li] = data.calc_d2jw[data.s2_li][2] = calc_ellipsoid_S2_d2jw_dGjdS2
                            data.calc_d2jw[3][data.s2_li] = data.calc_d2jw[data.s2_li][3] = calc_diff_S2_d2jw_dOjdS2
                            data.calc_d2jw[4][data.s2_li] = data.calc_d2jw[data.s2_li][4] = calc_diff_S2_d2jw_dOjdS2
                            data.calc_d2jw[5][data.s2_li] = data.calc_d2jw[data.s2_li][5] = calc_diff_S2_d2jw_dOjdS2


                # Diffusion parameters and model-free parameters {S2, te}.
                elif data.s2_i != None and data.te_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2_te_jw_comps
                    data.calc_jw =          calc_S2_te_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_S2_te_djw_comps

                    if self.model_type != 'diff':
                        # Gradient.
                        data.calc_djw[data.s2_li] = calc_S2_te_djw_dS2
                        data.calc_djw[data.te_li] = calc_S2_te_djw_dte

                        # Hessian.
                        data.calc_d2jw[data.s2_li][data.te_li] = data.calc_d2jw[data.te_li][data.s2_li] =   calc_S2_te_d2jw_dS2dte
                        data.calc_d2jw[data.te_li][data.te_li] =                                            calc_S2_te_d2jw_dte2

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_S2_te_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_S2_te_d2jw_dGjdGk
                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2_li] = data.calc_d2jw[data.s2_li][0] = calc_diff_S2_te_d2jw_dGjdS2
                            data.calc_d2jw[0][data.te_li] = data.calc_d2jw[data.te_li][0] = calc_diff_S2_te_d2jw_dGjdte

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_S2_te_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_S2_te_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_S2_te_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_S2_te_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_S2_te_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2_li] = data.calc_d2jw[data.s2_li][0] = calc_diff_S2_te_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li] = data.calc_d2jw[data.s2_li][1] = calc_diff_S2_te_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li] = data.calc_d2jw[data.s2_li][2] = calc_diff_S2_te_d2jw_dOjdS2
                            data.calc_d2jw[3][data.s2_li] = data.calc_d2jw[data.s2_li][3] = calc_diff_S2_te_d2jw_dOjdS2

                            data.calc_d2jw[0][data.te_li] = data.calc_d2jw[data.te_li][0] = calc_diff_S2_te_d2jw_dGjdte
                            data.calc_d2jw[1][data.te_li] = data.calc_d2jw[data.te_li][1] = calc_diff_S2_te_d2jw_dGjdte
                            data.calc_d2jw[2][data.te_li] = data.calc_d2jw[data.te_li][2] = calc_diff_S2_te_d2jw_dOjdte
                            data.calc_d2jw[3][data.te_li] = data.calc_d2jw[data.te_li][3] = calc_diff_S2_te_d2jw_dOjdte

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_S2_te_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_S2_te_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_S2_te_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_S2_te_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_S2_te_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_S2_te_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_S2_te_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_S2_te_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2_li] = data.calc_d2jw[data.s2_li][0] = calc_ellipsoid_S2_te_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li] = data.calc_d2jw[data.s2_li][1] = calc_ellipsoid_S2_te_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li] = data.calc_d2jw[data.s2_li][2] = calc_ellipsoid_S2_te_d2jw_dGjdS2
                            data.calc_d2jw[3][data.s2_li] = data.calc_d2jw[data.s2_li][3] = calc_diff_S2_te_d2jw_dOjdS2
                            data.calc_d2jw[4][data.s2_li] = data.calc_d2jw[data.s2_li][4] = calc_diff_S2_te_d2jw_dOjdS2
                            data.calc_d2jw[5][data.s2_li] = data.calc_d2jw[data.s2_li][5] = calc_diff_S2_te_d2jw_dOjdS2

                            data.calc_d2jw[0][data.te_li] = data.calc_d2jw[data.te_li][0] = calc_ellipsoid_S2_te_d2jw_dGjdte
                            data.calc_d2jw[1][data.te_li] = data.calc_d2jw[data.te_li][1] = calc_ellipsoid_S2_te_d2jw_dGjdte
                            data.calc_d2jw[2][data.te_li] = data.calc_d2jw[data.te_li][2] = calc_ellipsoid_S2_te_d2jw_dGjdte
                            data.calc_d2jw[3][data.te_li] = data.calc_d2jw[data.te_li][3] = calc_diff_S2_te_d2jw_dOjdte
                            data.calc_d2jw[4][data.te_li] = data.calc_d2jw[data.te_li][4] = calc_diff_S2_te_d2jw_dOjdte
                            data.calc_d2jw[5][data.te_li] = data.calc_d2jw[data.te_li][5] = calc_diff_S2_te_d2jw_dOjdte

                # Bad parameter combination.
                else:
                    print("Invalid combination of parameters for the extended model-free equation.")
                    return 0



        # The extended model-free equations {S2f, tf, S2, ts, Rex, r, CSA}.
        ###################################################################

        elif data.equations == 'mf_ext':
            # Find the indices of the model-free parameters.
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2f':
                    data.s2f_li = num_diff_params + i
                    data.s2f_i = self.param_index + i
                elif data.param_types[i] == 'tf':
                    data.tf_li = num_diff_params + i
                    data.tf_i = self.param_index + i
                elif data.param_types[i] == 'S2':
                    data.s2_li = num_diff_params + i
                    data.s2_i = self.param_index + i
                elif data.param_types[i] == 'ts':
                    data.ts_li = num_diff_params + i
                    data.ts_i = self.param_index + i
                elif data.param_types[i] == 'Rex':
                    data.rex_li = num_diff_params + i
                    data.rex_i = self.param_index + i
                elif data.param_types[i] == 'r':
                    data.r_li = num_diff_params + i
                    data.r_i = self.param_index + i
                elif data.param_types[i] == 'CSA':
                    data.csa_li = num_diff_params + i
                    data.csa_i = self.param_index + i
                elif data.param_types[i] == 'local_tm':
                    pass
                else:
                    print("Unknown parameter.")
                    return 0

            # Increment the parameter index.
            self.param_index = self.param_index + data.num_params

            # Single residue minimisation with fixed diffusion parameters.
            if self.model_type == 'mf':
                # Model-free parameters {S2f, S2, ts}.
                if data.s2f_i != None and data.tf_i == None and data.s2_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_S2_ts_jw_comps
                    data.calc_jw =          calc_S2f_S2_ts_jw

                    # Gradient.
                    data.calc_djw_comps =           calc_S2f_S2_ts_djw_comps
                    data.calc_djw[data.s2f_li] =    calc_S2f_S2_ts_djw_dS2f
                    data.calc_djw[data.s2_li] =     calc_S2f_S2_ts_djw_dS2
                    data.calc_djw[data.ts_li] =     calc_S2f_S2_ts_djw_dts

                    # Hessian.
                    data.calc_d2jw[data.s2f_li][data.ts_li] = data.calc_d2jw[data.ts_li][data.s2f_li] = calc_S2f_S2_ts_d2jw_dS2fdts
                    data.calc_d2jw[data.s2_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2_li]  = calc_S2f_S2_ts_d2jw_dS2dts
                    data.calc_d2jw[data.ts_li][data.ts_li]  =                                           calc_S2f_S2_ts_d2jw_dts2

                # Model-free parameters {S2f, tf, S2, ts}.
                elif data.s2f_i != None and data.tf_i != None and data.s2_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_tf_S2_ts_jw_comps
                    data.calc_jw =          calc_S2f_tf_S2_ts_jw

                    # Gradient.
                    data.calc_djw_comps =          calc_S2f_tf_S2_ts_djw_comps
                    data.calc_djw[data.s2f_li] =   calc_S2f_tf_S2_ts_djw_dS2f
                    data.calc_djw[data.tf_li] =    calc_S2f_tf_S2_ts_djw_dtf
                    data.calc_djw[data.s2_li] =    calc_S2f_S2_ts_djw_dS2
                    data.calc_djw[data.ts_li] =    calc_S2f_S2_ts_djw_dts

                    # Hessian.
                    data.calc_d2jw[data.s2f_li][data.tf_li] = data.calc_d2jw[data.tf_li][data.s2f_li] = calc_S2f_tf_S2_ts_d2jw_dS2fdtf
                    data.calc_d2jw[data.s2f_li][data.ts_li] = data.calc_d2jw[data.ts_li][data.s2f_li] = calc_S2f_S2_ts_d2jw_dS2fdts
                    data.calc_d2jw[data.s2_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2_li]  = calc_S2f_S2_ts_d2jw_dS2dts
                    data.calc_d2jw[data.tf_li][data.tf_li]  =                                           calc_S2f_tf_S2_ts_d2jw_dtf2
                    data.calc_d2jw[data.ts_li][data.ts_li]  =                                           calc_S2f_S2_ts_d2jw_dts2

                # Bad parameter combination.
                else:
                    print("Invalid combination of parameters for the extended model-free equation.")
                    return 0

            # Minimisation with variable diffusion parameters.
            else:
                # Diffusion parameters and model-free parameters {S2f, S2, ts}.
                if data.s2f_i != None and data.tf_i == None and data.s2_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_S2_ts_jw_comps
                    data.calc_jw =          calc_S2f_S2_ts_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_S2f_S2_ts_djw_comps

                    if self.model_type != 'diff':
                        # Gradient.
                        data.calc_djw[data.s2f_li] =    calc_S2f_S2_ts_djw_dS2f
                        data.calc_djw[data.s2_li] =     calc_S2f_S2_ts_djw_dS2
                        data.calc_djw[data.ts_li] =     calc_S2f_S2_ts_djw_dts

                        # Hessian.
                        data.calc_d2jw[data.s2f_li][data.ts_li] = data.calc_d2jw[data.ts_li][data.s2f_li] = calc_S2f_S2_ts_d2jw_dS2fdts
                        data.calc_d2jw[data.s2_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2_li]  = calc_S2f_S2_ts_d2jw_dS2dts
                        data.calc_d2jw[data.ts_li][data.ts_li]  =                                           calc_S2f_S2_ts_d2jw_dts2

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_S2f_S2_ts_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_S2f_S2_ts_d2jw_dGjdGk
                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_diff_S2f_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[0][data.s2_li]  = data.calc_d2jw[data.s2_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdts

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_S2f_S2_ts_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_S2f_S2_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_S2f_S2_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_S2f_S2_ts_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_S2f_S2_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_diff_S2f_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_diff_S2f_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_diff_S2f_S2_ts_d2jw_dOjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_S2_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.s2_li]  = data.calc_d2jw[data.s2_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li]  = data.calc_d2jw[data.s2_li][1]  = calc_diff_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li]  = data.calc_d2jw[data.s2_li][2]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2
                            data.calc_d2jw[3][data.s2_li]  = data.calc_d2jw[data.s2_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_diff_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_diff_S2f_S2_ts_d2jw_dOjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdts

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_S2f_S2_ts_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_S2f_S2_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_S2f_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_S2f_S2_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_S2_ts_d2jw_dOjdS2f
                            data.calc_d2jw[4][data.s2f_li] = data.calc_d2jw[data.s2f_li][4] = calc_diff_S2f_S2_ts_d2jw_dOjdS2f
                            data.calc_d2jw[5][data.s2f_li] = data.calc_d2jw[data.s2f_li][5] = calc_diff_S2f_S2_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.s2_li]  = data.calc_d2jw[data.s2_li][0]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li]  = data.calc_d2jw[data.s2_li][1]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li]  = data.calc_d2jw[data.s2_li][2]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[3][data.s2_li]  = data.calc_d2jw[data.s2_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2
                            data.calc_d2jw[4][data.s2_li]  = data.calc_d2jw[data.s2_li][4]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2
                            data.calc_d2jw[5][data.s2_li]  = data.calc_d2jw[data.s2_li][5]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdts
                            data.calc_d2jw[4][data.ts_li]  = data.calc_d2jw[data.ts_li][4]  = calc_diff_S2f_S2_ts_d2jw_dOjdts
                            data.calc_d2jw[5][data.ts_li]  = data.calc_d2jw[data.ts_li][5]  = calc_diff_S2f_S2_ts_d2jw_dOjdts


                # Diffusion parameters and model-free parameters {S2f, tf, S2, ts}.
                elif data.s2f_i != None and data.tf_i != None and data.s2_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_tf_S2_ts_jw_comps
                    data.calc_jw =          calc_S2f_tf_S2_ts_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_S2f_tf_S2_ts_djw_comps

                    if self.model_type != 'diff':
                        # Gradient.
                        data.calc_djw[data.s2f_li] =    calc_S2f_tf_S2_ts_djw_dS2f
                        data.calc_djw[data.tf_li] =     calc_S2f_tf_S2_ts_djw_dtf
                        data.calc_djw[data.s2_li] =     calc_S2f_S2_ts_djw_dS2
                        data.calc_djw[data.ts_li] =     calc_S2f_S2_ts_djw_dts

                        # Hessian.
                        data.calc_d2jw[data.s2f_li][data.tf_li] = data.calc_d2jw[data.tf_li][data.s2f_li] = calc_S2f_tf_S2_ts_d2jw_dS2fdtf
                        data.calc_d2jw[data.s2f_li][data.ts_li] = data.calc_d2jw[data.ts_li][data.s2f_li] = calc_S2f_S2_ts_d2jw_dS2fdts
                        data.calc_d2jw[data.s2_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2_li]  = calc_S2f_S2_ts_d2jw_dS2dts
                        data.calc_d2jw[data.tf_li][data.tf_li]  =                                           calc_S2f_tf_S2_ts_d2jw_dtf2
                        data.calc_d2jw[data.ts_li][data.ts_li]  =                                           calc_S2f_S2_ts_d2jw_dts2

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_S2f_tf_S2_ts_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_S2f_tf_S2_ts_d2jw_dGjdGk
                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_diff_S2f_tf_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[0][data.tf_li]  = data.calc_d2jw[data.tf_li][0]  = calc_diff_S2f_tf_S2_ts_d2jw_dGjdtf
                            data.calc_d2jw[0][data.s2_li]  = data.calc_d2jw[data.s2_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdts

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_S2f_tf_S2_ts_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_S2f_tf_S2_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_S2f_tf_S2_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_S2f_tf_S2_ts_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_diff_S2f_tf_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_diff_S2f_tf_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_diff_S2f_tf_S2_ts_d2jw_dOjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_tf_S2_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.tf_li]  = data.calc_d2jw[data.tf_li][0]  = calc_diff_S2f_tf_S2_ts_d2jw_dGjdtf
                            data.calc_d2jw[1][data.tf_li]  = data.calc_d2jw[data.tf_li][1]  = calc_diff_S2f_tf_S2_ts_d2jw_dGjdtf
                            data.calc_d2jw[2][data.tf_li]  = data.calc_d2jw[data.tf_li][2]  = calc_diff_S2f_tf_S2_ts_d2jw_dOjdtf
                            data.calc_d2jw[3][data.tf_li]  = data.calc_d2jw[data.tf_li][3]  = calc_diff_S2f_tf_S2_ts_d2jw_dOjdtf

                            data.calc_d2jw[0][data.s2_li]  = data.calc_d2jw[data.s2_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li]  = data.calc_d2jw[data.s2_li][1]  = calc_diff_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li]  = data.calc_d2jw[data.s2_li][2]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2
                            data.calc_d2jw[3][data.s2_li]  = data.calc_d2jw[data.s2_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_diff_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_diff_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_diff_S2f_S2_ts_d2jw_dOjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdts

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_S2f_tf_S2_ts_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_S2f_tf_S2_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_tf_S2_ts_d2jw_dOjdS2f
                            data.calc_d2jw[4][data.s2f_li] = data.calc_d2jw[data.s2f_li][4] = calc_diff_S2f_tf_S2_ts_d2jw_dOjdS2f
                            data.calc_d2jw[5][data.s2f_li] = data.calc_d2jw[data.s2f_li][5] = calc_diff_S2f_tf_S2_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.tf_li]  = data.calc_d2jw[data.tf_li][0]  = calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdtf
                            data.calc_d2jw[1][data.tf_li]  = data.calc_d2jw[data.tf_li][1]  = calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdtf
                            data.calc_d2jw[2][data.tf_li]  = data.calc_d2jw[data.tf_li][2]  = calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdtf
                            data.calc_d2jw[3][data.tf_li]  = data.calc_d2jw[data.tf_li][3]  = calc_diff_S2f_tf_S2_ts_d2jw_dOjdtf
                            data.calc_d2jw[4][data.tf_li]  = data.calc_d2jw[data.tf_li][4]  = calc_diff_S2f_tf_S2_ts_d2jw_dOjdtf
                            data.calc_d2jw[5][data.tf_li]  = data.calc_d2jw[data.tf_li][5]  = calc_diff_S2f_tf_S2_ts_d2jw_dOjdtf

                            data.calc_d2jw[0][data.s2_li]  = data.calc_d2jw[data.s2_li][0]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[1][data.s2_li]  = data.calc_d2jw[data.s2_li][1]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[2][data.s2_li]  = data.calc_d2jw[data.s2_li][2]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2
                            data.calc_d2jw[3][data.s2_li]  = data.calc_d2jw[data.s2_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2
                            data.calc_d2jw[4][data.s2_li]  = data.calc_d2jw[data.s2_li][4]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2
                            data.calc_d2jw[5][data.s2_li]  = data.calc_d2jw[data.s2_li][5]  = calc_diff_S2f_S2_ts_d2jw_dOjdS2

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2_ts_d2jw_dOjdts
                            data.calc_d2jw[4][data.ts_li]  = data.calc_d2jw[data.ts_li][4]  = calc_diff_S2f_S2_ts_d2jw_dOjdts
                            data.calc_d2jw[5][data.ts_li]  = data.calc_d2jw[data.ts_li][5]  = calc_diff_S2f_S2_ts_d2jw_dOjdts

                # Bad parameter combination.
                else:
                    print("Invalid combination of parameters for the extended model-free equation.")
                    return 0


        # The extended 2 model-free equations {tm, S2f, tf, S2s, ts, Rex, r, CSA}.
        #########################################################################

        elif data.equations == 'mf_ext2':
            # Find the indices of the model-free parameters.
            for i in xrange(data.num_params):
                if data.param_types[i] == 'S2f':
                    data.s2f_li = num_diff_params + i
                    data.s2f_i = self.param_index + i
                elif data.param_types[i] == 'tf':
                    data.tf_li = num_diff_params + i
                    data.tf_i = self.param_index + i
                elif data.param_types[i] == 'S2s':
                    data.s2s_li = num_diff_params + i
                    data.s2s_i = self.param_index + i
                elif data.param_types[i] == 'ts':
                    data.ts_li = num_diff_params + i
                    data.ts_i = self.param_index + i
                elif data.param_types[i] == 'Rex':
                    data.rex_li = num_diff_params + i
                    data.rex_i = self.param_index + i
                elif data.param_types[i] == 'r':
                    data.r_li = num_diff_params + i
                    data.r_i = self.param_index + i
                elif data.param_types[i] == 'CSA':
                    data.csa_li = num_diff_params + i
                    data.csa_i = self.param_index + i
                elif data.param_types[i] == 'local_tm':
                    pass
                else:
                    print("Unknown parameter.")
                    return 0

            # Increment the parameter index.
            self.param_index = self.param_index + data.num_params

            # Single residue minimisation with fixed diffusion parameters.
            if self.model_type == 'mf':
                # Model-free parameters {S2f, S2s, ts}.
                if data.s2f_i != None and data.tf_i == None and data.s2s_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_S2s_ts_jw_comps
                    data.calc_jw =          calc_S2f_S2s_ts_jw

                    # Gradient.
                    data.calc_djw_comps =           calc_S2f_S2s_ts_djw_comps
                    data.calc_djw[data.s2f_li] =    calc_S2f_S2s_ts_djw_dS2f
                    data.calc_djw[data.s2s_li] =    calc_S2f_tf_S2s_ts_djw_dS2s
                    data.calc_djw[data.ts_li] =     calc_S2f_S2s_ts_djw_dts

                    # Hessian.
                    data.calc_d2jw[data.s2f_li][data.s2s_li] = data.calc_d2jw[data.s2s_li][data.s2f_li] =   calc_S2f_S2s_ts_d2jw_dS2fdS2s
                    data.calc_d2jw[data.s2f_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2f_li]  =   calc_S2f_S2s_ts_d2jw_dS2fdts
                    data.calc_d2jw[data.s2s_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2s_li]  =   calc_S2f_S2s_ts_d2jw_dS2sdts
                    data.calc_d2jw[data.ts_li][data.ts_li]   =                                              calc_S2f_S2s_ts_d2jw_dts2

                # Model-free parameters {S2f, tf, S2s, ts}.
                elif data.s2f_i != None and data.tf_i != None and data.s2s_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_tf_S2s_ts_jw_comps
                    data.calc_jw =          calc_S2f_tf_S2s_ts_jw

                    # Gradient.
                    data.calc_djw_comps =           calc_S2f_tf_S2s_ts_djw_comps
                    data.calc_djw[data.s2f_li] =    calc_S2f_tf_S2s_ts_djw_dS2f
                    data.calc_djw[data.tf_li] =     calc_S2f_tf_S2s_ts_djw_dtf
                    data.calc_djw[data.s2s_li] =    calc_S2f_tf_S2s_ts_djw_dS2s
                    data.calc_djw[data.ts_li] =     calc_S2f_tf_S2s_ts_djw_dts

                    # Hessian.
                    data.calc_d2jw[data.s2f_li][data.s2s_li] = data.calc_d2jw[data.s2s_li][data.s2f_li] =   calc_S2f_S2s_ts_d2jw_dS2fdS2s
                    data.calc_d2jw[data.s2f_li][data.tf_li]  = data.calc_d2jw[data.tf_li][data.s2f_li]  =   calc_S2f_tf_S2s_ts_d2jw_dS2fdtf
                    data.calc_d2jw[data.s2f_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2f_li]  =   calc_S2f_tf_S2s_ts_d2jw_dS2fdts
                    data.calc_d2jw[data.s2s_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2s_li]  =   calc_S2f_tf_S2s_ts_d2jw_dS2sdts
                    data.calc_d2jw[data.tf_li][data.tf_li]   =                                              calc_S2f_tf_S2s_ts_d2jw_dtf2
                    data.calc_d2jw[data.ts_li][data.ts_li]   =                                              calc_S2f_tf_S2s_ts_d2jw_dts2

                # Bad parameter combination.
                else:
                    print("Invalid combination of parameters for the extended model-free equation.")
                    return 0

            # Minimisation with variable diffusion parameters.
            else:
                # Diffusion parameters and model-free parameters {S2f, S2s, ts}.
                if data.s2f_i != None and data.tf_i == None and data.s2s_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_S2s_ts_jw_comps
                    data.calc_jw =          calc_S2f_S2s_ts_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_S2f_S2s_ts_djw_comps

                    if self.model_type != 'diff':
                        # Gradient.
                        data.calc_djw[data.s2f_li] =    calc_diff_S2f_S2s_ts_djw_dS2f
                        data.calc_djw[data.s2s_li] =    calc_diff_S2f_S2s_ts_djw_dS2s
                        data.calc_djw[data.ts_li] =     calc_diff_S2f_S2s_ts_djw_dts

                        # Hessian.
                        data.calc_d2jw[data.s2f_li][data.s2s_li] = data.calc_d2jw[data.s2s_li][data.s2f_li] =   calc_S2f_S2s_ts_d2jw_dS2fdS2s
                        data.calc_d2jw[data.s2f_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2f_li]  =   calc_diff_S2f_S2s_ts_d2jw_dS2fdts
                        data.calc_d2jw[data.s2s_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2s_li]  =   calc_diff_S2f_S2s_ts_d2jw_dS2sdts
                        data.calc_d2jw[data.ts_li][data.ts_li]   =                                              calc_diff_S2f_S2s_ts_d2jw_dts2

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_S2f_S2s_ts_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_S2f_S2s_ts_d2jw_dGjdGk
                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] =   calc_diff_S2f_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[0][data.s2s_li] = data.calc_d2jw[data.s2s_li][0] =   calc_diff_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  =   calc_diff_S2f_S2s_ts_d2jw_dGjdts

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_S2f_S2s_ts_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_S2f_S2s_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_S2f_S2s_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_S2f_S2s_ts_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_S2f_S2s_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_diff_S2f_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_diff_S2f_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.s2s_li] = data.calc_d2jw[data.s2s_li][0] = calc_diff_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[1][data.s2s_li] = data.calc_d2jw[data.s2s_li][1] = calc_diff_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[2][data.s2s_li] = data.calc_d2jw[data.s2s_li][2] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s
                            data.calc_d2jw[3][data.s2s_li] = data.calc_d2jw[data.s2s_li][3] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_diff_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_diff_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_S2f_S2s_ts_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_S2f_S2s_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_S2f_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_S2f_S2s_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2f
                            data.calc_d2jw[4][data.s2f_li] = data.calc_d2jw[data.s2f_li][4] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2f
                            data.calc_d2jw[5][data.s2f_li] = data.calc_d2jw[data.s2f_li][5] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.s2s_li] = data.calc_d2jw[data.s2s_li][0] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[1][data.s2s_li] = data.calc_d2jw[data.s2s_li][1] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[2][data.s2s_li] = data.calc_d2jw[data.s2s_li][2] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[3][data.s2s_li] = data.calc_d2jw[data.s2s_li][3] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s
                            data.calc_d2jw[4][data.s2s_li] = data.calc_d2jw[data.s2s_li][4] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s
                            data.calc_d2jw[5][data.s2s_li] = data.calc_d2jw[data.s2s_li][5] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts
                            data.calc_d2jw[4][data.ts_li]  = data.calc_d2jw[data.ts_li][4]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts
                            data.calc_d2jw[5][data.ts_li]  = data.calc_d2jw[data.ts_li][5]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts

                # Diffusion parameters and model-free parameters {S2f, tf, S2s, ts}.
                elif data.s2f_i != None and data.tf_i != None and data.s2s_i != None and data.ts_i != None:
                    # Equation.
                    data.calc_jw_comps =    calc_S2f_tf_S2s_ts_jw_comps
                    data.calc_jw =          calc_S2f_tf_S2s_ts_jw

                    # Gradient.
                    data.calc_djw_comps = calc_diff_S2f_tf_S2s_ts_djw_comps

                    if self.model_type != 'diff':
                        # Gradient.
                        data.calc_djw[data.s2f_li] =    calc_diff_S2f_tf_S2s_ts_djw_dS2f
                        data.calc_djw[data.tf_li] =     calc_diff_S2f_tf_S2s_ts_djw_dtf
                        data.calc_djw[data.s2s_li] =    calc_diff_S2f_tf_S2s_ts_djw_dS2s
                        data.calc_djw[data.ts_li] =     calc_diff_S2f_tf_S2s_ts_djw_dts

                        # Hessian.
                        data.calc_d2jw[data.s2f_li][data.s2s_li] = data.calc_d2jw[data.s2s_li][data.s2f_li] =   calc_S2f_S2s_ts_d2jw_dS2fdS2s
                        data.calc_d2jw[data.s2f_li][data.tf_li]  = data.calc_d2jw[data.tf_li][data.s2f_li]  =   calc_diff_S2f_tf_S2s_ts_d2jw_dS2fdtf
                        data.calc_d2jw[data.s2f_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2f_li]  =   calc_diff_S2f_tf_S2s_ts_d2jw_dS2fdts
                        data.calc_d2jw[data.tf_li][data.tf_li]   =                                              calc_diff_S2f_tf_S2s_ts_d2jw_dtf2
                        data.calc_d2jw[data.s2s_li][data.ts_li]  = data.calc_d2jw[data.ts_li][data.s2s_li]  =   calc_diff_S2f_tf_S2s_ts_d2jw_dS2sdts
                        data.calc_d2jw[data.ts_li][data.ts_li]   =                                              calc_diff_S2f_tf_S2s_ts_d2jw_dts2

                    # Diffusion as a sphere.
                    if self.diff_data.type == 'sphere':
                        # Gradient.
                        data.calc_djw[0] = calc_diff_S2f_tf_S2s_ts_djw_dGj

                        # Hessian.
                        data.calc_d2jw[0][0] = calc_diff_S2f_tf_S2s_ts_d2jw_dGjdGk
                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[0][data.tf_li]  = data.calc_d2jw[data.tf_li][0]  =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdtf
                            data.calc_d2jw[0][data.s2s_li] = data.calc_d2jw[data.s2s_li][0] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdts

                    # Diffusion as a spheroid.
                    elif self.diff_data.type == 'spheroid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = calc_diff_S2f_tf_S2s_ts_djw_dGj
                        data.calc_djw[2] = data.calc_djw[3] = calc_diff_S2f_tf_S2s_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_diff_S2f_tf_S2s_ts_d2jw_dGjdOj

                        data.calc_d2jw[2][2] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][3] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_diff_S2f_tf_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_diff_S2f_tf_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.tf_li]  = data.calc_d2jw[data.tf_li][0]  = calc_diff_S2f_tf_S2s_ts_d2jw_dGjdtf
                            data.calc_d2jw[1][data.tf_li]  = data.calc_d2jw[data.tf_li][1]  = calc_diff_S2f_tf_S2s_ts_d2jw_dGjdtf
                            data.calc_d2jw[2][data.tf_li]  = data.calc_d2jw[data.tf_li][2]  = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdtf
                            data.calc_d2jw[3][data.tf_li]  = data.calc_d2jw[data.tf_li][3]  = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdtf

                            data.calc_d2jw[0][data.s2s_li] = data.calc_d2jw[data.s2s_li][0] = calc_diff_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[1][data.s2s_li] = data.calc_d2jw[data.s2s_li][1] = calc_diff_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[2][data.s2s_li] = data.calc_d2jw[data.s2s_li][2] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s
                            data.calc_d2jw[3][data.s2s_li] = data.calc_d2jw[data.s2s_li][3] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_diff_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_diff_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts

                    # Diffusion as an ellipsoid.
                    elif self.diff_data.type == 'ellipsoid':
                        # Gradient.
                        data.calc_djw[0] = data.calc_djw[1] = data.calc_djw[2] = calc_ellipsoid_S2f_tf_S2s_ts_djw_dGj
                        data.calc_djw[3] = data.calc_djw[4] = data.calc_djw[5] = calc_diff_S2f_tf_S2s_ts_djw_dOj

                        # Hessian.
                        data.calc_d2jw[0][0] =                          calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][1] = data.calc_d2jw[1][0] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[0][2] = data.calc_d2jw[2][0] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][1] =                          calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[1][2] = data.calc_d2jw[2][1] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk
                        data.calc_d2jw[2][2] =                          calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk

                        data.calc_d2jw[0][3] = data.calc_d2jw[3][0] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][4] = data.calc_d2jw[4][0] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[0][5] = data.calc_d2jw[5][0] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][3] = data.calc_d2jw[3][1] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][4] = data.calc_d2jw[4][1] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[1][5] = data.calc_d2jw[5][1] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][3] = data.calc_d2jw[3][2] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][4] = data.calc_d2jw[4][2] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj
                        data.calc_d2jw[2][5] = data.calc_d2jw[5][2] =   calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj

                        data.calc_d2jw[3][3] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][4] = data.calc_d2jw[4][3] =   calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[3][5] = data.calc_d2jw[5][3] =   calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][4] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[4][5] = data.calc_d2jw[5][4] =   calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk
                        data.calc_d2jw[5][5] =                          calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk

                        if self.model_type != 'diff':
                            data.calc_d2jw[0][data.s2f_li] = data.calc_d2jw[data.s2f_li][0] = calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[1][data.s2f_li] = data.calc_d2jw[data.s2f_li][1] = calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[2][data.s2f_li] = data.calc_d2jw[data.s2f_li][2] = calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdS2f
                            data.calc_d2jw[3][data.s2f_li] = data.calc_d2jw[data.s2f_li][3] = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2f
                            data.calc_d2jw[4][data.s2f_li] = data.calc_d2jw[data.s2f_li][4] = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2f
                            data.calc_d2jw[5][data.s2f_li] = data.calc_d2jw[data.s2f_li][5] = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2f

                            data.calc_d2jw[0][data.tf_li]  = data.calc_d2jw[data.tf_li][0]  = calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdtf
                            data.calc_d2jw[1][data.tf_li]  = data.calc_d2jw[data.tf_li][1]  = calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdtf
                            data.calc_d2jw[2][data.tf_li]  = data.calc_d2jw[data.tf_li][2]  = calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdtf
                            data.calc_d2jw[3][data.tf_li]  = data.calc_d2jw[data.tf_li][3]  = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdtf
                            data.calc_d2jw[4][data.tf_li]  = data.calc_d2jw[data.tf_li][4]  = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdtf
                            data.calc_d2jw[5][data.tf_li]  = data.calc_d2jw[data.tf_li][5]  = calc_diff_S2f_tf_S2s_ts_d2jw_dOjdtf

                            data.calc_d2jw[0][data.s2s_li] = data.calc_d2jw[data.s2s_li][0] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[1][data.s2s_li] = data.calc_d2jw[data.s2s_li][1] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[2][data.s2s_li] = data.calc_d2jw[data.s2s_li][2] = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s
                            data.calc_d2jw[3][data.s2s_li] = data.calc_d2jw[data.s2s_li][3] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s
                            data.calc_d2jw[4][data.s2s_li] = data.calc_d2jw[data.s2s_li][4] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s
                            data.calc_d2jw[5][data.s2s_li] = data.calc_d2jw[data.s2s_li][5] = calc_diff_S2f_S2s_ts_d2jw_dOjdS2s

                            data.calc_d2jw[0][data.ts_li]  = data.calc_d2jw[data.ts_li][0]  = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[1][data.ts_li]  = data.calc_d2jw[data.ts_li][1]  = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[2][data.ts_li]  = data.calc_d2jw[data.ts_li][2]  = calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts
                            data.calc_d2jw[3][data.ts_li]  = data.calc_d2jw[data.ts_li][3]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts
                            data.calc_d2jw[4][data.ts_li]  = data.calc_d2jw[data.ts_li][4]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts
                            data.calc_d2jw[5][data.ts_li]  = data.calc_d2jw[data.ts_li][5]  = calc_diff_S2f_S2s_ts_d2jw_dOjdts

                # Bad parameter combination.
                else:
                    print("Invalid combination of parameters for the extended model-free equation.")
                    return 0

        # Unknown model-free equation.
        else:
            print("Unknown model-free equation.")
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
        if data.rex_i == None:
            data.create_ri_prime = func_ri_prime
        else:
            data.create_ri_prime = func_ri_prime_rex

        # dri_prime and d2ri_prime.
        for i in xrange(data.total_num_params):
            # Diffusion tensor parameters are the only parameters.
            if self.model_type == 'diff':
                # Gradient.
                data.create_dri_prime.append(func_dri_djw_prime)

                # Hessian.
                data.create_d2ri_prime.append([])
                for j in xrange(data.total_num_params):
                    data.create_d2ri_prime[i].append(func_d2ri_djwidjwj_prime)

                # Skip to the next parameter index.
                continue

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
                        data.create_d2ri_prime[i].append(func_d2ri_djwdr_prime)

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
                        data.create_d2ri_prime[i].append(func_d2ri_djwdcsa_prime)

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

        if data.r_i == None and data.csa_i == None:
            # The main ri component functions
            if data.rex_i == None:
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

        elif data.r_i != None and data.csa_i == None:
            # The main ri component functions
            if data.rex_i == None:
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

        elif data.r_i == None and data.csa_i != None:
            # The main ri component functions
            if data.rex_i == None:
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

        elif data.r_i != None and data.csa_i != None:
            # The main ri component functions
            if data.rex_i == None:
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
            print("Invalid combination of parameters for the model-free equations.")
            return 0

        return 1


class Data:
    def __init__(self):
        """Empty container for storing data."""
