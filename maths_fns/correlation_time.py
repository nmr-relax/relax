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


##########
# Sphere #
##########



# Sphere correlation time.
#########################

def calc_sphere_ti(data, diff_data):
    """Diffusional correlation times.

    The correlation time is::
    
        t0 = tm.
    """

    data.ti[0] = diff_data.params[0]



# Sphere correlation time gradient.
###################################

def calc_sphere_dti(data, diff_data):
    """Partial derivatives of the diffusional correlation times.

    The tm partial derivatives are::

        dt0
        ---  =  1.
        dtm
    """

    data.dti[0] = 1.0




############
# Spheroid #
############



# Spheroid correlation times.
#############################

def calc_spheroid_ti(data, diff_data):
    """Diffusional correlation times.

    The equations for the parameters {Diso, Da} are::

        t-1  =  (6Diso - 2Da)**-1,

        t0   =  (6Diso - Da)**-1,

        t1   =  (6Diso + 2Da)**-1,

    The diffusion parameter set in data.diff_params is {tm, Da, theta, phi}.
    """

    # Calculate the inverse of tm.
    if diff_data.params[0] == 0.0:
        data.inv_tm = 1e99
    else:
        data.inv_tm = 1.0 / diff_data.params[0]

    # Scaling factors.
    data.tau_scale[0] = -2.0
    data.tau_scale[1] = -1.0
    data.tau_scale[2] = 2.0

    # Components.
    data.tau_comps = data.inv_tm + data.tau_scale * diff_data.params[1]

    # t-1 component.
    if data.tau_comps[0] == 0.0:
        data.tau_comps[0] = 1e99
    else:
        data.tau_comps[0] = 1.0 / data.tau_comps[0]

    # t0 component.
    if data.tau_comps[1] == 0.0:
        data.tau_comps[1] = 1e99
    else:
        data.tau_comps[1] = 1.0 / data.tau_comps[1]

    # t1 component.
    if data.tau_comps[2] == 0.0:
        data.tau_comps[2] = 1e99
    else:
        data.tau_comps[2] = 1.0 / data.tau_comps[2]

    # Correlation times.
    data.ti = 1.0 * data.tau_comps



# Spheroid correlation time gradient.
#####################################

def calc_spheroid_dti(data, diff_data):
    """Diffusional correlation time gradients.

    tm partial derivatives
    ======================

    The equations are::

        dt-1        dDiso
        ----  =  -6 ----- (6Diso - 2Da)**-2,
        dtm          dtm

        dt0         dDiso
        ---   =  -6 ----- (6Diso - Da)**-2,
        dtm          dtm

        dt1         dDiso
        ---   =  -6 ----- (6Diso + 2Da)**-2.
        dtm          dtm


    As::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

        dt-1
        ----  =  tm**-2 (6Diso - 2Da)**-2,
        dtm

        dt0
        ---   =  tm**-2 (6Diso - Da)**-2,
        dtm

        dt1
        ---   =  tm**-2 (6Diso + 2Da)**-2.
        dtm


    Da partial derivatives
    ======================

    The equations are::

        dt-1
        ----  =  2(6Diso - 2Da)**-2,
        dDa

        dt0
        ---   =  (6Diso - Da)**-2,
        dDa

        dt1
        ---   =  -2(6Diso + 2Da)**-2.
        dDa


    The diffusion parameter set in data.diff_params is {tm, Da, theta, phi}.
    """

    # Components.
    data.tau_comps_sqrd = data.tau_comps**2
    data.inv_tm_sqrd = data.inv_tm**2


    # tm partial derivative.
    ########################

    data.dti[0] = data.inv_tm_sqrd * data.tau_comps_sqrd


    # Da partial derivative.
    ########################

    # Scaling factors.
    data.tau_scale[0] = 2.0
    data.tau_scale[1] = 1.0
    data.tau_scale[2] = -2.0

    data.dti[1] = data.tau_scale * data.tau_comps_sqrd



# Spheroid correlation time Hessian.
####################################

def calc_spheroid_d2ti(data, diff_data):
    """Diffusional correlation time Hessians.

    tm-tm partial derivatives
    =========================

    The equations are::

        d2t-1        / dDiso \ 2                         d2Diso
        -----  =  72 | ----- |   (6Diso - 2Da)**-3  -  6 ------ (6Diso - 2Da)**-2,
        dtm2         \  dtm  /                            dtm2

        d2t0         / dDiso \ 2                        d2Diso
        ----   =  72 | ----- |   (6Diso - Da)**-3  -  6 ------ (6Diso - Da)**-2,
        dtm2         \  dtm  /                           dtm2

        d2t1         / dDiso \ 2                         d2Diso
        ----   =  72 | ----- |   (6Diso + 2Da)**-3  -  6 ------ (6Diso + 2Da)**-2.
        dtm2         \  dtm  /                            dtm2


    As::

        d2Diso
        ------  =  1/3 * tm**-3,
         dtm2

    and::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

        d2t-1
        -----  =  2tm**-4 (6Diso - 2Da)**-3  -  2tm**-3 (6Diso - 2Da)**-2,
        dtm2

        d2t0
        ----   =  2tm**-4 (6Diso - Da)**-3  -  2tm**-3 (6Diso - Da)**-2,
        dtm2

        d2t1
        ----   =  2tm**-4 (6Diso + 2Da)**-3  -  2tm**-3 (6Diso + 2Da)**-2.
        dtm2


    tm-Da partial derivatives
    =========================

    The equations are::

         d2t-1          dDiso
        -------  =  -24 ----- (6Diso - 2Da)**-3,
        dtm.dDa          dtm

         d2t0           dDiso
        -------  =  -12 ----- (6Diso - Da)**-3,
        dtm.dDa          dtm

         d2t1          dDiso
        -------  =  24 ----- (6Diso + 2Da)**-3.
        dtm.dDa         dtm

    As::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

         d2t-1
        -------  =  4tm**-2 (6Diso - 2Da)**-3,
        dtm.dDa

         d2t0
        -------  =  2tm**-2 (6Diso - Da)**-3,
        dtm.dDa

         d2t1
        -------  =  -4tm**-2 (6Diso + 2Da)**-3.
        dtm.dDa



    Da-Da partial derivatives
    =========================

    The equations are::

        d2t-1
        -----  =  8 (6Diso - 2Da)**-3,
        dDa2

        d2t0
        ----  =  2 (6Diso - Da)**-3,
        dDa2

        d2t1
        ----  =  8 (6Diso + 2Da)**-3. 
        dDa2


    The diffusion parameter set in data.diff_params is {tm, Da, theta, phi}.
    """

    # Components.
    data.tau_comps_cubed = data.tau_comps**3


    # tm-tm partial derivative.
    ###########################

    data.d2ti[0, 0] = 2.0 * data.inv_tm**3 * (data.inv_tm * data.tau_comps_cubed  -  data.tau_comps_sqrd)


    # tm-Da partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = 4.0
    data.tau_scale[1] = 2.0
    data.tau_scale[2] = -4.0

    data.d2ti[0, 1] = data.d2ti[1, 0] = data.tau_scale * data.inv_tm_sqrd * data.tau_comps_cubed


    # Da-Da partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = 8.0
    data.tau_scale[1] = 2.0
    data.tau_scale[2] = 8.0

    data.d2ti[1, 1] = data.tau_scale * data.tau_comps_cubed




#############
# Ellipsoid #
#############



# Ellipsoid correlation times.
##############################

def calc_ellipsoid_ti(data, diff_data):
    """Diffusional correlation times.

    The equations for the parameters {Diso, Da, Dr} are::

        t-2  =  (6Diso - 2DaR)**-1,

        t-1  =  (6Diso - Da(1 + 3Dr))**-1,

        t0   =  (6Diso - Da(1 - 3Dr))**-1,

        t1   =  (6Diso + 2Da)**-1,

        t2   =  (6Diso + 2DaR)**-1,

    where::
              __________
        R = \/1 + 3Dr**2.

    The diffusion parameter set in data.diff_params is {tm, Da, Dr, alpha, beta, gamma}.
    """

    # Calculate the inverse of tm.
    if diff_data.params[0] == 0.0:
        data.inv_tm = 1e99
    else:
        data.inv_tm = 1.0 / diff_data.params[0]

    # Calculate R.
    data.R = sqrt(1.0 + 3.0*diff_data.params[2]**2)

    # Factors.
    data.one_3Dr = 1.0 + 3.0 * diff_data.params[2]
    data.one_m3Dr = 1.0 - 3.0 * diff_data.params[2]

    # Scaling factors.
    data.tau_scale[0] = -2.0 * data.R
    data.tau_scale[1] = -data.one_3Dr
    data.tau_scale[2] = -data.one_m3Dr
    data.tau_scale[3] = 2.0
    data.tau_scale[4] = 2.0 * data.R

    # Components.
    data.tau_comps = data.inv_tm + data.tau_scale * diff_data.params[1]

    # t-2 component.
    if data.tau_comps[0] == 0.0:
        data.tau_comps[0] = 1e99
    else:
        data.tau_comps[0] = 1.0 / data.tau_comps[0]

    # t-1 component.
    if data.tau_comps[1] == 0.0:
        data.tau_comps[1] = 1e99
    else:
        data.tau_comps[1] = 1.0 / data.tau_comps[1]

    # t0 component.
    if data.tau_comps[2] == 0.0:
        data.tau_comps[2] = 1e99
    else:
        data.tau_comps[2] = 1.0 / data.tau_comps[2]

    # t1 component.
    if data.tau_comps[3] == 0.0:
        data.tau_comps[3] = 1e99
    else:
        data.tau_comps[3] = 1.0 / data.tau_comps[3]

    # t2 component.
    if data.tau_comps[4] == 0.0:
        data.tau_comps[4] = 1e99
    else:
        data.tau_comps[4] = 1.0 / data.tau_comps[4]

    # Correlation times.
    data.ti = 1.0 * data.tau_comps



# Ellipsoid correlation time gradient.
######################################

def calc_ellipsoid_dti(data, diff_data):
    """Diffusional correlation time gradients.

    tm partial derivatives
    ======================

    The equations are::

        dt-2         dDiso
        ----  =  - 6 ----- (6Diso - 2DaR)**-2,
        dtm           dtm

        dt-1         dDiso
        ----  =  - 6 ----- (6Diso - Da(1 + 3Dr))**-2,
        dtm           dtm

        dt0          dDiso
        ---   =  - 6 ----- (6Diso - Da(1 - 3Dr))**-2,
        dtm           dtm

        dt1          dDiso
        ---   =  - 6 ----- (6Diso + 2Da)**-2,
        dtm           dtm

        dt2          dDiso
        ---   =  - 6 ----- (6Diso + 2DaR)**-2.
        dtm           dtm


    As::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

        dt-2
        ----  =  tm**-2 (6Diso - 2DaR)**-2,
        dtm

        dt-1
        ----  =  tm**-2 (6Diso - Da(1 + 3Dr))**-2,
        dtm

        dt0
        ---   =  tm**-2 (6Diso - Da(1 - 3Dr))**-2,
        dtm

        dt1
        ---   =  tm**-2 (6Diso + 2Da)**-2,
        dtm

        dt2
        ---   =  tm**-2 (6Diso + 2DaR)**-2.
        dtm


    Da partial derivatives
    ======================

    The equations are::

        dt-2
        ----  =  2R (6Diso - 2DaR)**-2,
        dDa

        dt-1
        ----  =  (1 + 3Dr) (6Diso - Da(1 + 3Dr))**-2,
        dDa

        dt0
        ---   =  (1 - 3Dr) (6Diso - Da(1 - 3Dr))**-2,
        dDa

        dt1
        ---   =  -2 (6Diso + 2Da)**-2,
        dDa

        dt2
        ---   =  -2R (6Diso + 2DaR)**-2.
        dDa


    Dr partial derivatives
    ======================

    The equations are::

        dt-2
        ----  =  6 Da.Dr/R (6Diso - 2DaR)**-2,
        dDr

        dt-1
        ----  =  3Da (6Diso - Da(1 + 3Dr))**-2,
        dDr

        dt0
        ---   =  -3Da (6Diso - Da(1 - 3Dr))**-2,
        dDr

        dt1
        ---   =  0,
        dDr

        dt2
        ---   =  -6 Da.Dr/R (6Diso + 2DaR)**-2.
        dDr

    The diffusion parameter set in data.diff_params is {tm, Da, Dr, alpha, beta, gamma}.
    """

    # Components.
    data.tau_comps_sqrd = data.tau_comps**2
    data.inv_tm_sqrd = data.inv_tm**2
    data.sixDaDrR = 6.0 * diff_data.params[1] * diff_data.params[2] / data.R


    # tm partial derivative.
    ########################

    data.dti[0] = data.inv_tm_sqrd * data.tau_comps_sqrd


    # Da partial derivative.
    ########################

    # Scaling factors.
    data.tau_scale[0] = 2.0 * data.R
    data.tau_scale[1] = data.one_3Dr
    data.tau_scale[2] = data.one_m3Dr
    data.tau_scale[3] = -2.0
    data.tau_scale[4] = -2.0 * data.R

    data.dti[1] = data.tau_scale * data.tau_comps_sqrd


    # Dr partial derivative.
    ########################

    # Scaling factors.
    data.tau_scale[0] = data.sixDaDrR
    data.tau_scale[1] = 3.0 * diff_data.params[1]
    data.tau_scale[2] = -3.0 * diff_data.params[1]
    data.tau_scale[3] = 0.0
    data.tau_scale[4] = -data.sixDaDrR

    data.dti[2] = data.tau_scale * data.tau_comps_sqrd



# Ellipsoid correlation time Hessians.
######################################

def calc_ellipsoid_d2ti(data, diff_data):
    """Diffusional correlation time Hessians.

    tm-tm partial derivatives
    =========================

    The equations are::

        d2t-2        / dDiso \ 2                          d2Diso
        -----  =  72 | ----- |   (6Diso - 2DaR)**-3  -  6 ------ (6Diso - 2DaR)**-2,
        dtm2         \  dtm  /                             dtm2

        d2t-1        / dDiso \ 2                                 d2Diso
        -----  =  72 | ----- |   (6Diso - Da(1 + 3Dr))**-3  -  6 ------ (6Diso - Da(1 + 3Dr))**-2,
        dtm2         \  dtm  /                                    dtm2

        d2t0         / dDiso \ 2                                 d2Diso
        ----   =  72 | ----- |   (6Diso - Da(1 - 3Dr))**-3  -  6 ------ (6Diso - Da(1 - 3Dr))**-2,
        dtm2         \  dtm  /                                    dtm2

        d2t1         / dDiso \ 2                         d2Diso
        ----   =  72 | ----- |   (6Diso + 2Da)**-3  -  6 ------ (6Diso + 2Da)**-2,
        dtm2         \  dtm  /                            dtm2

        d2t2         / dDiso \ 2                          d2Diso
        ----   =  72 | ----- |   (6Diso + 2DaR)**-3  -  6 ------ (6Diso + 2DaR)**-2.
        dtm2         \  dtm  /                             dtm2

    As::

        d2Diso
        ------  =  1/3 * tm**-3,
         dtm2

    and::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

        d2t-2
        -----  =  2tm**-4 (6Diso - 2DaR)**-3  -  2tm**-3 (6Diso - 2DaR)**-2,
        dtm2

        d2t-1
        -----  =  2tm**-4 (6Diso - Da(1 + 3Dr))**-3  -  2tm**-3 (6Diso - Da(1 + 3Dr))**-2,
        dtm2

        d2t0
        ----   =  2tm**-4 (6Diso - Da(1 - 3Dr))**-3  -  2tm**-3 (6Diso - Da(1 - 3Dr))**-2,
        dtm2

        d2t1
        ----   =  2tm**-4 (6Diso + 2Da)**-3  -  2tm**-3 (6Diso + 2Da)**-2,
        dtm2

        d2t2
        ----   =  2tm**-4 (6Diso + 2DaR)**-3  -  2tm**-3 (6Diso + 2DaR)**-2.
        dtm2



    tm-Da partial derivatives
    =========================

    The equations are::

         d2t-2           dDiso
        -------  =  -24R ----- (6Diso - 2DaR)**-3,
        dtm.dDa           dtm

         d2t-1                    dDiso
        -------  =  -12(1 + 3Dr) ----- (6Diso - Da(1 + 3Dr))**-3,
        dtm.dDa                    dtm

         d2t0                     dDiso
        -------  =  -12(1 - 3Dr) ----- (6Diso - Da(1 - 3Dr))**-3,
        dtm.dDa                    dtm

         d2t1          dDiso
        -------  =  24 ----- (6Diso + 2Da)**-3,
        dtm.dDa         dtm

         d2t2           dDiso
        -------  =  24R ----- (6Diso + 2DaR)**-3.
        dtm.dDa          dtm

    As::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

         d2t-2
        -------  =  4R tm**-2 (6Diso - 2DaR)**-3,
        dtm.dDa

         d2t-1
        -------  =  2(1 + 3Dr) tm**-2 (6Diso - Da(1 + 3Dr))**-3,
        dtm.dDa

         d2t0
        -------  =  2(1 - 3Dr) tm**-2 (6Diso - Da(1 - 3Dr))**-3,
        dtm.dDa

         d2t1
        -------  =  -4 tm**-2 (6Diso + 2Da)**-3,
        dtm.dDa

         d2t2
        -------  =  -4R tm**-2 (6Diso + 2DaR)**-3.
        dtm.dDa


    tm-Dr partial derivatives
    =========================

    The equations are::

         d2t-2                  dDiso
        -------  =  -72 Da.Dr/R ----- (6Diso - 2DaR)**-3,
        dtm.dDr                  dtm
 
         d2t-1             dDiso
        -------  =  -36 Da ----- (6Diso - Da(1 + 3Dr))**-3,
        dtm.dDr             dtm

         d2t0             dDiso
        -------  =  36 Da ----- (6Diso - Da(1 - 3Dr))**-3,
        dtm.dDr            dtm

         d2t1
        -------  =  0,
        dtm.dDr

         d2t2                  dDiso
        -------  =  72 Da.Dr/R ----- (6Diso + 2DaR)**-3.
        dtm.dDr                 dtm

    As::

        dDiso
        -----  =  -1/6 * tm**-2,
         dtm

    the equations simplify to::

         d2t-2
        -------  =  12 Da.Dr/R tm**-2 (6Diso - 2DaR)**-3,
        dtm.dDr

         d2t-1
        -------  =  6 Da tm**-2 (6Diso - Da(1 + 3Dr))**-3,
        dtm.dDr

         d2t0
        -------  =  -6 Da tm**-2 (6Diso - Da(1 - 3Dr))**-3,
        dtm.dDr

         d2t1
        -------  =  0,
        dtm.dDr

         d2t2
        -------  =  -12 Da.Dr/R tm**-2 (6Diso + 2DaR)**-3.
        dtm.dDr


    Da-Da partial derivatives
    =========================

    The equations are::

        d2t-2
        -----  =  8R**2 (6Diso - 2DaR)**-3,
        dDa2

        d2t-1
        -----  =  2(1 + 3Dr)**2 (6Diso - Da(1 + 3Dr))**-3,
        dDa2

        d2t0
        ----   =  2(1 - 3Dr)**2 (6Diso - Da(1 - 3Dr))**-3,
        dDa2

        d2t1
        ----   =  8(6Diso + 2Da)**-3,
        dDa2

        d2t2
        ----   =  8R**2 (6Diso + 2DaR)**-3.
        dDa2


    Da-Dr partial derivatives
    =========================

    The equations are::

         d2t-2
        -------  =  24Da.Dr (6Diso - 2DaR)**-3  +  6Dr/R (6Diso - 2DaR)**-2,
        dDa.dDr

         d2t-1
        -------  =  6Da (1 + 3Dr)(6Diso - Da(1 + 3Dr))**-3  +  3(6Diso - Da(1 + 3Dr))**-2,
        dDa.dDr

         d2t0
        -------   =  -6Da (1 - 3Dr)(6Diso - Da(1 - 3Dr))**-3  -  3(6Diso - Da(1 - 3Dr))**-2,
        dDa.dDr

         d2t1
        -------   =  0,
        dDa.dDr

         d2t2
        -------   =  24Da.Dr (6Diso + 2DaR)**-3  -  6Dr/R (6Diso + 2DaR)**-2.
        dDa.dDr


    Dr-Dr partial derivatives
    =========================

    The equations are::

        d2t-2
        -----  =  72(Da.Dr/R)**2 (6Diso - 2DaR)**-3  +  6Da/R**3 (6Diso - 2DaR)**-2,
        dDr2

        d2t-1
        -----  =  18Da**2 (6Diso - Da(1 + 3Dr))**-3,
        dDr2

        d2t0
        ----   =  18Da**2 (6Diso - Da(1 - 3Dr))**-3,
        dDr2

        d2t1
        ----   =  0,
        dDr2

        d2t2
        ----   =  72(Da.Dr/R)**2 (6Diso + 2DaR)**-3  -  6Da/R**3 (6Diso + 2DaR)**-2.
        dDr2


    The diffusion parameter set in data.diff_params is {tm, Da, Dr, alpha, beta, gamma}.
    """

    # Components.
    data.tau_comps_cubed = data.tau_comps**3


    # tm-tm partial derivative.
    ###########################

    data.d2ti[0, 0] = 2.0 * data.inv_tm**3 * (data.inv_tm * data.tau_comps_cubed  -  data.tau_comps_sqrd)


    # tm-Da partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = 2.0 * data.R
    data.tau_scale[1] = data.one_3Dr
    data.tau_scale[2] = data.one_m3Dr
    data.tau_scale[3] = -2.0
    data.tau_scale[4] = -2.0 * data.R

    data.d2ti[0, 1] = data.d2ti[1, 0] = 2.0 * data.tau_scale * data.inv_tm_sqrd * data.tau_comps_cubed


    # tm-Dr partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = data.sixDaDrR
    data.tau_scale[1] = 3.0 * diff_data.params[1]
    data.tau_scale[2] = -3.0 * diff_data.params[1]
    data.tau_scale[3] = 0.0
    data.tau_scale[4] = -data.sixDaDrR

    data.d2ti[0, 2] = data.d2ti[2, 0] = 2.0 * data.tau_scale * data.inv_tm_sqrd * data.tau_comps_cubed


    # Da-Da partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = 2.0 * data.R
    data.tau_scale[1] = data.one_3Dr
    data.tau_scale[2] = data.one_m3Dr
    data.tau_scale[3] = 2.0
    data.tau_scale[4] = 2.0 * data.R

    data.d2ti[1, 1] = 2.0 * data.tau_scale**2 * data.tau_comps_cubed


    # Da-Dr partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = 4.0 * diff_data.params[2]
    data.tau_scale[1] = data.one_3Dr
    data.tau_scale[2] = -data.one_m3Dr
    data.tau_scale[3] = 0.0
    data.tau_scale[4] = 4.0 * diff_data.params[2]

    data.d2ti[1, 2] = 6.0 * diff_data.params[1] * data.tau_scale * data.tau_comps_cubed

    # Scaling factors.
    data.tau_scale[0] = 6.0 * diff_data.params[2] / data.R
    data.tau_scale[1] = 3.0
    data.tau_scale[2] = -3.0
    data.tau_scale[3] = 0.0
    data.tau_scale[4] = -6.0 * diff_data.params[2] / data.R

    data.d2ti[1, 2] = data.d2ti[2, 1] = data.d2ti[1, 2] + data.tau_scale * data.tau_comps_sqrd


    # Dr-Dr partial derivative.
    ###########################

    # Scaling factors.
    data.tau_scale[0] = data.sixDaDrR
    data.tau_scale[1] = 3.0 * diff_data.params[1]
    data.tau_scale[2] = 3.0 * diff_data.params[1]
    data.tau_scale[3] = 0.0
    data.tau_scale[4] = data.sixDaDrR

    data.d2ti[2, 2] = 2.0 * data.tau_scale**2 * data.tau_comps_cubed

    # Scaling factors.
    data.tau_scale[0] = 1.0
    data.tau_scale[1] = 0.0
    data.tau_scale[2] = 0.0
    data.tau_scale[3] = 0.0
    data.tau_scale[4] = -1.0

    try:
        data.R_cubed = data.R**3
    except OverflowError:
        data.R_cubed = 1e99
    data.d2ti[2, 2] = data.d2ti[2, 2] + 6.0 * diff_data.params[1] / data.R_cubed * data.tau_scale * data.tau_comps_sqrd
