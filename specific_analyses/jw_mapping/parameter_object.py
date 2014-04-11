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
"""The module for the reduced spectral density mapping parameter list object."""

# relax module imports.
from lib.physical_constants import N15_CSA
from specific_analyses.parameter_object import Param_list


class Jw_mapping_params(Param_list):
    """The reduced spectral density mapping parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # Execute the base class __init__ method.
        Param_list.__init__(self)

        # Add the base information for the analysis.
        self._add_csa(default=N15_CSA)

        # Add the model parameters.
        self._add('j0', scope='spin', string='J(0)', desc='Spectral density value at 0 MHz', py_type=float, set='params', grace_string='\\qJ(0)\\Q', err=True, sim=True)
        self._add('jwx', scope='spin', string='J(wX)', desc='Spectral density value at the frequency of the heteronucleus', py_type=float, set='params', grace_string='\\qJ(\\xw\\f{}\\sX\\N)\\Q', err=True, sim=True)
        self._add('jwh', scope='spin', string='J(wH)', desc='Spectral density value at the frequency of the proton', py_type=float, set='params', grace_string='\\qJ(\\xw\\f{}\\sH\\N)\\Q', err=True, sim=True)

        # Set up the user function documentation.
        self._set_uf_title("Reduced spectral density mapping parameters")
