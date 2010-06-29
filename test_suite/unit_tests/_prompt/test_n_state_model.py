###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
from relax_errors import RelaxBoolError, RelaxIntError, RelaxLenError, RelaxListError, RelaxListNumError, RelaxNoneListNumError, RelaxNoneStrError, RelaxNumError, RelaxStrError
from test_suite.unit_tests.n_state_model_testing_base import N_state_model_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_n_state_model(N_state_model_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.n_state_model' module."""

    # Instantiate the user function class.
    n_state_model_fns = N_state_model()


    def test_CoM_argfail_pivot_point(self):
        """The pivot_point arg test of the n_state_model.CoM() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int, float, and number list arguments, and skip them (if the length is 3).
            if (data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list') and len(data[1]) == 3:
                continue

            # The argument test.
            self.assertRaises(RelaxListNumError, self.n_state_model_fns.CoM, pivot_point=data[1])


    def test_CoM_argfail_centre(self):
        """The centre arg test of the n_state_model.CoM() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, int, float, and number list arguments, and skip them (if the length is 3).
            if data[0] == 'None' or ((data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list') and len(data[1]) == 3):
                continue

            # The argument test.
            self.assertRaises(RelaxNoneListNumError, self.n_state_model_fns.CoM, centre=data[1])


    def test_cone_pdb_argfail_cone_type(self):
        """The cone_type arg test of the n_state_model.cone_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.cone_pdb, cone_type=data[1])


    def test_cone_pdb_argfail_scale(self):
        """The scale arg test of the n_state_model.cone_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, bin, and int arguments, and skip them.
            if data[0] == 'float' or data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.n_state_model_fns.cone_pdb, cone_type='', scale=data[1])


    def test_cone_pdb_argfail_file(self):
        """The file arg test of the n_state_model.cone_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.cone_pdb, cone_type='', file=data[1])


    def test_cone_pdb_argfail_dir(self):
        """The dir arg test of the n_state_model.cone_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.n_state_model_fns.cone_pdb, cone_type='', dir=data[1])


    def test_cone_pdb_argfail_force(self):
        """The force arg test of the n_state_model.cone_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.n_state_model_fns.cone_pdb, cone_type='', force=data[1])


    def test_number_of_states_argfail_N(self):
        """Failure of the N arg of the n_state_model.number_of_states() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin and int arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.n_state_model_fns.number_of_states, N=data[1])


    def test_ref_domain_argfail_ref(self):
        """Failure of the ref arg of the n_state_model.ref_domain() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.ref_domain, ref=data[1])


    def test_select_model_argfail_model(self):
        """Failure of the model arg of the n_state_model.select_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.n_state_model_fns.select_model, model=data[1])
