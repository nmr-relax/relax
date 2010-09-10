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
from prompt.minimisation import Minimisation
from relax_errors import RelaxError, RelaxBoolError, RelaxIntError, RelaxIntListIntError, RelaxListError, RelaxListNumError, RelaxNoneError, RelaxNoneListNumError, RelaxNoneNumError, RelaxNumError, RelaxStrError
from test_suite.unit_tests.minimisation_testing_base import Minimisation_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_minimisation(Minimisation_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.minimisation' module."""

    # Instantiate the user function class.
    minimisation_fns = Minimisation()


    def test_calc_argfail_verbosity(self):
        """The verbosity arg test of the calc() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.minimisation_fns.calc, verbosity=data[1])


    def test_grid_search_argfail_lower(self):
        """The lower arg test of the grid_search() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and int, float, and number list arguments arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneListNumError, self.minimisation_fns.grid_search, lower=data[1])


    def test_grid_search_argfail_upper(self):
        """The upper arg test of the grid_search() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and int, float, and number list arguments arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneListNumError, self.minimisation_fns.grid_search, upper=data[1])


    def test_grid_search_argfail_inc(self):
        """The inc arg test of the grid_search() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin, int, and interger list arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int' or data[0] == 'int list' or data[0] == 'none list':
                continue

            # The argument test.
            self.assertRaises(RelaxIntListIntError, self.minimisation_fns.grid_search, inc=data[1])


    def test_grid_search_argfail_constraints(self):
        """The constraints arg test of the grid_search() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.minimisation_fns.grid_search, constraints=data[1])


    def test_grid_search_argfail_verbosity(self):
        """The verbosity arg test of the grid_search() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.minimisation_fns.grid_search, verbosity=data[1])


    def test_minimise_argfail_args(self):
        """The test of the arguments of the minimise() user function."""

        # No arguments.
        self.assertRaises(RelaxNoneError, self.minimisation_fns.minimise)

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.minimisation_fns.minimise, data[1])
            self.assertRaises(RelaxStrError, self.minimisation_fns.minimise, 'a', data[1])
            self.assertRaises(RelaxStrError, self.minimisation_fns.minimise, 'a', 'b', data[1])


    def test_minimise_argfail_bad_keyword(self):
        """The test of a bad keyword argument in the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # The argument test.
            self.assertRaises(RelaxError, self.minimisation_fns.minimise, 'Newton', step_tol=data[1])


    def test_minimise_argfail_func_tol(self):
        """The func_tol arg test of the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, bin, and int arguments, and skip them.
            if data[0] == 'float' or data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.minimisation_fns.minimise, 'Newton', func_tol=data[1])


    def test_minimise_argfail_grad_tol(self):
        """The grad_tol arg test of the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, float, bin, and int arguments, and skip them.
            if data[0] == 'None' or data[0] == 'float' or data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneNumError, self.minimisation_fns.minimise, 'Newton', grad_tol=data[1])


    def test_minimise_argfail_max_iterations(self):
        """The max_iterations arg test of the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin and int arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.minimisation_fns.minimise, 'Newton', max_iterations=data[1])


    def test_minimise_argfail_constraints(self):
        """The constraints arg test of the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.minimisation_fns.minimise, 'Newton', constraints=data[1])


    def test_minimise_argfail_scaling(self):
        """The scaling arg test of the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.minimisation_fns.minimise, 'Newton', scaling=data[1])


    def test_minimise_argfail_verbosity(self):
        """The verbosity arg test of the minimise() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin and int arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.minimisation_fns.minimise, 'Newton', verbosity=data[1])


