###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


from ri_comps import r1_comps, dr1_comps, d2r1_comps
from ri_prime import func_ri_prime


def ri(data, create_ri, get_r1):
    """Additional layer of equations to simplify the relaxation equations, gradients, and Hessians.

    The R1 and R2 equations are left alone, while the NOE is calculated from the R1 and sigma_noe
    values.


    The relaxation equations
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.ri
    Dimension:  1D, (relaxation data)
    Type:  Numeric array, Float64
    Dependencies:  data.ri_prime
    Required by:  data.chi2, data.dchi2, data.d2chi2


    Formulae
    ~~~~~~~~

    R1()  =  R1'()


    R2()  =  R2'()

                   gH   sigma_noe()
    NOE()  =  1 +  -- . -----------
                   gN      R1()
    """

    # Calculate the NOE values.
    for i in xrange(data.num_ri):
        if create_ri[i]:
            create_ri[i](data, i, data.remap_table[i], get_r1)


def dri(data, create_dri, get_dr1):
    """Additional layer of equations to simplify the relaxation equations, gradients, and Hessians.

    The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation
    rate equation and the R1 equation.


    The relaxation gradients
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.dri
    Dimension:  2D, (parameters, relaxation data)
    Type:  Numeric array, Float64
    Dependencies:  data.ri_prime, data.dri_prime
    Required by:  data.dchi2, data.d2chi2


    Formulae
    ~~~~~~~~

     dR1()       dR1'()
    -------  =  -------
    dthetaj     dthetaj


     dR2()       dR2'()
    -------  =  -------
    dthetaj     dthetaj


     dNOE()     gH      1      /        dsigma_noe()                    dR1()  \ 
    -------  =  -- . ------- . | R1() . ------------  -  sigma_noe() . ------- |
    dthetaj     gN   R1()**2   \          dthetaj                      dthetaj /
    """

    # Loop over the relaxation values and modify the NOE gradients.
    for i in xrange(data.num_ri):
        if create_dri[i]:
            create_dri[i](data, i, data.remap_table[i], get_dr1)


def d2ri(data, create_d2ri, get_d2r1):
    """Additional layer of equations to simplify the relaxation equations, gradients, and Hessians.

    The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation
    rate equation and the R1 equation.


    The relaxation Hessians
    ~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.d2ri
    Dimension:  3D, (parameters, parameters, relaxation data)
    Type:  Numeric array, Float64
    Dependencies:  data.ri_prime, data.dri_prime, data.d2ri_prime
    Required by:  data.d2chi2


    Formulae
    ~~~~~~~~

         d2R1()             d2R1'()
    ---------------  =  ---------------
    dthetai.dthetaj     dthetai.dthetaj


         d2R2()             d2R2'()
    ---------------  =  ---------------
    dthetai.dthetaj     dthetai.dthetaj


        d2NOE()         gH      1      /               /      dR1()     dR1()                  d2R1()     \ 
    ---------------  =  -- . ------- . | sigma_noe() . | 2 . ------- . -------  -  R1() . --------------- |
    dthetai.dthetaj     gN   R1()**3   \               \     dthetai   dthetaj            dthetai.dthetaj /

                 / dsigma_noe()    dR1()       dR1()    dsigma_noe()             d2sigma_noe()  \ \ 
        - R1() . | ------------ . -------  +  ------- . ------------  -  R1() . --------------- | |
                 \   dthetai      dthetaj     dthetai     dthetaj               dthetai.dthetaj / /
    """

    # Loop over the relaxation values and modify the NOE Hessians.
    for i in xrange(data.num_ri):
        if create_d2ri[i]:
            create_d2ri[i](data, i, data.remap_table[i], get_d2r1)



# Calculate the NOE value.
##########################

def calc_noe(data, i, frq_num, get_r1):
    """Calculate the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Get the r1 value either from data.ri_prime or by calculation if the value is not in data.ri_prime
    data.r1[i] = get_r1[i](data, i, frq_num)

    # Calculate the NOE.
    if data.r1[i] == 0.0:
        data.ri[i] = 1e99
    else:
        data.ri[i] = 1.0 + data.g_ratio*(data.ri_prime[i] / data.r1[i])


def calc_dnoe(data, i, frq_num, get_dr1):
    """Calculate the derivative of the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Calculate the NOE derivative.
    data.dr1[i] = get_dr1[i](data, i, frq_num)
    if data.r1[i] == 0.0:
        data.dri[i] = 1e99
    else:
        data.dri[i] = data.g_ratio * (1.0 / data.r1[i]**2) * (data.r1[i] * data.dri_prime[i] - data.ri_prime[i] * data.dr1[i])


def calc_d2noe(data, i, frq_num, get_d2r1):
    """Calculate the second partial derivative of the NOE value.

    Half this code needs to be shifted into the function initialisation code.
    """

    # Calculate the NOE second derivative.
    data.d2r1[i] = get_d2r1[i](data, i, frq_num)
    if data.r1[i] == 0.0:
        data.d2ri[i] = 1e99
    else:
        for j in xrange(len(data.params)):
            a = data.ri_prime[i] * (2.0 * data.dr1[i, j] * data.dr1[i] - data.r1[i] * data.d2r1[i, j])
            b = data.r1[i] * (data.dri_prime[i, j] * data.dr1[i] + data.dr1[i, j] * data.dri_prime[i] - data.r1[i] * data.d2ri_prime[i, j])
            data.d2ri[i, j] = data.g_ratio * (1.0 / data.r1[i]**3) * (a - b)



# Calculate the R1 value.
#########################

def calc_r1(data, i, frq_num):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data.

    R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func
    """

    # Place data in the R1 data class.
    data.r1_data.params = data.params
    data.r1_data.remap_table = data.remap_table
    data.r1_data.jw = data.jw
    data.r1_data.dip_const_func = data.dip_const_func
    data.r1_data.csa_const_func = data.csa_const_func

    # Calculate the r1 components.
    r1_comps(data.r1_data, i)

    # Calculate the r1 value.
    func_ri_prime(data.r1_data)

    return data.r1_data.ri_prime[i]


def calc_dr1(data, i, frq_num):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data.

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
    data.r1_data.params = data.params
    data.r1_data.remap_table = data.remap_table
    data.r1_data.djw = data.djw
    data.r1_data.dip_const_grad = data.dip_const_grad
    data.r1_data.csa_const_grad = data.csa_const_grad

    # Calculate the dr1 components.
    dr1_comps(data.r1_data, i)

    # Calculate the dr1 value.
    for j in xrange(len(data.params)):
        data.r1_data.create_dri_prime[j](data.r1_data, j)

    return data.r1_data.dri_prime[i]


def calc_d2r1(data, i, frq_num):
    """Calculate the R1 value if there is no R1 data corresponding to the NOE data."""

    # Place data in the R1 data class.
    data.r1_data.params = data.params
    data.r1_data.remap_table = data.remap_table
    data.r1_data.d2jw = data.d2jw
    data.r1_data.dip_const_hess = data.dip_const_hess
    data.r1_data.csa_const_hess = data.csa_const_hess

    # Calculate the dr1 components.
    d2r1_comps(data.r1_data, i)

    # Calculate the dr1 value.
    for j in xrange(len(data.params)):
        for k in xrange(j + 1):
            if data.r1_data.create_d2ri_prime[j][k]:
                data.r1_data.create_d2ri_prime[j][k](data.r1_data, j, k)
                # Make the Hessian symmetric.
                if i != j:
                    data.r1_data.d2ri_prime[i, k, j] = data.r1_data.d2ri_prime[i, j, k]

    return data.r1_data.d2ri_prime[i]



# Extract the R1 value.
#######################

def extract_r1(data, i, frq_num):
    """Get the R1 value from data.ri_prime"""

    return data.ri_prime[data.noe_r1_table[i]]


def extract_dr1(data, i, frq_num):
    """Get the dR1 value from data.dri_prime"""

    return data.dri_prime[data.noe_r1_table[i]]


def extract_d2r1(data, i, frq_num):
    """Get the d2R1 value from data.d2ri_prime"""

    return data.d2ri_prime[data.noe_r1_table[i]]
