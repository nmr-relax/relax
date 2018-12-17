###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the minfx optimisation library,                        #
# https://gna.org/projects/minfx                                              #
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

# Module docstring.
"""Levenberg-Marquardt optimization.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import float64, zeros
from numpy.linalg import solve

# Minfx module imports.
from minfx.base_classes import Min


def levenberg_marquardt(chi2_func=None, dchi2_func=None, dfunc=None, errors=None, args=(), x0=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, print_flag=0, print_prefix="", full_output=False):
    """Levenberg-Marquardt minimisation.

    @keyword chi2_func:     User supplied chi-squared function which is run with the function parameters and args as options.
    @keyword chi2_func:     func
    @keyword dchi2_func:    User supplied chi-squared gradient function which is run with the function parameters and args as options.
    @keyword dchi2_func:    func
    @keyword dfunc:         User supplied function which should return a vector of partial derivatives of the function which back calculates values for the chi-squared function.
    @keyword dfunc:         func
    @keyword errors:        The experimental errors.
    @keyword errors:        numpy rank-1 array
    @keyword args:          A tuple containing the arguments to send to chi2_func and dchi2_func.
    @keyword args:          tuple
    @keyword x0:            The initial function parameter values.
    @keyword x0:            numpy rank-1 array
    @keyword func_tol:      The function tolerance value.  Once the function value between iterations decreases below this value, minimisation is terminated.
    @type func_tol:         float
    @keyword grad_tol:      The gradient tolerance value.
    @type grad_tol:         float
    @keyword maxiter:       The maximum number of iterations.
    @keyword maxiter:       int
    @keyword print_flag:    A flag specifying how much information should be printed to standard output during minimisation.  0 means no output, 1 means minimal output, and values above 1 increase the amount of output printed. 
    @type print_flag:       int
    @keyword print_prefix:  The text to add out to the front of all printouts.
    @type print_prefix:     str
    @keyword full_output:   A flag specifying what should be returned.  If full_output is False, the parameter values and chi-squared value are returned as a tuple.  If full_output is True, the parameter values, chi-squared value, number of iterations, and the warning flag are returned as a tuple.
    @keyword full_output:   bool
    """

    if print_flag:
        if print_flag >= 2:
            print(print_prefix)
        print(print_prefix)
        print(print_prefix + "Levenberg-Marquardt minimisation")
        print(print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    min = Levenberg_marquardt(chi2_func, dchi2_func, dfunc, errors, args, x0, func_tol, grad_tol, maxiter, full_output, print_flag, print_prefix)
    results = min.minimise()
    return results


class Levenberg_marquardt(Min):
    def __init__(self, chi2_func, dchi2_func, dfunc, errors, args, x0, func_tol, grad_tol, maxiter, full_output, print_flag, print_prefix):
        """Class for Levenberg-Marquardt minimisation specific functions.

        Unless you know what you are doing, you should call the function 'levenberg_marquardt' rather than using this class.
        """

        # Function arguments.
        self.chi2_func = chi2_func
        self.dchi2_func = dchi2_func
        self.dfunc = dfunc
        self.errors = errors
        self.args = args
        self.xk = x0
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.maxiter = maxiter
        self.full_output = full_output
        self.print_flag = print_flag
        self.print_prefix = print_prefix

        # Initialise the function, gradient, and Hessian evaluation counters.
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Initialise the warning string.
        self.warning = None

        # Set the convergence test function.
        self.setup_conv_tests()
        self.orig_conv_test = self.conv_test
        self.conv_test = self.test_mod

        # The initial chi-squared value, chi-squared gradient vector, and derivative function matrix.
        self.fk, self.f_count = self.chi2_func(*(self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = -0.5 * self.dchi2_func(*(self.xk,)+self.args), self.g_count + 1
        self.df = self.dfunc()
        self.dfk_new = None

        # Initial value of lambda (the Levenberg-Marquardt fudge factor).
        self.l = 0.001

        # N.
        self.n = len(self.xk)


    def create_lm_matrix(self):
        """Function to create the Levenberg-Marquardt matrix.

        The matrix is::

                           _n_
                           \   /     1        d y(xi)   d y(xi)                \ 
            LM_matrix_jk =  >  | ---------- . ------- . ------- . (1 + lambda) |
                           /__ \ sigma_i**2     dj        dk                   /
                           i=1

        where j == k is one of the function parameters, and::

                           _n_
                           \   /     1        d y(xi)   d y(xi) \ 
            LM_matrix_jk =  >  | ---------- . ------- . ------- |
                           /__ \ sigma_i**2     dj        dk    /
                           i=1

        where j != k are function parameters.
        """

        # Create the Levenberg-Marquardt matrix with elements equal to zero.
        self.lm_matrix = zeros((self.n, self.n), float64)

        # Calculate the inverse of the variance to minimise calculations.
        i_variance = 1.0 / self.errors**2

        # Loop over the error points from i=1 to n.
        for i in range(len(self.errors)):
            # Loop over all function parameters.
            for param_j in range(self.n):
                # Loop over the function parameters from the first to 'param_j' to create the Levenberg-Marquardt matrix.
                for param_k in range(param_j + 1):
                    if param_j == param_k:
                        matrix_jk = i_variance[i] * self.df[i, param_j] * self.df[i, param_k] * (1.0 + self.l)
                        self.lm_matrix[param_j, param_k] = self.lm_matrix[param_j, param_k] + matrix_jk
                    else:
                        matrix_jk = i_variance[i] * self.df[i, param_j] * self.df[i, param_k]
                        self.lm_matrix[param_j, param_k] = self.lm_matrix[param_j, param_k] + matrix_jk
                        self.lm_matrix[param_k, param_j] = self.lm_matrix[param_k, param_j] + matrix_jk


    def new_param_func(self):
        """Find the new parameter vector self.xk_new."""

        # Create the Levenberg-Marquardt matrix.
        self.create_lm_matrix()

        # Solve the Levenberg-Marquardt equation to get the vector of function parameter changes.
        #print("\nself.lm_matrix:\n" + repr(self.lm_matrix))
        #print("\nself.dfk:\n" + repr(self.dfk))
        self.pk = solve(self.lm_matrix, self.dfk)

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.pk
        self.fk_new, self.f_count = self.chi2_func(*(self.xk_new,)+self.args), self.f_count + 1

        if self.fk_new <= self.fk:
            # Move to xk+1 and shrink lambda.
            self.dfk_new, self.g_count = -0.5 * self.dchi2_func(*(self.xk_new,)+self.args), self.g_count + 1
            if self.l >= 1e-99:
                self.l = self.l * 0.1
            self.move_flag = 1
        else:
            # Don't move and increase lambda.
            if self.l <= 1e99:
                self.l = self.l * 10.0
            self.move_flag = 0

        # Print out.
        if self.print_flag >= 2:
            print(self.print_prefix + "xk_new:    " + repr(self.xk_new))
            print(self.print_prefix + "lm_matrix: " + repr(self.lm_matrix))
            print(self.print_prefix + "df:   " + repr(self.df))
            print(self.print_prefix + "l:    " + repr(self.l))
            print(self.print_prefix + "fk+1: " + repr(self.fk_new))
            print(self.print_prefix + "fk:   " + repr(self.fk))
            print(self.print_prefix + "move_flag: " + repr(self.move_flag))


    def test_mod(self, fk_new, fk, dfk_new):
        """Modified convergence test.

        This is needed to prevent the Levenberg-Marquardt minimiser from terminating if there is no movement during an iteration due to an uphill step being encountered.
        """

        if self.move_flag:
            if self.orig_conv_test(fk_new, fk, dfk_new):
                return 1


    def update(self):
        """Update function

        Update the chi-squared value, chi-squared gradient vector, and derivative function matrix.
        """

        if self.move_flag:
            self.xk = self.xk_new * 1.0
            self.fk = self.fk_new
            self.dfk = self.dfk_new * 1.0
            self.df = self.dfunc()
