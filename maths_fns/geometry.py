###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

from Numeric import dot
from math import cos, sin


# Dot product equation.
#######################

def calc_axial_geom(data, diff_data):
    """Function for calculating the dot product XH . Dpar.

    Delta is the dot product between the unit bond vector and the unit vector along Dpar.

    The unit Dpar vector is:

                 | sin(theta) * cos(phi) |
        Dpar  =  | sin(theta) * sin(phi) |
                 |      cos(theta)       |
    """

    # The unit Dpar vector.
    diff_data.dpar_unit_vector[0] = sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector[1] = sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector[2] = cos(diff_data.params[2])

    # The dot product.
    data.delta = dot(data.xh_unit_vector, diff_data.dpar_unit_vector)



# Dot product gradient.
#######################

def calc_axial_dgeom(data, diff_data):
    """Function for calculating the partial derivatives of the dot product XH . Dpar.

    The theta partial derivative of the unit Dpar vector is:

        dDpar      | cos(theta) * cos(phi) |
        ------  =  | cos(theta) * sin(phi) |
        dtheta     |      -sin(theta)      |

    The phi partial derivative of the unit Dpar vector is:

        dDpar     | -sin(theta) * sin(phi) |
        -----  =  |  sin(theta) * cos(phi) |
        dphi      |           0            |

    Psi is the diffusion parameter set {Dper, Dpar, theta, phi}
    """

    # The theta partial derivative of the unit Dpar vector.
    diff_data.dpar_unit_vector_dtheta[0] = cos(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector_dtheta[1] = cos(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector_dtheta[2] = -sin(diff_data.params[2])

    # The phi partial derivative of the unit Dpar vector.
    diff_data.dpar_unit_vector_dphi[0] = -sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector_dphi[1] = sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector_dphi[2] = 0.0

    # The dot product.
    data.ddelta_dpsi[0] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dtheta)
    data.ddelta_dpsi[1] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dphi)



# Dot product Hessian.
######################

def calc_axial_d2geom(data, diff_data):
    """Function for calculating the second partial derivatives of the dot product XH . Dpar.

    The theta-theta second partial derivative of the unit Dpar vector is:

        d2Dpar      | -sin(theta) * cos(phi) |
        -------  =  | -sin(theta) * sin(phi) |
        dtheta2     |      -cos(theta)       |

    The theta-phi second partial derivative of the unit Dpar vector is:

          d2Dpar        | -cos(theta) * sin(phi) |
        -----------  =  |  cos(theta) * cos(phi) |
        dtheta.dphi     |           0            |

    The phi-phi second partial derivative of the unit Dpar vector is:

        dDpar     | -sin(theta) * cos(phi) |
        -----  =  | -sin(theta) * sin(phi) |
        dphi2     |           0            |

    Psi is the diffusion parameter set {Dper, Dpar, theta, phi}
    """

    # The theta-theta second partial derivative of the unit Dpar vector.
    diff_data.dpar_unit_vector_dtheta2[0] = -sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector_dtheta2[1] = -sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector_dtheta2[2] = -cos(diff_data.params[2])

    # The theta-phi second partial derivative of the unit Dpar vector.
    diff_data.dpar_unit_vector_dthetadphi[0] = -cos(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector_dthetadphi[1] = cos(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector_dthetadphi[2] = 0.0

    # The phi-phi second partial derivative of the unit Dpar vector.
    diff_data.dpar_unit_vector_dphi2[0] = -sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector_dphi2[1] = -sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector_dphi2[2] = 0.0

    # The dot product.
    data.d2delta_dpsi2[0, 0] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dtheta2)
    data.d2delta_dpsi2[0, 1] = data.d2delta_dpsi2[3, 2] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dthetadphi)
    data.d2delta_dpsi2[1, 1] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dphi2)
