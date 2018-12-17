###############################################################################
#                                                                             #
# Copyright (C) 2003-2015 Edward d'Auvergne                                   #
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
"""Logarithmic barrier function optimization constraint algorithm.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from math import log
from numpy import dot, float64, inf, outer, sqrt, zeros
from re import match

# Minfx module imports.
from minfx.base_classes import print_iter, Min
from minfx.constraint_linear import Constraint_linear


def log_barrier_function(func=None, dfunc=None, d2func=None, args=(), x0=None, min_options=(), A=None, b=None, epsilon0=1e-5, scale_epsilon=1e-2, func_tol=1e-25, grad_tol=None, maxiter=1e6, inner_maxiter=500, full_output=0, print_flag=0):
    """The logarithmic barrier augmented function.

    From U{http://en.wikipedia.org/wiki/Barrier_function} and U{http://bayen.eecs.berkeley.edu/bayen/?q=webfm_send/247}.  This is an augmented function, the algorithm is:

        - Given starting points x0s.
        - while 1:
            - Find an approximate minimiser xk of the target function value plus the logarithmic barrier function value.
            - Final convergence test.
            - Scale the penalty function scaling factor epsilon.
            - k = k + 1.


    Linear constraints
    ==================

    These are defined as::

        A.x >= b

    where:

        - A is an m*n matrix where the rows are the transposed vectors, ai, of length n.  The elements of ai are the coefficients of the model parameters.
        - x is the vector of model parameters of dimension n.
        - b is the vector of scalars of dimension m.
        - m is the number of constraints.
        - n is the number of model parameters.

    E.g. if 0 <= q <= 1, q >= 1 - 2r, and 0 <= r, then::

        | 1  0 |            |  0 |
        |      |            |    |
        |-1  0 |   | q |    | -1 |
        |      | . |   | >= |    |
        | 1  2 |   | r |    |  1 |
        |      |            |    |
        | 0  1 |            |  2 |

    To use linear constraints both the matrix A and vector b need to be supplied.


    Initial values
    ==============

    These are the default initial values::

        epsilon0 = 1e-5
        scale_epsilon = 1e-2
    """

    if print_flag:
        print("\n")
        print("Logarithmic barrier function")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    min = Log_barrier_function(func, dfunc, d2func, args, x0, min_options, A, b, epsilon0, scale_epsilon, func_tol, grad_tol, maxiter, inner_maxiter, full_output, print_flag)
    if min.init_failure:
        return None
    results = min.minimise()
    return results



class Log_barrier_function(Min):
    def __init__(self, func, dfunc, d2func, args, x0, min_options, A, b, epsilon0, scale_epsilon, func_tol, grad_tol, maxiter, inner_maxiter, full_output, print_flag):
        """Class for logarithmic barrier function minimisation specific functions.

        Unless you know what you are doing, you should call the function 'log_barrier_function' rather than using this class.
        """

        # Import the 'generic_minimise' function from 'generic.py'.  It is important that
        # this import statment occurs here otherwise a recursive import between the module
        # 'generic' and this module occurs.  This means that the function 'generic_minimise'
        # has not been initialised and is therefore not in the namespace.
        from minfx.generic import generic_minimise
        self.generic_minimise = generic_minimise

        # Linear constraints.
        if A is not None and b is not None:
            self.A = A
            self.b = b
            constraint_linear = Constraint_linear(self.A, self.b)
            self.c = constraint_linear.func
            self.dc = constraint_linear.dfunc
            self.d2c = None
            self.m = len(self.b)
            if print_flag >= 2:
                print("Linear constraint matrices.")
                print("A:\n" + repr(self.A))
                print("b:\n" + repr(self.b))

        # Incorrectly supplied constraints.
        else:
            print("The constraints have been incorrectly supplied.")
            self.init_failure = 1
            return

        # min_options.
        if len(min_options) == 0:
            print("The unconstrained minimisation algorithm has not been specified.")
            self.init_failure = 1
            return
        self.min_algor = min_options[0]
        self.min_options = min_options[1:]

        # Function arguments.
        self.args = args
        self.func = func
        self.dfunc = dfunc
        self.d2func = d2func
        self.xk = x0
        self.epsilon = epsilon0
        self.scale_epsilon = scale_epsilon
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.maxiter = maxiter
        self.inner_maxiter = inner_maxiter
        self.full_output = full_output
        self.print_flag = print_flag

        # Set the print_prefix to nothing.
        self.print_prefix = ""

        # Initialisation failure flag.
        self.init_failure = 0

        # Initialise the function, gradient, and Hessian evaluation counters.
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Initialise the warning string.
        self.warning = None

        # Initialise data structures.
        self.test_str = zeros(self.m)
        self.f_log = self.func_log(*(self.xk,)+self.args)

        # Set the convergence test function.
        self.setup_conv_tests()


    def func_log(self, *args):
        """The logarithmic barrier function.

        The equation is::

                      /  sum_i=1^m -log(bi - AiT.x)    for Ax < b,
            psi(x) = <
                      \  +inf                          otherwise.
        """

        # Calculate the function and constraint values.
        self.fk = f_log = self.func(*(args[0],)+args[1:])
        self.ck = self.c(*(args[0],))

        # Calculate the logarithmic penalty function.
        for i in range(self.m):
            if self.ck[i] > 0:
                f_log += - self.epsilon * log(self.ck[i])
                self.test_str[i] = 1
            else:
                f_log = inf
                self.test_str[i] = 0

        if self.print_flag >= 4:
            print("")
            print("\tfunction value:       " + repr(self.fk))

        return f_log


    def func_dlog(self, *args):
        """The logarithmic barrier gradient."""

        # Calculate the function and constraint gradients.
        dfk = dpsi = self.dfunc(*(args[0],)+args[1:])
        self.dck = self.dc(*(args[0],))

        # Calculate the log-barrier gradient.
        for i in range(self.m):
            if self.test_str[i]:
                dpsi -= self.epsilon / self.ck[i] * self.dck[i]

        # Printout.
        if self.print_flag >= 4:
            print("")
            print("\tlog-barrier grad:    " + repr(dpsi))
            print("\tfunction grad:       " + repr(dfk))
            print("\tdck:                 " + repr(self.dck))
            print("\tTest structure:      " + repr(self.test_str))

        # Return the modified gradient.
        return dpsi


    def func_d2log(self, *args):
        """The logarithmic barrier Hessian."""

        # Calculate the function and constraint Hessians.
        d2psi = self.d2func(*(args[0],)+args[1:])
        self.d2ck = self.d2c(*(args[0],))

        # Calculate the log-barrier Hessian.
        for i in range(self.m):
            if self.test_str[i]:
                d2psi -= self.epsilon / self.ck[i] * self.d2ck[i]  +  self.epsilon / self.ck[i]**2 * outer(self.dck[i], self.dck[i])

        return d2psi


    def minimise(self):
        """Logarithmic barrier optimisation."""

        # Start the iteration counters.
        self.k = 0
        self.j = 0

        # Sub-algorithm printout.
        sub_print_flag = self.print_flag
        if sub_print_flag >= 2:
            sub_print_flag = sub_print_flag - 1

        # Iterate until the local minima is found.
        while True:
            # Print out.
            if self.print_flag:
                print_iter(self.k, self.xk, self.fk)
                print("Entering sub-algorithm.")

            # Maximum number of iterations for the sub-loop.
            if self.maxiter - self.j < self.inner_maxiter:
                maxiter = self.maxiter - self.j
            else:
                maxiter = self.inner_maxiter

            # Normal minimisation but using the modified target functions.
            results = self.generic_minimise(func=self.func_log, dfunc=self.func_dlog, d2func=self.func_d2log, args=self.args, x0=self.xk, min_algor=self.min_algor, min_options=self.min_options, func_tol=self.func_tol, grad_tol=self.grad_tol, maxiter=maxiter, full_output=1, print_flag=self.print_flag, print_prefix="\t")
            if results == None:
                return

            # Unpack and sort the results.
            self.xk_new, self.f_log_new, j, f, g, h, self.temp_warning = results
            self.j, self.f_count, self.g_count, self.h_count = self.j + j, self.f_count + f, self.g_count + g, self.h_count + h

            # Maximum number of iteration test.
            if self.j >= self.maxiter - 1:
                self.warning = "Maximum number of iterations reached"
                break

            # Convergence test.
            if self.conv_test(self.f_log_new, self.f_log):
                break

            # Infinite function value.
            if self.f_log_new == inf:
                self.warning = "Infinite function value encountered, can no longer perform optimisation."
                break

            # Update epsilon.
            self.epsilon = self.scale_epsilon * self.epsilon

            # Iteration counter update.
            self.xk = self.xk_new * 1.0
            self.f_log = self.f_log_new
            self.k = self.k + 1

        # Return.
        if self.full_output:
            try:
                self.fk = self.func(*(self.xk_new,)+self.args)
                return self.xk_new, self.fk, self.j, self.f_count, self.g_count, self.h_count, self.warning
            except AttributeError:
                self.fk = self.func(*(self.xk,)+self.args)
                return self.xk, self.fk, self.j, self.f_count, self.g_count, self.h_count, self.warning
        else:
            try:
                return self.xk_new
            except AttributeError:
                return self.xk
