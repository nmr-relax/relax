###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
import sys
from tempfile import mktemp
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.pipes import VALID_TYPES, get_pipe


class State(TestCase):
    """Class for testing the state saving and loading user functions."""

    def setUp(self):
        """Common set up for these system tests."""

        # Create a temporary file name.
        self.tmpfile = mktemp()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Delete the temporary file.
        try:
            remove(self.tmpfile)
        except OSError:
            pass


    def test_state(self):
        """Test the saving, loading, and second saving and loading of the program state."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('test', 'mf')

        # Save the state.
        self.relax.interpreter._State.save(self.tmpfile, force=True)

        # Load the state.
        self.relax.interpreter._State.load(self.tmpfile)

        # Save the state.
        self.relax.interpreter._State.save(self.tmpfile, force=True)

        # Load the state.
        self.relax.interpreter._State.load(self.tmpfile)


    def test_write_read_pipes(self):
        """Test the writing out, and re-reading of data pipes from the state file."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('test', 'relax_fit')

        # Remove the data pipe.
        ds.__reset__()

        # Create a few data pipes.
        for i in range(len(VALID_TYPES)):
            self.relax.interpreter._Pipe.create('test' + repr(i), VALID_TYPES[i])

        # Write the results.
        self.relax.interpreter._State.save(self.tmpfile)

        # Reset the relax data storage object.
        ds.__reset__()

        # Re-read the results.
        self.relax.interpreter._State.load(self.tmpfile)

        # Test the pipes.
        for i in range(len(VALID_TYPES)):
            # Name.
            name = 'test' + repr(i)
            self.assert_(name in ds)

            # Type.
            pipe = get_pipe(name)
            self.assertEqual(pipe.pipe_type, VALID_TYPES[i])
