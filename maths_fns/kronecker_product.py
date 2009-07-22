###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module for the calculation of the Kronecker product."""

# Python imports.
from numpy import concatenate, outer



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
    C.shape = A.shape + B.shape

    # Generate and return the Kronecker product matrix.
    return transpose_14(C, A.shape + B.shape)


def transpose_14(C, shape=(3,3,3,3)):
    """Perform the transpose of axes 1 and 4.

    @param A:       ixj matrix.
    @type A:        rank-2 numpy array
    @keyword shape: The rank-4 shape of the matrix A.
    @type shape:    tuple of 4 int
    @return:        A with axes 1 and 4 transposed.
    @rtype:         rank-2 numpy array
    """

    # Redefine the shape.
    orig_shape = C.shape
    C.shape = shape

    # Generate the transposed matrix.
    C_T14 = concatenate(concatenate(C, axis=1), axis=1)

    # Restore the shape of C.
    C.shape = orig_shape

    # Return the transposed matrix.
    return C_T14
