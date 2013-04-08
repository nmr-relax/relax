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
"""Module for the plotting of data."""


# relax module imports.
from pipe_control import minimise
import specific_analyses


def determine_functions(category):
    """Determine the specific functions for the given data type.

    @param category:    The data category.
    @type category:     str
    @return:            The analysis specific return_value, return_conversion_factor, and get_type methods.
    @rtype:             tuple of methods or None
    """

    # Spin category.
    if category == 'spin':
        return None, None, None

    # A minimisation statistic.
    if minimise.return_data_name(category):
        return minimise.return_value, minimise.return_conversion_factor, None

    # Analysis specific value returning functions.
    else:
        return_value = specific_analyses.setup.get_specific_fn('return_value')
        return_conversion_factor = specific_analyses.setup.get_specific_fn('return_conversion_factor')
        data_type = specific_analyses.setup.get_specific_fn('data_type')
        return return_value, return_conversion_factor, data_type
