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


# Isotropic global correlation time equation.
#############################################

def calc_iso_ti(data, diff_data):
    """Diffusional correlation times for isotropic diffusion.

    t0 = tm
    """

    data.ti[0] = diff_data.params[0]



# Axially symmetric global correlation time equation.
#####################################################

def calc_axial_ti(data, diff_data):
    """Diffusional correlation times.

    The equations are:

                 1
        t0  =  -----
               6Dper

                    1
        t1  =  ------------
               5Dper + Dpar

                     1
        t2  =  -------------
               2Dper + 4Dpar


    The diffusion parameter set in data.diff_params is {Dper, Dpar, theta, phi}.
    """

    # t0.
    if diff_data.params[0] == 0:
        data.ti[0] = 1e99
    else:
        data.ti[0] = 1.0 / (6.0 * diff_data.params[0])

    # t1.
    if diff_data.five_Dper_plus_Dpar == 0:
        data.ti[1] = 1e99
    else:
        data.ti[1] = 1.0 / diff_data.five_Dper_plus_Dpar

    # t2.
    if diff_data.Dper_plus_two_Dpar == 0:
        data.ti[2] = 1e99
    else:
        data.ti[2] = 1.0 / (2.0 * diff_data.Dper_plus_two_Dpar)



# Isotropic global correlation time equation.
#############################################

def calc_iso_dti(data, diff_data):
    """Diffusional correlation times for isotropic diffusion.

    The tm partial derivatives are:
    
        dt0
        ---  =  1
        dtm
    """

    data.dti[0] = 1.0



# Axially symmetric global correlation time gradient.
#####################################################

def calc_axial_dti(data, diff_data):
    """Partial derivatives of the diffusional correlation times.

    The Dper partial derivatives are:

         dt0           1
        -----  =  - --------
        dDper       6Dper**2

         dt1                5
        -----  =  - -----------------
        dDper       (5Dper + Dpar)**2

         dt1                1
        -----  =  - ------------------
        dDper       2(Dper + 2Dpar)**2


    The Dpar partial derivatives are:

         dt0
        -----  =  0
        dDpar

         dt1                1
        -----  =  - -----------------
        dDpar       (5Dper + Dpar)**2

         dt1                1
        -----  =  - -----------------
        dDpar       (Dper + 2Dpar)**2


    The diffusion parameter set in data.diff_params is {Dper, Dpar, theta, phi}.
    """

    # Dper partial derivatives.
    data.dti[0, 0] = -1.0 / (6.0 * diff_data.params[0]**2)
    data.dti[0, 1] = -5.0 / diff_data.five_Dper_plus_Dpar_sqrd
    data.dti[0, 2] = -1.0 / (2.0 * diff_data.Dper_plus_two_Dpar_sqrd)

    # Dpar partial derivatives.
    data.dti[1, 1] = -1.0 / diff_data.five_Dper_plus_Dpar_sqrd
    data.dti[1, 2] = -1.0 / diff_data.Dper_plus_two_Dpar_sqrd



# Axially symmetric global correlation time Hessian.
####################################################

def calc_axial_d2ti(data, diff_data):
    """Second partial derivatives of the diffusional correlation times.

    The Dper-Dper second partial derivatives are:

         d2t0         1
        ------  =  --------
        dDper2     3Dper**3

         d2t1             50
        ------  =  -----------------
        dDper2     (5Dper + Dpar)**3

         d2t1             1
        ------  =  -----------------
        dDper2     (Dper + 2Dpar)**3


    The Dper-Dpar second partial derivatives are:

           d2t0
        -----------  =  0
        dDper.dDpar

           d2t1               10
        -----------  =  -----------------
        dDper.dDpar     (5Dper + Dpar)**3

           d2t1                2
        --------- -  =  -----------------
        dDper.dDpar     (Dper + 2Dpar)**3


    The Dpar-Dpar second partial derivatives are:

         d2t0
        ------  =  0
        dDpar2

         d2t1             2
        ------  =  -----------------
        dDpar2     (5Dper + Dpar)**3

         d2t1             4
        ------  =  -----------------
        dDpar2     (Dper + 2Dpar)**3


    The diffusion parameter set in data.diff_params is {Dper, Dpar, theta, phi}.
    """

    # Dper-Dper second partial derivatives.
    data.d2ti[0, 0, 0] = 1.0 / (3.0 * diff_data.params[0]**3)
    data.d2ti[0, 0, 1] = 50.0 / diff_data.five_Dper_plus_Dpar_cubed
    data.d2ti[0, 0, 2] = 1.0 / diff_data.Dper_plus_two_Dpar_cubed

    # Dper-Dpar second partial derivatives.
    data.d2ti[0, 1, 1] = data.d2ti[1, 0, 1] = 10.0 / diff_data.five_Dper_plus_Dpar_cubed
    data.d2ti[0, 1, 2] = data.d2ti[1, 0, 2] = 2.0 / diff_data.Dper_plus_two_Dpar_cubed

    # Dpar-Dpar second partial derivatives.
    data.d2ti[1, 1, 1] = 2.0 / diff_data.five_Dper_plus_Dpar_cubed
    data.d2ti[1, 1, 2] = 4.0 / diff_data.Dper_plus_two_Dpar_cubed
