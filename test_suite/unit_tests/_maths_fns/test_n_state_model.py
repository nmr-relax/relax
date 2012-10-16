###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
from math import pi
from numpy import array, float64, ones
from unittest import TestCase

# relax module imports.
from maths_fns.n_state_model import N_state_opt


class Test_n_state_model(TestCase):
    """Unit tests for the maths_fns.n_state_model relax module."""

    def test_func1(self):
        """Unit test 1 of the func() method.

        The number of states is 2 and the number of tensors is 3.  All states are equi-probable with
        Euler rotations of {0, 0, 0}, hence the reduced tensors should be the same size as the full
        tensors.  The target function is designed to be zero.
        """

        # Init vals.
        N = 2
        init_params = array([0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float64)
        full_tensors = array([1.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0, 1.0, 0.0], float64)
        red_data     = array([1.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0, 1.0, 0.0], float64)
        err = ones(3*5, float64)
        full_in_ref_frame = [1, 1, 1]

        # Set up the class.
        model = N_state_opt(model='2-domain', N=2, init_params=init_params, full_tensors=full_tensors, red_data=red_data, red_errors=err, full_in_ref_frame=full_in_ref_frame)

        # Call the target function 3 times.
        for i in range(3):
            # Target function.
            chi2 = model.func_2domain(init_params)

            # Test that the chi2 value is zero each time!
            self.assertEqual(chi2, 0.0)


    def test_func2(self):
        """Unit test 2 of the func() method.

        The number of states is 2 and the number of tensors is 3.  All states are equi-probable with
        Euler rotations of {0, 0, 0}, hence the reduced tensors should be the same size as the full
        tensors.  The target function is designed to be one.
        """

        # Init vals.
        N = 2
        init_params = array([0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], float64)
        full_tensors = array([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0], float64)
        red_data     = array([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0], float64)
        err = ones(3*5, float64)
        full_in_ref_frame = [1, 1, 1]

        # Set up the class.
        model = N_state_opt(model='2-domain', N=2, init_params=init_params, full_tensors=full_tensors, red_data=red_data, red_errors=err, full_in_ref_frame=full_in_ref_frame)

        # Call the target function 3 times.
        for i in range(3):
            # Target function.
            chi2 = model.func_2domain(init_params)

            # Test that the chi2 value is zero each time!
            self.assertEqual(chi2, 1.0)


    def test_func3(self):
        """Unit test 3 of the func() method.

        The number of states is 2 and the number of tensors is 3.  The first state has a prob of 1.0
        with Euler rotations of {90, 0, 0}, hence the reduced tensors should be the same size as the full
        tensors but rotated by 90 degrees.  The target function is designed to be zero.
        """

        # Init vals.
        N = 2
        init_params = array([1.0, -pi/2.0, 0.0, 0.0, 0.0, 0.0, 0.0], float64)
        full_tensors = array([1.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0, 1.0, 0.0], float64)
        red_data     = array([0.5, 1.0, 0.0, 0.0, 0.0, 0.5, 1.0, -1.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0, 1.0], float64)
        err = ones(3*5, float64)
        full_in_ref_frame = [1, 1, 1]

        # Set up the class.
        model = N_state_opt(model='2-domain', N=2, init_params=init_params, full_tensors=full_tensors, red_data=red_data, red_errors=err, full_in_ref_frame=full_in_ref_frame)

        # Call the target function 3 times.
        for i in range(3):
            # Target function.
            chi2 = model.func_2domain(init_params)

            # Test that the chi2 value is zero each time!
            self.assertAlmostEqual(chi2, 0.0)


    def test_func4(self):
        """Unit test 4 of the func() method.

        The number of states is 2 and the number of tensors is 3.  All states are equi-probable with
        Euler rotations of {90, 0, 0} for only the first.  The target function is designed to be
        zero.
        """

        # Init vals.
        N = 2
        init_params = array([0.5, -pi/2.0, 0.0, 0.0, 0.0, 0.0, 0.0], float64)
        full_tensors = array([1.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0, 1.0, 0.0], float64)
        red_data     = array([0.75, 0.75, 0.0, 0.0, 0.0, 0.75, 0.75, 0.0, 0.0, 0.0, 0.75, 0.75, 0.0, 0.5, 0.5], float64)
        err = ones(3*5, float64)
        full_in_ref_frame = [1, 1, 1]

        # Set up the class.
        model = N_state_opt(model='2-domain', N=2, init_params=init_params, full_tensors=full_tensors, red_data=red_data, red_errors=err, full_in_ref_frame=full_in_ref_frame)

        # Call the target function 3 times.
        for i in range(3):
            # Target function.
            chi2 = model.func_2domain(init_params)

            # Test that the chi2 value is zero each time!
            self.assertAlmostEqual(chi2, 0.0)



