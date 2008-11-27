###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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


from LinearAlgebra import eigenvectors, inverse
from Numeric import Float64, dot, identity, matrixmultiply, outerproduct, sort, sqrt
from re import match

from bfgs import Bfgs
from newton import Newton
from base_classes import Hessian_mods, Trust_region, Min


def dogleg(func=None, dfunc=None, d2func=None, args=(), x0=None, min_options=(), func_tol=1e-25, grad_tol=None, maxiter=1e6, delta_max=1e10, delta0=1e5, eta=0.0001, mach_acc=1e-16, full_output=0, print_flag=0, print_prefix=""):
    """Dogleg trust region algorithm.

    Page 71 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.
    The dogleg method is defined by the trajectory p(tau):

                  / tau . pU            0 <= tau <= 1,
        p(tau) = <
                  \ pU + (tau - 1)(pB - pU),    1 <= tau <= 2.

    where:
        tau is in [0, 2]
        pU is the unconstrained minimiser along the steepest descent direction.
        pB is the full step.

    pU is defined by the formula:

                gT.g
        pU = - ------ g
               gT.B.g

    and pB by the formula:

        pB = - B^(-1).g

    If the full step is within the trust region it is taken.  Otherwise the point at which the
    dogleg trajectory intersects the trust region is taken.  This point can be found by solving the
    scalar quadratic equation:
        ||pU + (tau - 1)(pB - pU)||^2 = delta^2
    """

    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Dogleg minimisation"
        print print_prefix + "~~~~~~~~~~~~~~~~~~~"
    min = Dogleg(func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, delta_max, delta0, eta, mach_acc, full_output, print_flag, print_prefix)
    if min.init_failure:
        print print_prefix + "Initialisation of minimisation has failed."
        return None
    results = min.minimise()
    return results


class Dogleg(Hessian_mods, Trust_region, Min, Bfgs, Newton):
    def __init__(self, func, dfunc, d2func, args, x0, min_options, func_tol, grad_tol, maxiter, delta_max, delta0, eta, mach_acc, full_output, print_flag, print_prefix):
        """Class for Dogleg trust region minimisation specific functions.

        Unless you know what you are doing, you should call the function 'dogleg' rather than using
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
        self.mach_acc = mach_acc
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
        if self.hessian_type and match('[Bb][Ff][Gg][Ss]', self.hessian_type):
            self.setup_bfgs()
            self.specific_update = self.update_bfgs
            self.hessian_update = self.hessian_update_bfgs
            self.d2fk = inverse(self.Hk)
        elif self.hessian_type and match('[Nn]ewton', self.hessian_type):
            self.setup_newton()
            self.specific_update = self.update_newton
            self.hessian_update = self.hessian_update_newton


    def dogleg(self):
        """The dogleg algorithm."""

        # Calculate the full step and its norm.
        try:
            pB = -matrixmultiply(self.Hk, self.dfk)
        except AttributeError:
            # Backup the Hessian as the function self.get_pk may modify it.
            d2fk_backup = 1.0 * self.d2fk

            # The modified Newton step.
            pB = self.get_pk()

            # Restore the Hessian.
            self.d2fk = d2fk_backup
        norm_pB = sqrt(dot(pB, pB))

        # Test if the full step is within the trust region.
        if norm_pB <= self.delta:
            return pB

        # Calculate pU.
        curv = dot(self.dfk, dot(self.d2fk, self.dfk))
        pU = - dot(self.dfk, self.dfk) / curv * self.dfk
        dot_pU = dot(pU, pU)
        norm_pU = sqrt(dot_pU)

        # Test if the step pU exits the trust region.
        if norm_pU >= self.delta:
            return self.delta * pU / norm_pU

        # Find the solution to the scalar quadratic equation.
        pB_pU = pB - pU
        dot_pB_pU = dot(pB_pU, pB_pU)
        dot_pU_pB_pU = dot(pU, pB_pU)
        fact = dot_pU_pB_pU**2 - dot_pB_pU * (dot_pU - self.delta**2)
        tau = (-dot_pU_pB_pU + sqrt(fact)) / dot_pB_pU

        # Decide on which part of the trajectory to take.
        return pU + tau * pB_pU


    def hessian_update_bfgs(self):
        """BFGS Hessian update."""

        # BFGS matrix update.
        sk = self.xk_new - self.xk
        yk = self.dfk_new - self.dfk
        if dot(yk, sk) == 0:
            self.warning = "The BFGS matrix is indefinite.  This should not occur."
            rk = 1e99
        else:
            rk = 1.0 / dot(yk, sk)

        if self.k == 0:
            self.Hk = dot(yk, sk) / dot(yk, yk) * self.I

        a = self.I - rk*outerproduct(sk, yk)
        b = self.I - rk*outerproduct(yk, sk)
        c = rk*outerproduct(sk, sk)
        matrix = matrixmultiply(matrixmultiply(a, self.Hk), b) + c
        self.Hk = matrix

        # Calculate the Hessian.
        self.d2fk = inverse(self.Hk)


    def hessian_update_newton(self):
        """Empty function."""

        pass


    def new_param_func(self):
        """Find the dogleg minimiser."""

        self.pk = self.dogleg()
        self.xk_new = self.xk + self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

        if self.print_flag >= 2:
            print self.print_prefix + "Fin."
            print self.print_prefix + "   pk:     " + `self.pk`
            print self.print_prefix + "   xk:     " + `self.xk`
            print self.print_prefix + "   xk_new: " + `self.xk_new`
            print self.print_prefix + "   fk:     " + `self.fk`
            print self.print_prefix + "   fk_new: " + `self.fk_new`


    def update(self):
        """Update function.

        Run the trust region update.  If this update decides to shift xk+1 to xk, then run the BFGS
        or Newton updates.
        """

        self.trust_region_update()

        if not self.shift_flag:
            self.hessian_update()
        else:
            self.specific_update()
