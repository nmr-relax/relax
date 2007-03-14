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
from Numeric import Float64, array
from unittest import TestCase

# relax module imports.
from maths_fns.chi2 import *


class Test_chi2(TestCase):
    """Unit tests for the maths_fns.chi2 relax module."""

    def setUp(self):
        """Create a number of objects for the calculation and testing of the chi-squared equations."""

        # Some test data.
        self.data = array([1.0, 1.5, 2.0, 2.5, 3.0], Float64)

        # Some 'back calculated' data.
        self.back_calc = array([0.9, 1.45, 2.0, 2.55, 3.1], Float64)

        # A 'back calculated' gradient.
        self.back_calc_grad = array([[ 0.1,  0.2, 0.3, 0.2, 0.1],
                                     [-0.2, -0.1, 0.0, 0.1, 0.2]], Float64)

        # Some errors.
        self.errors = array([0.1, 0.1, 0.1, 0.1, 0.1], Float64)


    def tearDown(self):
        """Delete all the data structures."""

        del self.data
        del self.back_calc
        del self.back_calc_grad
        del self.errors


    def test_chi2(self):
        """Unit test for the value returned by the chi2 function.

        For the following data, the chi-squared value is 2.5

            data =      [1.0, 1.5,  2.0, 2.5,  3.0],

            back_calc = [0.9, 1.45, 2.0, 2.55, 3.1],

            errors =    [0.1, 0.1,  0.1, 0.1,  0.1].
        """

        # Get the chi-squared value.
        val = chi2(self.data, self.back_calc, self.errors)

        # Assert that the value must be 2.5.
        self.assertEqual(val, 2.5)


    def test_dchi2(self):
        """Unit test for the chi-squared gradient created by the dchi2 function.

        The chi-squared gradient is [0, 10] for the following data

            data =              [1.0, 1.5,  2.0, 2.5,  3.0],

            back_calc =         [0.9, 1.45, 2.0, 2.55, 3.1],

            back_calc_grad =    | 0.1,  0.2, 0.3, 0.2, 0.1|
                                |-0.2, -0.1, 0.0, 0.1, 0.2|,

            errors =            [0.1, 0.1,  0.1, 0.1,  0.1],
        """

        # Initial gradient.
        grad = [None, None]

        # Calculate the gradient elements.
        grad[0] = dchi2(self.data, self.back_calc, self.back_calc_grad[0], self.errors)
        grad[1] = dchi2(self.data, self.back_calc, self.back_calc_grad[1], self.errors)

        # Assert, to a precision of 13 decimal places, that the gradient is [0, 10].
        self.assertAlmostEqual(grad[0], 0.0, places=13)
        self.assertAlmostEqual(grad[1], 10.0, places=13)
