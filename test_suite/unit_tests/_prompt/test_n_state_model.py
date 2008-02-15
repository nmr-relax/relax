###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
from prompt.n_state_model import N_state_model
from relax_errors import RelaxBoolError, RelaxIntError, RelaxLenError, RelaxListError, RelaxListNumError, RelaxStrError
from test_suite.unit_tests.n_state_model_testing_base import N_state_model_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_n_state_model(N_state_model_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.n_state_model' module."""

    # Instantiate the user function class.
    n_state_model_fns = N_state_model(fake_relax.fake_instance())


    def test_CoM_argfail_pivot_point(self):
        """The pivot_point arg test of the n_state_model.CoM() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None arguments, and skip them.
            if data[0] == 'None':
                continue

            # Catch the list arguments.
            if type(data[1]) == list:
                # The wrong length.
                if len(data[1]) != 3:
                    self.assertRaises(RelaxLenError, self.n_state_model_fns.CoM, pivot_point=data[1])

                # Catch the int, float, and number list arguments, and skip them.
                elif data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list':
                    continue

                # The argument test.
                else:
                    self.assertRaises(RelaxListNumError, self.n_state_model_fns.CoM, pivot_point=data[1])

            # All other arguments.
            else:
                self.assertRaises(RelaxListError, self.n_state_model_fns.CoM, pivot_point=data[1])


    def test_CoM_argfail_centre(self):
        """The centre arg test of the n_state_model.CoM() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None arguments, and skip them.
            if data[0] == 'None':
                continue

            # Catch the list arguments.
            if type(data[1]) == list:
                # The wrong length.
                if len(data[1]) != 3:
                    self.assertRaises(RelaxLenError, self.n_state_model_fns.CoM, centre=data[1])

                # Catch the int, float, and number list arguments, and skip them.
                elif data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list':
                    continue

                # The argument test.
                else:
                    self.assertRaises(RelaxListNumError, self.n_state_model_fns.CoM, centre=data[1])

            # All other arguments.
            else:
                self.assertRaises(RelaxListError, self.n_state_model_fns.CoM, centre=data[1])


    def test_model_argfail_N(self):
        """Failure of the N arg of the n_state_model.model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin and int arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.n_state_model_fns.model, N=data[1])


    def test_model_argfail_ref(self):
        """Failure of the ref arg of the n_state_model.model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.model, N=5, ref=data[1])


    def test_set_domain_argfail_tensor(self):
        """Failure of the tensor arg of the n_state_model.set_domain() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.set_domain, tensor=data[1])


    def test_set_domain_argfail_domain(self):
        """Failure of the domain arg of the n_state_model.set_domain() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.set_domain, domain=data[1])


    def test_set_type_argfail_tensor(self):
        """Failure of the tensor arg of the n_state_model.set_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.set_type, tensor=data[1])


    def test_set_type_argfail_red(self):
        """Failure of the red arg of the n_state_model.set_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool argument, and skip it.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.n_state_model_fns.set_type, tensor='test', red=data[1])


