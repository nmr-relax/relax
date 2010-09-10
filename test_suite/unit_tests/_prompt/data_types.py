###############################################################################
#                                                                             #
# Copyright (C) 2007-2009 Edward d'Auvergne                                   #
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
from numpy import int8, int16, int32, int64, float32, float64, zeros
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


# Binaries.
DATA_TYPES.append(['bin', 0])
DATA_TYPES.append(['bin', 1])

# Booleans.
DATA_TYPES.append(['bool', True])
DATA_TYPES.append(['bool', False])

# Class objects.
DATA_TYPES.append(['class obj', Container()])

# Classes.
DATA_TYPES.append(['class', Container])

# Dictionaries.
DATA_TYPES.append(['dict', {}])
DATA_TYPES.append(['dict', {'a': 0, 'b': 1}])

# Integers.
DATA_TYPES.append(['int', 2])
DATA_TYPES.append(['int', 10])
DATA_TYPES.append(['int', -10])

# Numpy ints.
DATA_TYPES.append(['int', zeros(2, int8)[0]])
DATA_TYPES.append(['int', zeros(2, int16)[0]])
DATA_TYPES.append(['int', zeros(2, int32)[0]])
DATA_TYPES.append(['int', zeros(2, int64)[0]])

# File descriptor.
DATA_TYPES.append(['file', tmpfile()])

# Floats.
DATA_TYPES.append(['float', 0.0])
DATA_TYPES.append(['float', 1e-7])
DATA_TYPES.append(['float', 1000000.0])

# Numpy floats.
DATA_TYPES.append(['float', zeros(2, float32)[0]])
DATA_TYPES.append(['float', zeros(2, float64)[0]])

# Functions.
DATA_TYPES.append(['function', dummy_fn])
DATA_TYPES.append(['function', dummy_fn2])

# Lists.
DATA_TYPES.append(['list', []])
DATA_TYPES.append(['none list', [None, None]])

# List of integers.
DATA_TYPES.append(['int list', [-1, 0, 1]])
DATA_TYPES.append(['int list', [zeros(2, int32)[0]]])

# List of floats.
DATA_TYPES.append(['float list', [-1., 0., 1.]])
DATA_TYPES.append(['float list', [zeros(2, float64)[0]]])

# List of numbers.
DATA_TYPES.append(['number list', [-1., 0, 1.]])

# Lists of strings.
DATA_TYPES.append(['str list', ['a']])
DATA_TYPES.append(['str list', ['a', 'asldfjk']])

# None.
DATA_TYPES.append(['None', None])

# Strings.
DATA_TYPES.append(['str', 'a'])
DATA_TYPES.append(['str', '10'])

# Tuple.
DATA_TYPES.append(['tuple', (None, None)])

# Tuples of floats.
DATA_TYPES.append(['float tuple', (0.0,)])
DATA_TYPES.append(['float tuple', (0.0, 0.0)])
DATA_TYPES.append(['float tuple', (0.0, 0.0, 0.0)])
DATA_TYPES.append(['float tuple', (0.0, 0.0, 0.0, 0.0)])
DATA_TYPES.append(['float tuple', (0.0, 0.0, 0.0, 0.0, 0.0)])
DATA_TYPES.append(['float tuple', (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)])
DATA_TYPES.append(['float tuple', (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)])

# Tuples of strings.
DATA_TYPES.append(['str tuple', ('a',)])
DATA_TYPES.append(['str tuple', ('a', 'b')])
DATA_TYPES.append(['str tuple', ('a', 'b', 'c')])
