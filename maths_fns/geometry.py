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

    Delta is the dot product between the unit bond vector and the unit vector along Dpar.  The
    equation is:

        delta = XH . Dpar

    The unit Dpar vector is:

                 | sin(theta) * cos(phi) |
        Dpar  =  | sin(theta) * sin(phi) |
                 |      cos(theta)       |
    """

    # The unit Dpar vector.
    diff_data.dpar[0] = sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar[1] = sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar[2] = cos(diff_data.params[2])

    # Delta.
    data.delta = dot(data.xh_unit_vector, diff_data.dpar)



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
    diff_data.dpar_dtheta[0] = cos(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_dtheta[1] = cos(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_dtheta[2] = -sin(diff_data.params[2])

    # The phi partial derivative of the unit Dpar vector.
    diff_data.dpar_dphi[0] = -sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_dphi[1] = sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_dphi[2] = 0.0

    # Delta gradient.
    data.ddelta_dpsi[0] = dot(data.xh_unit_vector, diff_data.dpar_dtheta)
    data.ddelta_dpsi[1] = dot(data.xh_unit_vector, diff_data.dpar_dphi)



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
    diff_data.dpar_dtheta2[0] = -sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_dtheta2[1] = -sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_dtheta2[2] = -cos(diff_data.params[2])

    # The theta-phi second partial derivative of the unit Dpar vector.
    diff_data.dpar_dthetadphi[0] = -cos(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_dthetadphi[1] = cos(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_dthetadphi[2] = 0.0

    # The phi-phi second partial derivative of the unit Dpar vector.
    diff_data.dpar_dphi2[0] = -sin(diff_data.params[2]) * cos(diff_data.params[3])
    diff_data.dpar_dphi2[1] = -sin(diff_data.params[2]) * sin(diff_data.params[3])
    diff_data.dpar_dphi2[2] = 0.0

    # delta Hessian.
    data.d2delta_dpsi2[0, 0] = dot(data.xh_unit_vector, diff_data.dpar_dtheta2)
    data.d2delta_dpsi2[0, 1] = data.d2delta_dpsi2[1, 0] = dot(data.xh_unit_vector, diff_data.dpar_dthetadphi)
    data.d2delta_dpsi2[1, 1] = dot(data.xh_unit_vector, diff_data.dpar_dphi2)



# Anisotropic delta equations.
##############################

def calc_aniso_geom(data, diff_data):
    """Function for calculating delta_alpha, delta_beta, and delta_gamma.

    Deltas
    ~~~~~~

    delta_alpha is the dot product between the unit bond vector and the unit vector along Dx.  The
    equation is:

        delta_alpha = XH . Dx

    delta_beta is the dot product between the unit bond vector and the unit vector along Dy.  The
    equation is:

        delta_beta = XH . Dy

    delta_gamma is the dot product between the unit bond vector and the unit vector along Dz.  The
    equation is:

        delta_gamma = XH . Dz


    Unit vectors
    ~~~~~~~~~~~~

    The unit Dx vector is:

               | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
               |                    cos(alpha) * sin(beta)                      |

    The unit Dy vector is:

               | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Dy  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |
               |                   sin(alpha) * sin(beta)                      |

    The unit Dz vector is:

               | -sin(beta) * cos(gamma) |
        Dz  =  |  sin(beta) * sin(gamma) |
               |        cos(beta)        |

    """

    # Trig.
    data.sin_a = sin(diff_data.params[3])
    data.sin_b = sin(diff_data.params[4])
    data.sin_g = sin(diff_data.params[5])

    data.cos_a = cos(diff_data.params[3])
    data.cos_b = cos(diff_data.params[4])
    data.cos_g = cos(diff_data.params[5])

    # The unit Dx vector.
    diff_data.dx[0] = -data.sin_a * data.sin_g + data.cos_a * data.cos_b * data.cos_g
    diff_data.dx[1] = -data.sin_a * data.cos_g - data.cos_a * data.cos_b * data.sin_g
    diff_data.dx[2] =  data.cos_a * data.sin_b

    # The unit Dy vector.
    diff_data.dy[0] = data.cos_a * data.sin_g + data.sin_a * data.cos_b * data.cos_g
    diff_data.dy[1] = data.cos_a * data.cos_g - data.sin_a * data.cos_b * data.sin_g
    diff_data.dy[2] = data.sin_a * data.sin_b

    # The unit Dz vector.
    diff_data.dz[0] = -data.sin_b * data.cos_g
    diff_data.dz[1] =  data.sin_b * data.sin_g
    diff_data.dz[2] =  data.cos_b

    # Deltas
    data.delta_alpha = dot(data.xh_unit_vector, diff_data.dx)
    data.delta_beta =  dot(data.xh_unit_vector, diff_data.dy)
    data.delta_gamma = dot(data.xh_unit_vector, diff_data.dz)



# Anisotropic delta gradient.
#############################

def calc_aniso_dgeom(data, diff_data):
    """Function for calculating the partial derivative of delta_alpha, delta_beta, and delta_gamma.

    Dx gradient
    ~~~~~~~~~~~

    The alpha partial derivative of the unit Dx vector is:

         dDx       | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        ------  =  | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        dalpha     |                   -sin(alpha) * sin(beta)                      |

    The beta partial derivative of the unit Dx vector is:

         dDx      | -cos(alpha) * sin(beta) * cos(gamma) |
        -----  =  |  cos(alpha) * sin(beta) * sin(gamma) |
        dbeta     |       cos(alpha) * cos(beta)         |

    The gamma partial derivative of the unit Dx vector is:

         dDx       | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
        ------  =  |  sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        dgamma     |                             0                                  |


    Dy gradient
    ~~~~~~~~~~~

    The alpha partial derivative of the unit Dy vector is:

         dDy       | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        ------  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
        dalpha     |                    cos(alpha) * sin(beta)                      |

    The beta partial derivative of the unit Dy vector is:

         dDy      | -sin(alpha) * sin(beta) * cos(gamma) |
        -----  =  |  sin(alpha) * sin(beta) * sin(gamma) |
        dbeta     |       sin(alpha) * cos(beta)         |

    The gamma partial derivative of the unit Dy vector is:

         dDy       |  cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |
        ------  =  | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        dgamma     |                             0                                  |


    Dz gradient
    ~~~~~~~~~~~

    The alpha partial derivative of the unit Dz vector is:

         dDz       | 0 |
        ------  =  | 0 |
        dalpha     | 0 |

    The beta partial derivative of the unit Dz vector is:

         dDz      | -cos(beta) * cos(gamma) |
        -----  =  |  cos(beta) * sin(gamma) |
        dbeta     |        -sin(beta)       |

    The gamma partial derivative of the unit Dz vector is:

         dDz       | sin(beta) * sin(gamma) |
        ------  =  | sin(beta) * cos(gamma) |
        dgamma     |           0            |
    """

    # Dx gradient
    #############

    # The alpha partial derivative of the unit Dx vector.
    diff_data.ddx_dalpha[0] = -data.cos_a * data.sin_g - data.sin_a * data.cos_b * data.cos_g
    diff_data.ddx_dalpha[1] = -data.cos_a * data.cos_g + data.sin_a * data.cos_b * data.sin_g
    diff_data.ddx_dalpha[2] = -data.sin_a * data.sin_b

    # The beta partial derivative of the unit Dx vector.
    diff_data.ddx_dbeta[0] = -data.cos_a * data.sin_b * data.cos_g
    diff_data.ddx_dbeta[1] =  data.cos_a * data.sin_b * data.sin_g
    diff_data.ddx_dbeta[2] =  data.cos_a * data.cos_b

    # The gamma partial derivative of the unit Dx vector.
    diff_data.ddx_dgamma[0] = -data.sin_a * data.cos_g - data.cos_a * data.cos_b * data.sin_g
    diff_data.ddx_dgamma[1] =  data.sin_a * data.sin_g - data.cos_a * data.cos_b * data.cos_g


    # Dy gradient
    #############

    # The alpha partial derivative of the unit Dy vector.
    diff_data.ddy_dalpha[0] = -data.sin_a * data.sin_g + data.cos_a * data.cos_b * data.cos_g
    diff_data.ddy_dalpha[1] = -data.sin_a * data.cos_g - data.cos_a * data.cos_b * data.sin_g
    diff_data.ddy_dalpha[2] =  data.cos_a * data.sin_b

    # The beta partial derivative of the unit Dy vector.
    diff_data.ddy_dbeta[0] = -data.sin_a * data.sin_b * data.cos_g
    diff_data.ddy_dbeta[1] =  data.sin_a * data.sin_b * data.sin_g
    diff_data.ddy_dbeta[2] =  data.sin_a * data.cos_b

    # The gamma partial derivative of the unit Dy vector.
    diff_data.ddy_dgamma[0] =  data.cos_a * data.cos_g - data.sin_a * data.cos_b * data.sin_g
    diff_data.ddy_dgamma[1] = -data.cos_a * data.sin_g - data.sin_a * data.cos_b * data.cos_g


    # Dz gradient
    #############

    # The beta partial derivative of the unit Dz vector.
    diff_data.ddz_dbeta[0] = -data.cos_b * data.cos_g
    diff_data.ddz_dbeta[1] =  data.cos_b * data.sin_g
    diff_data.ddz_dbeta[2] = -data.sin_b

    # The gamma partial derivative of the unit Dz vector.
    diff_data.ddz_dgamma[0] = data.sin_b * data.sin_g
    diff_data.ddz_dgamma[1] = data.sin_b * data.cos_g


    # Delta gradients
    #################

    data.ddelta_alpha_dpsi[0] = dot(data.xh_unit_vector, diff_data.ddx_dalpha)
    data.ddelta_alpha_dpsi[1] = dot(data.xh_unit_vector, diff_data.ddx_dbeta)
    data.ddelta_alpha_dpsi[2] = dot(data.xh_unit_vector, diff_data.ddx_dgamma)

    data.ddelta_beta_dpsi[0] = dot(data.xh_unit_vector, diff_data.ddy_dalpha)
    data.ddelta_beta_dpsi[1] = dot(data.xh_unit_vector, diff_data.ddy_dbeta)
    data.ddelta_beta_dpsi[2] = dot(data.xh_unit_vector, diff_data.ddy_dgamma)

    data.ddelta_gamma_dpsi[1] = dot(data.xh_unit_vector, diff_data.ddz_dbeta)
    data.ddelta_gamma_dpsi[2] = dot(data.xh_unit_vector, diff_data.ddz_dgamma)



# Anisotropic delta Hessian.
############################

def calc_aniso_d2geom(data, diff_data):
    """Function calculating the second partial derivatives of delta_alpha, delta_beta, delta_gamma.

    Dx Hessian
    ~~~~~~~~~~

    The alpha-alpha second partial derivative of the unit Dx vector is:

         d2Dx       | sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        -------  =  | sin(alpha) * cos(gamma) + cos(alpha) * cos(beta) * sin(gamma) |
        dalpha2     |                  -cos(alpha) * sin(beta)                      |

    The alpha-beta second partial derivative of the unit Dx vector is:

            d2Dx         |  sin(alpha) * sin(beta) * cos(gamma) |
        ------------  =  | -sin(alpha) * sin(beta) * sin(gamma) |
        dalpha.dbeta     |      -sin(alpha) * cos(beta)         |

    The alpha-gamma second partial derivative of the unit Dx vector is:

            d2Dx          | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        -------------  =  |  cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        dalpha.dgamma     |                             0                                  |

    The beta-beta second partial derivative of the unit Dx vector is:

         d2Dx      | -cos(alpha) * cos(beta) * cos(gamma) |
        ------  =  |  cos(alpha) * cos(beta) * sin(gamma) |
        dbeta2     |      -cos(alpha) * sin(beta)         |

    The beta-gamma second partial derivative of the unit Dx vector is:

            d2Dx         | cos(alpha) * sin(beta) * sin(gamma) |
        ------------  =  | cos(alpha) * sin(beta) * cos(gamma) |
        dbeta.dgamma     |                 0                   |

    The gamma-gamma second partial derivative of the unit Dx vector is:

         d2Dx       | sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        -------  =  | sin(alpha) * cos(gamma) + cos(alpha) * cos(beta) * sin(gamma) |
        dgamma2     |                            0                                  |


    Dy Hessian
    ~~~~~~~~~~

    The alpha-alpha second partial derivative of the unit Dy vector is:

         d2Dy       | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        -------  =  | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        dalpha2     |                   -sin(alpha) * sin(beta)                      |

    The alpha-beta second partial derivative of the unit Dy vector is:

            d2Dy         | -cos(alpha) * sin(beta) * cos(gamma) |
        ------------  =  |  cos(alpha) * sin(beta) * sin(gamma) |
        dalpha.dbeta     |       cos(alpha) * cos(beta)         |

    The alpha-gamma second partial derivative of the unit Dy vector is:

            d2Dy          | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
        -------------  =  |  sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        dalpha.dgamma     |                             0                                  |

    The beta-beta second partial derivative of the unit Dy vector is:

         d2Dy      | -sin(alpha) * cos(beta) * cos(gamma) |
        ------  =  |  sin(alpha) * cos(beta) * sin(gamma) |
        dbeta2     |      -sin(alpha) * sin(beta)         |

    The beta-gamma second partial derivative of the unit Dy vector is:

            d2Dy         | sin(alpha) * sin(beta) * sin(gamma) |
        ------------  =  | sin(alpha) * sin(beta) * cos(gamma) |
        dbeta.dgamma     |                 0                   |

    The gamma-gamma second partial derivative of the unit Dy vector is:

         d2Dy       | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        -------  =  | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        dgamma2     |                             0                                  |


    Dz Hessian
    ~~~~~~~~~~

    The alpha-alpha second partial derivative of the unit Dz vector is:

         d2Dz       | 0 |
        -------  =  | 0 |
        dalpha2     | 0 |

    The alpha-beta second partial derivative of the unit Dz vector is:

            d2Dz         | 0 |
        ------------  =  | 0 |
        dalpha.dbeta     | 0 |

    The alpha-gamma second partial derivative of the unit Dz vector is:

             d2Dz         | 0 |
        -------------  =  | 0 |
        dalpha.dgamma     | 0 |

    The beta-beta second partial derivative of the unit Dz vector is:

         d2Dz      |  sin(beta) * cos(gamma) |
        ------  =  | -sin(beta) * sin(gamma) |
        dbeta2     |        -cos(beta)       |

    The beta-gamma second partial derivative of the unit Dz vector is:

            d2Dz         | cos(beta) * sin(gamma) |
        ------------  =  | cos(beta) * cos(gamma) |
        dbeta.dgamma     |           0            |

    The gamma-gamma second partial derivative of the unit Dz vector is:

         d2Dz       |  sin(beta) * cos(gamma) |
        -------  =  | -sin(beta) * sin(gamma) |
        dgamma2     |            0            |
    """

    # Dx Hessian
    ############

    # The alpha-alpha second partial derivative of the unit Dx vector.
    diff_data.d2dx_dalpha2[0] =  data.sin_a * data.sin_g - data.cos_a * data.cos_b * data.cos_g
    diff_data.d2dx_dalpha2[1] =  data.sin_a * data.cos_g + data.cos_a * data.cos_b * data.sin_g
    diff_data.d2dx_dalpha2[2] = -data.cos_a * data.sin_b

    # The alpha-beta second partial derivative of the unit Dx vector.
    diff_data.d2dx_dalpha_dbeta[0] =  data.sin_a * data.sin_b * data.cos_g
    diff_data.d2dx_dalpha_dbeta[1] = -data.sin_a * data.sin_b * data.sin_g
    diff_data.d2dx_dalpha_dbeta[2] = -data.sin_a * data.cos_b

    # The alpha-gamma second partial derivative of the unit Dx vector.
    diff_data.d2dx_dalpha_dgamma[0] = -data.cos_a * data.cos_g + data.sin_a * data.cos_b * data.sin_g
    diff_data.d2dx_dalpha_dgamma[1] =  data.cos_a * data.sin_g + data.sin_a * data.cos_b * data.cos_g
    diff_data.d2dx_dalpha_dgamma[2] = -data.sin_a * data.cos_b

    # The beta-beta second partial derivative of the unit Dx vector.
    diff_data.d2dx_dbeta2[0] = -data.cos_a * data.cos_b * data.cos_g
    diff_data.d2dx_dbeta2[1] =  data.cos_a * data.cos_b * data.sin_g
    diff_data.d2dx_dbeta2[2] = -data.cos_a * data.sin_b

    # The beta-gamma second partial derivative of the unit Dx vector.
    diff_data.d2dx_dbeta_dgamma[0] = data.cos_a * data.sin_b * data.sin_g
    diff_data.d2dx_dbeta_dgamma[1] = data.cos_a * data.sin_b * data.cos_g

    # The gamma-gamma second partial derivative of the unit Dx vector.
    diff_data.d2dx_dgamma2[0] = data.sin_a * data.sin_g - data.cos_a * data.cos_b * data.cos_g
    diff_data.d2dx_dgamma2[1] = data.sin_a * data.cos_g + data.cos_a * data.cos_b * data.sin_g


    # Dy Hessian
    ############

    # The alpha-alpha second partial derivative of the unit Dy vector.
    diff_data.d2dy_dalpha2[0] = -data.cos_a * data.sin_g - data.sin_a * data.cos_b * data.cos_g
    diff_data.d2dy_dalpha2[1] = -data.cos_a * data.cos_g + data.sin_a * data.cos_b * data.sin_g
    diff_data.d2dy_dalpha2[2] = -data.sin_a * data.sin_b

    # The alpha-beta second partial derivative of the unit Dy vector.
    diff_data.d2dy_dalpha_dbeta[0] = -data.cos_a * data.sin_b * data.cos_g
    diff_data.d2dy_dalpha_dbeta[1] =  data.cos_a * data.sin_b * data.sin_g
    diff_data.d2dy_dalpha_dbeta[2] =  data.cos_a * data.cos_b

    # The alpha-gamma second partial derivative of the unit Dy vector.
    diff_data.d2dy_dalpha_dgamma[0] = -data.sin_a * data.cos_g - data.cos_a * data.cos_b * data.sin_g
    diff_data.d2dy_dalpha_dgamma[1] =  data.sin_a * data.sin_g - data.cos_a * data.cos_b * data.cos_g

    # The beta-beta second partial derivative of the unit Dy vector.
    diff_data.d2dy_dbeta2[0] = -data.sin_a * data.cos_b * data.cos_g
    diff_data.d2dy_dbeta2[1] =  data.sin_a * data.cos_b * data.sin_g
    diff_data.d2dy_dbeta2[2] = -data.sin_a * data.sin_b

    # The beta-gamma second partial derivative of the unit Dy vector.
    diff_data.d2dy_dbeta_dgamma[0] = data.sin_a * data.sin_b * data.sin_g
    diff_data.d2dy_dbeta_dgamma[1] = data.sin_a * data.sin_b * data.cos_g

    # The gamma-gamma second partial derivative of the unit Dy vector.
    diff_data.d2dy_dgamma2[0] = -data.cos_a * data.sin_g - data.sin_a * data.cos_b * data.cos_g
    diff_data.d2dy_dgamma2[1] = -data.cos_a * data.cos_g + data.sin_a * data.cos_b * data.sin_g


    # Dz Hessian
    ############

    # The beta-beta second partial derivative of the unit Dz vector.
    diff_data.d2dz_dbeta2[0] =  data.sin_b * data.cos_g
    diff_data.d2dz_dbeta2[1] = -data.sin_b * data.sin_g
    diff_data.d2dz_dbeta2[2] = -data.cos_b

    # The beta-gamma second partial derivative of the unit Dz vector.
    diff_data.d2dz_dbeta_dgamma[0] = data.cos_b * data.sin_g
    diff_data.d2dz_dbeta_dgamma[1] = data.cos_b * data.cos_g

    # The gamma partial derivative of the unit Dz vector.
    diff_data.d2dz_dgamma2[0] =  data.sin_b * data.cos_g
    diff_data.d2dz_dgamma2[1] = -data.sin_b * data.sin_g


    # Delta Hessians
    ################

    data.d2delta_alpha_dpsi2[0, 0] = dot(data.xh_unit_vector, diff_data.d2dx_dalpha2)
    data.d2delta_alpha_dpsi2[0, 1] = data.d2delta_alpha_dpsi2[1, 0] = dot(data.xh_unit_vector, diff_data.d2dx_dalpha_dbeta)
    data.d2delta_alpha_dpsi2[0, 2] = data.d2delta_alpha_dpsi2[2, 0] = dot(data.xh_unit_vector, diff_data.d2dx_dalpha_dgamma)
    data.d2delta_alpha_dpsi2[1, 1] = dot(data.xh_unit_vector, diff_data.d2dx_dbeta2)
    data.d2delta_alpha_dpsi2[1, 2] = data.d2delta_alpha_dpsi2[2, 1] = dot(data.xh_unit_vector, diff_data.d2dx_dbeta_dgamma)
    data.d2delta_alpha_dpsi2[2, 2] = dot(data.xh_unit_vector, diff_data.d2dx_dgamma2)

    data.d2delta_beta_dpsi2[0, 0] = dot(data.xh_unit_vector, diff_data.d2dy_dalpha2)
    data.d2delta_beta_dpsi2[0, 1] = data.d2delta_alpha_dpsi2[1, 0] = dot(data.xh_unit_vector, diff_data.d2dy_dalpha_dbeta)
    data.d2delta_beta_dpsi2[0, 2] = data.d2delta_alpha_dpsi2[2, 0] = dot(data.xh_unit_vector, diff_data.d2dy_dalpha_dgamma)
    data.d2delta_beta_dpsi2[1, 1] = dot(data.xh_unit_vector, diff_data.d2dy_dbeta2)
    data.d2delta_beta_dpsi2[1, 2] = data.d2delta_alpha_dpsi2[2, 1] = dot(data.xh_unit_vector, diff_data.d2dy_dbeta_dgamma)
    data.d2delta_beta_dpsi2[2, 2] = dot(data.xh_unit_vector, diff_data.d2dy_dgamma2)

    data.d2delta_gamma_dpsi2[0, 0] = dot(data.xh_unit_vector, diff_data.d2dz_dalpha2)
    data.d2delta_gamma_dpsi2[0, 1] = data.d2delta_alpha_dpsi2[1, 0] = dot(data.xh_unit_vector, diff_data.d2dz_dalpha_dbeta)
    data.d2delta_gamma_dpsi2[0, 2] = data.d2delta_alpha_dpsi2[2, 0] = dot(data.xh_unit_vector, diff_data.d2dz_dalpha_dgamma)
    data.d2delta_gamma_dpsi2[1, 1] = dot(data.xh_unit_vector, diff_data.d2dz_dbeta2)
    data.d2delta_gamma_dpsi2[1, 2] = data.d2delta_alpha_dpsi2[2, 1] = dot(data.xh_unit_vector, diff_data.d2dz_dbeta_dgamma)
    data.d2delta_gamma_dpsi2[2, 2] = dot(data.xh_unit_vector, diff_data.d2dz_dgamma2)
