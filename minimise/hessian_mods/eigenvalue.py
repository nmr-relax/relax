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


from LinearAlgebra import eigenvectors, inverse
from Numeric import matrixmultiply, sort


def eigenvalue(dfk, d2fk, I, print_prefix, print_flag, return_matrix=0):
    """The eigenvalue Hessian modification.

    This modification is based on equation 6.14 from page 144 of 'Numerical Optimization' by
    Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    Returns the modified Newton step.
    """

    # Calculate the eigenvalues.
    eigen = eigenvectors(d2fk)
    eigenvals = sort(eigen[0])

    # Modify the Hessian if the smallest eigenvalue is negative.
    tau = None
    if eigenvals[0] < 0.0:
        tau = max(0.0, 1e-2 - eigenvals[0])
        matrix = d2fk + tau * I
    else:
        matrix = d2fk

    # Debugging.
    if print_flag >= 3:
        eigen_new = eigenvectors(matrix)
        eigenvals_new = sort(eigen_new[0])
        print print_prefix + "d2fk:\n" + `d2fk`
        print print_prefix + "eigenvals(d2fk): " + `eigenvals`
        print print_prefix + "tau: " + `tau`
        print print_prefix + "matrix:\n" + `matrix`
        print print_prefix + "eigenvals(matrix): " + `eigenvals_new`
        print print_prefix + "Newton dir: " + `-matrixmultiply(inverse(matrix), dfk)`

    # Calculate the Newton direction.
    if return_matrix:
        return -matrixmultiply(inverse(matrix), dfk), matrix
    else:
        return -matrixmultiply(inverse(matrix), dfk)
