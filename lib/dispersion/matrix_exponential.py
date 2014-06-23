###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
from numpy import array, any, diag, dot, einsum, eye, exp, iscomplex, newaxis, multiply, tile
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
        return array(eA)

    # Return only the real part.
    else:
        return array(eA.real)


def matrix_exponential_rankN(A):
    """Calculate the exact matrix exponential using the eigenvalue decomposition approach, for higher dimensional data.

    Here X is the Row and Column length, of the outer square matrix.

    @param A:   The square matrix to calculate the matrix exponential of.
    @type A:    numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    @return:    The matrix exponential.  This will have the same dimensionality as the A matrix.
    @rtype:     numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    """

    # Set initial to None.
    NE, NS, NM, NO, ND, Row, Col = None, None, None, None, None, None, None

    if len(A.shape) == 7:
        NE, NS, NM, NO, ND, Row, Col = A.shape
    elif len(A.shape) == 6:
        NS, NM, NO, ND, Row, Col = A.shape

    # Is the original matrix real?
    complex_flag = any(iscomplex(A))

    # The eigenvalue decomposition.
    W, V = eig(A)

    # W: The eigenvalues, each repeated according to its multiplicity.
    # The eigenvalues are not necessarily ordered.
    # The resulting array will be always be of complex type. Shape [NE][NS][NM][NO][ND][X]
    # V: The normalized (unit 'length') eigenvectors, such that the column v[:,i]
    # is the eigenvector corresponding to the eigenvalue w[i]. Shape [NE][NS][NM][NO][ND][X][X]

    # Calculate the exponential of all elements in the input array. Shape [NE][NS][NM][NO][ND][X]
    # Add one axis, to allow for broadcasting multiplication.
    if NE == None:
        W_exp = exp(W).reshape(NS, NM, NO, ND, Row, 1)
    else:
        W_exp = exp(W).reshape(NE, NS, NM, NO, ND, Row, 1)

    # Make a eye matrix, with Shape [NE][NS][NM][NO][ND][X][X]
    if NE == None:
        eye_mat = tile(eye(Row)[newaxis, newaxis, newaxis, newaxis, ...], (NS, NM, NO, ND, 1, 1) )
    else:
        eye_mat = tile(eye(Row)[newaxis, newaxis, newaxis, newaxis, newaxis, ...], (NE, NS, NM, NO, ND, 1, 1) )

    # Transform it to a diagonal matrix, with elements from vector down the diagonal.
    W_exp_diag = multiply(W_exp, eye_mat )

    # Make dot products for higher dimension.
    # "...", the Ellipsis notation, is designed to mean to insert as many full slices (:)
    # to extend the multi-dimensional slice to all dimensions.
    dot_V_W = einsum('...ij,...jk', V, W_exp_diag)

    # Compute the (multiplicative) inverse of a matrix.
    inv_V = inv(V)

    # Calculate the exact exponential.
    eA = einsum('...ij,...jk', dot_V_W, inv_V)

    # Return the complex matrix.
    if complex_flag:
        return array(eA)

    # Return only the real part.
    else:
        return array(eA.real)