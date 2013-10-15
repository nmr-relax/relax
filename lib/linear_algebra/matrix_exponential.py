###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
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
"""Module for the calculation of the matrix exponential."""

# Python module imports.
from numpy import diag, dot, exp, iscomplex
from numpy.linalg import eig, inv

# relax module imports.
from lib.check_types import is_complex


def matrix_exponential(A):
    """Calculate the exact matrix exponential using the eigenvalue decomposition approach.

    @param A:   The square matrix to calculate the matrix exponential of.
    @type A:    numpy rank-2 array
    @return:    The matrix exponential.  This will have the same dimensionality as the A matrix.
    @rtype:     numpy rank-2 array
    """

    # Is the original matrix real?
    complex_flag = is_complex(A[0, 0])

    # The eigenvalue decomposition.
    W, V = eig(A)

    # Calculate the exact exponential.
    eA = dot(dot(V, diag(exp(W))), inv(V))

    # Return the complex matrix.
    if complex_flag:
        return eA

    # Return only the real part.
    else:
        return eA.real
