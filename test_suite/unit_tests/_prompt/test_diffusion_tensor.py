###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Python module imports.
from unittest import TestCase

# relax module imports.
from prompt.interpreter import Interpreter
from relax_errors import RelaxError, RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxNumError, RelaxNumTupleNumError, RelaxStrError
from test_suite.unit_tests.diffusion_tensor_testing_base import Diffusion_tensor_base_class

# Unit test imports.
from data_types import DATA_TYPES


class Test_diffusion_tensor(Diffusion_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.diffusion_tensor' module."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Test_diffusion_tensor, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Alias the user function class.
        self.diffusion_tensor_fns = self.interpreter.diffusion_tensor


    def test_copy_argfail_pipe_from(self):
        """The pipe_from arg test of the diffusion_tensor.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.diffusion_tensor_fns.copy, pipe_from=data[1])


    def test_copy_argfail_pipe_to(self):
        """The pipe_to arg test of the diffusion_tensor.copy() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.diffusion_tensor_fns.copy, pipe_to=data[1])


    def test_copy_argfail_both_pipes(self):
        """The pipe_from and pipe_to arg test of the diffusion_tensor.copy() user function."""

        # Test that both cannot be None (the default)!
        self.assertRaises(RelaxError, self.diffusion_tensor_fns.copy)


    def test_init_argfail_params(self):
        """The params arg test of diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch a single float, int, or bin, and skip them.
            if data[0] == 'int' or data[0] == 'bin' or data[0] == 'float':
                continue

            # Catch the tuple arguments.
            if data[0] == 'tuple' or data[0] == 'float tuple' or data[0] == 'str tuple':
                # Correct tuple length.
                if len(data[1]) == 4 or len(data[1]) == 6:
                    continue

            # The argument test.
            self.assertRaises(RelaxNumTupleNumError, self.diffusion_tensor_fns.init, params=data[1])


    def test_init_argfail_time_scale(self):
        """The time_scale arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the number arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int' or data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.diffusion_tensor_fns.init, params=1e-9, time_scale=data[1])


    def test_init_argfail_d_scale(self):
        """The d_scale arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the number arguments, and skip them.
            if data[0] == 'bin' or data[0] == 'int' or data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.diffusion_tensor_fns.init, params=1e-9, d_scale=data[1])


    def test_init_argfail_angle_units(self):
        """The angle_units arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.diffusion_tensor_fns.init, params=1e-9, angle_units=data[1])


    def test_init_argfail_param_types(self):
        """The param_types arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.diffusion_tensor_fns.init, params=1e-9, param_types=data[1])


    def test_init_argfail_spheroid_type(self):
        """The spheroid_type arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.diffusion_tensor_fns.init, params=1e-9, spheroid_type=data[1])


    def test_init_argfail_fixed(self):
        """The fixed arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bool arguments, and skip them.
            if data[0] == 'bool':
                continue

            # The argument test.
            self.assertRaises(RelaxBoolError, self.diffusion_tensor_fns.init, params=1e-9, fixed=data[1])
