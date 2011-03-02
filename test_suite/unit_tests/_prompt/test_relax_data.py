###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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
from prompt.relax_data import Relax_data
from relax_errors import RelaxError, RelaxBoolError, RelaxFloatError, RelaxIntError, RelaxNoneIntError, RelaxNoneStrError, RelaxNumError, RelaxStrError
from test_suite.unit_tests.relax_data_testing_base import Relax_data_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_relax_data(Relax_data_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.relax_data' module."""

    # Instantiate the user function class.
    relax_data_fns = Relax_data()


    def test_back_calc_argfail_ri_id(self):
        """The ri_id arg test of the relax_data.back_calc() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.back_calc, ri_id=data[1])


    def test_back_calc_argfail_ri_type(self):
        """The ri_type arg test of the relax_data.back_calc() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.back_calc, ri_id='R2', ri_type=data[1])


    def test_back_calc_argfail_frq(self):
        """The frq arg test of the relax_data.back_calc() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the number arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int' or data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.relax_data_fns.back_calc, ri_id='R2_1000', frq=data[1])


    def test_copy_argfail_pipe_from(self):
        """The pipe_from arg test of the relax_data.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.relax_data_fns.copy, pipe_from=data[1])


    def test_copy_argfail_pipe_to(self):
        """The pipe_to arg test of the relax_data.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.relax_data_fns.copy, pipe_from='', pipe_to=data[1])


    def test_copy_argfail_both_pipes(self):
        """The pipe_from and pipe_to arg test of the relax_data.copy() user function."""

        # Test that both cannot be None (the default)!
        self.assertRaises(RelaxError, self.relax_data_fns.copy)


    def test_copy_argfail_ri_id(self):
        """The ri_id arg test of the relax_data.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.relax_data_fns.copy, pipe_from='', pipe_to='', ri_id=data[1])


    def test_delete_argfail_ri_id(self):
        """The ri_id arg test of the relax_data.delete() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.delete, ri_id=data[1])


    def test_display_argfail_ri_id(self):
        """The ri_id arg test of the relax_data.display() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.display, ri_id=data[1])


    def test_read_argfail_ri_id(self):
        """The ri_id arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.read, ri_id=data[1])


    def test_read_argfail_ri_type(self):
        """The ri_type arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.read, ri_id='R2', ri_type=data[1])


    def test_read_argfail_frq(self):
        """The frq arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the number arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int' or data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=data[1])


    def test_read_argfail_file(self):
        """The file arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file=data[1])


    def test_read_argfail_dir(self):
        """The dir arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', dir=data[1])


    def test_read_argfail_mol_name_col(self):
        """The mol_name_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', mol_name_col=data[1])


    def test_read_argfail_res_num_col(self):
        """The res_num_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', res_num_col=data[1])


    def test_read_argfail_res_name_col(self):
        """The res_name_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', res_name_col=data[1])


    def test_read_argfail_spin_num_col(self):
        """The spin_num_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', spin_num_col=data[1])


    def test_read_argfail_spin_name_col(self):
        """The spin_name_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', spin_name_col=data[1])


    def test_read_argfail_data_col(self):
        """The data_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', data_col=data[1])


    def test_read_argfail_error_col(self):
        """The error_col arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', error_col=data[1])


    def test_read_argfail_sep(self):
        """The sep arg test of the relax_data.read() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.relax_data_fns.read, ri_id='R2_1000', ri_type='R2', frq=1e9, file='R2_1000MHz', data_col=0, error_col=0, sep=data[1])


    def test_write_argfail_ri_id(self):
        """The ri_id arg test of the relax_data.write() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.write, ri_id=data[1])


    def test_write_argfail_file(self):
        """The file arg test of the relax_data.write() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_data_fns.write, ri_id='R2_1000', file=data[1])


    def test_write_argfail_dir(self):
        """The dir arg test of the relax_data.write() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.relax_data_fns.write, ri_id='R2_1000', file='a', dir=data[1])


    def test_write_argfail_force(self):
        """The force arg test of the relax_data.write() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.relax_data_fns.write, ri_id='R2_1000', file='a', force=data[1])
