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
from prompt.spin import Spin
from relax_errors import RelaxError, RelaxNoPipeError
from test_suite.unit_tests.spin_testing_base import Spin_base_class


# A class to act as a container.
class Container:
    pass

# Fake normal relax usage of the user function class.
relax = Container()
relax.interpreter = Container()
relax.interpreter.intro = True

# A dummy function for testing data types.
def dummy_fn():
    pass

# A second dummy function for testing data types.
def dummy_fn2():
    return "Hello"


class Test_spin(Spin_base_class, TestCase):
    """Unit tests for the functions of the 'generic_fns.spin' module."""

    # Instantiate the user function class.
    spin_fns = Spin(relax)


    def return_data_types(self):
        """Function for returning an array of many different Python objects.
        
        These objects are to test the correct behaviour towards the user function arguments.
        """

        # Create the array.
        data_types = []

        # None.
        data_types.append(['None', None])

        # Integers.
        data_types.append(['int', 0])
        data_types.append(['int', 10])
        data_types.append(['int', -10])

        # Binaries.
        data_types.append(['bin', 0])
        data_types.append(['bin', 1])

        # Floats.
        data_types.append(['float', 0.0])
        data_types.append(['float', 1e-7])
        data_types.append(['float', 1000000.0])

        # Functions.
        data_types.append(['function', dummy_fn])
        data_types.append(['function', dummy_fn2])

        # Strings.
        data_types.append(['str', 'a'])
        data_types.append(['str', '10'])

        # List.
        data_types.append(['list', []])
        data_types.append(['list', [None, None]])

        # List of integers.
        data_types.append(['int list', [-1, 0, 1]])

        # List of floats.
        data_types.append(['float list', [-1., 0., 1.]])

        # List of numbers.
        data_types.append(['number list', [-1., 0, 1.]])

        # List of strings.
        data_types.append(['str list', ['a']])
        data_types.append(['str list', ['a', 'asldfjk']])

        # Tuple.
        data_types.append(['tuple', (None, None)])

        # Return the data type array.
        return data_types
