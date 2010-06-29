###############################################################################
#                                                                             #
# Copyright (C) 2007-2009 Edward d'Auvergne                                   #
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

# Module docstring.
"""The model-free specific code."""


# The available modules.
__all__ = [ 'main',
            'mf_minimise',
            'molmol',
            'results']

# relax module imports.
from main import Model_free_main
from mf_minimise import Mf_minimise
from molmol import Molmol
from results import Results
from specific_fns.api_base import API_base
from specific_fns.api_common import API_common


class Model_free(Model_free_main, Mf_minimise, Molmol, Results, API_base, API_common):
    """Parent class containing all the model-free specific functions."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.return_error = self._return_error_relax_data
        self.return_value = self._return_value_general
        self.test_grid_ops = self._test_grid_ops_general
