###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Functions for calculating various optimisation potentials."""


def quad_pot(values, pot, lower, upper):
    """Calculate the flat-bottom quadratic energy potential.

    The formula used is::

                            / (x - x+)^2    if x > x+,
                            |                         
        V_pQuad(x;x+,x-) = <  (x - x-)^2    if x < x-,
                            |                         
                            \ 0             otherwise.

    Where x+ and x- are the absolute bounds.


    @param values:  An array of values of x.
    @type values:   numpy float array
    @param pot:     The array to place the potential values (V_pQuad) into.  This should have the
                    same dimensions as the values array.
    @type pot:      numpy float array
    @param lower:   The array of lower bounds.  This should have the same dimensions as the values
                    array.
    @type lower:    numpy float array
    @param upper:   The array of upper bounds.  This should have the same dimensions as the values
                    array.
    @type upper:    numpy float array
    """

    # Loop over the x values.
    for i in xrange(len(values)):
        # First condition.
        if values[i] > upper[i]:
            pot[i] = (values[i] - upper[i])**2

        # Second contition.
        elif values[i] < lower[i]:
            pot[i] = (values[i] - lower[i])**2

        # Otherwise clear the array element.
        else:
            pot[i] = 0.0
