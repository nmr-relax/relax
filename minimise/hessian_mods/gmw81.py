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


from LinearAlgebra import eigenvectors, solve_linear_equations
from Numeric import Float64, array, dot, sqrt, transpose


def gmw(dfk, d2fk, I, n, mach_acc, print_prefix, print_flag, return_matrix=0):
    """The Gill, Murray, and Wright modified Cholesky algorithm.

    Algorithm 6.5 from page 148 of 'Numerical Optimization' by Jorge Nocedal and Stephen J.
    Wright, 1999, 2nd ed.

    Returns the modified Newton step.
    """

    #d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], Float64)

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
    #P = 1.0 * I

    # Debugging.
    if print_flag >= 3:
        old_eigen = eigenvectors(d2fk)
        print print_prefix + "dfk: " + `dfk`
        print print_prefix + "d2fk:\n" + `d2fk`

    # Main loop.
    for j in range(n):
        ## Row and column swapping.
        #q = j
        #for i in range(j, n):
        #    if abs(a[i, i]) >= abs(a[q, q]):
        #        q = i

        ## Interchange row and column j and q.
        #p = 1.0 * I
        #if q != j:
        #    # Modify the permutation matrices.
        #    temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
        #    p[:, q], P[:, q] = p[:, j], P[:, j]
        #    p[:, j], P[:, j] = temp_p, temp_P

        #    # Permute a and r.
        #    a = dot(p, dot(a, p))
        #    r = dot(p, dot(r, p))
        #    e = dot(p, e)

        # Calculate ljj.
        theta_j = 0.0
        if j < n-1:
            for i in range(j+1, n):
                theta_j = max(theta_j, abs(a[j, i]))
        dj = max(abs(a[j, j]), (theta_j/beta)**2, delta)
        r[j, j] = sqrt(dj)

        # Calculate e (not really needed!).
        e[j] = dj - a[j, j]

        # Calculate l and a.
        for i in range(j+1, n):
            r[j, i] = a[j, i] / r[j, j]
            for k in range(j+1, i+1):
                a[k, i] = a[k, i] - dot(r[j, i], r[j, k])

    # The Cholesky factor.
    L = transpose(r)
    #L = dot(P, transpose(r))

    # Debugging.
    if print_flag >= 3:
        print print_prefix + "e: " + `e`
        #print print_prefix + "e: " + `dot(P, e)`
        #print print_prefix + "P:\n" + `P`
        temp = dot(L,transpose(L))
        print print_prefix + "d2fk reconstruted:\n" + `temp`
        eigen = eigenvectors(temp)
        print print_prefix + "Old eigenvalues: " + `old_eigen[0]`
        print print_prefix + "New eigenvalues: " + `eigen[0]`

    # Calculate the Newton direction.
    y = solve_linear_equations(L, dfk)
    if return_matrix:
        return -solve_linear_equations(transpose(L), y), dot(L, transpose(L))
    else:
        return -solve_linear_equations(transpose(L), y)
