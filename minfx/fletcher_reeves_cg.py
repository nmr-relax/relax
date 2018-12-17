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
"""Fletcher-Reeves conjugate gradient optimization.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import dot

# Minfx module imports.
from minfx.base_classes import Conjugate_gradient, Line_search, Min


def fletcher_reeves(func=None, dfunc=None, args=(), x0=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, a0=1.0, mu=0.0001, eta=0.1, full_output=0, print_flag=0, print_prefix=""):
    """Fletcher-Reeves conjugate gradient algorithm.

    Page 120 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.  The algorithm is:

        - Given x0
        - Evaluate f0 = f(x0), g0 = g(x0)
        - Set p0 = -g0, k = 0
        - while g0 != 0:
            - Compute ak and set xk+1 = xk + ak.pk
            - Evaluate gk+1
            - bk+1 = dot(gk+1, gk+1) / dot(gk, gk)
            - pk+1 = -gk+1 + bk+1.pk
            - k = k + 1
    """

    if print_flag:
        if print_flag >= 2:
            print(print_prefix)
        print(print_prefix)
        print(print_prefix + "Fletcher-Reeves conjugate gradient minimisation")
        print(print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    min = Fletcher_reeves(func, dfunc, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix)
    if min.init_failure:
        print(print_prefix + "Initialisation of minimisation has failed.")
        return None
    results = min.minimise()
    return results


class Fletcher_reeves(Conjugate_gradient, Line_search, Min):
    def __init__(self, func, dfunc, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix):
        """Class for Fletcher-Reeves conjugate gradient minimisation specific functions.

        Unless you know what you are doing, you should call the function 'fletcher_reeves' rather than using this class.
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

        # Calculate the initial function value and gradient vector.
        self.fk, self.f_count = self.func(*(self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = self.dfunc(*(self.xk,)+self.args), self.g_count + 1
        self.pk = -self.dfk
        self.dot_dfk = dot(self.dfk, self.dfk)


    def calc_bk(self):
        """Function to calculate the Fletcher-Reeves beta value."""

        # Calculate beta at k+1.
        return self.dot_dfk_new / self.dot_dfk
