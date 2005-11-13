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


# This module contains the following base classes:
#    Min:                The base class containing the main iterative minimisation loop and
#        a few other base class functions.
#    Line_search:        The base class containing the generic line search functions.
#    Trust_region:       The base class containing the generic trust-region functions.
#    Conjugate_gradient: The base class containing the generic conjugate gradient functions.


# Inbuilt python modules.
#########################

from LinearAlgebra import LinAlgError, inverse
from Numeric import dot, matrixmultiply, sqrt
from re import match


# Line search functions.
########################

from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


# Hessian modifications.
########################

from hessian_mods.eigenvalue import eigenvalue
from hessian_mods.cholesky import cholesky
from hessian_mods.gmw81 import gmw
from hessian_mods.gmw81_old import gmw_old
from hessian_mods.se99 import se99


# The generic minimisation base class (containing the main iterative loop).
###########################################################################

class Min:
    def __init__(self):
        """Base class containing the main minimisation iterative loop algorithm.

        The algorithm is defined in the minimise function.  Also supplied are generic setup,
        convergence tests, and update functions.
        """


    def double_test(self, fk_new, fk, gk):
        """Default base class function for both function and gradient convergence tests.

        Test if the minimum function tolerance between fk and fk+1 has been reached as well as if
        the minimum gradient tolerance has been reached.
        """

        # Test the function tolerance.
        if abs(fk_new - fk) <= self.func_tol:
            if self.print_flag >= 2:
                print "\n" + self.print_prefix + "Function tolerance reached."
                print self.print_prefix + "fk:          " + `fk`
                print self.print_prefix + "fk+1:        " + `fk_new`
                print self.print_prefix + "|fk+1 - fk|: " + `abs(fk_new - fk)`
                print self.print_prefix + "tol:         " + `self.func_tol`
            return 1

        # Test the gradient tolerance.
        elif sqrt(dot(gk, gk)) <= self.grad_tol:
            if self.print_flag >= 2:
                print "\n" + self.print_prefix + "Gradient tolerance reached."
                print self.print_prefix + "gk+1:     " + `gk`
                print self.print_prefix + "||gk+1||: " + `sqrt(dot(gk, gk))`
                print self.print_prefix + "tol:      " + `self.grad_tol`
            return 1


    def func_test(self, fk_new, fk, gk):
        """Default base class function for the function convergence test.

        Test if the minimum function tolerance between fk and fk+1 has been reached.
        """

        # Test the function tolerance.
        if abs(fk_new - fk) <= self.func_tol:
            if self.print_flag >= 2:
                print "\n" + self.print_prefix + "Function tolerance reached."
                print self.print_prefix + "fk:          " + `fk`
                print self.print_prefix + "fk+1:        " + `fk_new`
                print self.print_prefix + "|fk+1 - fk|: " + `abs(fk_new - fk)`
                print self.print_prefix + "tol:         " + `self.func_tol`
            return 1


    def grad_test(self, fk_new, fk, gk):
        """Default base class function for the gradient convergence test.

        Test if the minimum gradient tolerance has been reached.  Minimisation will also terminate
        if the function value difference between fk and fk+1 is zero.  This modification is
        essential for the quasi-Newton techniques.
        """

        # Test the gradient tolerance.
        if sqrt(dot(gk, gk)) <= self.grad_tol:
            if self.print_flag >= 2:
                print "\n" + self.print_prefix + "Gradient tolerance reached."
                print self.print_prefix + "gk+1:     " + `gk`
                print self.print_prefix + "||gk+1||: " + `sqrt(dot(gk, gk))`
                print self.print_prefix + "tol:      " + `self.grad_tol`
            return 1

        # No change in function value (prevents the minimiser from iterating without moving).
        elif fk_new - fk == 0.0:
            if self.print_flag >= 2:
                print "\n" + self.print_prefix + "Function difference of zero."
                print self.print_prefix + "fk_new - fk = 0.0"
            return 1


    def hessian_type_and_mod(self, min_options, default_type='Newton', default_mod='GMW'):
        """Hessian type and modification options.

        Function for sorting out the minimisation options when either the Hessian type or Hessian
        modification can be selected.
        """

        # Initialise.
        self.hessian_type = None
        self.hessian_mod = None

        # Test if the options are a tuple.
        if type(min_options) != tuple:
            print self.print_prefix + "The minimisation options " + `min_options` + " is not a tuple."
            self.init_failure = 1
            return

        # Test that no more thant 2 options are given.
        if len(min_options) > 2:
            print self.print_prefix + "A maximum of two minimisation options is allowed (the Hessian type and Hessian modification)."
            self.init_failure = 1
            return

        # Sort out the minimisation options.
        for opt in min_options:
            if self.hessian_type == None and opt != None and (match('[Bb][Ff][Gg][Ss]', opt) or match('[Nn]ewton', opt)):
                self.hessian_type = opt
            elif self.hessian_mod == None and self.valid_hessian_mod(opt):
                self.hessian_mod = opt
            else:
                print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is neither a valid Hessian type or modification."
                self.init_failure = 1
                return

        # Default Hessian type.
        if self.hessian_type == None:
            self.hessian_type = default_type

        # Make sure that no Hessian modification is used with the BFGS matrix.
        if match('[Bb][Ff][Gg][Ss]', self.hessian_type) and self.hessian_mod != None:
            print self.print_prefix + "When using the BFGS matrix, Hessian modifications should not be used."
            self.init_failure = 1
            return

        # Default Hessian modification when the Hessian type is Newton.
        if match('[Nn]ewton', self.hessian_type) and self.hessian_mod == None:
            self.hessian_mod = None
            #self.hessian_mod = default_mod

        # Print the Hessian type info.
        if self.print_flag:
            if match('[Bb][Ff][Gg][Ss]', self.hessian_type):
                print self.print_prefix + "Hessian type:  BFGS"
            else:
                print self.print_prefix + "Hessian type:  Newton"


    def minimise(self):
        """Main minimisation iterative loop algorithm.

        This algorithm is designed to be compatible with all iterative minimisers.  The outline is:

        k = 0
        while 1:
            New parameter function
            Convergence tests
            Update function
            k = k + 1
        """

        # Start the iteration counter.
        self.k = 0
        if self.print_flag:
            self.k2 = 0
            print ""   # Print a new line.

        # Iterate until the local minima is found.
        while 1:
            # Print out.
            if self.print_flag:
                out = 0
                if self.print_flag >= 2:
                    print "\n" + self.print_prefix + "Main iteration k=" + `self.k`
                    out = 1
                else:
                    if self.k2 == 100:
                        self.k2 = 0
                    if self.k2 == 0:
                        out = 1
                if out == 1:
                    print self.print_prefix + "%-3s%-8i%-4s%-65s %-4s%-20s" % ("k:", self.k, "xk:", `self.xk`, "fk:", `self.fk`)

            # Get xk+1 (new parameter function).
            try:
                self.new_param_func()
            except "LinearAlgebraError", message:
                self.warning = "LinearAlgebraError: " + message + " (fatal minimisation error)."
                break
            except LinAlgError, message:
                if type(message.args[0]) == int:
                    text = message.args[1]
                else:
                    text = message.args[0]
                self.warning = "LinearAlgebraError: " + text + " (fatal minimisation error)."
                break
            except OverflowError, message:
                if type(message.args[0]) == int:
                    text = message.args[1]
                else:
                    text = message.args[0]
                self.warning = "OverflowError: " + text + " (fatal minimisation error)."
                break
            except NameError, message:
                self.warning = message.args[0] + " (fatal minimisation error)."
                break

            # Test for warnings.
            if self.warning != None:
                break

            # Maximum number of iteration test.
            if self.k >= self.maxiter - 1:
                self.warning = "Maximum number of iterations reached"
                break

            # Convergence test.
            if self.conv_test(self.fk_new, self.fk, self.dfk_new):
                break

            # Update function.
            try:
                self.update()
            except OverflowError, message:
                if type(message.args[0]) == int:
                    text = message.args[1]
                else:
                    text = message.args[0]
                self.warning = "OverflowError: " + text + " (fatal minimisation error)."
                break
            except NameError, message:
                if type(message.args[0]) == int:
                    self.warning = message.args[1]
                else:
                    self.warning = message.args[0]
                break

            # Iteration counter update.
            self.k = self.k + 1
            if self.print_flag:
                self.k2 = self.k2 + 1

        if self.full_output:
            try:
                return self.xk_new, self.fk_new, self.k+1, self.f_count, self.g_count, self.h_count, self.warning
            except AttributeError:
                return self.xk, self.fk, self.k, self.f_count, self.g_count, self.h_count, self.warning
        else:
            try:
                return self.xk_new
            except AttributeError:
                return self.xk


    def setup_conv_tests(self):
        """Default base class for selecting the convergence tests."""

        if self.func_tol != None and self.grad_tol != None:
            self.conv_test = self.double_test
        elif self.func_tol != None:
            self.conv_test = self.func_test
        elif self.grad_tol != None:
            self.conv_test = self.grad_test
        else:
            print self.print_prefix + "Convergence tests cannot be setup because both func_tol and grad_tol are set to None."
            self.init_failure = 1
            return


    def update(self):
        """Default base class update function.

        xk+1 is shifted to xk
        fk+1 is shifted to fk
        """

        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new





# The base class containing the generic line search functions.
##############################################################

class Line_search:
    def __init__(self):
        """Base class containing the generic line search functions."""


    def backline(self):
        """Function for running the backtracking line search."""

        self.alpha, fc = backtrack(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0)
        self.f_count = self.f_count + fc


    def line_search_options(self, min_options):
        """Line search options.

        Function for sorting out the minimisation options when the only option can be a line search.
        """

        # Initialise.
        self.line_search_algor = None

        # Test if the options are a tuple.
        if type(min_options) != tuple:
            print self.print_prefix + "The minimisation options " + `min_options` + " is not a tuple."
            self.init_failure = 1
            return

        # No more than one option is allowed.
        if len(min_options) > 1:
            print self.print_prefix + "A maximum of one minimisation options is allowed (the line search algorithm)."
            self.init_failure = 1
            return

        # Sort out the minimisation options.
        for opt in min_options:
            if self.valid_line_search(opt):
                self.line_search_algor = opt
            else:
                print self.print_prefix + "The minimisation option " + `opt` + " from " + `min_options` + " is not a valid line search algorithm."
                self.init_failure = 1
                return

        # Default line search algorithm.
        if self.line_search_algor == None:
            self.line_search_algor = 'Back'


    def mt(self):
        """Function for running the More and Thuente line search."""

        self.alpha, fc, gc = more_thuente(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
        self.f_count = self.f_count + fc
        self.g_count = self.g_count + gc


    def no_search(self):
        """Set alpha to alpha0."""

        self.alpha = self.a0


    def nwi(self):
        """Function for running the Nocedal and Wright interpolation based line search."""

        self.alpha, fc = nocedal_wright_interpol(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, print_flag=0)
        self.f_count = self.f_count + fc


    def nww(self):
        """Function for running the Nocedal and Wright line search for the Wolfe conditions."""

        self.alpha, fc, gc = nocedal_wright_wolfe(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
        self.f_count = self.f_count + fc
        self.g_count = self.g_count + gc


    def setup_line_search(self):
        """The line search function."""

        if self.line_search_algor == None:
            self.init_failure = 1
            return
        elif match('^[Bb]ack', self.line_search_algor):
            if self.print_flag:
                print self.print_prefix + "Line search:  Backtracking line search."
            self.line_search = self.backline
        elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor) or match('^[Nn][Ww][Ii]', self.line_search_algor):
            if self.print_flag:
                print self.print_prefix + "Line search:  Nocedal and Wright interpolation based line search."
            self.line_search = self.nwi
        elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor) or match('^[Nn][Ww][Ww]', self.line_search_algor):
            if self.print_flag:
                print self.print_prefix + "Line search:  Nocedal and Wright line search for the Wolfe conditions."
            self.line_search = self.nww
        elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor) or match('^[Mm][Tt]', self.line_search_algor):
            if self.print_flag:
                print self.print_prefix + "Line search:  More and Thuente line search."
            self.line_search = self.mt
        elif match('^[Nn]one$', self.line_search_algor):
            if self.print_flag:
                print self.print_prefix + "Line search:  No line search."
            self.line_search = self.no_search


    def valid_line_search(self, type):
        """Test if the string 'type' is a valid line search algorithm."""

        if type == None:
            return 0
        elif match('^[Bb]ack', type) or match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', type) or match('^[Nn][Ww][Ii]', type) or match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', type) or match('^[Nn][Ww][Ww]', type) or match('^[Mm]ore[ _][Tt]huente$', type) or match('^[Mm][Tt]', type) or match('^[Nn]one$', type):
            return 1
        else:
            return 0





# The base class containing the generic trust-region functions.
###############################################################

class Trust_region:
    def __init__(self):
        """Base class containing the generic trust-region functions."""


    def trust_region_update(self):
        """An algorithm for trust region radius selection.

        Page 68 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

        First calculate rho using the formula:

                    f(xk) - f(xk + pk)
            rho  =  ------------------
                      mk(0) - mk(pk)

        Where the numerator is called the actual reduction and the denominator is the predicted reduction.

        Secondly choose the trust region radius for the next iteration.
        Finally decide if xk+1 should be shifted to xk.
        """

        # Actual reduction.
        act_red = self.fk - self.fk_new

        # Predicted reduction.
        pred_red = - dot(self.dfk, self.pk) - 0.5 * dot(self.pk, dot(self.d2fk, self.pk))

        # Rho.
        if pred_red == 0.0:
            self.rho = 1e99
        else:
            self.rho = act_red / pred_red

        # Calculate the Euclidean norm of pk.
        self.norm_pk = sqrt(dot(self.pk, self.pk))

        if self.print_flag >= 2:
            print self.print_prefix + "Actual reduction: " + `act_red`
            print self.print_prefix + "Predicted reduction: " + `pred_red`
            print self.print_prefix + "rho: " + `self.rho`
            print self.print_prefix + "||pk||: " + `self.norm_pk`

        # Rho is close to zero or negative, therefore the trust region is shrunk.
        if self.rho < 0.25 or pred_red < 0.0:
            self.delta = 0.25 * self.delta
            if self.print_flag >= 2:
                print self.print_prefix + "Shrinking the trust region."

        # Rho is close to one and pk has reached the boundary of the trust region, therefore the trust region is expanded.
        elif self.rho > 0.75 and abs(self.norm_pk - self.delta) < 1e-5:
            self.delta = min(2.0*self.delta, self.delta_max)
            if self.print_flag >= 2:
                print self.print_prefix + "Expanding the trust region."

        # Rho is positive but not close to one, therefore the trust region is unaltered.
        else:
            if self.print_flag >= 2:
                print self.print_prefix + "Trust region is unaltered."

        if self.print_flag >= 2:
            print self.print_prefix + "New trust region: " + `self.delta`

        # Choose the position for the next iteration.
        if self.rho > self.eta and pred_red > 0.0:
            self.shift_flag = 1
            if self.print_flag >= 2:
                print self.print_prefix + "rho > eta, " + `self.rho` + " > " + `self.eta`
                print self.print_prefix + "Moving to, self.xk_new: " + `self.xk_new`
        else:
            self.shift_flag = 0
            if self.print_flag >= 2:
                print self.print_prefix + "rho < eta, " + `self.rho` + " < " + `self.eta`
                print self.print_prefix + "Not moving, self.xk: " + `self.xk`





# The base class containing the generic conjugate gradient functions.
#####################################################################

class Conjugate_gradient:
    def __init__(self):
        """Class containing the non-specific conjugate gradient code."""


    def new_param_func(self):
        """The new parameter function.

        Do a line search then calculate xk+1, fk+1, and gk+1.
        """

        # Line search.
        self.line_search()

        # Find the new parameter vector and function value at that point.
        self.xk_new = self.xk + self.alpha * self.pk
        self.fk_new, self.f_count = apply(self.func, (self.xk_new,)+self.args), self.f_count + 1
        self.dfk_new, self.g_count = apply(self.dfunc, (self.xk_new,)+self.args), self.g_count + 1

        if self.print_flag >= 2:
            print self.print_prefix + "New param func:"
            print self.print_prefix + "\ta:    " + `self.alpha`
            print self.print_prefix + "\tpk:   " + `self.pk`
            print self.print_prefix + "\txk:   " + `self.xk`
            print self.print_prefix + "\txk+1: " + `self.xk_new`
            print self.print_prefix + "\tfk:   " + `self.fk`
            print self.print_prefix + "\tfk+1: " + `self.fk_new`
            print self.print_prefix + "\tgk:   " + `self.dfk`
            print self.print_prefix + "\tgk+1: " + `self.dfk_new`


    def old_cg_conv_test(self):
        """Convergence tests.

        This is old code implementing the conjugate gradient convergence test given on page 124 of
        'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.  This
        function is currently unused.
        """

        inf_norm = 0.0
        for i in xrange(len(self.dfk)):
            inf_norm = max(inf_norm, abs(self.dfk[i]))
        if inf_norm < self.grad_tol * (1.0 + abs(self.fk)):
            return 1
        elif self.fk_new - self.fk == 0.0:
            self.warning = "Function tol of zero reached."
            return 1


    def update(self):
        """Function to update the function value, gradient vector, and Hessian matrix"""

        # Gradient dot product at k+1.
        self.dot_dfk_new = dot(self.dfk_new, self.dfk_new)

        # Calculate beta at k+1.
        bk_new = self.calc_bk()

        # Restarts.
        if abs(dot(self.dfk_new, self.dfk)) / self.dot_dfk_new >= 0.1:
            if self.print_flag >= 2:
                print self.print_prefix + "Restarting."
            bk_new = 0

        # Calculate pk+1.
        self.pk_new = -self.dfk_new + bk_new * self.pk

        if self.print_flag >= 2:
            print self.print_prefix + "Update func:"
            print self.print_prefix + "\tpk:     " + `self.pk`
            print self.print_prefix + "\tpk+1:   " + `self.pk_new`

        # Update.
        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
        self.pk = self.pk_new * 1.0
        self.dot_dfk = self.dot_dfk_new




# The base class containing the Hessian modifications.
######################################################

class Hessian_mods:
    def __init__(self):
        """Base class containing the generic line search functions."""


    def cholesky(self, return_matrix=0):
        """Function for running the Cholesky Hessian modification."""

        return cholesky(self.dfk, self.d2fk, self.I, self.n, self.print_prefix, self.print_flag, return_matrix)


    def eigenvalue(self, return_matrix=0):
        """Function for running the eigenvalue Hessian modification."""

        return eigenvalue(self.dfk, self.d2fk, self.I, self.print_prefix, self.print_flag, return_matrix)


    def gmw(self, return_matrix=0):
        """Function for running the Gill, Murray, and Wright modified Cholesky algorithm."""

        return gmw(self.dfk, self.d2fk, self.I, self.n, self.mach_acc, self.print_prefix, self.print_flag, return_matrix)


    def gmw_old(self, return_matrix=0):
        """Function for running the Gill, Murray, and Wright modified Cholesky algorithm."""

        return gmw_old(self.dfk, self.d2fk, self.I, self.n, self.mach_acc, self.print_prefix, self.print_flag, return_matrix)


    def se99(self, return_matrix=0):
        """Function for running the Gill, Murray, and Wright modified Cholesky algorithm."""

        return se99(self.dfk, self.d2fk, self.I, self.n, self.tau, self.tau_bar, self.mu, self.print_prefix, self.print_flag, return_matrix)


    def setup_hessian_mod(self):
        """Initialise the Hessian modification functions."""

        # Unmodified Hessian.
        if self.hessian_mod == None or match('[Nn]one', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  Unmodified Hessian."
            self.get_pk = self.unmodified_hessian

        # Eigenvalue modification.
        elif match('^[Ee]igen', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  Eigenvalue modification."
            self.get_pk = self.eigenvalue

        # Cholesky with added multiple of the identity.
        elif match('^[Cc]hol', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  Cholesky with added multiple of the identity."
            self.get_pk = self.cholesky

        # The Gill, Murray, and Wright modified Cholesky algorithm.
        elif match('^[Gg][Mm][Ww]$', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  The Gill, Murray, and Wright modified Cholesky algorithm."
            self.get_pk = self.gmw

        # The Gill, Murray, and Wright modified Cholesky algorithm.
        elif match('^[Gg][Mm][Ww][ -_]old', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  The Gill, Murray, and Wright modified Cholesky algorithm."
            self.get_pk = self.gmw_old

        # The revised modified cholesky factorisation algorithm of Schnabel and Eskow, 99.
        elif match('^[Ss][Ee]99', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  The Schnabel and Eskow 1999 algorithm."
            self.tau = self.mach_acc ** (1.0/3.0)
            self.tau_bar = self.mach_acc ** (2.0/3.0)
            self.mu = 0.1
            self.get_pk = self.se99


    def unmodified_hessian(self, return_matrix=0):
        """Calculate the pure Newton direction."""

        if return_matrix:
            return -matrixmultiply(inverse(self.d2fk), self.dfk), self.d2fk
        else:
            return -matrixmultiply(inverse(self.d2fk), self.dfk)


    def valid_hessian_mod(self, mod):
        """Test if the string 'mod' is a valid Hessian modification."""

        if mod == None or match('^[Ee]igen', mod) or match('^[Cc]hol', mod) or match('^[Gg][Mm][Ww]$', mod) or match('^[Gg][Mm][Ww][ -_]old', mod) or match('^[Ss][Ee]99', mod) or match('^[Nn]one', mod):
            return 1
        else:
            return 0
