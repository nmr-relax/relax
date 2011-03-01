###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


# relax module imports.
from ri_comps import r1_comps, dr1_comps, d2r1_comps
from ri_prime import func_ri_prime


# Calculate the NOE value.
##########################

def calc_noe(data, i, frq_num, get_r1, params):
    """Calculate the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Get the r1 value either from data.ri or by calculation if the value is not in data.ri
    data.r1[i] = get_r1[i](data, i, frq_num, params)

    # Calculate the NOE.
    if data.r1[i] == 0.0 and data.ri[i] == 0.0:
        data.ri[i] = 1.0
    elif data.r1[i] == 0.0:
        data.ri[i] = 1e99
    else:
        data.ri[i] = 1.0 + data.g_ratio*(data.ri[i] / data.r1[i])


def calc_dnoe(data, i, frq_num, get_dr1, params, j):
    """Calculate the derivative of the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Calculate the NOE derivative.
    data.dr1[j, i] = get_dr1[i](data, i, frq_num, params, j)
    if data.r1[i] == 0.0 and data.ri[i] == 0.0:
        data.dri[j, i] = 0.0
    elif data.r1[i] == 0.0:
        data.dri[j, i] = 1e99
    else:
        data.dri[j, i] = data.g_ratio * (1.0 / data.r1[i]**2) * (data.r1[i] * data.dri[j, i] - data.ri[i] * data.dr1[j, i])


def calc_d2noe(data, i, frq_num, get_d2r1, params, j, k):
    """Calculate the second partial derivative of the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Calculate the NOE second derivative.
    data.d2r1[j, k, i] = get_d2r1[i](data, i, frq_num, params, j, k)
    if data.r1[i] == 0.0 and data.ri[i] == 0.0:
        data.d2ri[j, k, i] = 0.0
    elif data.r1[i] == 0.0:
        data.d2ri[j, k, i] = 1e99
    else:
        a = data.ri[i] * (2.0 * data.dr1[j, i] * data.dr1[k, i] - data.r1[i] * data.d2r1[j, k, i])
        b = data.r1[i] * (data.dri[j, i] * data.dr1[k, i] + data.dr1[j, i] * data.dri[k, i] - data.r1[i] * data.d2ri[j, k, i])
        data.d2ri[j, k, i] = data.g_ratio * (1.0 / data.r1[i]**3) * (a - b)



# Calculate the R1 value.
#########################

def calc_r1(data, i, frq_num, params):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data.

    R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func
    """

    # Place data in the R1 data class.
    data.r1_data.remap_table = data.remap_table
    data.r1_data.jw = data.jw
    data.r1_data.dip_const_func = data.dip_const_func
    data.r1_data.csa_const_func = data.csa_const_func

    # Calculate the r1 components.
    r1_comps(data.r1_data, i, params)

    # Calculate the r1 value.
    ri = func_ri_prime(data.r1_data)
    return ri[i]


def calc_dr1(data, i, frq_num, params, j):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data.

    The equations are::

        dR1()
        -----  =  dip_const_func . dip_Jw_R1_grad  +  csa_const_func . csa_Jw_R1_grad
         dJw

        dR1()
        -----  =  0
        dRex

        dR1()
        -----  =  dip_const_grad . dip_Jw_R1_func
         dr

        dR1()
        -----  =  csa_const_grad . csa_Jw_R1_func
        dcsa
    """

    # Place data in the R1 data class.
    data.r1_data.remap_table = data.remap_table
    data.r1_data.djw = data.djw
    data.r1_data.dip_const_grad = data.dip_const_grad
    data.r1_data.csa_const_grad = data.csa_const_grad

    # Calculate the dr1 components.
    dr1_comps(data.r1_data, i, params)

    # Calculate the dr1 value.
    dri = data.r1_data.create_dri_prime[j](data.r1_data)

    return dri[i]


def calc_d2r1(data, i, frq_num, params, j, k):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data."""

    # Place data in the R1 data class.
    data.r1_data.remap_table = data.remap_table
    data.r1_data.d2jw = data.d2jw
    data.r1_data.dip_const_hess = data.dip_const_hess
    data.r1_data.csa_const_hess = data.csa_const_hess

    # Calculate the dr1 components.
    d2r1_comps(data.r1_data, i, params)

    # Calculate the dr1 value.
    if data.r1_data.create_d2ri_prime[j][k]:
        d2ri = data.r1_data.create_d2ri_prime[j][k](data.r1_data)
        return d2ri[i]
    else:
        return 0.0



# Extract the R1 value.
#######################

def extract_r1(data, i, frq_num, params):
    """Get the R1 value from data.ri_prime"""

    return data.ri_prime[data.noe_r1_table[i]]


def extract_dr1(data, i, frq_num, params, j):
    """Get the dR1 value from data.dri_prime"""

    return data.dri_prime[j, data.noe_r1_table[i]]


def extract_d2r1(data, i, frq_num, params, j, k):
    """Get the d2R1 value from data.d2ri_prime"""

    return data.d2ri_prime[j, k, data.noe_r1_table[i]]
