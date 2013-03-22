###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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
from lib.errors import RelaxError, RelaxNoneValListValError, RelaxNoneStrError, RelaxNoneStrListStrError
from test_suite.unit_tests.value_testing_base import Value_base_class

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_value(Value_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.value' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_value, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.value_fns = self.interpreter.value


    def test_set_argfail_val(self):
        """The val arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, float, int, str, bin, float list, int list, str list, or bin list arguments, and skip them.
            if data[0] == 'None' or data[0] == 'bin' or data[0] == 'bool' or data[0] == 'int' or data[0] == 'str' or data[0] == 'float' or data[0] == 'int list' or data[0] == 'bin list' or data[0] == 'bool list' or data[0] == 'str list' or data[0] == 'float list' or data[0] == 'number list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneValListValError, self.value_fns.set, val=data[1], param='csa')


    def test_set_argfail_param(self):
        """The param arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, str, and str list arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str' or data[0] == 'str list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrListStrError, self.value_fns.set, param=data[1], val=None)


    def test_set_argfail_spin_id(self):
        """The spin_id arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.value_fns.set, spin_id=data[1])
