###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


from Numeric import dot, sqrt

from base_classes import Trust_region, Min


def cauchy_point(func=None, dfunc=None, d2func=None, args=(), x0=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, delta_max=1e5, delta0=1.0, eta=0.2, full_output=0, print_flag=0, print_prefix=""):
    """Cauchy Point trust region algorithm.

    Page 69 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.
    The Cauchy point is defined by:

                         delta
        pCk  =  - tau_k ------- dfk
                        ||dfk||

    where:
        delta_k is the trust region radius,
        dfk is the gradient vector,

                 / 1                        if dfk . Bk . dfk <= 0
        tau_k = <
                 \ min(||dfk||**2/(delta . dfk . Bk . dfk), 1)    otherwise.
    """

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Cauchy point minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~"
    min = Cauchy_point(func, dfunc, d2func, args, x0, func_tol, grad_tol, maxiter, delta_max, delta0, eta, full_output, print_flag, print_prefix)
    results = min.minimise()
    return results


class Cauchy_point(Trust_region, Min):
    def __init__(self, func, dfunc, d2func, args, x0, func_tol, grad_tol, maxiter, delta_max, delta0, eta, full_output, print_flag, print_prefix):
        """Class for Cauchy Point trust region minimisation specific functions.

        Unless you know what you are doing, you should call the function 'cauchy_point' rather than
        using this class.
        """

        # Function arguments.
        self.func = func
        self.dfunc = dfunc
        self.d2func = d2func
        self.args = args
        self.xk = x0
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.maxiter = maxiter
        self.full_output = full_output
        self.print_flag = print_flag
        self.print_prefix = print_prefix
        self.delta_max = delta_max
        self.delta = delta0
        self.eta = eta

        # Initialise the function, gradient, and Hessian evaluation counters.
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Initialise the warning string.
        self.warning = None

        # Set the convergence test function.
        self.setup_conv_tests()

        # Initial values before the first iteration.
        self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


    def new_param_func(self):
        """Find the Cauchy point."""

        # Calculate the curvature and norm.
        curv = dot(self.dfk, dot(self.d2fk, self.dfk))
        norm_dfk = sqrt(dot(self.dfk, self.dfk))

        # tau_k.
        if curv <= 0.0:
            self.tau_k = 1.0
        else:
            self.tau_k = min(norm_dfk ** 3 / (self.delta * curv), 1.0)

        if self.print_flag >= 2:
            print self.print_prefix + "dfk . Bk . dfk: " + `curv`
            print self.print_prefix + "tau_k:          " + `self.tau_k`

        # Cauchy point.
        self.pk = - self.tau_k * self.delta * self.dfk / norm_dfk

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1


    def update(self):
        """Update function.

        Function to update the function value, gradient vector, and Hessian matrix.
        """

        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
