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
from prompt.residue import Residue
from relax_errors import RelaxIntError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.residue_testing_base import Residue_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_residue(Residue_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.residue' module."""

    # Instantiate the user function class.
    residue_fns = Residue()


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
            if data[0] == 'None' or  data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.residue_fns.copy, res_from='#Old mol:1@111', res_to=data[1])


    def test_create_argfail_res_num(self):
        """Test the proper failure of the residue.create() user function for the res_num argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.residue_fns.create, res_num=data[1], res_name='NH')


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
