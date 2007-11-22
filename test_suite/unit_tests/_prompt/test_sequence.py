###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
import sys

# relax module imports.
from data import Data as relax_data_store
from data_types import return_data_types
from prompt.sequence import Sequence
from relax_errors import RelaxNoneIntError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.sequence_testing_base import Sequence_base_class

# Set the variable sys.ps3 (this is required by the user functions).
sys.ps3 = 'relax> '


# A class to act as a container.
class Container:
    pass

# Fake normal relax usage of the user function class.
relax = Container()
relax.interpreter = Container()
relax.interpreter.intro = True


class Test_sequence(Sequence_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.sequence' module."""

    # Instantiate the user function class.
    sequence_fns = Sequence(relax)


    def test_read_argfail_file(self):
        """Test the proper failure of the sequence.read() user function for the file argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.sequence_fns.read, file=data[1])


    def test_read_argfail_dir(self):
        """Test the proper failure of the sequence.read() user function for the dir argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.sequence_fns.read, file='a', dir=data[1])


    def test_read_argfail_mol_name_col(self):
        """The proper failure of the sequence.read() user function for the mol_name_col argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', mol_name_col=data[1])


    def test_read_argfail_res_num_col(self):
        """The proper failure of the sequence.read() user function for the res_num_col argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', res_num_col=data[1])


    def test_read_argfail_res_name_col(self):
        """The proper failure of the sequence.read() user function for the res_name_col argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', res_name_col=data[1])


    def test_read_argfail_spin_num_col(self):
        """The proper failure of the sequence.read() user function for the spin_num_col argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.sequence_fns.read, file='a', spin_num_col=data[1])


