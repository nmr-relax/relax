###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module for exponential curve-fitting."""

# Python module imports.
from math import exp


def exponential_2param_neg(rate=None, i0=None, x=None, y=None):
    """Calculate the data for a standard two parameter decreasing exponential.

    The y-values will be calculated based on the x-values.


    @keyword rate:  The exponential rate.
    @type rate:     float
    @keyword i0:    The initial intensity.
    @type i0:       float
    @keyword x:     The x-values at which to calculate the y-values.
    @type x:        numpy rank-1 float array
    @keyword y:     The data structure to store the y-values in.
    @type y:        numpy rank-1 float array
    """

    # Loop over the x-values.
    for i in range(len(x)):
        y[i] = i0 * exp(-rate*x[i])
