###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
from lib.errors import RelaxNoneNumError, RelaxStrError

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_relax_disp(TestCase):
    """Unit tests for the functions of the 'prompt.relax_disp' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_relax_disp, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.relax_disp_fns = self.interpreter.relax_disp


    def test_relax_cpmg_setup_argfail_cpmg_frq(self):
        """The cpmg_frq arg test of the relax_disp.cpmg_setup() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, int and None arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int' or data[0] == 'None':
                continue

        # The argument test.
        self.assertRaises(RelaxNoneNumError, self.relax_disp_fns.cpmg_setup, spectrum_id='test', cpmg_frq=data[1])


    def test_relax_cpmg_setup_argfail_spectrum_id(self):
        """The spectrum_id arg test of the relax_disp.cpmg_setup() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

        # The argument test.
        self.assertRaises(RelaxStrError, self.relax_disp_fns.cpmg_setup, spectrum_id=data[1])


    def test_relax_exp_type_argfail_exp_type(self):
        """The exp_type arg test of the relax_disp.exp_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

        # The argument test.
        self.assertRaises(RelaxStrError, self.relax_disp_fns.exp_type, exp_type=data[1])


    def test_relax_select_model_argfail_model(self):
        """The model arg test of the relax_disp.select_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

        # The argument test.
        self.assertRaises(RelaxStrError, self.relax_disp_fns.select_model, model=data[1])
