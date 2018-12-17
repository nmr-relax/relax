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
"""Cholesky Hessian modification with added multiple of the identity.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import dot, sqrt, trace, transpose
from numpy.linalg import LinAlgError, cholesky, solve


def cholesky_mod(dfk, d2fk, I, n, print_prefix, print_flag, return_matrix=0):
    """Cholesky with added multiple of the identity.

    Algorithm 6.3 from page 145 of 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    Returns the modified Newton step.
    """

    # Find the minimum diagonal value of the Hessian.
    min_aii = 1e99
    for i in range(n):
        min_aii = min(d2fk[i, i], min_aii)

    # Calculate the Frobenius norm of the Hessian.
    norm = sqrt(trace(dot(d2fk, d2fk)))
    half_norm = norm / 2.0

    # Choose the initial tk value.
    if min_aii > 0.0:
        tk = 0.0
    else:
        tk = half_norm

    # Debugging.
    if print_flag >= 3:
        print(print_prefix + "Frobenius norm: " + repr(norm))
        print(print_prefix + "min aii: " + repr(min_aii))
        print(print_prefix + "tk: " + repr(tk))

    # Loop until the matrix is positive definite.
    while True:
        if print_flag >= 3:
            print(print_prefix + "Iteration")

        # Calculate the matrix A + tk.I
        matrix = d2fk + tk * I

        # Attempt the Cholesky decomposition.
        try:
            L = cholesky(matrix)
            if print_flag >= 3:
                print(print_prefix + "\tCholesky matrix L:")
                for i in range(n):
                    print(print_prefix + "\t\t" + repr(L[i]))
        except LinAlgError:
            if print_flag >= 3:
                print(print_prefix + "\tLinearAlgebraError, matrix is not positive definite.")

            # Update of tk.
            tk = max(2.0*tk, half_norm)
        else:
            # Success, therefore break out of the while loop.
            break

    # Calculate the Newton direction.
    y = solve(L, dfk)
    if return_matrix:
        return -solve(transpose(L), y), matrix
    else:
        return -solve(transpose(L), y)
