###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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


from math import cos, sin
from Numeric import Float64, dot, identity, transpose, zeros



def auto_object_Diso(diff_data, i=None):
    """Function for automatically calculating the Diso value for simulation i.

    @return:    The Diso value for Monte Carlo simulation i.
    @rtype:     float
    """

    # Diso value for simulation i.
    return 1.0 / (6.0 * diff_data.tm_sim[i])


def auto_object_Dpar(diff_data, i=None):
    """Function for automatically calculating the Dpar value.

    @return:    The Dpar value for Monte Carlo simulation i.
    @rtype:     float
    """

    # Dpar value for simulation i (only generate the object if the diffusion is spheroidal).
    if diff_data.type == 'spheroid':
        return diff_data.Diso_sim[i] + 2.0/3.0 * diff_data.Da_sim[i]


def auto_object_Dpar_unit(diff_data, i=None):
    """Function for automatically calculating the Dpar unit vector.

    The unit vector parallel to the unique axis of the diffusion tensor is

                      | sin(theta) * cos(phi) |
        Dpar_unit  =  | sin(theta) * sin(phi) |.
                      |      cos(theta)       |

    If the argument 'i' is supplied, then the Dpar unit vector for Monte Carlo simulation i is
    returned instead.

    @return:    The Dpar unit vector.
    @rtype:     array (Float64)
    """

    # Only calculate the array if diffusion is spheroidal.
    if diff_data.type == 'spheroid':
        # Determine which angles to use.
        if i == None:
            theta = diff_data.theta
            phi = diff_data.phi
        else:
            theta = diff_data.theta_sim[i]
            phi = diff_data.phi_sim[i]

        # Initilise the vector.
        Dpar_unit = zeros(3, Float64)

        # Calculate the x, y, and z components.
        Dpar_unit[0] = sin(theta) * cos(phi)
        Dpar_unit[1] = sin(theta) * sin(phi)
        Dpar_unit[2] = cos(theta)

        # Return the unit vector.
        return Dpar_unit


def auto_object_Dper(diff_data, i=None):
    """Function for automatically calculating the Dper value.

    @return:    The Dper value for Monte Carlo simulation i.
    @rtype:     float
    """

    # Dper value for simulation i (only generate the object if the diffusion is spheroidal).
    if diff_data.type == 'spheroid':
        return diff_data.Diso_sim[i] - 1.0/3.0 * diff_data.Da_sim[i]


def auto_object_Dx(diff_data, i=None):
    """Function for automatically calculating the Dx value.

    @return:    The Dx value for Monte Carlo simulation i.
    @rtype:     float
    """

    # Dx value for simulation i (only generate the object if the diffusion is ellipsoidal).
    if diff_data.type == 'ellipsoid':
        return diff_data.Diso_sim[i] - 1.0/3.0 * diff_data.Da_sim[i] * (1.0 + 3.0*diff_data.Dr_sim[i])


def auto_object_Dx_unit(diff_data, i=None):
    """Function for automatically calculating the Dx unit vector.

    The unit Dx vector is

                    | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                    |                    cos(alpha) * sin(beta)                      |

    If the argument 'i' is supplied, then the Dx unit vector for Monte Carlo simulation i is
    returned instead.

    @return:    The Dx unit vector.
    @rtype:     array (Float64)
    """

    # Only calculate the array if diffusion is ellipsoidal.
    if diff_data.type == 'ellipsoid':
        # Determine which angles to use.
        if i == None:
            alpha = diff_data.alpha
            beta = diff_data.beta
            gamma = diff_data.gamma
        else:
            alpha = diff_data.alpha_sim[i]
            beta = diff_data.beta_sim[i]
            gamma = diff_data.gamma_sim[i]

        # Initilise the vector.
        Dx_unit = zeros(3, Float64)

        # Calculate the x, y, and z components.
        Dx_unit[0] = -sin(alpha) * sin(gamma)  +  cos(alpha) * cos(beta) * cos(gamma)
        Dx_unit[1] = -sin(alpha) * cos(gamma)  -  cos(alpha) * cos(beta) * sin(gamma)
        Dx_unit[2] = cos(alpha) * sin(beta)

        # Return the unit vector.
        return Dx_unit


def auto_object_Dy(diff_data, i=None):
    """Function for automatically calculating the Dy value.

    @return:    The Dy value for Monte Carlo simulation i.
    @rtype:     float
    """

    # Dy value for simulation i (only generate the object if the diffusion is ellipsoidal).
    if diff_data.type == 'ellipsoid':
        return diff_data.Diso_sim[i] - 1.0/3.0 * diff_data.Da_sim[i] * (1.0 - 3.0*diff_data.Dr_sim[i])


def auto_object_Dy_unit(diff_data, i=None):
    """Function for automatically calculating the Dy unit vector.

    The unit Dy vector is

                    | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Dy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                    |                   sin(alpha) * sin(beta)                      |

    If the argument 'i' is supplied, then the Dy unit vector for Monte Carlo simulation i is
    returned instead.

    @return:    The Dy unit vector.
    @rtype:     array (Float64)
    """

    # Only calculate the array if diffusion is ellipsoidal.
    if diff_data.type == 'ellipsoid':
        # Determine which angles to use.
        if i == None:
            alpha = diff_data.alpha
            beta = diff_data.beta
            gamma = diff_data.gamma
        else:
            alpha = diff_data.alpha_sim[i]
            beta = diff_data.beta_sim[i]
            gamma = diff_data.gamma_sim[i]

        # Initilise the vector.
        Dy_unit = zeros(3, Float64)

        # Calculate the x, y, and z components.
        Dy_unit[0] = cos(alpha) * sin(gamma)  +  sin(alpha) * cos(beta) * cos(gamma)
        Dy_unit[1] = cos(alpha) * cos(gamma)  -  sin(alpha) * cos(beta) * sin(gamma)
        Dy_unit[2] = sin(alpha) * sin(beta)

        # Return the unit vector.
        return Dy_unit


def auto_object_Dz(diff_data, i=None):
    """Function for automatically calculating the Dz value.

    @return:    The Dz value for Monte Carlo simulation i.
    @rtype:     float
    """

    # Dz value for simulation i (only generate the object if the diffusion is ellipsoidal).
    if diff_data.type == 'ellipsoid':
        return diff_data.Diso_sim[i] - 1.0/3.0 * diff_data.Da_sim[i] * (1.0 - 3.0*diff_data.Dr_sim[i])


def auto_object_Dz_unit(diff_data, i=None):
    """Function for automatically calculating the Dz unit vector.

    The unit Dz vector is

                    | -sin(beta) * cos(gamma) |
        Dz_unit  =  |  sin(beta) * sin(gamma) |.
                    |        cos(beta)        |

    If the argument 'i' is supplied, then the Dz unit vector for Monte Carlo simulation i is
    returned instead.

    @return:    The Dz unit vector.
    @rtype:     array (Float64)
    """

    # Only calculate the array if diffusion is ellipsoidal.
    if diff_data.type == 'ellipsoid':
        # Determine which angles to use.
        if i == None:
            alpha = diff_data.alpha
            beta = diff_data.beta
            gamma = diff_data.gamma
        else:
            alpha = diff_data.alpha_sim[i]
            beta = diff_data.beta_sim[i]
            gamma = diff_data.gamma_sim[i]

        # Initilise the vector.
        Dz_unit = zeros(3, Float64)

        # Calculate the x, y, and z components.
        Dz_unit[0] = -sin(beta) * cos(gamma)
        Dz_unit[1] = sin(beta) * sin(gamma)
        Dz_unit[2] = cos(beta)

        # Return the unit vector.
        return Dz_unit


def auto_object_rotation(diff_data, i=None):
    """Function for automatically calculating the rotation matrix.

    Spherical diffusion
    ===================

    As the orientation of the diffusion tensor within the structural frame is undefined when the
    molecule diffuses as a sphere, the rotation matrix is simply the identity matrix

              | 1  0  0 |
        R  =  | 0  1  0 |.
              | 0  0  1 |


    Spheroidal diffusion
    ====================

    The rotation matrix required to shift from the diffusion tensor frame to the structural
    frame is equal to

              |  cos(theta) * cos(phi)  -sin(phi)   sin(theta) * cos(phi) |
        R  =  |  cos(theta) * sin(phi)   cos(phi)   sin(theta) * sin(phi) |.
              | -sin(theta)              0          cos(theta)            |


    Ellipsoidal diffusion
    =====================

    The rotation matrix required to shift from the diffusion tensor frame to the structural
    frame is equal to

        R  =  | Dx_unit  Dy_unit  Dz_unit |,

              | Dx_unit[0]  Dy_unit[0]  Dz_unit[0] |
           =  | Dx_unit[1]  Dy_unit[1]  Dz_unit[1] |.
              | Dx_unit[2]  Dy_unit[2]  Dz_unit[2] |

    @return:    The rotation matrix.
    @rtype:     matrix (Float64)
    """

    # The rotation matrix for the sphere.
    if diff_data.type == 'sphere':
        return identity(3, Float64)

    # The rotation matrix for the spheroid.
    elif diff_data.type == 'spheroid':
        # Initialise the rotation matrix.
        rotation = identity(3, Float64)

        # First row of the rotation matrix.
        rotation[0, 0] = cos(diff_data.theta) * cos(diff_data.phi)
        rotation[1, 0] = cos(diff_data.theta) * sin(diff_data.phi)
        rotation[2, 0] = -sin(diff_data.theta)

        # Second row of the rotation matrix.
        rotation[0, 1] = -sin(diff_data.phi)
        rotation[1, 1] = cos(diff_data.phi)

        # Replace the last row of the rotation matrix with the Dpar unit vector.
        rotation[:, 2] = diff_data.Dpar_unit

        # Return the tensor.
        return rotation

    # The rotation matrix for the ellipsoid.
    elif diff_data.type == 'ellipsoid':
        # Initialise the rotation matrix.
        rotation = identity(3, Float64)

        # First column of the rotation matrix.
        rotation[:, 0] = diff_data.Dx_unit

        # Second column of the rotation matrix.
        rotation[:, 1] = diff_data.Dy_unit

        # Third column of the rotation matrix.
        rotation[:, 2] = diff_data.Dz_unit

        # Return the tensor.
        return rotation


def auto_object_tensor(diff_data, i=None):
    """Function for automatically calculating the diffusion tensor (in the structural frame).

    The diffusion tensor is calculated using the diagonalised tensor and the rotation matrix
    through the equation

        R . tensor_diag . R^T.

    @return:    The diffusion tensor (within the structural frame).
    @rtype:     matrix (Float64)
    """

    # Alias the rotation matrix.
    R = diff_data.rotation

    # Rotation (R . tensor_diag . R^T).
    return dot(R, dot(diff_data.tensor_diag, transpose(R)))


def auto_object_tensor_diag(diff_data, i=None):
    """Function for automatically calculating the diagonalised diffusion tensor.

    The diagonalised spherical diffusion tensor is defined as

                   | Diso     0     0 |
        tensor  =  |    0  Diso     0 |.
                   |    0     0  Diso |

    The diagonalised spheroidal tensor is defined as

                   | Dper     0     0 |
        tensor  =  |    0  Dper     0 |.
                   |    0     0  Dpar |

    The diagonalised ellipsoidal diffusion tensor is defined as

                   | Dx   0   0 |
        tensor  =  |  0  Dy   0 |.
                   |  0   0  Dz |

    @return:    The diagonalised diffusion tensor.
    @rtype:     matrix (Float64)
    """

    # Spherical diffusion tensor.
    if diff_data.type == 'sphere':
        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = diff_data.Diso
        tensor[1, 1] = diff_data.Diso
        tensor[2, 2] = diff_data.Diso

        # Return the tensor.
        return tensor

    # Spheroidal diffusion tensor.
    elif diff_data.type == 'spheroid':
        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = diff_data.Dper
        tensor[1, 1] = diff_data.Dper
        tensor[2, 2] = diff_data.Dpar

        # Return the tensor.
        return tensor

    # Ellipsoidal diffusion tensor.
    elif diff_data.type == 'ellipsoid':
        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = diff_data.Dx
        tensor[1, 1] = diff_data.Dy
        tensor[2, 2] = diff_data.Dz

        # Return the tensor.
        return tensor
