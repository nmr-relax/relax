###############################################################################
#                                                                             #
# Copyright (C) 2001-2004,2006-2009,2011-2012,2014-2015 Edward d'Auvergne     #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2008 Sebastien Morin                                          #
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
"""The alignment tensor objects of the relax data store."""

# Python module imports.
from math import pi, sqrt
from numpy import eye, float64, zeros
from numpy.linalg import det, eig, eigvals
from re import search

# relax module imports.
from data_store.data_classes import Element
from lib.float import nan
from lib.geometry.rotations import R_to_euler_zyz
from lib.errors import RelaxError
from lib.xml import fill_object_contents, xml_to_object


# Constants (once off calculations for speed).
fact_A2 = sqrt(2.0*pi / 15.0)
fact_A1 = sqrt(8.0*pi / 15.0)
fact_A0 = sqrt(4.0*pi / 5.0)


def calc_A(Axx, Ayy, Azz, Axy, Axz, Ayz):
    """Function for calculating the alignment tensor (in the structural frame).

    @param Axx:     The Axx tensor element.
    @type Axx:      float
    @param Ayy:     The Ayy tensor element.
    @type Ayy:      float
    @param Azz:     The Azz tensor element.
    @type Azz:      float
    @param Axy:     The Axy tensor element.
    @type Axy:      float
    @param Axz:     The Axz tensor element.
    @type Axz:      float
    @param Ayz:     The Ayz tensor element.
    @type Ayz:      float
    @return:        The alignment tensor (within the structural frame).
    @rtype:         3x3 numpy float64 array
    """

    # Initialise the tensor.
    tensor = zeros((3, 3), float64)

    # Populate the diagonal elements.
    tensor[0, 0] = Axx
    tensor[1, 1] = Ayy
    tensor[2, 2] = Azz

    # Populate the off diagonal elements.
    tensor[0, 1] = tensor[1, 0] = Axy
    tensor[0, 2] = tensor[2, 0] = Axz
    tensor[1, 2] = tensor[2, 1] = Ayz

    # Return the tensor.
    return tensor


def calc_A_5D(Axx, Ayy, Azz, Axy, Axz, Ayz):
    """Function for calculating the alignment tensor in the 5D vector notation.

    @param Axx:     The Axx tensor element.
    @type Axx:      float
    @param Ayy:     The Ayy tensor element.
    @type Ayy:      float
    @param Azz:     The Azz tensor element.
    @type Azz:      float
    @param Axy:     The Axy tensor element.
    @type Axy:      float
    @param Axz:     The Axz tensor element.
    @type Axz:      float
    @param Ayz:     The Ayz tensor element.
    @type Ayz:      float
    @return:        The alignment 5D tensor (within the structural frame).
    @rtype:         numpy rank-1 5D tensor
    """

    # Initialise the tensor.
    tensor = zeros(5, float64)

    # Populate the tensor.
    tensor[0] = Axx
    tensor[1] = Ayy
    tensor[2] = Axy
    tensor[3] = Axz
    tensor[4] = Ayz

    # Return the tensor.
    return tensor


def calc_A_diag(A):
    """Calculate the diagonalised alignment tensor.

    The diagonalised alignment tensor is defined as::

                   | Axx'  0    0  |
        tensor  =  |  0   Ayy'  0  |.
                   |  0    0   Azz'|

    The diagonalised alignment tensor is calculated by eigenvalue decomposition.


    @param A:   The full alignment tensor.
    @type A:    numpy array ((3, 3), float64)
    @return:    The diagonalised alignment tensor.
    @rtype:     numpy array ((3, 3), float64)
    """

    # The eigenvalues.
    vals = eigvals(A)

    # Find the |x| < |y| < |z| indices.
    abs_vals = abs(vals).tolist()
    Axx_index = abs_vals.index(min(abs_vals))
    Azz_index = abs_vals.index(max(abs_vals))
    last_index = list(range(3))
    last_index.pop(max(Axx_index, Azz_index))
    last_index.pop(min(Axx_index, Azz_index))
    Ayy_index = last_index[0]

    # Empty tensor.
    tensor_diag = zeros((3, 3), float64)

    # Fill the elements.
    tensor_diag[0, 0] = vals[Axx_index]
    tensor_diag[1, 1] = vals[Ayy_index]
    tensor_diag[2, 2] = vals[Azz_index]

    # Return the tensor.
    return tensor_diag


def calc_Aa(A_diag):
    """Calculate the anisotropic parameter Aa.

    This is given by::

        Aa = 3/2Azz = Szz,

    where Azz and Szz are the eigenvalues.


    @param A_diag:  The full alignment tensor, diagonalised.
    @type A_diag:   numpy array ((3, 3), float64)
    @return:        The Aa parameter
    @rtype:         float
    """

    # Return Aa.
    return 1.5 * A_diag[2, 2]


def calc_Ar(A_diag):
    """Calculate the rhombic parameter Ar.

    This is given by::

        Ar = Axx - Ayy,

    where Axx and Ayy are the eigenvalues.


    @param A_diag:  The full alignment tensor, diagonalised.
    @type A_diag:   numpy array ((3, 3), float64)
    @return:        The Ar parameter
    @rtype:         float
    """

    # Return Ar.
    return A_diag[0, 0] - A_diag[1, 1]


def calc_Axxyy(Axx, Ayy):
    """Function for calculating the Axx-yy value.

    The equation for calculating the parameter is::

        Axx-yy  =  Axx - Ayy.

    @param Axx:     The Axx component of the alignment tensor.
    @type Axx:      float
    @param Ayy:     The Ayy component of the alignment tensor.
    @type Ayy:      float
    @return:        The Axx-yy component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Axx-yy value.
    return Axx - Ayy


def calc_Azz(Axx, Ayy):
    """Function for calculating the Azz value.

    The equation for calculating the parameter is::

        Azz  =  - Axx - Ayy.

    @param Axx:     The Axx component of the alignment tensor.
    @type Axx:      float
    @param Ayy:     The Ayy component of the alignment tensor.
    @type Ayy:      float
    @return:        The Azz component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Azz value.
    return - Axx - Ayy


def calc_eigvals(A):
    """Calculate the eigenvalues and eigenvectors of the alignment tensor (A).

    @param A:       The full alignment tensor.
    @type A:        numpy array ((3, 3), float64)
    @return:        The eigensystem.
    @rtype:         tuple of numpy array (float64)
    """

    # The eigenvalues.
    vals = eigvals(A)

    # Find the |x| < |y| < |z| indices.
    abs_vals = abs(vals).tolist()
    x_index = abs_vals.index(min(abs_vals))
    z_index = abs_vals.index(max(abs_vals))
    last_index = list(range(3))
    last_index.pop(max(x_index, z_index))
    last_index.pop(min(x_index, z_index))
    y_index = last_index[0]

    # Return the sorted eigenvalues.
    return [vals[x_index], vals[y_index], vals[z_index]]


def calc_eta(A_diag):
    """Calculate the asymmetry parameter eta.

    This is given by::

        eta = (Axx - Ayy) / Azz

    where Aii are the eigenvalues.


    @param A_diag:  The full alignment tensor, diagonalised.
    @type A_diag:   numpy array ((3, 3), float64)
    @return:        The eta parameter
    @rtype:         float
    """

    # Zero Azz value, so return NaN.
    if A_diag[2, 2] == 0:
        return nan

    # Return eta.
    return (A_diag[0, 0] - A_diag[1, 1]) / A_diag[2, 2]


def calc_euler(rotation):
    """Calculate the zyz notation Euler angles.

    @param rotation:    The rotation matrix.
    @type rotation:     numpy 3D, rank-2 array
    @return:            The Euler angles alpha, beta, and gamma in zyz notation.
    @rtype:             tuple of float
    """

    return R_to_euler_zyz(rotation)


def calc_S(Sxx, Syy, Szz, Sxy, Sxz, Syz):
    """Function for calculating the alignment tensor (in the structural frame).

    @param Sxx:     The Sxx tensor element.
    @type Sxx:      float
    @param Syy:     The Syy tensor element.
    @type Syy:      float
    @param Szz:     The Szz tensor element.
    @type Szz:      float
    @param Sxy:     The Sxy tensor element.
    @type Sxy:      float
    @param Sxz:     The Sxz tensor element.
    @type Sxz:      float
    @param Syz:     The Syz tensor element.
    @type Syz:      float
    @return:        The alignment tensor (within the structural frame).
    @rtype:         3x3 numpy float64 array
    """

    # Initialise the tensor.
    tensor = zeros((3, 3), float64)

    # Populate the diagonal elements.
    tensor[0, 0] = Sxx
    tensor[1, 1] = Syy
    tensor[2, 2] = Szz

    # Populate the off diagonal elements.
    tensor[0, 1] = tensor[1, 0] = Sxy
    tensor[0, 2] = tensor[2, 0] = Sxz
    tensor[1, 2] = tensor[2, 1] = Syz

    # Return the tensor.
    return tensor


def calc_S_5D(Sxx, Syy, Szz, Sxy, Sxz, Syz):
    """Function for calculating the alignment tensor in the 5D vector notation.

    @param Sxx:     The Sxx tensor element.
    @type Sxx:      float
    @param Syy:     The Syy tensor element.
    @type Syy:      float
    @param Szz:     The Szz tensor element.
    @type Szz:      float
    @param Sxy:     The Sxy tensor element.
    @type Sxy:      float
    @param Sxz:     The Sxz tensor element.
    @type Sxz:      float
    @param Syz:     The Syz tensor element.
    @type Syz:      float
    @return:        The alignment 5D tensor (within the structural frame).
    @rtype:         numpy rank-1 5D tensor
    """

    # Initialise the tensor.
    tensor = zeros(5, float64)

    # Populate the tensor.
    tensor[0] = Sxx
    tensor[1] = Syy
    tensor[2] = Sxy
    tensor[3] = Sxz
    tensor[4] = Syz

    # Return the tensor.
    return tensor


def calc_S_diag(tensor):
    """Calculate the diagonalised alignment tensor.

    The diagonalised alignment tensor is defined as::

                   | Sxx'  0    0  |
        tensor  =  |  0   Syy'  0  |.
                   |  0    0   Szz'|

    The diagonalised alignment tensor is calculated by eigenvalue decomposition.


    @param tensor:      The full alignment tensor in its eigenframe.
    @type tensor:       numpy array ((3, 3), float64)
    @return:            The diagonalised alignment tensor.
    @rtype:             numpy array ((3, 3), float64)
    """

    # The eigenvalues.
    vals = eigvals(tensor)

    # Find the |x| < |y| < |z| indices.
    abs_vals = abs(vals).tolist()
    Sxx_index = abs_vals.index(min(abs_vals))
    Szz_index = abs_vals.index(max(abs_vals))
    last_index = list(range(3))
    last_index.pop(max(Sxx_index, Szz_index))
    last_index.pop(min(Sxx_index, Szz_index))
    Syy_index = last_index[0]

    # Empty tensor.
    tensor_diag = zeros((3, 3), float64)

    # Fill the elements.
    tensor_diag[0, 0] = vals[Sxx_index]
    tensor_diag[1, 1] = vals[Syy_index]
    tensor_diag[2, 2] = vals[Szz_index]

    # Return the tensor.
    return tensor_diag


def calc_A0(Szz):
    r"""Function for calculating the A0 irreducible component of the Saupe order matrix.

    The equation for calculating the parameter is::

             / 4pi \ 1/2 
        A0 = | --- |     Szz .
             \  5  /


    @param Szz:     The Szz component of the Saupe order matrix.
    @type Szz:      float
    @return:        The A0 irreducible component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the A0 value.
    return fact_A0 * Szz


def calc_A1(Sxz, Syz):
    r"""Function for calculating the A1 irreducible component of the Saupe order matrix.

    The equation for calculating the parameter is::

             / 8pi \ 1/2 
        A1 = | --- |     (Sxz + iSyz) .
             \ 15  /


    @param Sxz:     The Sxz component of the Saupe order matrix.
    @type Sxz:      float
    @param Syz:     The Syz component of the Saupe order matrix.
    @type Syz:      float
    @return:        The A1 irreducible component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the A1 value.
    return fact_A1 * (Sxz + 1.j*Syz)


def calc_A2(Sxx, Syy, Sxy):
    r"""Function for calculating the A2 irreducible component of the Saupe order matrix.

    The equation for calculating the parameter is::

             / 2pi \ 1/2 
        A2 = | --- |     (Sxx - Syy + 2iSxy) .
             \ 15  /


    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @return:        The A2 irreducible component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the A2 value.
    return fact_A2 * (Sxx - Syy + 2.j*Sxy)


def calc_Am1(Sxz, Syz):
    r"""Function for calculating the A-1 irreducible component of the Saupe order matrix.

    The equation for calculating the parameter is::

                / 8pi \ 1/2 
        A-1 = - | --- |     (Sxz - iSyz) .
                \ 15  /


    @param Sxz:     The Sxz component of the Saupe order matrix.
    @type Sxz:      float
    @param Syz:     The Syz component of the Saupe order matrix.
    @type Syz:      float
    @return:        The A-1 irreducible component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the A-1 value.
    return -fact_A1 * (Sxz - 1.j*Syz)


def calc_Am2(Sxx, Syy, Sxy):
    r"""Function for calculating the A-2 irreducible component of the Saupe order matrix.

    The equation for calculating the parameter is::

              / 2pi \ 1/2 
        A-2 = | --- |     (Sxx - Syy - 2iSxy) ,
              \ 15  /


    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @return:        The A-2 irreducible component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the A-2 value.
    return fact_A2 * (Sxx - Syy - 2.j*Sxy)


def calc_Sxx(Axx):
    """Function for calculating the Axx value.

    The equation for calculating the parameter is::

        Sxx  =  3/2 Axx.

    @param Axx:     The Axx component of the alignment tensor.
    @type Axx:      float
    @rtype:         float
    """

    # Calculate and return the Axx value.
    return 3.0/2.0 * Axx


def calc_Sxxyy(Sxx, Syy):
    """Function for calculating the Sxx-yy value.

    The equation for calculating the parameter is::

        Sxx-yy  =  Sxx - Syy.

    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @return:        The Sxx-yy component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the Sxx-yy value.
    return Sxx - Syy


def calc_Sxy(Axy):
    """Function for calculating the Axy value.

    The equation for calculating the parameter is::

        Sxy  =  3/2 Axy.

    @param Axy:     The Axy component of the alignment tensor.
    @type Axy:      float
    @rtype:         float
    """

    # Calculate and return the Axy value.
    return 3.0/2.0 * Axy


def calc_Sxz(Axz):
    """Function for calculating the Axz value.

    The equation for calculating the parameter is::

        Sxz  =  3/2 Axz.

    @param Axz:     The Axz component of the alignment tensor.
    @type Axz:      float
    @rtype:         float
    """

    # Calculate and return the Axz value.
    return 3.0/2.0 * Axz


def calc_Syy(Ayy):
    """Function for calculating the Ayy value.

    The equation for calculating the parameter is::

        Syy  =  3/2 Ayy.

    @param Ayy:     The Ayy component of the alignment tensor.
    @type Ayy:      float
    @rtype:         float
    """

    # Calculate and return the Ayy value.
    return 3.0/2.0 * Ayy


def calc_Syz(Ayz):
    """Function for calculating the Ayz value.

    The equation for calculating the parameter is::

        Syz  =  3/2 Ayz.

    @param Ayz:     The Ayz component of the alignment tensor.
    @type Ayz:      float
    @rtype:         float
    """

    # Calculate and return the Ayz value.
    return 3.0/2.0 * Ayz


def calc_Szz(Sxx, Syy):
    """Function for calculating the Szz value.

    The equation for calculating the parameter is::

        Szz  =  - Sxx - Syy.

    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @return:        The Szz component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the Szz value.
    return - Sxx - Syy


def calc_P(Axx, Ayy, Azz, Axy, Axz, Ayz):
    """Function for calculating the alignment tensor (in the structural frame).

    @param Axx:     The Axx tensor element.
    @type Axx:      float
    @param Ayy:     The Ayy tensor element.
    @type Ayy:      float
    @param Azz:     The Azz tensor element.
    @type Azz:      float
    @param Axy:     The Axy tensor element.
    @type Axy:      float
    @param Axz:     The Axz tensor element.
    @type Axz:      float
    @param Ayz:     The Ayz tensor element.
    @type Ayz:      float
    @return:        The alignment tensor (within the structural frame).
    @rtype:         3x3 numpy float64 array
    """

    # Initialise the tensor.
    tensor = zeros((3, 3), float64)

    # Populate the diagonal elements.
    tensor[0, 0] = Axx
    tensor[1, 1] = Ayy
    tensor[2, 2] = Azz

    # Populate the off diagonal elements.
    tensor[0, 1] = tensor[1, 0] = Axy
    tensor[0, 2] = tensor[2, 0] = Axz
    tensor[1, 2] = tensor[2, 1] = Ayz

    # Add 1/3 the identity matrix.
    tensor = tensor + eye(3)/3.0

    # Return the tensor.
    return tensor


def calc_P_5D(Axx, Ayy, Azz, Axy, Axz, Ayz):
    """Function for calculating the alignment tensor in the 5D vector notation.

    @param Axx:     The Axx tensor element.
    @type Axx:      float
    @param Ayy:     The Ayy tensor element.
    @type Ayy:      float
    @param Azz:     The Azz tensor element.
    @type Azz:      float
    @param Axy:     The Axy tensor element.
    @type Axy:      float
    @param Axz:     The Axz tensor element.
    @type Axz:      float
    @param Ayz:     The Ayz tensor element.
    @type Ayz:      float
    @return:        The alignment 5D tensor (within the structural frame).
    @rtype:         numpy rank-1 5D tensor
    """

    # Initialise the tensor.
    tensor = zeros(5, float64)

    # Populate the tensor.
    tensor[0] = Axx + 1.0/3.0
    tensor[1] = Ayy + 1.0/3.0
    tensor[2] = Axy
    tensor[3] = Axz
    tensor[4] = Ayz

    # Return the tensor.
    return tensor


def calc_P_diag(tensor):
    """Calculate the diagonalised alignment tensor.

    The diagonalised alignment tensor is defined as::

                   | Pxx'  0    0  |
        tensor  =  |  0   Pyy'  0  |.
                   |  0    0   Pzz'|

    The diagonalised alignment tensor is calculated by eigenvalue decomposition.


    @param tensor:      The full alignment tensor in its eigenframe.
    @type tensor:       numpy array ((3, 3), float64)
    @return:            The diagonalised alignment tensor.
    @rtype:             numpy array ((3, 3), float64)
    """

    # The eigenvalues.
    vals = eigvals(tensor)

    # Find the |x| < |y| < |z| indices.
    abs_vals = abs(vals).tolist()
    Pxx_index = abs_vals.index(min(abs_vals))
    Pzz_index = abs_vals.index(max(abs_vals))
    last_index = list(range(3))
    last_index.pop(max(Pxx_index, Pzz_index))
    last_index.pop(min(Pxx_index, Pzz_index))
    Pyy_index = last_index[0]

    # Empty tensor.
    tensor_diag = zeros((3, 3), float64)

    # Fill the elements.
    tensor_diag[0, 0] = vals[Pxx_index]
    tensor_diag[1, 1] = vals[Pyy_index]
    tensor_diag[2, 2] = vals[Pzz_index]

    # Add 1/3 the identity matrix.
    tensor = tensor + eye(3)/3.0

    # Return the tensor.
    return tensor_diag


def calc_Pxx(Axx):
    """Function for calculating the Pxx value.

    The equation for calculating the parameter is::

        Pxx  =  Axx + 1/3.

    @param Axx:     The Axx component of the alignment tensor.
    @type Axx:      float
    @rtype:         float
    """

    # Calculate and return the Pxx value.
    return Axx + 1.0/3.0


def calc_Pxxyy(Pxx, Pyy):
    """Function for calculating the Pxx-yy value.

    The equation for calculating the parameter is::

        Pxx-yy  =  Pxx - Pyy.

    @param Pxx:     The Pxx component of the alignment tensor.
    @type Pxx:      float
    @param Pyy:     The Pyy component of the alignment tensor.
    @type Pyy:      float
    @return:        The Pxx-yy component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Pxx-yy value.
    return Pxx - Pyy


def calc_Pxy(Axy):
    """Function for calculating the Pxy value.

    The equation for calculating the parameter is::

        Pxy  =  Axy.

    @param Axy:     The Axy component of the alignment tensor.
    @type Axy:      float
    @rtype:         float
    """

    # Calculate and return the Pxy value.
    return Axy


def calc_Pxz(Axz):
    """Function for calculating the Pxz value.

    The equation for calculating the parameter is::

        Pxz  =  Axz.

    @param Axz:     The Axz component of the alignment tensor.
    @type Axz:      float
    @rtype:         float
    """

    # Calculate and return the Pxz value.
    return Axz


def calc_Pyy(Ayy):
    """Function for calculating the Pyy value.

    The equation for calculating the parameter is::

        Pyy  =  Ayy + 1/3.

    @param Ayy:     The Ayy component of the alignment tensor.
    @type Ayy:      float
    @rtype:         float
    """

    # Calculate and return the Pyy value.
    return Ayy + 1.0/3.0


def calc_Pyz(Ayz):
    """Function for calculating the Pyz value.

    The equation for calculating the parameter is::

        Pyz  =  Ayz.

    @param Ayz:     The Ayz component of the alignment tensor.
    @type Ayz:      float
    @rtype:         float
    """

    # Calculate and return the Pyz value.
    return Ayz


def calc_Pzz(Pxx, Pyy):
    """Function for calculating the Pzz value.

    The equation for calculating the parameter is::

        Pzz  =  1 - Pxx - Pyy.

    @param Pxx:     The Pxx component of the alignment tensor.
    @type Pxx:      float
    @param Pyy:     The Pyy component of the alignment tensor.
    @type Pyy:      float
    @return:        The Pzz component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Pzz value.
    return 1.0 - Pxx - Pyy


def calc_R(Aa, Ar):
    """Calculate the rhombicity parameter R.

    This is given by::

        R = Ar / Aa.


    @param Aa:  The Aa parameter.
    @type Aa:   float
    @param Ar:  The Ar parameter.
    @type Ar:   float
    @return:    The R parameter.
    @rtype:     float
    """

    # Zero Aa value, so return NaN.
    if Aa == 0:
        return nan

    # Return R.
    return Ar / Aa


def calc_rotation(A):
    """Calculate the rotation matrix from the molecular frame to the tensor frame.

    This is defined by::

        | Azz | >= | Ayy | >= | Axx |.


    @param A:       The full alignment tensor.
    @type A:        numpy array ((3, 3), float64)
    @return:        The array of x, y, and z indices.
    @rtype:         list
    """

    # The eigenvalues.
    vals, rot = eig(A)

    # Find the |x| < |y| < |z| indices.
    abs_vals = abs(vals).tolist()
    x_index = abs_vals.index(min(abs_vals))
    z_index = abs_vals.index(max(abs_vals))
    last_index = list(range(3))
    last_index.pop(max(x_index, z_index))
    last_index.pop(min(x_index, z_index))
    y_index = last_index[0]

    # Empty rotation matrix for index permutations.
    rot_perm = zeros((3, 3), float64)

    # Permute the rotation matrix.
    perm = [x_index, y_index, z_index]
    for i in range(3):
        for j in range(3):
            rot_perm[i, j] = rot[i, perm[j]]

    # Switch from the left handed to right handed universe if required.
    if abs(det(rot_perm) - 1.0) > 1e-7:
        rot_perm[:, 0] = -rot_perm[:, 0]

    # Return the permuted rotation matrix.
    return rot_perm


def calc_unit_x(rotation):
    """Calculate the x unit vector.

    This is given by the eigenvalue decomposition.


    @param rotation:    The rotation matrix.
    @type rotation:     numpy 3D, rank-2 array
    @return:            The x unit vector.
    @rtype:             numpy array (float64)
    """

    # Return the x unit vector.
    return rotation[:, 0]


def calc_unit_y(rotation):
    """Calculate the y unit vector.

    This is given by the eigenvalue decomposition.


    @param rotation:    The rotation matrix.
    @type rotation:     numpy 3D, rank-2 array
    @return:            The y unit vector.
    @rtype:             numpy array (float64)
    """

    # Return the y unit vector.
    return rotation[:, 1]


def calc_unit_z(rotation):
    """Calculate the z unit vector.

    This is given by the eigenvalue decomposition.


    @param rotation:    The rotation matrix.
    @type rotation:     numpy 3D, rank-2 array
    @return:            The z unit vector.
    @rtype:             numpy array (float64)
    """

    # Return the z unit vector.
    return rotation[:, 2]


def dependency_generator():
    """Generator for the automatic updating the alignment tensor data structures.

    @return:  This generator successively yields three objects, the target object to update, the list of parameters which if modified cause the target to be updated, and the list of parameters that the target depends upon.
    """

    # Primary objects (only dependant on the modifiable objects).
    yield ('A',             ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Axx', 'Ayy', 'Azz', 'Axy', 'Axz', 'Ayz'])
    yield ('A_5D',          ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Axx', 'Ayy', 'Azz', 'Axy', 'Axz', 'Ayz'])
    yield ('Axxyy',         ['Axx', 'Ayy'],                                 ['Axx', 'Ayy'])
    yield ('Azz',           ['Axx', 'Ayy'],                                 ['Axx', 'Ayy'])

    yield ('P',             ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Axx', 'Ayy', 'Azz', 'Axy', 'Axz', 'Ayz'])
    yield ('P_5D',          ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Axx', 'Ayy', 'Azz', 'Axy', 'Axz', 'Ayz'])
    yield ('Pxx',           ['Axx'],                                        ['Axx'])
    yield ('Pxxyy',         ['Axx', 'Ayy'],                                 ['Axx', 'Ayy'])
    yield ('Pxy',           ['Axy'],                                        ['Axy'])
    yield ('Pxz',           ['Axz'],                                        ['Axz'])
    yield ('Pyy',           ['Ayy'],                                        ['Ayy'])
    yield ('Pyz',           ['Ayz'],                                        ['Ayz'])

    yield ('Sxx',           ['Axx'],                                        ['Axx'])
    yield ('Sxy',           ['Axy'],                                        ['Axy'])
    yield ('Sxz',           ['Axz'],                                        ['Axz'])
    yield ('Syy',           ['Ayy'],                                        ['Ayy'])
    yield ('Syz',           ['Ayz'],                                        ['Ayz'])

    # Secondary objects (dependant on the primary objects).
    yield ('A_diag',        ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['A'])
    yield ('eigvals',       ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['A'])
    yield ('rotation',      ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['A'])

    yield ('P_diag',        ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['P'])
    yield ('Pzz',           ['Axx', 'Ayy'],                                 ['Pxx', 'Pyy'])

    yield ('S',             ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Sxx', 'Syy', 'Szz', 'Sxy', 'Sxz', 'Syz'])
    yield ('S_5D',          ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Sxx', 'Syy', 'Szz', 'Sxy', 'Sxz', 'Syz'])
    yield ('S_diag',        ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['S'])
    yield ('Sxxyy',         ['Axx', 'Ayy'],                                 ['Sxx', 'Syy'])
    yield ('Szz',           ['Axx', 'Ayy'],                                 ['Sxx', 'Syy'])

    yield ('Am2',           ['Axx', 'Ayy', 'Axy'],                          ['Sxx', 'Syy', 'Sxy'])
    yield ('Am1',           ['Axy', 'Ayz'],                                 ['Sxz', 'Syz'])
    yield ('A0',            ['Axx', 'Ayy'],                                 ['Szz'])
    yield ('A1',            ['Axy', 'Ayz'],                                 ['Sxz', 'Syz'])
    yield ('A2',            ['Axx', 'Ayy', 'Axy'],                          ['Sxx', 'Syy', 'Sxy'])

    # Tertiary objects (dependant on the secondary objects).
    yield ('Aa',            ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['A_diag'])
    yield ('Ar',            ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['A_diag'])
    yield ('eta',           ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['A_diag'])

    yield ('unit_x',        ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['rotation'])
    yield ('unit_y',        ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['rotation'])
    yield ('unit_z',        ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['rotation'])

    yield ('euler',         ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['rotation'])

    # Quaternary objects (dependant on the tertiary objects).
    yield ('R',             ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'],            ['Aa', 'Ar'])



# Alignment tensor specific data.
#################################

class AlignTensorList(list):
    """List type data container for holding all the alignment tensors.

    The elements of the list should be AlignTensorData instances.
    """

    def __repr__(self):
        """Replacement function for displaying an instance of this class."""

        text = "Alignment tensors.\n\n"
        text = text + "%-8s%-20s\n" % ("Index", "Name")
        for i in range(len(self)):
            text = text + "%-8i%-20s\n" % (i, self[i].name)
        text = text + "\nThese can be accessed by typing 'pipe.align_tensor[index]'.\n"
        return text


    def add_item(self, name):
        """Append a new AlignTensorData instance to the list.

        @param name:    The tensor ID string.
        @type name:     str
        @return:        The tensor object.
        @rtype:         AlignTensorData instance
        """

        # Create the instance.
        obj = AlignTensorData(name)

        # Append the object.
        self.append(obj)

        # Return the object.
        return obj


    def from_xml(self, align_tensor_super_node, file_version=1):
        """Recreate the alignment tensor data structure from the XML alignment tensor node.

        @param align_tensor_super_node:     The alignment tensor XML nodes.
        @type align_tensor_super_node:      xml.dom.minicompat.Element instance
        @keyword file_version:              The relax XML version of the XML file.
        @type file_version:                 int
        """

        # Recreate all the alignment tensor data structures.
        xml_to_object(align_tensor_super_node, self, file_version=file_version, blacklist=['align_tensor'])

        # Get the individual tensors.
        align_tensor_nodes = align_tensor_super_node.getElementsByTagName('align_tensor')

        # Loop over the child nodes.
        for align_tensor_node in align_tensor_nodes:
            # Add the alignment tensor data container.
            self.add_item(align_tensor_node.getAttribute('name'))

            # A temporary object to pack the structures from the XML data into.
            temp_obj = Element()

            # Recreate all the other data structures (into the temporary object).
            xml_to_object(align_tensor_node, temp_obj, file_version=file_version)

            # Loop over all modifiable objects in the temporary object and make soft copies of them.
            for name in self[-1]._mod_attr:
                # Skip if missing from the object.
                if not hasattr(temp_obj, name):
                    continue

                # The category.
                if search('_err$', name):
                    category = 'err'
                    param = name.replace('_err', '')
                elif search('_sim$', name):
                    category = 'sim'
                    param = name.replace('_sim', '')
                else:
                    category = 'val'
                    param = name

                # Get the object.
                value = getattr(temp_obj, name)

                # Normal parameters.
                if category == 'val':
                    self[-1].set(param=param, value=value, category=category, update=False)

                # Errors.
                elif category == 'err':
                    self[-1].set(param=param, value=value, category=category, update=False)

                # Simulation objects objects.
                else:
                    # Set the simulation number if needed.
                    if not hasattr(self[-1], '_sim_num') or self[-1]._sim_num == None:
                        self[-1].set_sim_num(len(value))

                    # Recreate the list elements.
                    for i in range(len(value)):
                        self[-1].set(param=param, value=value[i], category=category, sim_index=i, update=False)

                # Update the data structures.
                for target, update_if_set, depends in dependency_generator():
                    self[-1]._update_object(param, target, update_if_set, depends, category)

            # Delete the temporary object.
            del temp_obj


    def names(self):
        """Return a list of the alignment tensor names."""

        # Loop over the tensors.
        names = []
        for i in range(len(self)):
            names.append(self[i].name)

        # Return the list.
        return names


    def to_xml(self, doc, element):
        """Create an XML element for the alignment tensors.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the alignment tensors XML element to.
        @type element:  XML element object
        """

        # Create the alignment tensors element and add it to the higher level element.
        tensor_list_element = doc.createElement('align_tensors')
        element.appendChild(tensor_list_element)

        # Set the alignment tensor attributes.
        tensor_list_element.setAttribute('desc', 'Alignment tensor list')

        # Add all simple python objects within the PipeContainer to the pipe element.
        fill_object_contents(doc, tensor_list_element, object=self, blacklist=list(self.__class__.__dict__.keys())+list(list.__dict__.keys()))

        # Loop over the tensors.
        for i in range(len(self)):
            # Create an XML element for a single tensor.
            tensor_element = doc.createElement('align_tensor')
            tensor_list_element.appendChild(tensor_element)
            tensor_element.setAttribute('index', repr(i))
            tensor_element.setAttribute('desc', 'Alignment tensor')

            # The blacklist.
            blacklist = ['type', 'is_empty'] + list(self[i].__class__.__dict__.keys())
            for name in dir(self):
                if name not in self[i]._mod_attr:
                    blacklist.append(name)

            # Add all simple python objects within the PipeContainer to the pipe element.
            fill_object_contents(doc, tensor_element, object=self[i], blacklist=blacklist)


class AlignTensorData(Element):
    """An empty data container for the alignment tensor elements."""

    # List of modifiable attributes.
    _mod_attr = [
        'name',
        'Axx',  'Axx_sim',  'Axx_err',
        'Ayy',  'Ayy_sim',  'Ayy_err',
        'Axy',  'Axy_sim',  'Axy_err',
        'Axz',  'Axz_sim',  'Axz_err',
        'Ayz',  'Ayz_sim',  'Ayz_err',
        'align_id',
        'domain',
        'red',
        'fixed'
    ]

    def __init__(self, name, fixed=False):
        """Set up the tensor data.

        @param name:    The tensor ID string.
        @type name:     str
        @keyword fixed: The optimisation flag.
        @type fixed:    bool
        """

        # Store the values.
        self.__dict__['name'] = name
        self.__dict__['fixed'] = fixed

        # The number of simulations.
        self.__dict__['_sim_num'] = None


    def __setattr__(self, name, value):
        """Make this object read-only."""

        raise RelaxError("The alignment tensor is a read-only object.  The alignment tensor set() method must be used instead.")


    def _update_object(self, param_name, target, update_if_set, depends, category, sim_index=None):
        """Function for updating the target object, its error, and the MC simulations.

        If the base name of the object is not within the 'update_if_set' list, this function returns
        without doing anything (to avoid wasting time).  Dependant upon the category the object
        (target), its error (target+'_err'), or all Monte Carlo simulations (target+'_sim') are
        updated.

        @param param_name:      The parameter name which is being set in the __setattr__() function.
        @type param_name:       str
        @param target:          The name of the object to update.
        @type target:           str
        @param update_if_set:   If the parameter being set by the __setattr__() function is not within this list of parameters, don't waste time updating the target.
        @param depends:         An array of names objects that the target is dependent upon.
        @type depends:          array of str
        @param category:        The category of the object to update (one of 'val', 'err', or 'sim').
        @type category:         str
        @keyword sim_index:     The index for a Monte Carlo simulation for simulated parameter.
        @type sim_index:        int or None
        @return:                None
        """

        # Only update if the parameter name is within the 'update_if_set' list.
        if not param_name in update_if_set:
            return

        # Get the function for calculating the value.
        fn = globals()['calc_'+target]


        # The value.
        ############

        if category == 'val':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name),)

            # Only update the object if its dependencies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target] = value


        # The error.
        ############

        if category == 'err':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the error object exists.
                if not hasattr(self, dep_name+'_err'):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name+'_err'),)

            # Only update the error object if its dependencies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target+'_err'] = value


        # The Monte Carlo simulations.
        ##############################

        if category == 'sim':
            # The simulation indices.
            if sim_index != None:
                sim_indices = [sim_index]
            else:
                sim_indices = list(range(self._sim_num))

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = []
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps.append(getattr(self, dep_name))

            # Only create the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Initialise an empty array to store the MC simulation object elements (if it doesn't already exist).
                if not target+'_sim' in self.__dict__:
                    self.__dict__[target+'_sim'] = AlignTensorSimList(elements=self._sim_num)

                # Repackage the deps structure.
                args = []
                skip = False
                for i in sim_indices:
                    args.append(())

                    # Loop over the dependent structures.
                    for j in range(len(deps)):
                        # None, so skip.
                        if deps[j] is None or deps[j][i] is None:
                            skip = True

                        # String data type.
                        if isinstance(deps[j], str):
                            args[-1] = args[-1] + (deps[j],)

                        # List data type.
                        else:
                            args[-1] = args[-1] + (deps[j][i],)

                # Loop over the sims and set the values.
                if not skip:
                    for i in sim_indices:
                        # Calculate the value.
                        value = fn(*args[sim_indices.index(i)])

                        # Set the attribute.
                        self.__dict__[target+'_sim']._set(value=value, sim_index=i)


    def set(self, param=None, value=None, category='val', sim_index=None, update=True):
        """Set a alignment tensor parameter.

        @keyword param:     The name of the parameter to set.
        @type param:        str
        @keyword value:     The parameter value.
        @type value:        anything
        @keyword category:  The type of parameter to set.  This can be 'val' for the normal parameter, 'err' for the parameter error, or 'sim' for Monte Carlo or other simulated parameters.
        @type category:     str
        @keyword sim_index: The index for a Monte Carlo simulation for simulated parameter.
        @type sim_index:    int or None
        @keyword update:    A flag which if True will cause all the alignment tensor objects to be updated correctly.  This can be turned off for speed, as long as the _update_object() method is called prior to using the tensor.
        @type update:       bool
        """

        # Check the type.
        if category not in ['val', 'err', 'sim']:
            raise RelaxError("The category of the parameter '%s' is incorrectly set to %s - it must be one of 'val', 'err' or 'sim'." % (param, category))

        # Test if the attribute that is trying to be set is modifiable.
        if not param in self._mod_attr:
            raise RelaxError("The object '%s' is not modifiable." % param)

        # Set a parameter value.
        if category == 'val':
            self.__dict__[param] = value

        # Set an error.
        elif category == 'err':
            self.__dict__[param+'_err'] = value

        # Set a simulation value.
        else:
            # Check that the simulation number has been set.
            if self._sim_num == None:
                raise RelaxError("The alignment tensor simulation number has not yet been specified, therefore a simulation value cannot be set.")

            # The simulation parameter name.
            sim_param = param+'_sim'

            # No object, so create it.
            if not hasattr(self, sim_param):
                self.__dict__[sim_param] = AlignTensorSimList(elements=self._sim_num)

            # The object.
            obj = getattr(self, sim_param)

            # Set the value.
            obj._set(value=value, sim_index=sim_index)

        # Skip the updating process for certain objects.
        if param in ['type']:
            return

        # Update the data structures.
        if update:
            for target, update_if_set, depends in dependency_generator():
                self._update_object(param, target, update_if_set, depends, category, sim_index=sim_index)


    def set_fixed(self, flag):
        """Set if the alignment tensor should be fixed during optimisation or not.

        @param flag:    The fixed flag.
        @type flag:     bool
        """

        self.__dict__['fixed'] = flag


    def set_sim_num(self, sim_number=None):
        """Set the number of Monte Carlo simulations for the construction of the simulation structures.

        @keyword sim_number:    The number of Monte Carlo simulations.
        @type sim_number:       int
        """

        # Store the value.
        self.__dict__['_sim_num'] = sim_number



class AlignTensorSimList(list):
    """Empty data container for Monte Carlo simulation alignment tensor data."""

    def __init__(self, elements=None):
        """Initialise the Monte Carlo simulation parameter list.

        @keyword elements:      The number of elements to initialise the length of the list to.
        @type elements:         None or int
        """

        # Initialise a length.
        for i in range(elements):
            self._append(None)


    def __setitem__(self, slice_obj, value):
        """This is a read-only object!"""

        raise RelaxError("The alignment tensor is a read-only object.  The alignment tensor set() method must be used instead.")


    def _append(self, value):
        """The secret append method.

        @param value:   The value to append to the list.
        @type value:    anything
        """

        # Execute the base class method.
        super(AlignTensorSimList, self).append(value)


    def _set(self, value=None, sim_index=None):
        """Replacement secret method for __setitem__().

        @keyword value:     The value to set.
        @type value:        anything
        @keyword sim_index: The index of the simulation value to set.
        @type sim_index:    int
        """

        # Execute the base class method.
        super(AlignTensorSimList, self).__setitem__(sim_index, value)
