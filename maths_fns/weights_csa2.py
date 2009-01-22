###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

from math import sqrt
from Numeric import outerproduct


##########
# Sphere #
##########


# Sphere weight.
################

def calc_csa2_sphere_ci(data, diff_data):
    """Weight for spherical diffusion.

    c0_csa2 = 1.
    """

    data.ci_csa2[0] = 1.0




############
# Spheroid #
############


# Spheroid weights.
###################

def calc_csa2_spheroid_ci(data, diff_data):
    """Weights for spheroidal diffusion.

    The equations are

        c-1_csa2 = 1/4 (3dz_csa2**2 - 1)**2,

        c0_csa2  = 3dz_csa2**2 (1 - dz_csa2**2),

        c1_csa2  = 3/4 (dz_csa2**2 - 1)**2,

    where dz_csa2 is the direction cosine of the unit csa eigenvector along the z-axis of the diffusion
    tensor which is calculated as the dot product of the unit eigenvector with a unit vector along
    Dpar.
    """

    # Components.
    data.three_dz_csa22_one = 3.0 * data.dz_csa2**2 - 1.0
    data.one_two_dz_csa22 = 1.0 - 2.0 * data.dz_csa2**2
    data.one_dz_csa22 = 1.0 - data.dz_csa2**2
    data.dz_csa22_one = -data.one_dz_csa22

    # Weights.
    data.ci_csa2[0] = 0.25 * data.three_dz_csa22_one**2
    data.ci_csa2[1] = 3.0 * data.dz_csa2**2 * data.one_dz_csa22
    data.ci_csa2[2] = 0.75 * data.dz_csa22_one**2



# Spheroid weight gradient.
###########################

def calc_csa2_spheroid_dci(data, diff_data):
    """Weight gradient for spheroidal diffusion.

    The equations are

        dc-1_csa2                               ddz_csa2
        --------- =  3dz_csa2 (3dz_csa2**2 - 1) -------- ,
          dOi                                     dOi

        dc0_csa2                                ddz_csa2
        --------  =  6dz_csa2 (1 - 2dz_csa2**2) -------- ,
          dOi                                     dOi

        dc1_csa2                               ddz_csa2
        --------  =  3dz_csa2 (dz_csa2**2 - 1) -------- ,
          dOi                                    dOi

    where the orientation parameter set O is {theta, phi}.
    """

    # Components.
    data.dci_csa2[2:, 0] = 3.0 * data.dz_csa2 * data.three_dz_csa22_one * data.ddz_csa2_dO
    data.dci_csa2[2:, 1] = 6.0 * data.dz_csa2 * data.one_two_dz_csa22 * data.ddz_csa2_dO
    data.dci_csa2[2:, 2] = 3.0 * data.dz_csa2 * data.dz_csa22_one * data.ddz_csa2_dO



# Spheroid weight Hessian.
##########################

def calc_csa2_spheroid_d2ci(data, diff_data):
    """Weight Hessian for spheroidal diffusion.

    The equations are

         d2c-1_csa2        /                  ddz_csa2   ddz_csa2                                d2dz_csa2   \ 
        ------------  =  3 |(9dz_csa2**2 - 1) -------- . --------  +  dz_csa2 (3dz_csa2**2 - 1) ------------ | ,
          dOi.dOj          \                    dOi        dOj                                    dOi.dOj    /

         d2c0_csa2         /                  ddz_csa2   ddz_csa2                                d2dz_csa2   \ 
        ------------  =  6 |(1 - 6dz_csa2**2) -------- . --------  +  dz_csa2 (1 - 2dz_csa2**2) ------------ | ,
          dOi.dOj          \                    dOi        dOj                                    dOi.dOj    /

         d2c1_csa2         /                  ddz_csa2   ddz_csa2                               d2dz_csa2   \ 
        ------------  =  3 |(3dz_csa2**2 - 1) -------- . --------  +  dz_csa2 (dz_csa2**2 - 1) ------------ | ,
          dOi.dOj          \                    dOi        dOj                                   dOi.dOj    /

    where the orientation parameter set O is {theta, phi}.
    """

    # Outer product.
    op_csa2 = outerproduct(data.ddz_csa2_dO, data.ddz_csa2_dO)

    # Hessian.
    data.d2ci_csa2[2:, 2:, 0] = 3.0 * ((9.0 * data.dz_csa2**2 - 1.0) * op_csa2  +  data.dz_csa2 * data.three_dz_csa22_one * data.d2dz_csa2_dO2)
    data.d2ci_csa2[2:, 2:, 1] = 6.0 * ((1.0 - 6.0*data.dz_csa2**2) * op_csa2  +  data.dz_csa2 * data.one_two_dz_csa22 * data.d2dz_csa2_dO2)
    data.d2ci_csa2[2:, 2:, 2] = 3.0 * (data.three_dz_csa22_one * op_csa2  +  data.dz_csa2 * data.dz_csa22_one * data.d2dz_csa2_dO2)




#############
# Ellipsoid #
#############


# Ellipsoid weights.
####################

def calc_csa2_ellipsoid_ci(data, diff_data):
    """Weight equations for ellipsoidal diffusion.

    The equations are

        c-2_csa2 = 1/4 (d_csa2 - e_csa2),

        c-1_csa2 = 3dy_csa2**2.dz_csa2**2,

        c0_csa2  = 3dx_csa2**2.dz_csa2**2,

        c1_csa2  = 3dx_csa2**2.dy_csa2**2,

        c2_csa2  = 1/4 (d_csa2 + e_csa2),

    where

        d_csa2  = 3(dx_csa2**4 + dy_csa2**4 + dz_csa2**4) - 1,

        e_csa2  =  1/R [(1 + 3Dr)(dx_csa2**4 + 2dy_csa2**2.dz_csa2**2) + (1 - 3Dr)(dy_csa2**4 + 2dx_csa2**2.dz_csa2**2)
                   - 2(dz_csa2**4 + 2dx_csa2**2.dy_csa2**2)],

    and where the factor R is defined as
             ___________
        R = V 1 + 3Dr**2.

    dx_csa2, dy_csa2, and dz_csa2 are the direction cosines of the csa eigenvectors along the x, y, and z-axes of the
    diffusion tensor, calculated as the dot product of the unit csa eigenvector and the unit vectors
    along Dx, Dy, and Dz respectively.
    """

    # Calculate R.
    data.R = sqrt(1 + 3.0*diff_data.params[2]**2)
    data.inv_R = 1.0 / data.R

    # Factors.
    data.one_3Dr = 1.0 + 3.0 * diff_data.params[2]
    data.one_m3Dr = 1.0 - 3.0 * diff_data.params[2]
    data.dx_csa2_sqrd = data.dx_csa2**2
    data.dy_csa2_sqrd = data.dy_csa2**2
    data.dz_csa2_sqrd = data.dz_csa2**2
    data.dx_csa2_cubed = data.dx_csa2**3
    data.dy_csa2_cubed = data.dy_csa2**3
    data.dz_csa2_cubed = data.dz_csa2**3
    data.dx_csa2_quar = data.dx_csa2**4
    data.dy_csa2_quar = data.dy_csa2**4
    data.dz_csa2_quar = data.dz_csa2**4

    # Components.
    data.ex_csa2 = data.dx_csa2_quar + 2.0 * data.dy_csa2_sqrd * data.dz_csa2_sqrd
    data.ey_csa2 = data.dy_csa2_quar + 2.0 * data.dx_csa2_sqrd * data.dz_csa2_sqrd
    data.ez_csa2 = data.dz_csa2_quar + 2.0 * data.dx_csa2_sqrd * data.dy_csa2_sqrd

    # Calculate d_csa2.
    d_csa2 = 3.0 * (data.dx_csa2_quar + data.dy_csa2_quar + data.dz_csa2_quar) - 1.0

    # Calculate e_csa2.
    e_csa2 = data.inv_R * (data.one_3Dr * data.ex_csa2  +  data.one_m3Dr * data.ey_csa2  -  2.0 * data.ez_csa2)

    # Weight c-2_csa2.
    data.ci_csa2[0] = 0.25 * (d_csa2 - e_csa2)

    # Weight c-1_csa2.
    data.ci_csa2[1] = 3.0 * data.dy_csa2**2 * data.dz_csa2**2

    # Weight c0_csa2.
    data.ci_csa2[2] = 3.0 * data.dx_csa2**2 * data.dz_csa2**2

    # Weight c1_csa2.
    data.ci_csa2[3] = 3.0 * data.dx_csa2**2 * data.dy_csa2**2

    # Weight c2_csa2.
    data.ci_csa2[4] = 0.25 * (d_csa2 + e_csa2)



# Ellipsoid weight gradient.
############################

def calc_csa2_ellipsoid_dci(data, diff_data):
    """Weight gradient for ellipsoidal diffusion.

    Oi partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_csa2       /            ddx_csa2                ddy_csa2                ddz_csa2 \     de_csa2
        ---------  =  3 | dx_csa2**3 --------  +  dy_csa2**3 --------  +  dz_csa2**3 -------- |  -  -------- ,
          dOi           \              dOi                     dOi                     dOi    /       dOi


        dc-1_csa2                      /         ddz_csa2             ddy_csa2 \ 
        ---------  =  6dy_csa2.dz_csa2 | dy_csa2 --------  +  dz_csa2 -------- | ,
          dOi                          \           dOi                  dOi    /


        dc0_csa2                      /         ddz_csa2             ddx_csa2 \ 
        --------  =  6dx_csa2.dz_csa2 | dx_csa2 --------  +  dz_csa2 -------- | ,
          dOi                         \           dOi                  dOi    /


        dc1_csa2                      /         ddy_csa2             ddx_csa2 \ 
        --------  =  6dx_csa2.dy_csa2 | dx_csa2 --------  +  dy_csa2 -------- | ,
          dOi                         \           dOi                  dOi    /


        dc2_csa2       /            ddx_csa2                ddy_csa2                ddz_csa2 \     de_csa2
        --------  =  3 | dx_csa2**3 --------  +  dy_csa2**3 --------  +  dz_csa2**3 -------- |  +  -------- ,
          dOi          \              dOi                     dOi                     dOi    /       dOi


    where

        de_csa2      1 /           /           ddx_csa2                     /         ddz_csa2             ddy_csa2 \ \ 
        --------  =  - | (1 + 3Dr) |dx_csa2**3 --------  +  dy_csa2.dz_csa2 | dy_csa2 --------  +  dz_csa2 -------- | |
          dOi        R \           \             dOi                        \           dOi                  dOi    / /

                              /            ddy_csa2                     /         ddz_csa2             ddx_csa2 \ \ 
                  + (1 - 3Dr) | dy_csa2**3 --------  +  dx_csa2.dz_csa2 | dx_csa2 --------  +  dz_csa2 -------- | |
                              \              dOi                        \           dOi                  dOi    / /

                      /            ddz_csa2                     /         ddy_csa2             ddx_csa2 \ \ \ 
                  - 2 | dz_csa2**3 --------  +  dx_csa2.dy_csa2 | dx_csa2 --------  +  dy_csa2 -------- | | | ,
                      \              dOi                        \           dOi                  dOi    / / /


    and where the orietation parameter set O is

        O = {alpha, beta, gamma}.


    tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_csa2
        ---------  =  0,
          dtm

        dc-1_csa2
        ---------  =  0,
          dtm

        dc0_csa2
        --------   =  0,
          dtm

        dc1_csa2
        --------   =  0,
          dtm

        dc2_csa2
        --------   =  0.
          dtm


    Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_csa2
        ---------  =  0,
          dDa

        dc-1_csa2
        ---------  =  0,
          dDa

        dc0_csa2
        --------   =  0,
          dDa

        dc1_csa2
        --------   =  0,
          dDa

        dc2_csa2
        --------   =  0.
          dDa



    Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_csa2       3 de_csa2
        ---------  =  - - --------,
          dDr           4   dDr

        dc-1_csa2
        ---------  =  0,
          dDr

        dc0_csa2
        --------   =  0,
          dDr

        dc1_csa2
        --------   =  0,
          dDr

        dc2_csa2      3 de_csa2
        --------   =  - --------,
          dDr         4   dDr

    where

        de_csa2       1   /                                                                                                                                             \ 
        --------  =  ---- | (1 - Dr) (dx_csa2**4 + 2dy_csa2**2.dz_csa2**2) - (1 + Dr) (dy_csa2**4 + 2dx_csa2**2.dz_csa2**2) + 2Dr (dz_csa2**4 + 2dx_csa2**2.dy_csa2**2) | .
          dDr        R**3 \                                                                                                                                             /


    """

    # Factors.
    data.inv_R_cubed = data.inv_R ** 3
    data.one_Dr = 1.0 + diff_data.params[2]
    data.one_mDr = 1.0 - diff_data.params[2]


    # Oi partial derivative.
    ##########################

    # Components.
    data.ci_csa2_xy = data.dx_csa2 * data.dy_csa2 * (data.dx_csa2 * data.ddy_csa2_dO  +  data.dy_csa2 * data.ddx_csa2_dO)
    data.ci_csa2_xz = data.dx_csa2 * data.dz_csa2 * (data.dx_csa2 * data.ddz_csa2_dO  +  data.dz_csa2 * data.ddx_csa2_dO)
    data.ci_csa2_yz = data.dy_csa2 * data.dz_csa2 * (data.dy_csa2 * data.ddz_csa2_dO  +  data.dz_csa2 * data.ddy_csa2_dO)

    data.ci_csa2_x = data.dx_csa2_cubed * data.ddx_csa2_dO
    data.ci_csa2_y = data.dy_csa2_cubed * data.ddy_csa2_dO
    data.ci_csa2_z = data.dz_csa2_cubed * data.ddz_csa2_dO

    data.ci_csa2_X = data.ci_csa2_x + data.ci_csa2_yz
    data.ci_csa2_Y = data.ci_csa2_y + data.ci_csa2_xz
    data.ci_csa2_Z = data.ci_csa2_z + data.ci_csa2_xy

    # Calculate dd_dOi.
    dd_csa2_dOi = 3.0 * (data.ci_csa2_x + data.ci_csa2_y + data.ci_csa2_z)

    # Calculate de_dOi.
    de_csa2_dOi = data.inv_R * (data.one_3Dr * data.ci_csa2_X  +  data.one_m3Dr * data.ci_csa2_Y  -  2.0 * data.ci_csa2_Z)

    # Weight c-2.
    data.dci_csa2[3:, 0] = dd_csa2_dOi - de_csa2_dOi

    # Weight c-1.
    data.dci_csa2[3:, 1] = 6.0 * data.ci_csa2_yz

    # Weight c0.
    data.dci_csa2[3:, 2] = 6.0 * data.ci_csa2_xz

    # Weight c1.
    data.dci_csa2[3:, 3] = 6.0 * data.ci_csa2_xy

    # Weight c2.
    data.dci_csa2[3:, 4] = dd_csa2_dOi + de_csa2_dOi


    # Dr partial derivative.
    ########################

    # Calculate de_dDr.
    de_csa2_dDr = data.inv_R_cubed * (data.one_mDr * data.ex_csa2  -  data.one_Dr * data.ey_csa2  +  2.0 * diff_data.params[2] * data.ez_csa2)

    # Weight c-2.
    data.dci_csa2[2, 0] = -0.75 * de_csa2_dDr

    # Weight c2.
    data.dci_csa2[2, 4] = 0.75 * de_csa2_dDr



# Ellipsoid weight Hessian.
###########################

def calc_csa2_ellipsoid_d2ci(data, diff_data):
    """Weight Hessian for ellipsoidal diffusion.

    Oi-Oj partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2        /            /          d2dx_csa2       ddx_csa2   ddx_csa2 \                /          d2dy_csa2       ddy_csa2   ddy_csa2 \                /          d2dz_csa2       ddz_csa2   ddz_csa2 \ \       d2e
        ------------  =  3 | dx_csa2**2 | dx_csa2 ------------ + 3 -------- . -------- |  +  dy_csa2**2 | dy_csa2 ------------ + 3 -------- . -------- |  +  dz_csa2**2 | dz_csa2 ------------ + 3 -------- . -------- | |  -  ------- ,
          dOi.dOj          \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / /     dOi.dOj


         d2c-1_csa2                   /          d2dz_csa2       ddz_csa2   ddz_csa2 \                        / ddy_csa2   ddz_csa2     ddz_csa2   ddy_csa2 \                  /          d2dy_csa2       ddy_csa2   ddy_csa2 \ 
        ------------  =  6 dy_csa2**2 | dz_csa2 ------------  +  -------- . -------- |  +  12 dy_csa2.dz_csa2 | -------- . --------  +  -------- . -------- |  +  6 dz_csa2**2 | dy_csa2 ------------  +  -------- . -------- | ,
          dOi.dOj                     \           dOi.dOj          dOi        dOj    /                        \   dOi        dOj          dOi        dOj    /                  \           dOi.dOj          dOi        dOj    /


         d2c0_csa2                    /          d2dz_csa2       ddz_csa2   ddz_csa2 \                        / ddx_csa2   ddz_csa2     ddz_csa2   ddx_csa2 \                  /          d2dx_csa2       ddx_csa2   ddx_csa2 \ 
        ------------  =  6 dx_csa2**2 | dz_csa2 ------------  +  -------- . -------- |  +  12 dx_csa2.dz_csa2 | -------- . --------  +  -------- . -------- |  +  6 dz_csa2**2 | dx_csa2 ------------  +  -------- . -------- | ,
          dOi.dOj                     \           dOi.dOj          dOi        dOj    /                        \   dOi        dOj          dOi        dOj    /                  \           dOi.dOj          dOi        dOj    /


         d2c1_csa2                    /          d2dy_csa2       ddy_csa2   ddy_csa2 \                        / ddx_csa2   ddy_csa2     ddy_csa2   ddx_csa2 \                  /          d2dx_csa2       ddx_csa2   ddx_csa2 \ 
        ------------  =  6 dx_csa2**2 | dy_csa2 ------------  +  -------- . -------- |  +  12 dx_csa2.dy_csa2 | -------- . --------  +  -------- . -------- |  +  6 dy_csa2**2 | dx_csa2 ------------  +  -------- . -------- | ,
          dOi.dOj                     \           dOi.dOj          dOi        dOj    /                        \   dOi        dOj          dOi        dOj    /                  \           dOi.dOj          dOi        dOj    /


         d2c2_csa2         /            /          d2dx_csa2       ddx_csa2   ddx_csa2 \                /          d2dy_csa2       ddy_csa2   ddy_csa2 \                /          d2dz_csa2       ddz_csa2   ddz_csa2 \ \       d2e
        ------------  =  3 | dx_csa2**2 | dx_csa2 ------------ + 3 -------- . -------- |  +  dy_csa2**2 | dy_csa2 ------------ + 3 -------- . -------- |  +  dz_csa2**2 | dz_csa2 ------------ + 3 -------- . -------- | |  +  ------------ ,
          dOi.dOj          \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / /     dOi.dOj

    where

          d2e_csa2       1 /           /            /          d2dx_csa2       ddx_csa2   ddx_csa2 \                /          d2dz_csa2       ddz_csa2   ddz_csa2 \ 
        ------------  =  - | (1 + 3Dr) | dx_csa2**2 | dx_csa2 ------------ + 3 -------- . -------- |  +  dy_csa2**2 | dz_csa2 ------------  +  -------- . -------- |
          dOi.dOj        R \           \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / 

                                               /          d2dy_csa2       ddy_csa2   ddy_csa2 \                      / ddy_csa2   ddz_csa2     ddz_csa2   ddy_csa2 \ \ 
                                  + dz_csa2**2 | dy_csa2 ------------  +  -------- . -------- |  +  2dy_csa2.dz_csa2 | -------- . --------  +  -------- . -------- | |
                                               \           dOi.dOj          dOi        dOj    /                      \   dOi        dOj          dOi        dOj    / /

                                  /            /          d2dy_csa2       ddy_csa2   ddy_csa2 \                /          d2dz_csa2       ddz_csa2   ddz_csa2 \ 
                      + (1 - 3Dr) | dy_csa2**2 | dy_csa2 ------------ + 3 -------- . -------- |  +  dx_csa2**2 | dz_csa2 ------------  +  -------- . -------- |
                                  \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / 

                                               /          d2dx_csa2       ddx_csa2   ddx_csa2 \                      / ddx_csa2   ddz_csa2     ddz_csa2   ddx_csa2 \ \ 
                                  + dz_csa2**2 | dx_csa2 ------------  +  -------- . -------- |  +  2dx_csa2.dz_csa2 | -------- . --------  +  -------- . -------- | |
                                               \           dOi.dOj          dOi        dOj    /                      \   dOi        dOj          dOi        dOj    / /

                          /            /          d2dz_csa2       ddz_csa2   ddz_csa2 \                /          d2dy_csa2       ddy_csa2   ddy_csa2 \ 
                      - 2 | dz_csa2**2 | dz_csa2 ------------ + 3 -------- . -------- |  +  dx_csa2**2 | dy_csa2 ------------  +  -------- . -------- |
                          \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / 

                                       /          d2dx_csa2       ddx_csa2   ddx_csa2 \                      / ddx_csa2   ddy_csa2     ddy_csa2   ddx_csa2 \ \ \ 
                          + dy_csa2**2 | dx_csa2 ------------  +  -------- . -------- |  +  2dx_csa2.dy_csa2 | -------- . --------  +  -------- . -------- | | |
                                       \           dOi.dOj          dOi        dOj    /                      \   dOi        dOj          dOi        dOj    / / /


    Oi-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2
        ------------  =  0,
          dOi.dtm


         d2c-1_csa2
        ------------  =  0,
          dOi.dtm


         d2c0_csa2
        ------------  =  0,
          dOi.dtm


         d2c1_csa2
        ------------  =  0,
          dOi.dtm


         d2c2_csa2
        ------------  =  0.
          dOi.dtm


    Oi-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2
        ------------  =  0,
          dOi.dDa


         d2c-1_csa2
        ------------  =  0,
          dOi.dDa


         d2c0_csa2
        ------------  =  0,
          dOi.dDa


         d2c1_csa2
        ------------  =  0,
          dOi.dDa


         d2c2_csa2
        ------------  =  0.
          dOi.dDa


    Oi-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2            d2e
        ------------  =  - 3 -------,
          dOi.dDr            dOi.dDr


         d2c-1_csa2
        ------------  =  0,
          dOi.dDr


         d2c0_csa2
        ------------  =  0,
          dOi.dDr


         d2c1_csa2
        ------------  =  0,
          dOi.dDr


         d2c2_csa2           d2e
        ------------  =  3 -------,
          dOi.dDr          dOi.dDr

    where

         d2e_csa2         1   /          /            ddx_csa2                     /         ddz_csa2             ddy_csa2 \ \ 
        ------------  =  ---- | (1 - Dr) | dx_csa2**3 --------  +  dy_csa2.dz_csa2 | dy_csa2 --------  +  dz_csa2 -------- | |
          dOi.dDr        R**3 \          \              dOi                        \           dOi                  dOi    / /

                                    /            ddy_csa2                     /         ddz_csa2             ddx_csa2 \ \ 
                         - (1 + Dr) | dy_csa2**3 --------  +  dx_csa2.dz_csa2 | dx_csa2 --------  +  dz_csa2 -------- | |
                                    \              dOi                        \           dOi                  dOi    / /

                               /            ddz_csa2                     /         ddy_csa2             ddx_csa2 \ \ \ 
                         + 2Dr | dz_csa2**3 --------  +  dx_csa2.dy_csa2 | dx_csa2 --------  +  dy_csa2 -------- | | |
                               \              dOi                        \           dOi                  dOi    / / /


    tm-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_csa2
        ----------  =  0,
          dtm2


        d2c-1_csa2
        ----------  =  0,
          dtm2


        d2c0_csa2
        ---------   =  0,
          dtm2


        d2c1_csa2
        ---------   =  0,
          dtm2


        d2c2_csa2
        ---------   =  0.
          dtm2


    tm-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2
        ------------  =  0,
          dtm.dDa


         d2c-1_csa2
        ------------  =  0,
          dtm.dDa


         d2c0_csa2
        ------------  =  0,
          dtm.dDa


         d2c1_csa2
        ------------  =  0,
          dtm.dDa


         d2c2_csa2
        ------------  =  0.
          dtm.dDa


    tm-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2
        ------------  =  0,
          dtm.dDr


         d2c-1_csa2
        ------------  =  0,
          dtm.dDr


         d2c0_csa2
        ------------  =  0,
          dtm.dDr


         d2c1_csa2
        ------------  =  0,
          dtm.dDr


         d2c2_csa2
        ------------  =  0.
          dtm.dDr


    Da-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_csa2
        -----------  =  0,
          dDa**2


        d2c-1_csa2
        -----------  =  0,
          dDa**2


         d2c0_csa2
        -----------  =  0,
          dDa**2


         d2c1_csa2
        -----------  =  0,
          dDa**2


         d2c2_csa2
        -----------  =  0.
          dDa**2


    Da-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csa2
        ------------  =  0,
          dDa.dDr


         d2c-1_csa2
        ------------  =  0,
          dDa.dDr


         d2c0_csa2
        ------------  =  0,
          dDa.dDr


         d2c1_csa2
        ------------  =  0,
          dDa.dDr


         d2c2_csa2
        ------------  =  0.
          dDa.dDr


    Dr-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_csa2        3  d2e
        -----------  =  - - ------,
          dDr**2          4 dDr**2


        d2c-1_csa2
        -----------  =  0,
          dDr**2


         d2c0_csa2
        -----------  =  0,
          dDr**2


         d2c1_csa2
        -----------  =  0,
          dDr**2


         d2c2_csa2      3  d2e
        -----------  =  - ------,
          dDr**2        4 dDr**2

    where

         d2e_csa2        1   /                                                                                                                                                                        \ 
        -----------  =  ---- | (6Dr**2 - 9Dr - 1)(dx_csa2**4 + 2dy_csa2**2.dz_csa2**2) + (6Dr**2 + 9Dr - 1)(dy_csa2**4 + 2dx_csa2**2.dz_csa2**2) - 2(6Dr**2 - 1)(ddz_csa2*4 + 2dx_csa2**2.dy_csa2**2) |
          dDr**2        R**5 \                                                                                                                                                                        /
     """

    # Oi-Oj partial derivative.
    ###############################

    # Outer products.
    op_csa2_xx = outerproduct(data.ddx_csa2_dO, data.ddx_csa2_dO)
    op_csa2_yy = outerproduct(data.ddy_csa2_dO, data.ddy_csa2_dO)
    op_csa2_zz = outerproduct(data.ddz_csa2_dO, data.ddz_csa2_dO)

    op_csa2_xy = outerproduct(data.ddx_csa2_dO, data.ddy_csa2_dO)
    op_csa2_yx = outerproduct(data.ddy_csa2_dO, data.ddx_csa2_dO)

    op_csa2_xz = outerproduct(data.ddx_csa2_dO, data.ddz_csa2_dO)
    op_csa2_zx = outerproduct(data.ddz_csa2_dO, data.ddx_csa2_dO)

    op_csa2_yz = outerproduct(data.ddy_csa2_dO, data.ddz_csa2_dO)
    op_csa2_zy = outerproduct(data.ddz_csa2_dO, data.ddy_csa2_dO)

    # Components.
    x_comp_csa2 = data.dx_csa2 * data.d2dx_csa2_dO2 + op_csa2_xx
    y_comp_csa2 = data.dy_csa2 * data.d2dy_csa2_dO2 + op_csa2_yy
    z_comp_csa2 = data.dz_csa2 * data.d2dz_csa2_dO2 + op_csa2_zz

    x3_comp_csa2 = data.dx_csa2_sqrd * (data.dx_csa2 * data.d2dx_csa2_dO2 + 3.0 * op_csa2_xx)
    y3_comp_csa2 = data.dy_csa2_sqrd * (data.dy_csa2 * data.d2dy_csa2_dO2 + 3.0 * op_csa2_yy)
    z3_comp_csa2 = data.dz_csa2_sqrd * (data.dz_csa2 * data.d2dz_csa2_dO2 + 3.0 * op_csa2_zz)

    xy_comp_csa2 = data.dx_csa2_sqrd * y_comp_csa2  +  2.0 * data.dx_csa2 * data.dy_csa2 * (op_csa2_xy + op_csa2_yx)  +  data.dy_csa2_sqrd * x_comp_csa2
    xz_comp_csa2 = data.dx_csa2_sqrd * z_comp_csa2  +  2.0 * data.dx_csa2 * data.dz_csa2 * (op_csa2_xz + op_csa2_zx)  +  data.dz_csa2_sqrd * x_comp_csa2
    yz_comp_csa2 = data.dy_csa2_sqrd * z_comp_csa2  +  2.0 * data.dy_csa2 * data.dz_csa2 * (op_csa2_yz + op_csa2_zy)  +  data.dz_csa2_sqrd * y_comp_csa2

    # Calculate d2d_dOidOj.
    d2d_csa2_dOidOj = 3.0 * (x3_comp_csa2 + y3_comp_csa2 + z3_comp_csa2)

    # Calculate d2e_dOidOj.
    d2e_csa2_dOidOj = data.inv_R * (data.one_3Dr * (x3_comp_csa2 + yz_comp_csa2) + data.one_m3Dr * (y3_comp_csa2 + xz_comp_csa2) - 2.0 * (z3_comp_csa2 + xy_comp_csa2))

    # Weight c-2.
    data.d2ci_csa2[3:, 3:, 0] = d2d_csa2_dOidOj - d2e_csa2_dOidOj

    # Weight c-2.
    data.d2ci_csa2[3:, 3:, 1] = 6.0 * yz_comp_csa2

    # Weight c-1.
    data.d2ci_csa2[3:, 3:, 2] = 6.0 * xz_comp_csa2

    # Weight c1.
    data.d2ci_csa2[3:, 3:, 3] = 6.0 * xy_comp_csa2

    # Weight c2.
    data.d2ci_csa2[3:, 3:, 4] = d2d_csa2_dOidOj + d2e_csa2_dOidOj


    # Oi-Dr partial derivative.
    #############################

    # Calculate d2e_dOidDr.
    d2e_csa2_dOidDr = data.inv_R_cubed * (data.one_mDr * data.ci_csa2_X  -  data.one_Dr * data.ci_csa2_Y  +  2.0 * diff_data.params[2] * data.ci_csa2_Z)

    # Weight c0.
    data.d2ci_csa2[3:, 2, 0] = data.d2ci_csa2[2, 3:, 0] = -3.0 * d2e_csa2_dOidDr

    # Weight c2.
    data.d2ci_csa2[3:, 2, 4] = data.d2ci_csa2[2, 3:, 4] = 3.0 * d2e_csa2_dOidDr


    # Dr-Dr partial derivative.
    ###########################

    # Components
    d2e1_dDr2 = 6.0 * diff_data.params[2]**2  -  9.0 * diff_data.params[2]  -  1.0
    d2e2_dDr2 = 6.0 * diff_data.params[2]**2  +  9.0 * diff_data.params[2]  -  1.0
    d2e3_dDr2 = 6.0 * diff_data.params[2]**2  -  1.0

    # Calculate d2e_csa2_dDr2.
    d2e_csa2_dDr2 = data.inv_R**5 * (d2e1_dDr2 * data.ex_csa2  +  d2e2_dDr2 * data.ey_csa2  -  2.0 * d2e3_dDr2 * data.ez_csa2)

    # Weight c0.
    data.d2ci_csa2[2, 2, 0] = -0.75 * d2e_csa2_dDr2

    # Weight c2.
    data.d2ci_csa2[2, 2, 4] = 0.75 * d2e_csa2_dDr2
