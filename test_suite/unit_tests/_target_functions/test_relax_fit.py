###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
from numpy import array, float64, zeros
from unittest import TestCase

# relax module imports.
from target_functions.relax_fit import setup, func, dfunc


class Test_relax_fit(TestCase):
    """Unit tests for the target_functions.relax_fit relax C module."""

    def setUp(self):
        """Create a number of objects for the calculation and testing of the relaxation curve-fitting equations."""

        # The parameter scaling.
        scaling_list = [1, 1000]

        # The parameter values at the minimum.
        self.I0 = 1000
        self.R = 1
        self.params = [self.R/scaling_list[0], self.I0/scaling_list[1]]

        # The time points.
        relax_times = [0, 1, 2, 3, 4]

        # The intensities for the above I0 and R.
        I = [1000.0, 367.879441171, 135.335283237, 49.7870683679, 18.3156388887]

        # The intensity errors.
        errors = [10, 10, 10, 10, 10]

        # Setup the C module.
        setup(num_params=2, num_times=len(relax_times), values=I, sd=errors, relax_times=relax_times, scaling_matrix=scaling_list)


    def test_func(self):
        """Unit test for the value returned by the func() function at the minimum."""

        # Get the chi-squared value.
        val = func(self.params)

        # Assert that the value must be 0.0.
        self.assertAlmostEqual(val, 0.0)


    def test_dfunc(self):
        """Unit test for the gradient returned by the dfunc() function at the minimum."""

        # Get the chi-squared gradient.
        grad = dfunc(self.params)

        # Printout.
        print("The gradient at the minimum is:\n%s" % grad)

        # Assert that the elements must be 0.0.
        self.assertAlmostEqual(grad[0], 0.0, 6)
        self.assertAlmostEqual(grad[1], 0.0, 6)
