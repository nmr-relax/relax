###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
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
"""Module for the calculation of the Kronecker product."""

# Python imports.
from numpy import outer



def kron_prod(A, B):
    """Calculate the Kronecker product of the matrices A and B.

    @param A:   ixj matrix.
    @type A:    rank-2 numpy array
    @param B:   kxl matrix.
    @type B:    rank-2 numpy array
    @return:    The Kronecker product.
    @rtype:     ikxjl rank-2 numpy array
    """

    # The outer product.
    C = outer(A, B)

    # Redefine the shape.
    orig_shape = C.shape
    C.shape = A.shape + B.shape

    # Generate and return the Kronecker product matrix.
    transpose_23(C)
    C.shape = orig_shape
    return C


def transpose_12(matrix):
    """Perform the 1,2 transpose of a rank-4, 3D tensor.

    @param matrix:  The rank-4 tensor either in (9, 9) shape for a matrix or the (3, 3, 3, 3) shape
                    for the tensor form.
    @type matrix:   numpy array
    """

    # Reshape if necessary.
    reshape = False
    if matrix.shape == (9, 9):
        reshape = True
        matrix.shape = (3, 3, 3, 3)

    # Perform the transpose.
    for i in range(3):
        for j in range(i, 3):
            for k in range(3):
                for l in range(3):
                    # Store the element.
                    element = matrix[i, j, k, l]

                    # Overwrite.
                    matrix[i, j, k, l] = matrix[j, i, k, l]
                    matrix[j, i, k, l] = element

    # Undo the reshape.
    if reshape:
        matrix.shape = (9, 9)


def transpose_13(matrix):
    """Perform the 1,3 transpose of a rank-4, 3D tensor.

    @param matrix:  The rank-4 tensor either in (9, 9) shape for a matrix or the (3, 3, 3, 3) shape
                    for the tensor form.
    @type matrix:   numpy array
    """

    # Reshape if necessary.
    reshape = False
    if matrix.shape == (9, 9):
        reshape = True
        matrix.shape = (3, 3, 3, 3)

    # Perform the transpose.
    for i in range(3):
        for j in range(3):
            for k in range(i, 3):
                for l in range(3):
                    # Store the element.
                    element = matrix[i, j, k, l]

                    # Overwrite.
                    matrix[i, j, k, l] = matrix[k, j, i, l]
                    matrix[k, j, i, l] = element

    # Undo the reshape.
    if reshape:
        matrix.shape = (9, 9)


def transpose_14(matrix):
    """Perform the 1,4 transpose of a rank-4, 3D tensor.

    @param matrix:  The rank-4 tensor either in (9, 9) shape for a matrix or the (3, 3, 3, 3) shape
                    for the tensor form.
    @type matrix:   numpy array
    """

    # Reshape if necessary.
    reshape = False
    if matrix.shape == (9, 9):
        reshape = True
        matrix.shape = (3, 3, 3, 3)

    # Perform the transpose.
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(i, 3):
                    # Store the element.
                    element = matrix[i, j, k, l]

                    # Overwrite.
                    matrix[i, j, k, l] = matrix[l, j, k, i]
                    matrix[l, j, k, i] = element

    # Undo the reshape.
    if reshape:
        matrix.shape = (9, 9)


def transpose_23(matrix):
    """Perform the 2,3 transpose of a rank-4, 3D tensor.

    @param matrix:  The rank-4 tensor either in (9, 9) shape for a matrix or the (3, 3, 3, 3) shape
                    for the tensor form.
    @type matrix:   numpy array
    """

    # Reshape if necessary.
    reshape = False
    if matrix.shape == (9, 9):
        reshape = True
        matrix.shape = (3, 3, 3, 3)

    # Perform the transpose.
    for i in range(3):
        for j in range(3):
            for k in range(j, 3):
                for l in range(3):
                    # Store the element.
                    element = matrix[i, j, k, l]

                    # Overwrite.
                    matrix[i, j, k, l] = matrix[i, k, j, l]
                    matrix[i, k, j, l] = element

    # Undo the reshape.
    if reshape:
        matrix.shape = (9, 9)


def transpose_24(matrix):
    """Perform the 2,4 transpose of a rank-4, 3D tensor.

    @param matrix:  The rank-4 tensor either in (9, 9) shape for a matrix or the (3, 3, 3, 3) shape
                    for the tensor form.
    @type matrix:   numpy array
    """

    # Reshape if necessary.
    reshape = False
    if matrix.shape == (9, 9):
        reshape = True
        matrix.shape = (3, 3, 3, 3)

    # Perform the transpose.
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(j, 3):
                    # Store the element.
                    element = matrix[i, j, k, l]

                    # Overwrite.
                    matrix[i, j, k, l] = matrix[i, l, k, j]
                    matrix[i, l, k, j] = element

    # Undo the reshape.
    if reshape:
        matrix.shape = (9, 9)


def transpose_34(matrix):
    """Perform the 3,4 transpose of a rank-4, 3D tensor.

    @param matrix:  The rank-4 tensor either in (9, 9) shape for a matrix or the (3, 3, 3, 3) shape
                    for the tensor form.
    @type matrix:   numpy array
    """

    # Reshape if necessary.
    reshape = False
    if matrix.shape == (9, 9):
        reshape = True
        matrix.shape = (3, 3, 3, 3)

    # Perform the transpose.
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(k, 3):
                    # Store the element.
                    element = matrix[i, j, k, l]

                    # Overwrite.
                    matrix[i, j, k, l] = matrix[i, j, l, k]
                    matrix[i, j, l, k] = element

    # Undo the reshape.
    if reshape:
        matrix.shape = (9, 9)
