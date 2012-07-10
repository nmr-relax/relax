###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


# The transformed relaxation equations
# ====================================
#
#    Relaxation equations
#    ====================
#
#        R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func
#
#
#                 dip_const_func                      csa_const_func
#        R2()  =  -------------- . dip_Jw_R2_func  +  -------------- . csa_Jw_R2_func  +  rex_const_func
#                       2                                   6
#
#
#        sigma_noe()  =  dip_const_func . dip_Jw_sigma_noe_func
#
#
#        Ri  =  dip_comps_func . dip_jw_comps_func  +  csa_comps_func * csa_jw_comps_func  +  rex_comps_func
#
#
#
# The transformed relaxation gradients
# ====================================
#
#    Spectral density parameter
#    ==========================
#
#        dR1()
#        -----  =  dip_const_func . dip_Jw_R1_grad  +  csa_const_func . csa_Jw_R1_grad
#         dJw
#
#
#        dR2()     dip_const_func                      csa_const_func
#        -----  =  -------------- . dip_Jw_R2_grad  +  -------------- . csa_Jw_R2_grad
#         dJw            2                                   6
#
#
#        dsigma_noe()
#        ------------  = dip_const_func . dip_Jw_sigma_noe_grad
#            dJw
#
#
#        dRi()
#        -----  =  dip_comps_func . dip_jw_comps_grad  +  csa_comps_func . csa_jw_comps_grad
#         dJw
#
#
#    Chemical exchange
#    =================
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
#    ===========
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
#    ===
#
#        dR1()
#        -----  =  csa_const_grad . csa_Jw_R1_func
#        dcsa
#
#
#        dR2()     csa_const_grad
#        -----  =  -------------- . csa_Jw_R2_func
#        dcsa            6
#
#
#        dsigma_noe()
#        ------------  =  0
#            dcsa
#
#
#        dRi()
#        -----  =  csa_comps_grad . csa_jw_comps_func
#        dcsa
#
#
#
# The transformed relaxation Hessians
# ===================================
#
#    Spectral density parameter - Spectral density parameter
#    =======================================================
#
#          d2R1()
#        ---------  =  dip_const_func . dip_Jw_R1_hess  +  csa_const_func . csa_Jw_R1_hess
#        dJwi.dJwj
#
#
#          d2R2()      dip_const_func                      csa_const_func
#        ---------  =  -------------- . dip_Jw_R2_hess  +  -------------- . csa_Jw_R2_hess
#        dJwi.dJwj           2                                   6
#
#
#        d2sigma_noe()
#        -------------  =  dip_const_func . dip_Jw_sigma_noe_hess
#          dJwi.dJwj
#
#
#          d2Ri()
#        ---------  =  dip_comps_func . dip_jw_comps_hess  +  csa_comps_func . csa_jw_comps_hess
#        dJwi.dJwj
#
#
#    Spectral density parameter - Chemical exchange
#    ==============================================
#
#         d2R1()               d2R2()              d2sigma_noe()
#        --------  =  0   ,   --------  =  0   ,   -------------  =  0
#        dJw.dRex             dJw.dRex               dJw.dRex
#
#
#    Spectral density parameter - CSA
#    ================================
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
#    ========================================
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
#    =====================================
#
#         d2R1()              d2R2()             d2sigma_noe()
#        -------  =  0   ,   -------  =  0   ,   -------------  =  0
#        dRex**2             dRex**2                dRex**2
#
#
#    Chemical exchange - CSA
#    =======================
#
#          d2R1()                d2R2()              d2sigma_noe()
#        ---------  =  0   ,   ---------  =  0   ,   -------------  =  0
#        dRex.dcsa             dRex.dcsa               dRex.dcsa
#
#
#    Chemical exchange - Bond length
#    ===============================
#
#         d2R1()              d2R2()             d2sigma_noe()
#        -------  =  0   ,   -------  =  0   ,   -------------  =  0
#        dRex.dr             dRex.dr                dRex.dr
#
#
#    CSA - CSA
#    =========
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
#    =================
#
#         d2R1()              d2R2()             d2sigma_noe()
#        -------  =  0   ,   -------  =  0   ,   -------------  =  0
#        dcsa.dr             dcsa.dr                dcsa.dr
#
#
#    Bond length - Bond length
#    =========================
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

    return data.dip_comps_func * data.dip_jw_comps_func + data.csa_comps_func * data.csa_jw_comps_func


def func_ri_prime_rex(data):
    """Calculate the transformed relaxation values."""

    return data.dip_comps_func * data.dip_jw_comps_func + data.csa_comps_func * data.csa_jw_comps_func + data.rex_comps_func


# Transformed relaxation gradients.
###################################

# dRi/dJ(w)
def func_dri_djw_prime(data):
    """Spectral density parameter derivatives."""

    return data.dip_comps_func * data.dip_jw_comps_grad + data.csa_comps_func * data.csa_jw_comps_grad


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

    The equations are::

          d2R1()
        ---------  =  dip_const_func . dip_Jw_R1_hess  +  csa_const_func . csa_Jw_R1_hess
        dJwi.dJwj

          d2R2()      dip_const_func                      csa_const_func
        ---------  =  -------------- . dip_Jw_R2_hess  +  -------------- . csa_Jw_R2_hess
        dJwi.dJwj           2                                   6

        d2sigma_noe()
        -------------  =  dip_const_func . dip_Jw_sigma_noe_hess
          dJwi.dJwj

          d2Ri()
        ---------  =  dip_comps_func . dip_jw_comps_hess  +  csa_comps_func . csa_jw_comps_hess
        dJwi.dJwj
    """

    return data.dip_comps_func * data.dip_jw_comps_hess + data.csa_comps_func * data.csa_jw_comps_hess


# d2Ri/dJ(w).dCSA
def func_d2ri_djwdcsa_prime(data):
    """Spectral density parameter / CSA Hessian.

    The equations are::

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

    The equations are::

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

    The equations are::

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

    The equations are::

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
