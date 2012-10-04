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
from relax_errors import RelaxBoolError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError, RelaxStrFileError

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_select(TestCase):
    """Unit tests for the functions of the 'prompt.select' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_select, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.select_fns = self.interpreter.select


    def test_read_argfail_file(self):
        """The file arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str' or data[0] == 'file':
                continue

            # The argument test.
            self.assertRaises(RelaxStrFileError, self.select_fns.read, file=data[1])


    def test_read_argfail_dir(self):
        """The dir arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.select_fns.read, file='unresolved', dir=data[1])


    def test_read_argfail_mol_name_col(self):
        """The mol_name_col arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.select_fns.read, file='unresolved', mol_name_col=data[1])


    def test_read_argfail_res_num_col(self):
        """The res_num_col arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.select_fns.read, file='unresolved', res_num_col=data[1])


    def test_read_argfail_res_name_col(self):
        """The res_name_col arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.select_fns.read, file='unresolved', res_name_col=data[1])


    def test_read_argfail_spin_num_col(self):
        """The spin_num_col arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.select_fns.read, file='unresolved', spin_num_col=data[1])


    def test_read_argfail_spin_name_col(self):
        """The spin_name_col arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.select_fns.read, file='unresolved', spin_name_col=data[1])


    def test_read_argfail_sep(self):
        """The sep arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.select_fns.read, file='unresolved', sep=data[1])


    def test_read_argfail_boolean(self):
        """The boolean arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.select_fns.read, file='unresolved', boolean=data[1])


    def test_read_argfail_change_all(self):
        """The change_all arg test of the select.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.select_fns.read, file='unresolved', change_all=data[1])


    def test_reverse_argfail_spin_id(self):
        """The spin_id arg test of the select.reverse() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.select_fns.reverse, spin_id=data[1])


    def test_spin_argfail_spin_id(self):
        """The spin_id arg test of the select.spin() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.select_fns.spin, spin_id=data[1])


    def test_spin_argfail_boolean(self):
        """The boolean arg test of the select.spin() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.select_fns.spin, boolean=data[1])


    def test_spin_argfail_change_all(self):
        """The change_all arg test of the select.spin() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.select_fns.spin, change_all=data[1])
