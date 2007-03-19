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
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from data.pipe_container import PipeContainer
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoRunError, RelaxRunError



class Test_pipes(TestCase):
    """Unit tests for the functions of the 'generic_fns.pipes' module."""

    def setUp(self):
        """Set up for all the data pipe unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a single object to the 'orig' data pipe.
        relax_data_store['orig'].x = 1

        # Add a single object to the single spin system of the 'orig' data pipe.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 1

        # Add an empty data pipe (for the 'eliminate_unused_pipes' test).
        relax_data_store.add(pipe_name='empty', pipe_type='mf')

        # Set the current pipe to the 'orig' data pipe.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_copy(self):
        """Test the copying of a data pipe.

        The function tested is generic_fns.pipes.copy().
        """

        # Copy the 'orig' data pipe to the 'new' data pipe.
        pipes.copy('orig', 'new')

        # Test that the new data pipe exists.
        self.assert_(relax_data_store.has_key('new'))

        # Test that the new data pipe has the object 'x' and that its value is 1.
        self.assertEqual(relax_data_store['new'].x, 1)

        # Change the value of x.
        relax_data_store['new'].x = 2

        # Test that the two values are different.
        self.assert_(relax_data_store['orig'].x != relax_data_store['new'].x)

        # Test that the new data pipe has the object 'mol[0].res[0].spin[0].num' and that its value is 1.
        self.assertEqual(relax_data_store['new'].mol[0].res[0].spin[0].num, 1)

        # Change the spin system number.
        relax_data_store['new'].mol[0].res[0].spin[0].num = 2

        # Test that the original spin system number hasn't changed.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 1)


    def test_copy_current(self):
        """Test the copying of current data pipe.

        The function tested is generic_fns.pipes.copy().
        """

        # Copy the 'orig' data pipe to the 'new' data pipe.
        pipes.copy(pipe_to='new')

        # Test that the new data pipe exists.
        self.assert_(relax_data_store.has_key('new'))

        # Test that the new data pipe has the object 'x' and that its value is 1.
        self.assertEqual(relax_data_store['new'].x, 1)

        # Change the value of x.
        relax_data_store['new'].x = 2

        # Test that the two values are different.
        self.assert_(relax_data_store['orig'].x != relax_data_store['new'].x)

        # Test that the new data pipe has the object 'mol[0].res[0].spin[0].num' and that its value is 1.
        self.assertEqual(relax_data_store['new'].mol[0].res[0].spin[0].num, 1)

        # Change the spin system number.
        relax_data_store['new'].mol[0].res[0].spin[0].num = 2

        # Test that the original spin system number hasn't changed.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 1)


    def test_copy_fail(self):
        """Test the failure of the copying of data pipes when the data pipe to copy to already exists.

        The function tested is generic_fns.pipes.copy()
        """

        # Assert that a RelaxRunError occurs when the data pipe to copy data to already exists.
        self.assertRaises(RelaxRunError, pipes.copy, 'orig', 'empty')


    def test_creation(self):
        """Test the creation of a data pipe.

        The function used is generic_fns.pipes.create().
        """

        # Create a new model-free data pipe.
        name = 'new'
        pipes.create(name, 'mf')

        # Test that the data pipe exists.
        self.assert_(relax_data_store.has_key(name))

        # Test that the current pipe is the new pipe.
        self.assertEqual(relax_data_store.current_pipe, name)


    def test_creation_fail(self):
        """Test the failure of the creation of a data pipe (by supplying an incorrect pipe type).

        The function used is generic_fns.pipes.create().
        """

        # Assert that a RelaxError occurs when the pipe type is invalid.
        self.assertRaises(RelaxError, pipes.create, 'new', 'x')


    def test_deletion(self):
        """Test the deletion of a data pipe.

        The function tested is generic_fns.pipes.delete()
        """

        # Set the current pipe to the 'orig' data pipe.
        name = 'orig'
        relax_data_store.current_pipe = name

        # Delete the 'orig' data pipe.
        pipes.delete(name)

        # Test that the data pipe no longer exists.
        self.assert_(not relax_data_store.has_key(name))

        # Test that the current pipe is None (as the current pipe was deleted).
        self.assertEqual(relax_data_store.current_pipe, None)


    def test_deletion_fail(self):
        """Test the failure of the deletion of a data pipe (by suppling a non-existant data pipe).

        The function tested is generic_fns.pipes.delete()
        """

        # Assert that a RelaxNoRunError occurs when the data pipe does not exist.
        self.assertRaises(RelaxNoRunError, pipes.delete, 'x')


    def test_switch(self):
        """Test the switching of the current data pipe.

        The function tested is generic_fns.pipes.switch().
        """

        # Switch to the 'orig' data pipe.
        pipes.switch('orig')

        # Test the current data pipe.
        self.assertEqual(relax_data_store.current_pipe, 'orig')

        # Switch to the 'empty' data pipe.
        pipes.switch('empty')

        # Test the current data pipe.
        self.assertEqual(relax_data_store.current_pipe, 'empty')


    def test_switch_fail(self):
        """Test the failure of switching to a non-existant data pipe.

        The function used is generic_fns.pipes.switch().
        """

        # Assert that a RelaxNoRunError occurs when the pipe type is invalid.
        self.assertRaises(RelaxNoRunError, pipes.switch, 'x')
