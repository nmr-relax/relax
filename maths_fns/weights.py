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

    data.dci[:, 0] = 3.0 * data.delta * (3.0 * data.delta**2 - 1.0) * data.ddelta_dpsi
    data.dci[:, 1] = 6.0 * data.delta * (1.0 - 2.0 * data.delta**2) * data.ddelta_dpsi
    data.dci[:, 2] = 3.0 * data.delta * (data.delta**2 - 1.0) * data.ddelta_dpsi



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
    data.d2ci[:, :, 0] = 3.0 * ((9.0 * data.delta**2 - 1.0) * op + data.delta * (3.0 * data.delta**2 - 1.0) * data.d2delta_dpsi2)
    data.d2ci[:, :, 1] = 6.0 * ((1.0 - 6.0 * data.delta**2) * op + data.delta * (1.0 - 2.0 * data.delta**2) * data.d2delta_dpsi2)
    data.d2ci[:, :, 2] = 3.0 * ((3.0 * data.delta**2 - 1.0) * op + data.delta * (data.delta**2 - 1.0) * data.d2delta_dpsi2)



# Anisotropic weight equation.
##############################

def calc_aniso_ci(data, diff_data):
    """Weight equations for axially symmetric diffusion.

    The equations are:

        c-2 = 3 . delta_alpha**2 . delta_beta**2

        c-1 = 3 . delta_alpha**2 . delta_gamma**2

        c0  = 1/4 (3(delta_alpha**4 + delta_beta**4 + delta_gamma**4) - 1 - e)

        c1  = 3 . delta_beta**2 . delta_gamma**2

        c2  = 1/4 (3(delta_alpha**4 + delta_beta**4 + delta_gamma**4) - 1 + e)

    where:
              Da - Dr                                                    Da + Dr                                                    2Da
        e  =  ------- (delta_alpha**4 + 2delta_beta**2.delta_gamma**2) + ------- (delta_beta**4 + 2delta_alpha**2.delta_gamma**2) - --- (delta_gamma**4 + 2delta_alpha**2.delta_beta**2)
                mu                                                         mu                                                       mu
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

    # Calculate e.
    if diff_data.params[1] == 0.0:
        e = 0.0
    else:
        e = (diff_data.params[1] - diff_data.params[2]) / data.mu * (data.delta_alpha**4 + 2.0 * data.delta_beta**2 * data.delta_gamma**2)
        e = e + (diff_data.params[1] + diff_data.params[2]) / data.mu * (data.delta_beta**4 + 2.0 * data.delta_alpha**2 * data.delta_gamma**2)
        e = e - 2.0 * diff_data.params[1] / data.mu * (data.delta_gamma**4 + 2.0 * data.delta_alpha**2 * data.delta_beta**2)

    # Weights.
    data.ci[0] = 3.0 * data.delta_alpha**2 * data.delta_beta**2
    data.ci[1] = 3.0 * data.delta_alpha**2 * data.delta_gamma**2
    data.ci[2] = 0.25 * (3.0 * (data.delta_alpha**4 + data.delta_beta**4 + data.delta_gamma**4) - 1 - e)
    data.ci[3] = 3.0 * data.delta_beta**2 * data.delta_gamma**2
    data.ci[4] = 0.25 * (3.0 * (data.delta_alpha**4 + data.delta_beta**4 + data.delta_gamma**4) - 1 + e)
