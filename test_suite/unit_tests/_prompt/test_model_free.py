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
from prompt.model_free import Model_free
from relax_errors import RelaxListStrError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.model_free_testing_base import Model_free_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_model_free(Model_free_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.model_free' module."""

    # Instantiate the user function class.
    model_free_fns = Model_free()


    def test_create_model_argfail_model(self):
        """The model arg test of the model_free.create_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.model_free_fns.create_model, model=data[1])


    def test_create_model_argfail_equation(self):
        """The equation arg test of the model_free.create_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.model_free_fns.create_model, equation=data[1])


    def test_create_model_argfail_params(self):
        """The params arg test of the model_free.create_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str list argument, and skip it.
            if data[0] == 'str list':
                continue

            # The argument test.
            self.assertRaises(RelaxListStrError, self.model_free_fns.create_model, model='test', equation='test', params=data[1])


    def test_create_model_argfail_spin_id(self):
        """The spin_id arg test of the model_free.create_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.model_free_fns.create_model, model='test', equation='test', params=['test'], spin_id=data[1])


    def test_remove_tm_argfail_spin_id(self):
        """The spin_id arg test of the model_free.remove_tm() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.model_free_fns.remove_tm, spin_id=data[1])


    def test_select_model_argfail_model(self):
        """The model arg test of the model_free.select_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.model_free_fns.select_model, model=data[1])


    def test_select_model_argfail_spin_id(self):
        """The spin_id arg test of the model_free.select_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.model_free_fns.select_model, model='test', spin_id=data[1])



