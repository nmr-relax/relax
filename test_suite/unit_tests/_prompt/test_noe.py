###############################################################################
#                                                                             #
# Copyright (C) 2008, 2010 Edward d'Auvergne                                  #
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
from prompt.noe import Noe
from relax_errors import RelaxNoneIntError, RelaxNoneStrError, RelaxStrError

# Unit test imports.
from data_types import DATA_TYPES


class Test_noe(TestCase):
    """Unit tests for the functions of the 'prompt.noe' module."""

    # Instantiate the user function class.
    noe_fns = Noe()


    def test_read_restraints_argfail_file(self):
        """The file arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.noe_fns.read_restraints, file=data[1])


    def test_read_restraints_argfail_dir(self):
        """The dir arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.noe_fns.read_restraints, file='noes', dir=data[1])


    def test_read_restraints_argfail_proton1_col(self):
        """The proton1_col arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.noe_fns.read_restraints, file='noes', proton1_col=data[1])


    def test_read_restraints_argfail_proton2_col(self):
        """The proton2_col arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.noe_fns.read_restraints, file='noes', proton2_col=data[1])


    def test_read_restraints_argfail_lower_col(self):
        """The lower_col arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.noe_fns.read_restraints, file='noes', lower_col=data[1])


    def test_read_restraints_argfail_upper_col(self):
        """The upper_col arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.noe_fns.read_restraints, file='noes', upper_col=data[1])


    def test_read_restraints_argfail_sep(self):
        """The sep arg test of the noe.read_restraints() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.noe_fns.read_restraints, file='noes', sep=data[1])


    def test_spectrum_type_argfail_spectrum_type(self):
        """The spectrum_type arg test of the noe.spectrum_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.noe_fns.spectrum_type, spectrum_type=data[1])


    def test_spectrum_type_argfail_spectrum_id(self):
        """The spectrum_id arg test of the noe.spectrum_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.noe_fns.spectrum_type, spectrum_type='x', spectrum_id=data[1])
