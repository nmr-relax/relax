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


    def calc(self, run=None, print_flag=1):
        """Function for calculating the function value."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific calculate function setup.
        calculate = self.relax.specific_setup.setup('calc', function_type)
        if calculate == None:
            raise RelaxFuncSetupError, ('calculate', function_type)

        # Minimisation.
        calculate(run=run, print_flag=print_flag)


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

        # Specific grid search function.
        grid_search = self.relax.specific_setup.setup('grid_search', function_type)
        if grid_search == None:
            raise RelaxFuncSetupError, ('grid search', function_type)

        # Grid search.
        grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


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

        # Specific minimisation function.
        minimise = self.relax.specific_setup.setup('minimise', function_type)
        if minimise == None:
            raise RelaxFuncSetupError, ('minimise', function_type)

        # Minimisation.
        minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)


    def set(self, run=None, values=None, print_flag=1):
        """Function for setting the initial parameter values."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific set function.
        set = self.relax.specific_setup.setup('set', function_type)
        if set == None:
            raise RelaxFuncSetupError, ('set', function_type)

        # Minimisation.
        set(run=run, values=values, print_flag=print_flag)


