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


from Numeric import Float64, add, argsort, average, sum, take, zeros

from base_classes import Min


def simplex(func=None, args=(), x0=None, func_tol=1e-25, maxiter=1e6, full_output=0, print_flag=0, print_prefix=""):
    """Downhill simplex minimisation."""

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Simplex minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~~"
    min = Simplex(func, args, x0, func_tol, maxiter, full_output, print_flag, print_prefix)
    results = min.minimise()
    return results


class Simplex(Min):
    def __init__(self, func, args, x0, func_tol, maxiter, full_output, print_flag, print_prefix):
        """Class for downhill simplex minimisation specific functions.

        Unless you know what you are doing, you should call the function 'simplex' rather than using
        this class.
        """

        # Function arguments.
        self.func = func
        self.args = args
        self.xk = x0
        self.func_tol = func_tol
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

        # Initialise some constants.
        self.n = len(self.xk)
        self.m = self.n + 1

        # Create the simplex
        self.simplex = zeros((self.m, self.n), Float64)
        self.simplex_vals = zeros(self.m, Float64)

        self.simplex[0] = self.xk * 1.0
        self.simplex_vals[0], self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1

        for i in xrange(self.n):
            j = i + 1
            self.simplex[j] = self.xk
            if self.xk[i] == 0.0:
                self.simplex[j, i] = 2.5 * 1e-4
            else:
                self.simplex[j, i] = 1.05 * self.simplex[j, i]
            self.simplex_vals[j], self.f_count = apply(self.func, (self.simplex[j],)+self.args), self.f_count + 1

        # Order the simplex.
        self.order_simplex()

        # Set xk and fk as the vertex of the simplex with the lowest function value.
        self.xk = self.simplex[0] * 1.0
        self.fk = self.simplex_vals[0]

        # Find the center of the simplex.
        self.center = average(self.simplex)


    def new_param_func(self):
        """The new parameter function.

        Simplex movement.
        """

        self.reflect_flag = 1
        self.shrink_flag = 0

        self.pivot_point = average(self.simplex[:-1])

        self.reflect()
        if self.reflect_val <= self.simplex_vals[0]:
            self.extend()
        elif self.reflect_val >= self.simplex_vals[-2]:
            self.reflect_flag = 0
            if self.reflect_val < self.simplex_vals[-1]:
                self.contract()
            else:
                self.contract_orig()
        if self.reflect_flag:
            self.simplex[-1], self.simplex_vals[-1] = self.reflect_vector, self.reflect_val
        if self.shrink_flag:
            self.shrink()

        self.order_simplex()

        # Update values.
        self.xk_new = self.simplex[0]
        self.fk_new = self.simplex_vals[0]
        self.dfk_new = None

        # Find the center of the simplex and calculate the distance moved.
        self.center_new = average(self.simplex)
        self.dist = sum(abs(self.center_new - self.center))


    def contract(self):
        """Contraction step."""

        self.contract_vector = 1.5 * self.pivot_point - 0.5 * self.simplex[-1]
        self.contract_val, self.f_count = apply(self.func, (self.contract_vector,)+self.args), self.f_count + 1
        if self.contract_val < self.reflect_val:
            self.simplex[-1], self.simplex_vals[-1] = self.contract_vector, self.contract_val
        else:
            self.shrink_flag = 1


    def contract_orig(self):
        """Contraction of the original simplex."""

        self.contract_orig_vector = 0.5 * (self.pivot_point + self.simplex[-1])
        self.contract_orig_val, self.f_count = apply(self.func, (self.contract_orig_vector,)+self.args), self.f_count + 1
        if self.contract_orig_val < self.simplex_vals[-1]:
            self.simplex[-1], self.simplex_vals[-1] = self.contract_orig_vector, self.contract_orig_val
        else:
            self.shrink_flag = 1


    def extend(self):
        """Extension step."""

        self.extend_vector = 3.0 * self.pivot_point - 2.0 * self.simplex[-1]
        self.extend_val, self.f_count = apply(self.func, (self.extend_vector,)+self.args), self.f_count + 1
        if self.extend_val < self.reflect_val:
            self.simplex[-1], self.simplex_vals[-1] = self.extend_vector, self.extend_val
            self.reflect_flag = 0


    def order_simplex(self):
        """Order the vertecies of the simplex according to accending function values."""
        sorted = argsort(self.simplex_vals)
        self.simplex = take(self.simplex, sorted)
        self.simplex_vals = take(self.simplex_vals, sorted)


    def reflect(self):
        """Reflection step."""

        self.reflect_vector = 2.0 * self.pivot_point - self.simplex[-1]
        self.reflect_val, self.f_count = apply(self.func, (self.reflect_vector,)+self.args), self.f_count + 1


    def shrink(self):
        """Shrinking step."""

        for i in xrange(self.n):
            j = i + 1
            self.simplex[j] = 0.5 * (self.simplex[0] + self.simplex[j])
            self.simplex_vals[j], self.f_count = apply(self.func, (self.simplex[j],)+self.args), self.f_count + 1


    def conv_test(self, *args):
        """Convergence test.

        Finish minimising when the function difference between the highest and lowest simplex
        vertecies is insignificant or if the simplex doesn't move.
        """

        if self.print_flag >= 2:
            print self.print_prefix + "diff = " + `self.simplex_vals[-1] - self.simplex_vals[0]`
            print self.print_prefix + "|diff| = " + `abs(self.simplex_vals[-1] - self.simplex_vals[0])`
            print self.print_prefix + "f_tol = " + `self.func_tol`
            print self.print_prefix + "center = " + `self.pivot_point`
            try:
                print self.print_prefix + "old center = " + `self.old_pivot`
                print self.print_prefix + "center diff = " + `self.pivot_point - self.old_pivot`
            except AttributeError:
                pass
            self.old_pivot = 1.0 * self.pivot_point
        if abs(self.simplex_vals[-1] - self.simplex_vals[0]) <= self.func_tol:
            if self.print_flag >= 2:
                print "\n" + self.print_prefix + "???Function tolerance reached."
                print self.print_prefix + "simplex_vals[-1]: " + `self.simplex_vals[-1]`
                print self.print_prefix + "simplex_vals[0]:  " + `self.simplex_vals[0]`
                print self.print_prefix + "|diff|:           " + `abs(self.simplex_vals[-1] - self.simplex_vals[0])`
                print self.print_prefix + "tol:              " + `self.func_tol`
            self.xk_new = self.simplex[0]
            self.fk_new = self.simplex_vals[0]
            return 1

        # Test if simplex has not moved.
        if self.dist == 0.0:
            self.warning = "Simplex has not moved."
            self.xk_new = self.simplex[0]
            self.fk_new = self.simplex_vals[0]
            return 1


    def update(self):
        """Update function."""

        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.center = self.center_new * 1.0
