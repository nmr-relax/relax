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


def determine_functions(data_name=None):
    """Determine the specific functions for the given data type.

    @keyword data_name: The name of the data or variable to plot.
    @type data_name:    str
    @return:            The analysis specific return_value, return_conversion_factor, and data_type methods.
    @rtype:             tuple of methods or None
    """

    # Spin data.
    if data_name in ['res_num', 'spin_num']:
        return None, None, None

    # A minimisation statistic.
    if minimise.return_data_name(data_name):
        return minimise.return_value, minimise.return_conversion_factor, None

    # Analysis specific value returning functions.
    else:
        return_value = specific_analyses.setup.get_specific_fn('return_value')
        return_conversion_factor = specific_analyses.setup.get_specific_fn('return_conversion_factor')
        data_type = specific_analyses.setup.get_specific_fn('data_type')
        return return_value, return_conversion_factor, data_type
