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


# Axially symmetric delta equation.
###################################

def calc_axial_geom(data, diff_data):
    """Function for calculating the dot product XH . Dpar.

    delta is the dot product between the unit bond vector and the unit vector along Dpar.  The
    equation is:

        delta = XH . Dpar

    The unit Dpar vector is:

                 | sin(theta) * cos(phi) |
        Dpar  =  | sin(theta) * sin(phi) |
                 |      cos(theta)       |
    """

    # The unit Dpar vector.
    diff_data.dpar_unit_vector[0] = sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_unit_vector[1] = sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_unit_vector[2] = cos(diff_data.params[2])

    # delta.
    data.delta = dot(data.xh_unit_vector, diff_data.dpar_unit_vector)



# Axially symmetric delta gradient.
###################################

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

    # delta gradient.
    data.ddelta_dpsi[0] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dtheta)
    data.ddelta_dpsi[1] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dphi)



# Axially symmetric delta Hessian.
##################################

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

    # delta Hessian.
    data.d2delta_dpsi2[0, 0] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dtheta2)
    data.d2delta_dpsi2[0, 1] = data.d2delta_dpsi2[1, 0] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dthetadphi)
    data.d2delta_dpsi2[1, 1] = dot(data.xh_unit_vector, diff_data.dpar_unit_vector_dphi2)



# Anisotropic delta1 and delta2 equations.
##########################################

def calc_aniso_geom(data, diff_data):
    """Function for calculating delta1 and delta2.

    delta1 is the dot product between the unit bond vector and the unit vector along Dz.  The
    equation is:

        delta1 = XH . Dz

    delta2 is the dot product between the unit vector along Dx and the double cross product of the
    unit Dz vector with the unit bond vector with the unit Dz vector again:

        delta2 = Dx . Dz x XH x Dz

    The unit Dz vector is:

               | -sin(beta) * cos(gamma) |
        Dz  =  |  sin(beta) * sin(gamma) |
               |        cos(beta)        |

    The unit Dx vector is:

               | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx  =  |          -sin(alpha) * (1 + cos(beta)) * cos(gamma)            |
               |                    cos(alpha) * sin(beta)                      |
    """

    # The unit Dz vector.
    diff_data.dz[0] = -sin(diff_data.params[4]) * cos(diff_data.params[5])
    diff_data.dz[1] = sin(diff_data.params[4]) * sin(diff_data.params[5])
    diff_data.dz[2] = cos(diff_data.params[4])

    # The unit Dx vector.
    diff_data.dx[0] = -sin(diff_data.params[3]) * sin(diff_data.params[5])  +  cos(diff_data.params[3]) * cos(diff_data.params[4]) * cos(diff_data.params[5])
    diff_data.dx[1] = -sin(diff_data.params[3]) * (1.0 + cos(diff_data.params[4])) * cos(diff_data.params[5])
    diff_data.dx[2] = cos(diff_data.params[3]) * sin(diff_data.params[4])

    # delta1 and delta2
    data.delta1 = dot(data.xh_unit_vector, diff_data.dz)
    data.delta2 = dot(data.dx, diff_data.dz)




