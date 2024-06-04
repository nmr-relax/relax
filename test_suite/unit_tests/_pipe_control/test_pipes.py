###############################################################################
#                                                                             #
# Copyright (C) 2007-2008,2014 Edward d'Auvergne                              #
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
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control import pipes
from pipe_control.reset import reset
from lib.errors import RelaxError, RelaxNoPipeError, RelaxPipeError
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_pipes(UnitTestCase):
    """Unit tests for the functions of the 'pipe_control.pipes' module."""

    def setUp(self):
        """Set up for all the data pipe unit tests."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Add a single object to the 'orig' data pipe.
        ds['orig'].x = 1

        # Add a single object to the single spin system of the 'orig' data pipe.
        ds['orig'].mol[0].res[0].spin[0].num = 1

        # Add an empty data pipe (for the 'eliminate_unused_pipes' test).
        ds.add(pipe_name='empty', pipe_type='mf')

        # Set the current pipe to the 'orig' data pipe.
        pipes.switch('orig')


    def test_copy(self):
        """Test the copying of a data pipe.

        The function tested is pipe_control.pipes.copy().
        """

        # Copy the 'orig' data pipe to the 'new' data pipe.
        pipes.copy('orig', 'new')

        # Test that the new data pipe exists.
        self.assertTrue('new' in ds)

        # Test that the new data pipe has the object 'x' and that its value is 1.
        self.assertEqual(ds['new'].x, 1)

        # Change the value of x.
        ds['new'].x = 2

        # Test that the two values are different.
        self.assertTrue(ds['orig'].x != ds['new'].x)

        # Test that the new data pipe has the object 'mol[0].res[0].spin[0].num' and that its value is 1.
        self.assertEqual(ds['new'].mol[0].res[0].spin[0].num, 1)

        # Change the spin system number.
        ds['new'].mol[0].res[0].spin[0].num = 2

        # Test that the original spin system number hasn't changed.
        self.assertEqual(ds['orig'].mol[0].res[0].spin[0].num, 1)


    def test_copy_current(self):
        """Test the copying of current data pipe.

        The function tested is pipe_control.pipes.copy().
        """

        # Copy the 'orig' data pipe to the 'new' data pipe.
        pipes.copy(pipe_to='new')

        # Test that the new data pipe exists.
        self.assertTrue('new' in ds)

        # Test that the new data pipe has the object 'x' and that its value is 1.
        self.assertEqual(ds['new'].x, 1)

        # Change the value of x.
        ds['new'].x = 2

        # Test that the two values are different.
        self.assertTrue(ds['orig'].x != ds['new'].x)

        # Test that the new data pipe has the object 'mol[0].res[0].spin[0].num' and that its value is 1.
        self.assertEqual(ds['new'].mol[0].res[0].spin[0].num, 1)

        # Change the spin system number.
        ds['new'].mol[0].res[0].spin[0].num = 2

        # Test that the original spin system number hasn't changed.
        self.assertEqual(ds['orig'].mol[0].res[0].spin[0].num, 1)


    def test_copy_fail(self):
        """Test the failure of the copying of data pipes when the data pipe to copy to already exists.

        The function tested is pipe_control.pipes.copy()
        """

        # Assert that a RelaxPipeError occurs when the data pipe to copy data to already exists.
        self.assertRaises(RelaxPipeError, pipes.copy, 'orig', 'empty')


    def test_creation(self):
        """Test the creation of a data pipe.

        The function used is pipe_control.pipes.create().
        """

        # Create a new model-free data pipe.
        name = 'new'
        pipes.create(name, 'mf')

        # Test that the data pipe exists.
        self.assertTrue(name in ds)

        # Test that the current pipe is the new pipe.
        self.assertEqual(pipes.cdp_name(), name)


    def test_creation_fail(self):
        """Test the failure of the creation of a data pipe (by supplying an incorrect pipe type).

        The function used is pipe_control.pipes.create().
        """

        # Assert that a RelaxError occurs when the pipe type is invalid.
        self.assertRaises(RelaxError, pipes.create, 'new', 'x')


    def test_current(self):
        """Get the current data pipe.

        The function used is pipe_control.pipes.cdp_name().
        """

        # Test the current pipe.
        self.assertEqual(pipes.cdp_name(), 'orig')


    def test_deletion(self):
        """Test the deletion of a data pipe.

        The function tested is pipe_control.pipes.delete()
        """

        # Set the current pipe to the 'orig' data pipe.
        name = 'orig'
        pipes.switch(name)

        # Delete the 'orig' data pipe.
        pipes.delete(name)

        # Test that the data pipe no longer exists.
        self.assertTrue(name not in ds)

        # Test that the current pipe is None (as the current pipe was deleted).
        self.assertEqual(pipes.cdp_name(), None)


    def test_deletion_fail(self):
        """Test the failure of the deletion of a data pipe (by suppling a non-existant data pipe).

        The function tested is pipe_control.pipes.delete()
        """

        # Assert that a RelaxNoPipeError occurs when the data pipe does not exist.
        self.assertRaises(RelaxNoPipeError, pipes.delete, 'x')


    def test_switch(self):
        """Test the switching of the current data pipe.

        The function tested is pipe_control.pipes.switch().
        """

        # Switch to the 'orig' data pipe.
        pipes.switch('orig')

        # Test the current data pipe.
        self.assertEqual(pipes.cdp_name(), 'orig')

        # Switch to the 'empty' data pipe.
        pipes.switch('empty')

        # Test the current data pipe.
        self.assertEqual(pipes.cdp_name(), 'empty')


    def test_switch_fail(self):
        """Test the failure of switching to a non-existant data pipe.

        The function used is pipe_control.pipes.switch().
        """

        # Assert that a RelaxNoPipeError occurs when the pipe type is invalid.
        self.assertRaises(RelaxNoPipeError, pipes.switch, 'x')


    def test_test(self):
        """The throwing of RelaxNoPipeError when the pipe does not exist.

        The function tested is pipe_control.pipes.check_pipe().
        """

        # The following should do nothing as the pipes exist.
        pipes.check_pipe()
        pipes.check_pipe('orig')
        pipes.check_pipe('empty')

        # Assert that a RelaxNoPipeError occurs when the pipe doesn't exist.
        self.assertRaises(RelaxNoPipeError, pipes.check_pipe, 'x')

        # Reset relax.
        reset()

        # Now none of the following pipes exist, hence errors should be thrown.
        self.assertRaises(RelaxNoPipeError, pipes.check_pipe)
        self.assertRaises(RelaxNoPipeError, pipes.check_pipe, 'orig')
        self.assertRaises(RelaxNoPipeError, pipes.check_pipe, 'empty')
