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

def calc_dipY_sphere_ci(data, diff_data, i):
    """Weight for spherical diffusion.

    c0_dipY = 1.
    """

    data.ci_dipY[i][0] = 1.0




############
# Spheroid #
############


# Spheroid weights.
###################

def calc_dipY_spheroid_ci(data, diff_data, i):
    """Weights for spheroidal diffusion.

    The equations are

        c-1_dipY = 1/4 (3dz_dipY**2 - 1)**2,

        c0_dipY  = 3dz_dipY**2 (1 - dz_dipY**2),

        c1_dipY  = 3/4 (dz_dipY**2 - 1)**2,

    where dz_dipY is the direction cosine of the unit csa eigenvector along the z-axis of the diffusion
    tensor which is calculated as the dot product of the unit eigenvector with a unit vector along
    Dpar.
    """

    # Components.
    data.three_dz_dipY2_one = 3.0 * data.dz_dipY[i]**2 - 1.0
    data.one_two_dz_dipY2 = 1.0 - 2.0 * data.dz_dipY[i]**2
    data.one_dz_dipY2 = 1.0 - data.dz_dipY[i]**2
    data.dz_dipY2_one = -data.one_dz_dipY2

    # Weights.
    data.ci_dipY[i][0] = 0.25 * data.three_dz_dipY2_one**2
    data.ci_dipY[i][1] = 3.0 * data.dz_dipY[i]**2 * data.one_dz_dipY2
    data.ci_dipY[i][2] = 0.75 * data.dz_dipY2_one**2



# Spheroid weight gradient.
###########################

def calc_dipY_spheroid_dci(data, diff_data, i):
    """Weight gradient for spheroidal diffusion.

    The equations are

        dc-1_dipY                               ddz_dipY
        --------- =  3dz_dipY (3dz_dipY**2 - 1) -------- ,
          dOi                                     dOi

        dc0_dipY                                ddz_dipY
        --------  =  6dz_dipY (1 - 2dz_dipY**2) -------- ,
          dOi                                     dOi

        dc1_dipY                               ddz_dipY
        --------  =  3dz_dipY (dz_dipY**2 - 1) -------- ,
          dOi                                    dOi

    where the orientation parameter set O is {theta, phi}.
    """

    # Components.
    data.three_dz_dipY2_one = 3.0 * data.dz_dipY[i]**2 - 1.0
    data.one_two_dz_dipY2 = 1.0 - 2.0 * data.dz_dipY[i]**2
    data.one_dz_dipY2 = 1.0 - data.dz_dipY[i]**2
    data.dz_dipY2_one = -data.one_dz_dipY2

    # Components.
    data.dci_dipY[i][2:, 0] = 3.0 * data.dz_dipY[i] * data.three_dz_dipY2_one * data.ddz_dipY_dO[i]
    data.dci_dipY[i][2:, 1] = 6.0 * data.dz_dipY[i] * data.one_two_dz_dipY2 * data.ddz_dipY_dO[i]
    data.dci_dipY[i][2:, 2] = 3.0 * data.dz_dipY[i] * data.dz_dipY2_one * data.ddz_dipY_dO[i]



# Spheroid weight Hessian.
##########################

def calc_dipY_spheroid_d2ci(data, diff_data, i):
    """Weight Hessian for spheroidal diffusion.

    The equations are

         d2c-1_dipY        /                  ddz_dipY   ddz_dipY                                d2dz_dipY   \ 
        ------------  =  3 |(9dz_dipY**2 - 1) -------- . --------  +  dz_dipY (3dz_dipY**2 - 1) ------------ | ,
          dOi.dOj          \                    dOi        dOj                                    dOi.dOj    /

         d2c0_dipY         /                  ddz_dipY   ddz_dipY                                d2dz_dipY   \ 
        ------------  =  6 |(1 - 6dz_dipY**2) -------- . --------  +  dz_dipY (1 - 2dz_dipY**2) ------------ | ,
          dOi.dOj          \                    dOi        dOj                                    dOi.dOj    /

         d2c1_dipY         /                  ddz_dipY   ddz_dipY                               d2dz_dipY   \ 
        ------------  =  3 |(3dz_dipY**2 - 1) -------- . --------  +  dz_dipY (dz_dipY**2 - 1) ------------ | ,
          dOi.dOj          \                    dOi        dOj                                   dOi.dOj    /

    where the orientation parameter set O is {theta, phi}.
    """

    # Components.
    data.three_dz_dipY2_one = 3.0 * data.dz_dipY[i]**2 - 1.0
    data.one_two_dz_dipY2 = 1.0 - 2.0 * data.dz_dipY[i]**2
    data.one_dz_dipY2 = 1.0 - data.dz_dipY[i]**2
    data.dz_dipY2_one = -data.one_dz_dipY2

    # Outer product.
    op_dipY = outerproduct(data.ddz_dipY_dO[i], data.ddz_dipY_dO[i])

    # Hessian.
    data.d2ci_dipY[i][2:, 2:, 0] = 3.0 * ((9.0 * data.dz_dipY[i]**2 - 1.0) * op_dipY  +  data.dz_dipY[i] * data.three_dz_dipY2_one * data.d2dz_dipY_dO2[i])
    data.d2ci_dipY[i][2:, 2:, 1] = 6.0 * ((1.0 - 6.0*data.dz_dipY[i]**2) * op_dipY  +  data.dz_dipY[i] * data.one_two_dz_dipY2 * data.d2dz_dipY_dO2[i])
    data.d2ci_dipY[i][2:, 2:, 2] = 3.0 * (data.three_dz_dipY2_one * op_dipY  +  data.dz_dipY[i] * data.dz_dipY2_one * data.d2dz_dipY_dO2[i])




#############
# Ellipsoid #
#############


# Ellipsoid weights.
####################

def calc_dipY_ellipsoid_ci(data, diff_data, i):
    """Weight equations for ellipsoidal diffusion.

    The equations are

        c-2_dipY = 1/4 (d_dipY - e_dipY),

        c-1_dipY = 3dy_dipY**2.dz_dipY**2,

        c0_dipY  = 3dx_dipY**2.dz_dipY**2,

        c1_dipY  = 3dx_dipY**2.dy_dipY**2,

        c2_dipY  = 1/4 (d_dipY + e_dipY),

    where

        d_dipY  = 3(dx_dipY**4 + dy_dipY**4 + dz_dipY**4) - 1,

        e_dipY  =  1/R [(1 + 3Dr)(dx_dipY**4 + 2dy_dipY**2.dz_dipY**2) + (1 - 3Dr)(dy_dipY**4 + 2dx_dipY**2.dz_dipY**2)
                   - 2(dz_dipY**4 + 2dx_dipY**2.dy_dipY**2)],

    and where the factor R is defined as
             ___________
        R = V 1 + 3Dr**2.

    dx_dipY, dy_dipY, and dz_dipY are the direction cosines of the csa eigenvectors along the x, y, and z-axes of the
    diffusion tensor, calculated as the dot product of the unit csa eigenvector and the unit vectors
    along Dx, Dy, and Dz respectively.
    """

    # Calculate R.
    data.R = sqrt(1 + 3.0*diff_data.params[2]**2)
    data.inv_R = 1.0 / data.R

    # Factors.
    data.one_3Dr = 1.0 + 3.0 * diff_data.params[2]
    data.one_m3Dr = 1.0 - 3.0 * diff_data.params[2]
    data.dx_dipY_sqrd = data.dx_dipY[i]**2
    data.dy_dipY_sqrd = data.dy_dipY[i]**2
    data.dz_dipY_sqrd = data.dz_dipY[i]**2
    data.dx_dipY_cubed = data.dx_dipY[i]**3
    data.dy_dipY_cubed = data.dy_dipY[i]**3
    data.dz_dipY_cubed = data.dz_dipY[i]**3
    data.dx_dipY_quar = data.dx_dipY[i]**4
    data.dy_dipY_quar = data.dy_dipY[i]**4
    data.dz_dipY_quar = data.dz_dipY[i]**4

    # Components.
    data.ex_dipY = data.dx_dipY_quar + 2.0 * data.dy_dipY_sqrd * data.dz_dipY_sqrd
    data.ey_dipY = data.dy_dipY_quar + 2.0 * data.dx_dipY_sqrd * data.dz_dipY_sqrd
    data.ez_dipY = data.dz_dipY_quar + 2.0 * data.dx_dipY_sqrd * data.dy_dipY_sqrd

    # Calculate d_dipY.
    d_dipY = 3.0 * (data.dx_dipY_quar + data.dy_dipY_quar + data.dz_dipY_quar) - 1.0

    # Calculate e_dipY.
    e_dipY = data.inv_R * (data.one_3Dr * data.ex_dipY  +  data.one_m3Dr * data.ey_dipY  -  2.0 * data.ez_dipY)

    # Weight c-2_dipY.
    data.ci_dipY[i][0] = 0.25 * (d_dipY - e_dipY)

    # Weight c-1_dipY.
    data.ci_dipY[i][1] = 3.0 * data.dy_dipY[i]**2 * data.dz_dipY[i]**2

    # Weight c0_dipY.
    data.ci_dipY[i][2] = 3.0 * data.dx_dipY[i]**2 * data.dz_dipY[i]**2

    # Weight c1_dipY.
    data.ci_dipY[i][3] = 3.0 * data.dx_dipY[i]**2 * data.dy_dipY[i]**2

    # Weight c2_dipY.
    data.ci_dipY[i][4] = 0.25 * (d_dipY + e_dipY)




# Ellipsoid weight gradient.
############################

def calc_dipY_ellipsoid_dci(data, diff_data, i):
    """Weight gradient for ellipsoidal diffusion.

    Oi partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_dipY       /            ddx_dipY                ddy_dipY                ddz_dipY \     de_dipY
        ---------  =  3 | dx_dipY**3 --------  +  dy_dipY**3 --------  +  dz_dipY**3 -------- |  -  -------- ,
          dOi           \              dOi                     dOi                     dOi    /       dOi


        dc-1_dipY                      /         ddz_dipY             ddy_dipY \ 
        ---------  =  6dy_dipY.dz_dipY | dy_dipY --------  +  dz_dipY -------- | ,
          dOi                          \           dOi                  dOi    /


        dc0_dipY                      /         ddz_dipY             ddx_dipY \ 
        --------  =  6dx_dipY.dz_dipY | dx_dipY --------  +  dz_dipY -------- | ,
          dOi                         \           dOi                  dOi    /


        dc1_dipY                      /         ddy_dipY             ddx_dipY \ 
        --------  =  6dx_dipY.dy_dipY | dx_dipY --------  +  dy_dipY -------- | ,
          dOi                         \           dOi                  dOi    /


        dc2_dipY       /            ddx_dipY                ddy_dipY                ddz_dipY \     de_dipY
        --------  =  3 | dx_dipY**3 --------  +  dy_dipY**3 --------  +  dz_dipY**3 -------- |  +  -------- ,
          dOi          \              dOi                     dOi                     dOi    /       dOi


    where

        de_dipY      1 /           /           ddx_dipY                     /         ddz_dipY             ddy_dipY \ \ 
        --------  =  - | (1 + 3Dr) |dx_dipY**3 --------  +  dy_dipY.dz_dipY | dy_dipY --------  +  dz_dipY -------- | |
          dOi        R \           \             dOi                        \           dOi                  dOi    / /

                              /            ddy_dipY                     /         ddz_dipY             ddx_dipY \ \ 
                  + (1 - 3Dr) | dy_dipY**3 --------  +  dx_dipY.dz_dipY | dx_dipY --------  +  dz_dipY -------- | |
                              \              dOi                        \           dOi                  dOi    / /

                      /            ddz_dipY                     /         ddy_dipY             ddx_dipY \ \ \ 
                  - 2 | dz_dipY**3 --------  +  dx_dipY.dy_dipY | dx_dipY --------  +  dy_dipY -------- | | | ,
                      \              dOi                        \           dOi                  dOi    / / /


    and where the orietation parameter set O is

        O = {alpha, beta, gamma}.


    tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_dipY
        ---------  =  0,
          dtm

        dc-1_dipY
        ---------  =  0,
          dtm

        dc0_dipY
        --------   =  0,
          dtm

        dc1_dipY
        --------   =  0,
          dtm

        dc2_dipY
        --------   =  0.
          dtm


    Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_dipY
        ---------  =  0,
          dDa

        dc-1_dipY
        ---------  =  0,
          dDa

        dc0_dipY
        --------   =  0,
          dDa

        dc1_dipY
        --------   =  0,
          dDa

        dc2_dipY
        --------   =  0.
          dDa



    Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_dipY       3 de_dipY
        ---------  =  - - --------,
          dDr           4   dDr

        dc-1_dipY
        ---------  =  0,
          dDr

        dc0_dipY
        --------   =  0,
          dDr

        dc1_dipY
        --------   =  0,
          dDr

        dc2_dipY      3 de_dipY
        --------   =  - --------,
          dDr         4   dDr

    where

        de_dipY       1   /                                                                                                                                             \ 
        --------  =  ---- | (1 - Dr) (dx_dipY**4 + 2dy_dipY**2.dz_dipY**2) - (1 + Dr) (dy_dipY**4 + 2dx_dipY**2.dz_dipY**2) + 2Dr (dz_dipY**4 + 2dx_dipY**2.dy_dipY**2) | .
          dDr        R**3 \                                                                                                                                             /


    """

    # Factors.
    data.one_3Dr = 1.0 + 3.0 * diff_data.params[2]
    data.one_m3Dr = 1.0 - 3.0 * diff_data.params[2]
    data.dx_dipY_sqrd = data.dx_dipY[i]**2
    data.dy_dipY_sqrd = data.dy_dipY[i]**2
    data.dz_dipY_sqrd = data.dz_dipY[i]**2
    data.dx_dipY_cubed = data.dx_dipY[i]**3
    data.dy_dipY_cubed = data.dy_dipY[i]**3
    data.dz_dipY_cubed = data.dz_dipY[i]**3
    data.dx_dipY_quar = data.dx_dipY[i]**4
    data.dy_dipY_quar = data.dy_dipY[i]**4
    data.dz_dipY_quar = data.dz_dipY[i]**4

    # Components.
    data.ex_dipY = data.dx_dipY_quar + 2.0 * data.dy_dipY_sqrd * data.dz_dipY_sqrd
    data.ey_dipY = data.dy_dipY_quar + 2.0 * data.dx_dipY_sqrd * data.dz_dipY_sqrd
    data.ez_dipY = data.dz_dipY_quar + 2.0 * data.dx_dipY_sqrd * data.dy_dipY_sqrd



    # Factors.
    data.inv_R_cubed = data.inv_R ** 3
    data.one_Dr = 1.0 + diff_data.params[2]
    data.one_mDr = 1.0 - diff_data.params[2]


    # Oi partial derivative.
    ##########################

    # Components.
    data.ci_dipY_xy = data.dx_dipY[i] * data.dy_dipY[i] * (data.dx_dipY[i] * data.ddy_dipY_dO[i]  +  data.dy_dipY[i] * data.ddx_dipY_dO[i])
    data.ci_dipY_xz = data.dx_dipY[i] * data.dz_dipY[i] * (data.dx_dipY[i] * data.ddz_dipY_dO[i]  +  data.dz_dipY[i] * data.ddx_dipY_dO[i])
    data.ci_dipY_yz = data.dy_dipY[i] * data.dz_dipY[i] * (data.dy_dipY[i] * data.ddz_dipY_dO[i]  +  data.dz_dipY[i] * data.ddy_dipY_dO[i])

    data.ci_dipY_x = data.dx_dipY_cubed * data.ddx_dipY_dO[i]
    data.ci_dipY_y = data.dy_dipY_cubed * data.ddy_dipY_dO[i]
    data.ci_dipY_z = data.dz_dipY_cubed * data.ddz_dipY_dO[i]

    data.ci_dipY_X = data.ci_dipY_x + data.ci_dipY_yz
    data.ci_dipY_Y = data.ci_dipY_y + data.ci_dipY_xz
    data.ci_dipY_Z = data.ci_dipY_z + data.ci_dipY_xy

    # Calculate dd_dOi.
    dd_dipY_dOi = 3.0 * (data.ci_dipY_x + data.ci_dipY_y + data.ci_dipY_z)

    # Calculate de_dOi.
    de_dipY_dOi = data.inv_R * (data.one_3Dr * data.ci_dipY_X  +  data.one_m3Dr * data.ci_dipY_Y  -  2.0 * data.ci_dipY_Z)

    # Weight c-2.
    data.dci_dipY[i][3:, 0] = dd_dipY_dOi - de_dipY_dOi

    # Weight c-1.
    data.dci_dipY[i][3:, 1] = 6.0 * data.ci_dipY_yz

    # Weight c0.
    data.dci_dipY[i][3:, 2] = 6.0 * data.ci_dipY_xz

    # Weight c1.
    data.dci_dipY[i][3:, 3] = 6.0 * data.ci_dipY_xy

    # Weight c2.
    data.dci_dipY[i][3:, 4] = dd_dipY_dOi + de_dipY_dOi


    # Dr partial derivative.
    ########################

    # Calculate de_dDr.
    de_dipY_dDr = data.inv_R_cubed * (data.one_mDr * data.ex_dipY  -  data.one_Dr * data.ey_dipY  +  2.0 * diff_data.params[2] * data.ez_dipY)

    # Weight c-2.
    data.dci_dipY[i][2, 0] = -0.75 * de_dipY_dDr

    # Weight c2.
    data.dci_dipY[i][2, 4] = 0.75 * de_dipY_dDr



# Ellipsoid weight Hessian.
###########################

def calc_dipY_ellipsoid_d2ci(data, diff_data, i):
    """Weight Hessian for ellipsoidal diffusion.

    Oi-Oj partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY        /            /          d2dx_dipY       ddx_dipY   ddx_dipY \                /          d2dy_dipY       ddy_dipY   ddy_dipY \                /          d2dz_dipY       ddz_dipY   ddz_dipY \ \       d2e
        ------------  =  3 | dx_dipY**2 | dx_dipY ------------ + 3 -------- . -------- |  +  dy_dipY**2 | dy_dipY ------------ + 3 -------- . -------- |  +  dz_dipY**2 | dz_dipY ------------ + 3 -------- . -------- | |  -  ------- ,
          dOi.dOj          \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / /     dOi.dOj


         d2c-1_dipY                   /          d2dz_dipY       ddz_dipY   ddz_dipY \                        / ddy_dipY   ddz_dipY     ddz_dipY   ddy_dipY \                  /          d2dy_dipY       ddy_dipY   ddy_dipY \ 
        ------------  =  6 dy_dipY**2 | dz_dipY ------------  +  -------- . -------- |  +  12 dy_dipY.dz_dipY | -------- . --------  +  -------- . -------- |  +  6 dz_dipY**2 | dy_dipY ------------  +  -------- . -------- | ,
          dOi.dOj                     \           dOi.dOj          dOi        dOj    /                        \   dOi        dOj          dOi        dOj    /                  \           dOi.dOj          dOi        dOj    /


         d2c0_dipY                    /          d2dz_dipY       ddz_dipY   ddz_dipY \                        / ddx_dipY   ddz_dipY     ddz_dipY   ddx_dipY \                  /          d2dx_dipY       ddx_dipY   ddx_dipY \ 
        ------------  =  6 dx_dipY**2 | dz_dipY ------------  +  -------- . -------- |  +  12 dx_dipY.dz_dipY | -------- . --------  +  -------- . -------- |  +  6 dz_dipY**2 | dx_dipY ------------  +  -------- . -------- | ,
          dOi.dOj                     \           dOi.dOj          dOi        dOj    /                        \   dOi        dOj          dOi        dOj    /                  \           dOi.dOj          dOi        dOj    /


         d2c1_dipY                    /          d2dy_dipY       ddy_dipY   ddy_dipY \                        / ddx_dipY   ddy_dipY     ddy_dipY   ddx_dipY \                  /          d2dx_dipY       ddx_dipY   ddx_dipY \ 
        ------------  =  6 dx_dipY**2 | dy_dipY ------------  +  -------- . -------- |  +  12 dx_dipY.dy_dipY | -------- . --------  +  -------- . -------- |  +  6 dy_dipY**2 | dx_dipY ------------  +  -------- . -------- | ,
          dOi.dOj                     \           dOi.dOj          dOi        dOj    /                        \   dOi        dOj          dOi        dOj    /                  \           dOi.dOj          dOi        dOj    /


         d2c2_dipY         /            /          d2dx_dipY       ddx_dipY   ddx_dipY \                /          d2dy_dipY       ddy_dipY   ddy_dipY \                /          d2dz_dipY       ddz_dipY   ddz_dipY \ \       d2e
        ------------  =  3 | dx_dipY**2 | dx_dipY ------------ + 3 -------- . -------- |  +  dy_dipY**2 | dy_dipY ------------ + 3 -------- . -------- |  +  dz_dipY**2 | dz_dipY ------------ + 3 -------- . -------- | |  +  ------------ ,
          dOi.dOj          \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / /     dOi.dOj

    where

          d2e_dipY       1 /           /            /          d2dx_dipY       ddx_dipY   ddx_dipY \                /          d2dz_dipY       ddz_dipY   ddz_dipY \ 
        ------------  =  - | (1 + 3Dr) | dx_dipY**2 | dx_dipY ------------ + 3 -------- . -------- |  +  dy_dipY**2 | dz_dipY ------------  +  -------- . -------- |
          dOi.dOj        R \           \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / 

                                               /          d2dy_dipY       ddy_dipY   ddy_dipY \                      / ddy_dipY   ddz_dipY     ddz_dipY   ddy_dipY \ \ 
                                  + dz_dipY**2 | dy_dipY ------------  +  -------- . -------- |  +  2dy_dipY.dz_dipY | -------- . --------  +  -------- . -------- | |
                                               \           dOi.dOj          dOi        dOj    /                      \   dOi        dOj          dOi        dOj    / /

                                  /            /          d2dy_dipY       ddy_dipY   ddy_dipY \                /          d2dz_dipY       ddz_dipY   ddz_dipY \ 
                      + (1 - 3Dr) | dy_dipY**2 | dy_dipY ------------ + 3 -------- . -------- |  +  dx_dipY**2 | dz_dipY ------------  +  -------- . -------- |
                                  \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / 

                                               /          d2dx_dipY       ddx_dipY   ddx_dipY \                      / ddx_dipY   ddz_dipY     ddz_dipY   ddx_dipY \ \ 
                                  + dz_dipY**2 | dx_dipY ------------  +  -------- . -------- |  +  2dx_dipY.dz_dipY | -------- . --------  +  -------- . -------- | |
                                               \           dOi.dOj          dOi        dOj    /                      \   dOi        dOj          dOi        dOj    / /

                          /            /          d2dz_dipY       ddz_dipY   ddz_dipY \                /          d2dy_dipY       ddy_dipY   ddy_dipY \ 
                      - 2 | dz_dipY**2 | dz_dipY ------------ + 3 -------- . -------- |  +  dx_dipY**2 | dy_dipY ------------  +  -------- . -------- |
                          \            \           dOi.dOj          dOi        dOj    /                \           dOi.dOj          dOi        dOj    / 

                                       /          d2dx_dipY       ddx_dipY   ddx_dipY \                      / ddx_dipY   ddy_dipY     ddy_dipY   ddx_dipY \ \ \ 
                          + dy_dipY**2 | dx_dipY ------------  +  -------- . -------- |  +  2dx_dipY.dy_dipY | -------- . --------  +  -------- . -------- | | |
                                       \           dOi.dOj          dOi        dOj    /                      \   dOi        dOj          dOi        dOj    / / /


    Oi-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY
        ------------  =  0,
          dOi.dtm


         d2c-1_dipY
        ------------  =  0,
          dOi.dtm


         d2c0_dipY
        ------------  =  0,
          dOi.dtm


         d2c1_dipY
        ------------  =  0,
          dOi.dtm


         d2c2_dipY
        ------------  =  0.
          dOi.dtm


    Oi-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY
        ------------  =  0,
          dOi.dDa


         d2c-1_dipY
        ------------  =  0,
          dOi.dDa


         d2c0_dipY
        ------------  =  0,
          dOi.dDa


         d2c1_dipY
        ------------  =  0,
          dOi.dDa


         d2c2_dipY
        ------------  =  0.
          dOi.dDa


    Oi-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY            d2e
        ------------  =  - 3 -------,
          dOi.dDr            dOi.dDr


         d2c-1_dipY
        ------------  =  0,
          dOi.dDr


         d2c0_dipY
        ------------  =  0,
          dOi.dDr


         d2c1_dipY
        ------------  =  0,
          dOi.dDr


         d2c2_dipY           d2e
        ------------  =  3 -------,
          dOi.dDr          dOi.dDr

    where

         d2e_dipY         1   /          /            ddx_dipY                     /         ddz_dipY             ddy_dipY \ \ 
        ------------  =  ---- | (1 - Dr) | dx_dipY**3 --------  +  dy_dipY.dz_dipY | dy_dipY --------  +  dz_dipY -------- | |
          dOi.dDr        R**3 \          \              dOi                        \           dOi                  dOi    / /

                                    /            ddy_dipY                     /         ddz_dipY             ddx_dipY \ \ 
                         - (1 + Dr) | dy_dipY**3 --------  +  dx_dipY.dz_dipY | dx_dipY --------  +  dz_dipY -------- | |
                                    \              dOi                        \           dOi                  dOi    / /

                               /            ddz_dipY                     /         ddy_dipY             ddx_dipY \ \ \ 
                         + 2Dr | dz_dipY**3 --------  +  dx_dipY.dy_dipY | dx_dipY --------  +  dy_dipY -------- | | |
                               \              dOi                        \           dOi                  dOi    / / /


    tm-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_dipY
        ----------  =  0,
          dtm2


        d2c-1_dipY
        ----------  =  0,
          dtm2


        d2c0_dipY
        ---------   =  0,
          dtm2


        d2c1_dipY
        ---------   =  0,
          dtm2


        d2c2_dipY
        ---------   =  0.
          dtm2


    tm-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY
        ------------  =  0,
          dtm.dDa


         d2c-1_dipY
        ------------  =  0,
          dtm.dDa


         d2c0_dipY
        ------------  =  0,
          dtm.dDa


         d2c1_dipY
        ------------  =  0,
          dtm.dDa


         d2c2_dipY
        ------------  =  0.
          dtm.dDa


    tm-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY
        ------------  =  0,
          dtm.dDr


         d2c-1_dipY
        ------------  =  0,
          dtm.dDr


         d2c0_dipY
        ------------  =  0,
          dtm.dDr


         d2c1_dipY
        ------------  =  0,
          dtm.dDr


         d2c2_dipY
        ------------  =  0.
          dtm.dDr


    Da-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_dipY
        -----------  =  0,
          dDa**2


        d2c-1_dipY
        -----------  =  0,
          dDa**2


         d2c0_dipY
        -----------  =  0,
          dDa**2


         d2c1_dipY
        -----------  =  0,
          dDa**2


         d2c2_dipY
        -----------  =  0.
          dDa**2


    Da-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_dipY
        ------------  =  0,
          dDa.dDr


         d2c-1_dipY
        ------------  =  0,
          dDa.dDr


         d2c0_dipY
        ------------  =  0,
          dDa.dDr


         d2c1_dipY
        ------------  =  0,
          dDa.dDr


         d2c2_dipY
        ------------  =  0.
          dDa.dDr


    Dr-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_dipY        3  d2e
        -----------  =  - - ------,
          dDr**2          4 dDr**2


        d2c-1_dipY
        -----------  =  0,
          dDr**2


         d2c0_dipY
        -----------  =  0,
          dDr**2


         d2c1_dipY
        -----------  =  0,
          dDr**2


         d2c2_dipY      3  d2e
        -----------  =  - ------,
          dDr**2        4 dDr**2

    where

         d2e_dipY        1   /                                                                                                                                                                        \ 
        -----------  =  ---- | (6Dr**2 - 9Dr - 1)(dx_dipY**4 + 2dy_dipY**2.dz_dipY**2) + (6Dr**2 + 9Dr - 1)(dy_dipY**4 + 2dx_dipY**2.dz_dipY**2) - 2(6Dr**2 - 1)(ddz_dipY*4 + 2dx_dipY**2.dy_dipY**2) |
          dDr**2        R**5 \                                                                                                                                                                        /
     """

    # Factors.
    data.one_3Dr = 1.0 + 3.0 * diff_data.params[2]
    data.one_m3Dr = 1.0 - 3.0 * diff_data.params[2]
    data.dx_dipY_sqrd = data.dx_dipY[i]**2
    data.dy_dipY_sqrd = data.dy_dipY[i]**2
    data.dz_dipY_sqrd = data.dz_dipY[i]**2
    data.dx_dipY_cubed = data.dx_dipY[i]**3
    data.dy_dipY_cubed = data.dy_dipY[i]**3
    data.dz_dipY_cubed = data.dz_dipY[i]**3
    data.dx_dipY_quar = data.dx_dipY[i]**4
    data.dy_dipY_quar = data.dy_dipY[i]**4
    data.dz_dipY_quar = data.dz_dipY[i]**4

    # Components.
    data.ex_dipY = data.dx_dipY_quar + 2.0 * data.dy_dipY_sqrd * data.dz_dipY_sqrd
    data.ey_dipY = data.dy_dipY_quar + 2.0 * data.dx_dipY_sqrd * data.dz_dipY_sqrd
    data.ez_dipY = data.dz_dipY_quar + 2.0 * data.dx_dipY_sqrd * data.dy_dipY_sqrd



    # Oi-Oj partial derivative.
    ###############################

    # Outer products.
    op_dipY_xx = outerproduct(data.ddx_dipY_dO[i], data.ddx_dipY_dO[i])
    op_dipY_yy = outerproduct(data.ddy_dipY_dO[i], data.ddy_dipY_dO[i])
    op_dipY_zz = outerproduct(data.ddz_dipY_dO[i], data.ddz_dipY_dO[i])

    op_dipY_xy = outerproduct(data.ddx_dipY_dO[i], data.ddy_dipY_dO[i])
    op_dipY_yx = outerproduct(data.ddy_dipY_dO[i], data.ddx_dipY_dO[i])

    op_dipY_xz = outerproduct(data.ddx_dipY_dO[i], data.ddz_dipY_dO[i])
    op_dipY_zx = outerproduct(data.ddz_dipY_dO[i], data.ddx_dipY_dO[i])

    op_dipY_yz = outerproduct(data.ddy_dipY_dO[i], data.ddz_dipY_dO[i])
    op_dipY_zy = outerproduct(data.ddz_dipY_dO[i], data.ddy_dipY_dO[i])

    # Components.
    x_comp_dipY = data.dx_dipY[i] * data.d2dx_dipY_dO2[i] + op_dipY_xx
    y_comp_dipY = data.dy_dipY[i] * data.d2dy_dipY_dO2[i] + op_dipY_yy
    z_comp_dipY = data.dz_dipY[i] * data.d2dz_dipY_dO2[i] + op_dipY_zz

    x3_comp_dipY = data.dx_dipY_sqrd * (data.dx_dipY[i] * data.d2dx_dipY_dO2[i] + 3.0 * op_dipY_xx)
    y3_comp_dipY = data.dy_dipY_sqrd * (data.dy_dipY[i] * data.d2dy_dipY_dO2[i] + 3.0 * op_dipY_yy)
    z3_comp_dipY = data.dz_dipY_sqrd * (data.dz_dipY[i] * data.d2dz_dipY_dO2[i] + 3.0 * op_dipY_zz)

    xy_comp_dipY = data.dx_dipY_sqrd * y_comp_dipY  +  2.0 * data.dx_dipY[i] * data.dy_dipY[i] * (op_dipY_xy + op_dipY_yx)  +  data.dy_dipY_sqrd * x_comp_dipY
    xz_comp_dipY = data.dx_dipY_sqrd * z_comp_dipY  +  2.0 * data.dx_dipY[i] * data.dz_dipY[i] * (op_dipY_xz + op_dipY_zx)  +  data.dz_dipY_sqrd * x_comp_dipY
    yz_comp_dipY = data.dy_dipY_sqrd * z_comp_dipY  +  2.0 * data.dy_dipY[i] * data.dz_dipY[i] * (op_dipY_yz + op_dipY_zy)  +  data.dz_dipY_sqrd * y_comp_dipY

    # Calculate d2d_dOidOj.
    d2d_dipY_dOidOj = 3.0 * (x3_comp_dipY + y3_comp_dipY + z3_comp_dipY)

    # Calculate d2e_dOidOj.
    d2e_dipY_dOidOj = data.inv_R * (data.one_3Dr * (x3_comp_dipY + yz_comp_dipY) + data.one_m3Dr * (y3_comp_dipY + xz_comp_dipY) - 2.0 * (z3_comp_dipY + xy_comp_dipY))

    # Weight c-2.
    data.d2ci_dipY[i][3:, 3:, 0] = d2d_dipY_dOidOj - d2e_dipY_dOidOj

    # Weight c-2.
    data.d2ci_dipY[i][3:, 3:, 1] = 6.0 * yz_comp_dipY

    # Weight c-1.
    data.d2ci_dipY[i][3:, 3:, 2] = 6.0 * xz_comp_dipY

    # Weight c1.
    data.d2ci_dipY[i][3:, 3:, 3] = 6.0 * xy_comp_dipY

    # Weight c2.
    data.d2ci_dipY[i][3:, 3:, 4] = d2d_dipY_dOidOj + d2e_dipY_dOidOj


    # Oi-Dr partial derivative.
    #############################

    # Calculate d2e_dOidDr.
    d2e_dipY_dOidDr = data.inv_R_cubed * (data.one_mDr * data.ci_dipY_X  -  data.one_Dr * data.ci_dipY_Y  +  2.0 * diff_data.params[2] * data.ci_dipY_Z)

    # Weight c0.
    data.d2ci_dipY[i][3:, 2, 0] = data.d2ci_dipY[i][2, 3:, 0] = -3.0 * d2e_dipY_dOidDr

    # Weight c2.
    data.d2ci_dipY[i][3:, 2, 4] = data.d2ci_dipY[i][2, 3:, 4] = 3.0 * d2e_dipY_dOidDr


    # Dr-Dr partial derivative.
    ###########################

    # Components
    d2e1_dDr2 = 6.0 * diff_data.params[2]**2  -  9.0 * diff_data.params[2]  -  1.0
    d2e2_dDr2 = 6.0 * diff_data.params[2]**2  +  9.0 * diff_data.params[2]  -  1.0
    d2e3_dDr2 = 6.0 * diff_data.params[2]**2  -  1.0

    # Calculate d2e_dipY_dDr2.
    d2e_dipY_dDr2 = data.inv_R**5 * (d2e1_dDr2 * data.ex_dipY  +  d2e2_dDr2 * data.ey_dipY  -  2.0 * d2e3_dDr2 * data.ez_dipY)

    # Weight c0.
    data.d2ci_dipY[i][2, 2, 0] = -0.75 * d2e_dipY_dDr2

    # Weight c2.
    data.d2ci_dipY[i][2, 2, 4] = 0.75 * d2e_dipY_dDr2
