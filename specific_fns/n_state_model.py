###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
from re import search

# relax module imports.
from data import Data as relax_data_store
from specific_fns.base_class import Common_functions


class N_state_model(Common_functions):
    def __init__(self):
        """Class containing functions for the N-state model."""


    def grid_search(self, lower, upper, inc, constraints, print_flag, sim_index=None):
        """The grid search function.

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
        @param constraints: If true, constraints are applied during the grid search (elinating parts
                            of the grid).  If false, no constraints are used.
        @type constraints:  bool
        @param print_flag:  A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type print_flag:   int
        """

        # Arguments.
        self.lower = lower
        self.upper = upper
        self.inc = inc

        # Minimisation.
        self.minimise(min_algor='grid', constraints=constraints, print_flag=print_flag, sim_index=sim_index)


    def overfit_deselect(self):
        """Dummy function nornally for deselecting spins with insufficient data for minimisation."""


    def return_data_name(self, name):
        """
        N-state model data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Bond length            | 'r'          | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |                        |              |                                                  |
        | CSA                    | 'csa'        | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|

        """

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'
