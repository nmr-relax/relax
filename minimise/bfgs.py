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


from Numeric import Float64, dot, identity, matrixmultiply, outerproduct

from base_classes import Line_search, Min


def bfgs(func=None, dfunc=None, args=(), x0=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, a0=1.0, mu=0.0001, eta=0.9, full_output=0, print_flag=0, print_prefix=""):
    """Quasi-Newton BFGS minimisation."""

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Quasi-Newton BFGS minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    min = Bfgs(func, dfunc, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix)
    if min.init_failure:
        print print_prefix + "Initialisation of minimisation has failed."
        return None
    results = min.minimise()
    return results


class Bfgs(Line_search, Min):
    def __init__(self, func, dfunc, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, full_output, print_flag, print_prefix):
        """Class for Quasi-Newton BFGS minimisation specific functions.

        Unless you know what you are doing, you should call the function 'bfgs' rather than using
        this class.
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

        # BFGS setup function.
        self.setup_bfgs()

        # Set the update function.
        self.update = self.update_bfgs


    def new_param_func(self):
        """The new parameter function.

        Find the search direction, do a line search, and get xk+1 and fk+1.
        """

        # Calculate the BFGS direction.
        self.pk = -matrixmultiply(self.Hk, self.dfk)

        # Line search.
        self.line_search()

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.alpha * self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

        # Debugging.
        if self.print_flag >= 2:
            print self.print_prefix + "pk:    " + `self.pk`
            print self.print_prefix + "alpha: " + `self.alpha`
            print self.print_prefix + "xk:    " + `self.xk`
            print self.print_prefix + "xk+1:  " + `self.xk_new`
            print self.print_prefix + "fk:    " + `self.fk`
            print self.print_prefix + "fk+1:  " + `self.fk_new`


    def setup_bfgs(self):
        """Setup function.

        Create the identity matrix I and calculate the function, gradient and initial BFGS inverse
        Hessian matrix.
        """

        # Set the Identity matrix I.
        self.I = identity(len(self.xk), Float64)

        # The initial BFGS function value, gradient vector, and BFGS approximation to the inverse Hessian matrix.
        self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
        self.Hk = self.I * 1.0


    def update_bfgs(self):
        """Function to update the function value, gradient vector, and the BFGS matrix."""

        # sk and yk.
        sk = self.xk_new - self.xk
        yk = self.dfk_new - self.dfk
        dot_yk_sk = dot(yk, sk)

        # rho k.
        if dot_yk_sk == 0:
            self.warning = "The BFGS matrix is indefinite.  This should not occur."
            rk = 1e99
        else:
            rk = 1.0 / dot_yk_sk

        # Preconditioning.
        if self.k == 0:
            self.Hk = dot_yk_sk / dot(yk, yk) * self.I

        self.Hk = matrixmultiply(self.I - rk*outerproduct(sk, yk), self.Hk)
        self.Hk = matrixmultiply(self.Hk, self.I - rk*outerproduct(yk, sk))
        self.Hk = self.Hk + rk*outerproduct(sk, sk)

        # Shift xk+1 data to xk.
        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
