###############################################################################
#                                                                             #
# Copyright (C) 2007, 2010 Edward d'Auvergne                                  #
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
from test_suite.unit_tests.state_testing_base import State_base_class
from prompt.state import State
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxStrFileError

# Unit test imports.
from data_types import DATA_TYPES

 
class Test_state(State_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.state' module."""

    # Instantiate the user function class.
    state = State()

    # Rename the user functions.
    state.load_state = state.load
    state.save_state = state.save


    def test_load_argfail_state(self):
        """Test the proper failure of the state.load() user function for the state argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str and file arguments, and skip them.
            if data[0] == 'str' or data[0] == 'file':
                continue

            # The argument test.
            self.assertRaises(RelaxStrFileError, self.state.load_state, state=data[1])


    def test_load_argfail_dir(self):
        """Test the proper failure of the state.load() user function for the dir argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.state.load_state, state='a', dir=data[1])


    def test_save_argfail_state(self):
        """Test the proper failure of the state.save() user function for the state argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str and file arguments, and skip them.
            if data[0] == 'str' or data[0] == 'file':
                continue

            # The argument test.
            self.assertRaises(RelaxStrFileError, self.state.save_state, state=data[1])


    def test_save_argfail_dir(self):
        """Test the proper failure of the state.save() user function for the dir argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.state.save_state, state='a', dir=data[1])


    def test_save_argfail_force(self):
        """Test the proper failure of the state.save() user function for the force argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.state.save_state, state='a', force=data[1])


    def test_save_argfail_compress_type(self):
        """Test the proper failure of the state.save() user function for the compress_type argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.state.save_state, state='a', compress_type=data[1])



