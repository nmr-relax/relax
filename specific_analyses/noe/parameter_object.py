###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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
"""The module for the steady-state heteronuclear NOE parameter list object."""

# relax module imports.
from specific_analyses.parameter_object import Param_list


class Noe_params(Param_list):
    """The steady-state heteronuclear NOE parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # The object is already initialised.
        if self._initialised: return

        # Execute the base class __init__ method.
        Param_list.__init__(self)

        # Add the base data.
        self._add_peak_intensity()

        # Add the single model parameter.
        self._add('noe', scope='spin', desc='The steady-state NOE value', py_type=float, set='params', grace_string='\\qNOE\\Q', err=True, sim=True)

        # Set up the user function documentation.
        self._set_uf_title("Steady-state NOE parameters")
        self._uf_param_table(label="table: NOE parameters", caption="Steady-state NOE parameters.")
