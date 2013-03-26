###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Module for the manipulation of alignment tensors."""

# Python imports.
from numpy.linalg import eigvals

# relax module imports.
from lib.physical_constants import g1H, h_bar, kB, mu0, return_gyromagnetic_ratio


def calc_chi_tensor(A, B0, T):
    """Convert the alignment tensor into the magnetic susceptibility (chi) tensor.

    A can be either the full tensor (3D or 5D), a component Aij of the tensor, Aa, or Ar, anything that can be multiplied by the constants to convert from one to the other.


    @param A:       The alignment tensor or alignment tensor component.
    @type A:        numpy array or float
    @param B0:      The magnetic field strength in Hz.
    @type B0:       float
    @param T:       The temperature in Kalvin.
    @type T:        float
    @return:        A multiplied by the PCS constant.
    @rtype:         numpy array or float
    """

    # B0 in Tesla.
    B0 = 2.0 * pi * B0 / g1H

    # The conversion factor.
    conv = 15.0 * mu0 * kB * T / B0**2

    # Return the converted value.
    return conv * A


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


def kappa(nuc1='15N', nuc2='1H'):
    """Function for calculating the kappa constant.

    The kappa constant is::

        kappa = -3/(8pi^2).gI.gS.mu0.h_bar,

    where gI and gS are the gyromagnetic ratios of the I and S spins, mu0 is the permeability of
    free space, and h_bar is Planck's constant divided by 2pi.

    @param nuc1:    The first nucleus type.
    @type nuc1:     str
    @param nuc2:    The first nucleus type.
    @type nuc2:     str
    @return:        The kappa constant value.
    @rtype:         float
    """

    # Gyromagnetic ratios.
    gI = return_gyromagnetic_ratio(nuc1)
    gS = return_gyromagnetic_ratio(nuc2)

    # Kappa.
    return -3.0/(8.0*pi**2) * gI * gS * mu0 * h_bar


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
