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

from math import sqrt
from Numeric import outerproduct


# Isotropic weight equation.
############################

def calc_iso_ci(data, diff_data):
    """Weight equations for isotropic diffusion.

    c0 = 1
    """

    data.ci[0] = 1.0



# Axially symmetric weight equation.
####################################

def calc_axial_ci(data, diff_data):
    """Weight equations for axially symmetric diffusion.

    The equations are:

        c0 = 1/4 (3delta**2 - 1)**2
        c1 = 3delta**2 (1 - delta**2)
        c2 = 3/4 (1 - delta**2)**2

    where delta is the dot product of the unit bond vector and the unit vector along Dpar.
    """

    data.ci[0] = 0.25 * (3.0 * data.delta**2 - 1.0)**2
    data.ci[1] = 3.0 * data.delta**2 * (1.0 - data.delta**2)
    data.ci[2] = 0.75 * (1.0 - data.delta**2)**2



# Axially symmetric weight gradient.
####################################

def calc_axial_dci(data, diff_data):
    """Weight gradient for axially symmetric diffusion.

    The equations are:

         dc0                             ddelta
        -----  =  3delta (3delta**2 - 1) ------
        dpsii                            dpsii

         dc1                             ddelta
        -----  =  6delta (1 - 2delta**2) ------
        dpsii                            dpsii

         dc2                            ddelta
        -----  =  3delta (delta**2 - 1) ------
        dpsii                           dpsii

    where psi = {theta, phi}
    """

    data.dci[2:, 0] = 3.0 * data.delta * (3.0 * data.delta**2 - 1.0) * data.ddelta_dpsi
    data.dci[2:, 1] = 6.0 * data.delta * (1.0 - 2.0 * data.delta**2) * data.ddelta_dpsi
    data.dci[2:, 2] = 3.0 * data.delta * (data.delta**2 - 1.0) * data.ddelta_dpsi



# Axially symmetric weight Hessian.
###################################

def calc_axial_d2ci(data, diff_data):
    """Weight Hessian for axially symmetric diffusion.

    The equations are:

           d2c0           /                ddelta   ddelta                             d2delta   \ 
        -----------  =  3 |(9delta**2 - 1) ------ . ------  +  delta (3delta**2 - 1) ----------- |
        dpsii.dpsij       \                dpsii    dpsij                            dpsii.dpsij /

           d2c1           /                ddelta   ddelta                             d2delta   \ 
        -----------  =  6 |(1 - 6delta**2) ------ . ------  +  delta (1 - 2delta**2) ----------- |
        dpsii.dpsij       \                dpsii    dpsij                            dpsii.dpsij /

           d2c2           /                ddelta   ddelta                            d2delta   \ 
        -----------  =  3 |(3delta**2 - 1) ------ . ------  +  delta (delta**2 - 1) ----------- |
        dpsii.dpsij       \                dpsii    dpsij                           dpsii.dpsij /

    where psi = {theta, phi}
    """

    # Outer product.
    op = outerproduct(data.ddelta_dpsi, data.ddelta_dpsi)

    # Hessian.
    data.d2ci[2:, 2:, 0] = 3.0 * ((9.0 * data.delta**2 - 1.0) * op + data.delta * (3.0 * data.delta**2 - 1.0) * data.d2delta_dpsi2)
    data.d2ci[2:, 2:, 1] = 6.0 * ((1.0 - 6.0 * data.delta**2) * op + data.delta * (1.0 - 2.0 * data.delta**2) * data.d2delta_dpsi2)
    data.d2ci[2:, 2:, 2] = 3.0 * ((3.0 * data.delta**2 - 1.0) * op + data.delta * (data.delta**2 - 1.0) * data.d2delta_dpsi2)



# Anisotropic weight equation.
##############################

def calc_aniso_ci(data, diff_data):
    """Weight equations for anisotropic diffusion.

    In the following equations, the following short-hand notation will be used:

        da = delta_alpha

        db = delta_beta

        dg = delta_gamma


    The equations are:

        c-2 = 3da**2.db**2


        c-1 = 3da**2.dg**2


        c0  = 1/4 (3(da**4 + db**4 + dg**4) - 1 - e)


        c1  = 3db**2.dg**2


        c2  = 1/4 (3(da**4 + db**4 + dg**4) - 1 + e)


              Da - Dr                          Da + Dr                          2Da
        e  =  ------- (da**4 + 2db**2.dg**2) + ------- (db**4 + 2da**2.dg**2) - --- (dg**4 + 2da**2.db**2)
                mu                               mu                             mu


    where:
              __________________
        mu = V Da**2 + Dr**2 / 3

        delta_alpha is the dot product of the unit bond vector and the unit vector along Dx.

        delta_beta is the dot product of the unit bond vector and the unit vector along Dy.

        delta_gamma is the dot product of the unit bond vector and the unit vector along Dz.

        alpha (in delta_alpha) is the directional cosine along Dx.

        beta (in delta_beta) is the directional cosine along Dy.

        gamma (in delta_gamma) is the directional cosine along Dz.
    """

    # Calculate mu.
    data.mu = sqrt(diff_data.params[1]**2 + diff_data.params[2]**2 / 3.0)

    # Components.
    data.c_alpha = data.delta_alpha**4 + 2.0 * data.delta_beta**2  * data.delta_gamma**2
    data.c_beta  = data.delta_beta**4  + 2.0 * data.delta_alpha**2 * data.delta_gamma**2
    data.c_gamma = data.delta_gamma**4 + 2.0 * data.delta_alpha**2 * data.delta_beta**2

    if data.mu == 0.0:
        data.e1 = 0.0
        data.e2 = 0.0
        data.e3 = 0.0
    else:
        data.e1 = (diff_data.params[1] - diff_data.params[2]) / data.mu
        data.e2 = (diff_data.params[1] + diff_data.params[2]) / data.mu
        data.e3 = 2.0 * diff_data.params[1] / data.mu

    # Calculate d.
    d = 3.0 * (data.delta_alpha**4 + data.delta_beta**4 + data.delta_gamma**4) - 1.0

    # Calculate e.
    e = data.e1 * data.c_alpha + data.e2 * data.c_beta - data.e3 * data.c_gamma

    # Weight c-2.
    data.ci[0] = 3.0 * data.delta_alpha**2 * data.delta_beta**2

    # Weight c-1.
    data.ci[1] = 3.0 * data.delta_alpha**2 * data.delta_gamma**2

    # Weight c0.
    data.ci[2] = 0.25 * (d - e)

    # Weight c1.
    data.ci[3] = 3.0 * data.delta_beta**2 * data.delta_gamma**2

    # Weight c2.
    data.ci[4] = 0.25 * (d + e)


# Anisotropic weight gradient.
##############################

def calc_aniso_dci(data, diff_data):
    """Weight gradient for anisotropic diffusion.

    psii partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~

        dc-2             /     dda          ddb  \ 
        -----  =  6da.db | db -----  +  da ----- |
        dpsii            \    dpsii        dpsii /


        dc-1             /     dda          ddg  \ 
        -----  =  6da.dg | dg -----  +  da ----- |
        dpsii            \    dpsii        dpsii /


         dc0        /        dda             ddb             ddg  \      de
        -----  =  3 | da**3 -----  +  db**3 -----  +  dg**3 ----- |  -  -----
        dpsii       \       dpsii           dpsii           dpsii /     dpsii


         dc1             /     ddb          ddg  \ 
        -----  =  6db.dg | dg -----  +  db ----- |
        dpsii            \    dpsii        dpsii /


         dc2        /        dda             ddb             ddg  \      de
        -----  =  3 | da**3 -----  +  db**3 -----  +  dg**3 ----- |  +  -----
        dpsii       \       dpsii           dpsii           dpsii /     dpsii



         de         Da - Dr /        dda            /     ddb          ddg  \ \ 
        -----  =    ------- | da**3 -----  +  db.dg | dg -----  +  db ----- | |
        dpsii         mu    \       dpsii           \    dpsii        dpsii / /

                    Da + Dr /        ddb            /     dda          ddg  \ \ 
                  + ------- | db**3 -----  +  da.dg | dg -----  +  da ----- | |
                      mu    \       dpsii           \    dpsii        dpsii / /

                    2Da /        ddg            /     dda          ddb  \ \ 
                  - --- | dg**3 -----  +  da.db | db -----  +  da ----- | |
                    mu  \       dpsii           \    dpsii        dpsii / /


    where psi = {alpha, beta, gamma}.


    Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2
        ----  =  0
        dDa

        dc-1
        ----  =  0
        dDa

        dc0        1 de
        ---   =  - - ---
        dDa        4 dDa

        dc1
        ---   =  0
        dDa

        dc2      1 de
        ---   =  - ---
        dDa      4 dDa


        de      1 / (3Da + Dr)Dr                          (3Da - Dr)Dr                          2Dr**2                        \ 
        ---  =  - | ------------ (da**4 + 2db**2.dg**2) - ------------ (db**4 + 2da**2.dg**2) - ------ (dg**4 + 2da**2.db**2) |
        dDa     3 \    mu**3                                 mu**3                              mu**3                         /



    Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2
        ----  =  0
        dDr

        dc-1
        ----  =  0
        dDr

        dc0        1 de
        ---   =  - - ---
        dDr        4 dDr

        dc1
        ---   =  0
        dDr

        dc2      1 de
        ---   =  - ---
        dDr      4 dDr


        de        1 / (3Da + Dr)Da                          (3Da - Dr)Da                          2Da.Dr                        \ 
        ---  =  - - | ------------ (da**4 + 2db**2.dg**2) - ------------ (db**4 + 2da**2.dg**2) - ------ (dg**4 + 2da**2.db**2) |
        dDr       3 \    mu**3                                 mu**3                              mu**3                         /


    tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2
        ----  =  0
        dtm

        dc-1
        ----  =  0
        dtm

        dc0
        ---   =  0
        dtm

        dc1
        ---   =  0
        dtm

        dc2
        ---   =  0
        dtm

    """

    # psii partial derivative.
    ##########################

    # Components.
    data.dc_dpsii_alpha_beta = data.delta_alpha * data.delta_beta * (data.delta_beta * data.ddelta_alpha_dpsi  +  data.delta_alpha * data.ddelta_beta_dpsi)
    data.dc_dpsii_alpha_gamma = data.delta_alpha * data.delta_gamma * (data.delta_gamma * data.ddelta_alpha_dpsi  +  data.delta_alpha * data.ddelta_gamma_dpsi)
    data.dc_dpsii_beta_gamma = data.delta_beta * data.delta_gamma * (data.delta_gamma * data.ddelta_beta_dpsi  +  data.delta_beta * data.ddelta_gamma_dpsi)

    data.dc_dpsii_alpha = data.delta_alpha**3 * data.ddelta_alpha_dpsi
    data.dc_dpsii_beta = data.delta_beta**3 * data.ddelta_beta_dpsi
    data.dc_dpsii_gamma = data.delta_gamma**3 * data.ddelta_gamma_dpsi

    data.dc_dpsii_alpha_ext = data.dc_dpsii_alpha + data.dc_dpsii_beta_gamma
    data.dc_dpsii_beta_ext = data.dc_dpsii_beta + data.dc_dpsii_alpha_gamma
    data.dc_dpsii_gamma_ext = data.dc_dpsii_gamma + data.dc_dpsii_alpha_beta

    # Calculate dd_dpsii.
    dd_dpsii = 3.0 * (data.dc_dpsii_alpha + data.dc_dpsii_beta + data.dc_dpsii_gamma)

    # Calculate de_dpsii.
    de_dpsii = data.e1 * data.dc_dpsii_alpha_ext + data.e2 * data.dc_dpsii_beta_ext - data.e3 * data.dc_dpsii_gamma_ext

    # Weight c-2.
    data.dci[3:, 0] = 6.0 * data.dc_dpsii_alpha_beta

    # Weight c-1.
    data.dci[3:, 1] = 6.0 * data.dc_dpsii_alpha_gamma

    # Weight c0.
    data.dci[3:, 2] = dd_dpsii - de_dpsii

    # Weight c1.
    data.dci[3:, 3] = 6.0 * data.dc_dpsii_beta_gamma

    # Weight c2.
    data.dci[3:, 4] = dd_dpsii + de_dpsii


    # Da partial derivative.
    ########################

    # Components.
    data.mu_cubed = data.mu**3

    if data.mu == 0.0:
        data.de1_dDa = 0.0
        data.de2_dDa = 0.0
        data.de3_dDa = 0.0
    else:
        data.de1_dDa = (3.0 * diff_data.params[1] + diff_data.params[2]) * diff_data.params[2] / data.mu_cubed
        data.de2_dDa = (3.0 * diff_data.params[1] - diff_data.params[2]) * diff_data.params[2] / data.mu_cubed
        data.de3_dDa = 2.0 * diff_data.params[2]**2 / data.mu_cubed

    # Calculate de_dDa.
    de_dDa = (data.de1_dDa * data.c_alpha - data.de2_dDa * data.c_beta - data.de3_dDa * data.c_gamma) / 3.0

    # Weight c0.
    data.dci[1, 2] = -0.25 * de_dDa

    # Weight c2.
    data.dci[1, 4] = 0.25 * de_dDa


    # Dr partial derivative.
    ########################

    # Components.
    if data.mu == 0.0:
        data.de1_dDr = 0.0
        data.de2_dDr = 0.0
        data.de3_dDr = 0.0
    else:
        data.de1_dDr = (3.0 * diff_data.params[1] + diff_data.params[2]) * diff_data.params[1] / data.mu_cubed
        data.de2_dDr = (3.0 * diff_data.params[1] - diff_data.params[2]) * diff_data.params[1] / data.mu_cubed
        data.de3_dDr = 2.0 * diff_data.params[1] * diff_data.params[2] / data.mu_cubed

    # Calculate de_dDr.
    de_dDr = - (data.de1_dDr * data.c_alpha - data.de2_dDr * data.c_beta - data.de3_dDr * data.c_gamma) / 3.0

    # Weight c0.
    data.dci[2, 2] = -0.25 * de_dDr

    # Weight c2.
    data.dci[2, 4] = 0.25 * de_dDr


# Anisotropic weight Hessian.
#############################

def calc_aniso_d2ci(data, diff_data):
    """Weight Hessian for anisotropic diffusion.

    psii-psij partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

           d2c-2          /       /  dda     dda          d2da     \            /  dda     ddb     ddb     dda  \           /  ddb     ddb          d2db     \ \ 
        -----------  =  6 | db**2 | ----- . ----- + da ----------- |  +  2da.db | ----- . ----- + ----- . ----- |  +  da**2 | ----- . ----- + db ----------- | |
        dpsii.dpsij       \       \ dpsii   dpsij      dpsii.dpsij /            \ dpsii   dpsij   dpsii   dpsij /           \ dpsii   dpsij      dpsii.dpsij / /


           d2c-1          /       /  dda     dda          d2da     \            /  dda     ddg     ddg     dda  \           /  ddg     ddg          d2dg     \ \ 
        -----------  =  6 | dg**2 | ----- . ----- + da ----------- |  +  2da.dg | ----- . ----- + ----- . ----- |  +  da**2 | ----- . ----- + dg ----------- | |
        dpsii.dpsij       \       \ dpsii   dpsij      dpsii.dpsij /            \ dpsii   dpsij   dpsii   dpsij /           \ dpsii   dpsij      dpsii.dpsij / /


           d2c0           /       /  dda     dda          d2da     \           /  ddb     ddb          d2db     \           /  ddg     ddg          d2dg     \ \         d2e
        -----------  =  3 | da**2 | ----- . ----- + da ----------- |  +  db**2 | ----- . ----- + db ----------- |  +  dg**2 | ----- . ----- + dg ----------- | |  -  -----------
        dpsii.dpsij       \       \ dpsii   dpsij      dpsii.dpsij /           \ dpsii   dpsij      dpsii.dpsij /           \ dpsii   dpsij      dpsii.dpsij / /     dpsii.dpsij


           d2c1           /       /  ddb     ddb          d2db     \            /  ddb     ddg     ddg     ddb  \           /  ddg     ddg          d2dg     \ \ 
        -----------  =  6 | dg**2 | ----- . ----- + db ----------- |  +  2db.dg | ----- . ----- + ----- . ----- |  +  db**2 | ----- . ----- + dg ----------- | |
        dpsii.dpsij       \       \ dpsii   dpsij      dpsii.dpsij /            \ dpsii   dpsij   dpsii   dpsij /           \ dpsii   dpsij      dpsii.dpsij / /


           d2c2           /       /  dda     dda          d2da     \           /  ddb     ddb          d2db     \           /  ddg     ddg          d2dg     \ \         d2e
        -----------  =  3 | da**2 | ----- . ----- + da ----------- |  +  db**2 | ----- . ----- + db ----------- |  +  dg**2 | ----- . ----- + dg ----------- | |  +  -----------
        dpsii.dpsij       \       \ dpsii   dpsij      dpsii.dpsij /           \ dpsii   dpsij      dpsii.dpsij /           \ dpsii   dpsij      dpsii.dpsij / /     dpsii.dpsij



            d2e         Da - Dr /       /    dda     dda          d2da     \ 
        -----------  =  ------- | da**2 | 3 ----- . ----- + da ----------- |
        dpsii.dpsij       mu    \       \   dpsii   dpsij      dpsii.dpsij /

                                           /  ddb     ddb          d2db     \            /  ddb     ddg     ddg     ddb  \           /  ddg     ddg          d2dg     \ \ 
                                  +  dg**2 | ----- . ----- + db ----------- |  +  2db.dg | ----- . ----- + ----- . ----- |  +  db**2 | ----- . ----- + dg ----------- | |
                                           \ dpsii   dpsij      dpsii.dpsij /            \ dpsii   dpsij   dpsii   dpsij /           \ dpsii   dpsij      dpsii.dpsij / /

                        Da + Dr /       /    ddb     ddb          d2db     \ 
                     +  ------- | db**2 | 3 ----- . ----- + db ----------- |
                          mu    \       \   dpsii   dpsij      dpsii.dpsij /

                                           /  dda     dda          d2da     \            /  dda     ddg     ddg     dda  \           /  ddg     ddg          d2dg     \ \ 
                                  +  dg**2 | ----- . ----- + da ----------- |  +  2da.dg | ----- . ----- + ----- . ----- |  +  da**2 | ----- . ----- + dg ----------- | |
                                           \ dpsii   dpsij      dpsii.dpsij /            \ dpsii   dpsij   dpsii   dpsij /           \ dpsii   dpsij      dpsii.dpsij / /

                        2Da /       /    ddg     ddg          d2dg     \ 
                     -  --- | dg**2 | 3 ----- . ----- + da ----------- |
                        mu  \       \   dpsii   dpsij      dpsii.dpsij /

                                           /  dda     dda          d2da     \            /  dda     ddb     ddb     dda  \           /  ddb     ddb          d2db     \ \ 
                                  +  db**2 | ----- . ----- + da ----------- |  +  2da.db | ----- . ----- + ----- . ----- |  +  da**2 | ----- . ----- + db ----------- | |
                                           \ dpsii   dpsij      dpsii.dpsij /            \ dpsii   dpsij   dpsii   dpsij /           \ dpsii   dpsij      dpsii.dpsij / /


    psii-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2c-2
        ---------  =  0
        dpsii.dDa


          d2c-1
        ---------  =  0
        dpsii.dDa


          d2c0             d2e
        ---------  =  - ---------
        dpsii.dDa       dpsii.dDa


          d2c1
        ---------  =  0
        dpsii.dDa


          d2c2           d2e
        ---------  =  ---------
        dpsii.dDa     dpsii.dDa



           d2e          1 (3Da + Dr)Dr /        dda            /     ddb          ddg  \ \ 
        ---------  =    - ------------ | da**3 -----  +  db.dg | dg -----  +  db ----- | |
        dpsii.dDa       3    mu**3     \       dpsii           \    dpsii        dpsii / /

                        1 (3Da - Dr)Dr /        ddb            /     dda          ddg  \ \ 
                      - - ------------ | db**3 -----  +  da.dg | dg -----  +  da ----- | |
                        3    mu**3     \       dpsii           \    dpsii        dpsii / /

                        2 Dr**2 /        ddg            /     dda          ddb  \ \ 
                      - - ----- | dg**3 -----  +  da.db | db -----  +  da ----- | |
                        3 mu**3 \       dpsii           \    dpsii        dpsii / /


    psii-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2c-2
        ---------  =  0
        dpsii.dDr


          d2c-1
        ---------  =  0
        dpsii.dDr


          d2c0             d2e
        ---------  =  - ---------
        dpsii.dDr       dpsii.dDr


          d2c1
        ---------  =  0
        dpsii.dDr


          d2c2           d2e
        ---------  =  ---------
        dpsii.dDr     dpsii.dDr



           d2e          1 (3Da + Dr)Da /        dda            /     ddb          ddg  \ \ 
        ---------  =  - - ------------ | da**3 -----  +  db.dg | dg -----  +  db ----- | |
        dpsii.dDr       3    mu**3     \       dpsii           \    dpsii        dpsii / /

                        1 (3Da - Dr)Da /        ddb            /     dda          ddg  \ \ 
                      - - ------------ | db**3 -----  +  da.dg | dg -----  +  da ----- | |
                        3    mu**3     \       dpsii           \    dpsii        dpsii / /

                        2 Dr**2 /        ddg            /     dda          ddb  \ \ 
                      - - ----- | dg**3 -----  +  da.db | db -----  +  da ----- | |
                        3 mu**3 \       dpsii           \    dpsii        dpsii / /


    psii-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2c-2
        ---------  =  0
        dpsii.dtm


          d2c-1
        ---------  =  0
        dpsii.dtm


          d2c0
        ---------  =  0
        dpsii.dtm


          d2c1
        ---------  =  0
        dpsii.dtm


          d2c2
        ---------  =  0
        dpsii.dtm


    Da-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2
        ------  =  0
        dDa**2


        d2c-1
        ------  =  0
        dDa**2


         d2c0        1  d2e
        ------  =  - - ------
        dDa**2       4 dDa**2


         d2c1
        ------  =  0
        dDa**2


         d2c2      1  d2e
        ------  =  - ------
        dDa**2     4 dDa**2



         d2e         1 / (6Da**2 + 3Da.Dr - Dr**2)Dr                          (6Da**2 - 3Da.Dr - Dr**2)Dr                          6Da.Dr**2                        \ 
        ------  =  - - | --------------------------- (da**4 + 2db**2.dg**2) - --------------------------- (db**4 + 2da**2.dg**2) - --------- (dg**4 + 2da**2.db**2) |
        dDa**2       3 \           mu**5                                                mu**5                                        mu**5                          /


    Da-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2
        -------  =  0
        dDa.dDr


         d2c-1
        -------  =  0
        dDa.dDr


         d2c0         1   d2e
        -------  =  - - -------
        dDa.dDr       4 dDa.dDr


         d2c1
        -------  =  0
        dDa.dDr


         d2c2       1   d2e
        -------  =  - -------
        dDa.dDr     4 dDa.dDr



          d2e       1 / 9Da**3 + 6Da**2.Dr - 6Da.Dr**2 - Dr**3                          9Da**3 - 6Da**2.Dr - 6Da.Dr**2 + Dr**3
        -------  =  - | -------------------------------------- (da**4 + 2db**2.dg**2) - -------------------------------------- (db**4 + 2da**2.dg**2)
        dDa.dDr     9 \                mu**5                                                           mu**5

                          2(Da**2 - Dr**2)Dr                        \ 
                        - ------------------ (dg**4 + 2da**2.db**2) |
                                mu**5                               /


    Da-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2
        -------  =  0
        dDa.dtm


         d2c-1
        -------  =  0
        dDa.dtm


         d2c0
        -------  =  0
        dDa.dtm


         d2c1
        -------  =  0
        dDa.dtm


         d2c2
        -------  =  0
        dDa.dtm



    Dr-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2
        ------  =  0
        dDr**2


        d2c-1
        ------  =  0
        dDr**2


         d2c0        1  d2e
        ------  =  - - ------
        dDr**2       4 dDr**2


         d2c1
        ------  =  0
        dDr**2


         d2c2      1  d2e
        ------  =  - ------
        dDr**2     4 dDr**2



         d2e         1 / (3Da**2 - 9Da.Dr - 2Dr**2)Da                          (3Da**2 + 9Da.Dr - 2Dr**2)Da                          2(3Da**2 - 2Dr**2)Da                        \
        ------  =  - - | ---------------------------- (da**4 + 2db**2.dg**2) + ---------------------------- (db**4 + 2da**2.dg**2) - -------------------- (dg**4 + 2da**2.db**2) |
        dDr**2       9 \            mu**5                                                 mu**5                                             mu**5                                /


    Dr-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2
        -------  =  0
        dDr.dtm


         d2c-1
        -------  =  0
        dDr.dtm


         d2c0
        -------  =  0
        dDr.dtm


         d2c1
        -------  =  0
        dDr.dtm


         d2c2
        -------  =  0
        dDr.dtm

     """

    # psii-psij partial derivative.
    ###############################

    # Outer products.
    op_alpha = outerproduct(data.ddelta_alpha_dpsi, data.ddelta_alpha_dpsi)
    op_beta  = outerproduct(data.ddelta_beta_dpsi, data.ddelta_beta_dpsi)
    op_gamma = outerproduct(data.ddelta_gamma_dpsi, data.ddelta_gamma_dpsi)

    op_alpha_beta  = outerproduct(data.ddelta_alpha_dpsi, data.ddelta_beta_dpsi)
    op_beta_alpha  = outerproduct(data.ddelta_beta_dpsi, data.ddelta_alpha_dpsi)
    op_alpha_gamma = outerproduct(data.ddelta_alpha_dpsi, data.ddelta_gamma_dpsi)
    op_gamma_alpha = outerproduct(data.ddelta_gamma_dpsi, data.ddelta_alpha_dpsi)
    op_beta_gamma  = outerproduct(data.ddelta_beta_dpsi, data.ddelta_gamma_dpsi)
    op_gamma_beta  = outerproduct(data.ddelta_gamma_dpsi, data.ddelta_beta_dpsi)

    # Components.
    alpha_comp = op_alpha + data.delta_alpha * data.d2delta_alpha_dpsi2
    beta_comp  = op_beta  + data.delta_beta * data.d2delta_beta_dpsi2
    gamma_comp = op_gamma + data.delta_gamma * data.d2delta_gamma_dpsi2

    alpha3_comp = data.delta_alpha**2 * (3.0 * op_alpha + data.delta_alpha * data.d2delta_alpha_dpsi2)
    beta3_comp  = data.delta_beta**2  * (3.0 * op_beta  + data.delta_beta  * data.d2delta_beta_dpsi2)
    gamma3_comp = data.delta_gamma**2 * (3.0 * op_gamma + data.delta_gamma * data.d2delta_gamma_dpsi2)

    alpha_beta_comp  = data.delta_beta**2  * alpha_comp + 2.0 * data.delta_alpha * data.delta_beta  * (op_alpha_beta  + op_beta_alpha)  + data.delta_alpha**2 * beta_comp
    alpha_gamma_comp = data.delta_gamma**2 * alpha_comp + 2.0 * data.delta_alpha * data.delta_gamma * (op_alpha_gamma + op_gamma_alpha) + data.delta_alpha**2 * gamma_comp
    beta_gamma_comp  = data.delta_gamma**2 * beta_comp  + 2.0 * data.delta_beta  * data.delta_gamma * (op_beta_gamma  + op_gamma_beta)  + data.delta_beta**2  * gamma_comp

    # Calculate d2d_dpsii_dpsij.
    d2d_dpsii_dpsij = 3.0 * (alpha3_comp + beta3_comp + gamma3_comp)

    # Calculate d2e_dpsii_dpsij.
    d2e_dpsii_dpsij = data.e1 * (alpha3_comp + alpha_beta_comp) + data.e2 * (beta3_comp + alpha_gamma_comp) - data.e3 * (alpha3_comp + beta_gamma_comp)

    # Weight c-2.
    data.d2ci[3:, 3:, 0] = 6.0 * alpha_beta_comp

    # Weight c-1.
    data.d2ci[3:, 3:, 1] = 6.0 * alpha_gamma_comp

    # Weight c0.
    data.d2ci[3:, 3:, 2] = d2d_dpsii_dpsij - d2e_dpsii_dpsij

    # Weight c1.
    data.d2ci[3:, 3:, 3] = 6.0 * beta_gamma_comp

    # Weight c2.
    data.d2ci[3:, 3:, 4] = d2d_dpsii_dpsij + d2e_dpsii_dpsij


    # psii-Da partial derivative.
    #############################

    # Calculate d2e_dpsii_dDa.
    d2e_dpsii_dDa = 1.0 / 3.0 * (data.de1_dDa * data.dc_dpsii_alpha - data.de2_dDa * data.dc_dpsii_beta - data.de2_dDa * data.dc_dpsii_gamma)

    # Weight c0.
    data.d2ci[3:, 1, 2] = data.d2ci[1, 3:, 2] = -d2e_dpsii_dDa

    # Weight c2.
    data.d2ci[3:, 1, 4] = data.d2ci[1, 3:, 4] = d2e_dpsii_dDa


    # psii-Dr partial derivative.
    #############################

    # Calculate d2e_dpsii_dDr.
    d2e_dpsii_dDr = -1.0 / 3.0 * (data.de1_dDr * data.dc_dpsii_alpha - data.de2_dDr * data.dc_dpsii_beta - data.de2_dDr * data.dc_dpsii_gamma)

    # Weight c0.
    data.d2ci[3:, 2, 2] = data.d2ci[2, 3:, 2] = -d2e_dpsii_dDr

    # Weight c2.
    data.d2ci[3:, 2, 4] = data.d2ci[2, 3:, 4] = d2e_dpsii_dDr


    # Da-Da partial derivative.
    ###########################

    # Components.
    mu_five = data.mu**5

    if data.mu == 0.0:
        d2e1_dDa2 = 0.0
        d2e2_dDa2 = 0.0
        d2e3_dDa2 = 0.0
    else:
        d2e1_dDa2 = (6.0 * diff_data.params[1]**2 + 3.0 * diff_data.params[1] * diff_data.params[2] - diff_data.params[2]**2) * diff_data.params[2] / mu_five
        d2e2_dDa2 = (6.0 * diff_data.params[1]**2 - 3.0 * diff_data.params[1] * diff_data.params[2] - diff_data.params[2]**2) * diff_data.params[2] / mu_five
        d2e3_dDa2 = 6.0 * diff_data.params[1] * diff_data.params[2]**2 / mu_five

    # Calculate d2e_dDa2.
    d2e_dDa2 = -1.0 / 3.0 * (d2e1_dDa2 * data.c_alpha - d2e2_dDa2 * data.c_beta - d2e2_dDa2 * data.c_gamma)

    # Weight c0.
    data.d2ci[1, 1, 2] = -0.25 * d2e_dDa2

    # Weight c2.
    data.d2ci[1, 1, 4] = 0.25 * d2e_dDa2


    # Da-Dr partial derivative.
    ###########################

    # Components.
    if data.mu == 0.0:
        d2e1_dDa_dDr = 0.0
        d2e2_dDa_dDr = 0.0
        d2e3_dDa_dDr = 0.0
    else:
        d2e1_dDa_dDr = (9.0 * diff_data.params[1]**3 + 6.0 * diff_data.params[1]**2 * diff_data.params[2] - 6.0 * diff_data.params[1] * diff_data.params[2]**2 - diff_data.params[2]**3) / mu_five
        d2e2_dDa_dDr = (9.0 * diff_data.params[1]**3 - 6.0 * diff_data.params[1]**2 * diff_data.params[2] - 6.0 * diff_data.params[1] * diff_data.params[2]**2 + diff_data.params[2]**3) / mu_five
        d2e3_dDa_dDr = 2.0 * (diff_data.params[1]**2 - diff_data.params[2]**2) * diff_data.params[2] / mu_five

    # Calculate d2e_dDa2.
    d2e_dDa_dDr = 1.0 / 9.0 * (d2e1_dDa_dDr * data.c_alpha - d2e2_dDa_dDr * data.c_beta - d2e2_dDa_dDr * data.c_gamma)

    # Weight c0.
    data.d2ci[1, 2, 2] = data.d2ci[2, 1, 2] = -0.25 * d2e_dDa_dDr

    # Weight c2.
    data.d2ci[1, 2, 4] = data.d2ci[2, 1, 4] = 0.25 * d2e_dDa_dDr


    # Dr-Dr partial derivative.
    ###########################

    # Components.
    if data.mu == 0.0:
        d2e1_dDr2 = 0.0
        d2e2_dDr2 = 0.0
        d2e3_dDr2 = 0.0
    else:
        d2e1_dDr2 = (3.0 * diff_data.params[1]**2 - 9.0 * diff_data.params[1] * diff_data.params[2] - 2.0 * diff_data.params[2]**2) * diff_data.params[1] / mu_five
        d2e2_dDr2 = (3.0 * diff_data.params[1]**2 + 9.0 * diff_data.params[1] * diff_data.params[2] - 2.0 * diff_data.params[2]**2) * diff_data.params[1] / mu_five
        d2e3_dDr2 = 2.0 * (3.0 * diff_data.params[1]**2 - 2.0 * diff_data.params[2]**2) * diff_data.params[1] / mu_five

    # Calculate d2e_dDr2.
    d2e_dDr2 = -1.0 / 9.0 * (d2e1_dDr2 * data.c_alpha - d2e2_dDr2 * data.c_beta - d2e2_dDr2 * data.c_gamma)

    # Weight c0.
    data.d2ci[2, 2, 2] = -0.25 * d2e_dDr2

    # Weight c2.
    data.d2ci[2, 2, 4] = 0.25 * d2e_dDr2
