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
from Numeric import Float64, dot, matrixmultiply, outerproduct, sqrt, zeros

from newton import Newton
from base_classes import Min, Trust_region


def steihaug(func=None, dfunc=None, d2func=None, args=(), x0=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, epsilon=1e-8, delta_max=1e5, delta0=1.0, eta=0.2, full_output=0, print_flag=0, print_prefix=""):
    """Steihaug conjugate-gradient trust region algorithm.

    Page 75 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    The CG-Steihaug algorithm is:

    epsilon > 0
    p0 = 0, r0 = g, d0 = -r0
    if ||r0|| < epsilon:
        return p = p0
    while 1:
        if djT.B.dj <= 0:
            Find tau such that p = pj + tau.dj minimises m(p) in (4.9) and satisfies ||p|| = delta
            return p
        aj = rjT.rj / djT.B.dj
        pj+1 = pj + aj.dj
        if ||pj+1|| >= delta:
            Find tau such that p = pj + tau.dj satisfies ||p|| = delta
            return p
        rj+1 = rj + aj.B.dj
        if ||rj+1|| < epsilon.||r0||:
            return p = pj+1
        bj+1 = rj+1T.rj+1 / rjT.rj
        dj+1 = rj+1 + bj+1.dj
    """

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "CG-Steihaug minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~"
    min = Steihaug(func, dfunc, d2func, args, x0, func_tol, grad_tol, maxiter, epsilon, delta_max, delta0, eta, full_output, print_flag, print_prefix)
    results = min.minimise()
    return results


class Steihaug(Min, Trust_region, Newton):
    def __init__(self, func, dfunc, d2func, args, x0, func_tol, grad_tol, maxiter, epsilon, delta_max, delta0, eta, full_output, print_flag, print_prefix):
        """Class for Steihaug conjugate-gradient trust region minimisation specific functions.

        Unless you know what you are doing, you should call the function 'steihaug' rather than
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
        self.epsilon = epsilon
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

        # Newton setup function.
        self.setup_newton()

        # Set the update function.
        self.specific_update = self.update_newton


    def get_pk(self):
        """The CG-Steihaug algorithm."""

        # Initial values at j = 0.
        self.pj = zeros(len(self.xk), Float64)
        self.rj = self.dfk * 1.0
        self.dj = -self.dfk * 1.0
        self.B = self.d2fk * 1.0
        len_r0 = sqrt(dot(self.rj, self.rj))
        length_test = self.epsilon * len_r0

        if self.print_flag >= 2:
            print self.print_prefix + "p0: " + `self.pj`
            print self.print_prefix + "r0: " + `self.rj`
            print self.print_prefix + "d0: " + `self.dj`

        if len_r0 < self.epsilon:
            if self.print_flag >= 2:
                print self.print_prefix + "len rj < epsilon."
            return self.pj

        # Iterate over j.
        j = 0
        while 1:
            # The curvature.
            curv = dot(self.dj, dot(self.B, self.dj))
            if self.print_flag >= 2:
                print self.print_prefix + "\nIteration j = " + `j`
                print self.print_prefix + "Curv: " + `curv`

            # First test.
            if curv <= 0.0:
                tau = self.get_tau()
                if self.print_flag >= 2:
                    print self.print_prefix + "curv <= 0.0, therefore tau = " + `tau`
                return self.pj + tau * self.dj

            aj = dot(self.rj, self.rj) / curv
            self.pj_new = self.pj + aj * self.dj
            if self.print_flag >= 2:
                print self.print_prefix + "aj: " + `aj`
                print self.print_prefix + "pj+1: " + `self.pj_new`

            # Second test.
            if sqrt(dot(self.pj_new, self.pj_new)) >= self.delta:
                tau = self.get_tau()
                if self.print_flag >= 2:
                    print self.print_prefix + "sqrt(dot(self.pj_new, self.pj_new)) >= self.delta, therefore tau = " + `tau`
                return self.pj + tau * self.dj

            self.rj_new = self.rj + aj * dot(self.B, self.dj)
            if self.print_flag >= 2:
                print self.print_prefix + "rj+1: " + `self.rj_new`

            # Third test.
            if sqrt(dot(self.rj_new, self.rj_new)) < length_test:
                if self.print_flag >= 2:
                    print self.print_prefix + "sqrt(dot(self.rj_new, self.rj_new)) < length_test"
                return self.pj_new

            bj_new = dot(self.rj_new, self.rj_new) / dot(self.rj, self.rj)
            self.dj_new = -self.rj_new + bj_new * self.dj
            if self.print_flag >= 2:
                print self.print_prefix + "len rj+1: " + `sqrt(dot(self.rj_new, self.rj_new))`
                print self.print_prefix + "epsilon.||r0||: " + `length_test`
                print self.print_prefix + "bj+1: " + `bj_new`
                print self.print_prefix + "dj+1: " + `self.dj_new`

            # Update j+1 to j.
            self.pj = self.pj_new * 1.0
            self.rj = self.rj_new * 1.0
            self.dj = self.dj_new * 1.0
            #if j > 2:
            #    import sys
            #    sys.exit()
            j = j + 1


    def get_tau(self):
        """Function to find tau such that p = pj + tau.dj, and ||p|| = delta."""

        dot_pj_dj = dot(self.pj, self.dj)
        len_dj_sqrd = dot(self.dj, self.dj)

        tau = -dot_pj_dj + sqrt(dot_pj_dj**2 - len_dj_sqrd * (dot(self.pj, self.pj) - self.delta**2)) / len_dj_sqrd
        return tau


    def new_param_func(self):
        """Find the CG-Steihaug minimiser."""

        # Get the pk vector.
        self.pk = self.get_pk()

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1


    def update(self):
        """Update function.

        Run the trust region update.  If this update decides to shift xk+1 to xk, then run the
        Newton update.
        """

        self.trust_region_update()
        if self.shift_flag:
            self.specific_update()
