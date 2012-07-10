###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Python module imports.
from math import sqrt
from numpy import outer


##########
# Sphere #
##########


# Sphere weight.
################

def calc_sphere_ci(data, diff_data):
    """Weight for spherical diffusion.

    The equation is::

        c0 = 1.
    """

    data.ci[0] = 1.0




############
# Spheroid #
############


# Spheroid weights.
###################

def calc_spheroid_ci(data, diff_data):
    """Weights for spheroidal diffusion.

    The equations are::

        c-1 = 1/4 (3dz**2 - 1)**2,

        c0  = 3dz**2 (1 - dz**2),

        c1  = 3/4 (dz**2 - 1)**2,

    where dz is the direction cosine of the unit bond vector along the z-axis of the diffusion
    tensor which is calculated as the dot product of the unit bond vector with a unit vector along
    Dpar.
    """

    # Components.
    data.three_dz2_one = 3.0 * data.dz**2 - 1.0
    data.one_two_dz2 = 1.0 - 2.0 * data.dz**2
    data.one_dz2 = 1.0 - data.dz**2
    data.dz2_one = -data.one_dz2

    # Weights.
    data.ci[0] = 0.25 * data.three_dz2_one**2
    data.ci[1] = 3.0 * data.dz**2 * data.one_dz2
    data.ci[2] = 0.75 * data.dz2_one**2



# Spheroid weight gradient.
###########################

def calc_spheroid_dci(data, diff_data):
    """Weight gradient for spheroidal diffusion.

    The equations are::

        dc-1                     ddz
        ---- =  3dz (3dz**2 - 1) --- ,
        dOi                      dOi

        dc0                      ddz
        ---  =  6dz (1 - 2dz**2) --- ,
        dOi                      dOi

        dc1                     ddz
        ---  =  3dz (dz**2 - 1) --- ,
        dOi                     dOi

    where the orientation parameter set O is {theta, phi}.
    """

    # Components.
    data.dci[2:, 0] = 3.0 * data.dz * data.three_dz2_one * data.ddz_dO
    data.dci[2:, 1] = 6.0 * data.dz * data.one_two_dz2 * data.ddz_dO
    data.dci[2:, 2] = 3.0 * data.dz * data.dz2_one * data.ddz_dO



# Spheroid weight Hessian.
##########################

def calc_spheroid_d2ci(data, diff_data):
    """Weight Hessian for spheroidal diffusion.

    The equations are::

         d2c-1        /             ddz   ddz                      d2dz   \ 
        -------  =  3 |(9dz**2 - 1) --- . ---  +  dz (3dz**2 - 1) ------- | ,
        dOi.dOj       \             dOi   dOj                     dOi.dOj /

         d2c0         /             ddz   ddz                      d2dz   \ 
        -------  =  6 |(1 - 6dz**2) --- . ---  +  dz (1 - 2dz**2) ------- | ,
        dOi.dOj       \             dOi   dOj                     dOi.dOj /

         d2c1         /             ddz   ddz                     d2dz   \ 
        -------  =  3 |(3dz**2 - 1) --- . ---  +  dz (dz**2 - 1) ------- | ,
        dOi.dOj       \             dOi   dOj                    dOi.dOj /

    where the orientation parameter set O is {theta, phi}.
    """

    # Outer product.
    op = outer(data.ddz_dO, data.ddz_dO)

    # Hessian.
    data.d2ci[2:, 2:, 0] = 3.0 * ((9.0 * data.dz**2 - 1.0) * op  +  data.dz * data.three_dz2_one * data.d2dz_dO2)
    data.d2ci[2:, 2:, 1] = 6.0 * ((1.0 - 6.0*data.dz**2) * op  +  data.dz * data.one_two_dz2 * data.d2dz_dO2)
    data.d2ci[2:, 2:, 2] = 3.0 * (data.three_dz2_one * op  +  data.dz * data.dz2_one * data.d2dz_dO2)




#############
# Ellipsoid #
#############


# Ellipsoid weights.
####################

def calc_ellipsoid_ci(data, diff_data):
    """Weight equations for ellipsoidal diffusion.

    The equations are::

        c-2 = 1/4 (d - e),

        c-1 = 3dy**2.dz**2,

        c0  = 3dx**2.dz**2,

        c1  = 3dx**2.dy**2,

        c2  = 1/4 (d + e),

    where::

        d  = 3(dx**4 + dy**4 + dz**4) - 1,

        e  =  1/R [(1 + 3Dr)(dx**4 + 2dy**2.dz**2) + (1 - 3Dr)(dy**4 + 2dx**2.dz**2)
                   - 2(dz**4 + 2dx**2.dy**2)],

    and where the factor R is defined as::
             ___________
        R = V 1 + 3Dr**2.

    dx, dy, and dz are the direction cosines of the XH bond vector along the x, y, and z-axes of the
    diffusion tensor, calculated as the dot product of the unit bond vector and the unit vectors
    along Dx, Dy, and Dz respectively.
    """

    # Calculate R.
    data.R = sqrt(1 + 3.0*diff_data.params[2]**2)
    data.inv_R = 1.0 / data.R

    # Factors.
    data.one_3Dr = 1.0 + 3.0 * diff_data.params[2]
    data.one_m3Dr = 1.0 - 3.0 * diff_data.params[2]
    data.dx_sqrd = data.dx**2
    data.dy_sqrd = data.dy**2
    data.dz_sqrd = data.dz**2
    data.dx_cubed = data.dx**3
    data.dy_cubed = data.dy**3
    data.dz_cubed = data.dz**3
    data.dx_quar = data.dx**4
    data.dy_quar = data.dy**4
    data.dz_quar = data.dz**4

    # Components.
    data.ex = data.dx_quar + 2.0 * data.dy_sqrd * data.dz_sqrd
    data.ey = data.dy_quar + 2.0 * data.dx_sqrd * data.dz_sqrd
    data.ez = data.dz_quar + 2.0 * data.dx_sqrd * data.dy_sqrd

    # Calculate d.
    d = 3.0 * (data.dx_quar + data.dy_quar + data.dz_quar) - 1.0

    # Calculate e.
    e = data.inv_R * (data.one_3Dr * data.ex  +  data.one_m3Dr * data.ey  -  2.0 * data.ez)

    # Weight c-2.
    data.ci[0] = 0.25 * (d - e)

    # Weight c-1.
    data.ci[1] = 3.0 * data.dy**2 * data.dz**2

    # Weight c0.
    data.ci[2] = 3.0 * data.dx**2 * data.dz**2

    # Weight c1.
    data.ci[3] = 3.0 * data.dx**2 * data.dy**2

    # Weight c2.
    data.ci[4] = 0.25 * (d + e)



# Ellipsoid weight gradient.
############################

def calc_ellipsoid_dci(data, diff_data):
    """Weight gradient for ellipsoidal diffusion.

    Oi partial derivatives
    ======================

    The equations are::

        dc-2       /       ddx           ddy           ddz \     de
        ----  =  3 | dx**3 ---  +  dy**3 ---  +  dz**3 --- |  -  --- ,
        dOi        \       dOi           dOi           dOi /     dOi


        dc-1            /    ddz        ddy \ 
        ----  =  6dy.dz | dy ---  +  dz --- | ,
        dOi             \    dOi        dOi /


        dc0            /    ddz        ddx \ 
        ---  =  6dx.dz | dx ---  +  dz --- | ,
        dOi            \    dOi        dOi /


        dc1            /    ddy        ddx \ 
        ---  =  6dx.dy | dx ---  +  dy --- | ,
        dOi            \    dOi        dOi /


        dc2       /       ddx           ddy           ddz \     de
        ---  =  3 | dx**3 ---  +  dy**3 ---  +  dz**3 --- |  +  --- ,
        dOi       \       dOi           dOi           dOi /     dOi


    where::

        de      1 /           /      ddx           /    ddz        ddy \ \ 
        ---  =  - | (1 + 3Dr) |dx**3 ---  +  dy.dz | dy ---  +  dz --- | |
        dOi     R \           \      dOi           \    dOi        dOi / /

                              /       ddy           /    ddz        ddx \ \ 
                  + (1 - 3Dr) | dy**3 ---  +  dx.dz | dx ---  +  dz --- | |
                              \       dOi           \    dOi        dOi / /

                      /       ddz           /    ddy        ddx \ \ \ 
                  - 2 | dz**3 ---  +  dx.dy | dx ---  +  dy --- | | | ,
                      \       dOi           \    dOi        dOi / / /


    and where the orietation parameter set O is::

        O = {alpha, beta, gamma}.


    tm partial derivatives
    ======================

    The equations are::

        dc-2
        ----  =  0,
        dtm

        dc-1
        ----  =  0,
        dtm

        dc0
        ---   =  0,
        dtm

        dc1
        ---   =  0,
        dtm

        dc2
        ---   =  0.
        dtm


    Da partial derivatives
    ======================

    The equations are::

        dc-2
        ----  =  0,
        dDa

        dc-1
        ----  =  0,
        dDa

        dc0
        ---   =  0,
        dDa

        dc1
        ---   =  0,
        dDa

        dc2
        ---   =  0.
        dDa



    Dr partial derivatives
    ======================

    The equations are::

        dc-2       3 de
        ----  =  - - ---,
        dDr        4 dDr

        dc-1
        ----  =  0,
        dDr

        dc0
        ---   =  0,
        dDr

        dc1
        ---   =  0,
        dDr

        dc2      3 de
        ---   =  - ---,
        dDr      4 dDr

    where::

        de       1   /                                                                                                \ 
        ---  =  ---- | (1 - Dr) (dx**4 + 2dy**2.dz**2) - (1 + Dr) (dy**4 + 2dx**2.dz**2) + 2Dr (dz**4 + 2dx**2.dy**2) | .
        dDr     R**3 \                                                                                                /


    """

    # Factors.
    data.inv_R_cubed = data.inv_R ** 3
    data.one_Dr = 1.0 + diff_data.params[2]
    data.one_mDr = 1.0 - diff_data.params[2]


    # Oi partial derivative.
    ##########################

    # Components.
    data.ci_xy = data.dx * data.dy * (data.dx * data.ddy_dO  +  data.dy * data.ddx_dO)
    data.ci_xz = data.dx * data.dz * (data.dx * data.ddz_dO  +  data.dz * data.ddx_dO)
    data.ci_yz = data.dy * data.dz * (data.dy * data.ddz_dO  +  data.dz * data.ddy_dO)

    data.ci_x = data.dx_cubed * data.ddx_dO
    data.ci_y = data.dy_cubed * data.ddy_dO
    data.ci_z = data.dz_cubed * data.ddz_dO

    data.ci_X = data.ci_x + data.ci_yz
    data.ci_Y = data.ci_y + data.ci_xz
    data.ci_Z = data.ci_z + data.ci_xy

    # Calculate dd_dOi.
    dd_dOi = 3.0 * (data.ci_x + data.ci_y + data.ci_z)

    # Calculate de_dOi.
    de_dOi = data.inv_R * (data.one_3Dr * data.ci_X  +  data.one_m3Dr * data.ci_Y  -  2.0 * data.ci_Z)

    # Weight c-2.
    data.dci[3:, 0] = dd_dOi - de_dOi

    # Weight c-1.
    data.dci[3:, 1] = 6.0 * data.ci_yz

    # Weight c0.
    data.dci[3:, 2] = 6.0 * data.ci_xz

    # Weight c1.
    data.dci[3:, 3] = 6.0 * data.ci_xy

    # Weight c2.
    data.dci[3:, 4] = dd_dOi + de_dOi


    # Dr partial derivative.
    ########################

    # Calculate de_dDr.
    de_dDr = data.inv_R_cubed * (data.one_mDr * data.ex  -  data.one_Dr * data.ey  +  2.0 * diff_data.params[2] * data.ez)

    # Weight c-2.
    data.dci[2, 0] = -0.75 * de_dDr

    # Weight c2.
    data.dci[2, 4] = 0.75 * de_dDr



# Ellipsoid weight Hessian.
###########################

def calc_ellipsoid_d2ci(data, diff_data):
    """Weight Hessian for ellipsoidal diffusion.

    Oi-Oj partial derivatives
    =========================

    The equations are::

         d2c-2        /       /     d2dx       ddx   ddx \           /     d2dy       ddy   ddy \           /     d2dz       ddz   ddz \ \       d2e
        -------  =  3 | dx**2 | dx ------- + 3 --- . --- |  +  dy**2 | dy ------- + 3 --- . --- |  +  dz**2 | dz ------- + 3 --- . --- | |  -  ------- ,
        dOi.dOj       \       \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj / /     dOi.dOj


         d2c-1              /     d2dz       ddz   ddz \              / ddy   ddz     ddz   ddy \             /     d2dy       ddy   ddy \ 
        -------  =  6 dy**2 | dz -------  +  --- . --- |  +  12 dy.dz | --- . ---  +  --- . --- |  +  6 dz**2 | dy -------  +  --- . --- | ,
        dOi.dOj             \    dOi.dOj     dOi   dOj /              \ dOi   dOj     dOi   dOj /             \    dOi.dOj     dOi   dOj /


         d2c0               /     d2dz       ddz   ddz \              / ddx   ddz     ddz   ddx \             /     d2dx       ddx   ddx \ 
        -------  =  6 dx**2 | dz -------  +  --- . --- |  +  12 dx.dz | --- . ---  +  --- . --- |  +  6 dz**2 | dx -------  +  --- . --- | ,
        dOi.dOj             \    dOi.dOj     dOi   dOj /              \ dOi   dOj     dOi   dOj /             \    dOi.dOj     dOi   dOj /


         d2c1               /     d2dy       ddy   ddy \              / ddx   ddy     ddy   ddx \             /     d2dx       ddx   ddx \ 
        -------  =  6 dx**2 | dy -------  +  --- . --- |  +  12 dx.dy | --- . ---  +  --- . --- |  +  6 dy**2 | dx -------  +  --- . --- | ,
        dOi.dOj             \    dOi.dOj     dOi   dOj /              \ dOi   dOj     dOi   dOj /             \    dOi.dOj     dOi   dOj /


         d2c2         /       /     d2dx       ddx   ddx \           /     d2dy       ddy   ddy \           /     d2dz       ddz   ddz \ \       d2e
        -------  =  3 | dx**2 | dx ------- + 3 --- . --- |  +  dy**2 | dy ------- + 3 --- . --- |  +  dz**2 | dz ------- + 3 --- . --- | |  +  ------- ,
        dOi.dOj       \       \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj / /     dOi.dOj

    where::

          d2e       1 /           /       /     d2dx       ddx   ddx \           /     d2dz       ddz   ddz \ 
        -------  =  - | (1 + 3Dr) | dx**2 | dx ------- + 3 --- . --- |  +  dy**2 | dz -------  +  --- . --- |
        dOi.dOj     R \           \       \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj / 

                                          /     d2dy       ddy   ddy \            / ddy   ddz     ddz   ddy \ \ 
                                  + dz**2 | dy -------  +  --- . --- |  +  2dy.dz | --- . ---  +  --- . --- | |
                                          \    dOi.dOj     dOi   dOj /            \ dOi   dOj     dOi   dOj / /

                                  /       /     d2dy       ddy   ddy \           /     d2dz       ddz   ddz \ 
                      + (1 - 3Dr) | dy**2 | dy ------- + 3 --- . --- |  +  dx**2 | dz -------  +  --- . --- |
                                  \       \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj / 

                                          /     d2dx       ddx   ddx \            / ddx   ddz     ddz   ddx \ \ 
                                  + dz**2 | dx -------  +  --- . --- |  +  2dx.dz | --- . ---  +  --- . --- | |
                                          \    dOi.dOj     dOi   dOj /            \ dOi   dOj     dOi   dOj / /

                          /       /     d2dz       ddz   ddz \           /     d2dy       ddy   ddy \ 
                      - 2 | dz**2 | dz ------- + 3 --- . --- |  +  dx**2 | dy -------  +  --- . --- |
                          \       \    dOi.dOj     dOi   dOj /           \    dOi.dOj     dOi   dOj / 

                                  /     d2dx       ddx   ddx \            / ddx   ddy     ddy   ddx \ \ \ 
                          + dy**2 | dx -------  +  --- . --- |  +  2dx.dy | --- . ---  +  --- . --- | | |
                                  \    dOi.dOj     dOi   dOj /            \ dOi   dOj     dOi   dOj / / /


    Oi-tm partial derivatives
    =========================

    The equations are::

         d2c-2
        -------  =  0,
        dOi.dtm


         d2c-1
        -------  =  0,
        dOi.dtm


         d2c0
        -------  =  0,
        dOi.dtm


         d2c1
        -------  =  0,
        dOi.dtm


         d2c2
        -------  =  0.
        dOi.dtm


    Oi-Da partial derivatives
    =========================

    The equations are::

         d2c-2
        -------  =  0,
        dOi.dDa


         d2c-1
        -------  =  0,
        dOi.dDa


         d2c0
        -------  =  0,
        dOi.dDa


         d2c1
        -------  =  0,
        dOi.dDa


         d2c2
        -------  =  0.
        dOi.dDa


    Oi-Dr partial derivatives
    =========================

    The equations are::

         d2c-2            d2e
        -------  =  - 3 -------,
        dOi.dDr         dOi.dDr


         d2c-1
        -------  =  0,
        dOi.dDr


         d2c0
        -------  =  0,
        dOi.dDr


         d2c1
        -------  =  0,
        dOi.dDr


         d2c2           d2e
        -------  =  3 -------,
        dOi.dDr       dOi.dDr

    where::

         d2e         1   /          /       ddx           /    ddz        ddy \ \ 
        -------  =  ---- | (1 - Dr) | dx**3 ---  +  dy.dz | dy ---  +  dz --- | |
        dOi.dDr     R**3 \          \       dOi           \    dOi        dOi / /

                                    /       ddy           /    ddz        ddx \ \ 
                         - (1 + Dr) | dy**3 ---  +  dx.dz | dx ---  +  dz --- | |
                                    \       dOi           \    dOi        dOi / /

                               /       ddz           /    ddy        ddx \ \ \ 
                         + 2Dr | dz**3 ---  +  dx.dy | dx ---  +  dy --- | | |
                               \       dOi           \    dOi        dOi / / /


    tm-tm partial derivatives
    =========================

    The equations are::

        d2c-2
        -----  =  0,
        dtm2


        d2c-1
        -----  =  0,
        dtm2


        d2c0
        ----   =  0,
        dtm2


        d2c1
        ----   =  0,
        dtm2


        d2c2
        ----   =  0.
        dtm2


    tm-Da partial derivatives
    =========================

    The equations are::

         d2c-2
        -------  =  0,
        dtm.dDa


         d2c-1
        -------  =  0,
        dtm.dDa


         d2c0
        -------  =  0,
        dtm.dDa


         d2c1
        -------  =  0,
        dtm.dDa


         d2c2
        -------  =  0.
        dtm.dDa


    tm-Dr partial derivatives
    =========================

    The equations are::

         d2c-2
        -------  =  0,
        dtm.dDr


         d2c-1
        -------  =  0,
        dtm.dDr


         d2c0
        -------  =  0,
        dtm.dDr


         d2c1
        -------  =  0,
        dtm.dDr


         d2c2
        -------  =  0.
        dtm.dDr


    Da-Da partial derivatives
    =========================

    The equations are::

        d2c-2
        ------  =  0,
        dDa**2


        d2c-1
        ------  =  0,
        dDa**2


         d2c0
        ------  =  0,
        dDa**2


         d2c1
        ------  =  0,
        dDa**2


         d2c2
        ------  =  0.
        dDa**2


    Da-Dr partial derivatives
    =========================

    The equations are::

         d2c-2
        -------  =  0,
        dDa.dDr


         d2c-1
        -------  =  0,
        dDa.dDr


         d2c0
        -------  =  0,
        dDa.dDr


         d2c1
        -------  =  0,
        dDa.dDr


         d2c2
        -------  =  0.
        dDa.dDr


    Dr-Dr partial derivatives
    =========================

    The equations are::

        d2c-2        3  d2e
        ------  =  - - ------,
        dDr**2       4 dDr**2


        d2c-1
        ------  =  0,
        dDr**2


         d2c0
        ------  =  0,
        dDr**2


         d2c1
        ------  =  0,
        dDr**2


         d2c2      3  d2e
        ------  =  - ------,
        dDr**2     4 dDr**2

    where::

         d2e        1   /                                                                                                                           \ 
        ------  =  ---- | (6Dr**2 - 9Dr - 1)(dx**4 + 2dy**2.dz**2) + (6Dr**2 + 9Dr - 1)(dy**4 + 2dx**2.dz**2) - 2(6Dr**2 - 1)(ddz*4 + 2dx**2.dy**2) |
        dDr**2     R**5 \                                                                                                                           /
     """

    # Oi-Oj partial derivative.
    ###############################

    # Outer products.
    op_xx = outer(data.ddx_dO, data.ddx_dO)
    op_yy = outer(data.ddy_dO, data.ddy_dO)
    op_zz = outer(data.ddz_dO, data.ddz_dO)

    op_xy = outer(data.ddx_dO, data.ddy_dO)
    op_yx = outer(data.ddy_dO, data.ddx_dO)

    op_xz = outer(data.ddx_dO, data.ddz_dO)
    op_zx = outer(data.ddz_dO, data.ddx_dO)

    op_yz = outer(data.ddy_dO, data.ddz_dO)
    op_zy = outer(data.ddz_dO, data.ddy_dO)

    # Components.
    x_comp = data.dx * data.d2dx_dO2 + op_xx
    y_comp = data.dy * data.d2dy_dO2 + op_yy
    z_comp = data.dz * data.d2dz_dO2 + op_zz

    x3_comp = data.dx_sqrd * (data.dx * data.d2dx_dO2 + 3.0 * op_xx)
    y3_comp = data.dy_sqrd * (data.dy * data.d2dy_dO2 + 3.0 * op_yy)
    z3_comp = data.dz_sqrd * (data.dz * data.d2dz_dO2 + 3.0 * op_zz)

    xy_comp = data.dx_sqrd * y_comp  +  2.0 * data.dx * data.dy * (op_xy + op_yx)  +  data.dy_sqrd * x_comp
    xz_comp = data.dx_sqrd * z_comp  +  2.0 * data.dx * data.dz * (op_xz + op_zx)  +  data.dz_sqrd * x_comp
    yz_comp = data.dy_sqrd * z_comp  +  2.0 * data.dy * data.dz * (op_yz + op_zy)  +  data.dz_sqrd * y_comp

    # Calculate d2d_dOidOj.
    d2d_dOidOj = 3.0 * (x3_comp + y3_comp + z3_comp)

    # Calculate d2e_dOidOj.
    d2e_dOidOj = data.inv_R * (data.one_3Dr * (x3_comp + yz_comp) + data.one_m3Dr * (y3_comp + xz_comp) - 2.0 * (z3_comp + xy_comp))

    # Weight c-2.
    data.d2ci[3:, 3:, 0] = d2d_dOidOj - d2e_dOidOj

    # Weight c-2.
    data.d2ci[3:, 3:, 1] = 6.0 * yz_comp

    # Weight c-1.
    data.d2ci[3:, 3:, 2] = 6.0 * xz_comp

    # Weight c1.
    data.d2ci[3:, 3:, 3] = 6.0 * xy_comp

    # Weight c2.
    data.d2ci[3:, 3:, 4] = d2d_dOidOj + d2e_dOidOj


    # Oi-Dr partial derivative.
    #############################

    # Calculate d2e_dOidDr.
    d2e_dOidDr = data.inv_R_cubed * (data.one_mDr * data.ci_X  -  data.one_Dr * data.ci_Y  +  2.0 * diff_data.params[2] * data.ci_Z)

    # Weight c0.
    data.d2ci[3:, 2, 0] = data.d2ci[2, 3:, 0] = -3.0 * d2e_dOidDr

    # Weight c2.
    data.d2ci[3:, 2, 4] = data.d2ci[2, 3:, 4] = 3.0 * d2e_dOidDr


    # Dr-Dr partial derivative.
    ###########################

    # Components
    d2e1_dDr2 = 6.0 * diff_data.params[2]**2  -  9.0 * diff_data.params[2]  -  1.0
    d2e2_dDr2 = 6.0 * diff_data.params[2]**2  +  9.0 * diff_data.params[2]  -  1.0
    d2e3_dDr2 = 6.0 * diff_data.params[2]**2  -  1.0

    # Calculate d2e_dDr2.
    d2e_dDr2 = data.inv_R**5 * (d2e1_dDr2 * data.ex  +  d2e2_dDr2 * data.ey  -  2.0 * d2e3_dDr2 * data.ez)

    # Weight c0.
    data.d2ci[2, 2, 0] = -0.75 * d2e_dDr2

    # Weight c2.
    data.d2ci[2, 2, 4] = 0.75 * d2e_dDr2
