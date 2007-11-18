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



class Container:
    """A class to act as a container."""

    pass


def dummy_fn():
    """A dummy function for testing data types."""

    pass

def dummy_fn2():
    """A second dummy function for testing data types."""

    return "Hello"


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

    # Classes.
    data_types.append(['class', Container])

    # Class objects.
    data_types.append(['class obj', Container()])

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
