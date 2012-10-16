###############################################################################
#                                                                             #
# Copyright (C) 2006 Gary Thompson                                            #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from unittest import TestCase
from float import *
from copy import copy


# Some constants for the tests.
FLOAT_EPSILON = packBytesAsPyFloat([1, 0, 0, 0, 0, 0, 0, 0])
NEG_FLOAT_EPSILON = packBytesAsPyFloat([1, 0, 0, 0, 0, 0, 0, 128])
FLOAT_NORMAL = packBytesAsPyFloat([0, 0, 0, 0, 128, 132, 46, 65])
NEG_FLOAT_NORMAL = packBytesAsPyFloat([0, 0, 0, 0, 128, 132, 46, 193])
ZERO = packBytesAsPyFloat([0, 0, 0, 0, 0, 0, 0, 0])
NEG_ZERO = packBytesAsPyFloat([0, 0, 0, 0, 0, 0, 0, 128])


def make_dict_by_id(elements):
    """Convert the list into a dictionary of pointer:value pairs."""

    # Convert.
    result = {}
    for element in elements:
        result[id(element)] = element

    # Return the dictionary.
    return result


def winnow_dist_to_list_by_id(dict, exclude):
    """Generate a list of values in dict excluding the values given."""

    # Generate a new dictionary with the excluded values missing.
    resultDict = copy(dict)
    for val in exclude:
        del(resultDict[id(val)])

    # Return as a list.
    return list(resultDict.values())


class Test_float(TestCase):
    """Unit tests for the functions of the 'float' module."""

    # A dictionary of all numerical types (the key is the memory address, i.e. this is like a pointer).
    num_types = make_dict_by_id([pos_inf, neg_inf, FLOAT_NORMAL, NEG_FLOAT_NORMAL, FLOAT_EPSILON, NEG_FLOAT_EPSILON, nan, ZERO, NEG_ZERO])

    def do_test_sets(self, function, true_class=[], false_class=[]):
        """Method for checking all the values against the given function."""

        # The numbers that should return true.
        for val in true_class:
            self.assertEqual(function(val), True)

        # The numbers that should return false.
        for val in false_class:
            self.assertEqual(function(val), False)


    def test_getFloatClass(self):
        """Test the float.getFloatClass() function."""

        tests = (CLASS_POS_INF,        pos_inf,
                 CLASS_NEG_INF,        neg_inf,
                 CLASS_POS_NORMAL,     FLOAT_NORMAL,
                 CLASS_NEG_NORMAL,     -FLOAT_NORMAL,
                 CLASS_POS_DENORMAL,   FLOAT_EPSILON,
                 CLASS_NEG_DENORMAL,   -FLOAT_EPSILON,
                 CLASS_QUIET_NAN,      nan,
                 # WE DON'T USE SIGNAL NANS CLASS_SIGNAL_NAN,
                 CLASS_POS_ZERO,       ZERO,
                 CLASS_NEG_ZERO,       -ZERO
        )

        i = iter(tests)
        for (fpClass, value) in zip(i, i):
            self.assertEqual(fpClass, getFloatClass(value))


    def test_isPositive(self):
        """Test the float.isZero() function."""

        # Negative values.
        negatives = (neg_inf, NEG_FLOAT_NORMAL, NEG_FLOAT_EPSILON, NEG_ZERO)

        # Positive values.
        positives = winnow_dist_to_list_by_id(self.num_types, negatives)

        # Run the tests.
        self.do_test_sets(isPositive, true_class=positives, false_class=negatives)


    def test_isZero(self):
        """Test the float.isZero() function."""

        # The zeros.
        zeros = (ZERO, NEG_ZERO)

        # All other numbers.
        non_zeros = winnow_dist_to_list_by_id(self.num_types, zeros)

        # Run the tests.
        self.do_test_sets(isZero, true_class=zeros, false_class=non_zeros)
