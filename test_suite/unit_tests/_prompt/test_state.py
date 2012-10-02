###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
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
from unittest import TestCase

# relax module imports.
from prompt.interpreter import Interpreter
from test_suite.unit_tests.state_testing_base import State_base_class
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxStrFileError

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES

 
class Test_state(State_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.state' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_state, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.state = self.interpreter.state

        # Alias the user functions to work with the backend.
        self.state.load_state = self.state.load
        self.state.save_state = self.state.save


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
