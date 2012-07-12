###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from test_suite.unit_tests.base_classes import UnitTestCase


class Minimisation_base_class(UnitTestCase):
    """Base class for the tests of the minimisation modules.
    
    This includes both the 'prompt.minimisation' and 'generic_fns.minimise' modules.  The base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the minimisation unit tests."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')
