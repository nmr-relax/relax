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
from relax_errors import RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.molecule_testing_base import Molecule_base_class

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_molecule(Molecule_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.molecule' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_molecule, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.molecule_fns = self.interpreter.molecule


    def test_copy_argfail_pipe_from(self):
        """Test the proper failure of the molecule.copy() user function for the pipe_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.copy, pipe_from=data[1], mol_from='#Old mol', mol_to='#Old mol')


    def test_copy_argfail_mol_from(self):
        """Test the proper failure of the molecule.copy() user function for the mol_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.copy, mol_from=data[1], mol_to='#Old mol')


    def test_copy_argfail_pipe_to(self):
        """Test the proper failure of the molecule.copy() user function for the pipe_to argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.copy, pipe_to=data[1], mol_from='#Old mol', mol_to='#New mol2')


    def test_copy_argfail_mol_to(self):
        """Test the proper failure of the molecule.copy() user function for the mol_to argument."""

        # Set up some data.
        self.setup_data()

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.copy, mol_from='#Old mol', mol_to=data[1])


    def test_create_argfail_mol_name(self):
        """Test the proper failure of the molecule.create() user function for the mol_name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.create, mol_name=data[1])


    def test_delete_argfail_mol_id(self):
        """Test the proper failure of the molecule.delete() user function for the mol_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.delete, mol_id=data[1])


    def test_display_argfail_mol_id(self):
        """Test the proper failure of the molecule.display() user function for the mol_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.display, mol_id=data[1])


    def test_name_argfail_mol_id(self):
        """Test the proper failure of the molecule.name() user function for the mol_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.name, mol_id=data[1])


    def test_name_argfail_name(self):
        """Test the proper failure of the molecule.name() user function for the name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.name, name=data[1])
