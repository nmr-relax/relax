###############################################################################
#                                                                             #
# Copyright (C) 2003, 2005-2006 Edward d'Auvergne                             #
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


from LinearAlgebra import cholesky_decomposition, eigenvectors, inverse, solve_linear_equations
from math import acos
from Numeric import Float64, array, dot, identity, matrixmultiply, sort, sqrt, trace, transpose, zeros
from re import match

from base_classes import Hessian_mods, Line_search, Min


def newton(func=None, dfunc=None, d2func=None, args=(), x0=None, min_options=(), func_tol=1e-25, grad_tol=None, maxiter=1e6, a0=1.0, mu=0.0001, eta=0.9, mach_acc=1e-16, full_output=0, print_flag=0, print_prefix=""):
    """Newton minimisation."""

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Newton minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~"
    min = Newton(func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, mach_acc, full_output, print_flag, print_prefix)
    if min.init_failure:
        print print_prefix + "Initialisation of minimisation has failed."
        return None
    results = min.minimise()
    return results


class Newton(Hessian_mods, Line_search, Min):
    def __init__(self, func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, a0, mu, eta, mach_acc, full_output, print_flag, print_prefix):
        """Class for Newton minimisation specific functions.

        Unless you know what you are doing, you should call the function 'newton' rather than using
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
        self.mach_acc = mach_acc
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

        # Setup the line search and Hessian modification algorithms.
        self.line_search_algor = None
        self.hessian_mod = None

        # Test if the options are a tuple.
        if type(min_options) != tuple:
            print self.print_prefix + "The minimisation options " + `min_options` + " is not a tuple."
            self.init_failure = 1; return

        # Test that no more thant 2 options are given.
        if len(min_options) > 2:
            print self.print_prefix + "A maximum of two minimisation options is allowed (the line search algorithm and the Hessian modification)."
            self.init_failure = 1; return

        # Sort out the minimisation options.
        none_option = None
        for opt in min_options:
            if match('[Nn]one', opt):
                none_option = opt
                continue
            if self.line_search_algor == None and self.valid_line_search(opt):
                self.line_search_algor = opt
            elif self.hessian_mod == None and self.valid_hessian_mod(opt):
                self.hessian_mod = opt
            else:
                if self.line_search_algor:
                    print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is not a valid Hessian modification."
                elif self.hessian_mod:
                    print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is not a valid line search algorithm."
                else:
                    print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is neither a valid line search algorithm or Hessian modification."
                self.init_failure = 1; return
        if none_option and not self.hessian_mod:
            if self.valid_hessian_mod(none_option):
                self.hessian_mod = none_option
        elif none_option and not self.line_search_algor:
            if self.valid_line_search(none_option):
                self.line_search_algor = none_option
        elif none_option:
            print self.print_prefix + "Invalid combination of options " + `min_options` + "."
            self.init_failure = 1; return

        # Default line search algorithm.
        if self.line_search_algor == None:
            self.line_search_algor = 'Back'

        # Default Hessian modification.
        if self.hessian_mod == None:
            self.hessian_mod = 'GMW'

        # Line search and Hessian modification initialisation.
        self.setup_line_search()
        self.setup_hessian_mod()

        # Initialise the function, gradient, and Hessian evaluation counters.
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Initialise the warning string.
        self.warning = None

        # Constants.
        self.n = len(self.xk)
        self.I = identity(len(self.xk))

        # Set the convergence test function.
        self.setup_conv_tests()

        # Newton setup function.
        self.setup_newton()

        # Set the update function.
        self.update = self.update_newton


    def new_param_func(self):
        """The new parameter function.

        Find the search direction, do a line search, and get xk+1 and fk+1.
        """

        # Calculate the Newton direction.
        self.pk = self.get_pk()

        # Line search.
        self.line_search()

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.alpha * self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

        # Debugging.
        if self.print_flag >= 2:
            print "\n" + self.print_prefix + "New param function."
            print self.print_prefix + "pk:    " + `self.pk`
            print self.print_prefix + "alpha: " + `self.alpha`
            print self.print_prefix + "xk:    " + `self.xk`
            print self.print_prefix + "xk+1:  " + `self.xk_new`
            print self.print_prefix + "fk:    " + `self.fk`
            print self.print_prefix + "fk+1:  " + `self.fk_new`
            print self.print_prefix + "dfk:    " + `self.dfk`
            print self.print_prefix + "dfk+1:  " + `self.dfk_new`
            print self.print_prefix + "d2fk:\n" + `self.d2fk`

            #eigen = eigenvectors(self.d2fk)
            #print self.print_prefix + "Eigenvalues: " + `eigen[0]`

            print self.print_prefix + "Angle to the unit vector pointing along the first dimension."
            unit_vect = zeros(self.n, Float64)
            unit_vect[0] = 1.0
            dfk_angle = acos(dot(self.dfk, unit_vect) / sqrt(dot(self.dfk, self.dfk)))
            pk_angle = acos(dot(self.pk, unit_vect) / sqrt(dot(self.pk, self.pk)))
            print self.print_prefix + "steepest descent: " + `dfk_angle`
            print self.print_prefix + "Newton step:      " + `pk_angle`


    def setup_newton(self):
        """Setup function.

        The initial Newton function value, gradient vector, and Hessian matrix are calculated.
        """

        self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


    def update_newton(self):
        """Function to update the function value, gradient vector, and Hessian matrix."""

        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1
