###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Auxiliary functions for optimisation."""


# relax module imports.
from lib.errors import RelaxLenError


def test_grid_ops(lower=None, upper=None, inc=None, n=None):
    """Test that the grid search options are reasonable.

    @param lower:   The lower bounds of the grid search which must be equal to the number of parameters in the model.
    @type lower:    array of numbers
    @param upper:   The upper bounds of the grid search which must be equal to the number of parameters in the model.
    @type upper:    array of numbers
    @param inc:     The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
    @type inc:      array of int
    @param n:       The number of parameters in the model.
    @type n:        int
    """

    # Lower bounds test.
    if lower != None:
        if len(lower) != n:
            raise RelaxLenError('lower bounds', n)

    # Upper bounds.
    if upper != None:
        if len(upper) != n:
            raise RelaxLenError('upper bounds', n)

    # Increment.
    if isinstance(inc, list):
        if len(inc) != n:
            raise RelaxLenError('increment', n)
