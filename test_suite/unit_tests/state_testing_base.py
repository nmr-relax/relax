###############################################################################
#                                                                             #
# Copyright (C) 2007-2010 Edward d'Auvergne                                   #
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
from os import sep, tmpfile

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from status import Status; status = Status()


class State_base_class:
    """Base class for the tests of both the 'prompt.state' and 'generic_fns.state' modules.

    This base class also contains shared unit tests.
    """


    def setUp(self):
        """Set up for all the data pipe unit tests."""

        # Reset the relax data storage object.
        ds.__reset__()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the temporary file descriptor.
        try:
            del self.tmp_file
        except AttributeError:
            pass

        # Reset the relax data store.
        ds.__reset__()


    def test_load(self):
        """The unpickling and restoration of the relax data storage singleton.

        This tests the normal operation of the generic_fns.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assert_(not hasattr(ds, 'y'))

        # Load the state.
        self.state.load_state(state='basic_single_pipe', dir=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'saved_states')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test the contents of the restored singleton.
        self.assertEqual(list(ds.keys()), ['orig'])
        self.assertEqual(pipes.cdp_name(), 'orig')
        self.assertEqual(dp.x, 1)
        self.assertEqual(ds.y, 'Hello')


    def test_load_and_modify(self):
        """The modification of an unpickled and restored relax data storage singleton.

        This tests the normal operation of the generic_fns.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assert_(not hasattr(ds, 'y'))

        # Load the state.
        self.state.load_state(state='basic_single_pipe', dir=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'saved_states')

        # Add a new data pipe and some data to it.
        ds.add('new', 'jw_mapping')
        cdp.z = [None, None]

        # Get the data pipes.
        dp_orig = pipes.get_pipe('orig')
        dp_new = pipes.get_pipe('new')

        # Test the contents of the restored singleton (with subsequent data added).
        self.assertEqual(list(ds.keys()).sort(), ['orig', 'new'].sort())
        self.assertEqual(pipes.cdp_name(), 'new')
        self.assertEqual(dp_orig.x, 1)
        self.assertEqual(ds.y, 'Hello')
        self.assertEqual(dp_new.z, [None, None])


    def test_load_and_reset(self):
        """The resetting of an unpickled and restored relax data storage singleton.

        This tests the normal operation of the generic_fns.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assert_(not hasattr(ds, 'y'))

        # Load the state.
        self.state.load_state(state='basic_single_pipe', dir=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'saved_states')

        # Reset.
        ds.__reset__()

        # Test that there are no contents in the reset singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assert_(not hasattr(ds, 'y'))


    def test_save(self):
        """The pickling and saving of the relax data storage singleton.

        This tests the normal operation of the generic_fns.state.save() function.
        """

        # Create a temporary file descriptor.
        self.tmp_file = tmpfile()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Add a single object to the 'orig' data pipe.
        dp.x = 1

        # Add a single object to the storage object.
        ds.y = 'Hello'

        # Save the state.
        self.state.save_state(state=self.tmp_file)
