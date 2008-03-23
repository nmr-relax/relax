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
from numpy import float64, array, dot, zeros
from numpy.linalg import inv
from re import match

# relax module imports.
from data import Data as relax_data_store
from float import isNaN, isInf
from generic_fns import diffusion_tensor
from generic_fns.selection import count_spins, exists_mol_res_spin_data, return_spin_from_index, spin_loop
from maths_fns.mf import Mf
from minfx.generic import generic_minimise
from relax_errors import RelaxError, RelaxInfError, RelaxLenError, RelaxNaNError, RelaxNoModelError, RelaxNoPdbError, RelaxNoResError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoValueError, RelaxNoVectorsError, RelaxNucleusError



class Mf_minimise:
    """Class containing functions specific to model-free optimisation."""


    def back_calc(self, run=None, index=None, ri_label=None, frq_label=None, frq=None):
        """Back-calculation of relaxation data from the model-free parameter values."""

        # Run argument.
        self.run = run

        # Get the relaxation value from the minimise function.
        value = self.minimise(run=self.run, min_algor='back_calc', min_options=(index, ri_label, frq_label, frq))

        # Return the relaxation value.
        return value


    def calculate(self, run=None, res_num=None, verbosity=1, sim_index=None):
        """Calculation of the model-free chi-squared value."""

        # Arguments.
        self.run = run
        self.verbosity = verbosity

        # Test if the sequence data for self.run is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # The residue index.
        index = None
        if res_num != None:
            # Loop over the sequence.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Found the residue.
                if relax_data_store.res[self.run][i].num == res_num:
                    index = i
                    break

            # Can't find the residue.
            if index == None:
                raise RelaxNoResError, res_num

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Test if diffusion tensor data for the run exists.
        if self.param_set != 'local_tm' and not relax_data_store.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Test if the PDB file has been loaded.
        if self.param_set != 'local_tm' and relax_data_store.diff[self.run].type != 'sphere' and not relax_data_store.pdb.has_key(self.run):
            raise RelaxNoPdbError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(relax_data_store, 'gx'):
            raise RelaxNucleusError

        # Loop over the residues.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Alias the data structure.
            data = relax_data_store.res[self.run][i]

            # Skip deselected residues.
            if not data.select:
                continue

            # Single residue.
            if index != None and index != i:
                continue

            # Test if the model-free model has been setup.
            if not data.model:
                raise RelaxNoModelError, self.run

            # Test if unit vectors exist.
            if self.param_set != 'local_tm' and relax_data_store.diff[self.run].type != 'sphere' and not hasattr(data, 'xh_vect'):
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
                r = [data.r]
                csa = [data.csa]
            else:
                relax_data = [data.relax_sim_data[sim_index]]
                r = [data.r_sim[sim_index]]
                csa = [data.csa_sim[sim_index]]

            # Vectors.
            if self.param_set != 'local_tm' and relax_data_store.diff[self.run].type != 'sphere':
                xh_unit_vectors = [data.xh_vect]
            else:
                xh_unit_vectors = [None]

            # Count the number of model-free parameters for the residue index.
            num_params = [len(data.params)]

            # Repackage the parameter values for minimising just the diffusion tensor parameters.
            param_values = [self.assemble_param_vector(param_set='mf')]

            # Convert to Numeric arrays.
            relax_data = [array(data.relax_data, float64)]
            relax_error = [array(data.relax_error, float64)]

            # Package the diffusion tensor parameters.
            if self.param_set == 'local_tm':
                diff_params = [relax_data_store.res[self.run][i].local_tm]
                diff_type = 'sphere'
            else:
                # Alias.
                diff_data = relax_data_store.diff[self.run]

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
            self.mf = Mf(init_params=self.param_vector, param_set='mf', diff_type=diff_type, diff_params=diff_params, num_res=1, equations=[data.equation], param_types=[data.params], param_values=param_values, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=[data.num_frq], frq=[data.frq], num_ri=[data.num_ri], remap_table=[data.remap_table], noe_r1_table=[data.noe_r1_table], ri_labels=[data.ri_labels], gx=relax_data_store.gx, gh=relax_data_store.gh, g_ratio=relax_data_store.g_ratio, h_bar=relax_data_store.h_bar, mu0=relax_data_store.mu0, num_params=num_params, vectors=xh_unit_vectors)

            # Chi-squared calculation.
            try:
                chi2 = self.mf.func(self.param_vector)
            except OverflowError:
                chi2 = 1e200

            # Global chi-squared value.
            if self.param_set == 'all' or self.param_set == 'diff':
                relax_data_store.chi2[self.run] = relax_data_store.chi2[self.run] + chi2
            else:
                relax_data_store.res[self.run][i].chi2 = chi2


    def disassemble_param_vector(self, index=None, sim_index=None):
        """Function for disassembling the parameter vector."""

        # Initialise.
        param_index = 0

        # Diffusion tensor parameters of the Monte Carlo simulations.
        if sim_index != None and (self.param_set == 'diff' or self.param_set == 'all'):
            # Spherical diffusion.
            if relax_data_store.diff[self.run].type == 'sphere':
                # Sim values.
                relax_data_store.diff[self.run].tm_sim[sim_index] = self.param_vector[0]

                # Parameter index.
                param_index = param_index + 1

            # Spheroidal diffusion.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                # Sim values.
                relax_data_store.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                relax_data_store.diff[self.run].Da_sim[sim_index] = self.param_vector[1]
                relax_data_store.diff[self.run].theta_sim[sim_index] = self.param_vector[2]
                relax_data_store.diff[self.run].phi_sim[sim_index] = self.param_vector[3]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run, sim_index=sim_index)

                # Parameter index.
                param_index = param_index + 4

            # Ellipsoidal diffusion.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                # Sim values.
                relax_data_store.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                relax_data_store.diff[self.run].Da_sim[sim_index] = self.param_vector[1]
                relax_data_store.diff[self.run].Dr_sim[sim_index] = self.param_vector[2]
                relax_data_store.diff[self.run].alpha_sim[sim_index] = self.param_vector[3]
                relax_data_store.diff[self.run].beta_sim[sim_index] = self.param_vector[4]
                relax_data_store.diff[self.run].gamma_sim[sim_index] = self.param_vector[5]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run, sim_index=sim_index)

                # Parameter index.
                param_index = param_index + 6

        # Diffusion tensor parameters.
        elif self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if relax_data_store.diff[self.run].type == 'sphere':
                # Values.
                relax_data_store.diff[self.run].tm = self.param_vector[0]

                # Parameter index.
                param_index = param_index + 1

            # Spheroidal diffusion.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                # Values.
                relax_data_store.diff[self.run].tm = self.param_vector[0]
                relax_data_store.diff[self.run].Da = self.param_vector[1]
                relax_data_store.diff[self.run].theta = self.param_vector[2]
                relax_data_store.diff[self.run].phi = self.param_vector[3]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run)

                # Parameter index.
                param_index = param_index + 4

            # Ellipsoidal diffusion.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                # Values.
                relax_data_store.diff[self.run].tm = self.param_vector[0]
                relax_data_store.diff[self.run].Da = self.param_vector[1]
                relax_data_store.diff[self.run].Dr = self.param_vector[2]
                relax_data_store.diff[self.run].alpha = self.param_vector[3]
                relax_data_store.diff[self.run].beta = self.param_vector[4]
                relax_data_store.diff[self.run].gamma = self.param_vector[5]
                self.relax.generic.diffusion_tensor.fold_angles(run=self.run)

                # Parameter index.
                param_index = param_index + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Remap the residue data structure.
                data = relax_data_store.res[self.run][i]

                # Skip deselected residues.
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
            for i in xrange(len(relax_data_store.res[self.run])):
                # Remap the residue data structure.
                data = relax_data_store.res[self.run][i]

                # Skip deselected residues.
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


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The model-free grid search function.

        @keyword lower:         The lower bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.
                                The number of elements in the array must equal to the number of
                                parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating
                                parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None,
                                the normal model is optimised.
        @type sim_index:        int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def grid_search_config(self, num_params, spin=None, spin_id=None, lower=None, upper=None, inc=None, scaling_matrix=None):
        """Configure the grid search.

        @param num_params:          The number of parameters in the model.
        @type num_params:           int
        @keyword spin:              The spin data container.
        @type spin:                 SpinContainer instance
        @keyword spin_id:           The spin identification string.
        @type spin_id:              str
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.
                                    The number of elements in the array must equal to the number of
                                    parameters in the model.
        @type inc:                  array of int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Make sure that the length of the parameter array is > 0.
        if num_params == 0:
            print "Cannot run a grid search on a model with zero parameters, skipping the grid search."

        # Test the grid search options.
        self.test_grid_ops(lower=lower, upper=upper, inc=inc, n=num_params)

        # If inc is a single int, convert it into an array of that value.
        if type(inc) == int:
            temp = []
            for i in xrange(num_params):
                temp.append(inc)
            inc = temp

        # Minimisation options initialisation.
        min_options = []
        m = 0

        # Determine the parameter set type.
        param_set = self.determine_param_set_type()

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Minimisation options for diffusion tensor parameters.
        if param_set == 'diff' or param_set == 'all':
            # Get the diffusion tensor specific configuration.
            m = self.grid_search_config_diff(min_options, inc, m)

        # Model-free parameters (residue specific parameters).
        if param_set != 'diff':
            # The loop.
            if spin:
                loop = [spin]
            else:
                loop = spin_loop(spin_id)

            # Loop over the spins.
            for spin in loop:
                # Skip deselected residues.
                if not spin.select:
                    continue

                # Get the spin specific configuration.
                m = self.grid_search_config_spin(min_options, spin, inc, m)

        # Test if the grid is too large.
        self.test_grid_size(min_options)

        # Complete the grid search configuration.
        self.grid_search_config_fin(min_options, lower, upper, scaling_matrix)


    def grid_search_config_diff(self, min_options, inc, m):
        """Set up of the grid search for the diffusion tensor.

        This method appends the grid search configuration details to min_options list.  These
        details are in the form of a list consisting of the number of increments, lower bound, and
        upper bound for the corresponding residue.

        @param min_options: An array to append the grid search configuration details to.
        @type min_options:  list
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          array of int
        @param m:           The parameter index for the complete model.
        @type m:            int
        @return:            The index of the last parameter encountered (m).
        @rtype:             int
        """

        # Spherical diffusion {tm}.
        if cdp.diff.type == 'sphere':
            min_options.append([inc[0], 1.0 * 1e-9, 12.0 * 1e-9])
            m = m + 1

        # Spheroidal diffusion {tm, Da, theta, phi}.
        if cdp.diff.type == 'spheroid':
            min_options.append([inc[0], 1.0 * 1e-9, 12.0 * 1e-9])
            if cdp.diff.spheroid_type == 'prolate':
                min_options.append([inc[1], 0.0, 1e7])
            elif cdp.diff.spheroid_type == 'oblate':
                min_options.append([inc[1], -1e7, 0.0])
            else:
                min_options.append([inc[1], -1e7, 1e7])
            min_options.append([inc[2], 0.0, pi])
            min_options.append([inc[3], 0.0, pi])
            m = m + 4

        # Ellipsoidal diffusion {tm, Da, Dr, alpha, beta, gamma}.
        elif cdp.diff.type == 'ellipsoid':
            min_options.append([inc[0], 1.0 * 1e-9, 12.0 * 1e-9])
            min_options.append([inc[1], 0.0, 1e7])
            min_options.append([inc[2], 0.0, 1.0])
            min_options.append([inc[3], 0.0, pi])
            min_options.append([inc[4], 0.0, pi])
            min_options.append([inc[5], 0.0, pi])
            m = m + 6

        # Return the parameter index.
        return m


    def grid_search_config_fin(self, min_options, lower, upper, scaling_matrix):
        """Complete the grid search configuration.

        @param min_options:     The grid search configuration details.
        @type min_options:      list of lists (n, 3)
        @param lower:           The lower bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type lower:            array of numbers
        @param upper:           The upper bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type upper:            array of numbers
        @param scaling_matrix:  The scaling matrix.
        @type scaling_matrix:   numpy matrix
        """

        # Set the lower and upper bounds if these are supplied.
        if lower != None:
            for i in xrange(n):
                if lower[i] != None:
                    min_options[i][1] = lower[i]
        if upper != None:
            for i in xrange(n):
                if upper[i] != None:
                    min_options[i][2] = upper[i]

        # Diagonal scaling of minimisation options.
        for i in xrange(len(min_options)):
            min_options[i][1] = min_options[i][1] / scaling_matrix[i, i]
            min_options[i][2] = min_options[i][2] / scaling_matrix[i, i]


    def grid_search_config_spin(self, min_options, spin, inc, m):
        """Set up of the grid search for a single spin.

        This method appends the grid search configuration details to min_options list.  These
        details are in the form of a list consisting of the number of increments, lower bound, and
        upper bound for the corresponding residue.  The ordering of the lists in min_options matches
        that of the params list in the spin container.

        @param min_options: An array to append the grid search configuration details to.
        @type min_options:  list
        @param spin:        A SpinContainer object.
        @type spin:         class instance
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          array of int
        @param m:           The parameter index for the complete model.
        @type m:            int
        @return:            The index of the last parameter encountered (m).
        @rtype:             int
        """

        # Loop over the model-free parameters.
        for i in xrange(len(spin.params)):
            # Local tm.
            if spin.params[i] == 'local_tm':
                min_options.append([inc[m], 1.0 * 1e-9, 12.0 * 1e-9])

            # {S2, S2f, S2s}.
            elif match('S2', spin.params[i]):
                min_options.append([inc[m], 0.0, 1.0])

            # {te, tf, ts}.
            elif match('t', spin.params[i]):
                min_options.append([inc[m], 0.0, 500.0 * 1e-12])

            # Rex.
            elif spin.params[i] == 'Rex':
                min_options.append([inc[m], 0.0, 5.0 / (2.0 * pi * spin.frq[0])**2])

            # Bond length.
            elif spin.params[i] == 'r':
                min_options.append([inc[m], 1.0 * 1e-10, 1.05 * 1e-10])

            # CSA.
            elif spin.params[i] == 'CSA':
                min_options.append([inc[m], -120 * 1e-6, -200 * 1e-6])

            # Unknown option.
            else:
                raise RelaxError, "Unknown model-free parameter."

            # Increment m.
            m = m + 1

        # Return the parameter index.
        return m


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, scaling=1, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Model-free minimisation function.

        Three categories of parameter sets exist for which the approach to minimisation is
        different.  These are:

        Single spins optimisation:  The 'mf' and 'local_tm' parameter sets which are the
        model-free parameters for single spins, optionally with a local tm parameter.  These
        models have no global parameters.

        Diffusion tensor optimisations:  The 'diff' diffusion tensor parameter set.  No spin
        specific parameters exist.

        Optimisation of everything:  The 'all' parameter set consisting of all model-free and all
        diffusion tensor parameters.


        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerence which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerence which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow
                                    the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the
                                    greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if
                                    normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.
                                    The number of elements in the array must equal to the number of
                                    parameters in the model.  This argument is only used when doing a
                                    grid search.
        @type inc:                  array of int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model-free model has been setup.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

        # Determine the parameter set type.
        param_set = self.determine_param_set_type()

        # Parameter set for the back-calculate function.
        if min_algor == 'back_calc' and param_set != 'local_tm':
            param_set = 'mf'

        # Test if diffusion tensor data exists.
        if param_set != 'local_tm' and not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError, 'diffusion'

        # Tests for the PDB file, unit vectors, and nuclues type.
        if param_set != 'local_tm' and cdp.diff_tensor.type != 'sphere':
            # Test if the structure file has been loaded.
            if not hasattr(cdp.structure, 'structures'):
                raise RelaxNoPdbError

            # Test if unit vectors exist.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Unit vector.
                if not hasattr(spin, 'xh_vect'):
                    raise RelaxNoVectorsError

            # Test if the nucleus type has been set.
            if not hasattr(spin, 'nucleus'):
                raise RelaxNucleusError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if param_set == 'diff':
            # Loop over the sequence.
            for spin in spin_loop():
                unset_param = self.are_mf_params_set(spin)
                if unset_param != None:
                    raise RelaxNoValueError, unset_param

        # Print out.
        if verbosity >= 1:
            if param_set == 'mf':
                print "Only the model-free parameters for single spins will be used."
            elif param_set == 'local_mf':
                print "Only a local tm value together with the model-free parameters for single spins will be used."
            elif param_set == 'diff':
                print "Only diffusion tensor parameters will be used."
            elif param_set == 'all':
                print "The diffusion tensor parameters together with the model-free parameters for all spins will be used."

        # Test if the CSA and bond length values have been set.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # CSA value.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError, "bond length"

        # Number of spins, minimisation instances, and data sets for each parameter set type.
        if param_set == 'mf' or param_set == 'local_tm':
            num_instances = count_spins()
            num_data_sets = 1
            num_spins = 1
        elif param_set == 'diff' or param_set == 'all':
            num_instances = 1
            num_data_sets = count_spins()
            num_spins = count_selected_spins()

        # Number of spins, minimisation instances, and data sets for the back-calculate function.
        if min_algor == 'back_calc':
            num_instances = 1
            num_data_sets = 0
            num_spins = 1


        # Loop over the minimisation instances.
        #######################################

        for i in xrange(num_instances):
            # Get the spin container if required.
            if param_set == 'diff' or param_set == 'all':
                spin_index = None
                spin, spin_id = None, None
            elif min_algor == 'back_calc':
                spin_index = min_options[0]
                spin, spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)
            else:
                spin_index = i
                spin, spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

            # Individual spin stuff.
            if spin and (param_set == 'mf' or param_set == 'local_tm') and not min_algor == 'back_calc':
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins missing relaxation data or errors.
                if not hasattr(spin, 'relax_data') or not hasattr(spin, 'relax_error'):
                    continue

            # Parameter vector and diagonal scaling.
            if min_algor == 'back_calc':
                # Create the initial parameter vector.
                param_vector = self.assemble_param_vector(spin=spin)

                # Diagonal scaling.
                scaling_matrix = None

            else:
                # Create the initial parameter vector.
                param_vector = self.assemble_param_vector(spin=spin, sim_index=sim_index)

                # The number of parameters.
                num_params = len(param_vector)

                # Diagonal scaling.
                scaling_matrix = self.assemble_scaling_matrix(num_params, param_set=param_set, spin=spin, scaling=scaling)
                if len(scaling_matrix):
                    param_vector = dot(inv(scaling_matrix), param_vector)

            # Configure the grid search.
            if match('^[Gg]rid', min_algor):
                min_options = self.grid_search_config(num_params, spin=spin, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                min_options = dot(inv(scaling_matrix), min_options)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(num_params, param_set=param_set, spin=spin, scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity >= 1:
                # Individual spin stuff.
                if param_set == 'mf' or param_set == 'local_tm':
                    if verbosity >= 2:
                        print "\n\n"
                    string = "Fitting to spin " + `spin_id`
                    print "\n\n" + string
                    print len(string) * '~'
                if match('^[Gg]rid', min_algor):
                    print "Unconstrained grid search size: " + `grid_size` + " (constraints may decrease this size).\n"

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            iter_count = 0
            f_count = 0
            g_count = 0
            h_count = 0


            # Initialise the function to minimise.
            ######################################

            self.mf = Mf(init_params=param_vector, param_set=param_set, diff_type=diff_type, diff_params=diff_params, scaling_matrix=scaling_matrix, num_spins=num_spins, equations=equations, param_types=param_types, param_values=param_values, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=relax_data_store.gx, gh=relax_data_store.gh, g_ratio=relax_data_store.g_ratio, h_bar=relax_data_store.h_bar, mu0=relax_data_store.mu0, num_params=num_params, vectors=xh_unit_vectors)


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
                lm_error = zeros(number_ri, float64)
                index = 0
                for k in xrange(len(relax_error)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.mf.lm_dri, lm_error)


            # Back-calculation.
            ###################

            if min_algor == 'back_calc':
                return self.mf.calc_ri()


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=verbosity)
            if results == None:
                return
            param_vector, func, iter, fc, gc, hc, warning = results
            iter_count = iter_count + iter
            f_count = f_count + fc
            g_count = g_count + gc
            h_count = h_count + hc

            # Catch infinite chi-squared values.
            if isInf(func):
                raise RelaxInfError, 'chi-squared'

            # Catch chi-squared values of NaN.
            if isNaN(func):
                raise RelaxNaNError, 'chi-squared'

            # Scaling.
            if scaling:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(index=index, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Sequence specific minimisation statistics.
                if param_set == 'mf' or param_set == 'local_tm':
                    # Chi-squared statistic.
                    spin.chi2_sim[sim_index] = func

                    # Iterations.
                    spin.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    spin.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    spin.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    spin.h_count_sim[sim_index] = h_count

                    # Warning.
                    spin.warning_sim[sim_index] = warning

                # Global minimisation statistics.
                elif param_set == 'diff' or param_set == 'all':
                    # Chi-squared statistic.
                    cdp.chi2_sim[sim_index] = func

                    # Iterations.
                    cdp.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    cdp.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    cdp.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    cdp.h_count_sim[sim_index] = h_count

                    # Warning.
                    cdp.warning_sim[sim_index] = warning

            # Normal statistics.
            else:
                # Sequence specific minimisation statistics.
                if param_set == 'mf' or param_set == 'local_tm':
                    # Chi-squared statistic.
                    spin.chi2 = func

                    # Iterations.
                    spin.iter = iter_count

                    # Function evaluations.
                    spin.f_count = f_count

                    # Gradient evaluations.
                    spin.g_count = g_count

                    # Hessian evaluations.
                    spin.h_count = h_count

                    # Warning.
                    spin.warning = warning

                # Global minimisation statistics.
                elif param_set == 'diff' or param_set == 'all':
                    # Chi-squared statistic.
                    cdp.chi2 = func

                    # Iterations.
                    cdp.iter = iter_count

                    # Function evaluations.
                    cdp.f_count = f_count

                    # Gradient evaluations.
                    cdp.g_count = g_count

                    # Hessian evaluations.
                    cdp.h_count = h_count

                    # Warning.
                    cdp.warning = warning


    def minimise_data_setup():
        """Set up all the data required for minimisation.

        @return:        An insane tuple.  The full tuple is (relax_data, relax_error, equations,
                        param_types, param_values, r, csa, num_frq, frq, num_ri, remap_table,
                        noe_r1_table, ri_labels, num_params, xh_unit_vectors, diff_type,
                        diff_params)
        @rtype:         tuple
        """

        # Initialise the data structures for the model-free function.
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
        remap_table = []
        noe_r1_table = []
        ri_labels = []
        num_params = []
        xh_unit_vectors = []
        if param_set == 'local_tm':
            mf_params = []
        elif param_set == 'diff':
            param_values = []

        # Set up the data for the back_calc function.
        if min_algor == 'back_calc':
            # The data.
            relax_data = [0.0]
            relax_error = [0.000001]
            equations = [spin.equation]
            param_types = [spin.params]
            r = [spin.r]
            csa = [spin.csa]
            num_frq = [1]
            frq = [[min_options[3]]]
            num_ri = [1]
            remap_table = [[0]]
            noe_r1_table = [[None]]
            ri_labels = [[min_options[1]]]
            if param_set != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                xh_unit_vectors = [spin.xh_vect]
            else:
                xh_unit_vectors = [None]

            # Count the number of model-free parameters for the spin index.
            num_params = [len(spin.params)]

        # Loop over the number of data sets.
        for j in xrange(num_data_sets):
            # Set the spin index and get the spin, if not already set.
            if param_set == 'diff' or param_set == 'all':
                spin_index = j
                spin = return_spin_from_index(global_index=spin_index)

            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins where there is no data or errors.
            if not hasattr(spin, 'relax_data') or not hasattr(spin, 'relax_error'):
                continue

            # Make sure that the errors are strictly positive numbers.
            for k in xrange(len(spin.relax_error)):
                if spin.relax_error[k] == 0.0:
                    raise RelaxError, "Zero error for spin '" + `spin.num` + " " + spin.name + "', minimisation not possible."
                elif spin.relax_error[k] < 0.0:
                    raise RelaxError, "Negative error for spin '" + `spin.num` + " " + spin.name + "', minimisation not possible."

            # Repackage the data.
            if sim_index == None:
                relax_data.append(spin.relax_data)
            else:
                relax_data.append(spin.relax_sim_data[sim_index])
            relax_error.append(spin.relax_error)
            equations.append(spin.equation)
            param_types.append(spin.params)
            num_frq.append(spin.num_frq)
            frq.append(spin.frq)
            num_ri.append(spin.num_ri)
            remap_table.append(spin.remap_table)
            noe_r1_table.append(spin.noe_r1_table)
            ri_labels.append(spin.ri_labels)
            if sim_index == None or param_set == 'diff':
                r.append(spin.r)
                csa.append(spin.csa)
            else:
                r.append(spin.r_sim[sim_index])
                csa.append(spin.csa_sim[sim_index])

            # Model-free parameter values.
            if param_set == 'local_tm':
                pass

            # Vectors.
            if param_set != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                xh_unit_vectors.append(spin.xh_vect)
            else:
                xh_unit_vectors.append(None)

            # Count the number of model-free parameters for the spin index.
            num_params.append(len(spin.params))

            # Repackage the parameter values for minimising just the diffusion tensor parameters.
            if param_set == 'diff':
                param_values.append(self.assemble_param_vector(param_set='mf'))

        # Convert to numpy arrays.
        for k in xrange(len(relax_data)):
            relax_data[k] = array(relax_data[k], float64)
            relax_error[k] = array(relax_error[k], float64)

        # Diffusion tensor type.
        if param_set == 'local_tm':
            diff_type = 'sphere'
        else:
            diff_type = cdp.diff_tensor.type

        # Package the diffusion tensor parameters.
        diff_params = None
        if param_set == 'mf':
            # Spherical diffusion.
            if diff_type == 'sphere':
                diff_params = [cdp.diff_tensor.tm]

            # Spheroidal diffusion.
            elif diff_type == 'spheroid':
                diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.theta, cdp.diff_tensor.phi]

            # Ellipsoidal diffusion.
            elif diff_type == 'ellipsoid':
                diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.Dr, cdp.diff_tensor.alpha, cdp.diff_tensor.beta, cdp.diff_tensor.gamma]
        elif min_algor == 'back_calc' and param_set == 'local_tm':
            # Spherical diffusion.
            diff_params = [spin.local_tm]

        # Return all the data.
        return relax_data, relax_error, equations, param_types, param_values, r, csa, num_frq, frq, num_ri, remap_table, noe_r1_table, ri_labels, num_params, xh_unit_vectors, diff_type, diff_params


    def test_grid_size(self, min_options):
        """Test the size of the grid search.

        @param min_options: The grid search configuration.
        @type min_options:  list
        @raises RelaxError: If the grid size corresponds to a long int.
        """

        grid_size = 1
        for i in xrange(len(min_options)):
            grid_size = grid_size * min_options[i][0]
        if type(grid_size) == long:
            raise RelaxError, "A grid search of size " + `grid_size` + " is too large."
