###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
# Copyright (C) 2010 Pavel Kaderavek                                          #
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
from math import cos, sin
from numpy import dot



############
# Spheroid #
############


# Spheroid direction cosine equation.
#####################################

def calc_spheroid_di(data, diff_data):
    """Function for calculating the direction cosine dz.

    dz is the dot product between the unit bond vector and the unit vector along Dpar and is given
    by::

        dz = XH . Dpar.

    The unit Dpar vector is::

                 | sin(theta) * cos(phi) |
        Dpar  =  | sin(theta) * sin(phi) |
                 |      cos(theta)       |
    """

    # Components.
    diff_data.sin_theta = sin(diff_data.params[2])
    diff_data.cos_theta = cos(diff_data.params[2])
    diff_data.sin_phi = sin(diff_data.params[3])
    diff_data.cos_phi = cos(diff_data.params[3])

    # The unit Dpar vector.
    diff_data.dpar[0] = diff_data.sin_theta * diff_data.cos_phi
    diff_data.dpar[1] = diff_data.sin_theta * diff_data.sin_phi
    diff_data.dpar[2] = diff_data.cos_theta

    # Direction cosine.
    data.dz = dot(data.unit_vector, diff_data.dpar)



# Spheroid direction cosine gradient.
#####################################

def calc_spheroid_ddi(data, diff_data):
    """Function for calculating the partial derivatives of the direction cosine dz.

    The theta partial derivative of the unit Dpar vector is::

        dDpar      | cos(theta) * cos(phi) |
        ------  =  | cos(theta) * sin(phi) |
        dtheta     |      -sin(theta)      |

    The phi partial derivative of the unit Dpar vector is::

        dDpar     | -sin(theta) * sin(phi) |
        -----  =  |  sin(theta) * cos(phi) |
        dphi      |           0            |

    O is the orientational parameter set {theta, phi}
    """

    # The theta partial derivative of the unit Dpar vector.
    diff_data.dpar_dtheta[0] = diff_data.cos_theta * diff_data.cos_phi
    diff_data.dpar_dtheta[1] = diff_data.cos_theta * diff_data.sin_phi
    diff_data.dpar_dtheta[2] = -diff_data.sin_theta

    # The phi partial derivative of the unit Dpar vector.
    diff_data.dpar_dphi[0] = -diff_data.sin_theta * diff_data.sin_phi
    diff_data.dpar_dphi[1] = diff_data.sin_theta * diff_data.cos_phi
    diff_data.dpar_dphi[2] = 0.0

    # Direction cosine gradient.
    data.ddz_dO[0] = dot(data.unit_vector, diff_data.dpar_dtheta)
    data.ddz_dO[1] = dot(data.unit_vector, diff_data.dpar_dphi)



# Spheroid direction cosine Hessian.
####################################

def calc_spheroid_d2di(data, diff_data):
    """Function for calculating the second partial derivatives of the direction cosine dz.

    The theta-theta second partial derivative of the unit Dpar vector is::

        d2Dpar      | -sin(theta) * cos(phi) |
        -------  =  | -sin(theta) * sin(phi) |
        dtheta2     |      -cos(theta)       |

    The theta-phi second partial derivative of the unit Dpar vector is::

          d2Dpar        | -cos(theta) * sin(phi) |
        -----------  =  |  cos(theta) * cos(phi) |
        dtheta.dphi     |           0            |

    The phi-phi second partial derivative of the unit Dpar vector is::

        dDpar     | -sin(theta) * cos(phi) |
        -----  =  | -sin(theta) * sin(phi) |
        dphi2     |           0            |

    O is the orientational parameter set {theta, phi}
    """

    # The theta-theta second partial derivative of the unit Dpar vector.
    diff_data.dpar_dtheta2[0] = -diff_data.sin_theta * diff_data.cos_phi
    diff_data.dpar_dtheta2[1] = -diff_data.sin_theta * diff_data.sin_phi
    diff_data.dpar_dtheta2[2] = -diff_data.cos_theta

    # The theta-phi second partial derivative of the unit Dpar vector.
    diff_data.dpar_dthetadphi[0] = -diff_data.cos_theta * diff_data.sin_phi
    diff_data.dpar_dthetadphi[1] = diff_data.cos_theta * diff_data.cos_phi
    diff_data.dpar_dthetadphi[2] = 0.0

    # The phi-phi second partial derivative of the unit Dpar vector.
    diff_data.dpar_dphi2[0] = -diff_data.sin_theta * diff_data.cos_phi
    diff_data.dpar_dphi2[1] = -diff_data.sin_theta * diff_data.sin_phi
    diff_data.dpar_dphi2[2] = 0.0

    # Direction cosine Hessian.
    data.d2dz_dO2[0, 0] = dot(data.unit_vector, diff_data.dpar_dtheta2)
    data.d2dz_dO2[0, 1] = data.d2dz_dO2[1, 0] = dot(data.unit_vector, diff_data.dpar_dthetadphi)
    data.d2dz_dO2[1, 1] = dot(data.unit_vector, diff_data.dpar_dphi2)




#############
# Ellipsoid #
#############


# Ellipsoid direction cosine equations.
#######################################

def calc_ellipsoid_di(data, diff_data):
    """Function for calculating the direction cosines dx, dy, and dz.

    Direction cosines
    =================

    dx is the dot product between the unit bond vector and the unit vector along Dx.  The
    equation is::

        dx = XH . Dx

    dy is the dot product between the unit bond vector and the unit vector along Dy.  The
    equation is::

        dy = XH . Dy

    dz is the dot product between the unit bond vector and the unit vector along Dz.  The
    equation is::

        dz = XH . Dz


    Unit vectors
    ============

    The unit Dx vector is::

               | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
               |                    cos(alpha) * sin(beta)                      |

    The unit Dy vector is::

               | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Dy  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |
               |                   sin(alpha) * sin(beta)                      |

    The unit Dz vector is::

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

    # Direction cosines.
    data.dx = dot(data.unit_vector, diff_data.dx)
    data.dy = dot(data.unit_vector, diff_data.dy)
    data.dz = dot(data.unit_vector, diff_data.dz)



# Ellipsoid direction cosine gradient.
######################################

def calc_ellipsoid_ddi(data, diff_data):
    """Function for calculating the partial derivatives of the direction cosines dx, dy, and dz.

    Dx gradient
    ===========

    The alpha partial derivative of the unit Dx vector is::

         dDx       | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        ------  =  | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        dalpha     |                   -sin(alpha) * sin(beta)                      |

    The beta partial derivative of the unit Dx vector is::

         dDx      | -cos(alpha) * sin(beta) * cos(gamma) |
        -----  =  |  cos(alpha) * sin(beta) * sin(gamma) |
        dbeta     |       cos(alpha) * cos(beta)         |

    The gamma partial derivative of the unit Dx vector is::

         dDx       | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
        ------  =  |  sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        dgamma     |                             0                                  |


    Dy gradient
    ===========

    The alpha partial derivative of the unit Dy vector is::

         dDy       | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        ------  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
        dalpha     |                    cos(alpha) * sin(beta)                      |

    The beta partial derivative of the unit Dy vector is::

         dDy      | -sin(alpha) * sin(beta) * cos(gamma) |
        -----  =  |  sin(alpha) * sin(beta) * sin(gamma) |
        dbeta     |       sin(alpha) * cos(beta)         |

    The gamma partial derivative of the unit Dy vector is::

         dDy       |  cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |
        ------  =  | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        dgamma     |                             0                                  |


    Dz gradient
    ===========

    The alpha partial derivative of the unit Dz vector is::

         dDz       | 0 |
        ------  =  | 0 |
        dalpha     | 0 |

    The beta partial derivative of the unit Dz vector is::

         dDz      | -cos(beta) * cos(gamma) |
        -----  =  |  cos(beta) * sin(gamma) |
        dbeta     |        -sin(beta)       |

    The gamma partial derivative of the unit Dz vector is::

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


    # Direction cosine gradients
    ############################

    data.ddx_dO[0] = dot(data.unit_vector, diff_data.ddx_dalpha)
    data.ddx_dO[1] = dot(data.unit_vector, diff_data.ddx_dbeta)
    data.ddx_dO[2] = dot(data.unit_vector, diff_data.ddx_dgamma)

    data.ddy_dO[0] = dot(data.unit_vector, diff_data.ddy_dalpha)
    data.ddy_dO[1] = dot(data.unit_vector, diff_data.ddy_dbeta)
    data.ddy_dO[2] = dot(data.unit_vector, diff_data.ddy_dgamma)

    data.ddz_dO[1] = dot(data.unit_vector, diff_data.ddz_dbeta)
    data.ddz_dO[2] = dot(data.unit_vector, diff_data.ddz_dgamma)



# Ellipsoid direction cosine Hessian.
#####################################

def calc_ellipsoid_d2di(data, diff_data):
    """Function for calculating the second partial derivatives of the direction cosines dx, dy, dz.

    Dx Hessian
    ==========

    The alpha-alpha second partial derivative of the unit Dx vector is::

         d2Dx       | sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        -------  =  | sin(alpha) * cos(gamma) + cos(alpha) * cos(beta) * sin(gamma) |
        dalpha2     |                  -cos(alpha) * sin(beta)                      |

    The alpha-beta second partial derivative of the unit Dx vector is::

            d2Dx         |  sin(alpha) * sin(beta) * cos(gamma) |
        ------------  =  | -sin(alpha) * sin(beta) * sin(gamma) |
        dalpha.dbeta     |      -sin(alpha) * cos(beta)         |

    The alpha-gamma second partial derivative of the unit Dx vector is::

            d2Dx          | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        -------------  =  |  cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        dalpha.dgamma     |                             0                                  |

    The beta-beta second partial derivative of the unit Dx vector is::

         d2Dx      | -cos(alpha) * cos(beta) * cos(gamma) |
        ------  =  |  cos(alpha) * cos(beta) * sin(gamma) |
        dbeta2     |      -cos(alpha) * sin(beta)         |

    The beta-gamma second partial derivative of the unit Dx vector is::

            d2Dx         | cos(alpha) * sin(beta) * sin(gamma) |
        ------------  =  | cos(alpha) * sin(beta) * cos(gamma) |
        dbeta.dgamma     |                 0                   |

    The gamma-gamma second partial derivative of the unit Dx vector is::

         d2Dx       | sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        -------  =  | sin(alpha) * cos(gamma) + cos(alpha) * cos(beta) * sin(gamma) |
        dgamma2     |                            0                                  |


    Dy Hessian
    ==========

    The alpha-alpha second partial derivative of the unit Dy vector is::

         d2Dy       | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        -------  =  | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        dalpha2     |                   -sin(alpha) * sin(beta)                      |

    The alpha-beta second partial derivative of the unit Dy vector is::

            d2Dy         | -cos(alpha) * sin(beta) * cos(gamma) |
        ------------  =  |  cos(alpha) * sin(beta) * sin(gamma) |
        dalpha.dbeta     |       cos(alpha) * cos(beta)         |

    The alpha-gamma second partial derivative of the unit Dy vector is::

            d2Dy          | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
        -------------  =  |  sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma) |
        dalpha.dgamma     |                             0                                  |

    The beta-beta second partial derivative of the unit Dy vector is::

         d2Dy      | -sin(alpha) * cos(beta) * cos(gamma) |
        ------  =  |  sin(alpha) * cos(beta) * sin(gamma) |
        dbeta2     |      -sin(alpha) * sin(beta)         |

    The beta-gamma second partial derivative of the unit Dy vector is::

            d2Dy         | sin(alpha) * sin(beta) * sin(gamma) |
        ------------  =  | sin(alpha) * sin(beta) * cos(gamma) |
        dbeta.dgamma     |                 0                   |

    The gamma-gamma second partial derivative of the unit Dy vector is::

         d2Dy       | -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma) |
        -------  =  | -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma) |
        dgamma2     |                             0                                  |


    Dz Hessian
    ==========

    The alpha-alpha second partial derivative of the unit Dz vector is::

         d2Dz       | 0 |
        -------  =  | 0 |
        dalpha2     | 0 |

    The alpha-beta second partial derivative of the unit Dz vector is::

            d2Dz         | 0 |
        ------------  =  | 0 |
        dalpha.dbeta     | 0 |

    The alpha-gamma second partial derivative of the unit Dz vector is::

             d2Dz         | 0 |
        -------------  =  | 0 |
        dalpha.dgamma     | 0 |

    The beta-beta second partial derivative of the unit Dz vector is::

         d2Dz      |  sin(beta) * cos(gamma) |
        ------  =  | -sin(beta) * sin(gamma) |
        dbeta2     |        -cos(beta)       |

    The beta-gamma second partial derivative of the unit Dz vector is::

            d2Dz         | cos(beta) * sin(gamma) |
        ------------  =  | cos(beta) * cos(gamma) |
        dbeta.dgamma     |           0            |

    The gamma-gamma second partial derivative of the unit Dz vector is::

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


    # Direction cosine Hessians
    ###########################

    data.d2dx_dO2[0, 0] =                       dot(data.unit_vector, diff_data.d2dx_dalpha2)
    data.d2dx_dO2[0, 1] = data.d2dx_dO2[1, 0] = dot(data.unit_vector, diff_data.d2dx_dalpha_dbeta)
    data.d2dx_dO2[0, 2] = data.d2dx_dO2[2, 0] = dot(data.unit_vector, diff_data.d2dx_dalpha_dgamma)
    data.d2dx_dO2[1, 1] =                       dot(data.unit_vector, diff_data.d2dx_dbeta2)
    data.d2dx_dO2[1, 2] = data.d2dx_dO2[2, 1] = dot(data.unit_vector, diff_data.d2dx_dbeta_dgamma)
    data.d2dx_dO2[2, 2] =                       dot(data.unit_vector, diff_data.d2dx_dgamma2)

    data.d2dy_dO2[0, 0] =                       dot(data.unit_vector, diff_data.d2dy_dalpha2)
    data.d2dy_dO2[0, 1] = data.d2dy_dO2[1, 0] = dot(data.unit_vector, diff_data.d2dy_dalpha_dbeta)
    data.d2dy_dO2[0, 2] = data.d2dy_dO2[2, 0] = dot(data.unit_vector, diff_data.d2dy_dalpha_dgamma)
    data.d2dy_dO2[1, 1] =                       dot(data.unit_vector, diff_data.d2dy_dbeta2)
    data.d2dy_dO2[1, 2] = data.d2dy_dO2[2, 1] = dot(data.unit_vector, diff_data.d2dy_dbeta_dgamma)
    data.d2dy_dO2[2, 2] =                       dot(data.unit_vector, diff_data.d2dy_dgamma2)

    data.d2dz_dO2[1, 1] =                       dot(data.unit_vector, diff_data.d2dz_dbeta2)
    data.d2dz_dO2[1, 2] = data.d2dz_dO2[2, 1] = dot(data.unit_vector, diff_data.d2dz_dbeta_dgamma)
    data.d2dz_dO2[2, 2] =                       dot(data.unit_vector, diff_data.d2dz_dgamma2)
