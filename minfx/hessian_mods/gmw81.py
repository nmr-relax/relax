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
"""The Gill, Murray, and Wright (GMW) modified Cholesky Hessian modification algorithm.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from math import sqrt
from numpy import dot, transpose
from numpy.linalg import cholesky, eig, inv, LinAlgError, solve


def gmw(dfk, d2fk, I, n, mach_acc, print_prefix, print_flag, return_matrix=0):
    """The Gill, Murray, and Wright modified Cholesky algorithm.

    Algorithm 6.5 from page 148 of 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    Returns the modified Newton step.
    """

    # Test matrix.
    #d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], float64)
    #n = len(d2fk)
    #I = identity(n, float64)

    # Calculate gamma(A) and xi(A).
    gamma = 0.0
    xi = 0.0
    for i in range(n):
        gamma = max(abs(d2fk[i, i]), gamma)
        for j in range(i+1, n):
            xi = max(abs(d2fk[i, j]), xi)

    # Calculate delta and beta.
    delta = mach_acc * max(gamma + xi, 1.0)
    if n == 1:
        beta = sqrt(max(gamma, mach_acc))
    else:
        beta = sqrt(max(gamma, xi / sqrt(n**2 - 1.0), mach_acc))

    # Initialise data structures.
    a = 1.0 * d2fk
    r = 0.0 * d2fk
    e = 0.0 * dfk
    P = 1.0 * I

    # Debugging.
    if print_flag >= 3:
        old_eigen = eig(d2fk)
        print(print_prefix + "dfk: " + repr(dfk))
        print(print_prefix + "d2fk:\n" + repr(d2fk))

    # Main loop.
    for j in range(n):
        # Row and column swapping, find the index > j of the largest diagonal element.
        q = j
        for i in range(j+1, n):
            if abs(a[i, i]) >= abs(a[q, q]):
                q = i

        # Interchange row and column j and q (if j != q).
        if q != j:
            # Temporary permutation matrix for swaping 2 rows or columns.
            p = 1.0 * I

            # Modify the permutation matrix P by swaping columns.
            row_P = 1.0*P[:, q]
            P[:, q] = P[:, j]
            P[:, j] = row_P

            # Modify the permutation matrix p by swaping rows (same as columns because p = pT).
            row_p = 1.0*p[q]
            p[q] = p[j]
            p[j] = row_p

            # Permute a and r (p = pT).
            a = dot(p, dot(a, p))
            r = dot(r, p)

        # Calculate dj.
        theta_j = 0.0
        if j < n-1:
            for i in range(j+1, n):
                theta_j = max(theta_j, abs(a[j, i]))
        dj = max(abs(a[j, j]), (theta_j/beta)**2, delta)

        # Calculate e (not really needed!).
        if print_flag >= 3:
            e[j] = dj - a[j, j]

        # Calculate row j of r and update a.
        r[j, j] = sqrt(dj)     # Damned sqrt introduces roundoff error.
        for i in range(j+1, n):
            r[j, i] = a[j, i] / r[j, j]
            for k in range(j+1, i+1):
                a[i, k] = a[k, i] = a[k, i] - r[j, i] * r[j, k]     # Keep matrix a symmetric.

    # The Cholesky factor of d2fk.
    L = dot(P, transpose(r))

    # Debugging.
    if print_flag >= 3:
        print(print_prefix + "r:\n" + repr(r))
        print(print_prefix + "e: " + repr(e))
        print(print_prefix + "e rot: " + repr(dot(P, e)))
        print(print_prefix + "P:\n" + repr(P))
        print(print_prefix + "L:\n" + repr(L))
        print(print_prefix + "L.LT:\n" + repr(dot(L, transpose(L))))
        print(print_prefix + "L.LT - d2fk:\n" + repr(dot(L, transpose(L)) - d2fk))
        print(print_prefix + "dot(P, chol(L.LT)):\n" + repr(dot(P, cholesky(dot(L, transpose(L))))))
        print(print_prefix + "dot(P, chol(P.L.LT.PT)):\n" + repr(dot(P, cholesky(dot(P, dot(dot(L, transpose(L)), transpose(P)))))))
        E = 0.0 * d2fk
        for i in range(n):
            E[i, i] = e[i]
        E = dot(P, dot(E, transpose(P)))
        print(print_prefix + "E:\n" + repr(E))
        print(print_prefix + "PT.d2fk+E.P:\n" + repr(dot(transpose(P), dot(d2fk+E, P))))
        try:
            chol = cholesky(dot(transpose(P), dot(d2fk+E, P)))
            print(print_prefix + "chol(PT.d2fk+E.P):\n" + repr(chol))
            print(print_prefix + "rT - chol(PT.d2fk+E.P):\n" + repr(transpose(r) - chol))
            chol = dot(P, chol)
            print(print_prefix + "chol:\n" + repr(chol))
            print(print_prefix + "chol reconstructed:\n" + repr(dot(chol, transpose(chol))))
        except LinAlgError:
            print(print_prefix + "Matrix is not positive definite - Cholesky decomposition cannot be computed.")
        eigen = eig(dot(L, transpose(L)))
        print(print_prefix + "Old eigenvalues: " + repr(old_eigen))
        print(print_prefix + "New eigenvalues: " + repr(eigen))
        print(print_prefix + "Newton dir: " + repr(-solve(transpose(L), solve(L, dfk))))
        print(print_prefix + "Newton dir using inverse: " + repr(-dot(inv(d2fk+E), dfk)))

    # Calculate the Newton direction.
    y = solve(L, dfk)
    if return_matrix:
        return -solve(transpose(L), y), dot(L, transpose(L))
    else:
        return -solve(transpose(L), y)
