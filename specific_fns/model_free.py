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

from copy import deepcopy
from LinearAlgebra import inverse
from math import pi
from Numeric import Float64, array, identity, matrixmultiply, ones, transpose, zeros
from re import match
from string import replace
import sys

from maths_fns.mf import Mf
from minimise.generic import generic_minimise


class Model_free:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def assemble_param_vector(self, index=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        self.param_vector = []

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                self.param_vector.append(self.relax.data.diff[self.run].tm)

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                self.param_vector.append(self.relax.data.diff[self.run].tm)
                self.param_vector.append(self.relax.data.diff[self.run].Diso)
                self.param_vector.append(self.relax.data.diff[self.run].theta)
                self.param_vector.append(self.relax.data.diff[self.run].phi)

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                self.param_vector.append(self.relax.data.diff[self.run].Dx)
                self.param_vector.append(self.relax.data.diff[self.run].Dy)
                self.param_vector.append(self.relax.data.diff[self.run].Dz)
                self.param_vector.append(self.relax.data.diff[self.run].alpha)
                self.param_vector.append(self.relax.data.diff[self.run].beta)
                self.param_vector.append(self.relax.data.diff[self.run].gamma)

        # Model-free parameters.
        if self.param_set == 'mf' or self.param_set == 'all':
            # Loop over all residues.
            for i in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    # tm.
                    if self.relax.data.res[i].params[self.run][j] == 'tm':
                        if self.relax.data.res[i].tm[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].tm[self.run])

                    # S2.
                    if self.relax.data.res[i].params[self.run][j] == 'S2':
                        if self.relax.data.res[i].s2[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].s2[self.run])

                    # S2f.
                    if self.relax.data.res[i].params[self.run][j] == 'S2f':
                        if self.relax.data.res[i].s2f[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].s2f[self.run])

                    # S2s.
                    if self.relax.data.res[i].params[self.run][j] == 'S2s':
                        if self.relax.data.res[i].s2s[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].s2s[self.run])

                    # te.
                    if self.relax.data.res[i].params[self.run][j] == 'te':
                        if self.relax.data.res[i].te[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].te[self.run])

                    # tf.
                    if self.relax.data.res[i].params[self.run][j] == 'tf':
                        if self.relax.data.res[i].tf[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].tf[self.run])

                    # ts.
                    if self.relax.data.res[i].params[self.run][j] == 'ts':
                        if self.relax.data.res[i].ts[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].ts[self.run])

                    # Rex.
                    if self.relax.data.res[i].params[self.run][j] == 'Rex':
                        if self.relax.data.res[i].rex[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].rex[self.run])

                    # r.
                    if self.relax.data.res[i].params[self.run][j] == 'r':
                        if self.relax.data.res[i].r[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].r[self.run])

                    # CSA.
                    if self.relax.data.res[i].params[self.run][j] == 'CSA':
                        if self.relax.data.res[i].csa[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].csa[self.run])

        # Convert to a Numeric array.
        self.param_vector = array(self.param_vector, Float64)

        # Debug.
        if Debug:
            print "Param vector: " + `self.param_vector`


    def assemble_scaling_matrix(self, index=None):
        """Function for creating the scaling matrix."""

        # Initialise.
        self.scaling_matrix = identity(len(self.param_vector), Float64)
        i = 0

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # Test if the diffusion parameters should be scaled.
                if self.relax.data.diff[self.run].scaling:
                    # tm.
                    self.scaling_matrix[i, i] = 1e-15

                # Increment i.
                i = i + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # Test if the diffusion parameters should be scaled.
                if self.relax.data.diff[self.run].scaling:
                    # tm, Diso, theta, phi
                    self.scaling_matrix[i, i] = 1e-15
                    self.scaling_matrix[i+1, i+1] = 1.0
                    self.scaling_matrix[i+2, i+2] = 1.0
                    self.scaling_matrix[i+3, i+3] = 1.0

                # Increment i.
                i = i + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # Test if the diffusion parameters should be scaled.
                if self.relax.data.diff[self.run].scaling:
                    # Dx, Dy, Dz, alpha, beta, gamma.
                    self.scaling_matrix[i, i] = 1e9
                    self.scaling_matrix[i+1, i+1] = 1e9
                    self.scaling_matrix[i+2, i+2] = 1e9
                    self.scaling_matrix[i+3, i+3] = 1.0
                    self.scaling_matrix[i+4, i+4] = 1.0
                    self.scaling_matrix[i+5, i+5] = 1.0

                # Increment i.
                i = i + 6

        # Model-free parameters.
        if self.param_set == 'mf' or self.param_set == 'all':
            # Loop over all residues.
            for j in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[j].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and j != index:
                    continue

                # Skip residues which should not be scaled.
                if not self.relax.data.res[j].scaling[self.run]:
                    i = i + len(self.relax.data.res[j].params[self.run])
                    continue

                # Loop over the model-free parameters.
                for k in xrange(len(self.relax.data.res[j].params[self.run])):
                    # tm.
                    if self.relax.data.res[j].params[self.run][k] == 'tm':
                        self.scaling_matrix[i, i] = 1e-15

                    # te, tf, and ts.
                    elif match('t', self.relax.data.res[j].params[self.run][k]):
                        self.scaling_matrix[i, i] = 1e-15

                    # Rex.
                    elif self.relax.data.res[j].params[self.run][k] == 'Rex':
                        self.scaling_matrix[i, i] = 1.0 / (2.0 * pi * self.relax.data.res[j].frq[self.run][0]) ** 2

                    # Bond length.
                    elif self.relax.data.res[j].params[self.run][k] == 'r':
                        self.scaling_matrix[i, i] = 1e-10

                    # CSA.
                    elif self.relax.data.res[j].params[self.run][k] == 'CSA':
                        self.scaling_matrix[i, i] = 1e-4

                    # Increment i.
                    i = i + 1

        # Debug.
        if Debug:
            print "Scaling matrix:\n" + `self.scaling_matrix`


    def calculate(self, run=None, i=None, params=None, scaling_matrix=None):
        """Calculation of the model-free chi-squared value."""

        # Set up the relaxation data and errors and the function options.
        relax_data = array(self.relax.data.res[i].relax_data[run], Float64)
        relax_error = array(self.relax.data.res[i].relax_error[run], Float64)

        # Initialise the functions used in the minimisation.
        self.mf = Mf(self.relax, run=run, i=i, equation=self.relax.data.res[i].equations[run], param_types=self.relax.data.res[i].params[run], init_params=params, relax_data=relax_data, errors=relax_error, bond_length=self.relax.data.res[i].r[run], csa=self.relax.data.res[i].csa[run], diff_type=self.relax.data.diff[run].type, diff_params=[self.relax.data.diff[run].tm], scaling_matrix=scaling_matrix)

        # Chi-squared calculation.
        self.relax.data.res[i].chi2[run] = self.mf.func(params, 0)


    def create(self, run=None, model=None, equation=None, params=None, scaling=1):
        """Function to create a model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

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
        self.model_setup(run, model, equation, params, scaling)


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        # Empty arrays.
        list_data = [ 'models',
                      'params' ]
        if name in list_data:
            return []

        # None.
        none_data = [ 'equations',
                      'scaling',
                      's2',
                      's2f',
                      's2s',
                      'tm',
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
            return None


    def data_names(self):
        """Function for returning a list of names of data structures associated with model-free.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        model: The model-free model name.

        equations:  The model-free equation type.

        params:  An array of the model-free parameter names associated with the model.

        scaling:  The scaling flag.

        s2:  S2.

        s2f:  S2f.

        s2s:  S2s.

        tm:  tm.

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

        names = [ 'models',
                  'equations',
                  'params',
                  'scaling',
                  's2',
                  's2f',
                  's2s',
                  'tm',
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

        return names


    def determine_param_set_type(self):
        """Determine the type of parameter set."""

        # Check if any model-free parameters are allowed to vary.
        mf_all_fixed = 1
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Test the fixed flag.
            if not hasattr(self.relax.data.res[i], 'fixed'):
                mf_all_fixed = 0
                break
            if not self.relax.data.res[i].fixed[self.run]:
                mf_all_fixed = 0
                break

        # Find the type.
        if mf_all_fixed and self.relax.data.diff[self.run].fixed:
            raise RelaxError, "All parameters are fixed."
        elif mf_all_fixed and not self.relax.data.diff[self.run].fixed:
            if self.print_flag:
                print "Only diffusion tensor parameters will be used."
            return 'diff'
        elif self.relax.data.diff[self.run].fixed:
            if self.print_flag:
                print "Only the model-free parameters for single residues will be used."
            return 'mf'
        else:
            if self.print_flag:
                print "The diffusion tensor parameters together with the model-free parameters for all residues will be used."
            return 'all'


    def fixed_setup(self, params=None, min_options=None):
        """The fixed parameter value setup function."""

        for i in xrange(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                min_options[i] = 0.5

            # {te, tf, ts}.
            elif match('t', params[i]):
                if params[i] == 'tf':
                    min_options[i] = 10.0 * 1e-12
                elif params[i] == 'ts':
                    min_options[i] = 1000.0 * 1e-12
                else:
                    min_options[i] = 100.0 * 1e-12

            # Rex.
            if params[i] == 'Rex':
                min_options[i] = 0.0

            # Bond length.
            if params[i] == 'r':
                min_options[i] = 1.02 * 1e-10

            # CSA.
            if params[i] == 'CSA':
                min_options[i] = -170 * 1e-6

        return min_options


    def grid_search(self, run, lower, upper, inc, constraints, print_flag):
        """The grid search setup function."""

        # Arguments.
        self.run = run
        self.lower = lower
        self.upper = upper
        self.inc = inc
        self.constraints = constraints
        self.print_flag = print_flag

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # The parameter set 'mf'.
        if self.param_set == 'mf':
            self.grid_search_mf_params()

        # The parameter set 'diff'.
        elif self.param_set == 'diff':
            self.grid_search_diff_params()

        # The parameter set 'all'.
        elif self.param_set == 'all':
            self.grid_search_all_params()


    def grid_search_mf_params(self):
        """Function for the grid search of model-free parameters for single residues."""

        # Test the validity of the arguments.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # The number of parameters.
            n = len(self.relax.data.res[i].params[self.run])

            # Make sure that the length of the parameter array is > 0.
            if n == 0:
                raise RelaxError, "Cannot run a grid search on a model with zero parameters."

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

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Setup the grid search options.
            if type(self.inc) == int:
                temp = []
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    temp.append(self.inc)
                self.inc = temp

            # Minimisation options.
            min_options = []
            for j in xrange(len(self.relax.data.res[i].params[self.run])):
                # {S2, S2f, S2s}.
                if match('S2', self.relax.data.res[i].params[self.run][j]):
                    min_options.append([self.inc[j], 0.0, 1.0])

                # {te, tf, ts}.
                elif match('t', self.relax.data.res[i].params[self.run][j]):
                    min_options.append([self.inc[j], 0.0, 5000.0 * 1e-12])

                # Rex.
                elif self.relax.data.res[i].params[self.run][j] == 'Rex':
                    min_options.append([self.inc[j], 0.0, 10.0 / (2.0 * pi * self.relax.data.res[i].frq[self.run][0])**2])

                # Bond length.
                elif self.relax.data.res[i].params[self.run][j] == 'r':
                    min_options.append([self.inc[j], 1.0 * 1e-10, 1.05 * 1e-10])

                # CSA.
                elif self.relax.data.res[i].params[self.run][j] == 'CSA':
                    min_options.append([self.inc[j], -120 * 1e-6, -200 * 1e-6])

            # Set the lower and upper bounds if these are supplied.
            if self.lower != None:
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    if self.lower[j] != None:
                        min_options[j][1] = self.lower[j]
            if self.upper != None:
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    if self.upper[j] != None:
                        min_options[j][2] = self.upper[j]

            # Create the initial parameter vector.
            self.assemble_param_vector(index=i)

            # Diagonal scaling.
            scaling_matrix = None
            if self.relax.data.res[i].scaling[self.run]:
                scaling_matrix = self.assemble_scaling_matrix(self.run, self.relax.data.res[i], i)
                self.param_vector = matrixmultiply(inverse(scaling_matrix), self.param_vector)
                for j in xrange(len(min_options)):
                    min_options[j][1] = min_options[j][1] / scaling_matrix[j, j]
                    min_options[j][2] = min_options[j][2] / scaling_matrix[j, j]

            # Minimisation.
            self.minimise(run=self.run, i=i, init_params=self.param_vector, scaling_matrix=scaling_matrix, min_algor='grid', min_options=min_options, constraints=self.constraints, print_flag=self.print_flag)


    def initialise_mf_data(self, data, run):
        """Function for the initialisation of model-free data structures.

        Only data structures which do not exist are created.
        """

        # Get the data names.
        data_names = self.data_names()

        # Loop over the names.
        for name in data_names:
            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                setattr(data, name, {})

            # Get the data.
            object = getattr(data, name)

            # Get the initial data structure.
            value = self.data_init(name)

            # If the data structure does not have the key 'run', add it.
            if not object.has_key(run):
                object[run] = value


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

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(self.param_vector)
        zero_array = zeros(n, Float64)
        i = 0
        j = 0

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # tm >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # tm >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Diso >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # 0 <= theta <= 2*pi.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-2.0 * pi / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

                # 0 <= phi <= 2*pi.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-2.0 * pi / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # Dx >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Dy >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Dz >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # 0 <= alpha <= 2*pi.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-2.0 * pi / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

                # 0 <= beta <= 2*pi.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-2.0 * pi / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

                # 0 <= gamma <= 2*pi.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                b.append(-2.0 * pi / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 2

        # Model-free parameters.
        if self.param_set == 'mf' or self.param_set == 'all':
            # Loop over all residues.
            for k in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[k].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and j != index:
                    continue

                # Save current value of i.
                old_i = i

                # Loop over the model-free parameters.
                for l in xrange(len(self.relax.data.res[k].params[self.run])):
                    # Order parameters {S2, S2f, S2s}.
                    if match('S2', self.relax.data.res[k].params[self.run][l]):
                        # 0 <= S2 <= 1.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        b.append(-1.0 / self.scaling_matrix[i, i])
                        j = j + 2

                        # S2 <= S2f and S2 <= S2s.
                        if self.relax.data.res[k].params[self.run][l] == 'S2':
                            for m in xrange(len(self.relax.data.res[k].params[self.run])):
                                if self.relax.data.res[k].params[self.run][m] == 'S2f' or self.relax.data.res[k].params[self.run][m] == 'S2s':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = -1.0
                                    A[j][old_i+m] = 1.0
                                    b.append(0.0 / self.scaling_matrix[i, i])
                                    j = j + 1

                    # Correlation times {tm, te, tf, ts}.
                    elif match('t', self.relax.data.res[k].params[self.run][l]):
                        # 0 <= te <= 10000 ps.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        b.append(-10e-9 / self.scaling_matrix[i, i])
                        j = j + 2

                        # tf <= ts.
                        if self.relax.data.res[k].params[self.run][l] == 'ts':
                            for m in xrange(len(self.relax.data.res[k].params[self.run])):
                                if self.relax.data.res[k].params[self.run][m] == 'tf':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = 1.0
                                    A[j][old_i+m] = -1.0
                                    b.append(0.0)
                                    j = j + 1

                    # Rex.
                    elif self.relax.data.res[k].params[self.run][l] == 'Rex':
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                    # Bond length.
                    elif match('r', self.relax.data.res[k].params[self.run][l]):
                        # 0.9e-10 <= r <= 2e-10.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.9e-10 / self.scaling_matrix[i, i])
                        b.append(-2e-10 / self.scaling_matrix[i, i])
                        j = j + 2

                    # CSA.
                    elif match('CSA', self.relax.data.res[k].params[self.run][l]):
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

        # Debug.
        if Debug:
            print "Linear constraints, A:\n" + `A`
            print "Linear constraints, b:\n" + `b`

        return A, b


    def map_bounds(self, index, params, run):
        """The function for creating bounds for the mapping function."""

        # Bounds array.
        bounds = zeros((len(params), 2), Float64)

        for i in xrange(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                bounds[i] = [0, 1]

            # {te, tf, ts}.
            elif match('t', params[i]):
                bounds[i] = [0, 1e-8]

            # Rex.
            elif params[i] == 'Rex':
                bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.res[index].frq[run][0])**2]

            # Bond length.
            elif params[i] == 'r':
                bounds[i] = [1.0 * 1e-10, 1.1 * 1e-10]

            # CSA.
            elif params[i] == 'CSA':
                bounds[i] = [-100 * 1e-6, -300 * 1e-6]

        return bounds


    def map_labels(self, run, index, params, bounds, swap, inc, scaling_matrix):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        labels = "{"
        tick_locations = []
        tick_values = []
        n = len(params)
        axis_incs = 5.0
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in xrange(n):
            # {S2, S2f, S2s}.
            if match('S2', params[swap[i]]):
                # Labels.
                labels = labels + "\"" + params[swap[i]] + "\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1.0
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1.0

            # {te, tf, and ts}.
            elif match('t', params[swap[i]]):
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ps)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e12
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e12

            # Rex.
            elif params[swap[i]] == 'Rex':
                # Labels.
                labels = labels + "\"Rex (" + self.relax.data.res[index].frq_labels[run][0] + " MHz)\""

                # Tick values.
                vals = bounds[swap[i], 0] * (2.0 * pi * self.relax.data.res[index].frq[run][0])**2
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * (2.0 * pi * self.relax.data.res[index].frq[run][0])**2

            # Bond length.
            elif params[swap[i]] == 'r':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (A)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-10
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-10

            # CSA.
            elif params[swap[i]] == 'CSA':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ppm)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-6
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-6

            if i < n - 1:
                labels = labels + " "
            else:
                labels = labels + "}"

            # Tick locations.
            string = "{"
            val = 0.0
            for j in xrange(axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc
            string = string + " }"
            tick_locations.append(string)

            # Tick values.
            string = "{"
            for j in xrange(axis_incs + 1):
                if self.relax.data.res[index].scaling.has_key(run):
                    string = string + "\"" + "%.2f" % (vals * scaling_matrix[swap[i], swap[i]]) + "\" "
                else:
                    string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            string = string + "}"
            tick_values.append(string)

        return labels, tick_locations, tick_values


    def minimise(self, run, min_algor, min_options, func_tol, grad_tol, max_iterations, constraints, print_flag):
        """Model-free minimisation.

        Three types of parameter sets exist for which minimisation is different.  These are:
            'mf' - Model-free parameters for single residues.
            'diff' - Diffusion tensor parameters.
            'all' - All model-free and all diffusion tensor parameters.

        """

        # Arguments.
        self.run = run
        self.min_algor = min_algor
        self.min_options = min_options
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.max_iterations = max_iterations
        self.constraints = constraints
        self.print_flag = print_flag

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # The parameter set 'mf'.
        if self.param_set == 'mf':
            self.minimise_mf_params()

        # The parameter set 'diff'.
        elif self.param_set == 'diff':
            self.minimise_diff_params()

        # The parameter set 'all'.
        elif self.param_set == 'all':
            self.minimise_all_params()


    def minimise_all_params(self):
        """Function for minimising all diffusion tensor and model-free parameters simultaneously."""

        # Create the initial parameter vector.
        self.assemble_param_vector()

        # Diagonal scaling.
        self.assemble_scaling_matrix()
        self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

        # Linear constraints.
        if self.constraints:
            A, b = self.linear_constraints()

        raise RelaxError, "Not coded yet."


    def minimise_diff_params(self):
        """Function for minimising just the diffusion tensor parameters."""

        # Create the initial parameter vector.
        self.assemble_param_vector()

        # Diagonal scaling.
        self.assemble_scaling_matrix()
        self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

        # Linear constraints.
        if self.constraints:
            A, b = self.linear_constraints()

        raise RelaxError, "Not coded yet."

    def minimise_mf_params(self):
        """Function for minimising model-free parameters for single residues."""

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Make sure that the length of the parameter array is > 0.
            if len(self.relax.data.res[i].params[self.run]) == 0:
                raise RelaxError, "Cannot minimise a model with zero parameters."

            # Create the initial parameter vector.
            self.assemble_param_vector(index=i)

            # Diagonal scaling.
            self.assemble_scaling_matrix(index=i)
            self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

            # Linear constraints.
            if self.constraints:
                A, b = self.linear_constraints(index=i)

            # Print out.
            if self.print_flag >= 1:
                if self.print_flag >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name
                string2 = ""
                for j in xrange(len(string)):
                    string2 = string2 + "~"
                print string
                print string2

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            self.iter_count = 0
            self.f_count = 0
            self.g_count = 0
            self.h_count = 0

            # Set up the relaxation data and errors and the function options.
            relax_data = array(self.relax.data.res[i].relax_data[self.run], Float64)
            relax_error = array(self.relax.data.res[i].relax_error[self.run], Float64)

            # Make sure that the errors are all positive numbers.
            for j in xrange(len(relax_error)):
                if relax_error[j] == 0.0:
                    message = "Zero error, minimisation not possible."
                    if self.print_flag >= 1:
                        print message + "  Skipping residue."
                    self.relax.data.res[i].warning[run] = message
                    return
                elif relax_error[j] < 0.0:
                    message = "Negative error."
                    if self.print_flag >= 1:
                        print message + "  Skipping residue."
                    self.relax.data.res[i].warning[run] = message
                    return

            # Initialise the function to minimise.
            ######################################

            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                vectors = None

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                vectors = None

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                vectors = None
                raise RelaxError, "Not coded yet."

            self.mf = Mf(self.relax, run=self.run, i=i, equation=self.relax.data.res[i].equations[self.run], param_types=self.relax.data.res[i].params[self.run], init_params=self.param_vector, relax_data=relax_data, errors=relax_error, bond_length=self.relax.data.res[i].r[self.run], csa=self.relax.data.res[i].csa[self.run], diff_type=self.relax.data.diff[self.run].type, diff_params=[self.relax.data.diff[self.run].tm], scaling_matrix=self.scaling_matrix)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor):
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                min_options = min_options + (self.mf.lm_dri, relax_error)


            # Minimisation.
            ###############

            if self.constraints:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
            if results == None:
                return
            self.params, self.func, iter, fc, gc, hc, self.warning = results
            self.iter_count = self.iter_count + iter
            self.f_count = self.f_count + fc
            self.g_count = self.g_count + gc
            self.h_count = self.h_count + hc

            # Scaling.
            if self.relax.data.res[i].scaling[self.run]:
                self.params = matrixmultiply(self.scaling_matrix, self.params)

            # Types.
            types = self.relax.data.res[i].params[self.run]

            # Loop over the minimised parameters.
            for j in xrange(len(self.params)):
                # S2.
                if types[j] == 'S2':
                    self.relax.data.res[i].s2[self.run] = self.params[j]

                # S2f.
                elif types[j] == 'S2f':
                    # S2f.
                    self.relax.data.res[i].s2f[self.run] = self.params[j]

                    # Other order parameters.
                    for k in xrange(len(types)):
                        # S2 = S2f.S2s
                        if types[k] == 'S2s':
                            self.relax.data.res[i].s2[self.run] = self.params[j] * self.params[k]

                        # S2s = S2/S2f
                        elif types[k] == 'S2':
                            if self.params[j] == 0.0:
                                self.relax.data.res[i].s2s[self.run] = 1e99
                            else:
                                self.relax.data.res[i].s2s[self.run] = self.params[k] / self.params[j]

                # S2s.
                elif types[j] == 'S2s':
                    self.relax.data.res[i].s2s[self.run] = self.params[j]

                # te.
                elif types[j] == 'te':
                    self.relax.data.res[i].te[self.run] = self.params[j]

                # tf.
                elif types[j] == 'tf':
                    self.relax.data.res[i].tf[self.run] = self.params[j]

                # ts.
                elif types[j] == 'ts':
                    self.relax.data.res[i].ts[self.run] = self.params[j]

                # Rex.
                elif types[j] == 'Rex':
                    self.relax.data.res[i].rex[self.run] = self.params[j]

                # Bond length.
                elif types[j] == 'r':
                    self.relax.data.res[i].r[self.run] = self.params[j]

                # CSA.
                elif types[j] == 'CSA':
                    self.relax.data.res[i].csa[self.run] = self.params[j]

            # Chi-squared statistic.
            self.relax.data.res[i].chi2[self.run] = self.func

            # Iterations.
            self.relax.data.res[i].iter[self.run] = self.iter_count

            # Function evaluations.
            self.relax.data.res[i].f_count[self.run] = self.f_count

            # Gradient evaluations.
            self.relax.data.res[i].g_count[self.run] = self.g_count

            # Hessian evaluations.
            self.relax.data.res[i].h_count[self.run] = self.h_count

            # Warning.
            self.relax.data.res[i].warning[self.run] = self.warning


    def model_setup(self, run, model, equation, params, scaling_flag):
        """Function for updating various data structures depending on the model selected."""

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Initialise the data structures (if needed).
            self.initialise_mf_data(self.relax.data.res[i], run)

            # Model-free models, equations, and parameter types.
            self.relax.data.res[i].models[run] = model
            self.relax.data.res[i].equations[run] = equation
            self.relax.data.res[i].params[run] = params

            # Diagonal scaling.
            self.relax.data.res[i].scaling[run] = scaling_flag


    def read_results(self, file_data, run):
        """Function for printing the core of the results file."""

        # Remove the header.
        file_data = file_data[1:]

        # Loop over the file data.
        for i in xrange(len(file_data)):
            # Residue number and name.
            try:
                num = int(file_data[i][0])
            except ValueError:
                print "Warning, the residue number " + file_data[i][0] + " is not an integer."
                continue
            name = file_data[i][1]

            # Find the residue index.
            index = None
            for j in xrange(len(self.relax.data.res)):
                if self.relax.data.res[j].num == num and self.relax.data.res[j].name == name:
                    index = j
                    break
            if index == None:
                print "Warning, residue " + `num` + " " + name + " cannot be found in the sequence."
                continue

            # Test if relaxation data has been loaded.
            if not hasattr(self.relax.data.res[index], 'relax_data'):
                print "Relaxation data has not been loaded.  This is required for the frequency data for Rex values."
                break

            # Model details.
            model = file_data[i][2]
            equation = file_data[i][3]

            # Paramters.
            params = eval(file_data[i][4])
            if type(params) != list:
                print "Warning, the parameters " + file_data[i][4] + " is not an array."
                continue

            # S2.
            try:
                s2 = float(file_data[i][5])
            except ValueError:
                s2 = None

            # S2f.
            try:
                s2f = float(file_data[i][6])
            except ValueError:
                s2f = None

            # S2s.
            try:
                s2s = float(file_data[i][7])
            except ValueError:
                s2s = None

            # tm.
            try:
                tm = float(file_data[i][8])
                tm = tm * 1e-12
            except ValueError:
                tm = None

            # tf.
            try:
                tf = float(file_data[i][9])
                tf = tf * 1e-12
            except ValueError:
                tf = None

            # te and ts.
            try:
                te = float(file_data[i][10])
                te = te * 1e-12
            except ValueError:
                te = None
            if "te" in params:
                ts = None
            else:
                ts = te
                te = None

            # Rex.
            try:
                rex = float(file_data[i][11])
                rex = rex / (2.0 * pi * self.relax.data.res[i].frq[run][0])**2
            except ValueError:
                rex = None

            # Bond length.
            try:
                r = float(file_data[i][12])
                r = r * 1e-10
            except ValueError:
                r = None

            # CSA.
            try:
                csa = float(file_data[i][13])
                csa = csa * 1e-6
            except ValueError:
                csa = None

            # Chi-squared.
            try:
                chi2 = float(file_data[i][14])
            except ValueError:
                chi2 = None

            # Number of iterations.
            try:
                iter = int(file_data[i][15])
            except ValueError:
                iter = None

            # Function count.
            try:
                f_count = int(file_data[i][16])
            except ValueError:
                f_count = None

            # Gradient count.
            try:
                g_count = int(file_data[i][17])
            except ValueError:
                g_count = None

            # Hessian count.
            try:
                h_count = int(file_data[i][18])
            except ValueError:
                h_count = None

            # Warning.
            if len(file_data[i]) > 19:
                warning = file_data[i][19]
                for j in xrange(20, len(file_data[i])):
                    warning = warning + " " + file_data[i][j]
            else:
                warning = None

            # Initialise the runs data structure.
            if not hasattr(self.relax.data.res[index], 'runs'):
                self.relax.data.res[index].runs = []

            # Initialise the data structures (if needed).
            self.initialise_mf_data(self.relax.data.res[index], run)

            # Place the data into 'self.relax.data'.
            self.relax.data.res[index].models[run] = model
            self.relax.data.res[index].equations[run] = equation
            self.relax.data.res[index].params[run] = params
            self.relax.data.res[index].s2[run] = s2
            self.relax.data.res[index].s2f[run] = s2f
            self.relax.data.res[index].s2s[run] = s2s
            self.relax.data.res[index].tm[run] = tm
            self.relax.data.res[index].tf[run] = tf
            self.relax.data.res[index].te[run] = te
            self.relax.data.res[index].ts[run] = ts
            self.relax.data.res[index].rex[run] = rex
            self.relax.data.res[index].r[run] = r
            self.relax.data.res[index].csa[run] = csa
            self.relax.data.res[index].chi2[run] = chi2
            self.relax.data.res[index].iter[run] = iter
            self.relax.data.res[index].f_count[run] = f_count
            self.relax.data.res[index].g_count[run] = g_count
            self.relax.data.res[index].h_count[run] = h_count
            self.relax.data.res[index].warning[run] = warning


    def select(self, run=None, model=None, scaling=1):
        """Function for the selection of a preset model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run


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
            params = ['tm']
        elif model == 'tm1':
            equation = 'mf_orig'
            params = ['tm', 'S2']
        elif model == 'tm2':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'te']
        elif model == 'tm3':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'Rex']
        elif model == 'tm4':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'te', 'Rex']
        elif model == 'tm5':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'S2', 'ts']
        elif model == 'tm6':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm7':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm8':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm9':
            equation = 'mf_orig'
            params = ['tm', 'Rex']

        # Block 2.
        elif model == 'tm10':
            equation = 'mf_orig'
            params = ['tm', 'CSA']
        elif model == 'tm11':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2']
        elif model == 'tm12':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'te']
        elif model == 'tm13':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'Rex']
        elif model == 'tm14':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm15':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm16':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm17':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm18':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm19':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'Rex']

        # Block 3.
        elif model == 'tm20':
            equation = 'mf_orig'
            params = ['tm', 'r']
        elif model == 'tm21':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2']
        elif model == 'tm22':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'te']
        elif model == 'tm23':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'Rex']
        elif model == 'tm24':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'te', 'Rex']
        elif model == 'tm25':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'S2', 'ts']
        elif model == 'tm26':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm27':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm28':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm29':
            equation = 'mf_orig'
            params = ['tm', 'r', 'Rex']

        # Block 4.
        elif model == 'tm30':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA']
        elif model == 'tm31':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2']
        elif model == 'tm32':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'te']
        elif model == 'tm33':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'Rex']
        elif model == 'tm34':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm35':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm36':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm37':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm38':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm39':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'Rex']

        # Invalid models.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(run, model, equation, params, scaling)


    def write_header(self, file, run):
        """Function for printing the header of the results file."""

        # Residue number and name.
        file.write("%-5s" % "Num")
        file.write("%-6s" % "Name")

        # Model details.
        file.write("%-6s" % "Model")
        file.write("%-10s" % "Equation")
        file.write("%-36s" % "Params")

        # Parameters.
        file.write("%-26s" % "S2")
        file.write("%-26s" % "S2f")
        file.write("%-26s" % "S2s")
        file.write("%-26s" % "tm_(ps)")
        file.write("%-26s" % "tf_(ps)")
        file.write("%-26s" % "te_or_ts_(ps)")
        file.write("%-26s" % ("Rex_(" + self.relax.data.res[0].frq_labels[run][0] + "_MHz)"))
        file.write("%-26s" % "Bond_length_(A)")
        file.write("%-26s" % "CSA_(ppm)")

        # Minimisation results.
        file.write("%-26s" % "Chi-squared")
        file.write("%-9s" % "Iter")
        file.write("%-9s" % "f")
        file.write("%-9s" % "g")
        file.write("%-9s" % "h")
        file.write("Warning")

        # End of line.
        file.write("\n")


    def write_results(self, file, run, i):
        """Function for printing the core of the results file."""

        # Reassign data structure.
        res = self.relax.data.res[i]

        # Residue number and name.
        file.write("%-5s" % res.num)
        file.write("%-6s" % res.name)

        # Test if the run exists.
        if not run in res.runs:
            file.write("\n")
            return

        # Model details.
        file.write("%-6s" % res.models[run])
        file.write("%-10s" % res.equations[run])
        file.write("%-36s" % replace(`res.params[run]`, ' ', ''))

        # S2.
        if res.s2[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.s2[run]`)

        # S2f.
        if res.s2f[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.s2f[run]`)

        # S2s.
        if res.s2s[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.s2s[run]`)

        # tm.
        if hasattr(res, 'tm') and res.tm.has_key(run) and res.tm[run] != None:
            file.write("%-26s" % `res.tm[run] / 1e-12`)
        else:
            file.write("%-26s" % `self.relax.data.diff[run].tm / 1e-12`)

        # tf.
        if res.tf[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.tf[run] / 1e-12`)

        # te or ts.
        if res.te[run] == None and res.ts[run] == None:
            file.write("%-26s" % "N/A")
        elif res.te[run] != None:
            file.write("%-26s" % `res.te[run] / 1e-12`)
        else:
            file.write("%-26s" % `res.ts[run] / 1e-12`)

        # Rex.
        if res.rex[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.rex[run] * (2.0 * pi * res.frq[run][0])**2`)

        # Bond length.
        if res.r[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.r[run] / 1e-10`)

        # CSA.
        if res.csa[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.csa[run] / 1e-6`)

        # Chi-squared.
        file.write("%-26s" % `res.chi2[run]`)

        # Iterations
        if res.iter[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.iter[run])

        # Function count.
        if res.f_count[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.f_count[run])

        # Gradient count.
        if res.g_count[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.g_count[run])

        # Hessian count.
        if res.h_count[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.h_count[run])

        # Warning
        if res.warning[run] != None:
            file.write(res.warning[run])

        # End of line.
        file.write("\n")
