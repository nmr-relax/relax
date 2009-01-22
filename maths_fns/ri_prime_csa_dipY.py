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

from Numeric import sum

# The transformed relaxation equations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Relaxation equations
#    ~~~~~~~~~~~~~~~~~~~~
#
#        R1()  =  dip_const_func . dip_Jw_R1_func  +  csa1_const_func . csa1_Jw_R1_func  +  csa2_const_func . csa2_Jw_R1_func  +  csaC_const_func . csaC_Jw_R1_func  +  dip1_const_func . dip1_Jw_R1_func  +  dip2_const_func . dip2_Jw_R1_func
#
#
#                 dip_const_func                      csa1_const_func
#        R2()  =  -------------- . dip_Jw_R2_func  +  --------------- . csa1_Jw_R2_func  +                 
#                       2                                    6
#
#                 csa2_const_func                       csaC_const_func
#                 --------------- . csa2_Jw_R2_func  +  ---------------- . csaC_Jw_R2_func  +
#                        6                                     6
#
#                 dip1_const_func                      dip2_const_func
#                 -------------- . dip1_Jw_R2_func  +  --------------- . dip2_Jw_R2_func + ... +  rex_const_func 
#                        2                                    2
#
#
#        sigma_noe()  =  dip_const_func . dip_Jw_sigma_noe_func
#
#
#        Ri  =  dip_comps_func . dip_jw_comps_func  +  csa1_comps_func * csa1_jw_comps_func  +  csa2_comps_func * csa2_jw_comps_func  +  csaC_comps_func * csaC_jw_comps_func  +  dip1_comps_func * dip1_jw_comps_func  +  dip2_comps_func * dip2_jw_comps_func + ... +  rex_comps_func
#
#
#
# The transformed relaxation gradients
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Spectral density parameter
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#        dR1()
#        -----  =  dip_const_func . dip_Jw_R1_grad  +  csa1_const_func . csa1_Jw_R1_grad  +  csa2_const_func . csa2_Jw_R1_grad  +  csaC_const_func . csaC_Jw_R1_grad  +  dip1_const_func . dip1_Jw_R1_grad  +  dip2_const_func . dip2_Jw_R1_grad + ...
#         dJw
#
#
#
#        dR2()     dip_const_func                      csa1_const_func                       csa2_const_func                      csaC_const_func                        dip1_const_func                       dip2_const_func                  
#        -----  =  -------------- . dip_Jw_R2_grad  +  --------------- . csa1_Jw_R2_grad  +  --------------- . csa2_Jw_R2_grad  +  --------------- . csaC_Jw_R2_grad  +  --------------- . dip1_Jw_R2_grad  +  --------------- . dip2_Jw_R2_grad + ...
#         dJw            2                                    6                                     6                                    6                                      2                                     2                         
#
#
#        dsigma_noe()
#        ------------  = dip_const_func . dip_Jw_sigma_noe_grad
#            dJw
#
#
#        dRi()
#        -----  =  dip_comps_func . dip_jw_comps_grad  +  csa1_comps_func . csa1_jw_comps_grad  +  csa2_comps_func . csa2_jw_comps_grad  +  csaC_comps_func . csaC_jw_comps_grad  +  dip1_comps_func . dip1_jw_comps_grad  +  dip2_comps_func . dip2_jw_comps_grad + ...
#         dJw
#
#
#    Chemical exchange
#    ~~~~~~~~~~~~~~~~~
#
#        dR1()
#        -----  =  0
#        dRex
#
#
#        dR2()
#        -----  =  rex_const_grad
#        dRex
#
#
#        dsigma_noe()
#        ------------  =  0
#           dRex
#
#
#        dRi()
#        -----  =  rex_comps_grad
#        dRex
#
#
#    Bond length
#    ~~~~~~~~~~~
#
#        dR1()
#        -----  =  dip_const_grad . dip_Jw_R1_func
#         dr
#
#
#        dR2()     dip_const_grad
#        -----  =  -------------- . dip_Jw_R2_func
#         dr             2
#
#
#        dsigma_noe()
#        ------------  =  dip_const_grad . dip_Jw_sigma_noe_func
#             dr
#
#
#        dRi()
#        -----  =  dip_comps_grad . dip_jw_comps_func
#         dr
#
#
#    CSA
#    ~~~
#
#        dR1()
#        -----  =  csa1_const_grad . csa1_Jw_R1_func  +  csa2_const_grad . csa2_Jw_R1_func  +  csaC_const_grad . csaC_Jw_R1_func
#        dcsa
#
#
#        dR2()     csa1_const_grad                       csa2_const_grad                       csaC_const_grad                   
#        -----  =  --------------- . csa1_Jw_R2_func  +  --------------- . csa2_Jw_R2_func  +  --------------- . csaC_Jw_R2_func 
#        dcsa             6                                     6                                     6                          
#
#
#        dsigma_noe()
#        ------------  =  0
#            dcsa
#
#
#        dRi()
#        -----  =  csa1_const_grad . csa1_jw_comps_func  +  csa2_const_grad . csa2_jw_comps_func  +  csaC_const_grad . csaC_jw_comps_func
#        dcsa
#
#
#
# The transformed relaxation Hessians
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Spectral density parameter - Spectral density parameter
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#          d2R1()
#        ---------  =  dip_const_func . dip_Jw_R1_hess  +  csa1_const_func . csa1_Jw_R1_hess  +  csa2_const_func . csa2_Jw_R1_hess  +  csaC_const_func . csaC_Jw_R1_hess  +  dip1_const_func . dip1_Jw_R1_hess  +  dip2_const_func . dip2_Jw_R1_hess + ...
#        dJwi.dJwj
#
#
#          d2R2()      dip_const_func                      csa1_const_func                       csa2_const_func                       csaC_const_func                       dip1_const_func                       dip2_const_func                  
#        ---------  =  -------------- . dip_Jw_R2_hess  +  --------------- . csa1_Jw_R2_hess  +  --------------- . csa2_Jw_R2_hess  +  --------------- . csaC_Jw_R2_hess  +  --------------- . dip1_Jw_R2_hess  +  --------------- . dip2_Jw_R2_hess + ...
#        dJwi.dJwj           2                                    6                                     6                                     6                                     2                                     2                         
#
#
#        d2sigma_noe()
#        -------------  =  dip_const_func . dip_Jw_sigma_noe_hess
#          dJwi.dJwj
#
#
#          d2Ri()
#        ---------  =  dip_comps_func . dip_jw_comps_hess  +  csa1_const_func . csa1_jw_comps_hess  +  csa2_const_func . csa2_jw_comps_hess  +  csaC_const_func . csaC_jw_comps_hess  +  dip1_const_func . dip1_jw_comps_hess  +  dip2_const_func . dip2_jw_comps_hess + ...
#        dJwi.dJwj
#
#
#
#    Spectral density parameter - Chemical exchange
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#         d2R1()               d2R2()              d2sigma_noe()
#        --------  =  0   ,   --------  =  0   ,   -------------  =  0
#        dJw.dRex             dJw.dRex               dJw.dRex
#
#
#    Spectral density parameter - CSA
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#         d2R1()
#        --------  =  csa_const_grad . csa_Jw_R1_grad
#        dJw.dcsa
#
#
#         d2R2()      csa_const_grad
#        --------  =  -------------- . csa_Jw_R2_grad
#        dJw.dcsa           6
#
#
#        d2sigma_noe()
#        -------------  =  0
#          dJw.dcsa
#
#
#         d2Ri()
#        --------  =  csa_comps_grad . csa_jw_comps_grad
#        dJw.dcsa
#
#
#    Spectral density parameter - Bond length
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#        d2R1()
#        ------  =  dip_const_grad . dip_Jw_R1_grad
#        dJw.dr
#
#
#        d2R2()     dip_const_grad
#        ------  =  -------------- . dip_Jw_R2_grad
#        dJw.dr           2
#
#
#        d2sigma_noe()
#        -------------  =  dip_const_grad . dip_Jw_sigma_noe_grad
#           dJw.dr
#
#
#        d2Ri()
#        ------  =  dip_comps_grad . dip_jw_comps_grad
#        dJw.dr
#
#
#    Chemical exchange - Chemical exchange
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#         d2R1()              d2R2()             d2sigma_noe()
#        -------  =  0   ,   -------  =  0   ,   -------------  =  0
#        dRex**2             dRex**2                dRex**2
#
#
#    Chemical exchange - CSA
#    ~~~~~~~~~~~~~~~~~~~~~~~
#
#          d2R1()                d2R2()              d2sigma_noe()
#        ---------  =  0   ,   ---------  =  0   ,   -------------  =  0
#        dRex.dcsa             dRex.dcsa               dRex.dcsa
#
#
#    Chemical exchange - Bond length
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#         d2R1()              d2R2()             d2sigma_noe()
#        -------  =  0   ,   -------  =  0   ,   -------------  =  0
#        dRex.dr             dRex.dr                dRex.dr
#
#
#    CSA - CSA
#    ~~~~~~~~~
#
#         d2R1()
#        -------  =  csa_const_hess  . csa_Jw_R1_func
#        dcsa**2
#
#
#         d2R2()     csa_const_hess
#        -------  =  -------------- . csa_Jw_R2_func
#        dcsa**2           6
#
#
#        d2sigma_noe()
#        -------------  =  0
#           dcsa**2
#
#
#         d2Ri()
#        -------  =  csa_comps_hess  . csa_jw_comps_func
#        dcsa**2
#
#
#    CSA - Bond length
#    ~~~~~~~~~~~~~~~~~
#
#         d2R1()              d2R2()             d2sigma_noe()
#        -------  =  0   ,   -------  =  0   ,   -------------  =  0
#        dcsa.dr             dcsa.dr                dcsa.dr
#
#
#    Bond length - Bond length
#    ~~~~~~~~~~~~~~~~~~~~~~~~~
#
#        d2R1()
#        ------  =  dip_const_hess . dip_Jw_R1_func
#        dr**2
#
#
#        d2R2()     dip_const_hess
#        ------  =  -------------- . dip_Jw_R2_func
#        dr**2            2
#
#
#        d2sigma_noe()
#        -------------  =  dip_const_hess . dip_Jw_sigma_noe_func
#            dr**2
#
#
#        d2Ri()
#        ------  =  dip_comps_hess . dip_jw_comps_func
#        dr**2
#
#


# Transformed relaxation equatons.
##################################

def func_ri_prime(data):
    """Calculate the transformed relaxation values."""

    data.mezisoucet = 0.0
    for z in xrange(data.xy_vect_num):
	    if z == 0:
		    data.mezisoucet = data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    else:
		    data.mezisoucet = data.mezisoucet + data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    
    
    return data.dip_comps_func * data.dip_jw_comps_func + data.csa1_comps_func * data.csa1_jw_comps_func + data.csa2_comps_func * data.csa2_jw_comps_func + data.csaC_comps_func * data.csaC_jw_comps_func + data.mezisoucet


def func_ri_prime_rex(data):
    """Calculate the transformed relaxation values."""

    data.mezisoucet = 0.0
    for z in xrange(data.xy_vect_num):
	    if z == 0:
		    data.mezisoucet = data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    else:
		    data.mezisoucet = data.mezisoucet + data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    
    
    #return data.dip_comps_func * data.dip_jw_comps_func + data.csa1_comps_func * data.csa1_jw_comps_func + data.csa2_comps_func * data.csa2_jw_comps_func + data.csaC_comps_func * data.csaC_jw_comps_func + sum(data.dipY_comps_func * data.dipY_jw_comps_func, axis=0) + data.rex_comps_func
    return data.dip_comps_func * data.dip_jw_comps_func + data.csa1_comps_func * data.csa1_jw_comps_func + data.csa2_comps_func * data.csa2_jw_comps_func + data.csaC_comps_func * data.csaC_jw_comps_func + data.mezisoucet + data.rex_comps_func


# Transformed relaxation gradients.
###################################

# dRi/dJ(w)
def func_dri_djw_prime(data):
    """Spectral density parameter derivatives."""

    data.mezisoucet = 0.0
    for z in xrange(data.xy_vect_num):
	    if z == 0:
		    data.mezisoucet = data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    else:
		    data.mezisoucet = data.mezisoucet + data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    
    
    #return data.dip_comps_func * data.dip_jw_comps_grad + data.csa1_comps_func * data.csa1_jw_comps_grad + data.csa2_comps_func * data.csa2_jw_comps_grad + data.csaC_comps_func * data.csaC_jw_comps_grad + sum(data.dipY_comps_func * data.dipY_jw_comps_grad, axis=0) 
    return data.dip_comps_func * data.dip_jw_comps_grad + data.csa1_comps_func * data.csa1_jw_comps_grad + data.csa2_comps_func * data.csa2_jw_comps_grad + data.csaC_comps_func * data.csaC_jw_comps_grad + data.mezisoucet 


# dRi/dRex
def func_dri_drex_prime(data):
    """Chemical exchange derivatives."""

    return data.rex_comps_grad


# dRi/dr
def func_dri_dr_prime(data):
    """Bond length derivatives."""

    return data.dip_comps_grad * data.dip_jw_comps_func


# dRi/dCSA
def func_dri_dcsa_prime(data):
    """CSA derivatives."""

    return data.csa_comps_grad * data.csa_jw_comps_func




# Transformed relaxation Hessians.
##################################


# d2Ri/dJ(w)i.dJ(w)j
def func_d2ri_djwidjwj_prime(data):
    """Spectral density parameter / spectral density parameter Hessian.

      d2R1()
    ---------  =  dip_const_func . dip_Jw_R1_hess  +  csa1_const_func . csa1_Jw_R1_hess  +  csa2_const_func . csa2_Jw_R1_hess  +  csaC_const_func . csaC_Jw_R1_hess  +  dip1_const_func . dip1_Jw_R1_hess  +  dip2_const_func . dip2_Jw_R1_hess + ...
    dJwi.dJwj

      d2R2()      dip_const_func                      csa1_const_func                       csa2_const_func                       csaC_const_func                       dip1_const_func                       dip2_const_func                  
    ---------  =  -------------- . dip_Jw_R2_hess  +  --------------- . csa1_Jw_R2_hess  +  --------------- . csa2_Jw_R2_hess  +  --------------- . csaC_Jw_R2_hess  +  --------------- . dip1_Jw_R2_hess  +  --------------- . dip2_Jw_R2_hess + ...
    dJwi.dJwj           2                                    6                                     6                                     6                                     2                                     2                         

    d2sigma_noe()
    -------------  =  dip_const_func . dip_Jw_sigma_noe_hess
      dJwi.dJwj

      d2Ri()
    ---------  =  dip_comps_func . dip_jw_comps_hess  +  csa1_comps_func . csa1_jw_comps_hess  +  csa2_comps_func . csa2_jw_comps_hess  +  csaC_comps_func . csaC_jw_comps_hess  +  dip1_comps_func . dip1_jw_comps_hess  +  dip2_comps_func . dip2_jw_comps_hess + ...
    dJwi.dJwj
    """

    data.mezisoucet = 0.0
    for z in xrange(data.xy_vect_num):
	    if z == 0:
		    data.mezisoucet = data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    else:
		    data.mezisoucet = data.mezisoucet + data.dipY_comps_func[z] * data.dipY_jw_comps_func[z]
	    
    
    #return data.dip_comps_func * data.dip_jw_comps_hess + data.csa1_comps_func * data.csa1_jw_comps_hess + data.csa2_comps_func * data.csa2_jw_comps_hess + data.csaC_comps_func * data.csaC_jw_comps_hess + sum(data.dipY_comps_func * data.dipY_jw_comps_hess, axis=0) 
    return data.dip_comps_func * data.dip_jw_comps_hess + data.csa1_comps_func * data.csa1_jw_comps_hess + data.csa2_comps_func * data.csa2_jw_comps_hess + data.csaC_comps_func * data.csaC_jw_comps_hess + data.mezisoucet


# d2Ri/dJ(w).dCSA
def func_d2ri_djwdcsa_prime(data):
    """Spectral density parameter / CSA Hessian.

     d2R1()
    --------  =  csa_const_grad . csa_Jw_R1_grad
    dJw.dcsa

     d2R2()      csa_const_grad
    --------  =  -------------- . csa_Jw_R2_grad
    dJw.dcsa           6

    d2sigma_noe()
    -------------  =  0
      dJw.dcsa

     d2Ri()
    --------  =  csa_comps_grad . csa_jw_comps_grad
    dJw.dcsa
    """

    return data.csa_comps_grad * data.csa_jw_comps_grad


# d2Ri/dJ(w).dr
def func_d2ri_djwdr_prime(data):
    """Spectral density parameter / bond length Hessian.

    d2R1()
    ------  =  dip_const_grad . dip_Jw_R1_grad
    dJw.dr

    d2R2()     dip_const_grad
    ------  =  -------------- . dip_Jw_R2_grad
    dJw.dr           2

    d2sigma_noe()
    -------------  =  dip_const_grad . dip_Jw_sigma_noe_grad
       dJw.dr

    d2Ri()
    ------  =  dip_comps_grad . dip_jw_comps_grad
    dJw.dr
    """

    return data.dip_comps_grad * data.dip_jw_comps_grad


# d2Ri/dCSA^2
def func_d2ri_dcsa2_prime(data):
    """CSA / CSA Hessian.

     d2R1()
    -------  =  csa_const_hess  . csa_Jw_R1_func
    dcsa**2

     d2R2()     csa_const_hess
    -------  =  -------------- . csa_Jw_R2_func
    dcsa**2           6

    d2sigma_noe()
    -------------  =  0
       dcsa**2

     d2Ri()
    -------  =  csa_comps_hess  . csa_jw_comps_func
    dcsa**2
    """

    return data.csa_comps_hess * data.csa_jw_comps_func


# d2Ri/dr^2
def func_d2ri_dr2_prime(data):
    """Bond length / bond length Hessian.

    d2R1()
    ------  =  dip_const_hess . dip_Jw_R1_func
    dr**2

    d2R2()     dip_const_hess
    ------  =  -------------- . dip_Jw_R2_func
    dr**2            2

    d2sigma_noe()
    -------------  =  dip_const_hess . dip_Jw_sigma_noe_func
        dr**2

    d2Ri()
    ------  =  dip_comps_hess . dip_jw_comps_func
    dr**2
    """

    return data.dip_comps_hess * data.dip_jw_comps_func
