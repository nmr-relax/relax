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
from relax_errors import RelaxIntError, RelaxListIntError, RelaxNoneIntError, RelaxNoneIntListIntError, RelaxNoneStrError, RelaxNumError, RelaxStrError

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_spectrum(TestCase):
    """Unit tests for the functions of the 'prompt.spectrum' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_spectrum, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.spectrum_fns = self.interpreter.spectrum


    def test_baseplane_rmsd_argfail_error(self):
        """The error arg test of the spectrum.baseplane_rmsd() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, bin, and int arguments, and skip them.
            if data[0] == 'float' or data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.spectrum_fns.baseplane_rmsd, error=data[1])


    def test_baseplane_rmsd_argfail_spectrum_id(self):
        """The spectrum_id arg test of the spectrum.baseplane_rmsd() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.baseplane_rmsd, spectrum_id=data[1])


    def test_baseplane_rmsd_argfail_spin_id(self):
        """The spin_id arg test of the spectrum.baseplane_rmsd() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spectrum_fns.baseplane_rmsd, spectrum_id='x', spin_id=data[1])


    def test_integration_points_argfail_N(self):
        """The N arg test of the spectrum.integration_points() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin and int arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.spectrum_fns.integration_points, N=data[1])


    def test_integration_points_argfail_spectrum_id(self):
        """The spectrum_id arg test of the spectrum.integration_points() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.integration_points, N=0, spectrum_id=data[1])


    def test_integration_points_argfail_spin_id(self):
        """The spin_id arg test of the spectrum.integration_points() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spectrum_fns.integration_points, N=0, spectrum_id='x', spin_id=data[1])


    def test_read_intensities_argfail_file(self):
        """The file arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.read_intensities, file=data[1])


    def test_read_intensities_argfail_dir(self):
        """The dir arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spectrum_fns.read_intensities, file='a', dir=data[1])


    def test_read_intensities_argfail_spectrum_id(self):
        """The spectrum_id arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.read_intensities, spectrum_id=data[1])


    def test_read_intensities_argfail_heteronuc(self):
        """The heteronuc arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.read_intensities, heteronuc=data[1])


    def test_read_intensities_argfail_proton(self):
        """The proton arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.read_intensities, proton=data[1])


    def test_read_intensities_argfail_int_col(self):
        """The int_col arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, bin, or integer list arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin' or data[0] == 'int list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntListIntError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_col=data[1])


    def test_read_intensities_argfail_int_method(self):
        """The int_method arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spectrum_fns.read_intensities, int_method=data[1])


    def test_read_intensities_argfail_mol_name_col(self):
        """The mol_name_col arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_method='y', mol_name_col=data[1])


    def test_read_intensities_argfail_res_num_col(self):
        """The res_num_col arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_method='y', res_num_col=data[1])


    def test_read_intensities_argfail_res_name_col(self):
        """The res_name_col arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_method='y', res_name_col=data[1])


    def test_read_intensities_argfail_spin_num_col(self):
        """The spin_num_col arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_method='y', spin_num_col=data[1])


    def test_read_intensities_argfail_spin_name_col(self):
        """The spin_name_col arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, and bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_method='y', spin_name_col=data[1])


    def test_read_intensities_argfail_sep(self):
        """The sep arg test of the spectrum.read_intensities() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spectrum_fns.read_intensities, file='a', spectrum_id='x', int_method='y', sep=data[1])
