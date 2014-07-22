###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Module for the calculation of the matrix exponential, for higher dimensional data."""

# Python module imports.
from numpy import array, any, einsum, eye, exp, iscomplex, newaxis, multiply, tile
from numpy.linalg import eig, inv

# relax module imports.
from lib.check_types import is_complex


def matrix_exponential_rank_NE_NS_NM_NO_ND_x_x(A, dtype=None):
    """Calculate the exact matrix exponential using the eigenvalue decomposition approach, for higher dimensional data.  This of dimension [NS][NS][NM][NO][ND][X][X].

    Here X is the Row and Column length, of the outer square matrix.

    @param A:       The square matrix to calculate the matrix exponential of.
    @type A:        numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    @param dtype:   If provided, forces the calculation to use the data type specified.
    @type type:     data-type, optional
    @return:        The matrix exponential.  This will have the same dimensionality as the A matrix.
    @rtype:         numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    """

   # Extract shape.
    NE, NS, NM, NO, ND, Row, Col = A.shape

    # Convert dtype, if specified.
    if dtype != None:
        dtype_mat = A.dtype

        # If the dtype is different from the input.
        if dtype_mat != dtype:
            # This needs to be made as a copy.
            A = A.astype(dtype)

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
    W_exp = exp(W).reshape(NE, NS, NM, NO, ND, Row, 1)

    # Make a eye matrix, with Shape [NE][NS][NM][NO][ND][X][X]
    eye_mat = tile(eye(Row)[newaxis, newaxis, newaxis, newaxis, newaxis, ...], (NE, NS, NM, NO, ND, 1, 1) )

    # Transform it to a diagonal matrix, with elements from vector down the diagonal.
    # Use the dtype, if specified.
    if dtype != None:
        W_exp_diag = multiply(W_exp, eye_mat, dtype=dtype )
    else:
        W_exp_diag = multiply(W_exp, eye_mat)

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


def matrix_exponential_rank_NS_NM_NO_ND_x_x(A, dtype=None):
    """Calculate the exact matrix exponential using the eigenvalue decomposition approach, for higher dimensional data.  This of dimension [NS][NM][NO][ND][X][X].

    Here X is the Row and Column length, of the outer square matrix.

    @param A:       The square matrix to calculate the matrix exponential of.
    @type A:        numpy float array of rank [NS][NM][NO][ND][X][X]
    @param dtype:   If provided, forces the calculation to use the data type specified.
    @type type:     data-type, optional
    @return:        The matrix exponential.  This will have the same dimensionality as the A matrix.
    @rtype:         numpy float array of rank [NS][NM][NO][ND][X][X]
    """

    # Extract shape.
    NS, NM, NO, ND, Row, Col = A.shape

    # Convert dtype, if specified.
    if dtype != None:
        dtype_mat = A.dtype

        # If the dtype is different from the input.
        if dtype_mat != dtype:
            # This needs to be made as a copy.
            A = A.astype(dtype)

    # Is the original matrix real?
    complex_flag = any(iscomplex(A))

    # The eigenvalue decomposition.
    W, V = eig(A)

    # W: The eigenvalues, each repeated according to its multiplicity.
    # The eigenvalues are not necessarily ordered.
    # The resulting array will be always be of complex type. Shape [NS][NM][NO][ND][X]
    # V: The normalized (unit 'length') eigenvectors, such that the column v[:,i]
    # is the eigenvector corresponding to the eigenvalue w[i]. Shape [NS][NM][NO][ND][X][X]

    # Calculate the exponential of all elements in the input array. Shape [NS][NM][NO][ND][X]
    # Add one axis, to allow for broadcasting multiplication.
    W_exp = exp(W).reshape(NS, NM, NO, ND, Row, 1)

    # Make a eye matrix, with Shape [NE][NS][NM][NO][ND][X][X]
    eye_mat = tile(eye(Row)[newaxis, newaxis, newaxis, newaxis, ...], (NS, NM, NO, ND, 1, 1) )

    # Transform it to a diagonal matrix, with elements from vector down the diagonal.
    # Use the dtype, if specified.
    if dtype != None:
        W_exp_diag = multiply(W_exp, eye_mat, dtype=dtype )
    else:
        W_exp_diag = multiply(W_exp, eye_mat)

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