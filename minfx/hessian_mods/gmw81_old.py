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

Warning:  This code is not currently functional.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import dot, sort, sqrt, transpose
from numpy.linalg import eig, inv


def gmw_old(dfk, d2fk, I, n, mach_acc, print_prefix, print_flag, return_matrix=0):
    """Modified Cholesky Hessian modification.

    Algorithm 6.5 from page 148.

    Somehow the data structures l, d, and c can be stored in d2fk!
    """

    # Debugging (REMOVE!!!).
    #d2fk = array([[4, 2, 1], [2, 6, 3], [1, 3, -0.004]], float64)

    if print_flag >= 3:
        print("d2fk: " + repr(d2fk))
        eigen = eig(d2fk)
        eigenvals = sort(eigen[0])
        print("Eigenvalues: " + repr(eigenvals))

    # Calculate gamma(A) and xi(A).
    gamma = 0.0
    xi = 0.0
    for i in range(n):
        gamma = max(abs(d2fk[i, i]), gamma)
        for j in range(i+1, n):
            xi = max(abs(d2fk[i, j]), xi)

    # Calculate delta and beta.
    delta = mach_acc * max(gamma + xi, 1)
    beta = sqrt(max(gamma, xi / sqrt(n**2 - 1.0), mach_acc))

    # Initialise data structures.
    d2fk_orig = 1.0 * d2fk
    c = 0.0 * d2fk
    d = 0.0 * dfk
    l = 1.0 * I
    e = 0.0 * dfk
    P = 1.0 * I

    # Initial diagonal elements of c.
    for k in range(n):
        c[k, k] = d2fk[k, k]

    # Main loop.
    for j in range(n):
        if print_flag >= 3:
            print("\n<j: " + repr(j) + ">")

        # Row and column swapping.
        p = 1.0 * I
        q = j
        for i in range(j, n):
            if abs(c[q, q]) <= abs(c[i, i]):
                q = i
        if print_flag >= 3:
            print("Row and column swapping.")
            print("i range: " + repr(range(j, n)))
            print("q: " + repr(q))
            print("a: " + repr(d2fk))
            print("c: " + repr(c))
            print("d: " + repr(d))
            print("l: " + repr(l))
        if q != j:
            # Modify the permutation matrices.
            temp_p, temp_P = 1.0*p[:, q], 1.0*P[:, q]
            p[:, q], P[:, q] = p[:, j], P[:, j]
            p[:, j], P[:, j] = temp_p, temp_P

            # Permute both c and d2fk.
            c = dot(p, dot(c, p))
            d2fk = dot(p, dot(d2fk, p))

            if print_flag >= 3:
                print("p: " + repr(p))
                print("a(mod): " + repr(d2fk))
                print("c(mod): " + repr(c))
                print("d(mod): " + repr(d))
                print("l(mod): " + repr(l))

        # Calculate the elements of l.
        if print_flag >= 3:
            print("\nCalculate the elements of l.")
            print("s range: " + repr(range(j)))
        for s in range(j):
            if print_flag >= 3:
                print("s: " + repr(s))
            l[j, s] = c[j, s] / d[s]
        if print_flag >= 3:
            print("l: " + repr(l))

        # Calculate c[i, j].
        if print_flag >= 3:
            print("\nCalculate c[i, j].")
            print("i range: " + repr(range(j+1, n)))
        for i in range(j+1, n):
            sum = 0.0
            for s in range(j):
                if print_flag >= 3:
                    print("s range: " + repr(range(j)))
                sum = sum + l[j, s] * c[i, s]
            c[i, j] = d2fk[i, j] - sum
        if print_flag >= 3:
            print("c: " + repr(c))

        # Calculate d.
        if print_flag >= 3:
            print("\nCalculate d.")
        theta_j = 0.0
        if j < n-1:
            if print_flag >= 3:
                print("j < n, " + repr(j) + " < " + repr(n-1))
                print("i range: " + repr(range(j+1, n)))
            for i in range(j+1, n):
                theta_j = max(theta_j, abs(c[i, j]))
        else:
            if print_flag >= 3:
                print("j >= n, " + repr(j) + " >= " + repr(n-1))
        d[j] = max(abs(c[j, j]), (theta_j/beta)**2, delta)
        if print_flag >= 3:
            print("theta_j: " + repr(theta_j))
            print("d: " + repr(d))

        # Calculate c[i, i].
        if print_flag >= 3:
            print("\nCalculate c[i, i].")
        if j < n-1:
            if print_flag >= 3:
                print("j < n, " + repr(j) + " < " + repr(n-1))
                print("i range: " + repr(range(j+1, n)))
            for i in range(j+1, n):
                c[i, i] = c[i, i] - c[i, j]**2 / d[j]
        else:
            if print_flag >= 3:
                print("j >= n, " + repr(j) + " >= " + repr(n-1))
        if print_flag >= 3:
            print("c: " + repr(c))

        # Calculate e.
        e[j] = d[j] - c[j, j]

    for i in range(n):
        d2fk[i, i] = d2fk[i, i] + e[i]
    d2fk = dot(P, dot(d2fk, transpose(P)))

    # Debugging.
    if print_flag >= 3:
        print("\nFin:")
        print("gamma(A): " + repr(gamma))
        print("xi(A): " + repr(xi))
        print("delta: " + repr(delta))
        print("beta: " + repr(beta))
        print("c: " + repr(c))
        print("d: " + repr(d))
        print("l: " + repr(l))
        temp = 0.0 * I
        for i in range(len(d)):
            temp[i, i] = d[i]
        print("m: " + repr(dot(l, sqrt(temp))))
        print("mmT: " + repr(dot(dot(l, sqrt(temp)), transpose(dot(l, sqrt(temp))))))
        print("P: " + repr(P))
        print("e: " + repr(e))
        print("d2fk: " + repr(d2fk))
        eigen = eig(d2fk)
        eigenvals = sort(eigen[0])
        print("Eigenvalues: " + repr(eigenvals))
        import sys
        sys.exit()

    # Calculate the Newton direction.
    if return_matrix:
        return -dot(inv(d2fk), dfk), d2fk
    else:
        return -dot(inv(d2fk), dfk)
