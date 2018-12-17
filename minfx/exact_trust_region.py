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
"""Exact trust region optimization.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import dot, identity, sort, sqrt, transpose
from numpy.linalg import cholesky, eig, inv, solve
from re import match

# Minfx module imports.
from minfx.base_classes import Hessian_mods, Min, Trust_region
from minfx.bfgs import Bfgs
from minfx.newton import Newton


def exact_trust_region(func=None, dfunc=None, d2func=None, args=(), x0=None, min_options=(), func_tol=1e-25, grad_tol=None, maxiter=1e6, lambda0=0.0, delta_max=1e5, delta0=1.0, eta=0.2, mach_acc=1e-16, full_output=0, print_flag=0, print_prefix=""):
    """Exact trust region algorithm."""

    if print_flag:
        if print_flag >= 2:
            print(print_prefix)
        print(print_prefix)
        print(print_prefix + "Exact trust region minimisation")
        print(print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    min = Exact_trust_region(func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, lambda0, delta_max, delta0, eta, mach_acc, full_output, print_flag, print_prefix)
    if min.init_failure:
        print(print_prefix + "Initialisation of minimisation has failed.")
        return None
    results = min.minimise()
    return results


class Exact_trust_region(Trust_region, Bfgs, Newton):
    def __init__(self, func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, lambda0, delta_max, delta0, eta, mach_acc, full_output, print_flag, print_prefix):
        """Class for Exact trust region minimisation specific functions.

        Unless you know what you are doing, you should call the function 'exact_trust_region' rather than using this class.
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
        self.mach_acc = mach_acc
        self.lambda0 = lambda0
        self.delta_max = delta_max
        self.delta = delta0
        self.eta = eta

        # Initialisation failure flag.
        self.init_failure = 0

        # Setup the Hessian modification options and algorithm.
        self.hessian_type_and_mod(min_options)
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

        # Type specific functions.
        if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
            self.setup_bfgs()
            self.specific_update = self.update_bfgs
            self.d2fk = inv(self.Hk)
            self.warning = "Incomplete code."
        elif match('[Nn]ewton', self.hessian_type):
            self.setup_newton()
            self.specific_update = self.update_newton


    def new_param_func(self):
        """Find the exact trust region solution.

        Algorithm 4.4 from page 81 of 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.  This is only implemented for positive definite matrices.
        """

        # Matrix modification.
        pB, matrix = self.get_pk(return_matrix=1)

        # The exact trust region algorithm.
        l = 0
        lambda_l = self.lambda0

        while l < 3:
            # Calculate the matrix B + lambda(l).I
            B = matrix + lambda_l * self.I

            # Factor B + lambda(l).I = RT.R
            R = cholesky(B)

            # Solve RT.R.pl = -g
            y = solve(R, self.dfk)
            y = -solve(transpose(R), y)
            dot_pl = dot(y, y)

            # Solve RT.ql = pl
            y = solve(transpose(R), y)

            # lambda(l+1) update.
            lambda_l = lambda_l + (dot_pl / dot(y, y)) * ((sqrt(dot_pl) - self.delta) / self.delta)

            # Safeguard.
            lambda_l = max(0.0, lambda_l)

            if self.print_flag >= 2:
                print(self.print_prefix + "\tl: " + repr(l) + ", lambda(l) fin: " + repr(lambda_l))

            l = l + 1

        # Calculate the step.
        R = cholesky(matrix + lambda_l * self.I)
        y = solve(R, self.dfk)
        self.pk = -solve(transpose(R), y)

        if self.print_flag >= 2:
            print(self.print_prefix + "Step: " + repr(self.pk))

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.pk
        self.fk_new, self.f_count = self.func(*(self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = self.dfunc(*(self.xk_new,)+self.args), self.g_count + 1


    def old_param_func(self):
        """Find the exact trust region solution.

        More, J. J., and Sorensen D. C. 1983, Computing a trust region step.  SIAM J. Sci. Stat. Comput. 4, 553-572.  This function is incomplete.
        """

        self.warning = "Incomplete code, minimisation bypassed."
        print(self.print_prefix + "Incomplete code, minimisation bypassed.")
        return

        # Initialisation.
        iter = 0
        self.l = self.lambda0
        self.I = identity(len(self.dfk))

        # Initialise lL, lU, lS.
        self.lS = -1e99
        b = 0.0
        for j in range(len(self.d2fk)):
            self.lS = max(self.lS, -self.d2fk[j, j])
            sum = 0.0
            for i in range(len(self.d2fk[j])):
                sum = sum + abs(self.d2fk[i, j])
            b = max(b, sum)
        a = sqrt(dot(self.dfk, self.dfk)) / self.delta
        self.lL = max(0.0, self.lS, a - b)
        self.lU = a + b

        # Debugging.
        if self.print_flag >= 2:
            print(self.print_prefix + "Initialisation.")
            eigen = eig(self.d2fk)
            eigenvals = sort(eigen[0])
            for i in range(len(self.d2fk)):
                print(self.print_prefix + "\tB[" + repr(i) + ", " + repr(i) + "] = " + repr(self.d2fk[i, i]))
            print(self.print_prefix + "\tEigenvalues: " + repr(eigenvals))
            print(self.print_prefix + "\t||g||/delta: " + repr(a))
            print(self.print_prefix + "\t||B||1: " + repr(b))
            print(self.print_prefix + "\tl:  " + repr(self.l))
            print(self.print_prefix + "\tlL: " + repr(self.lL))
            print(self.print_prefix + "\tlU: " + repr(self.lU))
            print(self.print_prefix + "\tlS: " + repr(self.lS))

        # Iterative loop.
        return
        while True:
            # Safeguard lambda.
            if self.print_flag >= 2:
                print(self.print_prefix + "\n< Iteration " + repr(iter) + " >")
                print(self.print_prefix + "Safeguarding lambda.")
                print(self.print_prefix + "\tInit l: " + repr(self.l))
                print(self.print_prefix + "\tlL: " + repr(self.lL))
                print(self.print_prefix + "\tlU: " + repr(self.lU))
                print(self.print_prefix + "\tlS: " + repr(self.lS))
            self.l = max(self.l, self.lL)
            self.l = min(self.l, self.lU)
            if self.l <= self.lS:
                if self.print_flag >= 2:
                    print(self.print_prefix + "\tself.l <= self.lS")
                self.l = max(0.001*self.lU, sqrt(self.lL*self.lU))
            if self.print_flag >= 2:
                print(self.print_prefix + "\tFinal l: " + repr(self.l))

            # Calculate the matrix 'B + lambda.I' and factor 'B + lambda(l).I = RT.R'
            matrix = self.d2fk + self.l * self.I
            pos_def = 1
            if self.print_flag >= 2:
                print(self.print_prefix + "Cholesky decomp.")
                print(self.print_prefix + "\tB + lambda.I: " + repr(matrix))
                eigen = eig(matrix)
                eigenvals = sort(eigen[0])
                print(self.print_prefix + "\tEigenvalues: " + repr(eigenvals))
            try:
                func = cholesky
                R = func(matrix)
                if self.print_flag >= 2:
                    print(self.print_prefix + "\tCholesky matrix R: " + repr(R))
            except "LinearAlgebraError":
                if self.print_flag >= 2:
                    print(self.print_prefix + "\tLinearAlgebraError, matrix is not positive definite.")
                pos_def = 0
            if self.print_flag >= 2:
                print(self.print_prefix + "\tPos def: " + repr(pos_def))

            if pos_def:
                # Solve p = -inv(RT.R).g
                p = -dot(inv(matrix), self.dfk)
                if self.print_flag >= 2:
                    print(self.print_prefix + "Solve p = -inv(RT.R).g")
                    print(self.print_prefix + "\tp: " + repr(p))

                # Compute tau and z if ||p|| < delta.
                dot_p = dot(p, p)
                len_p = sqrt(dot_p)
                if len_p < self.delta:

                    # Calculate z.

                    # Calculate tau.
                    delta2_len_p2 = self.delta**2 - dot_p
                    dot_p_z = dot(p, z)
                    tau = delta2_len_p2 / (dot_p_z + sign(dot_p_z) * sqrt(dot_p_z**2 + delta2_len_p2**2))

                    if self.print_flag >= 2:
                        print(self.print_prefix + "||p|| < delta")
                        print(self.print_prefix + "\tz: " + repr(z))
                        print(self.print_prefix + "\ttau: " + repr(tau))
                else:
                    if self.print_flag >= 2:
                        print(self.print_prefix + "||p|| >= delta")
                        print(self.print_prefix + "\tNo doing anything???")

                # Solve q = inv(RT).p
                q = dot(inv(transpose(R)), p)

                # Update lL, lU.
                if len_p < self.delta:
                    self.lU = min(self.lU, self.l)
                else:
                    self.lL = max(self.lL, self.l)

                # lambda update.
                self.l_corr = dot_p / dot(q, q) * ((len_p - self.delta) / self.delta)

            else:
                # Update lambda via lambda = lS.
                self.lS = max(self.lS, self.l)

                self.l_corr = -self.l

            # Update lL
            self.lL = max(self.lL, self.lS)
            if self.print_flag >= 2:
                print(self.print_prefix + "Update lL: " + repr(self.lL))

            # Check the convergence criteria.

            # lambda update.
            self.l = self.l + self.l_corr

            iter = iter + 1

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.pk
        self.fk_new, self.f_count = self.func(*(self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = self.dfunc(*(self.xk_new,)+self.args), self.g_count + 1


    def safeguard(self, eigenvals):
        """Safeguarding function."""

        if self.lambda_l < -eigenvals[0]:
            self.lambda_l = -eigenvals[0] + 1.0
            if self.print_flag >= 2:
                print(self.print_prefix + "\tSafeguarding. lambda(l) = " + repr(self.lambda_l))
        elif self.lambda_l <= 0.0:
            if self.print_flag >= 2:
                print(self.print_prefix + "\tSafeguarding. lambda(l)=0")
            self.lambda_l = 0.0


    def update(self):
        """Update function.

        Run the trust region update.  If this update decides to shift xk+1 to xk, then run the Newton update.
        """

        self.trust_region_update()
        if self.shift_flag:
            self.specific_update()
