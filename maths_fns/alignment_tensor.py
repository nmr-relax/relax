###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Module for the manipulation of alignment tensors."""

# Python imports.
from numpy.linalg import eigvals


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
