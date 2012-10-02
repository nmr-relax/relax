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
from relax_errors import RelaxIntError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.residue_testing_base import Residue_base_class

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_residue(Residue_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.residue' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_residue, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.residue_fns = self.interpreter.residue


    def test_copy_argfail_pipe_from(self):
        """Test the proper failure of the residue.copy() user function for the pipe_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.copy, pipe_from=data[1], res_from='#Old mol:1', res_to='#Old mol:2')


    def test_copy_argfail_res_from(self):
        """Test the proper failure of the residue.copy() user function for the res_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.residue_fns.copy, res_from=data[1], res_to='#Old mol:2')


    def test_copy_argfail_pipe_to(self):
        """Test the proper failure of the residue.copy() user function for the pipe_to argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.copy, pipe_to=data[1], res_from='#Old mol:1', res_to='#Old mol:2')


    def test_copy_argfail_res_to(self):
        """Test the proper failure of the residue.copy() user function for the res_to argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.copy, res_from='#Old mol:1@111', res_to=data[1])


    def test_create_argfail_res_num(self):
        """Test the proper failure of the residue.create() user function for the res_num argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.residue_fns.create, res_num=data[1], res_name='NH')


    def test_create_argfail_res_name(self):
        """Test the proper failure of the residue.create() user function for the res_name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.create, res_name=data[1], res_num=1)


    def test_create_argfail_mol_name(self):
        """Test the proper failure of the residue.create() user function for the mol_name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.create, mol_name=data[1], res_num=1, res_name='NH')


    def test_delete_argfail_res_id(self):
        """Test the proper failure of the residue.delete() user function for the res_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.residue_fns.delete, res_id=data[1])


    def test_display_argfail_res_id(self):
        """Test the proper failure of the residue.display() user function for the res_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.display, res_id=data[1])


    def test_name_argfail_res_id(self):
        """Test the proper failure of the residue.name() user function for the res_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.residue_fns.name, res_id=data[1])


    def test_name_argfail_name(self):
        """Test the proper failure of the residue.name() user function for the name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.residue_fns.name, name=data[1])


    def test_number_argfail_res_id(self):
        """Test the proper failure of the residue.number() user function for the res_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.residue_fns.number, res_id=data[1])


    def test_number_argfail_number(self):
        """Test the proper failure of the residue.number() user function for the number argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.residue_fns.number, res_id=':1', number=data[1])
