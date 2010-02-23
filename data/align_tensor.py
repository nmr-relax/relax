###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2010 Edward d'Auvergne                        #
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

# Python module imports.
from re import search
from math import cos, sin
from numpy import array, dot, eye, float64, identity, transpose, zeros
from numpy.linalg import eig, eigvals
from types import ListType

# relax module imports.
from data_classes import Element
from maths_fns.rotation_matrix import R_to_euler_zyz
from relax_errors import RelaxError
from relax_xml import fill_object_contents, xml_to_object



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
    last_index = range(3)
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
    last_index = range(3)
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
    last_index = range(3)
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
    last_index = range(3)
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
    last_index = range(3)
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

class AlignTensorList(ListType):
    """List type data container for holding all the alignment tensors.

    The elements of the list should be AlignTensorData instances.
    """

    def __repr__(self):
        """Replacement function for displaying an instance of this class."""

        text = "Alignment tensors.\n\n"
        text = text + "%-8s%-20s\n" % ("Index", "Name")
        for i in xrange(len(self)):
            text = text + "%-8i%-20s\n" % (i, self[i].name)
        text = text + "\nThese can be accessed by typing 'pipe.align_tensor[index]'.\n"
        return text


    def add_item(self, name):
        """Function for appending a new AlignTensorData instance to the list."""

        self.append(AlignTensorData(name))


    def from_xml(self, align_tensor_super_node):
        """Recreate the alignment tensor data structure from the XML alignment tensor node.

        @param align_tensor_super_node:     The alignment tensor XML nodes.
        @type align_tensor_super_node:      xml.dom.minicompat.Element instance
        """

        # Recreate all the alignment tensor data structures.
        xml_to_object(align_tensor_super_node, self, blacklist=['align_tensor'])

        # Get the individual tensors.
        align_tensor_nodes = align_tensor_super_node.getElementsByTagName('align_tensor')

        # Loop over the child nodes.
        for align_tensor_node in align_tensor_nodes:
            # Add the alignment tensor data container.
            self.add_item(align_tensor_node.getAttribute('name'))

            # Recreate all the other data structures.
            xml_to_object(align_tensor_node, self[-1])


    def names(self):
        """Return a list of the alignment tensor names."""

        # Loop over the tensors.
        names = []
        for i in xrange(len(self)):
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
        fill_object_contents(doc, tensor_list_element, object=self, blacklist=list(self.__class__.__dict__.keys() + list.__dict__.keys()))

        # Loop over the tensors.
        for i in xrange(len(self)):
            # Create an XML element for a single tensor.
            tensor_element = doc.createElement('align_tensor')
            tensor_list_element.appendChild(tensor_element)
            tensor_element.setAttribute('index', repr(i))
            tensor_element.setAttribute('desc', 'Alignment tensor')

            # Add all simple python objects within the PipeContainer to the pipe element.
            fill_object_contents(doc, tensor_element, object=self[i], blacklist=list(self[i].__class__.__dict__.keys()))


class AlignTensorData(Element):
    """An empty data container for the alignment tensor elements."""

    # List of modifiable attributes.
    __mod_attr__ = ['name',
                    'Axx',  'Axx_sim',  'Axx_err',
                    'Ayy',  'Ayy_sim',  'Ayy_err',
                    'Axy',  'Axy_sim',  'Axy_err',
                    'Axz',  'Axz_sim',  'Axz_err',
                    'Ayz',  'Ayz_sim',  'Ayz_err',
                    'domain',
                    'red']

    def __init__(self, name):
        """Function for placing the tensor name in the class namespace."""

        self.name = name


    def __setattr__(self, name, value):
        """Function for calculating the parameters, unit vectors, and tensors on the fly.

        @param name:    The name of the object to set.
        @type name:     str
        @param value:   The value to set the object corresponding to the name argument to.
        @type value:    Any Python object type
        """

        # Get the base parameter name and determine the object category ('val', 'err', or 'sim').
        if search('_err$', name):
            category = 'err'
            param_name = name[:-4]
        elif search('_sim$', name):
            category = 'sim'
            param_name = name[:-4]
        else:
            category = 'val'
            param_name = name

        # Test if the attribute that is trying to be set is modifiable.
        if not param_name in self.__mod_attr__:
            raise RelaxError("The object " + repr(name) + " is not modifiable.")

        # Set the attribute normally.
        self.__dict__[name] = value

        # Update the data structures.
        for target, update_if_set, depends in dependency_generator():
            self.__update_object(param_name, target, update_if_set, depends, category)


    def __update_sim_append(self, param_name, index):
        """Update the Monte Carlo simulation data lists when a simulation value is appended.

        @param param_name:  The MC sim parameter name which is being appended to.
        @type param_name:   str
        @param index:       The index of the Monte Carlo simulation which was set.
        @type index:        int
        """

        # Loop over the targets.
        for target, update_if_set, depends in dependency_generator():
            # Only update if the parameter name is within the 'update_if_set' list.
            if not param_name in update_if_set:
                continue

            # Get the function for calculating the value.
            fn = globals()['calc_'+target]

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the MC dependency.
                dep_obj = getattr(self, dep_name)

                # The alignment tensor type.
                if dep_name == 'type':
                    deps = deps+(dep_obj,)
                    continue

                # Test if the MC sim dependency is long enough.
                if len(dep_obj) <= index:
                    missing_dep = 1
                    break

                # Place the value corresponding to the index into the 'deps' array.
                deps = deps+(dep_obj[index],)

            # Only update the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Get the target object.
                target_obj = getattr(self, target+'_sim')

                # Calculate and set the value.
                target_obj.append_untouchable_item(fn(*deps))


    def __update_sim_set(self, param_name, index):
        """Update the Monte Carlo simulation data lists when a simulation value is set.

        @param param_name:  The MC sim parameter name which is being set.
        @type param_name:   str
        @param index:       The index of the Monte Carlo simulation which was set.
        @type index:        int
        """

        # Loop over the targets.
        for target, update_if_set, depends in dependency_generator():
            # Only update if the parameter name is within the 'update_if_set' list.
            if not param_name in update_if_set:
                continue

            # Get the function for calculating the value.
            fn = globals()['calc_'+target]

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the MC dependency.
                dep_obj = getattr(self, dep_name)

                # The alignment tensor type.
                if dep_name == 'type':
                    deps = deps+(dep_obj,)
                    continue

                # Test if the MC sim dependency is long enough.
                if len(dep_obj) <= index:
                    missing_dep = 1
                    break

                # Place the value corresponding to the index into the 'deps' array.
                deps = deps+(dep_obj[index],)

            # Only update the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Get the target object.
                target_obj = getattr(self, target+'_sim')

                # Calculate and set the value.
                target_obj.set_untouchable_item(index, fn(*deps))


    def __update_object(self, param_name, target, update_if_set, depends, category):
        """Function for updating the target object, its error, and the MC simulations.

        If the base name of the object is not within the 'update_if_set' list, this function returns
        without doing anything (to avoid wasting time).  Dependant upon the category the object
        (target), its error (target+'_err'), or all Monte Carlo simulations (target+'_sim') are
        updated.

        @param param_name:      The parameter name which is being set in the __setattr__() function.
        @type param_name:       str
        @param target:          The name of the object to update.
        @type target:           str
        @param update_if_set:   If the parameter being set by the __setattr__() function is not
            within this list of parameters, don't waste time updating the
            target.
        @param depends:         An array of names objects that the target is dependent upon.
        @type depends:          array of str
        @param category:        The category of the object to update (one of 'val', 'err', or
            'sim').
        @type category:         str
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

            # Only create the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Initialise an empty array to store the MC simulation object elements (if it doesn't already exist).
                if not target+'_sim' in self.__dict__:
                    self.__dict__[target+'_sim'] = AlignTensorSimList(target, self)



class AlignTensorSimList(ListType):
    """Empty data container for Monte Carlo simulation alignment tensor data."""

    def __init__(self, param_name, align_element):
        """Initialise the Monte Carlo simulation parameter list.

        This function makes the parameter name and parent object accessible to the functions of this
        list object.
        """

        self.param_name = param_name
        self.align_element = align_element


    def __setitem__(self, index, value):
        """Set the value."""

        # Set the value.
        ListType.__setitem__(self, index, value)

        # Then update the other lists.
        self.align_element._AlignTensorData__update_sim_set(self.param_name, index)


    def append(self, value):
        """Replacement function for the normal self.append() method."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]

        # Update the other MC lists.
        self.align_element._AlignTensorData__update_sim_append(self.param_name, len(self)-1)


    def append_untouchable_item(self, value):
        """Append the value for an untouchable MC data structure."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]


    def set_untouchable_item(self, index, value):
        """Set the value for an untouchable MC data structure."""

        # Set the value.
        ListType.__setitem__(self, index, value)
