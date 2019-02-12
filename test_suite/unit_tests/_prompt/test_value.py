###############################################################################
#                                                                             #
# Copyright (C) 2007-2008,2012,2019 Edward d'Auvergne                         #
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
from lib.errors import RelaxStrError, RelaxStrListStrError, RelaxValListValError
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
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.value_fns = self.interpreter.value


    def test_set_argfail_val(self):
        """The val arg test of the value.set() user function."""

        # Set the current data pipe to 'mf'.
        self.interpreter.pipe.switch('mf')

        # Loop over the data types.
        allowed_params = ['s2', 's2f', 's2s', 'te', 'ts', 'tf', 'rex', 'csa']
        for data in DATA_TYPES:
            # Skip empty lists.
            if data[0] in ['list']:
                continue

            # Make sure the param and val argument match.
            param = 'csa'
            if data[0] in ['file list', 'float list', 'int list', 'list', 'none list', 'number list', 'str list']:
                param = []
                for i in range(len(data[1])):
                    param.append(allowed_params[i])
                if not len(param):
                    param = 'csa'

            # Everything is allowed.
            self.value_fns.set(val=data[1], param=param)


    def test_set_argfail_param(self):
        """The param arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, str, and str list arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str' or data[0] == 'str list':
                continue

            # The argument test.
            self.assertRaises(RelaxStrListStrError, self.value_fns.set, param=data[1], val=None)


    def test_set_argfail_spin_id(self):
        """The spin_id arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.value_fns.set, spin_id=data[1])
