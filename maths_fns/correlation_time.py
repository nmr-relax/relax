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


# Isotropic global correlation time equation.
#############################################

def calc_iso_ti(data, diff_data):
    """Diffusional correlation times for isotropic diffusion.

    t0 = tm
    """

    data.ti[0] = diff_data.params[0]



# Isotropic global correlation time gradient.
#############################################

def calc_iso_dti(data, diff_data):
    """Partial derivatives of the diffusional correlation times.

    The tm partial derivatives are:

        dt0
        ---  =  1
        dtm
    """

    data.dti[0] = 1.0



# Axially symmetric global correlation time equation.
#####################################################

def calc_axial_ti(data, diff_data):
    """Diffusional correlation times.

    The equations for the parameters {Dper, Dpar} are:

                 1
        t0  =  -----
               6Dper

                    1
        t1  =  ------------
               5Dper + Dpar

                     1
        t2  =  -------------
               2Dper + 4Dpar


    The equations for the parameters {Diso, Da} are:

        t0   =  1/6 (Diso - Da)**-1

        t1   =  1/6 (Diso - Da/2)**-1

        t2   =  1/6 (Diso + Da)**-1

    The diffusion parameter set in data.diff_params is {tm, Da, theta, phi}.
    """

    # Calculate Diso.
    if diff_data.params[0] == 0.0:
        data.Diso = 1e99
    else:
        data.Diso = 1.0 / (6.0 * diff_data.params[0])

    # Components.
    data.t_0_comp  = data.Diso - diff_data.params[1]
    data.t_1_comp  = data.Diso - 0.5 * diff_data.params[1]
    data.t_2_comp  = data.Diso + diff_data.params[1]

    # t0.
    data.ti[0] = 6.0 * data.t_0_comp
    if data.ti[0] == 0.0:
        data.ti[0] = 1e99
    else:
        data.ti[0] = 1.0 / data.ti[0]

    # t1.
    data.ti[1] = 6.0 * data.t_1_comp
    if data.ti[1] == 0.0:
        data.ti[1] = 1e99
    else:
        data.ti[1] = 1.0 / data.ti[1]

    # t2.
    data.ti[2] = 6.0 * data.t_2_comp
    if data.ti[2] == 0.0:
        data.ti[2] = 1e99
    else:
        data.ti[2] = 1.0 / data.ti[2]




# Axially symmetric global correlation time gradient.
#####################################################

def calc_axial_dti(data, diff_data):
    """Diffusional correlation time gradients.

    tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dt0        1 dDiso
        ---   =  - - ----- (Diso - Da)**-2
        dtm        6  dtm

        dt1        1 dDiso
        ---   =  - - ----- (Diso - Da/2)**-2
        dtm        6  dtm

        dt2        1 dDiso
        ---   =  - - ----- (Diso + Da)**-2
        dtm        6  dtm


        dDiso
        -----  =  -1/6 * tm**-2
         dtm


    Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dt0
        ---   =  1/6 (Diso - Da)**-2
        dDa

        dt1
        ---   =  1/12 (Diso - Da/2)**-2
        dDa

        dt2
        ---   =  -1/6 (Diso + Da)**-2
        dDa


    The diffusion parameter set in data.diff_params is {tm, Da, theta, phi}.
    """

    # Components.
    data.t_0_comp_sqrd  = data.t_0_comp**2
    data.t_1_comp_sqrd  = data.t_1_comp**2
    data.t_2_comp_sqrd  = data.t_2_comp**2


    # tm partial derivative.
    ########################

    # Components.
    data.inv_dDiso_dtm = -6.0 * diff_data.params[0]**2

    # t0.
    data.dti[0, 0] = -6.0 * data.inv_dDiso_dtm * data.t_0_comp_sqrd
    if data.dti[0, 0] == 0.0:
        data.dti[0, 0] = 1e99
    else:
        data.dti[0, 0] = 1.0 / data.dti[0, 0]

    # t1.
    data.dti[0, 1] = -6.0 * data.inv_dDiso_dtm * data.t_1_comp_sqrd
    if data.dti[0, 1] == 0.0:
        data.dti[0, 1] = 1e99
    else:
        data.dti[0, 1] = 1.0 / data.dti[0, 1]

    # t2.
    data.dti[0, 2] = -6.0 * data.inv_dDiso_dtm * data.t_2_comp_sqrd
    if data.dti[0, 2] == 0.0:
        data.dti[0, 2] = 1e99
    else:
        data.dti[0, 2] = 1.0 / data.dti[0, 2]


    # Da partial derivative.
    ########################

    # t0.
    data.dti[1, 0] = 6.0 * data.t_0_comp_sqrd
    if data.dti[1, 0] == 0.0:
        if data.mu != 0.0:
            data.dti[1, 0] = 1e99
    else:
        data.dti[1, 0] = 1.0 / data.dti[1, 0]

    # t1.
    data.dti[1, 1] = 12.0 * data.t_1_comp_sqrd
    if data.dti[1, 1] == 0.0:
        data.dti[1, 1] = 1e99
    else:
        data.dti[1, 1] = 1.0 / data.dti[1, 1]

    # t2.
    data.dti[1, 2] = -6.0 * data.t_2_comp_sqrd
    if data.dti[1, 2] == 0.0:
        if data.mu != 0.0:
            data.dti[1, 2] = 1e99
    else:
        data.dti[1, 2] = 1.0 / data.dti[1, 2]


# Axially symmetric global correlation time Hessian.
####################################################

def calc_axial_d2ti(data, diff_data):
    """Diffusional correlation time Hessians.

    tm-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2t0      1 / dDiso \ 2                     1 d2Diso
        ----   =  - | ----- |   (Diso - Da)**-3  -  - ------ (Diso - Da)**-2
        dtm2      3 \  dtm  /                       6  dtm2

        d2t1      1 / dDiso \ 2                       1 d2Diso
        ----   =  - | ----- |   (Diso - Da/2)**-3  -  - ------ (Diso - Da/2)**-2
        dtm2      3 \  dtm  /                         6  dtm2

        d2t2      1 / dDiso \ 2                     1 d2Diso
        ----   =  - | ----- |   (Diso + Da)**-3  -  - ------ (Diso + Da)**-2
        dtm2      3 \  dtm  /                       6  dtm2


        d2Diso
        ------  =  1/3 * tm**-3
         dtm2


    tm-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2t0         1 dDiso
        -------  =  - - ----- (Diso - Da)**-3
        dtm.dDa       3  dtm

         d2t1         1 dDiso
        -------  =  - - ----- (Diso - Da/2)**-3
        dtm.dDa       6  dtm

         d2t2       1 dDiso
        -------  =  - ----- (Diso + Da)**-3
        dtm.dDa     3  dtm


    Da-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2t0
        ----  =  1/3 (Diso - Da)**-3
        dDa2

        d2t1
        ----  =  1/12 (Diso - Da/2)**-3
        dDa2

        d2t2
        ----  =  1/3 (Diso + Da)**-3 
        dDa2


    The diffusion parameter set in data.diff_params is {tm, Da, theta, phi}.
    """

    # Components.
    data.t_0_comp_cubed  = data.t_0_comp**3
    data.t_1_comp_cubed  = data.t_1_comp**3
    data.t_2_comp_cubed  = data.t_2_comp**3


    # tm-tm partial derivative.
    ###########################

    # Components.
    data.inv_d2Diso_dtm2 = 3.0 * diff_data.params[0]**3

    # t0.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_0_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_0_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 0] = 1e99
    else:
        data.d2ti[0, 0, 0] = 1.0 / a + 1.0 / b

    # t1.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_1_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_1_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 1] = 1e99
    else:
        data.d2ti[0, 0, 1] = 1.0 / a + 1.0 / b

    # t2.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_2_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_2_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 2] = 1e99
    else:
        data.d2ti[0, 0, 2] = 1.0 / a + 1.0 / b


    # tm-Da partial derivative.
    ###########################

    # t0.
    a = -3.0 * data.inv_dDiso_dtm * data.t_0_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 0] = data.d2ti[1, 0, 0] = 1e99
    else:
        data.d2ti[0, 1, 0] = data.d2ti[1, 0, 0] = 1.0 / a

    # t1.
    a = -6.0 * data.inv_dDiso_dtm * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 1] = data.d2ti[1, 0, 1] = 1e99
    else:
        data.d2ti[0, 1, 1] = data.d2ti[1, 0, 1] = 1.0 / a

    # t2.
    a = 3.0 * data.inv_dDiso_dtm * data.t_2_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 2] = data.d2ti[1, 0, 2] = 1e99
    else:
        data.d2ti[0, 1, 2] = data.d2ti[1, 0, 2] = 1.0 / a


    # Da-Da partial derivative.
    ###########################

    # t0.
    a = 3.0 * data.t_0_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 0] = 1e99
    else:
        data.d2ti[1, 1, 0] = 1.0 / a

    # t1.
    a = 12.0 * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 1] = 1e99
    else:
        data.d2ti[1, 1, 1] = 1.0 / a

    # t2.
    a = 3.0 * data.t_2_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 2] = 1e99
    else:
        data.d2ti[1, 1, 2] = 1.0 / a




# Anisotropic global correlation time equation.
###############################################

def calc_aniso_ti(data, diff_data):
    """Diffusional correlation times.

    The equations for the parameters {Diso, Da, Dr} are:

        t-2  =  1/6 (Diso + Da)**-1

        t-1  =  1/6 (Diso - (Da + Dr)/2)**-1

        t0   =  1/6 (Diso - mu)**-1

        t1   =  1/6 (Diso - (Da - Dr)/2)**-1

        t2   =  1/6 (Diso + mu)**-1

    where:
               __________________
        mu = \/ Da**2 + Dr**2 / 3

    The diffusion parameter set in data.diff_params is {tm, Da, Dr, alpha, beta, gamma}.
    """

    # Calculate Diso.
    if diff_data.params[0] == 0.0:
        data.Diso = 1e99
    else:
        data.Diso = 1.0 / (6.0 * diff_data.params[0])

    # Calculate mu.
    data.mu = sqrt(diff_data.params[1]**2 + diff_data.params[2]**2 / 3.0)

    # Components.
    data.t_m2_comp = data.Diso + diff_data.params[1]
    data.t_m1_comp = data.Diso - 0.5 * (diff_data.params[1] + diff_data.params[2])
    data.t_0_comp  = data.Diso - data.mu
    data.t_1_comp  = data.Diso - 0.5 * (diff_data.params[1] - diff_data.params[2])
    data.t_2_comp  = data.Diso + data.mu

    # t-2.
    data.ti[0] = 6.0 * data.t_m2_comp
    if data.ti[0] == 0.0:
        data.ti[0] = 1e99
    else:
        data.ti[0] = 1.0 / data.ti[0]

    # t-1.
    data.ti[1] = 6.0 * data.t_m1_comp
    if data.ti[1] == 0.0:
        data.ti[1] = 1e99
    else:
        data.ti[1] = 1.0 / data.ti[1]

    # t0.
    data.ti[2] = 6.0 * data.t_0_comp
    if data.ti[2] == 0.0:
        data.ti[2] = 1e99
    else:
        data.ti[2] = 1.0 / data.ti[2]

    # t1.
    data.ti[3] = 6.0 * data.t_1_comp
    if data.ti[3] == 0.0:
        data.ti[3] = 1e99
    else:
        data.ti[3] = 1.0 / data.ti[3]

    # t2.
    data.ti[4] = 6.0 * data.t_2_comp
    if data.ti[4] == 0.0:
        data.ti[4] = 1e99
    else:
        data.ti[4] = 1.0 / data.ti[4]



# Anisotropic global correlation time gradient.
###############################################

def calc_aniso_dti(data, diff_data):
    """Diffusional correlation time gradients.

    tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dt-2       1 dDiso
        ----  =  - - ----- (Diso + Da)**-2
        dtm        6  dtm

        dt-1       1 dDiso
        ----  =  - - ----- (Diso - (Da + Dr)/2)**-2
        dtm        6  dtm

        dt0        1 dDiso
        ---   =  - - ----- (Diso - mu)**-2
        dtm        6  dtm

        dt1        1 dDiso
        ---   =  - - ----- (Diso - (Da - Dr)/2)**-2
        dtm        6  dtm

        dt2        1 dDiso
        ---   =  - - ----- (Diso + mu)**-2
        dtm        6  dtm


        dDiso
        -----  =  -1/6 * tm**-2
         dtm


    Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dt-2
        ----  =  -1/6 (Diso + Da)**-2
        dDa

        dt-1
        ----  =  1/12 (Diso - (Da + Dr)/2)**-2
        dDa

        dt0
        ---   =  1/6 Da/mu (Diso - mu)**-2
        dDa

        dt1
        ---   =  1/12 (Diso - (Da - Dr)/2)**-2
        dDa

        dt2
        ---   =  -1/6 Da/mu (Diso + mu)**-2
        dDa


    Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dt-2
        ----  =  0
        dDr

        dt-1
        ----  =  1/12 (Diso - (Da + Dr)/2)**-2
        dDr

        dt0
        ---   =  1/18 Dr/mu (Diso - mu)**-2
        dDr

        dt1
        ---   =  -1/12 (Diso - (Da - Dr)/2)**-2
        dDr

        dt2
        ---   =  -1/18 Dr/mu (Diso + mu)**-2
        dDr

    The diffusion parameter set in data.diff_params is {tm, Da, Dr, alpha, beta, gamma}.
    """

    # Components.
    data.t_m2_comp_sqrd = data.t_m2_comp**2
    data.t_m1_comp_sqrd = data.t_m1_comp**2
    data.t_0_comp_sqrd  = data.t_0_comp**2
    data.t_1_comp_sqrd  = data.t_1_comp**2
    data.t_2_comp_sqrd  = data.t_2_comp**2


    # tm partial derivative.
    ########################

    # Components.
    data.inv_dDiso_dtm = -6.0 * diff_data.params[0]**2

    # t-2.
    data.dti[0, 0] = -6.0 * data.inv_dDiso_dtm * data.t_m2_comp_sqrd
    if data.dti[0, 0] == 0.0:
        data.dti[0, 0] = 1e99
    else:
        data.dti[0, 0] = 1.0 / data.dti[0, 0]

    # t-1.
    data.dti[0, 1] = -6.0 * data.inv_dDiso_dtm * data.t_m1_comp_sqrd
    if data.dti[0, 1] == 0.0:
        data.dti[0, 1] = 1e99
    else:
        data.dti[0, 1] = 1.0 / data.dti[0, 1]

    # t0.
    data.dti[0, 2] = -6.0 * data.inv_dDiso_dtm * data.t_0_comp_sqrd
    if data.dti[0, 2] == 0.0:
        data.dti[0, 2] = 1e99
    else:
        data.dti[0, 2] = 1.0 / data.dti[0, 2]

    # t1.
    data.dti[0, 3] = -6.0 * data.inv_dDiso_dtm * data.t_1_comp_sqrd
    if data.dti[0, 3] == 0.0:
        data.dti[0, 3] = 1e99
    else:
        data.dti[0, 3] = 1.0 / data.dti[0, 3]

    # t2.
    data.dti[0, 4] = -6.0 * data.inv_dDiso_dtm * data.t_2_comp_sqrd
    if data.dti[0, 4] == 0.0:
        data.dti[0, 4] = 1e99
    else:
        data.dti[0, 4] = 1.0 / data.dti[0, 4]


    # Da partial derivative.
    ########################

    # t-2.
    data.dti[1, 0] = -6.0 * data.t_m2_comp_sqrd
    if data.dti[1, 0] == 0.0:
        data.dti[1, 0] = 1e99
    else:
        data.dti[1, 0] = 1.0 / data.dti[1, 0]

    # t-1.
    data.dti[1, 1] = 12.0 * data.t_m1_comp_sqrd
    if data.dti[1, 1] == 0.0:
        data.dti[1, 1] = 1e99
    else:
        data.dti[1, 1] = 1.0 / data.dti[1, 1]

    # t0.
    data.dti[1, 2] = 6.0 * data.mu * data.t_0_comp_sqrd
    if data.dti[1, 2] == 0.0:
        if data.mu != 0.0:
            data.dti[1, 2] = 1e99
    else:
        data.dti[1, 2] = diff_data.params[1] / data.dti[1, 2]

    # t1.
    data.dti[1, 3] = 12.0 * data.t_1_comp_sqrd
    if data.dti[1, 3] == 0.0:
        data.dti[1, 3] = 1e99
    else:
        data.dti[1, 3] = 1.0 / data.dti[1, 3]

    # t2.
    data.dti[1, 4] = -6.0 * data.mu * data.t_2_comp_sqrd
    if data.dti[1, 4] == 0.0:
        if data.mu != 0.0:
            data.dti[1, 4] = 1e99
    else:
        data.dti[1, 4] = diff_data.params[1] / data.dti[1, 4]


    # Dr partial derivative.
    ########################

    # t-1.
    data.dti[2, 1] = 12.0 * data.t_m1_comp_sqrd
    if data.dti[2, 1] == 0.0:
        data.dti[2, 1] = 1e99
    else:
        data.dti[2, 1] = 1.0 / data.dti[2, 1]

    # t0.
    data.dti[2, 2] = 18.0 * data.mu * data.t_0_comp_sqrd
    if data.dti[2, 2] == 0.0:
        if data.mu != 0.0:
            data.dti[2, 2] = 1e99
    else:
        data.dti[2, 2] = diff_data.params[2] / data.dti[2, 2]

    # t1.
    data.dti[2, 3] = -12.0 * data.t_1_comp_sqrd
    if data.dti[2, 3] == 0.0:
        data.dti[2, 3] = 1e99
    else:
        data.dti[2, 3] = 1.0 / data.dti[2, 3]

    # t2.
    data.dti[2, 4] = -18.0 * data.mu * data.t_2_comp_sqrd
    if data.dti[2, 4] == 0.0:
        if data.mu != 0.0:
            data.dti[2, 4] = 1e99
    else:
        data.dti[2, 4] = diff_data.params[2] / data.dti[2, 4]



# Anisotropic global correlation time Hessians.
###############################################

def calc_aniso_d2ti(data, diff_data):
    """Diffusional correlation time Hessians.

    tm-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2t-2     1 / dDiso \ 2                     1 d2Diso
        -----  =  - | ----- |   (Diso + Da)**-3  -  - ------ (Diso + Da)**-2
        dtm2      3 \  dtm  /                       6  dtm2

        d2t-1     1 / dDiso \ 2                              1 d2Diso
        -----  =  - | ----- |   (Diso - (Da + Dr)/2)**-3  -  - ------ (Diso - (Da + Dr)/2)**-2
        dtm2      3 \  dtm  /                                6  dtm2

        d2t0      1 / dDiso \ 2                     1 d2Diso
        ----   =  - | ----- |   (Diso - mu)**-3  -  - ------ (Diso - mu)**-2
        dtm2      3 \  dtm  /                       6  dtm2

        d2t1      1 / dDiso \ 2                              1 d2Diso
        ----   =  - | ----- |   (Diso - (Da - Dr)/2)**-3  -  - ------ (Diso - (Da - Dr)/2)**-2
        dtm2      3 \  dtm  /                                6  dtm2

        d2t2      1 / dDiso \ 2                     1 d2Diso
        ----   =  - | ----- |   (Diso + mu)**-3  -  - ------ (Diso + mu)**-2
        dtm2      3 \  dtm  /                       6  dtm2


        d2Diso
        ------  =  1/3 * tm**-3
         dtm2


    tm-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2t-2      1 dDiso
        -------  =  - ----- (Diso + Da)**-3
        dtm.dDa     3  dtm

         d2t-1        1 dDiso
        -------  =  - - ----- (Diso - (Da + Dr)/2)**-3
        dtm.dDa       6  dtm

         d2t0         1 dDiso Da
        -------  =  - - ----- -- (Diso - mu)**-3
        dtm.dDa       3  dtm  mu

         d2t1         1 dDiso
        -------  =  - - ----- (Diso - (Da - Dr)/2)**-3
        dtm.dDa       6  dtm

         d2t2       1 dDiso Da
        -------  =  - ----- -- (Diso + mu)**-3
        dtm.dDa     3  dtm  mu


    tm-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2t-2
        -------  =  0
        dtm.dDr

         d2t-1        1 dDiso
        -------  =  - - ----- (Diso - (Da + Dr)/2)**-3
        dtm.dDr       6  dtm

         d2t0         1 dDiso Dr
        -------  =  - - ----- -- (Diso - mu)**-3
        dtm.dDr       9  dtm  mu

         d2t1       1 dDiso
        -------  =  - ----- (Diso - (Da - Dr)/2)**-3
        dtm.dDr     6  dtm

         d2t2       1 dDiso Dr
        -------  =  - ----- -- (Diso + mu)**-3
        dtm.dDr     9  dtm  mu


    Da-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2t-2
        -----  =  1/3 (Diso + Da)**-3
        dDa2

        d2t-1
        -----  =  1/12 (Diso - (Da + Dr)/2)**-3
        dDa2

        d2t0      1 Da**2                      1  / Da**2     \ 
        ----   =  - ----- (Diso - mu)**-3  -  --- | ----- - 1 | (Diso - mu)**-2
        dDa2      3 mu**2                     6mu \ mu**2     /

        d2t1
        ----   =  1/12 (Diso - (Da - Dr)/2)**-3
        dDa2

        d2t2      1 Da**2                      1  / Da**2     \ 
        ----   =  - ----- (Diso + mu)**-3  +  --- | ----- - 1 | (Diso + mu)**-2
        dDa2      3 mu**2                     6mu \ mu**2     /


    Da-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2t-2
        -------  =  0
        dDa.dDr

         d2t-1
        -------  =  1/12 (Diso - (Da + Dr)/2)**-3
        dDa.dDr

         d2t0        1 Da.Dr                     1  Da.Dr
        -------   =  - ----- (Diso - mu)**-3  -  -- ----- (Diso - mu)**-2
        dDa.dDr      9 mu**2                     18 mu**3

         d2t1
        -------   =  -1/12 (Diso - (Da - Dr)/2)**-3
        dDa.dDr

         d2t2        1 Da.Dr                     1  Da.Dr
        -------   =  - ----- (Diso + mu)**-3  +  -- ----- (Diso + mu)**-2
        dDa.dDr      9 mu**2                     18 mu**3


    Dr-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2t-2
        -----  =  0
        dDr2

        d2t-1
        -----  =  1/12 (Diso - (Da + Dr)/2)**-3
        dDr2

        d2t0      1  Dr**2                      1   / Dr**2      \ 
        ----   =  -- ----- (Diso - mu)**-3  -  ---- | ------ - 1 | (Diso - mu)**-2
        dDr2      27 mu**2                     18mu \ 3mu**2     /

        d2t1
        ----   =  1/12 (Diso - (Da - Dr)/2)**-3
        dDr2

        d2t2      1  Dr**2                      1   / Dr**2      \ 
        ----   =  -- ----- (Diso + mu)**-3  +  ---- | ------ - 1 | (Diso + mu)**-2
        dDr2      27 mu**2                     18mu \ 3mu**2     /


    The diffusion parameter set in data.diff_params is {tm, Da, Dr, alpha, beta, gamma}.
    """

    # Components.
    data.t_m2_comp_cubed = data.t_m2_comp**3
    data.t_m1_comp_cubed = data.t_m1_comp**3
    data.t_0_comp_cubed  = data.t_0_comp**3
    data.t_1_comp_cubed  = data.t_1_comp**3
    data.t_2_comp_cubed  = data.t_2_comp**3


    # tm-tm partial derivative.
    ###########################

    # Components.
    data.inv_d2Diso_dtm2 = 3.0 * diff_data.params[0]**3

    # t-2.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_m2_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_m2_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 0] = 1e99
    else:
        data.d2ti[0, 0, 0] = 1.0 / a + 1.0 / b

    # t-1.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_m1_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_m1_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 1] = 1e99
    else:
        data.d2ti[0, 0, 1] = 1.0 / a + 1.0 / b

    # t0.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_0_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_0_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 2] = 1e99
    else:
        data.d2ti[0, 0, 2] = 1.0 / a + 1.0 / b

    # t1.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_1_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_1_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 3] = 1e99
    else:
        data.d2ti[0, 0, 3] = 1.0 / a + 1.0 / b

    # t2.
    a = 3.0 * data.inv_dDiso_dtm**2 * data.t_2_comp_cubed
    b = -6.0 * data.inv_d2Diso_dtm2 * data.t_2_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[0, 0, 4] = 1e99
    else:
        data.d2ti[0, 0, 4] = 1.0 / a + 1.0 / b


    # tm-Da partial derivative.
    ###########################

    # t-2.
    a = 3.0 * data.inv_dDiso_dtm * data.t_m2_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 0] = data.d2ti[1, 0, 0] = 1e99
    else:
        data.d2ti[0, 1, 0] = data.d2ti[1, 0, 0] = 1.0 / a

    # t-1.
    a = -6.0 * data.inv_dDiso_dtm * data.t_m1_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 1] = data.d2ti[1, 0, 1] = 1e99
    else:
        data.d2ti[0, 1, 1] = data.d2ti[1, 0, 1] = 1.0 / a

    # t0.
    a = -3.0 * data.inv_dDiso_dtm * data.mu * data.t_0_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 2] = data.d2ti[1, 0, 2] = 1e99
    else:
        data.d2ti[0, 1, 2] = data.d2ti[1, 0, 2] = diff_data.params[1] / a

    # t1.
    a = -6.0 * data.inv_dDiso_dtm * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 3] = data.d2ti[1, 0, 3] = 1e99
    else:
        data.d2ti[0, 1, 3] = data.d2ti[1, 0, 3] = 1.0 / a

    # t2.
    a = 3.0 * data.inv_dDiso_dtm * data.mu * data.t_2_comp_cubed
    if a == 0.0:
        data.d2ti[0, 1, 4] = data.d2ti[1, 0, 4] = 1e99
    else:
        data.d2ti[0, 1, 4] = data.d2ti[1, 0, 4] = diff_data.params[1] / a


    # tm-Dr partial derivative.
    ###########################

    # t-1.
    a = -6.0 * data.inv_dDiso_dtm * data.t_m1_comp_cubed
    if a == 0.0:
        data.d2ti[0, 2, 1] = data.d2ti[2, 0, 1] = 1e99
    else:
        data.d2ti[0, 2, 1] = data.d2ti[2, 0, 1] = 1.0 / a

    # t0.
    a = -9.0 * data.inv_dDiso_dtm * data.mu * data.t_0_comp_cubed
    if a == 0.0:
        data.d2ti[0, 2, 2] = data.d2ti[2, 0, 2] = 1e99
    else:
        data.d2ti[0, 2, 2] = data.d2ti[2, 0, 2] = diff_data.params[2] / a

    # t1.
    a = 6.0 * data.inv_dDiso_dtm * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[0, 2, 3] = data.d2ti[2, 0, 3] = 1e99
    else:
        data.d2ti[0, 2, 3] = data.d2ti[2, 0, 3] = 1.0 / a

    # t2.
    a = 9.0 * data.inv_dDiso_dtm * data.mu * data.t_2_comp_cubed
    if a == 0.0:
        data.d2ti[0, 2, 4] = data.d2ti[2, 0, 4] = 1e99
    else:
        data.d2ti[0, 2, 4] = data.d2ti[2, 0, 4] = diff_data.params[2] / a


    # Da-Da partial derivative.
    ###########################

    # t-2.
    a = 3.0 * data.t_m2_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 0] = 1e99
    else:
        data.d2ti[1, 1, 0] = 1.0 / a

    # t-1.
    a = 12.0 * data.t_m1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 1] = 1e99
    else:
        data.d2ti[1, 1, 1] = 1.0 / a

    # t0.
    a = 3.0 * data.mu**2 * data.t_0_comp_cubed
    b = -6.0 * data.mu * data.t_0_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[1, 1, 2] = 1e99
    else:
        data.d2ti[1, 1, 2] = diff_data.params[1]**2 / a  +  (diff_data.params[1]**2 / data.mu**2 - 1.0) / b

    # t1.
    a = 12.0 * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 3] = 1e99
    else:
        data.d2ti[1, 1, 3] = 1.0 / a

    # t2.
    a = 3.0 * data.mu**2 * data.t_2_comp_cubed
    b = 6.0 * data.mu * data.t_2_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[1, 1, 4] = 1e99
    else:
        data.d2ti[1, 1, 4] = diff_data.params[1]**2 / a  +  (diff_data.params[1]**2 / data.mu**2 - 1.0) / b


    # Da-Dr partial derivative.
    ###########################

    # t-1.
    a = 12.0 * data.t_m1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 2, 1] = data.d2ti[2, 1, 1] = 1e99
    else:
        data.d2ti[1, 2, 1] = data.d2ti[2, 1, 1] = 1.0 / a

    # t0.
    a = 9.0 * data.mu**2 * data.t_0_comp_cubed
    b = -18.0 * data.mu**3 * data.t_0_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[1, 2, 2] = data.d2ti[2, 1, 2] = 1e99
    else:
        data.d2ti[1, 2, 2] = data.d2ti[2, 1, 2] = diff_data.params[1] * diff_data.params[2] / a  +  diff_data.params[1] * diff_data.params[2] / b

    # t1.
    a = -12.0 * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 2, 3] = data.d2ti[2, 1, 3] = 1e99
    else:
        data.d2ti[1, 2, 3] = data.d2ti[2, 1, 3] = 1.0 / a

    # t2.
    a = 9.0 * data.mu**2 * data.t_2_comp_cubed
    b = 18.0 * data.mu**3 * data.t_2_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[1, 2, 4] = data.d2ti[2, 1, 4] = 1e99
    else:
        data.d2ti[1, 2, 4] = data.d2ti[2, 1, 4] = diff_data.params[1] * diff_data.params[2] / a  +  diff_data.params[1] * diff_data.params[2] / b


    # Dr-Dr partial derivative.
    ###########################

    # t-1.
    a = 12.0 * data.t_m1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 1] = 1e99
    else:
        data.d2ti[1, 1, 1] = 1.0 / a

    # t0.
    a = 27.0 * data.mu**2 * data.t_0_comp_cubed
    b = -18.0 * data.mu * data.t_0_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[1, 1, 2] = 1e99
    else:
        data.d2ti[1, 1, 2] = diff_data.params[2]**2 / a  +  (diff_data.params[2]**2 / (3.0 * data.mu**2) - 1.0) / b

    # t1.
    a = 12.0 * data.t_1_comp_cubed
    if a == 0.0:
        data.d2ti[1, 1, 3] = 1e99
    else:
        data.d2ti[1, 1, 3] = 1.0 / a

    # t2.
    a = 27.0 * data.mu**2 * data.t_2_comp_cubed
    b = 18.0 * data.mu * data.t_2_comp_sqrd
    if a == 0.0 or b == 0.0:
        data.d2ti[1, 1, 4] = 1e99
    else:
        data.d2ti[1, 1, 4] = diff_data.params[2]**2 / a  +  (diff_data.params[2]**2 / (3.0 * data.mu**2) - 1.0) / b
