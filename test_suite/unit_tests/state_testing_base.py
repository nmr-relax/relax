###############################################################################
#                                                                             #
# Copyright (C) 2007-2008,2011 Edward d'Auvergne                              #
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

# Python module imports.
from os import sep
from tempfile import mkstemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control import pipes
from pipe_control.reset import reset
from status import Status; status = Status()
from test_suite.unit_tests.base_classes import UnitTestCase


class State_base_class(UnitTestCase):
    """Base class for the tests of both the 'prompt.state' and 'pipe_control.state' modules.

    This base class also contains shared unit tests.
    """

    def test_load(self):
        """The unpickling and restoration of the relax data storage singleton.

        This tests the normal operation of the pipe_control.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assertTrue(not hasattr(ds, 'y'))

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

        This tests the normal operation of the pipe_control.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assertTrue(not hasattr(ds, 'y'))

        # Load the state.
        self.state.load_state(state='basic_single_pipe', dir=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'saved_states')

        # Add a new data pipe and some data to it.
        ds.add('new', 'jw_mapping')
        cdp.z = [None, None]

        # Get the data pipes.
        dp_orig = pipes.get_pipe('orig')
        dp_new = pipes.get_pipe('new')

        # Test the contents of the restored singleton (with subsequent data added).
        self.assertTrue('orig' in ds)
        self.assertTrue('new' in ds)
        self.assertEqual(pipes.cdp_name(), 'new')
        self.assertEqual(dp_orig.x, 1)
        self.assertEqual(ds.y, 'Hello')
        self.assertEqual(dp_new.z, [None, None])


    def test_load_and_reset(self):
        """The resetting of an unpickled and restored relax data storage singleton.

        This tests the normal operation of the pipe_control.state.load() function.
        """

        # Test the contents of the empty singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assertTrue(not hasattr(ds, 'y'))

        # Load the state.
        self.state.load_state(state='basic_single_pipe', dir=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'saved_states')

        # Reset relax.
        reset()

        # Test that there are no contents in the reset singleton.
        self.assertEqual(list(ds.keys()), [])
        self.assertEqual(pipes.cdp_name(), None)
        self.assertTrue(not hasattr(ds, 'y'))


    def test_save(self):
        """The pickling and saving of the relax data storage singleton.

        This tests the normal operation of the pipe_control.state.save() function.
        """

        # Create a temporary file descriptor.
        ds.tmpfile_handle, ds.tmpfile = mkstemp(suffix='.bz2')

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Add a single object to the 'orig' data pipe.
        dp.x = 1

        # Add a single object to the storage object.
        ds.y = 'Hello'

        # Save the state.
        self.state.save_state(state=ds.tmpfile, force=True)
