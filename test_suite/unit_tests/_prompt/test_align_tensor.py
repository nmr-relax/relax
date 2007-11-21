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
import sys

# relax module imports.
from data_types import return_data_types
from prompt.align_tensor import Align_tensor
from relax_errors import RelaxBinError, RelaxIntError, RelaxListFloatError
from test_suite.unit_tests.align_tensor_testing_base import Align_tensor_base_class

# Set the variable sys.ps3 (this is required by the user functions).
sys.ps3 = 'relax> '


# A class to act as a container.
class Container:
    pass

# Fake normal relax usage of the user function class.
relax = Container()
relax.interpreter = Container()
relax.interpreter.intro = True


class Test_align_tensor(Align_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.align_tensor' module."""

    # Instantiate the user function class.
    align_tensor_fns = Align_tensor(relax)


    def test_init_argfail_params(self):
        """Test the proper failure of the align_tensor.init() user function for the params argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the float list arguments, and skip them.
            if data[0] == 'float list':
                continue

            # The argument test.
            self.assertRaises(RelaxListFloatError, self.align_tensor_fns.init, params=data[1])


    def test_init_argfail_param_types(self):
        """The proper failure of the align_tensor.init() user function for the param_types argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.align_tensor_fns.init, param_types=data[1])


    def test_init_argfail_errors(self):
        """The proper failure of the align_tensor.init() user function for the errors argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.align_tensor_fns.init, errors=data[1])



