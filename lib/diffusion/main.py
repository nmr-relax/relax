###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Module for the support of diffusion tensors."""

# Python module imports.
from math import pi
from numpy import cross, float64, transpose, zeros
from numpy.linalg import norm, svd

# relax module imports.
from lib.geometry.rotations import R_to_euler_zyz
from lib.text.table import format_table



def return_eigenvalues():
    """Function for returning Dx, Dy, and Dz."""

    # Reassign the data.
    data = cdp.diff_tensor

    # Diso.
    Diso = 1.0 / (6.0 * data.tm)

    # Dx.
    Dx = Diso - 1.0/3.0 * data.Da * (1.0  +  3.0 * data.Dr)

    # Dy.
    Dy = Diso - 1.0/3.0 * data.Da * (1.0  -  3.0 * data.Dr)

    # Dz.
    Dz = Diso + 2.0/3.0 * data.Da

    # Return the eigenvalues.
    return Dx, Dy, Dz


def tensor_eigen_system(tensor):
    """Determine the eigenvalues and vectors for the tensor, sorting the entries.

    @return:    The eigenvalues, rotation matrix, and the Euler angles in zyz notation.
    @rtype:     3D rank-1 array, 3D rank-2 array, float, float, float
    """

    # Eigenvalues.
    R, Di, A = svd(tensor)
    D_diag = zeros((3, 3), float64)
    for i in range(3):
        D_diag[i, i] = Di[i]

    # Reordering structure.
    reorder_data = []
    for i in range(3):
        reorder_data.append([Di[i], i])
    reorder_data.sort()

    # The indices.
    reorder = zeros(3, int)
    Di_sort = zeros(3, float)
    for i in range(3):
        Di_sort[i], reorder[i] = reorder_data[i]

    # Reorder columns.
    R_new = zeros((3, 3), float64)
    for i in range(3):
        R_new[:, i] = R[:, reorder[i]]

    # Switch from the left handed to right handed universes (if needed).
    if norm(cross(R_new[:, 0], R_new[:, 1]) - R_new[:, 2]) > 1e-7:
        R_new[:, 2] = -R_new[:, 2]

    # Reverse the rotation.
    R_new = transpose(R_new)

    # Euler angles (reverse rotation in the rotated axis system).
    gamma, beta, alpha = R_to_euler_zyz(R_new)

    # Collapse the pi axis rotation symmetries.
    if alpha >= pi:
        alpha = alpha - pi
    if gamma >= pi:
        alpha = pi - alpha
        beta = pi - beta
        gamma = gamma - pi
    if beta >= pi:
        alpha = pi - alpha
        beta = beta - pi

    # Return the values.
    return Di_sort, R_new, alpha, beta, gamma


def tensor_info_table(type=None, tm=None, Diso=None, Da=None, Dpar=None, Dper=None, Dratio=None, Dr=None, Dx=None, Dy=None, Dz=None, theta=None, phi=None, alpha=None, beta=None, gamma=None, fixed=None):
    """Print out details of the diffusion tensor.

    @keyword type:      The diffusion tensor type - one of 'sphere', 'spheroid', or 'ellipsoid'.
    @type type:         str
    @keyword tm:        The isotropic correlation time in seconds.
    @type tm:           float
    @keyword Diso:      The isotropic diffusion rate.
    @type Diso:         float
    @keyword Da:        The anisotropic component of the tensor.
    @type Da:           float or None
    @keyword Dpar:      The parallel component of the spheroidal diffusion tensor.
    @type Dpar:         float or None
    @keyword Dper:      The perpendicular component of the spheroidal diffusion tensor.
    @type Dper:         float or None
    @keyword Dratio:    The ratio of Dpar and Dper.
    @type Dratio:       float or None
    @keyword Dr:        The rhombic component of the diffusion tensor.
    @type Dr:           float or None
    @keyword Dx:        The x component of the ellipsoid.
    @type Dx:           float or None
    @keyword Dy:        The y component of the ellipsoid.
    @type Dy:           float or None
    @keyword Dz:        The z component of the ellipsoid.
    @type Dz:           float or None
    @keyword theta:     The azimuthal angle in radians.
    @type theta:        float or None
    @keyword phi:       The polar angle in radians.
    @type phi:          float or None
    @keyword alpha:     The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:        float or None
    @keyword beta:      The Euler angle beta in radians using the z-y-z convention.
    @type beta:         float or None
    @keyword gamma:     The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:        float or None
    """

    # Build the data for a table.
    contents = [["Diffusion type", type]]
    contents.append(["tm (s)", tm])
    contents.append(["Diso (rad/s)", Diso])
    if Da != None:
        contents.append(["Da (rad/s)", Da])
    if Dpar != None:
        contents.append(["Dpar (rad/s)", Dpar])
    if Dper != None:
        contents.append(["Dper (rad/s)", Dper])
    if Dratio != None:
        contents.append(["Dratio", Dratio])
    if Dr != None:
        contents.append(["Dr", Dr])
    if Dx != None:
        contents.append(["Dx (rad/s)", Dx])
    if Dy != None:
        contents.append(["Dy (rad/s)", Dy])
    if Dz != None:
        contents.append(["Dz (rad/s)", Dz])
    if theta != None:
        contents.append(["theta (rad)", theta])
    if phi != None:
        contents.append(["phi (rad)", phi])
    if alpha != None:
        contents.append(["alpha (rad)", alpha])
    if beta != None:
        contents.append(["beta (rad)", beta])
    if gamma != None:
        contents.append(["gamma (rad)", gamma])
    if fixed != None:
        contents.append(["Fixed flag", fixed])

    # Print out the table.
    print(format_table(contents=contents))
