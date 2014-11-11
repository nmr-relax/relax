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
from numpy import array, float64, transpose, zeros
from unittest import TestCase

# relax module imports.
from dep_check import C_module_exp_fn
from status import Status; status = Status()
if C_module_exp_fn:
    from target_functions.relax_fit import setup, func, dfunc, d2func, jacobian, jacobian_chi2


class Test_relax_fit(TestCase):
    """Unit tests for the target_functions.relax_fit relax C module."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the C modules are non-functional.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Test_relax_fit, self).__init__(methodName)

        # Missing module.
        if not C_module_exp_fn:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Relax curve-fitting C module', 'unit'])


    def setUp(self):
        """Create a number of objects for the calculation and testing of the relaxation curve-fitting equations."""

        # The parameter scaling.
        self.scaling_list = [1.0, 1000.0]

        # The parameter values at the minimum.
        self.I0 = 1000.0
        self.R = 1.0
        self.params = [self.R/self.scaling_list[0], self.I0/self.scaling_list[1]]

        # The time points.
        relax_times = [0.0, 1.0, 2.0, 3.0, 4.0]

        # The intensities for the above I0 and R.
        I = [1000.0, 367.879441171, 135.335283237, 49.7870683679, 18.3156388887]

        # The intensity errors.
        errors = [10.0, 10.0, 10.0, 10.0, 10.0]

        # Setup the C module.
        setup(num_params=2, num_times=len(relax_times), values=I, sd=errors, relax_times=relax_times, scaling_matrix=self.scaling_list)


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


    def test_dfunc_off_minimum(self):
        """Unit test for the gradient returned by the dfunc() function at a position away from the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/integrate.log.
        """

        # The off-minimum parameter values.
        I0 = 500.0
        R = 2.0
        params = [R/self.scaling_list[0], I0/self.scaling_list[1]]

        # Get the chi-squared gradient.
        grad = dfunc(params)

        # Printout.
        print("The gradient at %s is:\n    %s" % (params, grad))

        # Check that the gradient matches the numerically derived values.
        self.assertAlmostEqual(grad[0], 456.36655522098829*self.scaling_list[0], 3)
        self.assertAlmostEqual(grad[1], -10.8613338920982*self.scaling_list[1], 3)


    def test_d2func(self):
        """Unit test for the Hessian returned by the d2func() function at the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/Hessian.log.
        """

        # Get the chi-squared Hessian.
        hess = d2func(self.params)

        # Printout.
        print("The Hessian at the minimum is:\n%s" % hess)

        # Check that the Hessian matches the numerically derived values.
        self.assertAlmostEqual(hess[0][0],  4.72548021e+03*self.scaling_list[0]**2, 3)
        self.assertAlmostEqual(hess[0][1], -3.61489336e+00*self.scaling_list[0]*self.scaling_list[1], 3)
        self.assertAlmostEqual(hess[1][0], -3.61489336e+00*self.scaling_list[0]*self.scaling_list[1], 3)
        self.assertAlmostEqual(hess[1][1],  2.31293027e-02*self.scaling_list[1]**2, 3)


    def test_d2func_off_minimum(self):
        """Unit test for the Hessian returned by the d2func() function at a position away from the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/Hessian.log.
        """

        # The off-minimum parameter values.
        I0 = 500.0
        R = 2.0
        params = [R/self.scaling_list[0], I0/self.scaling_list[1]]

        # Get the chi-squared Hessian.
        hess = d2func(params)

        # Printout.
        print("The Hessian at %s is:\n%s" % (params, hess))

        # Check that the Hessian matches the numerically derived values.
        self.assertAlmostEqual(hess[0][0], -4.11964848e+02*self.scaling_list[0]**2, 3)
        self.assertAlmostEqual(hess[0][1],  7.22678641e-01*self.scaling_list[0]*self.scaling_list[1], 3)
        self.assertAlmostEqual(hess[1][0],  7.22678641e-01*self.scaling_list[0]*self.scaling_list[1], 3)
        self.assertAlmostEqual(hess[1][1],  2.03731472e-02*self.scaling_list[1]**2, 3)


    def test_jacobian(self):
        """Unit test for the Jacobian returned by the jacobian() function at the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/Hessian.log.
        """

        # Get the exponential curve Jacobian.
        matrix = jacobian(self.params)

        # The real Jacobian.
        real = [[  0.00000000e+00,   1.00000000e+00],
                [ -3.67879441e+02,   3.67879441e-01],
                [ -2.70670566e+02,   1.35335283e-01],
                [ -1.49361205e+02,   4.97870684e-02],
                [ -7.32625556e+01,   1.83156389e-02]]

        # Numpy conversion.
        matrix = array(matrix)
        real = transpose(array(real))

        # Printouts.
        print("The Jacobian at the minimum is:\n%s" % matrix)
        print("The real Jacobian at the minimum is:\n%s" % real)

        # Check that the Jacobian matches the numerically derived values.
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                self.assertAlmostEqual(matrix[i, j], real[i, j], 3)


    def test_jacobian_chi2(self):
        """Unit test for the Jacobian returned by the jacobian_chi2() function at the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/jacobian_chi2.log.
        """

        # Get the exponential curve Jacobian.
        matrix = jacobian_chi2(self.params)

        # The real Jacobian.
        real = [[  0.00000000e+00,   0.00000000e+00],
                [ -3.25440806e-09,   3.25446070e-12],
                [  2.09660266e-09,  -1.04831421e-12],
                [  1.07707223e-10,  -3.58994022e-14],
                [ -5.00778448e-11,   1.25201612e-14]]

        # Numpy conversion.
        matrix = array(matrix)
        real = transpose(array(real))

        # Printouts.
        print("The chi-squared Jacobian at the minimum is:\n%s" % matrix)
        print("The real chi-squared Jacobian at the minimum is:\n%s" % real)

        # Check that the Jacobian matches the numerically derived values.
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                self.assertAlmostEqual(matrix[i, j], real[i, j], 3)


    def test_jacobian_chi2_off_minimum(self):
        """Unit test for the Jacobian returned by the jacobian_chi2() function at a position away from the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/jacobian_chi2.log.
        """

        # The off-minimum parameter values.
        I0 = 500.0
        R = 2.0
        params = [R/self.scaling_list[0], I0/self.scaling_list[1]]

        # Get the exponential curve Jacobian.
        matrix = jacobian_chi2(params)

        # The real Jacobian.
        real = [[  0.00000000e+00,  -1.00000000e+01],
                [  4.06292489e+02,  -8.12584978e-01],
                [  4.62204173e+01,  -4.62204173e-02],
                [  3.61013094e+00,  -2.40675396e-03],
                [  2.43517791e-01,  -1.21758895e-04]]

        # Numpy conversion.
        matrix = array(matrix)
        real = transpose(array(real))

        # Printout.
        print("The chi-squared Jacobian at %s is:\n%s" % (params, matrix))
        print("The real chi-squared Jacobian at the minimum is:\n%s" % real)

        # Check that the Jacobian matches the numerically derived values.
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                self.assertAlmostEqual(matrix[i, j], real[i, j], 3)


    def test_jacobian_off_minimum(self):
        """Unit test for the Jacobian returned by the jacobian() function at a position away from the minimum.

        This uses the data from test_suite/shared_data/curve_fitting/numeric_gradient/Hessian.log.
        """

        # The off-minimum parameter values.
        I0 = 500.0
        R = 2.0
        params = [R/self.scaling_list[0], I0/self.scaling_list[1]]

        # Get the exponential curve Jacobian.
        matrix = jacobian(params)

        # The real Jacobian.
        real = [[  0.00000000e+00,   1.00000000e+00],
                [ -6.76676416e+01,   1.35335283e-01],
                [ -1.83156389e+01,   1.83156389e-02],
                [ -3.71812826e+00,   2.47875218e-03],
                [ -6.70925256e-01,   3.35462628e-04]]

        # Numpy conversion.
        matrix = array(matrix)
        real = transpose(array(real))

        # Printout.
        print("The Jacobian at %s is:\n%s" % (params, matrix))
        print("The real Jacobian at the minimum is:\n%s" % real)

        # Check that the Jacobian matches the numerically derived values.
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                self.assertAlmostEqual(matrix[i, j], real[i, j], 3)
