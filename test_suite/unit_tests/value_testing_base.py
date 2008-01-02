###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError



class Value_base_class:
    """Base class for the tests of both the 'prompt.value' and 'generic_fns.value' modules.

    This base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the value unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a model-free data pipe to the data store for testing model-free and diffusion parameters.
        relax_data_store.add(pipe_name='mf', pipe_type='mf')

        # Add a second model-free data pipe for copying tests.
        relax_data_store.add(pipe_name='mf2', pipe_type='mf')

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()
