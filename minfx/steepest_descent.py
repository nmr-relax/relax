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
"""Steepest descent (SD) optimization.

This file is part of the minfx optimisation library at U{https://gna.org/projects/minfx}.
"""

# Python module imports.
from numpy import dot

# Minfx module imports.
from minfx.base_classes import Line_search, Min


def steepest_descent(func=None, dfunc=None, args=(), x0=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, a0=1.0, mu=0.0001, eta=0.1, full_output=0, print_flag=0, print_prefix=""):
    """Steepest descent minimisation."""

    if print_flag:
        if print_flag >= 2:
            print(print_prefix)
        print(print_prefix)
        print(print_prefix + "Steepest descent minimisation")
        print(print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    min = Steepest_descent(func, dfunc, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix)
    if min.init_failure:
        print(print_prefix + "Initialisation of minimisation has failed.")
        return None
    results = min.minimise()
    return results


class Steepest_descent(Line_search, Min):
    def __init__(self, func, dfunc, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix):
        """Class for steepest descent minimisation specific functions.

        Unless you know what you are doing, you should call the function 'steepest_descent' rather than using this class.
        """

        # Function arguments.
        self.func = func
        self.dfunc = dfunc
        self.args = args
        self.xk = x0
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.maxiter = maxiter
        self.full_output = full_output
        self.print_flag = print_flag
        self.print_prefix = print_prefix

        # Set a0.
        self.a0 = a0

        # Line search constants for the Wolfe conditions.
        self.mu = mu
        self.eta = eta

        # Initialisation failure flag.
        self.init_failure = 0

        # Setup the line search options and algorithm.
        self.line_search_options(min_options)
        self.setup_line_search()

        # Initialise the function, gradient, and Hessian evaluation counters.
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Initialise the warning string.
        self.warning = None

        # Set the convergence test function.
        self.setup_conv_tests()

        # Calculate the function value and gradient vector.
        self.fk, self.f_count = self.func(*(self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = self.dfunc(*(self.xk,)+self.args), self.g_count + 1


    def new_param_func(self):
        """The new parameter function.

        Find the search direction, do a line search, and get xk+1 and fk+1.
        """

        # Calculate the steepest descent direction.
        self.pk = -self.dfk

        # Update a0 using information about the last iteration.
        try:
            self.a0 = self.alpha * dot(self.dfk_last, -self.dfk_last) / dot(self.dfk, -self.dfk)
        except AttributeError:
            "First iteration."
            pass

        # Line search.
        self.line_search()

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.alpha * self.pk
        self.fk_new, self.f_count = self.func(*(self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = self.dfunc(*(self.xk_new,)+self.args), self.g_count + 1


    def update(self):
        """Function to update the function value, gradient vector, and Hessian matrix."""

        # Store old data.
        self.fk_last = self.fk
        self.dfk_last = self.dfk * 1.0

        # Shift k+1 data to k.
        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
