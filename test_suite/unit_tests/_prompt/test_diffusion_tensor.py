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

# relax module imports.
from data import Data as relax_data_store
from prompt.diffusion_tensor import Diffusion_tensor
from relax_errors import RelaxBinError, RelaxFloatError, RelaxIntError, RelaxNoneStrError, RelaxNumTupleError, RelaxStrError
from test_suite.unit_tests.diffusion_tensor_testing_base import Diffusion_tensor_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_diffusion_tensor(Diffusion_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.diffusion_tensor' module."""

    # Instantiate the user function class.
    diffusion_tensor_fns = Diffusion_tensor(fake_relax.fake_instance())


    def test_copy_argfail_pipe_from(self):
        """Proper failure of the diffusion_tensor.copy() user function for the pipe_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.diffusion_tensor_fns.copy, pipe_from=data[1])


    def test_copy_argfail_pipe_to(self):
        """Proper failure of the diffusion_tensor.copy() user function for the pipe_to argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.diffusion_tensor_fns.copy, pipe_to=data[1])


    def test_init_argfail_params(self):
        """Proper failure of the diffusion_tensor.init() user function for the params argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float list arguments, and skip them.
            if data[0] == 'float tuple':
                continue

            # The argument test.
            self.assertRaises(RelaxNumTupleError, self.diffusion_tensor_fns.init, params=data[1])


    def test_init_argfail_time_scale(self):
        """The time_scale arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float argument, and skip it.
            if data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxFloatError, self.diffusion_tensor_fns.init, params=1e-9, time_scale=data[1])


    def test_init_argfail_d_scale(self):
        """The d_scale arg test of the diffusion_tensor.init() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float argument, and skip it.
            if data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxFloatError, self.diffusion_tensor_fns.init, params=1e-9, d_scale=data[1])


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
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.diffusion_tensor_fns.init, params=1e-9, fixed=data[1])
