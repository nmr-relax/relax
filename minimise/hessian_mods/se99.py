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

from LinearAlgebra import LinAlgError, cholesky_decomposition, eigenvalues, solve_linear_equations
from MLab import tril
from Numeric import Float64, array, dot, identity, sort, sqrt, take, transpose, zeros


def se99(dfk, d2fk, I, n, tau, tau_bar, mu, print_prefix, print_flag, return_matrix=0):
    """A revised modified cholesky factorisation algorithm.

    Schnabel, R. B. and Eskow, E. 1999, A revised modifed cholesky factorisation algorithm.
    SIAM J. Optim. 9, 1135-1148.
    """

    # Test matrix.
    d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], Float64)
    d2fk = array([[  1890.3, -1750.6,  -315.8,  3000.3],
                  [ -1705.6,  1538.3,   284.9, -2706.6],
                  [  -315.8,   284.9,    52.5,  -501.2],
                  [  3000.3, -2706.6,  -501.2,  4760.8]], Float64)
    n = len(d2fk)
    I = identity(n, Float64)

    # Create the matrices A and L.
    A = 1.0 * d2fk
    L = 0.0 * d2fk

    # Permutation matrix.
    P = 1.0 * I

    # Calculate gamma.
    gamma = abs(d2fk[0, 0])
    for i in xrange(n):
        gamma = max(abs(d2fk[i, i]), gamma)

    # Debugging.
    E = 0.0 * d2fk
    if print_flag >= 3:
        print print_prefix + "tau:     " + `tau`
        print print_prefix + "tau_bar: " + `tau_bar`
        print print_prefix + "mu:      " + `mu`
        print print_prefix + "d2fk:\n" + `d2fk`
        print print_prefix + "Orig A:\n" + `A`
        print print_prefix + "Orig L:\n" + `L`
        print print_prefix + "gamma: " + `gamma`


    # Phase one, A potentially positive definite.
    #############################################

    for j in xrange(n):
        if print_flag >= 3:
            print "\n" + print_prefix + "Iteration j = " + `j`
            print print_prefix + "Init A:\n" + `A`
            print print_prefix + "Init L:\n" + `L`
            print print_prefix + "Phase 1."

        # Calculate max_Aii and min_Aii
        max_Aii = A[j, j]
        min_Aii = A[j, j]
        for i in xrange(j, n):
            max_Aii = max(A[i, i], max_Aii)
            min_Aii = min(A[i, i], min_Aii)

        # Test for phase 2, A not positive definite.
        if max_Aii < tau_bar * gamma or min_Aii < - mu * max_Aii:
            exec_phasetwo(A, L, P, I, E, j, n, tau, tau_bar, gamma, print_prefix, print_flag)
            break

        else:
            # Pivot on maximum diagonal of remaining submatrix.
            i = j
            for k in xrange(j, n):
                if A[k, k] >= A[i, i]:
                    i = k

            # Interchange row and column i and j.
            p = 1.0 * I
            if i != j:
                if print_flag >= 3:
                    print print_prefix + "Switching rows and columns of " + `i` + " and " + `j` + " of A and L."

                # Modify the permutation matrices by swaping rows.
                row_p, row_P = 1.0*p[i], 1.0*P[i]
                p[i], P[i] = p[j], P[j]
                p[j], P[j] = row_p, row_P

                # Permute A.
                A = dot(p, dot(A, transpose(p)))
                L = dot(p, dot(L, transpose(p)))

                if print_flag >= 3:
                    print print_prefix + "Permuted A:\n" + `A`
                    print print_prefix + "Permuted L:\n" + `L`

            # Test for phase 2 again.
            min_num = 1e99
            for i in xrange(j+1, n):
                min_num = min(min_num, A[i, i] - A[i, j]**2 / A[j, j])
            if j+1 <= n and min_num < - mu * gamma:
                exec_phasetwo(A, L, P, I, E, j, n, tau, tau_bar, gamma, print_prefix, print_flag)
                break

            # Perform jth iteration of factorisation.
            else:
                jiter_factor(A, L, j, n)

            # Debugging.
            if print_flag >= 3:
                print print_prefix + "Factorised A:\n" + `A`
                print print_prefix + "Factorised L:\n" + `L`
                #import sys
                #sys.exit()

    # The Cholesky factor.
    L = dot(P, L)

    # Debugging.
    if print_flag >= 3:
        print "\n" + print_prefix + "Fin"
        print print_prefix + "d2fk:\n" + `d2fk`
        print print_prefix + "A:\n" + `A`
        print print_prefix + "L:\n" + `L`
        try:
            print print_prefix + "chol:\n" + `cholesky_decomposition(d2fk)`
        except LinAlgError:
            print print_prefix + "Matrix is not positive definite - Cholesky decomposition cannot be computed."
        print print_prefix + "E:\n" + `E`
        print print_prefix + "P:\n" + `P`
        print print_prefix + "Reconstructed d2fk:\n" + `dot(L, transpose(L))`
        print print_prefix + "d2fk + E:\n" + `d2fk + dot(P, dot(E, P))`

    import sys
    sys.exit()

    # Calculate the Newton direction.
    y = solve_linear_equations(L, dfk)
    if return_matrix:
        return -solve_linear_equations(transpose(L), y), dot(L, transpose(L))
    else:
        return -solve_linear_equations(transpose(L), y)


def exec_phasetwo(A, L, P, I, E, j, n, tau, tau_bar, gamma, print_prefix, print_flag):
    """Phase 2 of the algorithm, A not positive definite."""

    # Debugging.
    if print_flag >= 3:
        print print_prefix + "Phase 2."

    if j == n:
        # delta = Enn.
        delta = -A[n-1, n-1] + max(-tau*A[n-1, n-1] / (1.0 - tau), tau_bar*gamma)
        if print_flag >= 3:
            print print_prefix + "delta: " + `delta`
            E[n-1, n-1] = delta
        A[n-1, n-1] = A[n-1, n-1] + delta
        L[n-1, n-1] = sqrt(A[n-1, n-1])

    else:
        # Number of iterations performed in phase one (less 1).
        k = j - 1

        # Calculate the lower Gerschgorin bounds of Ak+1.
        g = zeros(n, Float64)
        for i in xrange(k+1, n):
            sum_Aij = 0.0
            for s in xrange(k+1, i-1):
                sum_Aij = sum_Aij + abs(A[i, j])
            sum_Aji = 0.0
            for s in xrange(i+1, n):
                sum_Aji = sum_Aji + abs(A[j, i])
            g[i] = A[i, i] - sum_Aij - sum_Aji
        if print_flag >= 3:
            print print_prefix + "g: " + `g`

        # Modified Cholesky decomposition.
        delta_prev = 0.0
        for j in xrange(k+1, n-2):
            # Pivot on the maximum lower Gerschgorin bound estimate.
            i = j
            for k in xrange(j, n):
                if g[k] >= g[i]:
                    i = k

            # Interchange row and column i and j.
            p = 1.0 * I
            if i != j:
                if print_flag >= 3:
                    print print_prefix + "Switching rows and columns of " + `i` + " and " + `j` + " of A and L."

                # Modify the permutation matrices by swaping rows.
                row_p, row_P = 1.0*p[i], 1.0*P[i]
                p[i], P[i] = p[j], P[j]
                p[j], P[j] = row_p, row_P

                # Permute A.
                A = dot(p, dot(A, transpose(p)))
                L = dot(p, dot(L, transpose(p)))

                if print_flag >= 3:
                    print print_prefix + "Permuted A:\n" + `A`
                    print print_prefix + "Permuted L:\n" + `L`

            # Calculate Ejj and add to diagonal.
            normj = 0
            for i in xrange(j+1, n):
                normj = normj + abs(A[i, j])
            delta = max(0.0, -A[j, j] + max(normj, tau_bar*gamma), delta_prev)  # delta = Enn.
            if delta > 0.0:
                A[j, j] = A[j, j] + delta
                delta_prev = delta
            if print_flag >= 3:
                print print_prefix + "delta: " + `delta`
                E[j, j] = delta

            # Update Gerschgorin bound estimates.
            if A[j, j] != normj:
                temp = 1.0 - normj / A[j, j]
                for i in xrange(j+1, n):
                    g[i] = g[i] + abs(A[i, j]) * temp

            # Perform jth iteration of factorisation.
            jiter_factor(A, L, j, n)

        # Final 2*2 submatrix.
        mini = take(take(A, [n-2, n-1]), [n-2, n-1], 1)
        mini[0, 1] = mini[1, 0]
        eigenvals = sort(eigenvalues(mini))
        delta = max(0.0, -eigenvals[0] + max(tau*(eigenvals[1] - eigenvals[0])/(1.0 - tau), tau_bar*gamma), delta_prev)
        if delta > 0.0:
            A[n-2, n-2] = A[n-2, n-2] + delta
            A[n-1, n-1] = A[n-1, n-1] + delta
            delta_prev = delta
        if print_flag >= 3:
            print print_prefix + "delta: " + `delta`
            E[n-2, n-2] = E[n-1, n-1] = delta

        L[n-2, n-2] = sqrt(A[n-2, n-2])
        L[n-1, n-2] = A[n-1, n-2] / L[n-2, n-2]
        L[n-1, n-1] = sqrt(A[n-1, n-1] - L[n-1, n-2]**2)

        if print_flag >= 3:
            print print_prefix + "mini:\n" + `mini`
            print print_prefix + "eigenvals: " + `eigenvals`
            print print_prefix + "Factorised A:\n" + `A`
            print print_prefix + "Factorised L:\n" + `L`


def jiter_factor(A, L, j, n):
    """Perform jth iteration of factorisation."""

    L[j, j] = sqrt(A[j, j])
    for i in xrange(j+1, n):
        L[i, j] = A[i, j] / L[j, j]
        for k in xrange(j+1, i+1):
            A[i, k] = A[i, k] - L[i, j]*L[k, j]
