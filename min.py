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


    def calc(self, run=None):
        """Function for calculating the function value."""

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Equation type specific function setup.
            fns = self.relax.specific_setup.setup("calc", self.relax.data.res[i].equations[run])
            if fns == None:
                return
            self.create_param_vector, self.calculate = fns

            # Create the parameter vector.
            params = self.create_param_vector(run, self.relax.data.res[i])

            # Diagonal scaling.
            if self.relax.data.res[i].scaling.has_key(run):
                params = params / self.relax.data.res[i].scaling[run]

            # Minimisation.
            self.calculate(run=run, i=i, params=params)


    def fixed(self, run=None, values=None, print_flag=1):
        """Function for fixing the initial parameter values."""

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Equation type specific function setup.
            fns = self.relax.specific_setup.setup("fixed", self.relax.data.res[i].equations[run])
            if fns == None:
                return
            self.create_param_vector, self.fixed_setup, self.minimise = fns

            # Setup the fixed parameter options.
            if values:
                # User supplied values.
                min_options = array(values)
            else:
                # Fixed values.
                empty = zeros(len(self.relax.data.res[i].params[run]), Float64)
                min_options = self.fixed_setup(self.relax.data.res[i].params[run], min_options=empty)

            # Create the initial parameter vector.
            init_params = self.create_param_vector(run, self.relax.data.res[i])

            # Diagonal scaling.
            if self.relax.data.res[i].scaling.has_key(run):
                init_params = init_params / self.relax.data.res[i].scaling[run]
                min_options = min_options / self.relax.data.res[i].scaling[run]

            # Minimisation.
            self.minimise(run=run, i=i, init_params=init_params, min_algor="fixed", min_options=min_options, print_flag=print_flag)


    def grid_search(self, run=None, lower=None, upper=None, inc=None, constraints=0, print_flag=1):
        """The grid search function."""

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Equation type specific function setup.
            fns = self.relax.specific_setup.setup("grid_search", self.relax.data.res[i].equations[run])
            if fns == None:
                return
            self.create_param_vector, self.grid_setup, self.minimise = fns

            # Setup the grid search options.
            if type(inc) == int:
                temp = []
                for j in range(len(self.relax.data.res[i].params[run])):
                    temp.append(inc)
                inc = temp

            min_options = self.grid_setup(run=run, params=self.relax.data.res[i].params[run], index=i, inc_vector=inc)

            # Set the lower and upper bounds if these are supplied.
            if lower != None:
                for j in range(len(self.relax.data.res[i].params[run])):
                    if lower[j] != None:
                        min_options[j][1] = lower[j]
            if upper != None:
                for j in range(len(self.relax.data.res[i].params[run])):
                    if upper[j] != None:
                        min_options[j][2] = upper[j]

            # Create the initial parameter vector.
            init_params = self.create_param_vector(run, self.relax.data.res[i])

            # Diagonal scaling.
            if self.relax.data.res[i].scaling.has_key(run):
                init_params = init_params / self.relax.data.res[i].scaling[run]
                for j in range(len(min_options)):
                    min_options[j][1] = min_options[j][1] / self.relax.data.res[i].scaling[run][j]
                    min_options[j][2] = min_options[j][2] / self.relax.data.res[i].scaling[run][j]

            # Minimisation.
            self.minimise(run=run, i=i, init_params=init_params, min_algor='grid', min_options=min_options, constraints=constraints, print_flag=print_flag)


    def min(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, print_flag=1):
        """Minimisation function."""

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Equation type specific function setup.
            fns = self.relax.specific_setup.setup("minimise", self.relax.data.res[i].equations[run])
            if fns == None:
                return
            self.create_param_vector, self.minimise = fns

            # Create the initial parameter vector.
            init_params = self.create_param_vector(run, self.relax.data.res[i])

            # Diagonal scaling.
            if self.relax.data.res[i].scaling.has_key(run):
                init_params = init_params / self.relax.data.res[i].scaling[run]

            # Minimisation.
            self.minimise(run=run, i=i, init_params=init_params, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)
