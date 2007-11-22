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
from os import tmpfile


class Container:
    """A class to act as a container."""

    pass


def dummy_fn():
    """A dummy function for testing data types."""

    pass

def dummy_fn2():
    """A second dummy function for testing data types."""

    return "Hello"


# Create the array.
DATA_TYPES = []
"""An array of many different Python objects for testing the correct behaviour of user function args."""


# None.
DATA_TYPES.append(['None', None])

# Integers.
DATA_TYPES.append(['int', 2])
DATA_TYPES.append(['int', 10])
DATA_TYPES.append(['int', -10])

# Binaries.
DATA_TYPES.append(['bin', 0])
DATA_TYPES.append(['bin', 1])

# File descriptor.
DATA_TYPES.append(['file', tmpfile()])

# Floats.
DATA_TYPES.append(['float', 0.0])
DATA_TYPES.append(['float', 1e-7])
DATA_TYPES.append(['float', 1000000.0])

# Functions.
DATA_TYPES.append(['function', dummy_fn])
DATA_TYPES.append(['function', dummy_fn2])

# Classes.
DATA_TYPES.append(['class', Container])

# Class objects.
DATA_TYPES.append(['class obj', Container()])

# Strings.
DATA_TYPES.append(['str', 'a'])
DATA_TYPES.append(['str', '10'])

# Booleans.
DATA_TYPES.append(['bool', True])
DATA_TYPES.append(['bool', False])

# List.
DATA_TYPES.append(['list', []])
DATA_TYPES.append(['list', [None, None]])

# List of integers.
DATA_TYPES.append(['int list', [-1, 0, 1]])

# List of floats.
DATA_TYPES.append(['float list', [-1., 0., 1.]])

# List of numbers.
DATA_TYPES.append(['number list', [-1., 0, 1.]])

# List of strings.
DATA_TYPES.append(['str list', ['a']])
DATA_TYPES.append(['str list', ['a', 'asldfjk']])

# Dictionary.
DATA_TYPES.append(['dict', {}])
DATA_TYPES.append(['dict', {'a': 0, 'b': 1}])

# Tuple.
DATA_TYPES.append(['tuple', (None, None)])
