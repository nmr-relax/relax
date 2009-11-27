###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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

from copy import deepcopy
from LinearAlgebra import inverse
from math import pi
from Numeric import Float64, array, identity, matrixmultiply, ones, transpose, zeros
from re import match, search
from string import replace, split
import sys

from base_class import Common_functions
from maths_fns.mf_csa import Mf_csa
from minimise.generic import generic_minimise
from float import isNaN,isInf 


class Model_free_csa(Common_functions):
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax

        # Class containing the Molmol specific functions.
        self.molmol = Molmol(self.relax)


    def are_mf_params_set(self, index=None):
        """Function for testing if the model-free parameter values are set."""

        # Alias the data structure.
        data = self.relax.data.res[self.run][index]

        # Unselected residue.
        if data.select == 0:
            return

        # Loop over the model-free parameters.
        for j in xrange(len(data.params)):
            # Local tm.
            if data.params[j] == 'local_tm' and data.local_tm == None:
                return data.params[j]

            # S2.
            elif data.params[j] == 'S2' and data.s2 == None:
                return data.params[j]

            # S2f.
            elif data.params[j] == 'S2f' and data.s2f == None:
                return data.params[j]

            # S2s.
            elif data.params[j] == 'S2s' and data.s2s == None:
                return data.params[j]

            # te.
            elif data.params[j] == 'te' and data.te == None:
                return data.params[j]

            # tf.
            elif data.params[j] == 'tf' and data.tf == None:
                return data.params[j]

            # ts.
            elif data.params[j] == 'ts' and data.ts == None:
                return data.params[j]

            # Rex.
            elif data.params[j] == 'Rex' and data.rex == None:
                return data.params[j]

            # r.
            elif data.params[j] == 'r' and data.r == None:
                return data.params[j]

            # CSA.
            elif data.params[j] == 'CSA' and data.csa == None:
                return data.params[j]


    def assemble_param_names(self, index=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        self.param_names = []

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                self.param_names.append('tm')

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                self.param_names.append('tm')
                self.param_names.append('Da')
                self.param_names.append('theta')
                self.param_names.append('phi')

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                self.param_names.append('tm')
                self.param_names.append('Da')
                self.param_names.append('Dr')
                self.param_names.append('alpha')
                self.param_names.append('beta')
                self.param_names.append('gamma')

        # Model-free parameters (residue specific parameters).
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over the model-free parameters and add the names.
                for j in xrange(len(self.relax.data.res[self.run][i].params)):
                    self.param_names.append(self.relax.data.res[self.run][i].params[j])


    def assemble_param_vector(self, index=None, sim_index=None, param_set=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        param_vector = []
        if param_set == None:
            param_set = self.param_set

        # Monte Carlo diffusion tensor parameters.
        if sim_index != None and (param_set == 'diff' or param_set == 'all'):
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                param_vector.append(self.relax.data.diff[self.run].tm_sim[sim_index])

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                param_vector.append(self.relax.data.diff[self.run].tm_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].Da_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].theta_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].phi_sim[sim_index])

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                param_vector.append(self.relax.data.diff[self.run].tm_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].Da_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].Dr_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].alpha_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].beta_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].gamma_sim[sim_index])

        # Diffusion tensor parameters.
        elif param_set == 'diff' or param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                param_vector.append(self.relax.data.diff[self.run].tm)

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                param_vector.append(self.relax.data.diff[self.run].tm)
                param_vector.append(self.relax.data.diff[self.run].Da)
                param_vector.append(self.relax.data.diff[self.run].theta)
                param_vector.append(self.relax.data.diff[self.run].phi)

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                param_vector.append(self.relax.data.diff[self.run].tm)
                param_vector.append(self.relax.data.diff[self.run].Da)
                param_vector.append(self.relax.data.diff[self.run].Dr)
                param_vector.append(self.relax.data.diff[self.run].alpha)
                param_vector.append(self.relax.data.diff[self.run].beta)
                param_vector.append(self.relax.data.diff[self.run].gamma)

        # Model-free parameters (residue specific parameters).
        if param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if (param_set == 'mf' or param_set == 'local_tm') and index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[self.run][i].params)):
                    # local tm.
                    if self.relax.data.res[self.run][i].params[j] == 'local_tm':
                        if self.relax.data.res[self.run][i].local_tm == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].local_tm_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].local_tm)

                    # S2.
                    elif self.relax.data.res[self.run][i].params[j] == 'S2':
                        if self.relax.data.res[self.run][i].s2 == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].s2_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].s2)

                    # S2f.
                    elif self.relax.data.res[self.run][i].params[j] == 'S2f':
                        if self.relax.data.res[self.run][i].s2f == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].s2f_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].s2f)

                    # S2s.
                    elif self.relax.data.res[self.run][i].params[j] == 'S2s':
                        if self.relax.data.res[self.run][i].s2s == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].s2s_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].s2s)

                    # te.
                    elif self.relax.data.res[self.run][i].params[j] == 'te':
                        if self.relax.data.res[self.run][i].te == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].te_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].te)

                    # tf.
                    elif self.relax.data.res[self.run][i].params[j] == 'tf':
                        if self.relax.data.res[self.run][i].tf == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].tf_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].tf)

                    # ts.
                    elif self.relax.data.res[self.run][i].params[j] == 'ts':
                        if self.relax.data.res[self.run][i].ts == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].ts_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].ts)

                    # Rex.
                    elif self.relax.data.res[self.run][i].params[j] == 'Rex':
                        if self.relax.data.res[self.run][i].rex == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].rex_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].rex)

                    # r.
                    elif self.relax.data.res[self.run][i].params[j] == 'r':
                        if self.relax.data.res[self.run][i].r == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].r_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].r)

                    # CSA.
                    elif self.relax.data.res[self.run][i].params[j] == 'CSA':
                        if self.relax.data.res[self.run][i].csa == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].csa_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].csa)

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

        # Return a Numeric array.
        return array(param_vector, Float64)


    def assemble_scaling_matrix(self, index=None, scaling=1):
        """Function for creating the scaling matrix."""

        # Initialise.
        if len(self.param_vector) == 0:
            self.scaling_matrix = zeros((0, 0), Float64)
        else:
            self.scaling_matrix = identity(len(self.param_vector), Float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return

        # tm, te, tf, and ts (must all be the same for diagonal scaling!).
        ti_scaling = 1e-12

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                # tm.
                self.scaling_matrix[i, i] = ti_scaling

                # Increment i.
                i = i + 1

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                # tm, Da, theta, phi
                self.scaling_matrix[i, i] = ti_scaling
                self.scaling_matrix[i+1, i+1] = 1e7
                self.scaling_matrix[i+2, i+2] = 1.0
                self.scaling_matrix[i+3, i+3] = 1.0

                # Increment i.
                i = i + 4

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # tm, Da, Dr, alpha, beta, gamma.
                self.scaling_matrix[i, i] = ti_scaling
                self.scaling_matrix[i+1, i+1] = 1e7
                self.scaling_matrix[i+2, i+2] = 1.0
                self.scaling_matrix[i+3, i+3] = 1.0
                self.scaling_matrix[i+4, i+4] = 1.0
                self.scaling_matrix[i+5, i+5] = 1.0

                # Increment i.
                i = i + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][j].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and j != index:
                    continue

                # Loop over the model-free parameters.
                for k in xrange(len(self.relax.data.res[self.run][j].params)):
                    # Local tm, te, tf, and ts (must all be the same for diagonal scaling!).
                    if self.relax.data.res[self.run][j].params[k] == 'local_tm' or search('^t', self.relax.data.res[self.run][j].params[k]):
                        self.scaling_matrix[i, i] = ti_scaling

                    # Rex.
                    elif self.relax.data.res[self.run][j].params[k] == 'Rex':
                        self.scaling_matrix[i, i] = 1.0 / (2.0 * pi * self.relax.data.res[self.run][j].frq[0]) ** 2

                    # Bond length.
                    elif self.relax.data.res[self.run][j].params[k] == 'r':
                        self.scaling_matrix[i, i] = 1e-10

                    # CSA.
                    elif self.relax.data.res[self.run][j].params[k] == 'CSA':
                        self.scaling_matrix[i, i] = 1e-4

                    # Increment i.
                    i = i + 1


    def back_calc(self, run=None, index=None, ri_label=None, frq_label=None, frq=None):
        """Back-calculation of relaxation data from the model-free parameter values."""

        # Run argument.
        self.run = run

        # Get the relaxation value from the minimise function.
        value = self.minimise(run=self.run, min_algor='back_calc', min_options=(index, ri_label, frq_label, frq))

        # Return the relaxation value.
        return value


    def calculate(self, run=None, res_num=None, print_flag=1, sim_index=None):
        """Calculation of the model-free chi-squared value."""

        # Arguments.
        self.run = run
        self.print_flag = print_flag

        # Test if the sequence data for self.run is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # The residue index.
        index = None
        if res_num != None:
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Found the residue.
                if self.relax.data.res[self.run][i].num == res_num:
                    index = i
                    break

            # Can't find the residue.
            if index == None:
                raise RelaxNoResError, res_num

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Test if diffusion tensor data for the run exists.
        if self.param_set != 'local_tm' and not self.relax.data.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Test if the PDB file has been loaded.
        if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere' and not self.relax.data.pdb.has_key(self.run):
            raise RelaxNoPdbError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Loop over the residues.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Alias the data structure.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Single residue.
            if index != None and index != i:
                continue

            # Test if the model-free model has been setup.
            if not data.model:
                raise RelaxNoModelError, self.run

            # Test if unit vectors exist.
            if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere' and not hasattr(data, 'xh_vect'):
                raise RelaxNoVectorsError, self.run

            # Test if the model-free parameter values exist.
            unset_param = self.are_mf_params_set(i)
            if unset_param != None:
                raise RelaxNoValueError, unset_param

            # Test if the CSA value has been set.
            if not hasattr(data, 'csa') or data.csa == None:
                raise RelaxNoValueError, "CSA"

            # Test if the bond length value has been set.
            if not hasattr(data, 'r') or data.r == None:
                raise RelaxNoValueError, "bond length"

            # Skip residues where there is no data or errors.
            if not hasattr(data, 'relax_data') or not hasattr(data, 'relax_error'):
                continue

            # Make sure that the errors are strictly positive numbers.
            for j in xrange(len(data.relax_error)):
                if data.relax_error[j] == 0.0:
                    raise RelaxError, "Zero error for residue '" + `data.num` + " " + data.name + "', calculation not possible."
                elif data.relax_error[j] < 0.0:
                    raise RelaxError, "Negative error for residue '" + `data.num` + " " + data.name + "', calculation not possible."

            # Create the initial parameter vector.
            self.param_vector = self.assemble_param_vector(index=i, sim_index=sim_index)

            # Repackage the data.
            if sim_index == None:
                relax_data = [data.relax_data]
                cst = [data.cst]
                csea = [data.csea]
                csa_data_ax = [data.csa_data_ax]
                csa_data_by = [data.csa_data_by]
                csa_data_cz = [data.csa_data_cz]
                r = [data.r]
                csa = [data.csa]
		xy_vect_num = [data.xy_vect_num]
		xy_data = [data.xy_data]
            else:
                relax_data = [data.relax_sim_data[sim_index]]
                r = [data.r_sim[sim_index]]
                csa = [data.csa_sim[sim_index]]

            # Vectors.
            if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere':
                xh_unit_vectors = [data.xh_vect]
            else:
                xh_unit_vectors = [None]

            # Count the number of model-free parameters for the residue index.
            num_params = [len(data.params)]

            # Repackage the parameter values for minimising just the diffusion tensor parameters.
            param_values = [self.assemble_param_vector(param_set='mf')]

            # Convert to Numeric arrays.
            relax_data = [array(data.relax_data, Float64)]
            relax_error = [array(data.relax_error, Float64)]
            cst = [array(data.cst, Float64)]
            csea = [array(data.csea, Float64)]
            csa_data_ax = [array(data.csa_data_ax, Float64)]
            csa_data_by = [array(data.csa_data_by, Float64)]
            csa_data_cz = [array(data.csa_data_cz, Float64)]

            # Package the diffusion tensor parameters.
            if self.param_set == 'local_tm':
                diff_params = [self.relax.data.res[self.run][i].local_tm]
                diff_type = 'sphere'
            else:
                # Alias.
                diff_data = self.relax.data.diff[self.run]

                # Diff type.
                diff_type = diff_data.type

                # Spherical diffusion.
                if diff_type == 'sphere':
                    diff_params = [diff_data.tm]

                # Spheroidal diffusion.
                elif diff_type == 'spheroid':
                    diff_params = [diff_data.tm, diff_data.Da, diff_data.theta, diff_data.phi]

                # Ellipsoidal diffusion.
                elif diff_type == 'ellipsoid':
                    diff_params = [diff_data.tm, diff_data.Da, diff_data.Dr, diff_data.alpha, diff_data.beta, diff_data.gamma]

            # Initialise the model-free function.
            self.mf_csa = Mf_csa(init_params=self.param_vector, param_set='mf', diff_type=diff_type, diff_params=diff_params, num_res=1, equations=[data.equation], param_types=[data.params], param_values=param_values, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=[data.num_frq], frq=[data.frq], num_ri=[data.num_ri], remap_table=[data.remap_table], noe_r1_table=[data.noe_r1_table], ri_labels=[data.ri_labels], gx=self.relax.data.gx, gh=self.relax.data.gh, g_ratio=self.relax.data.g_ratio, h_bar=self.relax.data.h_bar, mu0=self.relax.data.mu0, num_params=num_params, vectors=xh_unit_vectors, csa_data_ax=csa_data_ax, csa_data_by=csa_data_by, csa_data_cz=csa_data_cz, csa_labels=csa_labels, num_csa=num_csa, cst=cst, csea=csea, xy_vect_num=xy_vect_num, xy_data=xy_data)

            # Chi-squared calculation.
            try:
                chi2 = self.mf_csa.func(self.param_vector)
            except OverflowError:
                chi2 = 1e200

            # Global chi-squared value.
            if self.param_set == 'all' or self.param_set == 'diff':
                self.relax.data.chi2[self.run] = self.relax.data.chi2[self.run] + chi2
            else:
                self.relax.data.res[self.run][i].chi2 = chi2


    def copy(self, run1=None, run2=None, sim=None):
        """Function for copying all model-free data from run1 to run2."""

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Test if the run type of run1 is set to 'mf_csa'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run1)]
        if function_type != 'mf_csa':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the run type of run2 is set to 'mf_csa'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run2)]
        if function_type != 'mf_csa':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the sequence data for run1 is loaded.
        if not self.relax.data.res.has_key(run1):
            raise RelaxNoSequenceError, run1

        # Test if the sequence data for run2 is loaded.
        if not self.relax.data.res.has_key(run2):
            raise RelaxNoSequenceError, run2

        # Get all data structure names.
        names = self.data_names()

        # Copy the data.
        for i in xrange(len(self.relax.data.res[run1])):
            # Remap the data structure 'self.relax.data.res[run1][i]'.
            data1 = self.relax.data.res[run1][i]
            data2 = self.relax.data.res[run2][i]

            # Loop through the data structure names.
            for name in names:
                # All data.
                if not sim:
                    # Skip the data structure if it does not exist.
                    if not hasattr(data1, name):
                        continue

                    # Copy the data structure.
                    setattr(data2, name, deepcopy(getattr(data1, name)))

                # Copy just the simulation data for the simulation 'sim'.
                else:
                    # Sim data name
                    name = name + '_sim'

                    # Skip the data structure if it does not exist in both runs.
                    if not hasattr(data1, name) or not hasattr(data2, name):
                        continue

                    # Get the objects.
                    object1 = getattr(data1, name)
                    object2 = getattr(data2, name)

                    # Copy the data.
                    object2[sim] = object1[sim]


    def create_mc_data(self, run, i):
        """Function for creating the Monte Carlo Ri data."""

        # Arguments
        self.run = run

        # Initialise the data data structure.
        data = []

        # Test if the model is set.
        if not hasattr(self.relax.data.res[self.run][i], 'model') or not self.relax.data.res[self.run][i].model:
            raise RelaxNoModelError, self.run

        # Loop over the relaxation data.
        for j in xrange(len(self.relax.data.res[run][i].relax_data)):
            # Back calculate the value.
            value = self.back_calc(run=run, index=i, ri_label=self.relax.data.res[run][i].ri_labels[j], frq_label=self.relax.data.res[run][i].frq_labels[self.relax.data.res[run][i].remap_table[j]], frq=self.relax.data.res[run][i].frq[self.relax.data.res[run][i].remap_table[j]])

            # Append the value.
            data.append(value)

        # Return the data.
        return data


    def create_model(self, run=None, model=None, equation=None, params=None, res_num=None):
        """Function to create a model-free model."""

        # Run argument.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf_csa'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf_csa':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Check the validity of the model-free equation type.
        valid_types = ['mf_orig', 'mf_ext', 'mf_ext2']
        if not equation in valid_types:
            raise RelaxError, "The model-free equation type argument " + `equation` + " is invalid and should be one of " + `valid_types` + "."

        # Check the validity of the parameter array.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in xrange(len(params)):
            # Invalid parameter flag.
            invalid_param = 0

            # S2.
            if params[i] == 'S2':
                # Does the array contain more than one instance of S2.
                if s2:
                    invalid_param = 1
                s2 = 1

                # Does the array contain S2s.
                s2s_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2s':
                        s2s_flag = 1
                if s2s_flag:
                    invalid_param = 1

            # te.
            elif params[i] == 'te':
                # Does the array contain more than one instance of te and has the extended model-free formula been selected.
                if equation == 'mf_ext' or te:
                    invalid_param = 1
                te = 1

                # Does the array contain the parameter S2.
                s2_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2':
                        s2_flag = 1
                if not s2_flag:
                    invalid_param = 1

            # S2f.
            elif params[i] == 'S2f':
                # Does the array contain more than one instance of S2f and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2f:
                    invalid_param = 1
                s2f = 1

            # S2s.
            elif params[i] == 'S2s':
                # Does the array contain more than one instance of S2s and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2s:
                    invalid_param = 1
                s2s = 1

            # tf.
            elif params[i] == 'tf':
                # Does the array contain more than one instance of tf and has the original model-free formula been selected.
                if equation == 'mf_orig' or tf:
                    invalid_param = 1
                tf = 1

                # Does the array contain the parameter S2f.
                s2f_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2f':
                        s2f_flag = 1
                if not s2f_flag:
                    invalid_param = 1

            # ts.
            elif params[i] == 'ts':
                # Does the array contain more than one instance of ts and has the original model-free formula been selected.
                if equation == 'mf_orig' or ts:
                    invalid_param = 1
                ts = 1

                # Does the array contain the parameter S2 or S2s.
                flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2' or params[j] == 'S2f':
                        flag = 1
                if not flag:
                    invalid_param = 1

            # Rex.
            elif params[i] == 'Rex':
                if rex:
                    invalid_param = 1
                rex = 1

            # Bond length.
            elif params[i] == 'r':
                if r:
                    invalid_param = 1
                r = 1

            # CSA.
            elif params[i] == 'CSA':
                if csa:
                    invalid_param = 1
                csa = 1

            # Unknown parameter.
            else:
                raise RelaxError, "The parameter " + params[i] + " is not supported."

            # The invalid parameter flag is set.
            if invalid_param:
                raise RelaxError, "The parameter array " + `params` + " contains an invalid combination of parameters."

        # Set up the model.
        self.model_setup(run, model, equation, params, res_num)


    def data_init(self, data):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Data structures which are initially None.
            none_data = [ 'equation',
                          'model',
                          's2',
                          's2f',
                          's2s',
                          'local_tm',
                          'te',
                          'tf',
                          'ts',
                          'rex',
                          'r',
                          'csa',
                          'chi2',
                          'iter',
                          'f_count',
                          'g_count',
                          'h_count',
                          'warning' ]
            if name in none_data:
                init_data = None

            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                setattr(data, name, init_data)


    def data_names(self, set='all'):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        model:  The model-free model name.

        equation:  The model-free equation type.

        params:  An array of the model-free parameter names associated with the model.

        s2:  S2.

        s2f:  S2f.

        s2s:  S2s.

        local_tm:  local tm.

        te:  te.

        tf:  tf.

        ts:  ts.

        rex:  Rex.

        r:  Bond length.

        csa:  CSA value.

        chi2:  Chi-squared value.

        iter:  Iterations.

        f_count:  Function count.

        g_count:  Gradient count.

        h_count:  Hessian count.

        warning:  Minimisation warning.
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('model')
            names.append('equation')
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('s2')
            names.append('s2f')
            names.append('s2s')
            names.append('local_tm')
            names.append('te')
            names.append('tf')
            names.append('ts')
            names.append('rex')
            names.append('r')
            names.append('csa')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        return names


    def default_value(self, param):
        """
        Model-free default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        _______________________________________________________________________________________
        |                                       |                    |                        |
        | Data type                             | Object name        | Value                  |
        |_______________________________________|____________________|________________________|
        |                                       |                    |                        |
        | Local tm                              | 'local_tm'         | 10 * 1e-9              |
        |                                       |                    |                        |
        | Order parameters S2, S2f, and S2s     | 's2', 's2f', 's2s' | 0.8                    |
        |                                       |                    |                        |
        | Correlation time te                   | 'te'               | 100 * 1e-12            |
        |                                       |                    |                        |
        | Correlation time tf                   | 'tf'               | 10 * 1e-12             |
        |                                       |                    |                        |
        | Correlation time ts                   | 'ts'               | 1000 * 1e-12           |
        |                                       |                    |                        |
        | Chemical exchange relaxation          | 'rex'              | 0.0                    |
        |                                       |                    |                        |
        | Bond length                           | 'r'                | 1.02 * 1e-10           |
        |                                       |                    |                        |
        | CSA                                   | 'csa'              | -170 * 1e-6            |
        |_______________________________________|____________________|________________________|

        """

        # Local tm.
        if param == 'local_tm':
            return 10.0 * 1e-9

        # {S2, S2f, S2s}.
        elif search('^S2', param):
            return 0.8

        # te.
        elif param == 'te':
            return 100.0 * 1e-12

        # tf.
        elif param == 'tf':
            return 10.0 * 1e-12

        # ts.
        elif param == 'ts':
            return 1000.0 * 1e-12

        # Rex.
        elif param == 'Rex':
            return 0.0

        # Bond length.
        elif param == 'r':
            return 1.02 * 1e-10

        # CSA.
        elif param == 'CSA':
            return -170 * 1e-6


    def delete(self, run):
        """Function for deleting all model-free data."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf_csa'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf_csa':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Get all data structure names.
        names = self.data_names()

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(data, name):
                    continue

                # Delete the data.
                delattr(data, name)

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def determine_param_set_type(self, run=None):
        """Determine the type of parameter set."""

        # Run name.
        if run:
            self.run = run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # If there is a local tm, fail if not all residues have a local tm parameter.
        local_tm = 0
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            # This code causes a bug after model elimination if the model has been eliminated (select = 0).
            #if not self.relax.data.res[self.run][i].select:
            #    continue

            # No params.
            if not hasattr(self.relax.data.res[self.run][i], 'params'):
                continue

            # Local tm.
            if local_tm == 0 and 'local_tm' in self.relax.data.res[self.run][i].params:
                local_tm = 1

            # Inconsistencies.
            elif local_tm == 1 and not 'local_tm' in self.relax.data.res[self.run][i].params:
                raise RelaxError, "All residues must either have a local tm parameter or not."

        # Check if any model-free parameters are allowed to vary.
        mf_all_fixed = 1
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            # This code causes a bug after model elimination if the model has been eliminated (select = 0).
            #if not self.relax.data.res[self.run][i].select:
            #    continue

            # Test the fixed flag.
            if not hasattr(self.relax.data.res[self.run][i], 'fixed'):
                mf_all_fixed = 0
                break
            if not self.relax.data.res[self.run][i].fixed:
                mf_all_fixed = 0
                break

        # Local tm.
        if local_tm:
            return 'local_tm'

        # Test if the diffusion tensor data is loaded.
        if not self.relax.data.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # 'diff' parameter set.
        if mf_all_fixed:
            # All parameters fixed.
            if self.relax.data.diff[self.run].fixed:
                raise RelaxError, "All parameters are fixed."

            return 'diff'

        # 'mf' parameter set.
        if self.relax.data.diff[self.run].fixed:
            return 'mf'

        # 'all' parameter set.
        else:
            return 'all'


    def disassemble_param_vector(self, index=None, sim_index=None):
        """Function for disassembling the parameter vector."""

        # Initialise.
        param_index = 0

        # Diffusion tensor parameters of the Monte Carlo simulations.
        if sim_index != None and (self.param_set == 'diff' or self.param_set == 'all'):
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                # Sim values.
                self.relax.data.diff[self.run].tm_sim[sim_index] = self.param_vector[0]

                # Parameter index.
                param_index = param_index + 1

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                # Sim values.
                self.relax.data.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                self.relax.data.diff[self.run].Da_sim[sim_index] = self.param_vector[1]
                self.relax.data.diff[self.run].theta_sim[sim_index] = self.param_vector[2]
                self.relax.data.diff[self.run].phi_sim[sim_index] = self.param_vector[3]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run, sim_index=sim_index)

                # Parameter index.
                param_index = param_index + 4

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # Sim values.
                self.relax.data.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                self.relax.data.diff[self.run].Da_sim[sim_index] = self.param_vector[1]
                self.relax.data.diff[self.run].Dr_sim[sim_index] = self.param_vector[2]
                self.relax.data.diff[self.run].alpha_sim[sim_index] = self.param_vector[3]
                self.relax.data.diff[self.run].beta_sim[sim_index] = self.param_vector[4]
                self.relax.data.diff[self.run].gamma_sim[sim_index] = self.param_vector[5]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run, sim_index=sim_index)

                # Parameter index.
                param_index = param_index + 6

        # Diffusion tensor parameters.
        elif self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                # Values.
                self.relax.data.diff[self.run].tm = self.param_vector[0]

                # Parameter index.
                param_index = param_index + 1

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                # Values.
                self.relax.data.diff[self.run].tm = self.param_vector[0]
                self.relax.data.diff[self.run].Da = self.param_vector[1]
                self.relax.data.diff[self.run].theta = self.param_vector[2]
                self.relax.data.diff[self.run].phi = self.param_vector[3]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run)

                # Parameter index.
                param_index = param_index + 4

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # Values.
                self.relax.data.diff[self.run].tm = self.param_vector[0]
                self.relax.data.diff[self.run].Da = self.param_vector[1]
                self.relax.data.diff[self.run].Dr = self.param_vector[2]
                self.relax.data.diff[self.run].alpha = self.param_vector[3]
                self.relax.data.diff[self.run].beta = self.param_vector[4]
                self.relax.data.diff[self.run].gamma = self.param_vector[5]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run)

                # Parameter index.
                param_index = param_index + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the residue data structure.
                data = self.relax.data.res[self.run][i]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(data.params)):
                    # Local tm.
                    if data.params[j] == 'local_tm':
                        if sim_index == None:
                            data.local_tm = self.param_vector[param_index]
                        else:
                            data.local_tm_sim[sim_index] = self.param_vector[param_index]

                    # S2.
                    elif data.params[j] == 'S2':
                        if sim_index == None:
                            data.s2 = self.param_vector[param_index]
                        else:
                            data.s2_sim[sim_index] = self.param_vector[param_index]

                    # S2f.
                    elif data.params[j] == 'S2f':
                        if sim_index == None:
                            data.s2f = self.param_vector[param_index]
                        else:
                            data.s2f_sim[sim_index] = self.param_vector[param_index]

                    # S2s.
                    elif data.params[j] == 'S2s':
                        if sim_index == None:
                            data.s2s = self.param_vector[param_index]
                        else:
                            data.s2s_sim[sim_index] = self.param_vector[param_index]

                    # te.
                    elif data.params[j] == 'te':
                        if sim_index == None:
                            data.te = self.param_vector[param_index]
                        else:
                            data.te_sim[sim_index] = self.param_vector[param_index]

                    # tf.
                    elif data.params[j] == 'tf':
                        if sim_index == None:
                            data.tf = self.param_vector[param_index]
                        else:
                            data.tf_sim[sim_index] = self.param_vector[param_index]

                    # ts.
                    elif data.params[j] == 'ts':
                        if sim_index == None:
                            data.ts = self.param_vector[param_index]
                        else:
                            data.ts_sim[sim_index] = self.param_vector[param_index]

                    # Rex.
                    elif data.params[j] == 'Rex':
                        if sim_index == None:
                            data.rex = self.param_vector[param_index]
                        else:
                            data.rex_sim[sim_index] = self.param_vector[param_index]

                    # r.
                    elif data.params[j] == 'r':
                        if sim_index == None:
                            data.r = self.param_vector[param_index]
                        else:
                            data.r_sim[sim_index] = self.param_vector[param_index]

                    # CSA.
                    elif data.params[j] == 'CSA':
                        if sim_index == None:
                            data.csa = self.param_vector[param_index]
                        else:
                            data.csa_sim[sim_index] = self.param_vector[param_index]

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

                    # Increment the parameter index.
                    param_index = param_index + 1

        # Calculate all order parameters after unpacking the vector.
        if self.param_set != 'diff':
            # Loop over all residues.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the residue data structure.
                data = self.relax.data.res[self.run][i]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Normal values.
                if sim_index == None:
                    # S2.
                    if 'S2' not in data.params and 'S2f' in data.params and 'S2s' in data.params:
                        data.s2 = data.s2f * data.s2s

                    # S2f.
                    if 'S2f' not in data.params and 'S2' in data.params and 'S2s' in data.params:
                        if data.s2s == 0.0:
                            data.s2f = 1e99
                        else:
                            data.s2f = data.s2 / data.s2s

                    # S2s.
                    if 'S2s' not in data.params and 'S2' in data.params and 'S2f' in data.params:
                        if data.s2f == 0.0:
                            data.s2s = 1e99
                        else:
                            data.s2s = data.s2 / data.s2f

                # Simulation values.
                else:
                    # S2.
                    if 'S2' not in data.params and 'S2f' in data.params and 'S2s' in data.params:
                        data.s2_sim[sim_index] = data.s2f_sim[sim_index] * data.s2s_sim[sim_index]

                    # S2f.
                    if 'S2f' not in data.params and 'S2' in data.params and 'S2s' in data.params:
                        if data.s2s_sim[sim_index] == 0.0:
                            data.s2f_sim[sim_index] = 1e99
                        else:
                            data.s2f_sim[sim_index] = data.s2_sim[sim_index] / data.s2s_sim[sim_index]

                    # S2s.
                    if 'S2s' not in data.params and 'S2' in data.params and 'S2f' in data.params:
                        if data.s2f_sim[sim_index] == 0.0:
                            data.s2s_sim[sim_index] = 1e99
                        else:
                            data.s2s_sim[sim_index] = data.s2_sim[sim_index] / data.s2f_sim[sim_index]


    def duplicate_data(self, new_run=None, old_run=None, instance=None, global_stats=0):
        """Function for duplicating data."""

        # self.run for determining the parameter set.
        self.run = old_run

        # Duplicate all non-residue specific data.
        for data_name in dir(self.relax.data):
            # Skip 'res'.
            if data_name == 'res':
                continue

            # Get the object.
            data = getattr(self.relax.data, data_name)

            # Skip the data if it is not a dictionary (or equivalent).
            if not hasattr(data, 'has_key'):
                continue

            # Skip the data if it doesn't contain the key 'old_run'.
            if not data.has_key(old_run):
                continue

            # If the dictionary already contains the key 'new_run', but the data is different, raise an error (skip PDB and diffusion data).
            if data_name != 'pdb' and data_name != 'diff' and data.has_key(new_run) and data[old_run] != data[new_run]:
                raise RelaxError, "The data between run " + `new_run` + " and run " + `old_run` + " is not consistent."

            # Skip the data if it contains the key 'new_run'.
            if data.has_key(new_run):
                continue

            # Duplicate the data.
            data[new_run] = deepcopy(data[old_run])

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Sequence specific data.
        if self.param_set == 'mf' or (self.param_set == 'local_tm' and not global_stats):
            # Create the sequence data if it does not exist.
            if not self.relax.data.res.has_key(new_run) or not len(self.relax.data.res[new_run]):
                # Add the new run to 'self.relax.data.res'.
                self.relax.data.res.add_list(new_run)

                # Fill the array 'self.relax.data.res[new_run]' with empty data containers and place sequence data into the array.
                for i in xrange(len(self.relax.data.res[old_run])):
                    # Append a data container.
                    self.relax.data.res[new_run].add_item()

                    # Insert the data.
                    self.relax.data.res[new_run][i].num = self.relax.data.res[old_run][i].num
                    self.relax.data.res[new_run][i].name = self.relax.data.res[old_run][i].name
                    self.relax.data.res[new_run][i].select = self.relax.data.res[old_run][i].select

            # Duplicate the residue specific data.
            self.relax.data.res[new_run][instance] = deepcopy(self.relax.data.res[old_run][instance])

        # Other data types.
        else:
            # Duplicate the residue specific data.
            self.relax.data.res[new_run] = deepcopy(self.relax.data.res[old_run])


    def eliminate(self, name, value, run, i, args):
        """
        Local tm model elimination rule
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The local tm, in some cases, may exceed the value expected for a global correlation time.
        Generally the tm value will be stuck at the upper limit defined for the parameter.  These
        models are eliminated using the rule:

            tm >= c

        The default value of c is 50 ns, although this can be overridden by supplying the value (in
        seconds) as the first element of the args tuple.


        Internal correlation times {te, tf, ts} model elimination rules
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        These parameters may experience the same problem as the local tm in that the model fails and
        the parameter value is stuck at the upper limit.  These parameters are constrained using the
        formula (te, tf, ts <= 2tm).  These failed models are eliminated using the rule:

            te, tf, ts >= c . tm

        The default value of c is 1.5.  Because of round-off errors and the constraint algorithm,
        setting c to 2 will result in no models being eliminated as the minimised parameters will
        always be less than 2tm.  The value can be changed by supplying the value as the second
        element of the tuple.


        Arguments
        ~~~~~~~~~

        The 'args' argument must be a tuple of length 2, the elements of which must be numbers.  For
        example, to eliminate models which have a local tm value greater than 25 ns and models with
        internal correlation times greater than 1.5 times tm, set 'args' to (25 * 1e-9, 1.5).
        """

        # Default values.
        c1 = 50.0 * 1e-9
        c2 = 1.5

        # Depack the arguments.
        if args != None:
            c1, c2 = args

        # Get the tm value.
        if self.param_set == 'local_tm':
            tm = self.relax.data.res[run][i].local_tm
        else:
            tm = self.relax.data.diff[run].tm

        # Local tm.
        if name == 'local_tm' and value >= c1:
            print "The local tm parameter of " + `value` + " is greater than " + `c1` + ", eliminating spin system " + `self.relax.data.res[run][i].num` + " " + self.relax.data.res[run][i].name + " of the run " + `run`
            return 1

        # Internal correlation times.
        if match('t[efs]', name) and value >= c2 * tm:
            print "The " + name + " value of " + `value` + " is greater than " + `c2 * tm` + ", eliminating spin system " + `self.relax.data.res[run][i].num` + " " + self.relax.data.res[run][i].name + " of the run " + `run`
            return 1

        # Accept model.
        return 0


    def get_param_names(self, run, i):
        """Function for returning a vector of parameter names."""

        # Arguments
        self.run = run

        # Skip residues where there is no data or errors.
        if not hasattr(self.relax.data.res[self.run][i], 'relax_data') or not hasattr(self.relax.data.res[self.run][i], 'relax_error'):
            return

        # Test if the model-free model has been setup.
        for j in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][j].select:
                continue

            # Not setup.
            if not self.relax.data.res[self.run][j].model:
                raise RelaxNoModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Residue index.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            index = i
        else:
            index = None

        # Assemble the parameter names.
        self.assemble_param_names(index=index)

        # Return the parameter names.
        return self.param_names


    def get_param_values(self, run, i, sim_index=None):
        """Function for returning a vector of parameter values."""

        # Arguments
        self.run = run

        # Skip residues where there is no data or errors.
        if not hasattr(self.relax.data.res[self.run][i], 'relax_data') or not hasattr(self.relax.data.res[self.run][i], 'relax_error'):
            return

        # Test if the model-free model has been setup.
        for j in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][j].select:
                continue

            # Not setup.
            if not self.relax.data.res[self.run][j].model:
                raise RelaxNoModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Residue index.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            index = i
        else:
            index = None

        # Assemble the parameter values.
        self.param_vector = self.assemble_param_vector(index=index, sim_index=sim_index)

        # Return the parameter names.
        return self.param_vector


    def grid_search(self, run, lower, upper, inc, constraints, print_flag, sim_index=None):
        """The grid search function."""

        # Arguments.
        self.lower = lower
        self.upper = upper
        self.inc = inc

        # Minimisation.
        self.minimise(run=run, min_algor='grid', constraints=constraints, print_flag=print_flag, sim_index=sim_index)


    def grid_search_setup(self, index=None):
        """The grid search setup function."""

        # The length of the parameter array.
        n = len(self.param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            print "Cannot run a grid search on a model with zero parameters, skipping the grid search."

        # Lower bounds.
        if self.lower != None:
            if len(self.lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if self.upper != None:
            if len(self.upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(self.inc) == list:
            if len(self.inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = self.inc
        elif type(self.inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(self.inc)
            inc = temp

        # Minimisation options initialisation.
        min_options = []
        m = 0

        # Minimisation options for diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion {tm}.
            if self.relax.data.diff[self.run].type == 'sphere':
                min_options.append([inc[0], 1.0 * 1e-9, 12.0 * 1e-9])
                m = m + 1

            # Spheroidal diffusion {tm, Da, theta, phi}.
            if self.relax.data.diff[self.run].type == 'spheroid':
                min_options.append([inc[0], 1.0 * 1e-9, 12.0 * 1e-9])
                if self.relax.data.diff[self.run].spheroid_type == 'prolate':
                    min_options.append([inc[1], 0.0, 1e7])
                elif self.relax.data.diff[self.run].spheroid_type == 'oblate':
                    min_options.append([inc[1], -1e7, 0.0])
                else:
                    min_options.append([inc[1], -1e7, 1e7])
                min_options.append([inc[2], 0.0, pi])
                min_options.append([inc[3], 0.0, pi])
                m = m + 4

            # Ellipsoidal diffusion {tm, Da, Dr, alpha, beta, gamma}.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                min_options.append([inc[0], 1.0 * 1e-9, 12.0 * 1e-9])
                min_options.append([inc[1], 0.0, 1e7])
                min_options.append([inc[2], 0.0, 1.0])
                min_options.append([inc[3], 0.0, pi])
                min_options.append([inc[4], 0.0, pi])
                min_options.append([inc[5], 0.0, pi])
                m = m + 6

        # Model-free parameters (residue specific parameters).
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[self.run][i].params)):
                    # Local tm.
                    if self.relax.data.res[self.run][i].params[j] == 'local_tm':
                        min_options.append([inc[m], 1.0 * 1e-9, 12.0 * 1e-9])

                    # {S2, S2f, S2s}.
                    elif match('S2', self.relax.data.res[self.run][i].params[j]):
                        min_options.append([inc[m], 0.0, 1.0])

                    # {te, tf, ts}.
                    elif match('t', self.relax.data.res[self.run][i].params[j]):
                        min_options.append([inc[m], 0.0, 500.0 * 1e-12])

                    # Rex.
                    elif self.relax.data.res[self.run][i].params[j] == 'Rex':
                        min_options.append([inc[m], 0.0, 5.0 / (2.0 * pi * self.relax.data.res[self.run][i].frq[0])**2])

                    # Bond length.
                    elif self.relax.data.res[self.run][i].params[j] == 'r':
                        min_options.append([inc[m], 1.0 * 1e-10, 1.05 * 1e-10])

                    # CSA.
                    elif self.relax.data.res[self.run][i].params[j] == 'CSA':
                        min_options.append([inc[m], -120 * 1e-6, -200 * 1e-6])

                    # Unknown option.
                    else:
                        raise RelaxError, "Unknown model-free parameter."

                    # Increment m.
                    m = m + 1

        # Set the lower and upper bounds if these are supplied.
        if self.lower != None:
            for j in xrange(n):
                if self.lower[j] != None:
                    min_options[j][1] = self.lower[j]
        if self.upper != None:
            for j in xrange(n):
                if self.upper[j] != None:
                    min_options[j][2] = self.upper[j]

        # Test if the grid is too large.
        self.grid_size = 1
        for i in xrange(len(min_options)):
            self.grid_size = self.grid_size * min_options[i][0]
        if type(self.grid_size) == long:
            raise RelaxError, "A grid search of size " + `self.grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / self.scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / self.scaling_matrix[j, j]

        return min_options


    def linear_constraints(self, index=None):
        """Function for setting up the model-free linear constraint matrices A and b.

        Standard notation
        ~~~~~~~~~~~~~~~~~

        The order parameter constraints are:

            0 <= S2 <= 1
            0 <= S2f <= 1
            0 <= S2s <= 1

        By substituting the formula S2 = S2f.S2s into the above inequalities, the additional two
        inequalities can be derived:

            S2 <= S2f
            S2 <= S2s

        Correlation time constraints are:

            te >= 0
            tf >= 0
            ts >= 0

            tf <= ts

            te, tf, ts <= 2 * tm

        Additional constraints used include:

            Rex >= 0
            0.9e-10 <= r <= 2e-10
            -300e-6 <= CSA <= 0


        Rearranged notation
        ~~~~~~~~~~~~~~~~~~~
        The above ineqality constraints can be rearranged into:

            S2 >= 0
            -S2 >= -1
            S2f >= 0
            -S2f >= -1
            S2s >= 0
            -S2s >= -1
            S2f - S2 >= 0
            S2s - S2 >= 0
            te >= 0
            tf >= 0
            ts >= 0
            ts - tf >= 0
            Rex >= 0
            r >= 0.9e-10
            -r >= -2e-10
            CSA >= -300e-6
            -CSA >= 0


        Matrix notation
        ~~~~~~~~~~~~~~~

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            |-1  0  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  1  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            | 0 -1  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  0  1  0  0  0  0  0  0 |     | S2  |      |    0    |
            |                           |     |     |      |         |
            | 0  0 -1  0  0  0  0  0  0 |     | S2f |      |   -1    |
            |                           |     |     |      |         |
            |-1  1  0  0  0  0  0  0  0 |     | S2s |      |    0    |
            |                           |     |     |      |         |
            |-1  0  1  0  0  0  0  0  0 |     | te  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  1  0  0  0  0  0 |  .  | tf  |  >=  |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  1  0  0  0  0 |     | ts  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  1  0  0  0 |     | Rex |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0 -1  1  0  0  0 |     |  r  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  0  1  0  0 |     | CSA |      |    0    |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  1  0 |                  | 0.9e-10 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0 -1  0 |                  | -2e-10  |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0  1 |                  | -300e-6 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0 -1 |                  |    0    |

        """

        # Upper limit flag for correlation times.
        upper_time_limit = 1

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(self.param_vector)
        zero_array = zeros(n, Float64)
        i = 0
        j = 0

        # Diffusion tensor parameters.
        if self.param_set != 'mf' and self.relax.data.diff.has_key(self.run):
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                # 0 <= tm <= 200 ns.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-200.0 * 1e-9 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                # 0 <= tm <= 200 ns.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-200.0 * 1e-9 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

                # Prolate diffusion, Da >= 0.
                if self.relax.data.diff[self.run].spheroid_type == 'prolate':
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    b.append(0.0 / self.scaling_matrix[i, i])
                    i = i + 1
                    j = j + 1

                    # Add two to i for the theta and phi parameters.
                    i = i + 2

                # Oblate diffusion, Da <= 0.
                elif self.relax.data.diff[self.run].spheroid_type == 'oblate':
                    A.append(zero_array * 0.0)
                    A[j][i] = -1.0
                    b.append(0.0 / self.scaling_matrix[i, i])
                    i = i + 1
                    j = j + 1

                    # Add two to i for the theta and phi parameters.
                    i = i + 2

                else:
                    # Add three to i for the Da, theta and phi parameters.
                    i = i + 3

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # 0 <= tm <= 200 ns.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-200.0 * 1e-9 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

                # Da >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # 0 <= Dr <= 1.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-1.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

                # Add three to i for the alpha, beta, and gamma parameters.
                i = i + 3

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for k in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][k].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and k != index:
                    continue

                # Save current value of i.
                old_i = i

                # Loop over the model-free parameters.
                for l in xrange(len(self.relax.data.res[self.run][k].params)):
                    # Local tm.
                    if self.relax.data.res[self.run][k].params[l] == 'local_tm':
                        if upper_time_limit:
                            # 0 <= tm <= 200 ns.
                            A.append(zero_array * 0.0)
                            A.append(zero_array * 0.0)
                            A[j][i] = 1.0
                            A[j+1][i] = -1.0
                            b.append(0.0 / self.scaling_matrix[i, i])
                            b.append(-200.0 * 1e-9 / self.scaling_matrix[i, i])
                            j = j + 2
                        else:
                            # 0 <= tm.
                            A.append(zero_array * 0.0)
                            A[j][i] = 1.0
                            b.append(0.0 / self.scaling_matrix[i, i])
                            j = j + 1

                    # Order parameters {S2, S2f, S2s}.
                    elif match('S2', self.relax.data.res[self.run][k].params[l]):
                        # 0 <= S2 <= 1.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        b.append(-1.0 / self.scaling_matrix[i, i])
                        j = j + 2

                        # S2 <= S2f and S2 <= S2s.
                        if self.relax.data.res[self.run][k].params[l] == 'S2':
                            for m in xrange(len(self.relax.data.res[self.run][k].params)):
                                if self.relax.data.res[self.run][k].params[m] == 'S2f' or self.relax.data.res[self.run][k].params[m] == 'S2s':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = -1.0
                                    A[j][old_i+m] = 1.0
                                    b.append(0.0)
                                    j = j + 1

                    # Correlation times {te, tf, ts}.
                    elif match('t[efs]', self.relax.data.res[self.run][k].params[l]):
                        # te, tf, ts >= 0.
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                        # tf <= ts.
                        if self.relax.data.res[self.run][k].params[l] == 'ts':
                            for m in xrange(len(self.relax.data.res[self.run][k].params)):
                                if self.relax.data.res[self.run][k].params[m] == 'tf':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = 1.0
                                    A[j][old_i+m] = -1.0
                                    b.append(0.0)
                                    j = j + 1

                        # te, tf, ts <= 2 * tm.  (tf not needed because tf <= ts).
                        if upper_time_limit:
                            if not self.relax.data.res[self.run][k].params[l] == 'tf':
                                if self.param_set == 'mf':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = -1.0
                                    b.append(-2.0 * self.relax.data.diff[self.run].tm / self.scaling_matrix[i, i])
                                else:
                                    A.append(zero_array * 0.0)
                                    A[j][0] = 2.0
                                    A[j][i] = -1.0
                                    b.append(0.0)

                                j = j + 1

                    # Rex.
                    elif self.relax.data.res[self.run][k].params[l] == 'Rex':
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                    # Bond length.
                    elif self.relax.data.res[self.run][k].params[l] == 'r':
                        # 0.9e-10 <= r <= 2e-10.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.9e-10 / self.scaling_matrix[i, i])
                        b.append(-2e-10 / self.scaling_matrix[i, i])
                        j = j + 2

                    # CSA.
                    elif self.relax.data.res[self.run][k].params[l] == 'CSA':
                        # -300e-6 <= CSA <= 0.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(-300e-6 / self.scaling_matrix[i, i])
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 2

                    # Increment i.
                    i = i + 1

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def map_bounds(self, run, param):
        """The function for creating bounds for the mapping function."""

        # Arguments.
        self.run = run

        # {S2, S2f, S2s}.
        if search('^s2', param):
            return [0, 1]

        # {local tm, te, tf, ts}.
        elif search('^t', param) or param == 'local_tm':
            return [0, 1e-8]

        # Rex.
        elif param == 'rex':
            return [0, 30.0 / (2.0 * pi * self.relax.data.frq[self.run][0])**2]

        # Bond length.
        elif param == 'r':
            return [1.0 * 1e-10, 1.1 * 1e-10]

        # CSA.
        elif param == 'csa':
            return [-100 * 1e-6, -300 * 1e-6]


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, scaling=1, print_flag=0, sim_index=None):
        """Model-free minimisation.

        Three types of parameter sets exist for which minimisation is different.  These are:
            'mf' - Model-free parameters for single residues.
            'diff' - Diffusion tensor parameters.
            'all' - All model-free and all diffusion tensor parameters.
        """

        # Arguments.
        self.run = run
        self.print_flag = print_flag

        # Test if the sequence data for self.run is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the model-free model has been setup.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # Not setup.
            if not self.relax.data.res[self.run][i].model:
                raise RelaxNoModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Parameter set for the back-calculate function.
        if min_algor == 'back_calc' and self.param_set != 'local_tm':
            self.param_set = 'mf'

        # Test if diffusion tensor data for the run exists.
        if self.param_set != 'local_tm' and not self.relax.data.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Tests for the PDB file and unit vectors.
        if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere':
            # Test if the PDB file has been loaded.
            if not self.relax.data.pdb.has_key(self.run):
                raise RelaxNoPdbError, self.run

            # Test if unit vectors exist.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Unit vector.
                if not hasattr(self.relax.data.res[self.run][i], 'xh_vect'):
                    raise RelaxNoVectorsError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if self.param_set == 'diff':
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                unset_param = self.are_mf_params_set(i)
                if unset_param != None:
                    raise RelaxNoValueError, unset_param

        # Print out.
        if self.print_flag >= 1:
            if self.param_set == 'mf':
                print "Only the model-free parameters for single residues will be used."
            elif self.param_set == 'local_mf':
                print "Only a local tm value together with the model-free parameters for single residues will be used."
            elif self.param_set == 'diff':
                print "Only diffusion tensor parameters will be used."
            elif self.param_set == 'all':
                print "The diffusion tensor parameters together with the model-free parameters for all residues will be used."

        # Count the total number of residues and test if the CSA and bond length values have been set.
        num_res = 0
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # CSA value.
            if not hasattr(self.relax.data.res[self.run][i], 'csa') or self.relax.data.res[self.run][i].csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(self.relax.data.res[self.run][i], 'r') or self.relax.data.res[self.run][i].r == None:
                raise RelaxNoValueError, "bond length"

            # Increment the number of residues.
            num_res = num_res + 1

        # Number of residues, minimisation instances, and data sets for each parameter set type.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            num_instances = len(self.relax.data.res[self.run])
            num_data_sets = 1
            num_res = 1
        elif self.param_set == 'diff' or self.param_set == 'all':
            num_instances = 1
            num_data_sets = len(self.relax.data.res[self.run])

        # Number of residues, minimisation instances, and data sets for the back-calculate function.
        if min_algor == 'back_calc':
            num_instances = 1
            num_data_sets = 0
            num_res = 1


        # Loop over the minimisation instances.
        #######################################
        
        for i in xrange(num_instances):
            # Set the residue index.
            if min_algor == 'back_calc':
                index = min_options[0]
            else:
                index = i

            # The residue index for the global models.
            if self.param_set == 'diff' or self.param_set == 'all':
                index = None

            # Individual residue stuff.
            if (self.param_set == 'mf' or self.param_set == 'local_tm') and not min_algor == 'back_calc':
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Skip residues where there is no data or errors.
                if not hasattr(self.relax.data.res[self.run][i], 'relax_data') or not hasattr(self.relax.data.res[self.run][i], 'relax_error'):
                    continue

            # Parameter vector and diagonal scaling.
            if min_algor == 'back_calc':
                # Create the initial parameter vector.
                self.param_vector = self.assemble_param_vector(index=index)

                # Diagonal scaling.
                self.scaling_matrix = None

            else:
                # Create the initial parameter vector.
                self.param_vector = self.assemble_param_vector(index=index, sim_index=sim_index)

                # Diagonal scaling.
                self.assemble_scaling_matrix(index=index, scaling=scaling)
                if self.scaling_matrix:
                    self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                min_options = self.grid_search_setup(index=index)

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                min_options = matrixmultiply(inverse(self.scaling_matrix), min_options)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(index=index)

            # Print out.
            if self.print_flag >= 1:
                # Individual residue stuff.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    if self.print_flag >= 2:
                        print "\n\n"
                    string = "Fitting to residue: " + `self.relax.data.res[self.run][index].num` + " " + self.relax.data.res[self.run][index].name
                    print "\n\n" + string
                    print len(string) * '~'
                if match('^[Gg]rid', min_algor):
                    print "Unconstrained grid search size: " + `self.grid_size` + " (constraints may decrease this size).\n"

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            self.iter_count = 0
            self.f_count = 0
            self.g_count = 0
            self.h_count = 0

            # Initialise the data structures for the model-free function.
            cst = []
            csea = []
            csa_data_ax = []
            csa_data_by = []
            csa_data_cz = []
            relax_data = []
            relax_error = []
            equations = []
            param_types = []
            param_values = None
            r = []
            csa = []
            num_frq = []
            frq = []
            num_ri = []
            num_csa = []
            remap_table = []
            noe_r1_table = []
            ri_labels = []
            csa_labels = []
            num_params = []
            xh_unit_vectors = []
	    xy_vect_num = []
	    xy_data = []
            if self.param_set == 'local_tm':
                mf_params = []
            elif self.param_set == 'diff':
                param_values = []

            # Set up the data for the back_calc function.
            if min_algor == 'back_calc':
                # The data.
                relax_data = [0.0]
                relax_error = [0.000001]
                equations = [self.relax.data.res[self.run][index].equation]
                param_types = [self.relax.data.res[self.run][index].params]
                r = [self.relax.data.res[self.run][index].r]
                csa = [self.relax.data.res[self.run][index].csa]
                num_frq = [1]
                frq = [[min_options[3]]]
                num_ri = [1]
                num_csa = [self.relax.data.res[self.run][index].num_csa]
                cst = [self.relax.data.res[self.run][index].cst]
                csea = [self.relax.data.res[self.run][index].csea]
                csa_data_ax = [self.relax.data.res[self.run][index].csa_data_ax]
                csa_data_by = [self.relax.data.res[self.run][index].csa_data_by]
                csa_data_cz = [self.relax.data.res[self.run][index].csa_data_cz]
                csa_labels = [self.relax.data.res[self.run][index].csa_labels]
		xy_vect_num = [self.relax.data.res[self.run][index].xy_vect_num]
		#print self.relax.data.res[self.run][index].xy_vect_num
		if self.relax.data.res[self.run][index].xy_vect_num > 0:
		    xy_data = [self.relax.data.res[self.run][index].xy_data]
		
                remap_table = [[0]]
                noe_r1_table = [[None]]
                ri_labels = [[min_options[1]]]
                if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere':
                    xh_unit_vectors = [self.relax.data.res[self.run][index].xh_vect]
                else:
                    xh_unit_vectors = [None]

                # Count the number of model-free parameters for the residue index.
                num_params = [len(self.relax.data.res[self.run][index].params)]


            # Loop over the number of data sets.
            for j in xrange(num_data_sets):
                # Set the sequence index.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    seq_index = i
                else:
                    seq_index = j

                # Alias the data structure.
                data = self.relax.data.res[self.run][seq_index]
                # Skip unselected residues.
                if not data.select:
                    continue

                # Skip residues where there is no data or errors.
                if not hasattr(data, 'relax_data') or not hasattr(data, 'relax_error'):
                    continue

                # Make sure that the errors are strictly positive numbers.
                for k in xrange(len(data.relax_error)):
                    if data.relax_error[k] == 0.0:
                        raise RelaxError, "Zero error for residue '" + `data.num` + " " + data.name + "', minimisation not possible."
                    elif data.relax_error[k] < 0.0:
                        raise RelaxError, "Negative error for residue '" + `data.num` + " " + data.name + "', minimisation not possible."

                # Repackage the data.
                if sim_index == None:
                    relax_data.append(data.relax_data)
                    cst.append(data.cst)
                    csea.append(data.csea)
                    csa_data_ax.append(data.csa_data_ax)
                    csa_data_by.append(data.csa_data_by)
                    csa_data_cz.append(data.csa_data_cz)
                else:
                    relax_data.append(data.relax_sim_data[sim_index])
                    cst.append(data.cst)
                    csea.append(data.csea)
                    csa_data_ax.append(data.csa_data_ax)
                    csa_data_by.append(data.csa_data_by)
                    csa_data_cz.append(data.csa_data_cz)
                relax_error.append(data.relax_error)
                equations.append(data.equation)
                param_types.append(data.params)
                num_frq.append(data.num_frq)
                frq.append(data.frq)
                num_ri.append(data.num_ri)
                num_csa.append(data.num_csa)
                remap_table.append(data.remap_table)
                noe_r1_table.append(data.noe_r1_table)
                ri_labels.append(data.ri_labels)
                csa_labels.append(data.csa_labels)
		if self.param_set != 'local_tm':
		    xy_vect_num.append(data.xy_vect_num)
		    if data.xy_vect_num > 0:
		        xy_data.append(data.xy_data)
		else:
		    xy_vect_num.append(0)
		
                if sim_index == None or self.param_set == 'diff':
                    r.append(data.r)
                    csa.append(data.csa)
                else:
                    r.append(data.r_sim[sim_index])
                    csa.append(data.csa_sim[sim_index])

                # Model-free parameter values.
                if self.param_set == 'local_tm':
                    pass

                # Vectors.
                if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere':
                    xh_unit_vectors.append(data.xh_vect)
                else:
                    xh_unit_vectors.append(None)

                # Count the number of model-free parameters for the residue index.
                num_params.append(len(data.params))

                # Repackage the parameter values for minimising just the diffusion tensor parameters.
                if self.param_set == 'diff':
                    param_values.append(self.assemble_param_vector(param_set='mf'))

            # Convert to Numeric arrays.
            for k in xrange(len(relax_data)):
                relax_data[k] = array(relax_data[k], Float64)
                relax_error[k] = array(relax_error[k], Float64)

            # Convert to Numeric arrays.
            for k in xrange(len(csa_data_ax)):
                cst[k] = array(cst[k], Float64)
                csea[k] = array(csea[k], Float64)
                csa_data_ax[k] = array(csa_data_ax[k], Float64)
                csa_data_by[k] = array(csa_data_by[k], Float64)
                csa_data_cz[k] = array(csa_data_cz[k], Float64)

            # Diffusion tensor type.
            if self.param_set == 'local_tm':
                diff_type = 'sphere'
            else:
                diff_type = self.relax.data.diff[self.run].type

            # Package the diffusion tensor parameters.
            diff_params = None
            if self.param_set == 'mf':
                # Alias.
                data = self.relax.data.diff[self.run]

                # Spherical diffusion.
                if diff_type == 'sphere':
                    diff_params = [data.tm]

                # Spheroidal diffusion.
                elif diff_type == 'spheroid':
                    diff_params = [data.tm, data.Da, data.theta, data.phi]

                # Ellipsoidal diffusion.
                elif diff_type == 'ellipsoid':
                    diff_params = [data.tm, data.Da, data.Dr, data.alpha, data.beta, data.gamma]
            elif min_algor == 'back_calc' and self.param_set == 'local_tm':
                # Spherical diffusion.
                diff_params = [self.relax.data.res[self.run][index].local_tm]



            # Initialise the function to minimise.
            ######################################

            self.mf_csa = Mf_csa(init_params=self.param_vector, param_set=self.param_set, diff_type=diff_type, diff_params=diff_params, scaling_matrix=self.scaling_matrix, num_res=num_res, equations=equations, param_types=param_types, param_values=param_values, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=self.relax.data.gx, gh=self.relax.data.gh, g_ratio=self.relax.data.g_ratio, h_bar=self.relax.data.h_bar, mu0=self.relax.data.mu0, num_params=num_params, vectors=xh_unit_vectors, csa_data_ax=csa_data_ax, csa_data_by=csa_data_by, csa_data_cz=csa_data_cz, csa_labels=csa_labels, num_csa=num_csa, cst=cst, csea=csea, xy_vect_num=xy_vect_num, xy_data=xy_data)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor):
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Total number of ri.
                number_ri = 0
                for k in xrange(len(relax_error)):
                    number_ri = number_ri + len(relax_error[k])

                # Reconstruct the error data structure.
                lm_error = zeros(number_ri, Float64)
                index = 0
                for k in xrange(len(relax_error)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.mf_csa.lm_dri, lm_error)


            # Back-calculation.
            ###################

            if min_algor == 'back_calc':
                return self.mf_csa.calc_ri()


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=self.mf_csa.func, dfunc=self.mf_csa.dfunc, d2func=self.mf_csa.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
            else:
                results = generic_minimise(func=self.mf_csa.func, dfunc=self.mf_csa.dfunc, d2func=self.mf_csa.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
            if results == None:
                return
            self.param_vector, self.func, iter, fc, gc, hc, self.warning = results
            self.iter_count = self.iter_count + iter
            self.f_count = self.f_count + fc
            self.g_count = self.g_count + gc
            self.h_count = self.h_count + hc

            # Catch infinite chi-squared values.
            if isInf(self.func):
                raise RelaxInfError, 'chi-squared'

            # Catch chi-squared values of NaN.
            if isNaN(self.func):
                raise RelaxNaNError, 'chi-squared'

            # Scaling.
            if scaling:
                self.param_vector = matrixmultiply(self.scaling_matrix, self.param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(index=index, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Sequence specific minimisation statistics.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    # Chi-squared statistic.
                    self.relax.data.res[self.run][i].chi2_sim[sim_index] = self.func

                    # Iterations.
                    self.relax.data.res[self.run][i].iter_sim[sim_index] = self.iter_count

                    # Function evaluations.
                    self.relax.data.res[self.run][i].f_count_sim[sim_index] = self.f_count

                    # Gradient evaluations.
                    self.relax.data.res[self.run][i].g_count_sim[sim_index] = self.g_count

                    # Hessian evaluations.
                    self.relax.data.res[self.run][i].h_count_sim[sim_index] = self.h_count

                    # Warning.
                    self.relax.data.res[self.run][i].warning_sim[sim_index] = self.warning

                # Global minimisation statistics.
                elif self.param_set == 'diff' or self.param_set == 'all':
                    # Chi-squared statistic.
                    self.relax.data.chi2_sim[self.run][sim_index] = self.func

                    # Iterations.
                    self.relax.data.iter_sim[self.run][sim_index] = self.iter_count

                    # Function evaluations.
                    self.relax.data.f_count_sim[self.run][sim_index] = self.f_count

                    # Gradient evaluations.
                    self.relax.data.g_count_sim[self.run][sim_index] = self.g_count

                    # Hessian evaluations.
                    self.relax.data.h_count_sim[self.run][sim_index] = self.h_count

                    # Warning.
                    self.relax.data.warning_sim[self.run][sim_index] = self.warning

            # Normal statistics.
            else:
                # Sequence specific minimisation statistics.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    # Chi-squared statistic.
                    self.relax.data.res[self.run][i].chi2 = self.func

                    # Iterations.
                    self.relax.data.res[self.run][i].iter = self.iter_count

                    # Function evaluations.
                    self.relax.data.res[self.run][i].f_count = self.f_count

                    # Gradient evaluations.
                    self.relax.data.res[self.run][i].g_count = self.g_count

                    # Hessian evaluations.
                    self.relax.data.res[self.run][i].h_count = self.h_count

                    # Warning.
                    self.relax.data.res[self.run][i].warning = self.warning

                # Global minimisation statistics.
                elif self.param_set == 'diff' or self.param_set == 'all':
                    # Chi-squared statistic.
                    self.relax.data.chi2[self.run] = self.func

                    # Iterations.
                    self.relax.data.iter[self.run] = self.iter_count

                    # Function evaluations.
                    self.relax.data.f_count[self.run] = self.f_count

                    # Gradient evaluations.
                    self.relax.data.g_count[self.run] = self.g_count

                    # Hessian evaluations.
                    self.relax.data.h_count[self.run] = self.h_count

                    # Warning.
                    self.relax.data.warning[self.run] = self.warning


    def model_setup(self, run=None, model=None, equation=None, params=None, res_num=None):
        """Function for updating various data structures depending on the model selected."""

        # Test that no diffusion tensor exists for the run if local tm is a parameter in the model.
        for param in params:
            if param == 'local_tm' and self.relax.data.diff.has_key(run):
                raise RelaxTensorError, run

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # If res_num is set, then skip all other residues.
            if res_num != None and res_num != self.relax.data.res[run][i].num:
                continue

            # Initialise the data structures (if needed).
            self.data_init(self.relax.data.res[run][i])

            # Model-free model, equation, and parameter types.
            self.relax.data.res[run][i].model = model
            self.relax.data.res[run][i].equation = equation
            self.relax.data.res[run][i].params = params


    def model_statistics(self, run=None, instance=None, global_stats=None):
        """Function for returning k, n, and chi2.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.
        """

        # Arguments.
        self.run = run

        # Determine if local or global statistics will be returned.
        if global_stats == None:
            global_stats = 1
            for i in xrange(len(self.relax.data.res[self.run])):
                if hasattr(self.relax.data.res[self.run][i], 'chi2') and self.relax.data.res[self.run][i].chi2 != None:
                    global_stats = 0
                    break

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Statistics for a single residue.
        if not global_stats:
            # Skip unselected residues.
            if not self.relax.data.res[self.run][instance].select:
                return None, None, None

            # Missing data sets.
            if not hasattr(self.relax.data.res[self.run][instance], 'relax_data'):
                return None, None, None

            # Count the number of parameters.
            self.param_vector = self.assemble_param_vector(index=instance)
            k = len(self.param_vector)

            # Count the number of data points.
            n = len(self.relax.data.res[self.run][instance].relax_data)

            # The chi2 value.
            chi2 = self.relax.data.res[self.run][instance].chi2

        # Global stats.
        elif global_stats:
            # Count the number of parameters.
            self.param_vector = self.assemble_param_vector()
            k = len(self.param_vector)

            # Count the number of data points.
            n = 0
            chi2 = 0
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Skip residues with no relaxation data.
                if not hasattr(self.relax.data.res[self.run][i], 'relax_data') or not len(self.relax.data.res[self.run][i].relax_data):
                    continue

                n = n + len(self.relax.data.res[self.run][i].relax_data)

                # Local tm models.
                if self.param_set == 'local_tm':
                    chi2 = chi2 + self.relax.data.res[self.run][i].chi2

            # The chi2 value.
            if self.param_set != 'local_tm':
                chi2 = self.relax.data.chi2[self.run]

        # Return the data.
        return k, n, chi2


    def num_instances(self, run=None):
        """Function for returning the number of instances."""

        # Arguments.
        self.run = run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            return 0

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Sequence specific data.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            return len(self.relax.data.res[self.run])

        # Other data.
        elif self.param_set == 'diff' or self.param_set == 'all':
            return 1

        # Should not be here.
        else:
            raise RelaxFault


    def overfit_deselect(self, run):
        """Function for deselecting residues without sufficient data to support minimisation"""

        # Test sequence data exists.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Loop over residue data:
        for residue in self.relax.data.res[run]:
            # Skip unselected data:
            if not residue.select:
                continue

            # Check for data structure.
            if not hasattr(residue, 'relax_data'):
                residue.select = 0
                continue

            # Require 3 or more data points
            if len(residue.relax_data) < 3:
                residue.select = 0
                continue

            # Require at least as many data points as params to prevent over-fitting
            if hasattr(residue, 'params'):
                if len(residue.params) > len(residue.relax_data):
                    residue.select = 0
                    continue

            # Test for structural data if required
            if hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(run):
                if self.relax.data.diff[run].type == 'spheroid' or self.relax.data.diff[run].type == 'ellipsoid':
                    if not hasattr(residue, 'xh_vect'):
                        residue.select = 0
                        continue


    def read_columnar_col_numbers(self, header):
        """Function for sorting the column numbers from the columnar formatted results file."""

        # Initialise the hash.
        self.col = {}

        # Loop over the columns.
        for i in xrange(len(header)):
            # Residue info.
            if header[i] == 'Num':
                self.col['num'] = i
            elif header[i] == 'Name':
                self.col['name'] = i
            elif header[i] == 'Selected':
                self.col['select'] = i
            elif header[i] == 'Data_set':
                self.col['data_set'] = i
            elif header[i] == 'Nucleus':
                self.col['nucleus'] = i
            elif header[i] == 'Model':
                self.col['model'] = i
            elif header[i] == 'Equation':
                self.col['eqi'] = i
            elif header[i] == 'Params':
                self.col['params'] = i
            elif header[i] == 'Param_set':
                self.col['param_set'] = i

            # Parameters.
            elif header[i] == 'S2':
                self.col['s2'] = i
            elif header[i] == 'S2f':
                self.col['s2f'] = i
            elif header[i] == 'S2s':
                self.col['s2s'] = i
            elif search('^Local_tm', header[i]):
                self.col['local_tm'] = i
            elif search('^te', header[i]):
                self.col['te'] = i
            elif search('^tf', header[i]):
                self.col['tf'] = i
            elif search('^ts', header[i]):
                self.col['ts'] = i
            elif search('^Rex', header[i]):
                self.col['rex'] = i
            elif search('^Bond_length', header[i]):
                self.col['r'] = i
            elif search('^CSA', header[i]):
                self.col['csa'] = i

            # Minimisation info.
            elif header[i] == 'Chi-squared':
                self.col['chi2'] = i
            elif header[i] == 'Iter':
                self.col['iter'] = i
            elif header[i] == 'f_count':
                self.col['f_count'] = i
            elif header[i] == 'g_count':
                self.col['g_count'] = i
            elif header[i] == 'h_count':
                self.col['h_count'] = i
            elif header[i] == 'Warning':
                self.col['warn'] = i

            # Diffusion tensor.
            elif header[i] == 'Diff_type':
                self.col['diff_type'] = i
            elif header[i] == 'tm_(s)':
                self.col['tm'] = i
            elif header[i] == 'Da_(1/s)':
                self.col['da'] = i
            elif header[i] == 'theta_(deg)':
                self.col['theta'] = i
            elif header[i] == 'phi_(deg)':
                self.col['phi'] = i
            elif header[i] == 'Da_(1/s)':
                self.col['da'] = i
            elif header[i] == 'Dr_(1/s)':
                self.col['dr'] = i
            elif header[i] == 'alpha_(deg)':
                self.col['alpha'] = i
            elif header[i] == 'beta_(deg)':
                self.col['beta'] = i
            elif header[i] == 'gamma_(deg)':
                self.col['gamma'] = i

            # PDB and XH vector.
            elif header[i] == 'PDB':
                self.col['pdb'] = i
            elif header[i] == 'PDB_model':
                self.col['pdb_model'] = i
            elif header[i] == 'PDB_heteronuc':
                self.col['pdb_heteronuc'] = i
            elif header[i] == 'PDB_proton':
                self.col['pdb_proton'] = i
            elif header[i] == 'XH_vector':
                self.col['xh_vect'] = i

            # Relaxation data.
            elif header[i] == 'Ri_labels':
                self.col['ri_labels'] = i
            elif header[i] == 'Remap_table':
                self.col['remap_table'] = i
            elif header[i] == 'Frq_labels':
                self.col['frq_labels'] = i
            elif header[i] == 'Frequencies':
                self.col['frq'] = i


    def read_columnar_diff_tensor(self):
        """Function for setting up the diffusion tensor from the columnar formatted results file."""

        # The diffusion tensor type.
        diff_type = self.file_line[self.col['diff_type']]
        if diff_type == 'None':
            diff_type = None

        # Sphere.
        if diff_type == 'sphere':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = tm

            # Errors.
            elif self.data_set == 'error':
                self.relax.data.diff[self.run].tm_err = tm

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(self.relax.data.diff[self.run], 'tm_sim'):
                    self.relax.data.diff[self.run].tm_sim = []

                # Append the value.
                self.relax.data.diff[self.run].tm_sim.append(tm)


        # Spheroid.
        elif diff_type == 'spheroid' or diff_type == 'oblate' or diff_type == 'prolate':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
                Da = float(self.file_line[self.col['da']])
                theta = float(self.file_line[self.col['theta']]) / 360.0 * 2.0 * pi
                phi = float(self.file_line[self.col['phi']]) / 360.0 * 2.0 * pi
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = [tm, Da, theta, phi]

            # Errors.
            elif self.data_set == 'error':
                self.relax.data.diff[self.run].tm_err = tm
                self.relax.data.diff[self.run].Da_err = Da
                self.relax.data.diff[self.run].theta_err = theta
                self.relax.data.diff[self.run].phi_err = phi

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(self.relax.data.diff[self.run], 'tm_sim'):
                    self.relax.data.diff[self.run].tm_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'Da_sim'):
                    self.relax.data.diff[self.run].Da_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'theta_sim'):
                    self.relax.data.diff[self.run].theta_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'phi_sim'):
                    self.relax.data.diff[self.run].phi_sim = []

                # Append the value.
                self.relax.data.diff[self.run].tm_sim.append(tm)
                self.relax.data.diff[self.run].Da_sim.append(Da)
                self.relax.data.diff[self.run].theta_sim.append(theta)
                self.relax.data.diff[self.run].phi_sim.append(phi)


        # Ellipsoid.
        elif diff_type == 'ellipsoid':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
                Da = float(self.file_line[self.col['da']])
                Dr = float(self.file_line[self.col['dr']])
                alpha = float(self.file_line[self.col['alpha']]) / 360.0 * 2.0 * pi
                beta = float(self.file_line[self.col['beta']]) / 360.0 * 2.0 * pi
                gamma = float(self.file_line[self.col['gamma']]) / 360.0 * 2.0 * pi
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = [tm, Da, Dr, alpha, beta, gamma]

            # Errors.
            elif self.data_set == 'error':
                self.relax.data.diff[self.run].tm_err = tm
                self.relax.data.diff[self.run].Da_err = Da
                self.relax.data.diff[self.run].Dr_err = Dr
                self.relax.data.diff[self.run].alpha_err = alpha
                self.relax.data.diff[self.run].beta_err = beta
                self.relax.data.diff[self.run].gamma_err = gamma

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(self.relax.data.diff[self.run], 'tm_sim'):
                    self.relax.data.diff[self.run].tm_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'Da_sim'):
                    self.relax.data.diff[self.run].Da_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'Dr_sim'):
                    self.relax.data.diff[self.run].Dr_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'alpha_sim'):
                    self.relax.data.diff[self.run].alpha_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'beta_sim'):
                    self.relax.data.diff[self.run].beta_sim = []
                if not hasattr(self.relax.data.diff[self.run], 'gamma_sim'):
                    self.relax.data.diff[self.run].gamma_sim = []

                # Append the value.
                self.relax.data.diff[self.run].tm_sim.append(tm)
                self.relax.data.diff[self.run].Da_sim.append(Da)
                self.relax.data.diff[self.run].Dr_sim.append(Dr)
                self.relax.data.diff[self.run].alpha_sim.append(alpha)
                self.relax.data.diff[self.run].beta_sim.append(beta)
                self.relax.data.diff[self.run].gamma_sim.append(gamma)


        # Set the diffusion tensor.
        if self.data_set == 'value' and diff_type:
            # Sort out the spheroid type.
            spheroid_type = None
            if diff_type == 'oblate' or diff_type == 'prolate':
                spheroid_type = diff_type

            # Set the diffusion tensor.
            self.relax.generic.diffusion_tensor.init(run=self.run, params=diff_params, angle_units='rad', spheroid_type=spheroid_type)


    def read_columnar_find_index(self):
        """Function for generating the sequence and or returning the residue index."""

        # Residue number and name.
        try:
            self.res_num = int(self.file_line[self.col['num']])
        except ValueError:
            raise RelaxError, "The residue number " + self.file_line[self.col['num']] + " is not an integer."
        self.res_name = self.file_line[self.col['name']]

        # Find the residue index.
        res_index = None
        for j in xrange(len(self.relax.data.res[self.run])):
            if self.relax.data.res[self.run][j].num == self.res_num and self.relax.data.res[self.run][j].name == self.res_name:
                res_index = j
                break
        if res_index == None:
            raise RelaxError, "Residue " + `self.res_num` + " " + self.res_name + " cannot be found in the sequence."

        # Return the index.
        return res_index


    def read_columnar_model_free_data(self):
        """Function for reading the model-free data."""

        # Reassign data structure.
        data = self.relax.data.res[self.run][self.res_index]

        # Set up the model-free models.
        if self.data_set == 'value':
            # Get the model-free model.
            model = self.file_line[self.col['model']]

            # Get the model-free equation.
            equation = self.file_line[self.col['eqi']]

            # Get the model-free parameters.
            params = eval(self.file_line[self.col['params']])

            # Fix for the 1.2 relax versions whereby the parameter 'tm' was renamed to 'local_tm' (which occurred in version 1.2.5).
            for i in xrange(len(params)):
                if params[i] == 'tm':
                    params[i] = 'local_tm'

            # Set up the model-free model.
            if model and equation:
                self.model_setup(self.run, model=model, equation=equation, params=params, res_num=self.res_num)

        # Values.
        if self.data_set == 'value':
            # S2.
            try:
                data.s2 = float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2')
            except ValueError:
                data.s2 = None

            # S2f.
            try:
                data.s2f = float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f')
            except ValueError:
                data.s2f = None

            # S2s.
            try:
                data.s2s = float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s')
            except ValueError:
                data.s2s = None

            # Local tm.
            try:
                data.local_tm = float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm')
            except ValueError:
                data.local_tm = None

            # te.
            try:
                data.te = float(self.file_line[self.col['te']]) * self.return_conversion_factor('te')
            except ValueError:
                data.te = None

            # tf.
            try:
                data.tf = float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf')
            except ValueError:
                data.tf = None

            # ts.
            try:
                data.ts = float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts')
            except ValueError:
                data.ts = None

            # Rex.
            try:
                data.rex = float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex')
            except ValueError:
                data.rex = None

            # Bond length.
            try:
                data.r = float(self.file_line[self.col['r']]) * self.return_conversion_factor('r')
            except ValueError:
                data.r = None

            # CSA.
            try:
                data.csa = float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa')
            except ValueError:
                data.csa = None

            # Minimisation details (global minimisation results).
            if self.param_set == 'diff' or self.param_set == 'all':
                self.relax.data.chi2[self.run] = eval(self.file_line[self.col['chi2']])
                self.relax.data.iter[self.run] = eval(self.file_line[self.col['iter']])
                self.relax.data.f_count[self.run] = eval(self.file_line[self.col['f_count']])
                self.relax.data.g_count[self.run] = eval(self.file_line[self.col['g_count']])
                self.relax.data.h_count[self.run] = eval(self.file_line[self.col['h_count']])
                if self.file_line[self.col['warn']] == 'None':
                    self.relax.data.warning[self.run] = None
                else:
                    self.relax.data.warning[self.run] = replace(self.file_line[self.col['warn']], '_', ' ')

            # Minimisation details (individual residue results).
            else:
                data.chi2 = eval(self.file_line[self.col['chi2']])
                data.iter = eval(self.file_line[self.col['iter']])
                data.f_count = eval(self.file_line[self.col['f_count']])
                data.g_count = eval(self.file_line[self.col['g_count']])
                data.h_count = eval(self.file_line[self.col['h_count']])
                if self.file_line[self.col['warn']] == 'None':
                    data.warning = None
                else:
                    data.warning = replace(self.file_line[self.col['warn']], '_', ' ')

        # Errors.
        if self.data_set == 'error':
            # S2.
            try:
                data.s2_err = float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2')
            except ValueError:
                data.s2_err = None

            # S2f.
            try:
                data.s2f_err = float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f')
            except ValueError:
                data.s2f_err = None

            # S2s.
            try:
                data.s2s_err = float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s')
            except ValueError:
                data.s2s_err = None

            # Local tm.
            try:
                data.local_tm_err = float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm')
            except ValueError:
                data.local_tm_err = None

            # te.
            try:
                data.te_err = float(self.file_line[self.col['te']]) * self.return_conversion_factor('te')
            except ValueError:
                data.te_err = None

            # tf.
            try:
                data.tf_err = float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf')
            except ValueError:
                data.tf_err = None

            # ts.
            try:
                data.ts_err = float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts')
            except ValueError:
                data.ts_err = None

            # Rex.
            try:
                data.rex_err = float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex')
            except ValueError:
                data.rex_err = None

            # Bond length.
            try:
                data.r_err = float(self.file_line[self.col['r']]) * self.return_conversion_factor('r')
            except ValueError:
                data.r_err = None

            # CSA.
            try:
                data.csa_err = float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa')
            except ValueError:
                data.csa_err = None


        # Construct the simulation data structures.
        if self.data_set == 'sim_0':
            # Get the parameter object names.
            param_names = self.data_names(set='params')

            # Get the minimisation statistic object names.
            min_names = self.data_names(set='min')

            # Loop over all the parameter names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(data, sim_object_name, [])

            # Loop over all the minimisation object names.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                if self.param_set == 'diff' or self.param_set == 'all':
                    setattr(self.relax.data, sim_object_name, {})
                    object = getattr(self.relax.data, sim_object_name)
                    object[self.run] = []
                else:
                    setattr(data, sim_object_name, [])

        # Simulations.
        if self.data_set != 'value' and self.data_set != 'error':
            # S2.
            try:
                data.s2_sim.append(float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2'))
            except ValueError:
                data.s2_sim.append(None)

            # S2f.
            try:
                data.s2f_sim.append(float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f'))
            except ValueError:
                data.s2f_sim.append(None)

            # S2s.
            try:
                data.s2s_sim.append(float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s'))
            except ValueError:
                data.s2s_sim.append(None)

            # Local tm.
            try:
                data.local_tm_sim.append(float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm'))
            except ValueError:
                data.local_tm_sim.append(None)

            # te.
            try:
                data.te_sim.append(float(self.file_line[self.col['te']]) * self.return_conversion_factor('te'))
            except ValueError:
                data.te_sim.append(None)

            # tf.
            try:
                data.tf_sim.append(float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf'))
            except ValueError:
                data.tf_sim.append(None)

            # ts.
            try:
                data.ts_sim.append(float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts'))
            except ValueError:
                data.ts_sim.append(None)

            # Rex.
            try:
                data.rex_sim.append(float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex'))
            except ValueError:
                data.rex_sim.append(None)

            # Bond length.
            try:
                data.r_sim.append(float(self.file_line[self.col['r']]) * self.return_conversion_factor('r'))
            except ValueError:
                data.r_sim.append(None)

            # CSA.
            try:
                data.csa_sim.append(float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa'))
            except ValueError:
                data.csa_sim.append(None)

            # Minimisation details (global minimisation results).
            if self.param_set == 'diff' or self.param_set == 'all':
                self.relax.data.chi2_sim[self.run].append(eval(self.file_line[self.col['chi2']]))
                self.relax.data.iter_sim[self.run].append(eval(self.file_line[self.col['iter']]))
                self.relax.data.f_count_sim[self.run].append(eval(self.file_line[self.col['f_count']]))
                self.relax.data.g_count_sim[self.run].append(eval(self.file_line[self.col['g_count']]))
                self.relax.data.h_count_sim[self.run].append(eval(self.file_line[self.col['h_count']]))
                if self.file_line[self.col['warn']] == 'None':
                    self.relax.data.warning_sim[self.run].append(None)
                else:
                    self.relax.data.warning_sim[self.run].append(replace(self.file_line[self.col['warn']], '_', ' '))

            # Minimisation details (individual residue results).
            else:
                data.chi2_sim.append(eval(self.file_line[self.col['chi2']]))
                data.iter_sim.append(eval(self.file_line[self.col['iter']]))
                data.f_count_sim.append(eval(self.file_line[self.col['f_count']]))
                data.g_count_sim.append(eval(self.file_line[self.col['g_count']]))
                data.h_count_sim.append(eval(self.file_line[self.col['h_count']]))
                if self.file_line[self.col['warn']] == 'None':
                    data.warning_sim.append(None)
                else:
                    data.warning_sim.append(replace(self.file_line[self.col['warn']], '_', ' '))


    def read_columnar_param_set(self):
        """Function for reading the parameter set."""

        # Extract the parameter set if it exists, otherwise return.
        if self.file_line[self.col['param_set']] != 'None':
            self.param_set = self.file_line[self.col['param_set']]
        else:
            return

        # Local tm and model-free only parameter sets.
        if self.param_set == 'local_tm' or self.param_set == 'mf':
            diff_fixed = 1
            res_fixed = 0

        # Diffusion tensor parameter set.
        elif self.param_set == 'diff':
            diff_fixed = 0
            res_fixed = 1

        # 'all' parameter set.
        elif self.param_set == 'all':
            diff_fixed = 0
            res_fixed = 0

        # No parameter set.
        elif self.param_set == 'None':
            self.param_set = None
            diff_fixed = None
            res_fixed = None

        # Set the diffusion tensor fixed flag.
        if self.param_set != 'local_tm' and diff_fixed != None:
            self.relax.data.diff[self.run].fixed = diff_fixed

        # Set the residue specific fixed flag.
        for i in xrange(len(self.relax.data.res[self.run])):
            if res_fixed != None:
                self.relax.data.res[self.run][i].fixed = res_fixed


    def read_columnar_pdb(self, print_flag=1):
        """Function for reading the PDB file."""

        # File name.
        pdb = self.file_line[self.col['pdb']]

        # PDB model.
        pdb_model = eval(self.file_line[self.col['pdb_model']])

        # Heteronucleus.
        if self.col.has_key('pdb_heteronuc'):
            pdb_heteronuc = self.file_line[self.col['pdb_heteronuc']]

        # Proton.
        if self.col.has_key('pdb_proton'):
            pdb_proton = self.file_line[self.col['pdb_proton']]

        # Load the PDB.
        if not pdb == 'None':
            self.relax.generic.pdb.load(run=self.run, file=pdb, model=pdb_model, heteronuc=pdb_heteronuc, proton=pdb_proton, calc_vectors=0, fail=0, print_flag=print_flag)
            return 1
        else:
            return 0


    def read_columnar_relax_data(self):
        """Function for reading the relaxation data."""

        # Skip the error 'data_set'.
        if self.data_set == 'error':
            return

        # Relaxation data structures.
        self.ri_labels = eval(self.file_line[self.col['ri_labels']])
        self.remap_table = eval(self.file_line[self.col['remap_table']])
        self.frq_labels = eval(self.file_line[self.col['frq_labels']])
        self.frq = eval(self.file_line[self.col['frq']])

        # No relaxation data.
        if not self.ri_labels:
            return

        # Initialise the value and error arrays.
        values = []
        errors = []

        # Loop over the relaxation data of the residue.
        for i in xrange(len(self.ri_labels)):
            # Determine the data and error columns for this relaxation data set.
            data_col = self.col['frq'] + i + 1
            error_col = self.col['frq'] + len(self.ri_labels) + i + 1

            # Append the value and error.
            values.append(eval(self.file_line[data_col]))
            errors.append(eval(self.file_line[error_col]))

        # Simulations.
        sim = 0
        if self.data_set != 'value' and self.data_set != 'error':
            sim = 1

        # Add the relaxation data.
        self.relax.specific.relax_data.add_residue(run=self.run, res_index=self.res_index, ri_labels=self.ri_labels, remap_table=self.remap_table, frq_labels=self.frq_labels, frq=self.frq, values=values, errors=errors, sim=sim)


    def read_columnar_results(self, run, file_data, print_flag=1):
        """Function for reading the results file."""

        # Arguments.
        self.run = run

        # Extract and remove the header.
        header = file_data[0]
        file_data = file_data[1:]

        # Sort the column numbers.
        self.read_columnar_col_numbers(header)

        # Test the file.
        if len(self.col) < 2:
            raise RelaxInvalidDataError

        # Initialise some data structures and flags.
        nucleus_set = 0
        sim_num = None
        sims = []
        all_select_sim = []
        diff_data_set = 0
        diff_error_set = 0
        diff_sim_set = None
        self.param_set = None
        pdb = 0
        pdb_model = None
        pdb_heteronuc = None
        pdb_proton = None
        self.ri_labels = None

        # Generate the sequence.
        for self.file_line in file_data:
            # The data set.
            self.data_set = self.file_line[self.col['data_set']]

            # Stop creating the sequence once the data_set is no longer 'value'.
            if self.data_set != 'value':
                break

            # Sequence.
            self.read_columnar_sequence()


        # Loop over the lines of the file data.
        for self.file_line in file_data:
            # The data set.
            self.data_set = self.file_line[self.col['data_set']]

            # Find the residue index.
            self.res_index = self.read_columnar_find_index()

            # Reassign data structure.
            data = self.relax.data.res[self.run][self.res_index]

            # Backwards compatibility for the reading of the results file from versions 1.2.0 to 1.2.9.
            if len(self.file_line) == 4:
                continue

            # Set the nucleus type.
            if not nucleus_set:
                if self.file_line[self.col['nucleus']] != 'None':
                    self.relax.generic.nuclei.set_values(self.file_line[self.col['nucleus']])
                    nucleus_set = 1

            # Simulation number.
            if self.data_set != 'value' and self.data_set != 'error':
                # Extract the number from the self.data_set string.
                sim_num = split(self.data_set, '_')
                try:
                    sim_num = int(sim_num[1])
                except:
                    raise RelaxError, "The simulation number '%s' is invalid." % sim_num

                # A new simulation number.
                if sim_num not in sims:
                    # Update the sims array and append an empty array to the selected sims array.
                    sims.append(sim_num)
                    all_select_sim.append([])

                # Selected simulations.
                all_select_sim[-1].append(int(self.file_line[self.col['select']]))

            # Diffusion tensor data.
            if self.data_set == 'value' and not diff_data_set:
                self.read_columnar_diff_tensor()
                diff_data_set = 1

            # Diffusion tensor errors.
            elif self.data_set == 'error' and not diff_error_set:
                self.read_columnar_diff_tensor()
                diff_error_set = 1

            # Diffusion tensor simulation data.
            elif self.data_set != 'value' and self.data_set != 'error' and sim_num != diff_sim_set:
                self.read_columnar_diff_tensor()
                diff_sim_set = sim_num

            # Parameter set.
            if self.param_set == None:
                self.read_columnar_param_set()

            # PDB.
            if not pdb:
                if self.read_columnar_pdb(print_flag):
                    pdb = 1

            # XH vector, heteronucleus, and proton.
            if self.data_set == 'value':
                self.read_columnar_xh_vect()

            # Relaxation data.
            self.read_columnar_relax_data()

            # Model-free data.
            self.read_columnar_model_free_data()

        # Set up the simulations.
        if len(sims):
            # Convert the selected simulation array of arrays into a Numeric matrix and transpose it.
            all_select_sim = transpose(array(all_select_sim))

            # Set up the Monte Carlo simulations.
            self.relax.generic.monte_carlo.setup(self.run, number=len(sims), all_select_sim=all_select_sim)

            # Turn the simulation state to off!
            self.relax.data.sim_state[self.run] = 0


    def read_columnar_sequence(self):
        """Function for generating the sequence."""

        # Residue number and name.
        try:
            res_num = int(self.file_line[self.col['num']])
        except ValueError:
            raise RelaxError, "The residue number " + self.file_line[self.col['num']] + " is not an integer."
        res_name = self.file_line[self.col['name']]

        # Generate the sequence.
        self.relax.generic.sequence.add(self.run, res_num, res_name, select=int(self.file_line[self.col['select']]))


    def read_columnar_xh_vect(self):
        """Function for reading the XH unit vectors."""

        # The vector.
        xh_vect = eval(self.file_line[self.col['xh_vect']])
        if xh_vect:
            # Numeric array format.
            try:
                xh_vect = array(xh_vect, Float64)
            except:
                raise RelaxError, "The XH unit vector " + self.file_line[self.col['xh_vect']] + " is invalid."

            # Set the vector.
            self.relax.generic.pdb.set_vector(run=self.run, res=self.res_index, xh_vect=xh_vect)

        # The heteronucleus and proton names.
        self.relax.data.res[self.run][self.res_index].heteronuc = self.file_line[self.col['pdb_heteronuc']]
        self.relax.data.res[self.run][self.res_index].proton = self.file_line[self.col['pdb_proton']]


    def remove_tm(self, run, res_num):
        """Function for removing the local tm parameter from the model-free parameters."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf_csa'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf_csa':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # If res_num is set, then skip all other residues.
            if res_num != None and res_num != data.num:
                continue

            # Test if a local tm parameter exists.
            if not hasattr(data, 'params') or not 'local_tm' in data.params:
                continue

            # Remove tm.
            data.params.remove('local_tm')

            # Model name.
            if match('^tm', data.model):
                data.model = data.model[1:]

            # Set the local tm value to None.
            data.local_tm = None

            # Set all the minimisation details to None.
            data.chi2 = None
            data.iter = None
            data.f_count = None
            data.g_count = None
            data.h_count = None
            data.warning = None

        # Set the global minimisation details to None.
        self.relax.data.chi2[self.run] = None
        self.relax.data.iter[self.run] = None
        self.relax.data.f_count[self.run] = None
        self.relax.data.g_count[self.run] = None
        self.relax.data.h_count[self.run] = None
        self.relax.data.warning[self.run] = None


    def return_conversion_factor(self, param):
        """Function for returning the factor of conversion between different parameter units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return 1e-12 for te.
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # tm (nanoseconds).
        if object_name == 'tm' or object_name == 'local_tm':
            return 1e-9

        # te, tf, and ts (picoseconds).
        elif object_name in ['te', 'tf', 'ts']:
            return 1e-12

        # Rex (value at 1st field strength).
        elif object_name == 'rex':
            return 1.0 / (2.0 * pi * self.relax.data.frq[self.run][0])**2

        # Bond length (Angstrom).
        elif object_name == 'r':
            return 1e-10

        # CSA (ppm).
        elif object_name == 'csa':
            return 1e-6

        # No conversion factor.
        else:
            return 1.0


    def return_data_name(self, name):
        """
        Model-free data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Local tm               | 'local_tm'   | '[Ll]ocal[ -_]tm'                                |
        |                        |              |                                                  |
        | Order parameter S2     | 's2'         | '^[Ss]2$'                                        |
        |                        |              |                                                  |
        | Order parameter S2f    | 's2f'        | '^[Ss]2f$'                                       |
        |                        |              |                                                  |
        | Order parameter S2s    | 's2s'        | '^[Ss]2s$'                                       |
        |                        |              |                                                  |
        | Correlation time te    | 'te'         | '^te$'                                           |
        |                        |              |                                                  |
        | Correlation time tf    | 'tf'         | '^tf$'                                           |
        |                        |              |                                                  |
        | Correlation time ts    | 'ts'         | '^ts$'                                           |
        |                        |              |                                                  |
        | Chemical exchange      | 'rex'        | '^[Rr]ex$' or '[Cc]emical[ -_][Ee]xchange'       |
        |                        |              |                                                  |
        | Bond length            | 'r'          | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |                        |              |                                                  |
        | CSA                    | 'csa'        | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|

        """

        # Local tm.
        if search('[Ll]ocal[ -_]tm', name):
            return 'local_tm'

        # Order parameter S2.
        if search('^[Ss]2$', name):
            return 's2'

        # Order parameter S2f.
        if search('^[Ss]2f$', name):
            return 's2f'

        # Order parameter S2s.
        if search('^[Ss]2s$', name):
            return 's2s'

        # Correlation time te.
        if search('^te$', name):
            return 'te'

        # Correlation time tf.
        if search('^tf$', name):
            return 'tf'

        # Correlation time ts.
        if search('^ts$', name):
            return 'ts'

        # Rex.
        if search('^[Rr]ex$', name) or search('[Cc]emical[ -_][Ee]xchange', name):
            return 'rex'

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'


    def return_grace_string(self, param):
        """Function for returning the Grace string representing the parameter for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(param)

        # Local tm.
        if object_name == 'tm' or object_name == 'local_tm':
            return '\\xt\\f{}\\sm'

        # Order parameter S2.
        elif object_name == 's2':
            return '\\qS\\v{0.4}\\z{0.71}2\\Q'

        # Order parameter S2f.
        elif object_name == 's2f':
            return '\\qS\\sf\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q'

        # Order parameter S2s.
        elif object_name == 's2s':
            return '\\qS\\ss\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q'

        # Correlation time te.
        elif object_name == 'te':
            return '\\xt\\f{}\\se'

        # Correlation time tf.
        elif object_name == 'tf':
            return '\\xt\\f{}\\sf'

        # Correlation time ts.
        elif object_name == 'ts':
            return '\\xt\\f{}\\ss'

        # Rex.
        elif object_name == 'rex':
            return '\\qR\\sex\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'


    def return_units(self, param):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # tm (nanoseconds).
        if object_name == 'tm' or object_name == 'local_tm':
            return 'ns'

        # te, tf, and ts (picoseconds).
        elif object_name in ['te', 'tf', 'ts']:
            return 'ps'

        # Rex (value at 1st field strength).
        elif object_name == 'rex':
            return self.relax.data.frq_labels[self.run][0] + ' MHz'

        # Bond length (Angstrom).
        elif object_name == 'r':
            return 'Angstrom'

        # CSA (ppm).
        elif object_name == 'csa':
            return 'ppm'


    def select_model(self, run=None, model=None, res_num=None):
        """Function for the selection of a preset model-free model."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf_csa'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf_csa':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Preset models.
        ################

        # Block 1.
        if model == 'm0':
            equation = 'mf_orig'
            params = []
        elif model == 'm1':
            equation = 'mf_orig'
            params = ['S2']
        elif model == 'm2':
            equation = 'mf_orig'
            params = ['S2', 'te']
        elif model == 'm3':
            equation = 'mf_orig'
            params = ['S2', 'Rex']
        elif model == 'm4':
            equation = 'mf_orig'
            params = ['S2', 'te', 'Rex']
        elif model == 'm5':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts']
        elif model == 'm6':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts']
        elif model == 'm7':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts', 'Rex']
        elif model == 'm8':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm9':
            equation = 'mf_orig'
            params = ['Rex']

        # Block 2.
        elif model == 'm10':
            equation = 'mf_orig'
            params = ['CSA']
        elif model == 'm11':
            equation = 'mf_orig'
            params = ['CSA', 'S2']
        elif model == 'm12':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te']
        elif model == 'm13':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'Rex']
        elif model == 'm14':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te', 'Rex']
        elif model == 'm15':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts']
        elif model == 'm16':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm17':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm18':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm19':
            equation = 'mf_orig'
            params = ['CSA', 'Rex']

        # Block 3.
        elif model == 'm20':
            equation = 'mf_orig'
            params = ['r']
        elif model == 'm21':
            equation = 'mf_orig'
            params = ['r', 'S2']
        elif model == 'm22':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te']
        elif model == 'm23':
            equation = 'mf_orig'
            params = ['r', 'S2', 'Rex']
        elif model == 'm24':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te', 'Rex']
        elif model == 'm25':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts']
        elif model == 'm26':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm27':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm28':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm29':
            equation = 'mf_orig'
            params = ['r', 'Rex']

        # Block 4.
        elif model == 'm30':
            equation = 'mf_orig'
            params = ['r', 'CSA']
        elif model == 'm31':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2']
        elif model == 'm32':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te']
        elif model == 'm33':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'Rex']
        elif model == 'm34':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'm35':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'm36':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm37':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm38':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm39':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'Rex']


        # Preset models with local correlation time.
        ############################################

        # Block 1.
        elif model == 'tm0':
            equation = 'mf_orig'
            params = ['local_tm']
        elif model == 'tm1':
            equation = 'mf_orig'
            params = ['local_tm', 'S2']
        elif model == 'tm2':
            equation = 'mf_orig'
            params = ['local_tm', 'S2', 'te']
        elif model == 'tm3':
            equation = 'mf_orig'
            params = ['local_tm', 'S2', 'Rex']
        elif model == 'tm4':
            equation = 'mf_orig'
            params = ['local_tm', 'S2', 'te', 'Rex']
        elif model == 'tm5':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'S2', 'ts']
        elif model == 'tm6':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm7':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm8':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm9':
            equation = 'mf_orig'
            params = ['local_tm', 'Rex']

        # Block 2.
        elif model == 'tm10':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA']
        elif model == 'tm11':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2']
        elif model == 'tm12':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2', 'te']
        elif model == 'tm13':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2', 'Rex']
        elif model == 'tm14':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm15':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm16':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm17':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm18':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm19':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'Rex']

        # Block 3.
        elif model == 'tm20':
            equation = 'mf_orig'
            params = ['local_tm', 'r']
        elif model == 'tm21':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2']
        elif model == 'tm22':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2', 'te']
        elif model == 'tm23':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2', 'Rex']
        elif model == 'tm24':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2', 'te', 'Rex']
        elif model == 'tm25':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'S2', 'ts']
        elif model == 'tm26':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm27':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm28':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm29':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'Rex']

        # Block 4.
        elif model == 'tm30':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA']
        elif model == 'tm31':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2']
        elif model == 'tm32':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2', 'te']
        elif model == 'tm33':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2', 'Rex']
        elif model == 'tm34':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm35':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm36':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm37':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm38':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm39':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'Rex']

        # Invalid model.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(self.run, model, equation, params, res_num)


    def set_doc(self):
        """
        Model-free set details
        ~~~~~~~~~~~~~~~~~~~~~~

        Setting a parameter value may have no effect depending on which model-free model is chosen,
        for example if S2f values and S2s values are set but the run corresponds to model-free model
        'm4' then, because these data values are not parameters of the model, they will have no
        effect.

        Note that the Rex values are scaled quadratically with field strength and should be supplied
        as a field strength independent value.  Use the following formula to get the correct value:

            value = Rex / (2.0 * pi * frequency) ** 2

        where:
            Rex is the chemical exchange value for the current frequency.
            pi is in the namespace of relax, ie just type 'pi'.
            frequency is the proton frequency corresponding to the data.
        """


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Parameter increment counter.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')


        # Diffusion tensor parameter errors.
        ####################################

        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    self.relax.data.diff[self.run].tm_err = error

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    self.relax.data.diff[self.run].tm_err = error
                elif index == 1:
                    self.relax.data.diff[self.run].Da_err = error
                elif index == 2:
                    self.relax.data.diff[self.run].theta_err = error
                elif index == 3:
                    self.relax.data.diff[self.run].phi_err = error

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    self.relax.data.diff[self.run].tm_err = error
                elif index == 1:
                    self.relax.data.diff[self.run].Da_err = error
                elif index == 2:
                    self.relax.data.diff[self.run].Dr_err = error
                elif index == 3:
                    self.relax.data.diff[self.run].alpha_err = error
                elif index == 4:
                    self.relax.data.diff[self.run].beta_err = error
                elif index == 5:
                    self.relax.data.diff[self.run].gamma_err = error

                # Increment.
                inc = inc + 6


        # Model-free parameter errors for the parameter set 'all'.
        ##########################################################

        if self.param_set == 'all':
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        setattr(self.relax.data.res[self.run][i], param + "_err", error)

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the parameter sets 'mf' and 'local_tm'.
        ###################################################################

        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Skip unselected residues.
            if not self.relax.data.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    setattr(self.relax.data.res[self.run][instance], param + "_err", error)

                # Increment.
                inc = inc + 1


    def set_selected_sim(self, run, instance, select_sim):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            if not hasattr(self.relax.data, 'select_sim'):
                self.relax.data.select_sim = {}
            self.relax.data.select_sim[self.run] = select_sim

        # Multiple instances.
        else:
            self.relax.data.res[self.run][instance].select_sim = select_sim


    def set_update(self, run, param, index):
        """Function to update the other model-free parameters."""

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][index]

        # S2f parameter.
        if param == 'S2f':
            # Update S2 if S2s exists.
            if hasattr(data, 's2s') and data.s2s != None:
                data.s2 = data.s2f * data.s2s


        # S2s parameter.
        if param == 'S2s':
            # Update S2 if S2f exists.
            if hasattr(data, 's2f') and data.s2f != None:
                data.s2 = data.s2f * data.s2s


    def sim_init_values(self, run):
        """Function for initialising Monte Carlo parameter values."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')

        # List of diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                diff_params = ['tm']

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                diff_params = ['tm', 'Da', 'theta', 'phi']

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(self.relax.data.diff[self.run], sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(self.relax.data, sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

        # Residue specific parameters.
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over all the parameter names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Test if the simulation object already exists.
                    if hasattr(self.relax.data.res[self.run][i], sim_object_name):
                        raise RelaxError, "Monte Carlo parameter values have already been set."


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the global minimisation stats objects.
        for object_name in min_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(self.relax.data, sim_object_name, {})

            # Get the simulation object.
            sim_object = getattr(self.relax.data, sim_object_name)

            # Add the run.
            sim_object[self.run] = []

            # Loop over the simulations.
            for j in xrange(self.relax.data.sim_number[self.run]):
                # Get the object.
                object = getattr(self.relax.data, object_name)

                # Test if the object has the key self.run.
                if not object.has_key(self.run):
                    continue

                # Copy and append the data.
                sim_object[self.run].append(deepcopy(object[self.run]))

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(self.relax.data.diff[self.run], sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(self.relax.data.diff[self.run], sim_object_name)

                # Loop over the simulations.
                for j in xrange(self.relax.data.sim_number[self.run]):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(self.relax.data.diff[self.run], object_name)))

        # Residue specific parameters.
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over all the data names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(self.relax.data.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(self.relax.data.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(self.relax.data.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(self.relax.data.res[self.run][i], object_name)))

                # Loop over all the minimisation object names.
                for object_name in min_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(self.relax.data.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(self.relax.data.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(self.relax.data.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(self.relax.data.res[self.run][i], object_name)))


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(self.relax.data.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        self.relax.data.res[run][i].relax_sim_data = sim_data


    def sim_return_chi2(self, run, instance):
        """Function for returning the array of simulation chi-squared values."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            return self.relax.data.chi2_sim[self.run]

        # Multiple instances.
        else:
            return self.relax.data.res[self.run][instance].chi2_sim


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Parameter increment counter.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')


        # Diffusion tensor parameters.
        ##############################

        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if self.relax.data.diff[self.run].type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    return self.relax.data.diff[self.run].tm_sim

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    return self.relax.data.diff[self.run].tm_sim
                elif index == 1:
                    return self.relax.data.diff[self.run].Da_sim
                elif index == 2:
                    return self.relax.data.diff[self.run].theta_sim
                elif index == 3:
                    return self.relax.data.diff[self.run].phi_sim

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    return self.relax.data.diff[self.run].tm_sim
                elif index == 1:
                    return self.relax.data.diff[self.run].Da_sim
                elif index == 2:
                    return self.relax.data.diff[self.run].Dr_sim
                elif index == 3:
                    return self.relax.data.diff[self.run].alpha_sim
                elif index == 4:
                    return self.relax.data.diff[self.run].beta_sim
                elif index == 5:
                    return self.relax.data.diff[self.run].gamma_sim

                # Increment.
                inc = inc + 6


        # Model-free parameters for the parameter set 'all'.
        ####################################################

        if self.param_set == 'all':
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        return getattr(self.relax.data.res[self.run][i], param + "_sim")

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the parameter sets 'mf' and 'local_tm'.
        ###################################################################

        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Skip unselected residues.
            if not self.relax.data.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    return getattr(self.relax.data.res[self.run][instance], param + "_sim")

                # Increment.
                inc = inc + 1


    def sim_return_selected(self, run, instance):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            return self.relax.data.select_sim[self.run]

        # Multiple instances.
        else:
            return self.relax.data.res[self.run][instance].select_sim


    def skip_function(self, run=None, instance=None, min_instances=None, num_instances=None):
        """Function for skiping certain data."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # All residues.
        combine = 0
        if min_instances == 1 and min_instances != num_instances:
            combine = 1

        # Sequence specific data.
        if (self.param_set == 'mf' or self.param_set == 'local_tm') and not combine and not self.relax.data.res[self.run][instance].select:
            return 1

        # Don't skip.
        return 0


    def unselect(self, run, i, sim_index=None):
        """Function for unselecting models or simulations."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Simulation unselect.
        if sim_index != None:
            # Single instance.
            if self.param_set == 'mf' or self.param_set == 'local_tm':
                self.relax.data.res[self.run][i].select_sim[sim_index] = 0

            # Multiple instances.
            else:
                self.relax.data.select_sim[self.run][sim_index] = 0

        # Residue unselect.
        else:
            # Single residue.
            if self.param_set == 'mf' or self.param_set == 'local_tm':
                self.relax.data.res[self.run][i].select = 0


    def write_columnar_line(self, file=None, num=None, name=None, select=None, select_sim=None, data_set=None, nucleus=None, model=None, equation=None, params=None, param_set=None, s2=None, s2f=None, s2s=None, local_tm=None, te=None, tf=None, ts=None, rex=None, r=None, csa=None, chi2=None, i=None, f=None, g=None, h=None, warn=None, diff_type=None, diff_params=None, pdb=None, pdb_model=None, pdb_heteronuc=None, pdb_proton=None, xh_vect=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag.
        if select_sim != None:
            file.write("%-9s " % select_sim)
        else:
            file.write("%-9s " % select)

        # Data set.
        file.write("%-9s " % data_set)

        # Nucleus.
        file.write("%-7s " % nucleus)

        # Model details.
        file.write("%-5s %-9s %-35s " % (model, equation, params))

        # Parameter set.
        file.write("%-10s " % param_set)

        # Parameters.
        file.write("%-25s " % s2)
        file.write("%-25s " % s2f)
        file.write("%-25s " % s2s)
        file.write("%-25s " % local_tm)
        file.write("%-25s " % te)
        file.write("%-25s " % tf)
        file.write("%-25s " % ts)
        file.write("%-25s " % rex)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)

        # Minimisation results.
        file.write("%-25s %-8s %-8s %-8s %-8s %-45s " % (chi2, i, f, g, h, warn))

        # Diffusion parameters.
        file.write("%-10s " % diff_type)
        if diff_params:
            for i in xrange(len(diff_params)):
                file.write("%-25s " % diff_params[i])

        # PDB.
        file.write("%-40s " % pdb)
        file.write("%-10s " % pdb_model)
        file.write("%-15s " % pdb_heteronuc)
        file.write("%-15s " % pdb_proton)

        # XH unit vector.
        file.write("%-70s " % xh_vect)

        # Relaxation data setup.
        if ri_labels:
            file.write("%-40s " % ri_labels)
            file.write("%-25s " % remap_table)
            file.write("%-25s " % frq_labels)
            file.write("%-30s " % frq)

        # Relaxation data.
        if ri:
            for i in xrange(len(ri)):
                if ri[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri[i])

        # Relaxation errors.
        if ri_error:
            for i in xrange(len(ri_error)):
                if ri_error[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri_error[i])

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file, run):
        """Function for printing the results into a file."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()


        # Header.
        #########

        # Diffusion parameters.
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
            # Sphere.
            if self.relax.data.diff[self.run].type == 'sphere':
                diff_params = ['tm_(s)']

            # Spheroid.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'theta_(deg)', 'phi_(deg)']

            # Ellipsoid.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'Dr_(1/s)', 'alpha_(deg)', 'beta_(deg)', 'gamma_(deg)']

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(self.relax.data, 'num_ri'):
            for i in xrange(self.relax.data.num_ri[self.run]):
                ri.append('Ri_(' + self.relax.data.ri_labels[self.run][i] + "_" + self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]] + ")")
                ri_error.append('Ri_error_(' + self.relax.data.ri_labels[self.run][i] + "_" + self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', nucleus='Nucleus', model='Model', equation='Equation', params='Params', param_set='Param_set', s2='S2', s2f='S2f', s2s='S2s', local_tm='Local_tm_(' + self.return_units('local_tm') + ')', te='te_(' + self.return_units('te') + ')', tf='tf_(' + self.return_units('tf') + ')', ts='ts_(' + self.return_units('ts') + ')', rex='Rex_(' + replace(self.return_units('rex'), ' ', '_') + ')', r='Bond_length_(' + self.return_units('r') + ')', csa='CSA_(' + self.return_units('csa') + ')', chi2='Chi-squared', i='Iter', f='f_count', g='g_count', h='h_count', warn='Warning', diff_type='Diff_type', diff_params=diff_params, pdb='PDB', pdb_model='PDB_model', pdb_heteronuc='PDB_heteronuc', pdb_proton='PDB_proton', xh_vect='XH_vector', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        nucleus = self.relax.generic.nuclei.find_nucleus()

        # Diffusion parameters.
        diff_type = None
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
            # Sphere.
            if self.relax.data.diff[self.run].type == 'sphere':
                diff_type = 'sphere'
                diff_params = [`self.relax.data.diff[self.run].tm`]

            # Spheroid.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                diff_type = self.relax.data.diff[self.run].spheroid_type
                if diff_type == None:
                    diff_type = 'spheroid'
                diff_params = [`self.relax.data.diff[self.run].tm`, `self.relax.data.diff[self.run].Da`, `self.relax.data.diff[self.run].theta * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].phi * 360 / (2.0 * pi)`]

            # Ellipsoid.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                diff_type = 'ellipsoid'
                diff_params = [`self.relax.data.diff[self.run].tm`, `self.relax.data.diff[self.run].Da`, `self.relax.data.diff[self.run].Dr`, `self.relax.data.diff[self.run].alpha * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].beta * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].gamma * 360 / (2.0 * pi)`]

        # PDB.
        pdb = None
        pdb_model = None
        pdb_heteronuc = None
        pdb_proton = None
        if self.relax.data.pdb.has_key(self.run):
            pdb = self.relax.data.pdb[self.run].file_name
            pdb_model = self.relax.data.pdb[self.run].model
            pdb_heteronuc = self.relax.data.pdb[self.run].heteronuc
            pdb_proton = self.relax.data.pdb[self.run].proton

        # Relaxation data setup.
        try:
            ri_labels = replace(`self.relax.data.ri_labels[self.run]`, ' ', '')
            remap_table = replace(`self.relax.data.remap_table[self.run]`, ' ', '')
            frq_labels = replace(`self.relax.data.frq_labels[self.run]`, ' ', '')
            frq = replace(`self.relax.data.frq[self.run]`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # Model details.
            model = None
            if hasattr(data, 'model'):
                model = data.model

            equation = None
            if hasattr(data, 'equation'):
                equation = data.equation

            params = None
            if hasattr(data, 'params'):
                params = replace(`data.params`, ' ', '')

            # S2.
            s2 = None
            if hasattr(data, 's2') and data.s2 != None:
                s2 = data.s2 / self.return_conversion_factor('s2')
            s2 = `s2`

            # S2f.
            s2f = None
            if hasattr(data, 's2f') and data.s2f != None:
                s2f = data.s2f / self.return_conversion_factor('s2f')
            s2f = `s2f`

            # S2s.
            s2s = None
            if hasattr(data, 's2s') and data.s2s != None:
                s2s = data.s2s / self.return_conversion_factor('s2s')
            s2s = `s2s`

            # Local tm.
            local_tm = None
            if hasattr(data, 'local_tm') and data.local_tm != None:
                local_tm = data.local_tm / self.return_conversion_factor('local_tm')
            local_tm = `local_tm`

            # te.
            te = None
            if hasattr(data, 'te') and data.te != None:
                te = data.te / self.return_conversion_factor('te')
            te = `te`

            # tf.
            tf = None
            if hasattr(data, 'tf') and data.tf != None:
                tf = data.tf / self.return_conversion_factor('tf')
            tf = `tf`

            # ts.
            ts = None
            if hasattr(data, 'ts') and data.ts != None:
                ts = data.ts / self.return_conversion_factor('ts')
            ts = `ts`

            # Rex.
            rex = None
            if hasattr(data, 'rex') and data.rex != None:
                rex = data.rex / self.return_conversion_factor('rex')
            rex = `rex`

            # Bond length.
            r = None
            if hasattr(data, 'r') and data.r != None:
                r = data.r / self.return_conversion_factor('r')
            r = `r`

            # CSA.
            csa = None
            if hasattr(data, 'csa') and data.csa != None:
                csa = data.csa / self.return_conversion_factor('csa')
            csa = `csa`

            # Minimisation details.
            try:
                # Global minimisation results.
                if self.param_set == 'diff' or self.param_set == 'all':
                    chi2 = `self.relax.data.chi2[self.run]`
                    iter = self.relax.data.iter[self.run]
                    f = self.relax.data.f_count[self.run]
                    g = self.relax.data.g_count[self.run]
                    h = self.relax.data.h_count[self.run]
                    if type(self.relax.data.warning[self.run]) == str:
                        warn = replace(self.relax.data.warning[self.run], ' ', '_')
                    else:
                        warn = self.relax.data.warning[self.run]

                # Individual residue results.
                else:
                    chi2 = `data.chi2`
                    iter = data.iter
                    f = data.f_count
                    g = data.g_count
                    h = data.h_count
                    if type(data.warning) == str:
                        warn = replace(data.warning, ' ', '_')
                    else:
                        warn = data.warning

            # No minimisation details.
            except:
                chi2 = None
                iter = None
                f = None
                g = None
                h = None
                warn = None

            # XH vector.
            xh_vect = None
            if hasattr(data, 'xh_vect'):
                xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(self.relax.data, 'num_ri'):
                for i in xrange(self.relax.data.num_ri[self.run]):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(data.num_ri):
                            if data.ri_labels[j] == self.relax.data.ri_labels[self.run][i] and data.frq_labels[data.remap_table[j]] == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(`data.relax_data[index]`)
                        ri_error.append(`data.relax_error[index]`)

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='value', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=pdb_heteronuc, pdb_proton=pdb_proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Only invoke this section if errors exist.
        if self.has_errors():
            # Diffusion parameters.
            diff_params = None
            if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
                # Sphere.
                if self.relax.data.diff[self.run].type == 'sphere':
                    diff_params = [None]

                # Spheroid.
                elif self.relax.data.diff[self.run].type == 'spheroid':
                    diff_params = [None, None, None, None]

                # Ellipsoid.
                elif self.relax.data.diff[self.run].type == 'ellipsoid':
                    diff_params = [None, None, None, None, None, None]

                # Diffusion parameter errors.
                if self.param_set == 'diff' or self.param_set == 'all':
                    # Sphere.
                    if self.relax.data.diff[self.run].type == 'sphere' and hasattr(self.relax.data.diff[self.run], 'tm_err'):
                        diff_params = [`self.relax.data.diff[self.run].tm_err`]

                    # Spheroid.
                    elif self.relax.data.diff[self.run].type == 'spheroid' and hasattr(self.relax.data.diff[self.run], 'tm_err'):
                        diff_params = [`self.relax.data.diff[self.run].tm_err`, `self.relax.data.diff[self.run].Da_err`, `self.relax.data.diff[self.run].theta_err * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].phi_err * 360 / (2.0 * pi)`]

                    # Ellipsoid.
                    elif self.relax.data.diff[self.run].type == 'ellipsoid' and hasattr(self.relax.data.diff[self.run], 'tm_err'):
                        diff_params = [`self.relax.data.diff[self.run].tm_err`, `self.relax.data.diff[self.run].Da_err`, `self.relax.data.diff[self.run].Dr_err`, `self.relax.data.diff[self.run].alpha_err * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].beta_err * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].gamma_err * 360 / (2.0 * pi)`]

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Reassign data structure.
                data = self.relax.data.res[self.run][i]

                # Model details.
                model = None
                if hasattr(data, 'model'):
                    model = data.model

                equation = None
                if hasattr(data, 'equation'):
                    equation = data.equation

                params = None
                if hasattr(data, 'params'):
                    params = replace(`data.params`, ' ', '')

                # S2.
                s2 = None
                if hasattr(data, 's2_err') and data.s2_err != None:
                    s2 = data.s2_err / self.return_conversion_factor('s2')
                s2 = `s2`

                # S2f.
                s2f = None
                if hasattr(data, 's2f_err') and data.s2f_err != None:
                    s2f = data.s2f_err / self.return_conversion_factor('s2f')
                s2f = `s2f`

                # S2s.
                s2s = None
                if hasattr(data, 's2s_err') and data.s2s_err != None:
                    s2s = data.s2s_err / self.return_conversion_factor('s2s')
                s2s = `s2s`

                # Local tm.
                local_tm = None
                if hasattr(data, 'local_tm_err') and data.local_tm_err != None:
                    local_tm = data.local_tm_err / self.return_conversion_factor('local_tm')
                local_tm = `local_tm`

                # te.
                te = None
                if hasattr(data, 'te_err') and data.te_err != None:
                    te = data.te_err / self.return_conversion_factor('te')
                te = `te`

                # tf.
                tf = None
                if hasattr(data, 'tf_err') and data.tf_err != None:
                    tf = data.tf_err / self.return_conversion_factor('tf')
                tf = `tf`

                # ts.
                ts = None
                if hasattr(data, 'ts_err') and data.ts_err != None:
                    ts = data.ts_err / self.return_conversion_factor('ts')
                ts = `ts`

                # Rex.
                rex = None
                if hasattr(data, 'rex_err') and data.rex_err != None:
                    rex = data.rex_err / self.return_conversion_factor('rex')
                rex = `rex`

                # Bond length.
                r = None
                if hasattr(data, 'r_err') and data.r_err != None:
                    r = data.r_err / self.return_conversion_factor('r')
                r = `r`

                # CSA.
                csa = None
                if hasattr(data, 'csa_err') and data.csa_err != None:
                    csa = data.csa_err / self.return_conversion_factor('csa')
                csa = `csa`

                # Relaxation data and errors.
                ri = []
                ri_error = []
                for i in xrange(self.relax.data.num_ri[self.run]):
                    ri.append(None)
                    ri_error.append(None)

                # XH vector.
                xh_vect = None
                if hasattr(data, 'xh_vect'):
                    xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

                # Write the line.
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='error', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=pdb_heteronuc, pdb_proton=pdb_proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Only invoke this section if simulations have been setup.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[self.run]:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[self.run]):
                # Diffusion parameters.
                diff_params = None
                if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
                    # Diffusion parameter simulation values.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        # Sphere.
                        if self.relax.data.diff[self.run].type == 'sphere':
                            diff_params = [`self.relax.data.diff[self.run].tm_sim[i]`]

                        # Spheroid.
                        elif self.relax.data.diff[self.run].type == 'spheroid':
                            diff_params = [`self.relax.data.diff[self.run].tm_sim[i]`, `self.relax.data.diff[self.run].Da_sim[i]`, `self.relax.data.diff[self.run].theta_sim[i] * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].phi_sim[i] * 360 / (2.0 * pi)`]

                        # Ellipsoid.
                        elif self.relax.data.diff[self.run].type == 'ellipsoid':
                            diff_params = [`self.relax.data.diff[self.run].tm_sim[i]`, `self.relax.data.diff[self.run].Da_sim[i]`, `self.relax.data.diff[self.run].Dr_sim[i]`, `self.relax.data.diff[self.run].alpha_sim[i] * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].beta_sim[i] * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].gamma_sim[i] * 360 / (2.0 * pi)`]

                    # No simulation values.
                    else:
                        # Sphere.
                        if self.relax.data.diff[self.run].type == 'sphere':
                            diff_params = [None]

                        # Spheroid.
                        elif self.relax.data.diff[self.run].type == 'spheroid':
                            diff_params = [None, None, None, None]

                        # Ellipsoid.
                        elif self.relax.data.diff[self.run].type == 'ellipsoid':
                            diff_params = [None, None, None, None, None, None]

                # Loop over the sequence.
                for j in xrange(len(self.relax.data.res[self.run])):
                    # Reassign data structure.
                    data = self.relax.data.res[self.run][j]

                    # Model details.
                    model = None
                    if hasattr(data, 'model'):
                        model = data.model

                    equation = None
                    if hasattr(data, 'equation'):
                        equation = data.equation

                    params = None
                    if hasattr(data, 'params'):
                        params = replace(`data.params`, ' ', '')

                    # Selected simulation.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        select_sim = self.relax.data.select_sim[self.run][i]
                    else:
                        select_sim = data.select_sim[i]

                    # S2.
                    s2 = None
                    if hasattr(data, 's2_sim') and data.s2_sim[i] != None:
                        s2 = data.s2_sim[i] / self.return_conversion_factor('s2')
                    s2 = `s2`

                    # S2f.
                    s2f = None
                    if hasattr(data, 's2f_sim') and data.s2f_sim[i] != None:
                        s2f = data.s2f_sim[i] / self.return_conversion_factor('s2f')
                    s2f = `s2f`

                    # S2s.
                    s2s = None
                    if hasattr(data, 's2s_sim') and data.s2s_sim[i] != None:
                        s2s = data.s2s_sim[i] / self.return_conversion_factor('s2s')
                    s2s = `s2s`

                    # Local tm.
                    local_tm = None
                    if hasattr(data, 'local_tm_sim') and data.local_tm_sim[i] != None:
                        local_tm = data.local_tm_sim[i] / self.return_conversion_factor('local_tm')
                    local_tm = `local_tm`

                    # te.
                    te = None
                    if hasattr(data, 'te_sim') and data.te_sim[i] != None:
                        te = data.te_sim[i] / self.return_conversion_factor('te')
                    te = `te`

                    # tf.
                    tf = None
                    if hasattr(data, 'tf_sim') and data.tf_sim[i] != None:
                        tf = data.tf_sim[i] / self.return_conversion_factor('tf')
                    tf = `tf`

                    # ts.
                    ts = None
                    if hasattr(data, 'ts_sim') and data.ts_sim[i] != None:
                        ts = data.ts_sim[i] / self.return_conversion_factor('ts')
                    ts = `ts`

                    # Rex.
                    rex = None
                    if hasattr(data, 'rex_sim') and data.rex_sim[i] != None:
                        rex = data.rex_sim[i] / self.return_conversion_factor('rex')
                    rex = `rex`

                    # Bond length.
                    r = None
                    if hasattr(data, 'r_sim') and data.r_sim[i] != None:
                        r = data.r_sim[i] / self.return_conversion_factor('r')
                    r = `r`

                    # CSA.
                    csa = None
                    if hasattr(data, 'csa_sim') and data.csa_sim[i] != None:
                        csa = data.csa_sim[i] / self.return_conversion_factor('csa')
                    csa = `csa`

                    # Minimisation details.
                    try:
                        # Global minimisation results.
                        if self.param_set == 'diff' or self.param_set == 'all':
                            chi2 = `self.relax.data.chi2_sim[self.run][i]`
                            iter = self.relax.data.iter_sim[self.run][i]
                            f = self.relax.data.f_count_sim[self.run][i]
                            g = self.relax.data.g_count_sim[self.run][i]
                            h = self.relax.data.h_count_sim[self.run][i]
                            if type(self.relax.data.warning_sim[self.run][i]) == str:
                                warn = replace(self.relax.data.warning_sim[self.run][i], ' ', '_')
                            else:
                                warn = self.relax.data.warning_sim[self.run][i]

                        # Individual residue results.
                        else:
                            chi2 = `data.chi2_sim[i]`
                            iter = data.iter_sim[i]
                            f = data.f_count_sim[i]
                            g = data.g_count_sim[i]
                            h = data.h_count_sim[i]
                            if type(data.warning_sim[i]) == str:
                                warn = replace(data.warning_sim[i], ' ', '_')
                            else:
                                warn = data.warning_sim[i]

                    # No minimisation details.
                    except AttributeError:
                        chi2 = None
                        iter = None
                        f = None
                        g = None
                        h = None
                        warn = None

                    # Relaxation data and errors.
                    ri = []
                    ri_error = []
                    for k in xrange(self.relax.data.num_ri[self.run]):
                        # Find the residue specific data corresponding to k.
                        index = None
                        for l in xrange(data.num_ri):
                            if data.ri_labels[l] == self.relax.data.ri_labels[self.run][k] and data.frq_labels[data.remap_table[l]] == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][k]]:
                                index = l

                        # Data exists for this data type.
                        try:
                            ri.append(`data.relax_sim_data[i][index]`)
                            ri_error.append(`data.relax_error[index]`)
                        except:
                            ri.append(None)
                            ri_error.append(None)

                    # XH vector.
                    xh_vect = None
                    if hasattr(data, 'xh_vect'):
                        xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

                    # Write the line.
                    self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, select_sim=select_sim, data_set='sim_'+`i`, nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=pdb_heteronuc, pdb_proton=pdb_proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)






##############################
# Molmol specific functions. #
##############################

class Molmol:
    def __init__(self, relax):
        """Class containing the Molmol specific functions."""

        self.relax = relax


    def classic(self, data_type, colour_start, colour_end, colour_list):
        """
        Classic style
        ~~~~~~~~~~~~~

        Creator:  Edward d'Auvergne

        Argument string:  "classic"

        Description:  The classic style draws the backbone of the protein in the Molmol 'neon'
        style.  Rather than colouring the amino acids to which the NH bond belongs, the three
        covalent bonds of the peptide bond from Ca to Ca in which the NH bond is located are
        coloured.  Deselected residues are shown as black lines.

        Supported data types:
        ____________________________________________________________________________________________
        |                |             |                                                           |
        | Data type      | String      | Description                                               |
        |________________|_____________|___________________________________________________________|
        |                |             |                                                           |
        | S2.            | 'S2'        | The standard model-free order parameter, equal to S2f.S2s |
        |                |             | for the two timescale models.  The default colour         |
        |                |             | gradient starts at 'yellow' and ends at 'red'.            |
        |                |             |                                                           |
        | S2f.           | 'S2f'       | The order parameter of the faster of two internal         |
        |                |             | motions.  Residues which are described by model-free      |
        |                |             | models m1 to m4, the single timescale models, are         |
        |                |             | illustrated as white neon bonds.  The default colour      |
        |                |             | gradient is the same as that for the S2 data type.        |
        |                |             |                                                           |
        | S2s.           | 'S2s'       | The order parameter of the slower of two internal         |
        |                |             | motions.  This functions exactly as S2f except that S2s   |
        |                |             | is plotted instead.                                       |
        |                |             |                                                           |
        | Amplitude of   | 'amp_fast'  | Model independent display of the amplite of fast motions. |
        | fast motions.  |             | For residues described by model-free models m5 to m8, the |
        |                |             | value plotted is that of S2f.  However, for residues      |
        |                |             | described by models m1 to m4, what is shown is dependent  |
        |                |             | on the timescale of the motions.  This is because these   |
        |                |             | single timescale models can, at times, be perfect         |
        |                |             | approximations to the more complex two timescale models.  |
        |                |             | Hence if te is less than 200 ps, S2 is plotted. Otherwise |
        |                |             | the peptide bond is coloured white.  The default colour   |
        |                |             | gradient  is the same as that for S2.                     |
        |                |             |                                                           |
        | Amplitude of   | 'amp_slow'  | Model independent display of the amplite of slow motions, |
        | slow motions.  |             | arbitrarily defined as motions slower than 200 ps.  For   |
        |                |             | residues described by model-free models m5 to m8, the     |
        |                |             | order parameter S2 is plotted if ts > 200 ps.  For models |
        |                |             | m1 to m4, S2 is plotted if te > 200 ps.  The default      |
        |                |             | colour gradient is the same as that for S2.               |
        |                |             |                                                           |
        | te.            | 'te'        | The correlation time, te.  The default colour gradient    |
        |                |             | starts at 'turquoise' and ends at 'blue'.                 |
        |                |             |                                                           |
        | tf.            | 'tf'        | The correlation time, tf.  The default colour gradient is |
        |                |             | the same as that of te.                                   |
        |                |             |                                                           |
        | ts.            | 'ts'        | The correlation time, ts.  The default colour gradient    |
        |                |             | starts at 'blue' and ends at 'black'.                     |
        |                |             |                                                           |
        | Timescale of   | 'time_fast' | Model independent display of the timescale of fast        |
        | fast motions   |             | motions.  For models m5 to m8, only the parameter tf is   |
        |                |             | plotted.  For models m2 and m4, the parameter te is       |
        |                |             | plotted only if it is less than 200 ps.  All other        |
        |                |             | residues are assumed to have a correlation time of zero.  |
        |                |             | The default colour gradient is the same as that of te.    |
        |                |             |                                                           |
        | Timescale of   | 'time_slow' | Model independent display of the timescale of slow        |
        | slow motions   |             | motions.  For models m5 to m8, only the parameter ts is   |
        |                |             | plotted.  For models m2 and m4, the parameter te is       |
        |                |             | plotted only if it is greater than 200 ps.  All other     |
        |                |             | residues are coloured white.  The default colour gradient |
        |                |             | is the same as that of ts.                                |
        |                |             |                                                           |
        | Chemical       | 'Rex'       | The chemical exchange, Rex.  Residues which experience no |
        | exchange       |             | chemical exchange are coloured white.  The default colour |
        |                |             | gradient starts at 'yellow' and finishes at 'red'.        |
        |________________|_____________|___________________________________________________________|
        """

        # Generate the macro header.
        ############################

        self.classic_header()


        # S2.
        #####

        if data_type == 'S2':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have an S2 value.
                if not hasattr(residue, 's2') or residue.s2 == None:
                    continue

                # S2 width and colour.
                self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)


        # S2f.
        ######

        elif data_type == 'S2f':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Colour residues which don't have an S2f value white.
                if not hasattr(residue, 's2f') or residue.s2f == None:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

                # S2f width and colour.
                else:
                    self.classic_order_param(residue, residue.s2f, colour_start, colour_end, colour_list)


        # S2s.
        ######

        elif data_type == 'S2s':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Colour residues which don't have an S2s value white.
                if not hasattr(residue, 's2s') or residue.s2s == None:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

                # S2s width and colour.
                else:
                    self.classic_order_param(residue, residue.s2s, colour_start, colour_end, colour_list)


        # Amplitude of fast motions.
        ############################

        elif data_type == 'amp_fast':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # S2f width and colour (for models m5 to m8).
                if hasattr(residue, 's2f') and residue.s2f != None:
                    self.classic_order_param(residue, residue.s2f, colour_start, colour_end, colour_list)

                # S2 width and colour (for models m1 and m3).
                elif model == 'm1' or model == 'm3':
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # S2 width and colour (for models m2 and m4 when te <= 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te <= 200e-12:
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # White bonds (for models m2 and m4 when te > 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te > 200e-12:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

                # Catch errors.
                else:
                    raise RelaxFault


        # Amplitude of slow motions.
        ############################

        elif data_type == 'amp_slow':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # S2 width and colour (for models m5 to m8).
                if hasattr(residue, 'ts') and residue.ts != None:
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # S2 width and colour (for models m2 and m4 when te > 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te > 200 * 1e-12:
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # White bonds for fast motions.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

        # te.
        #####

        elif data_type == 'te':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have a te value.
                if not hasattr(residue, 'te') or residue.te == None:
                    continue

                # te width and colour.
                self.classic_correlation_time(residue, residue.te, colour_start, colour_end, colour_list)


        # tf.
        #####

        elif data_type == 'tf':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have a tf value.
                if not hasattr(residue, 'tf') or residue.tf == None:
                    continue

                # tf width and colour.
                self.classic_correlation_time(residue, residue.tf, colour_start, colour_end, colour_list)


        # ts.
        #####

        elif data_type == 'ts':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have a ts value.
                if not hasattr(residue, 'ts') or residue.ts == None:
                    continue

                # The default start and end colours.
                if colour_start == None:
                    colour_start = 'blue'
                if colour_end == None:
                    colour_end = 'black'

                # ts width and colour.
                self.classic_correlation_time(residue, residue.ts / 10.0, colour_start, colour_end, colour_list)


        # Timescale of fast motions.
        ############################

        elif data_type == 'time_fast':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # tf width and colour (for models m5 to m8).
                if hasattr(residue, 'tf') and residue.tf != None:
                    self.classic_correlation_time(residue, residue.tf, colour_start, colour_end, colour_list)

                # te width and colour (for models m2 and m4 when te <= 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te <= 200e-12:
                    self.classic_correlation_time(residue, residue.te, colour_start, colour_end, colour_list)

                # All other residues are assumed to have a fast correlation time of zero (statistically zero, not real zero!).
                # Colour these bonds white.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])


        # Timescale of slow motions.
        ############################

        elif data_type == 'time_slow':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # The default start and end colours.
                if colour_start == None:
                    colour_start = 'blue'
                if colour_end == None:
                    colour_end = 'black'

                # ts width and colour (for models m5 to m8).
                if hasattr(residue, 'ts') and residue.ts != None:
                    self.classic_correlation_time(residue, residue.ts / 10.0, colour_start, colour_end, colour_list)

                # te width and colour (for models m2 and m4 when te > 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te > 200e-12:
                    self.classic_correlation_time(residue, residue.te / 10.0, colour_start, colour_end, colour_list)

                # White bonds for the rest.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])


        # Rex.
        ######

        elif data_type == 'Rex':
            # Loop over the sequence.
            for residue in self.relax.data.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Residues which chemical exchange.
                if hasattr(residue, 'rex') and residue.rex != None:
                    self.classic_rex(residue, residue.rex, colour_start, colour_end, colour_list)

                # White bonds for the rest.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])


        # Unknown data type.
        ####################

        else:
            raise RelaxUnknownDataTypeError, data_type


    def classic_colour(self, res_num=None, width=None, rgb_array=None):
        """Colour the given peptide bond."""

        # Ca to C bond.
        self.commands.append("SelectBond 'atom1.name = \"CA\"  & atom2.name = \"C\" & res.num = " + `res_num-1` + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + `width`)
        self.commands.append("ColorBond " + `rgb_array[0]` + " " + `rgb_array[1]` + " " + `rgb_array[2]`)

        # C to N bond.
        self.commands.append("SelectBond 'atom1.name = \"C\"  & atom2.name = \"N\" & res.num = " + `res_num-1` + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + `width`)
        self.commands.append("ColorBond " + `rgb_array[0]` + " " + `rgb_array[1]` + " " + `rgb_array[2]`)

        # N to Ca bond.
        self.commands.append("SelectBond 'atom1.name = \"N\"  & atom2.name = \"CA\" & res.num = " + `res_num` + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + `width`)
        self.commands.append("ColorBond " + `rgb_array[0]` + " " + `rgb_array[1]` + " " + `rgb_array[2]`)

        # Blank line.
        self.commands.append("")


    def classic_correlation_time(self, residue, te, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for correlation times."""

        # The te value in picoseconds.
        te = te * 1e12

        # The bond width (aiming for a width range of 2 to 0 for te values of 0 to 10 ns).
        width = 2.0 - 200.0 / (te + 100.0)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (hyperbolic).
        colour_value = 1.0 / (te / 100.0 + 1.0)

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'turquoise'
        if colour_end == None:
            colour_end = 'blue'

        # Get the RGB colour array (swap the colours because of the inverted hyperbolic colour value).
        rgb_array = self.relax.colour.linear_gradient(colour_value, colour_end, colour_start, colour_list)

        # Colour the peptide bond.
        self.classic_colour(residue.num, width, rgb_array)


    def classic_header(self):
        """Create the header for the molmol macro."""

        # Hide all bonds.
        self.commands.append("SelectBond ''")
        self.commands.append("StyleBond invisible")

        # Show the backbone bonds as lines.
        self.commands.append("SelectBond 'bb'")
        self.commands.append("StyleBond line")

        # Colour the backbone black.
        self.commands.append("ColorBond 0 0 0")


    def classic_order_param(self, residue, s2, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for order parameters."""

        # The bond width (aiming for a width range of 2 to 0 for S2 values of 0.0 to 1.0).
        if s2 <= 0.0:
            width = 2.0
        else:
            width = 2.0 * (1.0 - s2**2)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (quartic).
        colour_value = s2 ** 4

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'red'
        if colour_end == None:
            colour_end = 'yellow'

        # Get the RGB colour array.
        rgb_array = self.relax.colour.linear_gradient(colour_value, colour_start, colour_end, colour_list)

        # Colour the peptide bond.
        self.classic_colour(residue.num, width, rgb_array)


    def classic_rex(self, residue, rex, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for correlation times."""

        # The Rex value at the first field strength.
        rex = rex * (2.0 * pi * self.relax.data.frq[self.run][0])**2

        # The bond width (aiming for a width range of 2 to 0 for Rex values of 0 to 25 s^-1).
        width = 2.0 - 2.0 / (rex/5.0 + 1.0)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (hyperbolic).
        colour_value = 1.0 / (rex + 1.0)

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'yellow'
        if colour_end == None:
            colour_end = 'red'

        # Get the RGB colour array (swap the colours because of the inverted hyperbolic colour value).
        rgb_array = self.relax.colour.linear_gradient(colour_value, colour_end, colour_start, colour_list)

        # Colour the peptide bond.
        self.classic_colour(residue.num, width, rgb_array)


    def macro(self, run, data_type, style, colour_start, colour_end, colour_list):
        """Create and return an array of Molmol macros of the model-free parameters."""

        # Arguments.
        self.run = run

        # Initialise.
        self.commands = []

        # The classic style.
        if style == 'classic':
            self.classic(data_type, colour_start, colour_end, colour_list)

        # Unknown style.
        else:
            raise RelaxStyleError, style

        # Return the command array.
        return self.commands
