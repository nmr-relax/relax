###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from Numeric import Float64, dot, outerproduct, sqrt, zeros
from re import match

#from bound_constraint import Bound_constraint
from constraint_linear import Constraint_linear
from base_classes import Min


def method_of_multipliers(func=None, dfunc=None, d2func=None, args=(), x0=None, min_options=(), A=None, b=None, l=None, u=None, c=None, dc=None, d2c=None, lambda0=None, init_lambda=1e4, mu0=1e-5, epsilon0=1e-2, gamma0=1e-2, scale_mu=0.5, scale_epsilon=1e-2, scale_gamma=1e-2, func_tol=1e-25, grad_tol=None, maxiter=1e6, inner_maxiter=500, full_output=0, print_flag=0):
    """The method of multipliers, also known as the augmented Lagrangian method.

    Page 515 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    The algorithm is:

    Given u0 > 0, tolerance t0 > 0, starting points x0s and lambda0
    while 1:
        Find an approximate minimiser xk of LA(.,lambdak; uk), starting at xks, and terminating when
            the augmented Lagrangian gradient <= tk
        Final convergence test
        Update Lagrange multipliers using formula 17.58
        Choose new penalty parameter uk+1 within (0, uk)
        Set starting point for the next iteration to xk+1s = xk
        k = k + 1


    Three types of inequality constraint are supported.  These are linear, bound, and general
    constraints and must be setup as follows.  The vector x is the vector of model parameters.
    Don't use bound constriants yet as this code is incomplete!

    Equality constraints are currently unimplemented.


    Linear constraints
    ~~~~~~~~~~~~~~~~~~

    These are defined as:

        A.x >= b

    where:
        A is an m*n matrix where the rows are the transposed vectors, ai, of length n.  The elements
        of ai are the coefficients of the model parameters.

        x is the vector of model parameters of dimension n.

        b is the vector of scalars of dimension m.

        m is the number of constraints.

        n is the number of model parameters.

    eg if 0 <= q <= 1, q >= 1 - 2r, and 0 <= r, then:

        | 1  0 |            |  0 |
        |      |            |    |
        |-1  0 |   | q |    | -1 |
        |      | . |   | >= |    |
        | 1  2 |   | r |    |  1 |
        |      |            |    |
        | 0  1 |            |  2 |

    To use linear constraints both the matrix A and vector b need to be supplied.


    Bound constraints
    ~~~~~~~~~~~~~~~~~

    Bound constraints are defined as:

        l <= x <= u

    where l and u are the vectors of lower and upper bounds respectively.

    eg if 0 <= q <= 1, r >= 0, s <= 3, then:

        |  0  |    | q |    |  1  |
        |  0  | <= | r | <= | inf |
        |-inf |    | s |    |  3  |

    To use bound constraints both vectors l and u need to be supplied.


    General constraints
    ~~~~~~~~~~~~~~~~~~~

    These are defined as:

        ci(x) >= 0

    where ci(x) are the constraint functions.

    To use general constrains the functions c, dc, and d2c need to be supplied.  The function c is
    the constraint function which should return the vector of constraint values.  The function dc is
    the constraint gradient function which should return the matrix of constraint gradients.  The
    function d2c is the constraint Hessian function which should return the 3D matrix of constraint
    Hessians.


    Initial values
    ~~~~~~~~~~~~~~

    These are the default initial values:

        mu0 = 1e-5
        epsilon0 = 1e-2
        gamma0 = 1e-2
        scale_mu = 0.5
        scale_epsilon = 1e-2
        scale_gamma = 1e-2
    """

    if print_flag:
        print "\n"
        print "Method of Multipliers"
        print "~~~~~~~~~~~~~~~~~~~~~"
    min = Method_of_multipliers(func, dfunc, d2func, args, x0, min_options, A, b, l, u, c, dc, d2c, lambda0, init_lambda, mu0, epsilon0, gamma0, scale_mu, scale_epsilon, scale_gamma, func_tol, grad_tol, maxiter, inner_maxiter, full_output, print_flag)
    if min.init_failure:
        return None
    results = min.minimise()
    return results



class Method_of_multipliers(Min):
    def __init__(self, func, dfunc, d2func, args, x0, min_options, A, b, l, u, c, dc, d2c, lambda0, init_lambda, mu0, epsilon0, gamma0, scale_mu, scale_epsilon, scale_gamma, func_tol, grad_tol, maxiter, inner_maxiter, full_output, print_flag):
        """Class for Newton minimisation specific functions.

        Unless you know what you are doing, you should call the function 'method_of_multipliers'
        rather than using this class.
        """

        # Import the 'generic_minimise' function from 'generic.py'.  It is important that
        # this import statment occurs here otherwise a recursive import between the module
        # 'generic' and this module occurs.  This means that the function 'generic_minimise'
        # has not been initialised and is therefore not in the namespace.
        from generic import generic_minimise
        self.generic_minimise = generic_minimise

        # Linear constraints.
        if A != None and b != None:
            self.A = A
            self.b = b
            self.constraint_linear = Constraint_linear(self.A, self.b)
            self.c = self.constraint_linear.func
            self.dc = self.constraint_linear.dfunc
            self.d2c = None
            self.func_d2LA = self.func_d2LA_simple
            self.m = len(self.b)
            if print_flag >= 2:
                print "Linear constraint matrices."
                print "A:\n" + `self.A`
                print "b:\n" + `self.b`

        # Bound constraints.
        elif l != None and u != None:
            print "Bound constraints are not implemented yet."
            self.init_failure = 1
            return
            self.l = l
            self.u = u
            #self.bound_constraint = bound_constraint(self.l, self.u)
            #self.c = self.bound_constraint.func
            #self.dc = self.bound_constraint.dfunc
            #self.d2c = None
            self.m = 2.0*len(self.l)

        # General constraints.
        elif c != None and dc != None and d2c != None:
            self.c = c
            self.dc = dc
            self.d2c = d2c

        # Incorrectly supplied constraints.
        else:
            print "The constraints have been incorrectly supplied."
            self.init_failure = 1
            return

        # min_options.
        if len(min_options) == 0:
            print "The unconstrained minimisation algorithm has not been specified."
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
        self.mu = mu0
        self.epsilon = epsilon0
        self.gamma = gamma0
        self.scale_mu = scale_mu
        self.scale_epsilon = scale_epsilon
        self.scale_gamma = scale_gamma
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.maxiter = maxiter
        self.inner_maxiter = inner_maxiter
        self.full_output = full_output
        self.print_flag = print_flag

        # Set the print prefix to nothing.
        self.print_prefix = ""

        # Initialisation failure flag.
        self.init_failure = 0

        # Initialise the function, gradient, and Hessian evaluation counters.
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Initialise the warning string.
        self.warning = None

        # Initial Lagrange multipliers.
        if lambda0 == None:
            self.lambda_k = zeros(self.m, Float64)
            self.ck = apply(self.c, (self.xk,)+args)
            for i in xrange(self.m):
                #self.lambda_k[i] = init_lambda
                if self.ck[i] <= 0.0:
                    self.lambda_k[i] = init_lambda
        else:
            self.lambda_k = lambda0

        # Initialise data structures.
        self.test_str = zeros(self.m)
        self.L = apply(self.func_LA, (self.xk,)+self.args)

        # Set the convergence test function.
        self.setup_conv_tests()


    def func_LA(self, *args):
        """The augmented Lagrangian function.

        The equation is:

            L(x, lambda_k; muk) = f(x) + sum(psi(ci(x), lambdai_k; muk))

        where:

                            /  -s.t + t^2/(2m)    if t - ms <= 0,
            psi(t, s; m) = <
                            \  -ms^2/2            otherwise.
        """

        # Calculate the function and constraint values.
        self.fk = L = apply(self.func, (args[0],)+args[1:])
        self.ck = apply(self.c, (args[0],))

        # Calculate the quadratic augmented Lagrangian value.
        for i in xrange(self.m):
            if self.ck[i] <= self.mu * self.lambda_k[i]:
                L = L  -  self.lambda_k[i] * self.ck[i]  +  0.5 * self.ck[i]**2 / self.mu
                self.test_str[i] = 1
            else:
                L = L  -  0.5 * self.mu * self.lambda_k[i]**2
                self.test_str[i] = 0

        if self.print_flag >= 4:
            print ""
            print "\taug Lagr value:       " + `L`
            print "\tfunction value:       " + `self.fk`
            print "\tck:                   " + `self.ck`
            print "\tMu:                   " + `self.mu`
            print "\tck - mu.lambda_k:     " + `self.ck - self.mu * self.lambda_k`
            print "\tlambda_k - ck/mu:     " + `self.lambda_k - self.ck / self.mu`
            print "\tepsilon:              " + `self.epsilon`
            print "\tgamma:                " + `self.gamma`
            print "\tLagrange multipliers: " + `self.lambda_k`
            print "\tTest structure:       " + `self.test_str`

        return L


    def func_dLA(self, *args):
        """The augmented Lagrangian gradient."""

        # Calculate the function and constraint gradients.
        dfk = dL = apply(self.dfunc, (args[0],)+args[1:])
        self.dck = apply(self.dc, (args[0],))

        # Calculate the quadratic augmented Lagrangian gradient.
        for i in xrange(self.m):
            if self.test_str[i]:
                dL = dL  -  (self.lambda_k[i] - self.ck[i] / self.mu) * self.dck[i]

        if self.print_flag >= 4:
            print ""
            print "\taug Lagr grad:       " + `dL`
            print "\tfunction grad:       " + `dfk`
            print "\tdck:                   " + `self.dck`
            print "\tTest structure:       " + `self.test_str`

        return dL


    def func_d2LA(self, *args):
        """The quadratic augmented Lagrangian Hessian."""

        # Calculate the function and constraint Hessians.
        d2L = apply(self.d2func, (args[0],)+args[1:])
        self.d2ck = apply(self.d2c, (args[0],))

        # Calculate the quadratic augmented Lagrangian Hessian.
        for i in xrange(self.m):
            if self.test_str[i]:
                d2L = d2L  +  outerproduct(self.dck[i], self.dck[i]) / self.mu  -  (self.lambda_k[i] - self.ck[i] / self.mu) * self.d2ck[i]

        return d2L


    def func_d2LA_simple(self, *args):
        """The augmented Lagrangian Hessian.

        This function has been simplified by assuming that the constraint Hessian is zero.
        """

        # Calculate the function Hessians.
        d2L = d2fk = apply(self.d2func, (args[0],)+args[1:])

        # Calculate the quadratic augmented Lagrangian Hessian.
        for i in xrange(self.m):
            if self.test_str[i]:
                d2L = d2L  +  outerproduct(self.dck[i], self.dck[i]) / self.mu

        if self.print_flag >= 4:
            print ""
            print "\taug Lagr Hess:       " + `d2L`
            print "\tfunction Hess:       " + `d2fk`
            print "\tTest structure:       " + `self.test_str`

        return d2L


    def minimise(self):
        """Method of multipliers algorithm."""

        # Start the iteration counters.
        self.k = 0
        self.j = 0

        # Sub-algorithm print out.
        sub_print_flag = self.print_flag
        if sub_print_flag >= 2:
            sub_print_flag = sub_print_flag - 1

        # Iterate until the local minima is found.
        while 1:
            # Print out.
            if self.print_flag:
                print "\n%-3s%-8i%-4s%-65s%-4s%-20s" % ("k:", self.k, "xk:", `self.xk`, "fk:", `self.fk`)
                if self.print_flag >= 2:
                    self.printout()
                print "Entering sub-algorithm."

            # Calculate the augmented Lagrangian gradient tolerance.
            self.tk = min(self.epsilon, self.gamma*sqrt(dot(self.ck, self.ck)))

            # Maximum number of iterations for the sub-loop.
            if self.maxiter - self.j < self.inner_maxiter:
                maxiter = self.maxiter - self.j
            else:
                maxiter = self.inner_maxiter

            # Unconstrained minimisation sub-loop.
            results = self.generic_minimise(func=self.func_LA, dfunc=self.func_dLA, d2func=self.func_d2LA, args=self.args, x0=self.xk, min_algor=self.min_algor, min_options=self.min_options, func_tol=None, grad_tol=self.tk, maxiter=maxiter, full_output=1, print_flag=sub_print_flag, print_prefix="\t")
            if results == None:
                return

            # Unpack and sort the results.
            self.xk_new, self.L_new, j, f, g, h, self.temp_warning = results
            self.j, self.f_count, self.g_count, self.h_count = self.j + j, self.f_count + f, self.g_count + g, self.h_count + h
            #if self.warning != None:
            #    break

            # Maximum number of iteration test.
            if self.j >= self.maxiter - 1:
                self.warning = "Maximum number of iterations reached"
                break

            # Convergence test.
            if not hasattr(self, 'dL'):
                self.dL = apply(self.func_dLA, (self.xk_new,)+self.args)
            if self.conv_test(self.L_new, self.L, self.dL):
                break

            # Lagrange multiplier update function.
            # The update is given by the following formula:
            #    lambdai_k+1 = max(lambdai_k - ci(xk)/mu, 0)
            self.ck = apply(self.c, (self.xk_new,)+self.args)
            for i in xrange(self.m):
                self.lambda_k[i] = max(self.lambda_k[i] - self.ck[i] / self.mu, 0.0)

            # Update mu, epsilon, and gamma.
            self.mu = self.scale_mu * self.mu
            self.epsilon = self.scale_epsilon * self.epsilon
            self.gamma = self.scale_gamma * self.gamma
            if self.mu < 1e-99:
                self.warning = "Mu too small."
                break

            # Iteration counter update.
            self.xk = self.xk_new * 1.0
            self.L = self.L_new
            self.k = self.k + 1

        if self.print_flag >= 2:
            self.printout()

        # Return.
        if self.full_output:
            try:
                self.fk = apply(self.func, (self.xk_new,)+self.args)
                return self.xk_new, self.fk, self.j, self.f_count, self.g_count, self.h_count, self.warning
            except AttributeError:
                self.fk = apply(self.func, (self.xk,)+self.args)
                return self.xk, self.fk, self.j, self.f_count, self.g_count, self.h_count, self.warning
        else:
            try:
                return self.xk_new
            except AttributeError:
                return self.xk


    def printout(self):
        """Function to print out various data structures."""

        print "aug Lagr value:       " + `self.L`
        print "function value:       " + `self.fk`
        print "ck:                   " + `self.ck`
        print "Mu:                   " + `self.mu`
        print "ck - mu.lambda_k:     " + `self.ck - self.mu * self.lambda_k`
        print "epsilon:              " + `self.epsilon`
        print "gamma:                " + `self.gamma`
        print "Lagrange multipliers: " + `self.lambda_k`
        print "Test structure:       " + `self.test_str`
