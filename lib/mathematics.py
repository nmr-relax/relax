###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Module for basic mathematical operations."""

# Python module imports.
from math import ceil, log10


def order_of_magnitude(value):
    """Determine the order of magnitude of the given number.

    For example, the number 1,234 will be give a value of 4.0.


    @param value:   The value to determine the order of magnitude of.
    @type value:    float or int
    @return:        The order of magnitude.
    @rtype:         float
    """

    # Calculate and return the value.
    return ceil(log10(value))


def round_to_next_order(value):
    """Round the given value up to the next order of magnitude.

    For example, the number 1,234 will be rounded up to 10,000.

    
    @param value:   The value to determine the order of magnitude of.
    @type value:    float or int
    @return:        The new value rounded up to the next order of magnitude.
    @rtype:         float
    """
    
    # Calculate and return the value.
    return 10**(order_of_magnitude(value))
