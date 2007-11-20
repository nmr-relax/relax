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
from os import remove
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from generic_fns.state import load_state, save_state



class Test_state(TestCase):
    """Unit tests for the functions of the 'generic_fns.state' module."""

    def setUp(self):
        """Set up for all the data pipe unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a single object to the 'orig' data pipe.
        relax_data_store['orig'].x = 1


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data store.
        relax_data_store.__reset__()

        # Clean up the temporarily created dump files.
        try:
            remove('test.bz2')
        except OSError:
            pass


    def test_load(self):
        """The unpickling and restoration of the relax data storage singleton.

        This tests the normal operation of the generic_fns.state.load() function.
        """

        # Save the state.
        save_state('test')

        # Reset the relax data store.
        relax_data_store.__reset__()

        # Test the contents of the empty singleton.
        self.assertEqual(relax_data_store.keys(), [])
        self.assertEqual(relax_data_store.current_pipe, None)

        # Load the state.
        load_state('test')

        # Test the contents of the restored singleton.
        self.assertEqual(relax_data_store.keys(), ['orig'])
        self.assertEqual(relax_data_store.current_pipe, 'orig')
        self.assertEqual(relax_data_store['orig'].x, 1)


    def test_save(self):
        """The pickling and saving of the relax data storage singleton.

        This tests the normal operation of the generic_fns.state.save() function.
        """

        # Save the state.
        save_state('test')
