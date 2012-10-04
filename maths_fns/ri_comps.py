###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################


# Constant formulae
# =================
#
#    Dipolar constants
#    =================
#                           1   / mu0  \ 2  (gH.gN.h_bar)**2
#        dip_const_func  =  - . | ---- |  . ----------------
#                           4   \ 4.pi /         <r**6>
#
#
#                             3   / mu0  \ 2  (gH.gN.h_bar)**2
#        dip_const_grad  =  - - . | ---- |  . ----------------
#                             2   \ 4.pi /         <r**7>
#
#
#                           21   / mu0  \ 2  (gH.gN.h_bar)**2
#        dip_const_hess  =  -- . | ---- |  . ----------------
#                           2    \ 4.pi /         <r**8>
#
#
#    CSA constants
#    =============
#                           (wN.csa)**2
#        csa_const_func  =  -----------
#                                3
#
#                           2.wN**2.csa
#        csa_const_grad  =  -----------
#                                3
#
#                           2.wN**2
#        csa_const_hess  =  -------
#                              3
#
#    Rex constants
#    =============
#        rex_const_func  =  rhoex * (2.pi.wH)**2
#
#        rex_const_grad  =  (2.pi.wH)**2
#
#        rex_const_hess  =  0
#
#
# Component formulae
# ==================
#
#    R1 components
#    =============
#
#        Dipolar components
#        ==================
#
#            dip_R1_func     =  dip_const_func
#
#            dip_R1_grad     =  dip_const_grad
#
#            dip_R1_hess     =  dip_const_hess
#
#
#        Dipolar spectral density components
#        ===================================
#
#            dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)
#
#                               dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
#            dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
#                                  dJw             dJw              dJw
#
#                               d2J(wH-wN)          d2J(wN)          d2J(wH+wN)
#            dip_Jw_R1_hess  =  ----------  +  3 . ---------  +  6 . ----------
#                               dJwi.dJwj          dJwi.dJwj         dJwi.dJwj
#
#
#        CSA components
#        ==============
#
#            csa_R1_func     =  csa_const_func
#
#            csa_R1_grad     =  csa_const_grad
#
#            csa_R1_hess     =  csa_const_hess
#
#
#        CSA spectral density components
#        ===============================
#
#            csa_Jw_R1_func  =  J(wN)
#
#                               dJ(wN)
#            csa_Jw_R1_grad  =  ------
#                                dJw
#
#                                d2J(wN)
#            csa_Jw_R1_hess  =  ---------
#                               dJwi.dJwj
#
#
#        Rex components
#        ==============
#
#            rex_R1_func     =  0
#
#            rex_R1_grad     =  0
#
#            rex_R1_hess     =  0
#
#
#    R2 components
#    =============
#
#        Dipolar components
#        ==================
#
#            dip_R2_func     =  dip_const_func / 2
#
#            dip_R2_grad     =  dip_const_grad / 2
#
#            dip_R2_hess     =  dip_const_hess / 2
#
#
#        Dipolar spectral density components
#        ===================================
#
#            dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)
#
#                                   dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
#            dip_Jw_R2_grad  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
#                                    dJw         dJw             dJw            dJw              dJw
#
#                                     d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN)
#            dip_Jw_R2_hess  =  4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ----------
#                                   dJwi.dJwj     dJwi.dJwj          dJwi.dJwj         dJwi.dJwj         dJwi.dJwj
#
#
#        CSA components
#        ==============
#
#            csa_R2_func     =  csa_const_func / 6
#
#            csa_R2_grad     =  csa_const_grad / 6
#
#            csa_R2_hess     =  csa_const_hess / 6
#
#
#        CSA spectral density components
#        ===============================
#
#            csa_Jw_R2_func  =  4J(0) + 3J(wN)
#
#                                   dJ(0)         dJ(wN)
#            csa_Jw_R2_grad  =  4 . -----  +  3 . ------
#                                    dJw           dJw
#
#                                     d2J(0)           d2J(wN)
#            csa_Jw_R2_hess  =  4 . ---------  +  3 . ---------
#                                   dJwi.dJwj         dJwi.dJwj
#
#
#        Rex components
#        ==============
#
#            rex_R2_func     =  rex_const_func
#
#            rex_R2_grad     =  rex_const_grad
#
#            rex_R2_hess     =  0
#
#
#    sigma_noe components
#    ====================
#
#        Dipolar components
#        ==================
#
#            dip_sigma_noe_func      =  dip_const_func
#
#            dip_sigma_noe_grad      =  dip_const_grad
#
#            dip_sigma_noe_hess      =  dip_const_hess
#
#
#        Dipolar spectral density components
#        ===================================
#
#            dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)
#
#                                          dJ(wH+wN)     dJ(wH-wN)
#            dip_Jw_sigma_noe_grad  =  6 . ---------  -  ---------
#                                             dJw           dJw
#
#                                          d2J(wH+wN)     d2J(wH-wN)
#            dip_Jw_sigma_noe_hess  =  6 . ----------  -  ----------
#                                          dJwi.dJwj      dJwi.dJwj
#
#
#        CSA components
#        ==============
#
#            csa_sigma_noe_func      =  0
#
#            csa_sigma_noe_grad      =  0
#
#            csa_sigma_noe_hess      =  0
#
#
#        CSA spectral density components
#        ===============================
#
#            csa_Jw_sigma_noe_func   =  0
#
#            csa_Jw_sigma_noe_grad   =  0
#
#            csa_Jw_sigma_noe_hess   =  0
#
#
#        Rex components
#        ==============
#
#            rex_sigma_noe_func      =  0
#
#            rex_sigma_noe_grad      =  0
#
#            rex_sigma_noe_hess      =  0
#

# Python module imports.
from math import pi


# The main functions for the calculation of the Ri components.
##############################################################

# These functions are duplicated many times for all combinations of Rex, bond length, and CSA as model parameters
# to make the code more efficient.

# Ri.
def ri_comps(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar J(w) components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - Dipolar constant components.
        - CSA constant components.
    """

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])


# Ri (Rex).
def ri_comps_rex(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar J(w) components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - Dipolar constant components.
        - CSA constant components.
    """

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])

        # Rex components
        if data.create_rex_func[i]:
            data.rex_comps_func[i] = data.create_rex_func[i](params[data.rex_i], data.frq[data.remap_table[i]])


# Ri (Bond length).
def ri_comps_r(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - CSA constant components.
    """

    # Dipolar constant function value.
    comp_dip_const_func(data, params[data.r_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_func[i] = data.dip_const_func
        if data.create_dip_func[i]:
            data.dip_comps_func[i] = data.create_dip_func[i](data.dip_const_func)

        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])


# Ri (CSA).
def ri_comps_csa(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - Dipolar constant components.
    """

    # CSA constant function value.
    comp_csa_const_func(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_func[i]:
            data.csa_comps_func[i] = data.create_csa_func[i](data.csa_const_func[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])


# Ri (Bond length, CSA).
def ri_comps_r_csa(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
    """

    # Dipolar constant function value.
    comp_dip_const_func(data, params[data.r_i])

    # CSA constant function value.
    comp_csa_const_func(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_func[i] = data.dip_const_func
        if data.create_dip_func[i]:
            data.dip_comps_func[i] = data.create_dip_func[i](data.dip_const_func)

        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_func[i]:
            data.csa_comps_func[i] = data.create_csa_func[i](data.csa_const_func[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])


# Ri (Bond length, Rex).
def ri_comps_r_rex(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - CSA constant components.
    """

    # Dipolar constant function value.
    comp_dip_const_func(data, params[data.r_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_func[i] = data.dip_const_func
        if data.create_dip_func[i]:
            data.dip_comps_func[i] = data.create_dip_func[i](data.dip_const_func)

        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])

        # Rex components
        if data.create_rex_func[i]:
            data.rex_comps_func[i] = data.create_rex_func[i](params[data.rex_i], data.frq[data.remap_table[i]])


# Ri (CSA, Rex).
def ri_comps_csa_rex(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - Dipolar constant components.
    """

    # CSA constant function value.
    comp_csa_const_func(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_func[i]:
            data.csa_comps_func[i] = data.create_csa_func[i](data.csa_const_func[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])

        # Rex components
        if data.create_rex_func[i]:
            data.rex_comps_func[i] = data.create_rex_func[i](params[data.rex_i], data.frq[data.remap_table[i]])


# Ri (Bond length, CSA, Rex).
def ri_comps_r_csa_rex(data, params):
    """Calculate the ri function components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - None.
    """

    # Dipolar constant function value.
    comp_dip_const_func(data, params[data.r_i])

    # CSA constant function value.
    comp_csa_const_func(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_func[i] = data.dip_const_func
        if data.create_dip_func[i]:
            data.dip_comps_func[i] = data.create_dip_func[i](data.dip_const_func)

        # Dipolar J(w) components
        data.dip_jw_comps_func[i] = data.create_dip_jw_func[i](data.jw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_func[i]:
            data.csa_comps_func[i] = data.create_csa_func[i](data.csa_const_func[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_func[i]:
            data.csa_jw_comps_func[i] = data.create_csa_jw_func[i](data.jw, data.remap_table[i])

        # Rex components
        if data.create_rex_func[i]:
            data.rex_comps_func[i] = data.create_rex_func[i](params[data.rex_i], data.frq[data.remap_table[i]])


# R1 comps.
def r1_comps(data, i, params):
    """Calculate the r1 function components."""

    # Dipolar constant function value.
    if data.r_i:
        comp_dip_const_func(data, params[data.r_i])

    # CSA constant function value.
    if data.csa_i:
        comp_csa_const_func(data, params[data.csa_i])

    # Dipolar constant components.
    data.dip_comps_func[i] = data.dip_const_func

    # Dipolar J(w) components
    data.dip_jw_comps_func[i] = comp_r1_dip_jw(data.jw, data.remap_table[i])

    # CSA constant components.
    data.csa_comps_func[i] = data.csa_const_func[data.remap_table[i]]

    # CSA J(w) components.
    data.csa_jw_comps_func[i] = comp_r1_csa_jw(data.jw, data.remap_table[i])



# The main functions for the calculation of the dRi components.
###############################################################

# These functions are duplicated many times for all combinations of Rex, bond length, and CSA as model parameters
# to make the code more efficient.


# dRi.
def dri_comps(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar J(w) components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - Dipolar constant components.
        - CSA constant components.
    """

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])


# dRi (Rex).
def dri_comps_rex(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar J(w) components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - Dipolar constant components.
        - CSA constant components.
    """

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])

        # Rex components
        if data.create_rex_grad[i]:
            data.rex_comps_grad[i] = data.create_rex_grad[i](data.frq[data.remap_table[i]])


# dRi (Bond length).
def dri_comps_r(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - CSA constant components.
    """

    # Dipolar constant gradient value.
    comp_dip_const_grad(data, params[data.r_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_grad[i] = data.dip_const_grad
        if data.create_dip_grad[i]:
            data.dip_comps_grad[i] = data.create_dip_grad[i](data.dip_const_grad)

        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])


# dRi (CSA).
def dri_comps_csa(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - Dipolar constant components.
    """

    # CSA constant gradient value.
    comp_csa_const_grad(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_grad[i]:
            data.csa_comps_grad[i] = data.create_csa_grad[i](data.csa_const_grad[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])


# dRi (Bond length, CSA).
def dri_comps_r_csa(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
    """

    # Dipolar constant gradient value.
    comp_dip_const_grad(data, params[data.r_i])

    # CSA constant gradient value.
    comp_csa_const_grad(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_grad[i] = data.dip_const_grad
        if data.create_dip_grad[i]:
            data.dip_comps_grad[i] = data.create_dip_grad[i](data.dip_const_grad)

        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_grad[i]:
            data.csa_comps_grad[i] = data.create_csa_grad[i](data.csa_const_grad[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])


# dRi (Bond length, Rex).
def dri_comps_r_rex(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - CSA constant components.
    """

    # Dipolar constant gradient value.
    comp_dip_const_grad(data, params[data.r_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_grad[i] = data.dip_const_grad
        if data.create_dip_grad[i]:
            data.dip_comps_grad[i] = data.create_dip_grad[i](data.dip_const_grad)

        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])

        # Rex components
        if data.create_rex_grad[i]:
            data.rex_comps_grad[i] = data.create_rex_grad[i](data.frq[data.remap_table[i]])


# dRi (CSA, Rex).
def dri_comps_csa_rex(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - Dipolar constant components.
    """

    # CSA constant gradient value.
    comp_csa_const_grad(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_grad[i]:
            data.csa_comps_grad[i] = data.create_csa_grad[i](data.csa_const_grad[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])

        # Rex components
        if data.create_rex_grad[i]:
            data.rex_comps_grad[i] = data.create_rex_grad[i](data.frq[data.remap_table[i]])


# dRi (Bond length, CSA, Rex).
def dri_comps_r_csa_rex(data, params):
    """Calculate the dri gradient components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
        - Rex constant components.
    Pre-calculated:
        - None.
    """

    # Dipolar constant gradient value.
    comp_dip_const_grad(data, params[data.r_i])

    # CSA constant gradient value.
    comp_csa_const_grad(data, params[data.csa_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_grad[i] = data.dip_const_grad
        if data.create_dip_grad[i]:
            data.dip_comps_grad[i] = data.create_dip_grad[i](data.dip_const_grad)

        # Dipolar J(w) components
        data.dip_jw_comps_grad[i] = data.create_dip_jw_grad[i](data.djw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_grad[i]:
            data.csa_comps_grad[i] = data.create_csa_grad[i](data.csa_const_grad[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_grad[i]:
            data.csa_jw_comps_grad[i] = data.create_csa_jw_grad[i](data.djw, data.remap_table[i])

        # Rex components
        if data.create_rex_grad[i]:
            data.rex_comps_grad[i] = data.create_rex_grad[i](data.frq[data.remap_table[i]])


# dR1 comps.
def dr1_comps(data, i, params):
    """Calculate the dr1 gradient components."""

    # Dipolar constant gradient value.
    if data.r_i:
        comp_dip_const_grad(data, params[data.r_i])

    # CSA constant gradient value.
    if data.csa_i:
        comp_csa_const_grad(data, params[data.csa_i])

    # Dipolar constant components.
    data.dip_comps_grad[i] = data.dip_const_grad

    # Dipolar J(w) components
    data.dip_jw_comps_grad[i] = comp_r1_dip_jw(data.djw, data.remap_table[i])

    # CSA constant components.
    data.csa_comps_grad[i] = data.csa_const_grad[data.remap_table[i]]

    # CSA J(w) components.
    data.csa_jw_comps_grad[i] = comp_r1_csa_jw(data.djw, data.remap_table[i])


# The main functions for the calculation of the d2Ri components.
################################################################

# These functions are duplicated many times for all combinations of Rex, bond length, and CSA as model parameters
# to make the code more efficient.


# d2Ri.
def d2ri_comps(data, params):
    """Calculate the d2ri Hessian components.

    Calculated:
        - Dipolar J(w) components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - Dipolar constant components.
        - CSA constant components.
    """

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_hess[i] = data.create_dip_jw_hess[i](data.d2jw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_hess[i]:
            data.csa_jw_comps_hess[i] = data.create_csa_jw_hess[i](data.d2jw, data.remap_table[i])


# d2Ri (Bond length).
def d2ri_comps_r(data, params):
    """Calculate the d2ri Hessian components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - CSA constant components.
    """

    # Dipolar constant Hessian value.
    comp_dip_const_hess(data, params[data.r_i])

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_hess[i] = data.dip_const_hess
        if data.create_dip_hess[i]:
            data.dip_comps_hess[i] = data.create_dip_hess[i](data.dip_const_hess)

        # Dipolar J(w) components
        data.dip_jw_comps_hess[i] = data.create_dip_jw_hess[i](data.d2jw, data.remap_table[i])

        # CSA J(w) components.
        if data.create_csa_jw_hess[i]:
            data.csa_jw_comps_hess[i] = data.create_csa_jw_hess[i](data.d2jw, data.remap_table[i])


# d2Ri (CSA).
def d2ri_comps_csa(data, params):
    """Calculate the d2ri Hessian components.

    Calculated:
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
        - Dipolar constant components.
    """

    # CSA constant Hessian value.
    comp_csa_const_hess(data, params)

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar J(w) components
        data.dip_jw_comps_hess[i] = data.create_dip_jw_hess[i](data.d2jw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_hess[i]:
            data.csa_comps_hess[i] = data.create_csa_hess[i](data.csa_const_hess[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_hess[i]:
            data.csa_jw_comps_hess[i] = data.create_csa_jw_hess[i](data.d2jw, data.remap_table[i])


# d2Ri (Bond length, CSA).
def d2ri_comps_r_csa(data, params):
    """Calculate the d2ri Hessian components.

    Calculated:
        - Dipolar constant components.
        - Dipolar J(w) components.
        - CSA constant components.
        - CSA J(w) components.
    Pre-calculated:
        - Rex constant components.
    """

    # Dipolar constant Hessian value.
    comp_dip_const_hess(data, params[data.r_i])

    # CSA constant Hessian value.
    comp_csa_const_hess(data, params)

    # Loop over the relaxation values.
    for i in range(data.num_ri):
        # Dipolar constant components.
        data.dip_comps_hess[i] = data.dip_const_hess
        if data.create_dip_hess[i]:
            data.dip_comps_hess[i] = data.create_dip_hess[i](data.dip_const_hess)

        # Dipolar J(w) components
        data.dip_jw_comps_hess[i] = data.create_dip_jw_hess[i](data.d2jw, data.remap_table[i])

        # CSA constant components.
        if data.create_csa_hess[i]:
            data.csa_comps_hess[i] = data.create_csa_hess[i](data.csa_const_hess[data.remap_table[i]])

        # CSA J(w) components.
        if data.create_csa_jw_hess[i]:
            data.csa_jw_comps_hess[i] = data.create_csa_jw_hess[i](data.d2jw, data.remap_table[i])


# d2R1 comps.
def d2r1_comps(data, i, params):
    """Calculate the d2ri Hessian components."""

    # Dipolar constant gradient value.
    if data.r_i:
        comp_dip_const_hess(data, params[data.r_i])

    # CSA constant gradient value.
    if data.csa_i:
        comp_csa_const_hess(data, params)

    # Dipolar constant components.
    data.dip_comps_hess[i] = data.dip_const_hess

    # Dipolar J(w) components
    data.dip_jw_comps_hess[i] = comp_r1_dip_jw(data.d2jw, data.remap_table[i])

    # CSA constant components.
    data.csa_comps_hess[i] = data.csa_const_hess[data.remap_table[i]]

    # CSA J(w) components.
    data.csa_jw_comps_hess[i] = comp_r1_csa_jw(data.d2jw, data.remap_table[i])



# Functions to calculate the invariant part of the dipolar and CSA constants.
#############################################################################


# Dipolar.
def calc_fixed_dip(data):
    """Calculate the fixed component of the dipolar constant.

    The equation is::

                            / mu0  \ 2
        dip_const_fixed  =  | ---- |  . (gH.gN.h_bar)**2
                            \ 4.pi /
    """

    data.dip_const_fixed = ((data.mu0 / (4.0*pi)) * data.h_bar * data.gh * data.gx) ** 2


# CSA.
def calc_fixed_csa(data):
    """Calculate the fixed component of the CSA constants.

    The equation is::

                            wN**2
        csa_const_fixed  =  -----
                              3
    """

    for j in range(data.num_frq):
        data.csa_const_fixed[j] = data.frq_sqrd_list[j, 1] / 3.0



# Functions to calculate the dipolar constant values, gradients, and Hessians.
##############################################################################


# Function.
def comp_dip_const_func(data, bond_length):
    """Calculate the dipolar constant.

    Dipolar constant
    ================

    The equation is::

                           1   / mu0  \ 2  (gH.gN.h_bar)**2
        dip_const_func  =  - . | ---- |  . ----------------
                           4   \ 4.pi /         <r**6>
    """

    if bond_length == 0.0:
        data.dip_const_func = 1e99
    else:
        data.dip_const_func = 0.25 * data.dip_const_fixed * bond_length**-6


# Gradient.
def comp_dip_const_grad(data, bond_length):
    """Calculate the derivative of the dipolar constant.

    Dipolar constant gradient
    =========================

    The equation is::

                             3   / mu0  \ 2  (gH.gN.h_bar)**2
        dip_const_grad  =  - - . | ---- |  . ----------------
                             2   \ 4.pi /         <r**7>
    """

    if bond_length == 0.0:
        data.dip_const_grad = 1e99
    else:
        data.dip_const_grad = -1.5 * data.dip_const_fixed * bond_length**-7


# Hessian.
def comp_dip_const_hess(data, bond_length):
    """Calculate the second derivative of the dipolar constant.

    Dipolar constant Hessian
    ========================

    The equation is::

                           21   / mu0  \ 2  (gH.gN.h_bar)**2
        dip_const_hess  =  -- . | ---- |  . ----------------
                           2    \ 4.pi /         <r**8>
    """

    if bond_length == 0.0:
        data.dip_const_hess = 1e99
    else:
        data.dip_const_hess = 10.5 * data.dip_const_fixed * bond_length**-8



# Functions to calculate the CSA constant values, gradients, and Hessians.
##########################################################################


# Function.
def comp_csa_const_func(data, csa):
    """Calculate the CSA constant.

    CSA constant
    ============

    The equation is::

                           (wN.csa)**2
        csa_const_func  =  -----------
                                3
    """

    for i in range(data.num_frq):
        data.csa_const_func[i] = data.csa_const_fixed[i] * csa**2


# Gradient.
def comp_csa_const_grad(data, csa):
    """Calculate the derivative of the CSA constant.

    CSA constant gradient
    =====================

    The equation is::

                           2.wN**2.csa
        csa_const_grad  =  -----------
                                3
    """

    for i in range(data.num_frq):
        data.csa_const_grad[i] = 2.0 * data.csa_const_fixed[i] * csa


# Hessian.
def comp_csa_const_hess(data, params):
    """Calculate the second derivative of the CSA constant.

    CSA constant Hessian
    ====================

    The equation is::

                           2.wN**2
        csa_const_hess  =  -------
                              3
    """

    for i in range(data.num_frq):
        data.csa_const_hess[i] = 2.0 * data.csa_const_fixed[i]



# Functions to calculate the Rex constant values and gradients.
###############################################################


# Function.
def comp_rex_const_func(rhoex, frq):
    """Calculate the Rex value.

    Rex constant
    ============

    The equation is::

        rex_const_func  =  rhoex * wH**2
    """

    return rhoex * (2.0 * pi * frq) ** 2


# Gradient.
def comp_rex_const_grad(frq):
    """Calculate the Rex gradient.

    Rex gradient
    ============

    The equation is::

        rex_const_grad  =  wH**2
    """

    return (2.0 * pi * frq) ** 2



# Functions to calculate the dipolar constant components.
#########################################################


def comp_r2_dip_const(dip_const_data):
    """Calculate the R1 dipolar constant components.

    The equations are::

        dip_const_func / 2

        dip_const_grad / 2

        dip_const_hess / 2
    """

    return dip_const_data / 2.0



# Functions to calculate the CSA constant components.
#####################################################

# sigma_noe has no CSA components!

def comp_r1_csa_const(csa_const_data):
    """Calculate the R1 CSA constant components.

    The equations are::

        csa_const_func

        csa_const_grad

        csa_const_hess
    """

    return csa_const_data


def comp_r2_csa_const(csa_const_data):
    """Calculate the R2 CSA constant. components

    The equations are::

        csa_const_func / 6

        csa_const_grad / 6

        csa_const_hess / 6
    """

    return csa_const_data / 6.0



# Functions to calculate the dipolar J(w) components.
#####################################################


# R1.
def comp_r1_dip_jw(jw_data, frq_num):
    """Calculate the R1 dipolar J(w) components.

    The equations are::

        dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

                           dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
        dip_Jw_R1_grad  =  ---------  +  3 . ------  +  6 . ---------
                              dJw             dJw              dJw

                           d2J(wH-wN)          d2J(wN)          d2J(wH+wN)
        dip_Jw_R1_hess  =  ----------  +  3 . ---------  +  6 . ----------
                           dJwi.dJwj          dJwi.dJwj         dJwi.dJwj
    """

    return jw_data[frq_num, 2] + 3.0*jw_data[frq_num, 1] + 6.0*jw_data[frq_num, 4]


# R2.
def comp_r2_dip_jw(jw_data, frq_num):
    """Calculate the R2 dipolar J(w) components.

    The equations are::

        dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

                               dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
        dip_Jw_R2_grad  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
                                dJw         dJw             dJw            dJw              dJw

                                 d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN)
        dip_Jw_R2_hess  =  4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ----------
                               dJwi.dJwj     dJwi.dJwj          dJwi.dJwj         dJwi.dJwj         dJwi.dJwj
    """

    return 4.0*jw_data[frq_num, 0] + jw_data[frq_num, 2] + 3.0*jw_data[frq_num, 1] + 6.0*jw_data[frq_num, 3] + 6.0*jw_data[frq_num, 4]


# sigma_noe.
def comp_sigma_noe_dip_jw(jw_data, frq_num):
    """Calculate the sigma_noe dipolar J(w) components.

    The equations are::

        dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)

                                      dJ(wH+wN)     dJ(wH-wN)
        dip_Jw_sigma_noe_grad  =  6 . ---------  -  ---------
                                         dJw           dJw

                                      d2J(wH+wN)     d2J(wH-wN)
        dip_Jw_sigma_noe_hess  =  6 . ----------  -  ----------
                                      dJwi.dJwj      dJwi.dJwj
    """

    return 6.0*jw_data[frq_num, 4] - jw_data[frq_num, 2]



# Functions to calculate the CSA J(w) components.
#################################################

# sigma_noe has no CSA J(w) components!

# R1.
def comp_r1_csa_jw(jw_data, frq_num):
    """Calculate the R1 CSA J(w) components.

    The equations are::

        csa_Jw_R1_func  =  J(wN)

                           dJ(wN)
        csa_Jw_R1_grad  =  ------
                            dJw

                            d2J(wN)
        csa_Jw_R1_hess  =  ---------
                           dJwi.dJwj
    """

    return jw_data[frq_num, 1]


# R2.
def comp_r2_csa_jw(jw_data, frq_num):
    """Calculate the R1 CSA J(w) components.

    The equations are::

        csa_Jw_R2_func  =  4J(0) + 3J(wN)

                               dJ(0)         dJ(wN)
        csa_Jw_R2_grad  =  4 . -----  +  3 . ------
                                dJw           dJw

                                 d2J(0)           d2J(wN)
        csa_Jw_R2_hess  =  4 . ---------  +  3 . ---------
                               dJwi.dJwj         dJwi.dJwj
    """

    return 4.0*jw_data[frq_num, 0] + 3.0*jw_data[frq_num, 1]
