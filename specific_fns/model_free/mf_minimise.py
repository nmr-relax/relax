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
from LinearAlgebra import inverse
from math import pi
from Numeric import Float64, array, matrixmultiply, zeros
from re import match

# relax module imports.
from data import Data as relax_data_store
from float import isNaN, isInf
from generic_fns.selection import spin_loop
from maths_fns.mf import Mf
from minimise.generic import generic_minimise
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
            relax_data = [array(data.relax_data, Float64)]
            relax_error = [array(data.relax_error, Float64)]

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


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The model-free grid search function.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          array of int
        @param constraints: If True, constraints are applied during the grid search (elinating parts
                            of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        @param sim_index:   The index of the simulation to apply the grid search to.  If None, the
                            normal model is optimised.
        @type sim_index:    int
        """

        # Create the initial parameter vector.
        param_vector = self.assemble_param_vector()

        # The length of the parameter array.
        n = len(param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            print "Cannot run a grid search on a model with zero parameters, skipping the grid search."

        # Test the grid search options.
        self.test_grid_ops(lower=lower, upper=upper, inc=inc, n=n)

        # If inc is a single int, convert it into an array of that value.
        if type(inc) == int:
            temp = []
            for j in xrange(n):
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

        # Model-free parameters (residue specific parameters).
        if param_set != 'diff':
            # Spin loop.
            for spin in spin_loop():
                # Skip unselected residues.
                if not spin.select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(spin.params)):
                    # Local tm.
                    if spin.params[j] == 'local_tm':
                        min_options.append([inc[m], 1.0 * 1e-9, 12.0 * 1e-9])

                    # {S2, S2f, S2s}.
                    elif match('S2', spin.params[j]):
                        min_options.append([inc[m], 0.0, 1.0])

                    # {te, tf, ts}.
                    elif match('t', spin.params[j]):
                        min_options.append([inc[m], 0.0, 500.0 * 1e-12])

                    # Rex.
                    elif spin.params[j] == 'Rex':
                        min_options.append([inc[m], 0.0, 5.0 / (2.0 * pi * spin.frq[0])**2])

                    # Bond length.
                    elif spin.params[j] == 'r':
                        min_options.append([inc[m], 1.0 * 1e-10, 1.05 * 1e-10])

                    # CSA.
                    elif spin.params[j] == 'CSA':
                        min_options.append([inc[m], -120 * 1e-6, -200 * 1e-6])

                    # Unknown option.
                    else:
                        raise RelaxError, "Unknown model-free parameter."

                    # Increment m.
                    m = m + 1

        # Set the lower and upper bounds if these are supplied.
        if lower != None:
            for j in xrange(n):
                if lower[j] != None:
                    min_options[j][1] = lower[j]
        if upper != None:
            for j in xrange(n):
                if upper[j] != None:
                    min_options[j][2] = upper[j]

        # Test if the grid is too large.
        grid_size = 1
        for i in xrange(len(min_options)):
            grid_size = grid_size * min_options[i][0]
        if type(grid_size) == long:
            raise RelaxError, "A grid search of size " + `grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / scaling_matrix[j, j]

        # Minimisation.
        self.minimise(min_algor='grid', min_options=min_options, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, scaling=1, verbosity=0, sim_index=None):
        """Model-free minimisation.

        Three types of parameter sets exist for which minimisation is different.  These are:
            'mf' - Model-free parameters for single residues.
            'diff' - Diffusion tensor parameters.
            'all' - All model-free and all diffusion tensor parameters.
        """

        # Arguments.
        self.run = run
        self.verbosity = verbosity

        # Test if the sequence data for self.run is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the model-free model has been setup.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][i].select:
                continue

            # Not setup.
            if not relax_data_store.res[self.run][i].model:
                raise RelaxNoModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Parameter set for the back-calculate function.
        if min_algor == 'back_calc' and self.param_set != 'local_tm':
            self.param_set = 'mf'

        # Test if diffusion tensor data for the run exists.
        if self.param_set != 'local_tm' and not relax_data_store.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Tests for the PDB file and unit vectors.
        if self.param_set != 'local_tm' and relax_data_store.diff[self.run].type != 'sphere':
            # Test if the PDB file has been loaded.
            if not relax_data_store.pdb.has_key(self.run):
                raise RelaxNoPdbError, self.run

            # Test if unit vectors exist.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Skip unselected residues.
                if not relax_data_store.res[self.run][i].select:
                    continue

                # Unit vector.
                if not hasattr(relax_data_store.res[self.run][i], 'xh_vect'):
                    raise RelaxNoVectorsError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(relax_data_store, 'gx'):
            raise RelaxNucleusError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if self.param_set == 'diff':
            # Loop over the sequence.
            for i in xrange(len(relax_data_store.res[self.run])):
                unset_param = self.are_mf_params_set(i)
                if unset_param != None:
                    raise RelaxNoValueError, unset_param

        # Print out.
        if self.verbosity >= 1:
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
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][i].select:
                continue

            # CSA value.
            if not hasattr(relax_data_store.res[self.run][i], 'csa') or relax_data_store.res[self.run][i].csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(relax_data_store.res[self.run][i], 'r') or relax_data_store.res[self.run][i].r == None:
                raise RelaxNoValueError, "bond length"

            # Increment the number of residues.
            num_res = num_res + 1

        # Number of residues, minimisation instances, and data sets for each parameter set type.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            num_instances = len(relax_data_store.res[self.run])
            num_data_sets = 1
            num_res = 1
        elif self.param_set == 'diff' or self.param_set == 'all':
            num_instances = 1
            num_data_sets = len(relax_data_store.res[self.run])

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
                if not relax_data_store.res[self.run][i].select:
                    continue

                # Skip residues where there is no data or errors.
                if not hasattr(relax_data_store.res[self.run][i], 'relax_data') or not hasattr(relax_data_store.res[self.run][i], 'relax_error'):
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
            if self.verbosity >= 1:
                # Individual residue stuff.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    if self.verbosity >= 2:
                        print "\n\n"
                    string = "Fitting to residue: " + `relax_data_store.res[self.run][index].num` + " " + relax_data_store.res[self.run][index].name
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
            if self.param_set == 'local_tm':
                mf_params = []
            elif self.param_set == 'diff':
                param_values = []

            # Set up the data for the back_calc function.
            if min_algor == 'back_calc':
                # The data.
                relax_data = [0.0]
                relax_error = [0.000001]
                equations = [relax_data_store.res[self.run][index].equation]
                param_types = [relax_data_store.res[self.run][index].params]
                r = [relax_data_store.res[self.run][index].r]
                csa = [relax_data_store.res[self.run][index].csa]
                num_frq = [1]
                frq = [[min_options[3]]]
                num_ri = [1]
                remap_table = [[0]]
                noe_r1_table = [[None]]
                ri_labels = [[min_options[1]]]
                if self.param_set != 'local_tm' and relax_data_store.diff[self.run].type != 'sphere':
                    xh_unit_vectors = [relax_data_store.res[self.run][index].xh_vect]
                else:
                    xh_unit_vectors = [None]

                # Count the number of model-free parameters for the residue index.
                num_params = [len(relax_data_store.res[self.run][index].params)]

            # Loop over the number of data sets.
            for j in xrange(num_data_sets):
                # Set the sequence index.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    seq_index = i
                else:
                    seq_index = j

                # Alias the data structure.
                data = relax_data_store.res[self.run][seq_index]

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
                else:
                    relax_data.append(data.relax_sim_data[sim_index])
                relax_error.append(data.relax_error)
                equations.append(data.equation)
                param_types.append(data.params)
                num_frq.append(data.num_frq)
                frq.append(data.frq)
                num_ri.append(data.num_ri)
                remap_table.append(data.remap_table)
                noe_r1_table.append(data.noe_r1_table)
                ri_labels.append(data.ri_labels)
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
                if self.param_set != 'local_tm' and relax_data_store.diff[self.run].type != 'sphere':
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

            # Diffusion tensor type.
            if self.param_set == 'local_tm':
                diff_type = 'sphere'
            else:
                diff_type = relax_data_store.diff[self.run].type

            # Package the diffusion tensor parameters.
            diff_params = None
            if self.param_set == 'mf':
                # Alias.
                data = relax_data_store.diff[self.run]

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
                diff_params = [relax_data_store.res[self.run][index].local_tm]



            # Initialise the function to minimise.
            ######################################

            self.mf = Mf(init_params=self.param_vector, param_set=self.param_set, diff_type=diff_type, diff_params=diff_params, scaling_matrix=self.scaling_matrix, num_res=num_res, equations=equations, param_types=param_types, param_values=param_values, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=relax_data_store.gx, gh=relax_data_store.gh, g_ratio=relax_data_store.g_ratio, h_bar=relax_data_store.h_bar, mu0=relax_data_store.mu0, num_params=num_params, vectors=xh_unit_vectors)


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

                min_options = min_options + (self.mf.lm_dri, lm_error)


            # Back-calculation.
            ###################

            if min_algor == 'back_calc':
                return self.mf.calc_ri()


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=verbosity)
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
                    relax_data_store.res[self.run][i].chi2_sim[sim_index] = self.func

                    # Iterations.
                    relax_data_store.res[self.run][i].iter_sim[sim_index] = self.iter_count

                    # Function evaluations.
                    relax_data_store.res[self.run][i].f_count_sim[sim_index] = self.f_count

                    # Gradient evaluations.
                    relax_data_store.res[self.run][i].g_count_sim[sim_index] = self.g_count

                    # Hessian evaluations.
                    relax_data_store.res[self.run][i].h_count_sim[sim_index] = self.h_count

                    # Warning.
                    relax_data_store.res[self.run][i].warning_sim[sim_index] = self.warning

                # Global minimisation statistics.
                elif self.param_set == 'diff' or self.param_set == 'all':
                    # Chi-squared statistic.
                    relax_data_store.chi2_sim[self.run][sim_index] = self.func

                    # Iterations.
                    relax_data_store.iter_sim[self.run][sim_index] = self.iter_count

                    # Function evaluations.
                    relax_data_store.f_count_sim[self.run][sim_index] = self.f_count

                    # Gradient evaluations.
                    relax_data_store.g_count_sim[self.run][sim_index] = self.g_count

                    # Hessian evaluations.
                    relax_data_store.h_count_sim[self.run][sim_index] = self.h_count

                    # Warning.
                    relax_data_store.warning_sim[self.run][sim_index] = self.warning

            # Normal statistics.
            else:
                # Sequence specific minimisation statistics.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    # Chi-squared statistic.
                    relax_data_store.res[self.run][i].chi2 = self.func

                    # Iterations.
                    relax_data_store.res[self.run][i].iter = self.iter_count

                    # Function evaluations.
                    relax_data_store.res[self.run][i].f_count = self.f_count

                    # Gradient evaluations.
                    relax_data_store.res[self.run][i].g_count = self.g_count

                    # Hessian evaluations.
                    relax_data_store.res[self.run][i].h_count = self.h_count

                    # Warning.
                    relax_data_store.res[self.run][i].warning = self.warning

                # Global minimisation statistics.
                elif self.param_set == 'diff' or self.param_set == 'all':
                    # Chi-squared statistic.
                    relax_data_store.chi2[self.run] = self.func

                    # Iterations.
                    relax_data_store.iter[self.run] = self.iter_count

                    # Function evaluations.
                    relax_data_store.f_count[self.run] = self.f_count

                    # Gradient evaluations.
                    relax_data_store.g_count[self.run] = self.g_count

                    # Hessian evaluations.
                    relax_data_store.h_count[self.run] = self.h_count

                    # Warning.
                    relax_data_store.warning[self.run] = self.warning
