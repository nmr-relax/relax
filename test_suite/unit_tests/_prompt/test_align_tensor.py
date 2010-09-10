###############################################################################
#                                                                             #
# Copyright (C) 2007-2010 Edward d'Auvergne                                   #
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
from generic_fns import align_tensor
from prompt.align_tensor import Align_tensor
from relax_errors import RelaxError, RelaxBoolError, RelaxFloatError, RelaxIntError, RelaxNoneListStrError, RelaxNoneStrError, RelaxTupleNumError, RelaxStrError
from test_suite.unit_tests.align_tensor_testing_base import Align_tensor_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_align_tensor(Align_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.align_tensor' module."""

    # Instantiate the user function class.
    align_tensor_fns = Align_tensor()


    def test_copy_argfail_tensor_from(self):
        """Failure of the tensor_from arg of the align_tensor.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.copy, tensor_from=data[1])


    def test_copy_argfail_pipe_from(self):
        """The pipe_from arg test of the align_tensor.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.align_tensor_fns.copy, tensor_from='Pf1', pipe_from=data[1])


    def test_copy_argfail_tensor_to(self):
        """Failure of the tensor_to arg of the align_tensor.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.copy, tensor_to=data[1])


    def test_copy_argfail_pipe_to(self):
        """The pipe_to arg test of the align_tensor.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.align_tensor_fns.copy, tensor_from='Pf1', tensor_to='Pf1', pipe_to=data[1])


    def test_copy_argfail_both_pipes(self):
        """The pipe_from and pipe_to arg test of the align_tensor.copy() user function."""

        # Test that both cannot be None (the default)!
        self.assertRaises(RelaxError, self.align_tensor_fns.copy, tensor_from='Pf1', tensor_to='Pf1')


    def test_delete_argfail_tensor(self):
        """Failure of the tensor arg of the align_tensor.delete() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.align_tensor_fns.delete, tensor=data[1])


    def test_display_argfail_tensor(self):
        """Failure of the tensor arg of the align_tensor.display() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.align_tensor_fns.display, tensor=data[1])


    def test_init_argfail_tensor(self):
        """Failure of the tensor arg of the align_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.init, tensor=data[1])


    def test_init_argfail_params(self):
        """Failure of the params arg of the align_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the tuple arguments.
            if data[0] == 'tuple' or data[0] == 'float tuple' or data[0] == 'str tuple':
                # Correct tuple length.
                if len(data[1]) == 5:
                    continue

            # The argument test.
            self.assertRaises(RelaxTupleNumError, self.align_tensor_fns.init, tensor='Pf1', params=data[1])


    def test_init_argfail_scale(self):
        """The scale arg test of the align_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float argument, and skip it.
            if data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxFloatError, self.align_tensor_fns.init, tensor='Pf1', params=(0.0, 0.0, 0.0, 0.0, 0.0), scale=data[1])


    def test_init_argfail_angle_units(self):
        """The angle_units arg test of the align_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.init, params=(0.0, 0.0, 0.0, 0.0, 0.0), angle_units=data[1])


    def test_init_argfail_param_types(self):
        """The proper failure of the align_tensor.init() user function for the param_types argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.align_tensor_fns.init, tensor='Pf1', params=(0.0, 0.0, 0.0, 0.0, 0.0), param_types=data[1])


    def test_init_argfail_errors(self):
        """The errors arg test of the align_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.align_tensor_fns.init, tensor='Pf1', params=(0.0, 0.0, 0.0, 0.0, 0.0), errors=data[1])


    def test_matrix_angles_argfail_basis_set(self):
        """The proper failure of the align_tensor.matrix_angles() user function for the basis_set argument."""

        # Add an alignment tensor.
        align_tensor.init('a', (0.0, 0.0, 0.0, 0.0, 0.0))

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.align_tensor_fns.matrix_angles, basis_set=data[1])


    def test_matrix_angles_argfail_basis_tensors(self):
        """The tensors arg unit test of the align_tensor.matrix_angles() user function."""

        # Add an alignment tensor.
        align_tensor.init('a', (0.0, 0.0, 0.0, 0.0, 0.0))

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str list arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneListStrError, self.align_tensor_fns.matrix_angles, tensors=data[1])


    def test_reduction_argfail_full_tensor(self):
        """Failure of the full_tensor arg of the align_tensor.reduction() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.reduction, full_tensor=data[1])


    def test_reduction_argfail_red_tensor(self):
        """Failure of the red_tensor arg of the align_tensor.reduction() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.reduction, full_tensor='test', red_tensor=data[1])

    def test_set_domain_argfail_tensor(self):
        """Failure of the tensor arg of the align_tensor.set_domain() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.set_domain, tensor=data[1])


    def test_set_domain_argfail_domain(self):
        """Failure of the domain arg of the align_tensor.set_domain() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.align_tensor_fns.set_domain, domain=data[1])


    def test_svd_argfail_basis_set(self):
        """The proper failure of the align_tensor.svd() user function for the basis_set argument."""

        # Add an alignment tensor.
        align_tensor.init('a', (0.0, 0.0, 0.0, 0.0, 0.0))

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.align_tensor_fns.svd, basis_set=data[1])


    def test_svd_argfail_basis_tensors(self):
        """The tensors arg unit test of the align_tensor.svd() user function."""

        # Add an alignment tensor.
        align_tensor.init('a', (0.0, 0.0, 0.0, 0.0, 0.0))

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str list arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str list':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneListStrError, self.align_tensor_fns.svd, tensors=data[1])


