###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from generic_fns import sequence
from relax_errors import RelaxError
import sys


class Relax_data_base_class:
    """Base class for the tests of the relaxation data tensor modules.

    This includes both the 'prompt.relax_data' and 'generic_fns.relax_data' modules.
    The base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the relaxation data unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_read(self):
        """Test the reading of relaxation data.

        The functions tested are both specific_fns.relax_data.read() and prompt.relax_data.read().
        """

        # Get the relative path of relax.
        path = sys.path[0]
        if path == '.':
            path = sys.path[-1]

        # First read the residue sequence out of the Ap4Aase 600 MHz NOE data file.
        sequence.read(file='Ap4Aase.Noe.600.bz2', dir=path+'/test_suite/shared_data/relaxation_data')

        # Then read the data out of the same file.
        self.relax_data_fns.read(ri_label='NOE', frq_label='600', frq=600e6, file='Ap4Aase.Noe.600.bz2', dir=path+'/test_suite/shared_data/relaxation_data')
