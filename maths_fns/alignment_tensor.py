###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful;                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the manipulation of alignment tensors."""

# Python imports.
from numpy.linalg import eigvals


def dAi_dAxx(A):
    """The dAi/dAxx gradient.

    This function will modify the A matrix to be equal to::

      dAi   | 1  0  0 |
     ---- = | 0  0  0 |
     dAxx   | 0  0 -1 |


    @param A:   The alignment tensor object.
    @type A:    numpy rank-2 3D tensor
    """

    # Set all elements.
    A[0, 0] = 1.0;  A[0, 1] = 0.0;  A[0, 2] = 0.0
    A[1, 0] = 0.0;  A[1, 1] = 0.0;  A[1, 2] = 0.0
    A[2, 0] = 0.0;  A[2, 1] = 0.0;  A[2, 2] = -1.0


def dAi_dAyy(A):
    """The dAi/dAyy gradient.

    This function will modify the A matrix to be equal to::

      dAi   | 0  0  0 |
     ---- = | 0  1  0 |
     dAyy   | 0  0 -1 |


    @param A:   The alignment tensor object.
    @type A:    numpy rank-2 3D tensor
    """

    # Set all elements.
    A[0, 0] = 0.0;  A[0, 1] = 0.0;  A[0, 2] = 0.0
    A[1, 0] = 0.0;  A[1, 1] = 1.0;  A[1, 2] = 0.0
    A[2, 0] = 0.0;  A[2, 1] = 0.0;  A[2, 2] = -1.0


def dAi_dAxy(A):
    """The dAi/dAxy gradient.

    This function will modify the A matrix to be equal to::

      dAi   | 0  1  0 |
     ---- = | 1  0  0 |
     dAxy   | 0  0  0 |


    @param A:   The alignment tensor object.
    @type A:    numpy rank-2 3D tensor
    """

    # Set all elements.
    A[0, 0] = 0.0;  A[0, 1] = 1.0;  A[0, 2] = 0.0
    A[1, 0] = 1.0;  A[1, 1] = 0.0;  A[1, 2] = 0.0
    A[2, 0] = 0.0;  A[2, 1] = 0.0;  A[2, 2] = 0.0


def dAi_dAxz(A):
    """The dAi/dAxz gradient.

    This function will modify the A matrix to be equal to::

      dAi   | 0  0  1 |
     ---- = | 0  0  0 |
     dAxz   | 1  0  0 |


    @param A:   The alignment tensor object.
    @type A:    numpy rank-2 3D tensor
    """

    # Set all elements.
    A[0, 0] = 0.0;  A[0, 1] = 0.0;  A[0, 2] = 1.0
    A[1, 0] = 0.0;  A[1, 1] = 0.0;  A[1, 2] = 0.0
    A[2, 0] = 1.0;  A[2, 1] = 0.0;  A[2, 2] = 0.0


def dAi_dAyz(A):
    """The dAi/dAyz gradient.

    This function will modify the A matrix to be equal to::

      dAi   | 0  0  0 |
     ---- = | 0  0  1 |
     dAyz   | 0  1  0 |


    @param A:   The alignment tensor object.
    @type A:    numpy rank-2 3D tensor
    """

    # Set all elements.
    A[0, 0] = 0.0;  A[0, 1] = 0.0;  A[0, 2] = 0.0
    A[1, 0] = 0.0;  A[1, 1] = 0.0;  A[1, 2] = 1.0
    A[2, 0] = 0.0;  A[2, 1] = 1.0;  A[2, 2] = 0.0


def maxA(tensor):
    """Find the maximal alignment - the Azz component in the alignment frame.

    @param tensor:      The alignment tensor object.
    @type tensor:       numpy rank-2 3D tensor
    @return:            The Azz component in the alignment frame.
    """

    # Return the value.
    return max(abs(eigvals(tensor)))


def to_5D(vector_5D, tensor):
    """Convert the rank-2 3D alignment tensor matrix to the 5D vector format.

    @param vector_5D:   The 5D vector object to populate.  The vector format is {Axx, Ayy, Axy, Axz,
                        Ayz}.
    @type vector_5D:    numpy 5D vector
    @param tensor:      The alignment tensor object.
    @type tensor:       numpy rank-2 3D tensor
    """

    # Convert the matrix form to the vector form.
    vector_5D[0] = tensor[0, 0]
    vector_5D[1] = tensor[1, 1]
    vector_5D[2] = tensor[0, 1]
    vector_5D[3] = tensor[0, 2]
    vector_5D[4] = tensor[1, 2]


def to_tensor(tensor, vector_5D):
    """Convert the 5D vector alignment tensor form to the rank-2 3D matrix from.

    @param tensor:      The alignment tensor object, in matrix format, to populate.
    @type tensor:       numpy rank-2 3D tensor
    @param vector_5D:   The 5D vector object.  The vector format is {Axx, Ayy, Axy, Axz, Ayz}.
    @type vector_5D:    numpy 5D vector
    """

    # Convert the vector form to the matrix form.
    tensor[0, 0] = vector_5D[0]
    tensor[0, 1] = vector_5D[2]
    tensor[0, 2] = vector_5D[3]
    tensor[1, 0] = vector_5D[2]
    tensor[1, 1] = vector_5D[1]
    tensor[1, 2] = vector_5D[4]
    tensor[2, 0] = vector_5D[3]
    tensor[2, 1] = vector_5D[4]
    tensor[2, 2] = -vector_5D[0] -vector_5D[1]
