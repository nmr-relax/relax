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

from LinearAlgebra import cholesky_decomposition, solve_linear_equations
from MLab import tril
from Numeric import dot, sqrt, transpose


def se99(dfk, d2fk, I, n, tau, tau_bar, mu, print_prefix, print_flag, return_matrix=0):
    """A revised modified cholesky factorisation algorithm.

    Schnabel, R. B. and Eskow, E. 1999, A revised modifed cholesky factorisation algorithm.
    SIAM J. Optim. 9, 1135-1148.
    """

    # Create the matrix A which is n*n symmetric stored in lower triangular form.
    A = tril(d2fk)

    # Calculate gamma.
    gamma = abs(d2fk[0, 0])
    for i in range(n):
        gamma = max(abs(d2fk[i, i]), gamma)

    # Permutation matrix.
    #P = 1.0 * I

    # Debugging.
    if print_flag >= 3:
        print print_prefix + "tau:     " + `tau`
        print print_prefix + "tau_bar: " + `tau_bar`
        print print_prefix + "mu:      " + `mu`
        print print_prefix + "d2fk:\n" + `d2fk`
        print print_prefix + "A:\n" + `A`
        print print_prefix + "gamma: " + `gamma`


    # Phase one, A potentially positive definite.
    #############################################

    for j in range(n):
        # Calculate max_Aii and min_Aii
        max_Aii = A[j, j]
        min_Aii = A[j, j]
        for i in range(j, n):
            max_Aii = max(A[i, i], max_Aii)
            min_Aii = min(A[i, i], min_Aii)

        # Test for phase 2, A not positive definite.
        if max_Aii < tau_bar * gamma or min_Aii < - mu * max_Aii:
            exec_phasetwo(j, n, print_prefix, print_flag)

        else:
            ## Pivot on maximum diagonal of remaining submatrix.
            #i = j
            #for k in range(j, n):
            #    if A[k, k] >= A[i, i]:
            #        i = k

            ## Interchange row and column i and j.
            #p = 1.0 * I
            #if i != j:
            #    # Modify the permutation matrices.
            #    temp_p, temp_P = 1.0*p[:, i], 1.0*P[:, i]
            #    p[:, i], P[:, i] = p[:, j], P[:, j]
            #    p[:, j], P[:, j] = temp_p, temp_P

            #    # Permute A.
            #    if print_flag >= 3:
            #        print print_prefix + "Switching rows and columns of " + `i` + " and " + `j` + " of A."
            #        print print_prefix + "A:\n" + `A`
            #    #A = A + transpose(tril(A, -1))
            #    #print print_prefix + "A:\n" + `A`
            #    A = dot(p, dot(A, p))
            #    l = dot(p, dot(l, p))
            #    #print print_prefix + "A:\n" + `A`
            #    #A = tril(A)
            #    #print print_prefix + "A:\n" + `A`
            #    if print_flag >= 3:
            #        print print_prefix + "A:\n" + `A`

            min_num = 1e99
            for i in range(j+1, n):
                min_num = min(min_num, A[i, i] - A[i, j]**2 / A[j, j])

            # Test for phase 2 again.
            if j+1 <= n and min_num < - mu * gamma:
                exec_phasetwo(print_prefix, print_flag)

            # Perform jth iteration of factorisation.
            else:
                A[j, j] = sqrt(A[j, j])
                for i in range(j+1, n):
                    A[i, j] = A[i, j] / A[j, j]
                    for k in range(j+1, i+1):
                        A[i, k] = A[i, k] - A[i, j]*A[k, j]

    # The Cholesky factor.
    #L = dot(P, dot(A, P))

    # Debugging.
    if print_flag >= 3:
        print "\n" + print_prefix + "Fin"
        print print_prefix + "A:\n" + `A`
        #print print_prefix + "L:\n" + `L`
        #print print_prefix + "P:\n" + `P`
        print print_prefix + "chol:\n" + `cholesky_decomposition(d2fk)`

    # Calculate the Newton direction.
    y = solve_linear_equations(A, dfk)
    if return_matrix:
        return -solve_linear_equations(transpose(A), y), dot(A, transpose(A))
    else:
        return -solve_linear_equations(transpose(A), y)


def exec_phasetwo(A, j, n, tau, tau_bar, gamma, print_prefix, print_flag):
    """Phase 2 of the algorithm, A not positive definite."""

    if j == n:
        # Enn.
        delta = -A[n, n] + max(-tau*A[n, n] / (1.0 - tau), tau_bar*gamma)
        A[n, n] = A[n, n] + delta
        A[n, n] = sqrt(A[n, n])

    else:
        # Number of iterations performed in phase one.
        k = j - 1


    # Debugging.
    if print_flag >= 3:
        print print_prefix + "Phase 2."
        print print_prefix + "A:\n" + `A`

    print "Exit"
    import sys
    sys.exit()

