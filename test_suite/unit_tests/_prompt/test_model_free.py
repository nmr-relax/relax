###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
from lib.errors import RelaxListStrError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.model_free_testing_base import Model_free_base_class

# Unit test imports.
from test_suite.unit_tests._prompt.data_types import DATA_TYPES


class Test_model_free(Model_free_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.model_free' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_model_free, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.model_free_fns = self.interpreter.model_free


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



