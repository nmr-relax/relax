###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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
from Numeric import Float64, array, dot, identity, matrixmultiply, sort, sqrt, transpose
from re import match

from base_classes import Line_search, Min


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


class Newton(Line_search, Min):
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
            self.line_search_algor = 'More Thuente'

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


    def cholesky(self, return_matrix=0):
        """Cholesky with added multiple of the identity.

        Algorithm 6.3 from page 145 of 'Numerical Optimization' by Jorge Nocedal and Stephen J.
        Wright, 1999, 2nd ed.

        Returns the modified Newton step.
        """

        # Calculate the Frobenius norm of the Hessian and the minimum diagonal value.
        norm = 0.0
        min_aii = 1e99
        for i in range(self.n):
            min_aii = min(self.d2fk[i, i], min_aii)
            for j in range(self.n):
                norm = norm + self.d2fk[i, j]**2
        norm = sqrt(norm)
        half_norm = norm / 2.0

        if min_aii > 0.0:
            tk = 0.0
        else:
            tk = half_norm

        if self.print_flag >= 3:
            print self.print_prefix + "Frobenius norm: " + `norm`
            print self.print_prefix + "min aii: " + `min_aii`
            print self.print_prefix + "tk: " + `tk`

        k = 0
        while 1:
            if self.print_flag >= 3:
                print self.print_prefix + "Iteration " + `k`

            # Calculate the matrix A + tk.I
            matrix = self.d2fk + tk * self.I

            try:
                self.L = cholesky_decomposition(matrix)
                if self.print_flag >= 3:
                    print self.print_prefix + "\tCholesky matrix L:"
                    for i in range(self.n):
                        print self.print_prefix + "\t\t" + `self.L[i]`
                break
            except "LinearAlgebraError":
                if self.print_flag >= 3:
                    print self.print_prefix + "\tLinearAlgebraError, matrix is not positive definite."
                tk = max(2.0*tk, half_norm)

            k = k + 1

        # Calculate the Newton direction.
        y = solve_linear_equations(self.L, self.dfk)
        if return_matrix:
            return -solve_linear_equations(transpose(self.L), y), matrix
        else:
            return -solve_linear_equations(transpose(self.L), y)


    def eigenvalue(self, return_matrix=0):
        """The eigenvalue Hessian modification.

        This modification is based on equation 6.14 from page 144 of 'Numerical Optimization' by
        Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

        Returns the modified Newton step.
        """

        if self.print_flag >= 3:
            print self.print_prefix + "d2fk: " + `self.d2fk`

        eigen = eigenvectors(self.d2fk)
        eigenvals = sort(eigen[0])
        tau = max(0.0, self.delta - eigenvals[0])
        matrix = self.d2fk + tau * self.I

        # Debugging.
        if self.print_flag >= 3:
            print self.print_prefix + "Eigenvalues: " + `eigenvals`
            print self.print_prefix + "tau: " + `tau`
            print self.print_prefix + "d2fk: " + `matrix`

        # Calculate the Newton direction.
        if return_matrix:
            return -matrixmultiply(inverse(matrix), self.dfk), matrix
        else:
            return -matrixmultiply(inverse(matrix), self.dfk)


    def gmw(self, return_matrix=0):
        """The Gill, Murray, and Wright modified Cholesky algorithm.

        Algorithm 6.5 from page 148 of 'Numerical Optimization' by Jorge Nocedal and Stephen J.
        Wright, 1999, 2nd ed.

        Returns the modified Newton step.
        """

        self.d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], Float64)

        # Calculate gamma(A) and xi(A).
        gamma = 0.0
        xi = 0.0
        for i in range(self.n):
            gamma = max(abs(self.d2fk[i, i]), gamma)
            for j in range(i+1, self.n):
                xi = max(abs(self.d2fk[i, j]), xi)

        # Calculate delta and beta.
        delta = self.mach_acc * max(gamma + xi, 1.0)
        if self.n == 1:
            beta = sqrt(max(gamma, self.mach_acc))
        else:
            beta = sqrt(max(gamma, xi / sqrt(self.n**2 - 1.0), self.mach_acc))

        # Initialise data structures.
        a = 1.0 * self.d2fk
        c = 0.0 * self.d2fk
        l = 0.0 * self.d2fk
        d = 0.0 * self.xk
        e = 0.0 * self.xk
        P = 1.0 * self.I

        if self.print_flag >= 3:
            old_eigen = eigenvectors(self.d2fk)
            print self.print_prefix + "dfk: " + `self.dfk`
            print self.print_prefix + "d2fk:"
            for i in range(len(self.d2fk)):
                print self.print_prefix + "\t" + `self.d2fk[i]`

        # Initialise the diagonal elements.
        for k in range(self.n):
            c[k, k] = a[k, k]

        # Main loop.
        for j in range(self.n):
            # Row and column swapping.
            q = j
            for i in range(j, self.n):
                if abs(c[i, i]) >= abs(c[q, q]):
                    q = i

            # Interchange row and column j and q.
            p = 1.0 * self.I
            if q != j:
                # Modify the permutation matrices.
                temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
                p[:, q], P[:, q] = p[:, j], P[:, j]
                p[:, j], P[:, j] = temp_p, temp_P

                # Permute a and r.
                a = dot(p, dot(a, p))
                c = dot(p, dot(c, p))
                l = dot(p, dot(l, p))
                d = dot(p, dot(d, p))
                e = dot(p, dot(e, p))

            # Calculate l[j, s].
            for s in range(j):
                l[j, s] = c[j, s] / d[s]

            # Calculate c[i, j].
            for i in range(j+1, self.n):
                sum = 0.0
                for s in range(j-1):
                    sum = sum + l[j, s] * c[i, s]
                c[i, j] = a[i, j] - sum

            # Calculate theta_j.
            theta_j = 0.0
            if j < self.n-1:
                for i in range(j+1, self.n):
                    theta_j = max(theta_j, abs(c[i, j]))

            # Calculate d[j].
            d[j] = max(abs(c[j, j]), (theta_j/beta)**2, delta)

            # Calculate e (not really needed!).
            e[j] = d[j] - c[j, j]

            # Calculate c[i, i].
            if j < self.n-1:
                for i in range(j+1, self.n):
                    c[i, i] = c[i, i] - c[i, j]**2 / d[j]

        # Permutation of c.
        matrix = dot(P, dot(c, P))

        if self.print_flag >= 3:
            print self.print_prefix + "e: " + `dot(P, dot(e, transpose(P)))`
            print self.print_prefix + "d: " + `dot(P, dot(d, transpose(P)))`
            print self.print_prefix + "P:"
            for i in range(len(P)):
                print self.print_prefix + "\t" + `P[i]`
            print self.print_prefix + "c:"
            for i in range(len(c)):
                print self.print_prefix + "\t" + `c[i]`
            print self.print_prefix + "d2fk reconstruted:"
            for i in range(len(matrix)):
                print self.print_prefix + "\t" + `matrix[i]`
            eigen = eigenvectors(matrix)
            print self.print_prefix + "Old eigenvalues: " + `old_eigen[0]`
            print self.print_prefix + "New eigenvalues: " + `eigen[0]`
            sorted = sort(old_eigen[0])
            if sorted[0] > 0.0:
                for i in range(len(e)):
                    if e[i] != 0.0:
                        print self.print_prefix + "\n### Fail ###\n"
                        import sys
                        sys.exit()

        import sys
        sys.exit()
        # Calculate the Newton direction.
        if return_matrix:
            return -matrixmultiply(inverse(matrix), self.dfk), matrix
        else:
            return -matrixmultiply(inverse(matrix), self.dfk)

        # Calculate the Newton direction.
        #y = solve_linear_equations(self.L, self.dfk)
        #if return_matrix:
        #    return -solve_linear_equations(transpose(self.L), y), dot(self.L, transpose(self.L))
        #else:
        #    return -solve_linear_equations(transpose(self.L), y)


    def gmw_good(self, return_matrix=0):
        """The Gill, Murray, and Wright modified Cholesky algorithm.

        Algorithm 6.5 from page 148 of 'Numerical Optimization' by Jorge Nocedal and Stephen J.
        Wright, 1999, 2nd ed.

        Returns the modified Newton step.
        """

        #self.d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], Float64)

        # Calculate gamma(A) and xi(A).
        gamma = 0.0
        xi = 0.0
        for i in range(self.n):
            gamma = max(abs(self.d2fk[i, i]), gamma)
            for j in range(i+1, self.n):
                xi = max(abs(self.d2fk[i, j]), xi)

        # Calculate delta and beta.
        delta = self.mach_acc * max(gamma + xi, 1.0)
        if self.n == 1:
            beta = sqrt(max(gamma, self.mach_acc))
        else:
            beta = sqrt(max(gamma, xi / sqrt(self.n**2 - 1.0), self.mach_acc))

        # Initialise data structures.
        a = self.d2fk
        r = 0.0 * self.d2fk
        e = 0.0 * self.xk
        P = 1.0 * self.I

        if self.print_flag >= 3:
            old_eigen = eigenvectors(self.d2fk)
            print self.print_prefix + "dfk: " + `self.dfk`
            print self.print_prefix + "d2fk:"
            for i in range(len(self.d2fk)):
                print self.print_prefix + "\t" + `self.d2fk[i]`

        # Main loop.
        for j in range(self.n):
            # Row and column swapping.
            q = j
            for i in range(j, self.n):
                if abs(a[i, i]) >= abs(a[q, q]):
                    q = i

            # Interchange row and column j and q.
            p = 1.0 * self.I
            if q != j:
                # Modify the permutation matrices.
                temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
                p[:, q], P[:, q] = p[:, j], P[:, j]
                p[:, j], P[:, j] = temp_p, temp_P

                # Permute a and r.
                a = dot(p, dot(a, p))
                r = dot(p, dot(r, p))

            # Calculate ljj.
            theta_j = 0.0
            if j < self.n-1:
                for i in range(j+1, self.n):
                    theta_j = max(theta_j, abs(a[j, i]))
            dj = max(abs(a[j, j]), (theta_j/beta)**2, delta)
            r[j, j] = sqrt(dj)

            # Calculate e (not really needed!).
            e[j] = dj - a[j, j]

            # Calculate l and a.
            for i in range(j+1, self.n):
                r[j, i] = a[j, i] / r[j, j]
                for k in range(j+1, i+1):
                    a[k, i] = a[k, i] - dot(r[j, i], r[j, k])

        # The Cholesky factor.
        self.L = dot(P, transpose(r))

        if self.print_flag >= 3:
            print self.print_prefix + "e: " + `dot(P, dot(e, transpose(P)))`
            print self.print_prefix + "P:"
            for i in range(len(P)):
                print self.print_prefix + "\t" + `P[i]`
            temp = dot(self.L,transpose(self.L))
            print self.print_prefix + "d2fk reconstruted:"
            for i in range(len(temp)):
                print self.print_prefix + "\t" + `temp[i]`
            eigen = eigenvectors(temp)
            print self.print_prefix + "Old eigenvalues: " + `old_eigen[0]`
            print self.print_prefix + "New eigenvalues: " + `eigen[0]`
            sorted = sort(old_eigen[0])
            if sorted[0] > 0.0:
                for i in range(len(e)):
                    if e[i] != 0.0:
                        print self.print_prefix + "\n### Fail ###\n"
                        import sys
                        sys.exit()

        # Calculate the Newton direction.
        y = solve_linear_equations(self.L, self.dfk)
        if return_matrix:
            return -solve_linear_equations(transpose(self.L), y), dot(self.L, transpose(self.L))
        else:
            return -solve_linear_equations(transpose(self.L), y)


    def gmw_old(self, return_matrix=0):
        """Modified Cholesky hessian modification.

        Algorithm 6.5 from page 148.

        Somehow the data structures l, d, and c can be stored in self.d2fk!
        """

        # Debugging (REMOVE!!!).
        #self.d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], Float64)
        if self.print_flag >= 3:
            print "d2fk: " + `self.d2fk`
            eigen = eigenvectors(self.d2fk)
            eigenvals = sort(eigen[0])
            print "Eigenvalues: " + `eigenvals`

        # Calculate gamma(A) and xi(A).
        gamma = 0.0
        xi = 0.0
        for i in range(self.n):
            gamma = max(abs(self.d2fk[i, i]), gamma)
            for j in range(i+1, self.n):
                xi = max(abs(self.d2fk[i, j]), xi)

        # Calculate delta and beta.
        delta = self.mach_acc * max(gamma + xi, 1)
        beta = sqrt(max(gamma, xi / sqrt(self.n**2 - 1.0), self.mach_acc))

        # Initialise data structures.
        d2fk_orig = 1.0 * self.d2fk
        c = 0.0 * self.d2fk
        d = 0.0 * self.xk
        l = 1.0 * self.I
        e = 0.0 * self.xk
        P = 1.0 * self.I

        # Initial diagonal elements of c.
        for k in range(self.n):
            c[k, k] = self.d2fk[k, k]

        # Main loop.
        for j in range(self.n):
            if self.print_flag >= 3:
                print "\n<j: " + `j` + ">"

            # Row and column swapping.
            p = 1.0 * self.I
            q = j
            for i in range(j, self.n):
                if abs(c[q, q]) <= abs(c[i, i]):
                    q = i
            if self.print_flag >= 3:
                print "Row and column swapping."
                print "i range: " + `range(j, self.n)`
                print "q: " + `q`
                print "a: " + `self.d2fk`
                print "c: " + `c`
                print "d: " + `d`
                print "l: " + `l`
            if q != j:
                # Modify the permutation matrices.
                temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
                p[:, q], P[:, q] = p[:, j], P[:, j]
                p[:, j], P[:, j] = temp_p, temp_P

                # Permute both c and d2fk.
                c = dot(p, dot(c, p))
                self.d2fk = dot(p, dot(self.d2fk, p))

                if self.print_flag >= 3:
                    print "p: " + `p`
                    print "a(mod): " + `self.d2fk`
                    print "c(mod): " + `c`
                    print "d(mod): " + `d`
                    print "l(mod): " + `l`

            # Calculate the elements of l.
            if self.print_flag >= 3:
                print "\nCalculate the elements of l."
                print "s range: " + `range(j)`
            for s in range(j):
                if self.print_flag >= 3:
                    print "s: " + `s`
                l[j, s] = c[j, s] / d[s]
            if self.print_flag >= 3:
                print "l: " + `l`

            # Calculate c[i, j].
            if self.print_flag >= 3:
                print "\nCalculate c[i, j]."
                print "i range: " + `range(j+1, self.n)`
            for i in range(j+1, self.n):
                sum = 0.0
                for s in range(j):
                    if self.print_flag >= 3:
                        print "s range: " + `range(j)`
                    sum = sum + l[j, s] * c[i, s]
                c[i, j] = self.d2fk[i, j] - sum
            if self.print_flag >= 3:
                print "c: " + `c`

            # Calculate d.
            if self.print_flag >= 3:
                print "\nCalculate d."
            theta_j = 0.0
            if j < self.n-1:
                if self.print_flag >= 3:
                    print "j < n, " + `j` + " < " + `self.n-1`
                    print "i range: " + `range(j+1, self.n)`
                for i in range(j+1, self.n):
                    theta_j = max(theta_j, abs(c[i, j]))
            else:
                if self.print_flag >= 3:
                    print "j >= n, " + `j` + " >= " + `self.n-1`
            d[j] = max(abs(c[j, j]), (theta_j/beta)**2, delta)
            if self.print_flag >= 3:
                print "theta_j: " + `theta_j`
                print "d: " + `d`

            # Calculate c[i, i].
            if self.print_flag >= 3:
                print "\nCalculate c[i, i]."
            if j < self.n-1:
                if self.print_flag >= 3:
                    print "j < n, " + `j` + " < " + `self.n-1`
                    print "i range: " + `range(j+1, self.n)`
                for i in range(j+1, self.n):
                    c[i, i] = c[i, i] - c[i, j]**2 / d[j]
            else:
                if self.print_flag >= 3:
                    print "j >= n, " + `j` + " >= " + `self.n-1`
            if self.print_flag >= 3:
                print "c: " + `c`

            # Calculate e.
            e[j] = d[j] - c[j, j]

        for i in range(self.n):
            self.d2fk[i, i] = self.d2fk[i, i] + e[i]
        self.d2fk = dot(P, dot(self.d2fk, transpose(P)))

        # Debugging.
        if self.print_flag >= 3:
            print "\nFin:"
            print "gamma(A): " + `gamma`
            print "xi(A): " + `xi`
            print "delta: " + `delta`
            print "beta: " + `beta`
            print "c: " + `c`
            print "d: " + `d`
            print "l: " + `l`
            temp = 0.0 * self.I
            for i in range(len(d)):
                temp[i, i] = d[i]
            print "m: " + `dot(l, sqrt(temp))`
            print "mmT: " + `dot(dot(l, sqrt(temp)), transpose(dot(l, sqrt(temp))))`
            print "P: " + `P`
            print "e: " + `e`
            print "d2fk: " + `self.d2fk`
            eigen = eigenvectors(self.d2fk)
            eigenvals = sort(eigen[0])
            print "Eigenvalues: " + `eigenvals`
            import sys
            sys.exit()

        # Calculate the Newton direction.
        if return_matrix:
            return -matrixmultiply(inverse(self.d2fk), self.dfk), self.d2fk
        else:
            return -matrixmultiply(inverse(self.d2fk), self.dfk)


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
            print self.print_prefix + "pk:    " + `self.pk`
            print self.print_prefix + "alpha: " + `self.alpha`
            print self.print_prefix + "xk:    " + `self.xk`
            print self.print_prefix + "xk+1:  " + `self.xk_new`
            print self.print_prefix + "fk:    " + `self.fk`
            print self.print_prefix + "fk+1:  " + `self.fk_new`
            eigen = eigenvectors(self.d2fk)
            print self.print_prefix + "B:"
            for i in range(self.n):
                print self.print_prefix + `self.d2fk[i]`
            print self.print_prefix + "Eigenvalues: " + `eigen[0]`


    def setup_hessian_mod(self):
        """Initialise the Hessian modification functions."""

        if self.hessian_mod == None or match('[Nn]one', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  Unmodified Hessian."
            self.get_pk = self.unmodified_hessian
        elif match('^[Ee]igen', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  Eigenvalue modification."
            self.get_pk = self.eigenvalue
            self.delta = sqrt(self.mach_acc)
        elif match('^[Cc]hol', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  Cholesky with added multiple of the identity."
            self.get_pk = self.cholesky
        elif match('^[Gg][Mm][Ww]', self.hessian_mod):
            if self.print_flag:
                print self.print_prefix + "Hessian modification:  The Gill, Murray, and Wright modified Cholesky algorithm."
            self.get_pk = self.gmw_old
            #self.get_pk = self.gmw
            #self.get_pk = self.gmw_good


    def setup_newton(self):
        """Setup function.

        The initial Newton function value, gradient vector, and Hessian matrix are calculated.
        """

        self.fk, self.f_count = apply(self.func, (self.xk,)+self.args), self.f_count + 1
        self.dfk, self.g_count = apply(self.dfunc, (self.xk,)+self.args), self.g_count + 1
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


    def unmodified_hessian(self, return_matrix=0):
        """Calculate the pure Newton direction."""

        if return_matrix:
            return -matrixmultiply(inverse(self.d2fk), self.dfk), self.d2fk
        else:
            return -matrixmultiply(inverse(self.d2fk), self.dfk)


    def update_newton(self):
        """Function to update the function value, gradient vector, and Hessian matrix."""

        self.xk = self.xk_new * 1.0
        self.fk = self.fk_new
        self.dfk = self.dfk_new * 1.0
        self.d2fk, self.h_count = apply(self.d2func, (self.xk,)+self.args), self.h_count + 1


    def valid_hessian_mod(self, mod):
        """Test if the string 'mod' is a valid Hessian modification."""

        if mod == None or match('^[Ee]igen', mod) or match('^[Cc]hol', mod) or match('^[Gg][Mm][Ww]', mod) or match('^[Nn]one', mod):
            return 1
        else:
            return 0
