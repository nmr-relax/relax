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


from math import pi
from LinearAlgebra import inverse
from Numeric import Float64, array, matrixmultiply, zeros
from re import match


class Minimise:
    def __init__(self, relax):
        """Class containing the calc, grid_search, minimise, and set functions."""

        self.relax = relax


    def calc(self, run=None):
        """Function for calculating the function value."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific parameter vector function setup.
        self.assemble_param_vector = self.relax.specific_setup.setup('param_vector', function_type)
        if self.assemble_param_vector == None:
            raise RelaxFuncSetupError, ('parameter vector', function_type)

        # Equation type specific scaling matrix function setup.
        self.assemble_scaling_matrix = self.relax.specific_setup.setup('scaling_matrix', function_type)
        if self.assemble_scaling_matrix == None:
            raise RelaxFuncSetupError, ('scaling matrix', function_type)

        # Equation type specific calculate function setup.
        self.calculate = self.relax.specific_setup.setup('calc', function_type)
        if self.calculate == None:
            raise RelaxFuncSetupError, ('calculate', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Create the parameter vector.
            params = self.assemble_param_vector(run, self.relax.data.res[i])

            # Diagonal scaling.
            scaling_matrix = None
            if self.relax.data.res[i].scaling[run]:
                scaling_matrix = self.assemble_scaling_matrix(run, self.relax.data.res[i], i)
                params = matrixmultiply(inverse(scaling_matrix), params)

            # Minimisation.
            self.calculate(run=run, i=i, params=params, scaling_matrix=scaling_matrix)


    def grid_search(self, run=None, lower=None, upper=None, inc=None, constraints=1, print_flag=1):
        """The grid search function."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific grid setup function setup.
        self.grid_search = self.relax.specific_setup.setup('grid_search', function_type)
        if self.grid_search == None:
            raise RelaxFuncSetupError, ('grid search', function_type)

        # Grid search.
        self.grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, print_flag=1):
        """Minimisation function."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific minimise function setup.
        self.minimise = self.relax.specific_setup.setup('minimise', function_type)
        if self.minimise == None:
            raise RelaxFuncSetupError, ('minimise', function_type)

        # Minimisation.
        self.minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)


    def set(self, run=None, values=None, print_flag=1):
        """Function for setting the initial parameter values."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test the validity of the arguments.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # The number of parameters.
            n = len(self.relax.data.res[i].params[run])

            # Make sure that the length of the parameter array is > 0.
            if n == 0:
                raise RelaxError, "Cannot set parameter values for a model with zero parameters."

            # Values.
            if values != None:
                if len(values) != n:
                    raise RelaxLenError, ('values', n)

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific parameter vector function setup.
        self.assemble_param_vector = self.relax.specific_setup.setup('param_vector', function_type)
        if self.assemble_param_vector == None:
            raise RelaxFuncSetupError, ('parameter vector', function_type)

        # Equation type specific scaling matrix function setup.
        self.assemble_scaling_matrix = self.relax.specific_setup.setup('scaling_matrix', function_type)
        if self.assemble_scaling_matrix == None:
            raise RelaxFuncSetupError, ('scaling matrix', function_type)

        # Equation type specific set setup function setup.
        self.fixed_setup = self.relax.specific_setup.setup('fixed', function_type)
        if self.fixed_setup == None:
            raise RelaxFuncSetupError, ('fixed setup', function_type)

        # Equation type specific minimise function setup.
        self.minimise = self.relax.specific_setup.setup('minimise', function_type)
        if self.minimise == None:
            raise RelaxFuncSetupError, ('minimise', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Setup the fixed parameter options.
            if values:
                # User supplied values.
                min_options = array(values)
            else:
                # Fixed values.
                empty = zeros(len(self.relax.data.res[i].params[run]), Float64)
                min_options = self.fixed_setup(self.relax.data.res[i].params[run], min_options=empty)

            # Create the initial parameter vector.
            init_params = self.assemble_param_vector(run, self.relax.data.res[i])

            # Diagonal scaling.
            scaling_matrix = None
            if self.relax.data.res[i].scaling[run]:
                scaling_matrix = self.assemble_scaling_matrix(run, self.relax.data.res[i], i)
                init_params = matrixmultiply(inverse(scaling_matrix), init_params)
                min_options = matrixmultiply(inverse(scaling_matrix), min_options)

            # Minimisation.
            self.minimise(run=run, i=i, init_params=init_params, scaling_matrix=scaling_matrix, min_algor="fixed", min_options=min_options, print_flag=print_flag)


