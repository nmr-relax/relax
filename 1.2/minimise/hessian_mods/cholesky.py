###############################################################################
#                                                                             #
# Copyright (C) 2003, 2006 Edward d'Auvergne                                  #
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


from LinearAlgebra import cholesky_decomposition, solve_linear_equations
from Numeric import dot, sqrt, trace, transpose


def cholesky(dfk, d2fk, I, n, print_prefix, print_flag, return_matrix=0):
    """Cholesky with added multiple of the identity.

    Algorithm 6.3 from page 145 of 'Numerical Optimization' by Jorge Nocedal and Stephen J.
    Wright, 1999, 2nd ed.

    Returns the modified Newton step.
    """

    # Find the minimum diagonal value of the Hessian.
    min_aii = 1e99
    for i in xrange(n):
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
        print print_prefix + "Frobenius norm: " + `norm`
        print print_prefix + "min aii: " + `min_aii`
        print print_prefix + "tk: " + `tk`

    # Loop until the matrix is positive definite.
    while 1:
        if print_flag >= 3:
            print print_prefix + "Iteration"

        # Calculate the matrix A + tk.I
        matrix = d2fk + tk * I

        # Attempt the Cholesky decomposition.
        try:
            L = cholesky_decomposition(matrix)
            if print_flag >= 3:
                print print_prefix + "\tCholesky matrix L:"
                for i in xrange(n):
                    print print_prefix + "\t\t" + `L[i]`
        except:
            if print_flag >= 3:
                print print_prefix + "\tLinearAlgebraError, matrix is not positive definite."

            # Update of tk.
            tk = max(2.0*tk, half_norm)
        else:
            # Success, therefore break out of the while loop.
            break

    # Calculate the Newton direction.
    y = solve_linear_equations(L, dfk)
    if return_matrix:
        return -solve_linear_equations(transpose(L), y), matrix
    else:
        return -solve_linear_equations(transpose(L), y)
