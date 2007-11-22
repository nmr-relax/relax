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

# Python module imports.
from os import remove, tmpfile

# relax module imports.
from data import Data as relax_data_store



class State_base_class:
    """Base class for the tests of both the 'prompt.state' and 'generic_fns.state' modules.

    This base class also contains shared unit tests.
    """


    def setUp(self):
        """Set up for all the data pipe unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the temporary file descriptor.
        try:
            del self.tmp_file
        except AttributeError:
            pass

        # Reset the relax data store.
        relax_data_store.__reset__()


    def test_load(self):
        """The unpickling and restoration of the relax data storage singleton.

        This tests the normal operation of the generic_fns.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(relax_data_store.keys(), [])
        self.assertEqual(relax_data_store.current_pipe, None)
        self.assert_(not hasattr(relax_data_store, 'y'))

        # Load the state.
        self.state.load_state(state='basic_single_pipe', dir_name='../shared_data/saved_states')

        # Test the contents of the restored singleton.
        self.assertEqual(relax_data_store.keys(), ['orig'])
        self.assertEqual(relax_data_store.current_pipe, 'orig')
        self.assertEqual(relax_data_store['orig'].x, 1)
        self.assertEqual(relax_data_store.y, 'Hello')


    def test_save(self):
        """The pickling and saving of the relax data storage singleton.

        This tests the normal operation of the generic_fns.state.save() function.
        """

        # Create a temporary file descriptor.
        self.tmp_file = tmpfile()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a single object to the 'orig' data pipe.
        relax_data_store['orig'].x = 1

        # Add a single object to the storage object.
        relax_data_store.y = 'Hello'

        # Save the state.
        self.state.save_state(state=self.tmp_file)
