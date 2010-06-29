###############################################################################
#                                                                             #
# Copyright (C) 2007, 2010 Edward d'Auvergne                                  #
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
from numpy import array, float64, zeros
from unittest import TestCase

# relax module imports.
from maths_fns.chi2 import *


class Test_chi2(TestCase):
    """Unit tests for the maths_fns.chi2 relax module."""

    def setUp(self):
        """Create a number of objects for the calculation and testing of the chi-squared equations."""

        # Some test data.
        self.data = array([1.0, 1.5, 2.0, 2.5, 3.0], float64)

        # Some 'back calculated' data.
        self.back_calc = array([0.9, 1.45, 2.0, 2.55, 3.1], float64)

        # A 'back calculated' gradient.
        self.back_calc_grad = array([[ 0.1,  0.2, 0.3, 0.2, 0.1],
                                     [-0.2, -0.1, 0.0, 0.1, 0.2]], float64)

        # A 'back calculated' Hessian.
        self.back_calc_hess = array([[[0.01, 0.005, 0.0, 0.005, 0.01],
                                      [0.05, 0.01,  0.0, 0.01,  0.05]],
                                     [[0.001, 0.0005, 0.0, 0.0005, 0.001],
                                      [0.005, 0.001,  0.0, 0.001,  0.005]]],
                                      float64)

        # Some errors.
        self.errors = array([0.1, 0.1, 0.1, 0.1, 0.1], float64)


    def tearDown(self):
        """Delete all the data structures."""

        del self.data
        del self.back_calc
        del self.back_calc_grad
        del self.back_calc_hess
        del self.errors


    def test_chi2(self):
        """Unit test for the value returned by the chi2 function.

        The chi-squared value is 2.5 for the following data::

            data =      | 1.0  1.5  2.0  2.5  3.0 |,

            back_calc = | 0.9  1.45 2.0  2.55 3.1 |,

            errors =    | 0.1  0.1  0.1  0.1  0.1 |.
        """

        # Get the chi-squared value.
        val = chi2(self.data, self.back_calc, self.errors)

        # Assert that the value must be 2.5.
        self.assertEqual(val, 2.5)

        # Delete the value.
        del val


    def test_dchi2(self):
        """Unit test for the chi-squared gradient created by the dchi2 function.

        The chi-squared gradient is [0, 10] for the following data::

            data =              |  1.0  1.5  2.0  2.5  3.0 |,

            back_calc =         |  0.9  1.45 2.0  2.55 3.1 |,

            back_calc_grad =    |  0.1  0.2  0.3  0.2  0.1 |
                                | -0.2 -0.1  0.0  0.1  0.2 |,

            errors =            |  0.1  0.1  0.1  0.1  0.1 |.
        """

        # Calculate the gradient elements.
        grad = zeros(2, float64)
        dchi2(grad, 2, self.data, self.back_calc, self.back_calc_grad, self.errors)

        # Assert, to a precision of 13 decimal places, that the gradient is [0, 10].
        self.assertAlmostEqual(grad[0], 0.0, places=13)
        self.assertAlmostEqual(grad[1], 10.0, places=13)

        # Delete the gradient data.
        del grad


    def test_dchi2_element(self):
        """Unit test for the chi-squared gradient created by the dchi2_element function.

        The chi-squared gradient is [0, 10] for the following data::

            data =              |  1.0  1.5  2.0  2.5  3.0 |,

            back_calc =         |  0.9  1.45 2.0  2.55 3.1 |,

            back_calc_grad =    |  0.1  0.2  0.3  0.2  0.1 |
                                | -0.2 -0.1  0.0  0.1  0.2 |,

            errors =            |  0.1  0.1  0.1  0.1  0.1 |.
        """

        # Calculate the gradient elements.
        grad0 = dchi2_element(self.data, self.back_calc, self.back_calc_grad[0], self.errors)
        grad1 = dchi2_element(self.data, self.back_calc, self.back_calc_grad[1], self.errors)

        # Assert, to a precision of 13 decimal places, that the gradient is [0, 10].
        self.assertAlmostEqual(grad0, 0.0, places=13)
        self.assertAlmostEqual(grad1, 10.0, places=13)

        # Delete the gradient data.
        del grad0, grad1


    def test_d2chi2(self):
        """Unit test for the chi-squared Hessian created by the d2chi2 function.

        For the data::

            data =              | 1.0    1.5    2.0    2.5    3.0   |,

            back_calc =         | 0.9    1.45   2.0    2.55   3.1   |,

            back_calc_grad =    | 0.1    0.2    0.3    0.2    0.1   |
                                |-0.2   -0.1    0.0    0.1    0.2   |,

            back_calc_hess[0] = | 0.01   0.005  0.0    0.005  0.01  |
                                | 0.05   0.01   0.0    0.01   0.05  |,

            back_calc_hess[1] = | 0.001  0.0005 0.0    0.0005 0.001 |
                                | 0.005  0.001  0.0    0.001  0.005 |,

            errors =            | 0.1    0.1    0.1    0.1    0.1   |,

        the chi-squared hessian is::

            Hessian = | 38.0   0.0 |
                      |  0.0  20.0 |.
        """

        # Calculate the Hessian.
        hess = zeros((2, 2), float64)
        d2chi2(hess, 2, self.data, self.back_calc, self.back_calc_grad, self.back_calc_hess, self.errors)

        # Assert, to a precision of 13 decimal places, that the Hessian is [[38.0, 0], [0, 20]].
        self.assertAlmostEqual(hess[0, 0], 38.0, places=13)
        self.assertAlmostEqual(hess[0, 1], 0.0, places=13)
        self.assertAlmostEqual(hess[1, 0], 0.0, places=13)
        self.assertAlmostEqual(hess[1, 1], 20.0, places=13)

        # Delete the Hessian data.
        del hess


    def test_d2chi2_element(self):
        """Unit test for the chi-squared Hessian created by the d2chi2_element function.

        For the data::

            data =              | 1.0    1.5    2.0    2.5    3.0   |,

            back_calc =         | 0.9    1.45   2.0    2.55   3.1   |,

            back_calc_grad =    | 0.1    0.2    0.3    0.2    0.1   |
                                |-0.2   -0.1    0.0    0.1    0.2   |,

            back_calc_hess[0] = | 0.01   0.005  0.0    0.005  0.01  |
                                | 0.05   0.01   0.0    0.01   0.05  |,

            back_calc_hess[1] = | 0.001  0.0005 0.0    0.0005 0.001 |
                                | 0.005  0.001  0.0    0.001  0.005 |,

            errors =            | 0.1    0.1    0.1    0.1    0.1   |,

        the chi-squared hessian is::

            Hessian = | 38.0   0.0 |
                      |  0.0  20.0 |.
        """

        # Calculate the Hessian elements.
        hess00 = d2chi2_element(self.data, self.back_calc, self.back_calc_grad[0], self.back_calc_grad[0], self.back_calc_hess[0, 0], self.errors)
        hess01 = d2chi2_element(self.data, self.back_calc, self.back_calc_grad[0], self.back_calc_grad[1], self.back_calc_hess[0, 1], self.errors)
        hess10 = d2chi2_element(self.data, self.back_calc, self.back_calc_grad[1], self.back_calc_grad[0], self.back_calc_hess[1, 0], self.errors)
        hess11 = d2chi2_element(self.data, self.back_calc, self.back_calc_grad[1], self.back_calc_grad[1], self.back_calc_hess[1, 1], self.errors)

        # Assert, to a precision of 13 decimal places, that the Hessian is [[38.0, 0], [0, 20]].
        self.assertAlmostEqual(hess00, 38.0, places=13)
        self.assertAlmostEqual(hess01, 0.0, places=13)
        self.assertAlmostEqual(hess10, 0.0, places=13)
        self.assertAlmostEqual(hess11, 20.0, places=13)

        # Delete the Hessian data.
        del hess00, hess01, hess10, hess11
