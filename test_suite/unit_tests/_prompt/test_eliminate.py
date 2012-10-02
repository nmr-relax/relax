###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
from relax_errors import RelaxNoneFunctionError, RelaxNoneTupleError

# Unit test imports.
from test_suite.unit_tests._prompt.container import Container
from test_suite.unit_tests._prompt.data_types import DATA_TYPES



def dummy_function():
    pass



class Test_eliminate(TestCase):
    """Unit tests for the functions of the 'prompt.eliminate' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_eliminate, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Place the user functions into a container.
        self.eliminate_fns = Container()
        self.eliminate_fns.eliminate = self.interpreter.eliminate


    def test_eliminate_function(self):
        """The function arg unit test of the eliminate() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and func arguments, and skip them.
            if data[0] == 'None' or data[0] == 'function':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneFunctionError, self.eliminate_fns.eliminate, function=data[1])


    def test_eliminate_args(self):
        """The args arg unit test of the eliminate() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and tuple arguments, and skip them.
            if data[0] == 'None' or data[0] == 'tuple' or data[0] == 'float tuple' or data[0] == 'str tuple':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneTupleError, self.eliminate_fns.eliminate, function=dummy_function, args=data[1])
