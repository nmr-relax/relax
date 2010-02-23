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
from prompt.sequence import Sequence
from relax_errors import RelaxError, RelaxBoolError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.sequence_testing_base import Sequence_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_sequence(Sequence_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.sequence' module."""

    # Instantiate the user function class.
    sequence_fns = Sequence()


    def test_copy_argfail_pipe_from(self):
        """The pipe_from arg test of the sequence.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.copy, pipe_from=data[1])


    def test_copy_argfail_pipe_to(self):
        """The pipe_to arg test of the sequence.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.copy, pipe_to=data[1])


    def test_copy_argfail_both_pipes(self):
        """The pipe_from and pipe_to arg test of the sequence.copy() user function."""

        # Test that both cannot be None (the default)!
        self.assertRaises(RelaxError, self.sequence_fns.copy)


    def test_display_argfail_sep(self):
        """The proper failure of the sequence.display() user function for the sep argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.display, sep=data[1])


    def test_display_argfail_mol_name_flag(self):
        """The proper failure of the sequence.display() user function for the mol_name_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.display, mol_name_flag=data[1])


    def test_display_argfail_res_num_flag(self):
        """The proper failure of the sequence.display() user function for the res_num_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.display, res_num_flag=data[1])


    def test_display_argfail_res_name_flag(self):
        """The proper failure of the sequence.display() user function for the res_name_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.display, res_name_flag=data[1])


    def test_display_argfail_spin_num_flag(self):
        """The proper failure of the sequence.display() user function for the spin_num_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.display, spin_num_flag=data[1])


    def test_display_argfail_spin_name_flag(self):
        """The proper failure of the sequence.display() user function for the spin_name_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.display, spin_name_flag=data[1])


    def test_read_argfail_file(self):
        """Test the proper failure of the sequence.read() user function for the file argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.sequence_fns.read, file=data[1])


    def test_read_argfail_dir(self):
        """Test the proper failure of the sequence.read() user function for the dir argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.read, file='a', dir=data[1])


    def test_read_argfail_mol_name_col(self):
        """The proper failure of the sequence.read() user function for the mol_name_col argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', mol_name_col=data[1])


    def test_read_argfail_res_num_col(self):
        """The proper failure of the sequence.read() user function for the res_num_col argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', res_num_col=data[1])


    def test_read_argfail_res_name_col(self):
        """The proper failure of the sequence.read() user function for the res_name_col argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', res_name_col=data[1])


    def test_read_argfail_spin_num_col(self):
        """The proper failure of the sequence.read() user function for the spin_num_col argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', spin_num_col=data[1])


    def test_read_argfail_spin_name_col(self):
        """The proper failure of the sequence.read() user function for the spin_name_col argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', spin_name_col=data[1])


    def test_read_argfail_sep(self):
        """The proper failure of the sequence.read() user function for the sep argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.read, file='a', sep=data[1])


    def test_write_argfail_file(self):
        """Test the proper failure of the sequence.write() user function for the file argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.sequence_fns.write, file=data[1])


    def test_write_argfail_dir(self):
        """Test the proper failure of the sequence.write() user function for the dir argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.write, file='a', dir=data[1])


    def test_write_argfail_mol_name_flag(self):
        """The proper failure of the sequence.write() user function for the mol_name_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.write, file='a', mol_name_flag=data[1])


    def test_write_argfail_res_num_flag(self):
        """The proper failure of the sequence.write() user function for the res_num_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.write, file='a', res_num_flag=data[1])


    def test_write_argfail_res_name_flag(self):
        """The proper failure of the sequence.write() user function for the res_name_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.write, file='a', res_name_flag=data[1])


    def test_write_argfail_spin_num_flag(self):
        """The proper failure of the sequence.write() user function for the spin_num_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.write, file='a', spin_num_flag=data[1])


    def test_write_argfail_spin_name_flag(self):
        """The proper failure of the sequence.write() user function for the spin_name_flag argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.write, file='a', spin_name_flag=data[1])


    def test_write_argfail_sep(self):
        """The proper failure of the sequence.write() user function for the sep argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.write, file='a', sep=data[1])


    def test_write_argfail_force(self):
        """The force arg test of the sequence.write() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.sequence_fns.write, file='a', force=data[1])
