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


from LinearAlgebra import inverse
from Numeric import Float64, dot, matrixmultiply, sqrt, zeros

from base_classes import Line_search, Min


def ncg(func=None, dfunc=None, d2func=None, args=(), x0=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, a0=1.0, mu=0.0001, eta=0.9, full_output=0, print_flag=0, print_prefix=""):
    """Line search Newton conjugate gradient algorithm.

    Page 140 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    The algorithm is:

    Given initial point x0.
    while 1:
        Compute a search direction pk by applying the CG method to Hk.pk = -gk, starting from
            x0 = 0.  Terminate when ||rk|| <= min(0.5,sqrt(||gk||)), or if negative curvature is
            encountered.
        Set xk+1 = xk + ak.pk, where ak satisfies the Wolfe, Goldstein, or Armijo backtracking
            conditions.
    """

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Newton Conjugate Gradient minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    min = Ncg(func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix)
    if min.init_failure:
        print print_prefix + "Initialisation of minimisation has failed."
        return None
    results = min.minimise()
    return results


class Ncg(Line_search, Min):
    def __init__(self, func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix):
        """Class for newton conjugate gradient  minimisation specific functions.

        Unless you know what you are doing, you should call the function 'ncg' rather than using
        this class.
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

        # Calculate the initial Newton function value, gradient vector, and Hessian matrix.
        self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


    def get_pk(self):
        """The CG algorithm."""

        # Initial values at i = 0.
        xi = zeros(len(self.xk), Float64)
        ri = self.dfk * 1.0
        pi = -ri
        dot_ri = dot(ri, ri)
        len_g = sqrt(dot_ri)
        residual_test = min(0.5 * len_g, dot_ri)
        #residual_test = min(0.5, sqrt(len_g)) * len_g

        # Debugging.
        if self.print_flag >= 2:
            print self.print_prefix + "Initial data:"
            print self.print_prefix + "\tx0: " + `xi`
            print self.print_prefix + "\tr0: " + `ri`
            print self.print_prefix + "\tp0: " + `pi`

        i = 0
        while 1:
            # Matrix product and curvature.
            Api = dot(self.d2fk, pi)
            curv = dot(pi, Api)

            # Negative curvature test.
            if curv <= 0.0:
                if i == 0:
                    if dot_ri == 0.0:
                        return xi
                    else:
                        ai = dot_ri / curv
                        return xi + ai*pi
                else:
                    return xi
            if sqrt(dot_ri) <= residual_test:
                return xi

            # Conjugate gradient part
            ai = dot_ri / curv
            xi_new = xi + ai*pi
            ri_new = ri + ai*Api
            dot_ri_new = dot(ri_new, ri_new)
            bi_new = dot_ri_new / dot_ri
            pi_new = -ri_new + bi_new*pi

            # Debugging.
            if self.print_flag >= 2:
                print ""
                print self.print_prefix + "Iteration i = " + `i`
                print self.print_prefix + "Api: " + `Api`
                print self.print_prefix + "Curv: " + `curv`
                print self.print_prefix + "ai: " + `ai`
                print self.print_prefix + "xi+1: " + `xi_new`
                print self.print_prefix + "ri+1: " + `ri_new`
                print self.print_prefix + "bi+1: " + `bi_new`
                print self.print_prefix + "pi+1: " + `pi_new`

            # Update i+1 to i.
            xi = xi_new * 1.0
            ri = ri_new * 1.0
            pi = pi_new * 1.0
            dot_ri = dot_ri_new
            i = i + 1


    def new_param_func(self):
        """The new parameter function.

        Find the search direction, do a line search, and get xk+1 and fk+1.
        """

        # Get the pk vector.
        self.pk = self.get_pk()

        # Line search.
        self.line_search()

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.alpha * self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1


    def update(self):
        """Function to update the function value, gradient vector, and Hessian matrix."""

        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
