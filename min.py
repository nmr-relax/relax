###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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
from Numeric import Float64, array, zeros
from re import match


class Minimise:
    def __init__(self, relax):
        """Class containing the fixed, grid_search, and minimise functions."""

        self.relax = relax


    def fixed(self, model=None, values=None, print_flag=1):
        """Function for fixing the initial parameter values."""

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("fixed", model)
        if fns == None:
            return
        self.fixed_setup, self.main_loop = fns

        # Setup the fixed parameter options.
        if values:
            # User supplied values.
            min_options = array(values)
        else:
            # Fixed values.
            empty = zeros(len(self.relax.data.param_types[model]), Float64)
            min_options = self.fixed_setup(min_options=empty, model=model)

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(model):
            min_options = min_options / self.relax.data.scaling[model][0]

        # Main iterative loop.
        self.main_loop(model=model, min_algor="fixed", min_options=min_options, print_flag=print_flag)


    def grid_search(self, model=None, lower=None, upper=None, inc=[], constraints=0, print_flag=1):
        """The grid search function."""

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("grid_search", model)
        if fns == None:
            return
        self.grid_setup, self.main_loop = fns

        # Setup the grid search options.
        min_options = self.grid_setup(model=model, inc_vector=inc)

        # Set the lower and upper bounds if these are supplied.
        for i in range(len(self.relax.data.param_types[model])):
            if lower[i] != None:
                min_options[i][1] = lower[i]
            if upper[i] != None:
                min_options[i][2] = upper[i]

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(model):
            for i in range(len(min_options)):
                min_options[i][1] = min_options[i][1] / self.relax.data.scaling[model][0][i]
                min_options[i][2] = min_options[i][2] / self.relax.data.scaling[model][0][i]

        # Main iterative loop.
        self.main_loop(model=model, min_algor='grid', min_options=min_options, constraints=constraints, print_flag=print_flag)


    def minimise(self, model=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, print_flag=1):
        """Minimisation function."""

        # Equation type specific function setup.
        self.main_loop = self.relax.specific_setup.setup("minimise", model)
        if self.main_loop == None:
            return

        # Main iterative loop.
        self.main_loop(model=model, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)
