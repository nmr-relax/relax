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


    The equations for the parameters {tm, Dratio} are:

               1    /       1    \ 
        t0  =  - tm | 2 + ------ |
               3    \     Dratio /


               2    /          3      \ 
        t1  =  - tm | 2 + ----------- |
               5    \     1 + 5Dratio /


                  /         3      \ 
        t2  =  tm | 2 - ---------- |
                  \     2 + Dratio /

    The diffusion parameter set in data.diff_params is {tm, Dratio, theta, phi}.
    """

    # t0.
    if diff_data.params[1] == 0:
        if diff_data.params[0] == 0:
            data.ti[0] = 0.0
        else:
            data.ti[0] = 1e99
    else:
        data.ti[0] = diff_data.params[0]/3.0 * (2.0 + 1.0/diff_data.params[1])

    # t1.
    data.ti[1] = 0.4 * diff_data.params[0] * (2.0 + 3.0/(1.0 + 5.0*diff_data.params[1]))

    # t2.
    data.ti[2] = diff_data.params[0] * (2.0 - 3.0/(2.0 + diff_data.params[1]))




# Axially symmetric global correlation time gradient.
#####################################################

def calc_axial_dti(data, diff_data):
    """Partial derivatives of the diffusional correlation times.

    The tm partial derivatives are:

        dt0     1 /       1    \ 
        ---  =  - | 2 + ------ |
        dtm     3 \     Dratio /


        dt1     2 /          3      \ 
        ---  =  - | 2 + ----------- |
        dtm     5 \     1 + 5Dratio /


        dt2             3
        ---  =  2 - ----------
        dtm         2 + Dratio


    The Dratio partial derivatives are:

          dt0             tm
        -------  =  - ----------
        dDratio       3Dratio**2

          dt1               6tm
        -------  =  - ----------------
        dDratio       (1 + 5Dratio)**2

          dt2             3tm
        -------  =  ---------------
        dDratio     (2 + Dratio)**2


    The diffusion parameter set in data.diff_params is {tm, Dratio, theta, phi}.
    """

    # tm partial derivatives.
    if diff_data.params[1] == 0:
        data.dti[0, 0] = 1e99
    else:
        data.dti[0, 0] = (2.0 + 1.0/diff_data.params[1]) / 3.0
    data.dti[0, 1] = 0.4 * (2.0 + 3.0/(1.0 + 5.0*diff_data.params[1]))
    data.dti[0, 2] = 2.0 - 3.0/(2.0 + diff_data.params[1])

    # Dratio partial derivatives.
    if diff_data.params[1] == 0:
        if diff_data.params[0] == 0:
            data.dti[1, 0] = 0.0
        else:
            data.dti[1, 0] = -1e99
    else:
        data.dti[1, 0] = - diff_data.params[0] / (3.0 * diff_data.params[1]**2)
    data.dti[1, 1] = - 6.0 * diff_data.params[0] / (1.0 + 5.0*diff_data.params[1])**2
    data.dti[1, 2] = 3.0 * diff_data.params[0] / (2.0 + diff_data.params[1])**2



# Axially symmetric global correlation time Hessian.
####################################################

def calc_axial_d2ti(data, diff_data):
    """Second partial derivatives of the diffusional correlation times.

    The tm-tm second partial derivatives are:

        d2t0
        ----  =  0
        dtm2

        d2t1
        ----  =  0
        dtm2

        d2t1
        ----  =  0
        dtm2


    The tm-Dratio second partial derivatives are:

           d2t0               1
        -----------  =  - ----------
        dtm.dDratio       3Dratio**2

           d2t1                  6
        -----------  =  - ----------------
        dtm.dDratio       (1 + 5Dratio)**2

           d2t1                3
        -----------  =  ---------------
        dtm.dDratio     (2 + Dratio)**2


    The Dratio-Dratio second partial derivatives are:

          d2t0          2tm
        --------  =  ----------
        dDratio2     3Dratio**3

          d2t1             60tm
        --------  =  ----------------
        dDratio2     (1 + 5Dratio)**3

          d2t1               6tm
        --------  =  - ---------------
        dDratio2       (2 + Dratio)**3


    The diffusion parameter set in data.diff_params is {tm, Dratio, theta, phi}.
    """

    # tm-tm second partial derivatives (don't do anything).

    # tm-Dratio second partial derivatives.
    if diff_data.params[1] == 0:
        data.d2ti[0, 1, 0] = data.d2ti[1, 0, 0] = -1e99
    else:
        data.d2ti[0, 1, 0] = data.d2ti[1, 0, 0] = - 1.0/(3.0 * diff_data.params[1]**2)
    data.d2ti[0, 1, 1] = data.d2ti[1, 0, 1] = - 6.0 / (1.0 + 5.0*diff_data.params[1])**2
    data.d2ti[0, 1, 2] = data.d2ti[1, 0, 2] = 3.0 / (2.0 + diff_data.params[1])**2

    # Dratio-Dratio second partial derivatives.
    if diff_data.params[1] == 0:
        if diff_data.params[0] == 0:
            data.d2ti[1, 1, 0] = 0.0
        else:
            data.d2ti[1, 1, 0] = 1e99
    else:
        data.d2ti[1, 1, 0] = 2.0 * diff_data.params[0] / (3.0 * diff_data.params[1]**3)
    data.d2ti[1, 1, 1] = 60.0 * diff_data.params[0] / (1.0 + 5.0*diff_data.params[1])**3
    data.d2ti[1, 1, 2] = -6.0 * diff_data.params[0] / (2.0 + diff_data.params[1])**3



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
    if diff_data.params[0] == 0:
        data.Diso = 1e99
    else:
        data.Diso = 1.0 / (6.0 * diff_data.params[0])

    # Calculate mu.
    data.mu = sqrt(diff_data.params[1]**2 + diff_data.params[2]**2 / 3.0)

    # t-2.
    data.ti[0] = 6.0 * (data.Diso + diff_data.params[1])
    if data.ti[0] == 0.0:
        data.ti[0] = 1e99
    else:
        data.ti[0] = 1.0 / data.ti[0]

    # t-1.
    data.ti[1] = 6.0 * (data.Diso - 0.5 * (diff_data.params[1] + diff_data.params[1]))
    if data.ti[1] == 0.0:
        data.ti[1] = 1e99
    else:
        data.ti[1] = 1.0 / data.ti[1]

    # t0.
    data.ti[2] = 6.0 * (data.Diso - data.mu)
    if data.ti[2] == 0.0:
        data.ti[2] = 1e99
    else:
        data.ti[2] = 1.0 / data.ti[2]

    # t1.
    data.ti[3] = 6.0 * (data.Diso - 0.5 * (diff_data.params[1] - diff_data.params[1]))
    if data.ti[3] == 0.0:
        data.ti[3] = 1e99
    else:
        data.ti[3] = 1.0 / data.ti[3]

    # t2.
    data.ti[4] = 6.0 * (data.Diso + data.mu)
    if data.ti[4] == 0.0:
        data.ti[4] = 1e99
    else:
        data.ti[4] = 1.0 / data.ti[4]
