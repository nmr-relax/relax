###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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
"""Analysis specific code for the steady-state heteronuclear NOE calculation."""


# The available modules.
__all__ = [ 'main',
            'pymol']

# relax module imports.
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.noe.main import Noe_main


class Noe(Noe_main, API_base, API_common):
    """Parent class containing all the NOE specific functions."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Noe, self).__init__()

        # Place methods into the API.
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self._return_value_general

        # Set up the spin parameters.
        self.PARAMS.add('ref', scope='spin', desc='The reference peak intensity', py_type=float, grace_string='Reference intensity')
        self.PARAMS.add('sat', scope='spin', desc='The saturated peak intensity', py_type=float, grace_string='Saturated intensity')
        self.PARAMS.add('noe', scope='spin', desc='The NOE', py_type=float, grace_string='\\qNOE\\Q', err=True, sim=True)
