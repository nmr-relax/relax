###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Python module imports.
from datetime import date
from functools import partial
from operator import attrgetter, ne


# Module docstring.
"""Variables for the relaxation dispersion specific analysis."""


# Experiment types.
EXP_TYPE_CPMG_SQ = 'SQ CPMG'
EXP_TYPE_CPMG_DQ = 'DQ CPMG'
EXP_TYPE_CPMG_MQ = 'MQ CPMG'
EXP_TYPE_CPMG_ZQ = 'ZQ CPMG'
EXP_TYPE_CPMG_PROTON_SQ = '1H SQ CPMG'
EXP_TYPE_CPMG_PROTON_MQ = '1H MQ CPMG'
EXP_TYPE_CPMG_MMQ = 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ'
EXP_TYPE_NOREX = 'No Rex'
EXP_TYPE_NOREX_R1RHO = 'No Rex: R1rho off res'
EXP_TYPE_R1RHO = 'R1rho'
EXP_TYPE_R2EFF = 'R2eff/R1rho'

# Experiment type descriptions.
EXP_TYPE_DESC_CPMG_SQ = "the standard single quantum (SQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_DQ = "the double quantum (DQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_MQ = "the multiple quantum (MQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_ZQ = "the zero quantum (ZQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_PROTON_SQ = "the 1H single quantum (SQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_PROTON_MQ = "the 1H multiple quantum (MQ) CPMG-type experiment"
EXP_TYPE_DESC_R1RHO = "the R1rho-type experiment"


# The experiment type lists.
EXP_TYPE_LIST_CPMG = [EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]
"""The list of all dispersion experiment types for CPMG-type data."""

EXP_TYPE_LIST_R1RHO = [EXP_TYPE_R1RHO]
"""The list of all dispersion experiment types for R1rho-type data."""

EXP_TYPE_LIST = EXP_TYPE_LIST_CPMG + EXP_TYPE_LIST_R1RHO
"""The list of all dispersion experiment types."""


# Model equation types. Either analytic, silico or numeric.
EQ_ANALYTIC = 'analytic'
EQ_NUMERIC = 'numeric'
EQ_SILICO = 'silico'


# The model names, parameters, and descriptions.
MODEL_R2EFF = 'R2eff'
MODEL_DESC_R2EFF = "The model for determining the R2eff/R1rho values from peak intensities."
MODEL_PARAMS_R2EFF = ['r2eff', 'i0']    # The 'i0' parameter is only for the exponential curve-fitting.
# This year is fake. Just to get the order correct.
MODEL_YEAR_R2EFF = 1950
MODEL_EXP_TYPE_R2EFF = EXP_TYPE_R2EFF
MODEL_SITES_R2EFF = None
MODEL_EQ_R2EFF = EQ_ANALYTIC

MODEL_NOREX = 'No Rex'
MODEL_DESC_NOREX = "The model for no chemical exchange relaxation."
MODEL_PARAMS_NOREX = ['r2']
# This year is fake. Just to get the order correct.
MODEL_YEAR_NOREX = 1951
MODEL_EXP_TYPE_NOREX = EXP_TYPE_NOREX
MODEL_SITES_NOREX = 1
MODEL_EQ_NOREX = EQ_ANALYTIC

MODEL_NOREX_R1RHO = "No_Rex_R1rho_off_res"
MODEL_DESC_NOREX_R1RHO = "The model for no chemical exchange relaxation, for R1rho off resonance models."
MODEL_PARAMS_NOREX_R1RHO = ['r2']
# This year is fake. Just to get the order correct.
MODEL_YEAR_NOREX_R1RHO = 1952
MODEL_EXP_TYPE_NOREX_R1RHO = EXP_TYPE_NOREX_R1RHO
MODEL_SITES_NOREX_R1RHO = 1
MODEL_EQ_NOREX_R1RHO = EQ_ANALYTIC

MODEL_NOREX_R1RHO_FIT_R1 = "%s_fit_r1"%MODEL_NOREX_R1RHO
MODEL_DESC_NOREX_R1RHO_FIT_R1 = "The model for no chemical exchange relaxation, for R1rho off resonance models, where R1 is fitted."
MODEL_PARAMS_NOREX_R1RHO_FIT_R1 = ['r1_fit', 'r2']
# This year is fake. Just to get the order correct.
MODEL_YEAR_NOREX_R1RHO_FIT_R1 = 1953
MODEL_EXP_TYPE_NOREX_R1RHO_FIT_R1 = EXP_TYPE_NOREX_R1RHO
MODEL_SITES_NOREX_R1RHO_FIT_R1 = 1
MODEL_EQ_NOREX_R1RHO_FIT_R1 = EQ_ANALYTIC

MODEL_LM63 = 'LM63'
MODEL_DESC_LM63 = "The Luz and Meiboom (1963) 2-site fast exchange model for SQ-CPMG experiments."
MODEL_PARAMS_LM63 = ['r2', 'phi_ex', 'kex']
MODEL_YEAR_LM63 = 1963
MODEL_EXP_TYPE_LM63 = EXP_TYPE_CPMG_SQ
MODEL_SITES_LM63 = 2
MODEL_EQ_LM63 = EQ_ANALYTIC

MODEL_LM63_3SITE = 'LM63 3-site'
MODEL_DESC_LM63_3SITE = "The Luz and Meiboom (1963) 3-site fast exchange model for SQ-CPMG experiments."
MODEL_PARAMS_LM63_3SITE = ['r2', 'phi_ex_B', 'phi_ex_C', 'kB', 'kC']
MODEL_YEAR_LM63_3SITE = 1963
MODEL_EXP_TYPE_LM63_3SITE = EXP_TYPE_CPMG_SQ
MODEL_SITES_LM63_3SITE = 3
MODEL_EQ_LM63_3SITE = EQ_ANALYTIC

MODEL_CR72 = 'CR72'
MODEL_DESC_CR72 = "The reduced Carver and Richards (1972) 2-site model for all time scales for SQ-CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_CR72 = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_CR72 = 1972
MODEL_EXP_TYPE_CR72 = EXP_TYPE_CPMG_SQ
MODEL_SITES_CR72 = 2
MODEL_EQ_CR72 = EQ_ANALYTIC

MODEL_CR72_FULL = 'CR72 full'
MODEL_DESC_CR72_FULL = "The full Carver and Richards (1972) 2-site model for all time scales for SQ-CPMG experiments."
MODEL_PARAMS_CR72_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']
MODEL_YEAR_CR72_FULL = 1972
MODEL_EXP_TYPE_CR72_FULL = EXP_TYPE_CPMG_SQ
MODEL_SITES_CR72_FULL = 2
MODEL_EQ_CR72_FULL = EQ_ANALYTIC

MODEL_IT99 = 'IT99'
MODEL_DESC_IT99 = "The Ishima and Torchia (1999) 2-site CPMG model for all time scales for SQ-CPMG experiments, with skewed populations (pA >> pB)."
MODEL_PARAMS_IT99 = ['r2', 'pA', 'dw', 'tex']
MODEL_YEAR_IT99 = 1999
MODEL_EXP_TYPE_IT99 = EXP_TYPE_CPMG_SQ
MODEL_SITES_IT99 = 2
MODEL_EQ_IT99 = EQ_ANALYTIC

MODEL_TSMFK01 = 'TSMFK01'
MODEL_DESC_TSMFK01 = "The Tollinger et al. (2001) 2-site very-slow exchange model for SQ-CPMG experiments."
MODEL_PARAMS_TSMFK01 = ['r2a', 'dw', 'k_AB']
MODEL_YEAR_TSMFK01 = 2001
MODEL_EXP_TYPE_TSMFK01 = EXP_TYPE_CPMG_SQ
MODEL_SITES_TSMFK01 = 2
MODEL_EQ_TSMFK01 = EQ_ANALYTIC

MODEL_B14 = 'B14'
MODEL_DESC_B14 = "The Baldwin (2014) 2-site CPMG exact solution model for all time scales for SQ-CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_B14 = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_B14 = 2014
MODEL_EXP_TYPE_B14 = EXP_TYPE_CPMG_SQ
MODEL_SITES_B14 = 2
MODEL_EQ_B14 = EQ_ANALYTIC

MODEL_B14_FULL = 'B14 full'
MODEL_DESC_B14_FULL = "The Baldwin (2014) 2-site CPMG exact solution model for all time scales for SQ-CPMG experiments."
MODEL_PARAMS_B14_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']
MODEL_YEAR_B14_FULL = 2014
MODEL_EXP_TYPE_B14_FULL = EXP_TYPE_CPMG_SQ
MODEL_SITES_B14_FULL = 2
MODEL_EQ_B14_FULL = EQ_ANALYTIC

MODEL_M61 = 'M61'
MODEL_DESC_M61 = "The Meiboom (1961) on-resonance 2-site fast exchange model for R1rho-type experiments."
MODEL_PARAMS_M61 = ['r2', 'phi_ex', 'kex']
MODEL_YEAR_M61 = 1961
MODEL_EXP_TYPE_M61 = EXP_TYPE_R1RHO
MODEL_SITES_M61 = 2
MODEL_EQ_M61 = EQ_ANALYTIC

MODEL_M61B = 'M61 skew'
MODEL_DESC_M61B = "The Meiboom (1961) on-resonance 2-site model for R1rho-type experiments, with skewed populations (pA >> pB)."
MODEL_PARAMS_M61B = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_M61B = 1961
MODEL_EXP_TYPE_M61B = EXP_TYPE_R1RHO
MODEL_SITES_M61B = 2
MODEL_EQ_M61B = EQ_ANALYTIC

MODEL_DPL94 = 'DPL94'
"""The R1rho 2-site fast exchange model of Davis, Perlman and London (1994)."""
MODEL_DESC_DPL94 = "The Davis, Perlman and London (1994) extension of the Meiboom (1961) model for off-resonance data."
MODEL_PARAMS_DPL94 = ['r2', 'phi_ex', 'kex']
MODEL_YEAR_DPL94 = 1994
MODEL_EXP_TYPE_DPL94 = EXP_TYPE_R1RHO
MODEL_SITES_DPL94 = 2
MODEL_EQ_DPL94 = EQ_ANALYTIC

MODEL_DPL94_FIT_R1 = "%s_fit_r1"%MODEL_DPL94
"""The R1rho 2-site fast exchange model of Davis, Perlman and London (1994), where R1 is fitted."""
MODEL_DESC_DPL94_FIT_R1 = "The Davis, Perlman and London (1994) extension of the Meiboom (1961) model for off-resonance data, where R1 is fitted."
MODEL_PARAMS_DPL94_FIT_R1 = ['r1_fit', 'r2', 'phi_ex', 'kex']
MODEL_YEAR_DPL94_FIT_R1 = 1994
MODEL_EXP_TYPE_DPL94_FIT_R1 = EXP_TYPE_R1RHO
MODEL_SITES_DPL94_FIT_R1 = 2
MODEL_EQ_DPL94_FIT_R1 = EQ_ANALYTIC

MODEL_TP02 = 'TP02'
MODEL_DESC_TP02 = "The Trott and Palmer (2002) off-resonance 2-site model for R1rho-type experiments."
MODEL_PARAMS_TP02 = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_TP02 = 2002
MODEL_EXP_TYPE_TP02 = EXP_TYPE_R1RHO
MODEL_SITES_TP02 = 2
MODEL_EQ_TP02 = EQ_ANALYTIC

MODEL_TP02_FIT_R1 = "%s_fit_r1"%MODEL_TP02
MODEL_DESC_TP02_FIT_R1 = "The Trott and Palmer (2002) off-resonance 2-site model for R1rho-type experiments, where R1 is fitted."
MODEL_PARAMS_TP02_FIT_R1 = ['r1_fit', 'r2', 'pA', 'dw', 'kex']
MODEL_YEAR_TP02_FIT_R1 = 2002
MODEL_EXP_TYPE_TP02_FIT_R1 = EXP_TYPE_R1RHO
MODEL_SITES_TP02_FIT_R1 = 2
MODEL_EQ_TP02_FIT_R1 = EQ_ANALYTIC

MODEL_TAP03 = 'TAP03'
MODEL_DESC_TAP03 = "The Trott, Abergel and Palmer (2003) off-resonance 2-site model for R1rho-type experiments."
MODEL_PARAMS_TAP03 = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_TAP03 = 2003
MODEL_EXP_TYPE_TAP03 = EXP_TYPE_R1RHO
MODEL_SITES_TAP03 = 2
MODEL_EQ_TAP03 = EQ_ANALYTIC

MODEL_TAP03_FIT_R1 = "%s_fit_r1"%MODEL_TAP03
MODEL_DESC_TAP03_FIT_R1 = "The Trott, Abergel and Palmer (2003) off-resonance 2-site model for R1rho-type experiments, where R1 is fitted."
MODEL_PARAMS_TAP03_FIT_R1 = ['r1_fit', 'r2', 'pA', 'dw', 'kex']
MODEL_YEAR_TAP03_FIT_R1 = 2003
MODEL_EXP_TYPE_TAP03_FIT_R1 = EXP_TYPE_R1RHO
MODEL_SITES_TAP03_FIT_R1 = 2
MODEL_EQ_TAP03_FIT_R1 = EQ_ANALYTIC

MODEL_MP05 = 'MP05'
"""The R1rho 2-site off-resonance exchange model of Miloushev and Palmer (2005)."""
MODEL_DESC_MP05 = "The Miloushev and Palmer (2005) off-resonance 2-site model for R1rho-type experiments."
MODEL_PARAMS_MP05 = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_MP05 = 2005
MODEL_EXP_TYPE_MP05 = EXP_TYPE_R1RHO
MODEL_SITES_MP05 = 2
MODEL_EQ_MP05 = EQ_ANALYTIC

MODEL_MP05_FIT_R1 = "%s_fit_r1"%MODEL_MP05
"""The R1rho 2-site off-resonance exchange model of Miloushev and Palmer (2005)."""
MODEL_DESC_MP05_FIT_R1 = "The Miloushev and Palmer (2005) off-resonance 2-site model for R1rho-type experiments, where R1 is fitted."
MODEL_PARAMS_MP05_FIT_R1 = ['r1_fit', 'r2', 'pA', 'dw', 'kex']
MODEL_YEAR_MP05_FIT_R1 = 2005
MODEL_EXP_TYPE_MP05_FIT_R1 = EXP_TYPE_R1RHO
MODEL_SITES_MP05_FIT_R1 = 2
MODEL_EQ_MP05_FIT_R1 = EQ_ANALYTIC


# The Numerical model names.
MODEL_NS_CPMG_2SITE_3D = 'NS CPMG 2-site 3D'
MODEL_DESC_NS_CPMG_2SITE_3D = "The reduced numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for SQ CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_CPMG_2SITE_3D = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_CPMG_2SITE_3D = 2004
MODEL_EXP_TYPE_NS_CPMG_2SITE_3D = EXP_TYPE_CPMG_SQ
MODEL_SITES_NS_CPMG_2SITE_3D = 2
MODEL_EQ_NS_CPMG_2SITE_3D = EQ_NUMERIC

MODEL_NS_CPMG_2SITE_3D_FULL = 'NS CPMG 2-site 3D full'
MODEL_DESC_NS_CPMG_2SITE_3D_FULL = "The full numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for SQ CPMG experiments."
MODEL_PARAMS_NS_CPMG_2SITE_3D_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_CPMG_2SITE_3D_FULL = 2004
MODEL_EXP_TYPE_NS_CPMG_2SITE_3D_FULL = EXP_TYPE_CPMG_SQ
MODEL_SITES_NS_CPMG_2SITE_3D_FULL = 2
MODEL_EQ_NS_CPMG_2SITE_3D_FULL = EQ_NUMERIC

MODEL_NS_CPMG_2SITE_STAR = 'NS CPMG 2-site star'
MODEL_DESC_NS_CPMG_2SITE_STAR = "The numerical reduced solution for the 2-site Bloch-McConnell equations using complex conjugate matrices for SQ CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_CPMG_2SITE_STAR = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_CPMG_2SITE_STAR = 2004
MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR = EXP_TYPE_CPMG_SQ
MODEL_SITES_NS_CPMG_2SITE_STAR = 2
MODEL_EQ_NS_CPMG_2SITE_STAR = EQ_NUMERIC

MODEL_NS_CPMG_2SITE_STAR_FULL = 'NS CPMG 2-site star full'
MODEL_DESC_NS_CPMG_2SITE_STAR_FULL = "The full numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices for SQ CPMG experiments."
MODEL_PARAMS_NS_CPMG_2SITE_STAR_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_CPMG_2SITE_STAR_FULL = 2004
MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR_FULL = EXP_TYPE_CPMG_SQ
MODEL_SITES_NS_CPMG_2SITE_STAR_FULL = 2
MODEL_EQ_NS_CPMG_2SITE_STAR_FULL = EQ_NUMERIC

MODEL_NS_CPMG_2SITE_EXPANDED = 'NS CPMG 2-site expanded'
MODEL_DESC_NS_CPMG_2SITE_EXPANDED = "The numerical solution for the 2-site Bloch-McConnell equations for SQ CPMG experiments, expanded using Maple by Nikolai Skrynnikov."
MODEL_PARAMS_NS_CPMG_2SITE_EXPANDED = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_CPMG_2SITE_EXPANDED = 2001
MODEL_EXP_TYPE_NS_CPMG_2SITE_EXPANDED = EXP_TYPE_CPMG_SQ
MODEL_SITES_NS_CPMG_2SITE_EXPANDED = 2
MODEL_EQ_NS_CPMG_2SITE_EXPANDED = EQ_SILICO

MODEL_NS_R1RHO_2SITE = 'NS R1rho 2-site'
MODEL_DESC_NS_R1RHO_2SITE = "The reduced numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_R1RHO_2SITE = ['r2', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_R1RHO_2SITE = 2005
MODEL_EXP_TYPE_NS_R1RHO_2SITE = EXP_TYPE_R1RHO
MODEL_SITES_NS_R1RHO_2SITE = 2
MODEL_EQ_NS_R1RHO_2SITE = EQ_NUMERIC

MODEL_NS_R1RHO_2SITE_FIT_R1 = "%s_fit_r1"%MODEL_NS_R1RHO_2SITE
MODEL_DESC_NS_R1RHO_2SITE_FIT_R1 = "The reduced numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, whereby the simplification R20A = R20B is assumed, and where R1 is fitted."
MODEL_PARAMS_NS_R1RHO_2SITE_FIT_R1 = ['r1_fit', 'r2', 'pA', 'dw', 'kex']
MODEL_YEAR_NS_R1RHO_2SITE_FIT_R1 = 2005
MODEL_EXP_TYPE_NS_R1RHO_2SITE_FIT_R1 = EXP_TYPE_R1RHO
MODEL_SITES_NS_R1RHO_2SITE_FIT_R1 = 2
MODEL_EQ_NS_R1RHO_2SITE_FIT_R1 = EQ_NUMERIC

MODEL_NS_R1RHO_3SITE = 'NS R1rho 3-site'
MODEL_DESC_NS_R1RHO_3SITE = "The numerical solution for the 3-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_R1RHO_3SITE = ['r2', 'pA', 'dw_AB', 'kex_AB', 'pB', 'dw_BC', 'kex_BC', 'kex_AC']
MODEL_YEAR_NS_R1RHO_3SITE = 2005
MODEL_EXP_TYPE_NS_R1RHO_3SITE = EXP_TYPE_R1RHO
MODEL_SITES_NS_R1RHO_3SITE = 3
MODEL_EQ_NS_R1RHO_3SITE = EQ_NUMERIC

MODEL_NS_R1RHO_3SITE_LINEAR = 'NS R1rho 3-site linear'
MODEL_DESC_NS_R1RHO_3SITE_LINEAR = "The numerical solution for the 3-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, linearised with kAC = kCA = 0 and whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR = ['r2', 'pA', 'dw_AB', 'kex_AB', 'pB', 'dw_BC', 'kex_BC']
MODEL_YEAR_NS_R1RHO_3SITE_LINEAR = 2005
MODEL_EXP_TYPE_NS_R1RHO_3SITE_LINEAR = EXP_TYPE_R1RHO
MODEL_SITES_NS_R1RHO_3SITE_LINEAR = 3
MODEL_EQ_NS_R1RHO_3SITE_LINEAR = EQ_NUMERIC

# The multi-quantum data model names.
MODEL_MMQ_CR72 = 'MMQ CR72'
MODEL_DESC_MMQ_CR72 = "The Carver and Richards (1972) 2-site model for all time scales expanded for MMQ CPMG experiments by Korzhnev et al., 2004."
MODEL_PARAMS_MMQ_CR72 = ['r2', 'pA', 'dw', 'dwH', 'kex']
MODEL_YEAR_MMQ_CR72 = 2004
MODEL_EXP_TYPE_MMQ_CR72 = EXP_TYPE_CPMG_MMQ
MODEL_SITES_MMQ_CR72 = 2
MODEL_EQ_MMQ_CR72 = EQ_ANALYTIC

MODEL_NS_MMQ_2SITE = 'NS MMQ 2-site'
MODEL_DESC_NS_MMQ_2SITE = "The reduced numerical solution for the 2-site Bloch-McConnell equations for MMQ CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_MMQ_2SITE = ['r2', 'pA', 'dw', 'dwH', 'kex']
MODEL_YEAR_NS_MMQ_2SITE = 2005
MODEL_EXP_TYPE_NS_MMQ_2SITE = EXP_TYPE_CPMG_MMQ
MODEL_SITES_NS_MMQ_2SITE = 2
MODEL_EQ_NS_MMQ_2SITE = EQ_NUMERIC

MODEL_NS_MMQ_3SITE = 'NS MMQ 3-site'
MODEL_DESC_NS_MMQ_3SITE = "The numerical solution for the 3-site Bloch-McConnell equations for MMQ CPMG experiments, whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_MMQ_3SITE = ['r2', 'pA', 'dw_AB', 'dwH_AB', 'kex_AB', 'pB', 'dw_BC', 'dwH_BC', 'kex_BC', 'kex_AC']
MODEL_YEAR_NS_MMQ_3SITE = 2005
MODEL_EXP_TYPE_NS_MMQ_3SITE = EXP_TYPE_CPMG_MMQ
MODEL_SITES_NS_MMQ_3SITE = 3
MODEL_EQ_NS_MMQ_3SITE = EQ_NUMERIC

MODEL_NS_MMQ_3SITE_LINEAR = 'NS MMQ 3-site linear'
MODEL_DESC_NS_MMQ_3SITE_LINEAR = "The numerical solution for the 3-site Bloch-McConnell equations for MMQ CPMG experiments, linearised with kAC = kCA = 0 and whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_MMQ_3SITE_LINEAR = ['r2', 'pA', 'dw_AB', 'dwH_AB', 'kex_AB', 'pB', 'dw_BC', 'dwH_BC', 'kex_BC']
MODEL_YEAR_NS_MMQ_3SITE_LINEAR = 2005
MODEL_EXP_TYPE_NS_MMQ_3SITE_LINEAR = EXP_TYPE_CPMG_MMQ
MODEL_SITES_NS_MMQ_3SITE_LINEAR = 3
MODEL_EQ_NS_MMQ_3SITE_LINEAR = EQ_NUMERIC

# The parameters.
PARAMS_R20 = ['r2', 'r2a', 'r2b']

# The defined models, which is used for nesting.
MODEL_NEST_CPMG = MODEL_CR72
MODEL_NEST_MMQ =  MODEL_MMQ_CR72
MODEL_NEST_R1RHO = MODEL_MP05

MODEL_LIST_NEST = [MODEL_NEST_CPMG, MODEL_NEST_MMQ, MODEL_NEST_R1RHO]

# The model lists.
## The CPMG models
### The analytical CPMG models.
MODEL_LIST_ANALYTIC_CPMG = [MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL]
"""The list of all analytic CPMG models."""

### The numerical CPMG models.
MODEL_LIST_NUMERIC_CPMG = [MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED]
"""The list of all numeric CPMG models."""

### All CPMG models.
MODEL_LIST_CPMG_ONLY = MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG
"""The list of all dispersion models specifically for CPMG-type experiments (excluding the R2eff model and model 'No Rex')."""

### No Rex model + All CPMG models
MODEL_LIST_CPMG = [MODEL_NOREX] + MODEL_LIST_CPMG_ONLY
"""The list of all dispersion models specifically for CPMG-type experiments (excluding the R2eff model)."""

### R2eff + No Rex model + All CPMG models
MODEL_LIST_CPMG_FULL = [MODEL_R2EFF] + MODEL_LIST_CPMG
"""The list of the R2eff model together with all dispersion models specifically for CPMG-type experiments."""

## The MQ CPMG-type modelss.
### The analytical MQ CPMG models.
MODEL_LIST_ANALYTIC_CPMG_MMQ = [MODEL_MMQ_CR72]
"""The list of all numeric MMQ CPMG models."""

### The numerical MQ CPMG models.
MODEL_LIST_NUMERIC_CPMG_MMQ = [MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of all numeric MMQ CPMG models."""

### All MQ CPMG-type models.
MODEL_LIST_MMQ = MODEL_LIST_ANALYTIC_CPMG_MMQ + MODEL_LIST_NUMERIC_CPMG_MMQ
"""The list of all dispersion models specifically for MMQ CPMG-type experiments."""

### No Rex model + All MQ CPMG-type models.
MODEL_LIST_MQ_CPMG = [MODEL_NOREX] + MODEL_LIST_MMQ
"""The list of all dispersion models specifically for MQ CPMG-type experiments (excluding the R2eff model)."""

### R2eff + No Rex model + All MQ CPMG-type models.
MODEL_LIST_MQ_CPMG_FULL = [MODEL_R2EFF] + MODEL_LIST_MQ_CPMG
"""The list of the R2eff model together with all dispersion models specifically for MQ CPMG-type experiments."""

## The R1rho models.
### The analytical models.
#### On-resonance R1rho models.
MODEL_LIST_R1RHO_ON_RES = [MODEL_M61, MODEL_M61B]
"""The list of all dispersion models specifically for R1rho-type on-resonance experiments (excluding the R2eff model and model 'No Rex')."""

#### Off-resonance R1rho models, where R1 has been measured.
MODEL_LIST_ANALYTIC_R1RHO_W_R1 = [MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05]
"""The list of all dispersion models specifically for analytical R1rho-type experiments which use R1 in their equations (excluding the R2eff model and model 'No Rex')."""

#### Off-resonance R1rho models, where R1 will be fitted.
MODEL_LIST_ANALYTIC_R1RHO_FIT_R1 = [MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1]
"""The list of all dispersion models specifically for R1rho-type experiments which fit R1 in their equations (excluding the R2eff model and model 'No Rex')."""

### The numerical models.
#### Off-resonance R1rho models, where R1 has been measured.
MODEL_LIST_NUMERIC_R1RHO_W_R1 = [MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]
"""The list of all dispersion models specifically for numeric R1rho-type experiments which use R1 in their equations (excluding the R2eff model and model 'No Rex')."""

#### Off-resonance R1rho models, where R1 will be fitted.
MODEL_LIST_NUMERIC_R1RHO_FIT_R1 = [MODEL_NS_R1RHO_2SITE_FIT_R1]
"""The list of all dispersion models specifically for numeric R1rho-type experiments which fit R1 in their equations (excluding the R2eff model and model 'No Rex')."""

### All R1rho models.
#### All analytical R1rho models
MODEL_LIST_ANALYTIC_R1RHO = MODEL_LIST_R1RHO_ON_RES + MODEL_LIST_ANALYTIC_R1RHO_W_R1 + MODEL_LIST_ANALYTIC_R1RHO_FIT_R1
"""The list of all dispersion models specifically for analytical R1rho-type (excluding the R2eff model and model 'No Rex')."""

#### All numeric R1rho models
MODEL_LIST_NUMERIC_R1RHO = MODEL_LIST_NUMERIC_R1RHO_W_R1 + MODEL_LIST_NUMERIC_R1RHO_FIT_R1
"""The list of all dispersion models specifically for analytical R1rho-type (excluding the R2eff model and model 'No Rex')."""

#### All R1rho models which use R1.
MODEL_LIST_R1RHO_W_R1_ONLY = MODEL_LIST_ANALYTIC_R1RHO_W_R1 + MODEL_LIST_NUMERIC_R1RHO_W_R1
"""The list of all dispersion models specifically for R1rho-type experiments which use R1 in their equations (excluding the R2eff model and model 'No Rex')."""

#### All R1rho models which fit R1.
MODEL_LIST_R1RHO_FIT_R1_ONLY = MODEL_LIST_ANALYTIC_R1RHO_FIT_R1 + MODEL_LIST_NUMERIC_R1RHO_FIT_R1
"""The list of all dispersion models specifically for R1rho-type experiments which fit R1 in their equations (excluding the R2eff model)."""

### No Rex model + All R1rho models using/fitting R1.
#### No Rex model + All R1rho models which use R1.
MODEL_LIST_R1RHO_W_R1 = [MODEL_NOREX_R1RHO] + MODEL_LIST_R1RHO_W_R1_ONLY
"""The list of all dispersion models specifically for R1rho-type experiments which use R1 in their equations (excluding the R2eff model)."""

#### No Rex model + All R1rho models which fit R1.
MODEL_LIST_R1RHO_FIT_R1 = [MODEL_NOREX_R1RHO_FIT_R1] + MODEL_LIST_R1RHO_FIT_R1_ONLY
"""The list of all dispersion models specifically for R1rho-type experiments which fit R1 in their equations (excluding the R2eff model)."""

### All R1rho models.
#### No Rex model + All R1rho models.
MODEL_LIST_R1RHO = [MODEL_NOREX, MODEL_NOREX_R1RHO, MODEL_NOREX_R1RHO_FIT_R1] + MODEL_LIST_ANALYTIC_R1RHO + MODEL_LIST_NUMERIC_R1RHO
"""The list of all dispersion models specifically for R1rho-type experiments (excluding the R2eff model)."""

MODEL_LIST_R1RHO_FULL = [MODEL_R2EFF] + MODEL_LIST_R1RHO
"""The list of the R2eff model together with all dispersion models specifically for R1rho-type experiments."""

# Division of all models into analytic and numeric.
## The list of all analytic models.
MODEL_LIST_ANALYTIC = MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_ANALYTIC_R1RHO + MODEL_LIST_ANALYTIC_CPMG_MMQ
"""The list of all analytic models."""

## The list of all numeric models.
MODEL_LIST_NUMERIC = MODEL_LIST_NUMERIC_CPMG + MODEL_LIST_NUMERIC_R1RHO + MODEL_LIST_NUMERIC_CPMG_MMQ
"""The list of all numeric models."""

# List of all models.
MODEL_LIST_DISP = [MODEL_NOREX, MODEL_NOREX_R1RHO, MODEL_NOREX_R1RHO_FIT_R1] + MODEL_LIST_CPMG_ONLY + MODEL_LIST_R1RHO_ON_RES + MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY + MODEL_LIST_MMQ
"""The list of all dispersion models (excluding the R2eff model)."""

MODEL_LIST_FULL = [MODEL_R2EFF] + MODEL_LIST_DISP
"""The list of the R2eff model together with all dispersion models."""

# The model lists dependent on parameter.
MODEL_LIST_INV_RELAX_TIMES = [MODEL_B14, MODEL_B14_FULL, MODEL_MMQ_CR72, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_2SITE_FIT_R1, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]
"""The inverted relaxation delay"""

MODEL_PARAM_R20B = [MODEL_B14_FULL, MODEL_CR72_FULL, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR_FULL]
"""Models using R20B."""

MODEL_PARAM_DW_MIX_DOUBLE = [MODEL_LM63_3SITE, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]
"""Models using parameters with mixed dw, and has two variables. For example with both dw and dwH or dw_AB and dw_BC or phi_ex_B and phi_ex_C."""

MODEL_PARAM_DW_MIX_QUADRUPLE = [MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""Models using parameters with mixed dw, and has four variables. For example with both dw_AB, dw_BC, dwH_AB and dwH_BC."""



# Full model description list.
MODEL_DESC = {
    MODEL_R2EFF: MODEL_DESC_R2EFF,
    MODEL_NOREX: MODEL_DESC_NOREX,
    MODEL_NOREX_R1RHO: MODEL_DESC_NOREX_R1RHO,
    MODEL_NOREX_R1RHO_FIT_R1: MODEL_DESC_NOREX_R1RHO_FIT_R1,
    MODEL_LM63: MODEL_DESC_LM63,
    MODEL_LM63_3SITE: MODEL_DESC_LM63_3SITE,
    MODEL_CR72: MODEL_DESC_CR72,
    MODEL_CR72_FULL: MODEL_DESC_CR72_FULL,
    MODEL_IT99: MODEL_DESC_IT99,
    MODEL_TSMFK01: MODEL_DESC_TSMFK01,
    MODEL_B14: MODEL_DESC_B14,
    MODEL_B14_FULL: MODEL_DESC_B14_FULL,
    MODEL_M61: MODEL_DESC_M61,
    MODEL_M61B: MODEL_DESC_M61B,
    MODEL_DPL94: MODEL_DESC_DPL94,
    MODEL_DPL94_FIT_R1: MODEL_DESC_DPL94_FIT_R1,
    MODEL_TP02: MODEL_DESC_TP02,
    MODEL_TP02_FIT_R1: MODEL_DESC_TP02_FIT_R1,
    MODEL_TAP03: MODEL_DESC_TAP03,
    MODEL_TAP03_FIT_R1: MODEL_DESC_TAP03_FIT_R1,
    MODEL_MP05: MODEL_DESC_MP05,
    MODEL_MP05_FIT_R1: MODEL_DESC_MP05_FIT_R1,
    MODEL_NS_CPMG_2SITE_3D: MODEL_DESC_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_DESC_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_DESC_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_DESC_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_DESC_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_DESC_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_2SITE_FIT_R1: MODEL_DESC_NS_R1RHO_2SITE_FIT_R1,
    MODEL_NS_R1RHO_3SITE: MODEL_DESC_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_DESC_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_DESC_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_DESC_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_DESC_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_DESC_NS_MMQ_3SITE_LINEAR
}

# Full parameter list.
MODEL_PARAMS = {
    MODEL_R2EFF: MODEL_PARAMS_R2EFF,
    MODEL_NOREX: MODEL_PARAMS_NOREX,
    MODEL_NOREX_R1RHO: MODEL_PARAMS_NOREX_R1RHO,
    MODEL_NOREX_R1RHO_FIT_R1: MODEL_PARAMS_NOREX_R1RHO_FIT_R1,
    MODEL_LM63: MODEL_PARAMS_LM63,
    MODEL_LM63_3SITE: MODEL_PARAMS_LM63_3SITE,
    MODEL_CR72: MODEL_PARAMS_CR72,
    MODEL_CR72_FULL: MODEL_PARAMS_CR72_FULL,
    MODEL_IT99: MODEL_PARAMS_IT99,
    MODEL_TSMFK01: MODEL_PARAMS_TSMFK01,
    MODEL_B14: MODEL_PARAMS_B14,
    MODEL_B14_FULL: MODEL_PARAMS_B14_FULL,
    MODEL_M61: MODEL_PARAMS_M61,
    MODEL_M61B: MODEL_PARAMS_M61B,
    MODEL_DPL94: MODEL_PARAMS_DPL94,
    MODEL_DPL94_FIT_R1: MODEL_PARAMS_DPL94_FIT_R1,
    MODEL_TP02: MODEL_PARAMS_TP02,
    MODEL_TP02_FIT_R1: MODEL_PARAMS_TP02_FIT_R1,
    MODEL_TAP03: MODEL_PARAMS_TAP03,
    MODEL_TAP03_FIT_R1: MODEL_PARAMS_TAP03_FIT_R1,
    MODEL_MP05: MODEL_PARAMS_MP05,
    MODEL_MP05_FIT_R1: MODEL_PARAMS_MP05_FIT_R1,
    MODEL_NS_CPMG_2SITE_3D: MODEL_PARAMS_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_PARAMS_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_PARAMS_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_PARAMS_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_PARAMS_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_PARAMS_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_2SITE_FIT_R1: MODEL_PARAMS_NS_R1RHO_2SITE_FIT_R1,
    MODEL_NS_R1RHO_3SITE: MODEL_PARAMS_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_PARAMS_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_PARAMS_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_PARAMS_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_PARAMS_NS_MMQ_3SITE_LINEAR
}

# Full year list.
MODEL_YEAR = {
    MODEL_R2EFF: MODEL_YEAR_R2EFF,
    MODEL_NOREX: MODEL_YEAR_NOREX,
    MODEL_NOREX_R1RHO: MODEL_YEAR_NOREX_R1RHO,
    MODEL_NOREX_R1RHO_FIT_R1: MODEL_YEAR_NOREX_R1RHO_FIT_R1,
    MODEL_LM63: MODEL_YEAR_LM63,
    MODEL_LM63_3SITE: MODEL_YEAR_LM63_3SITE,
    MODEL_CR72: MODEL_YEAR_CR72,
    MODEL_CR72_FULL: MODEL_YEAR_CR72_FULL,
    MODEL_IT99: MODEL_YEAR_IT99,
    MODEL_TSMFK01: MODEL_YEAR_TSMFK01,
    MODEL_B14: MODEL_YEAR_B14,
    MODEL_B14_FULL: MODEL_YEAR_B14_FULL,
    MODEL_M61: MODEL_YEAR_M61,
    MODEL_M61B: MODEL_YEAR_M61B,
    MODEL_DPL94: MODEL_YEAR_DPL94,
    MODEL_DPL94_FIT_R1: MODEL_YEAR_DPL94_FIT_R1,
    MODEL_TP02: MODEL_YEAR_TP02,
    MODEL_TP02_FIT_R1: MODEL_YEAR_TP02_FIT_R1,
    MODEL_TAP03: MODEL_YEAR_TAP03,
    MODEL_TAP03_FIT_R1: MODEL_YEAR_TAP03_FIT_R1,
    MODEL_MP05: MODEL_YEAR_MP05,
    MODEL_MP05_FIT_R1: MODEL_YEAR_MP05_FIT_R1,
    MODEL_NS_CPMG_2SITE_3D: MODEL_YEAR_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_YEAR_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_YEAR_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_YEAR_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_YEAR_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_YEAR_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_2SITE_FIT_R1: MODEL_YEAR_NS_R1RHO_2SITE_FIT_R1,
    MODEL_NS_R1RHO_3SITE: MODEL_YEAR_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_YEAR_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_YEAR_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_YEAR_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_YEAR_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_YEAR_NS_MMQ_3SITE_LINEAR
}

# Full EXP_TYPE list.
MODEL_EXP_TYPE = {
    MODEL_R2EFF: MODEL_EXP_TYPE_R2EFF,
    MODEL_NOREX: MODEL_EXP_TYPE_NOREX,
    MODEL_NOREX_R1RHO: MODEL_EXP_TYPE_NOREX_R1RHO,
    MODEL_NOREX_R1RHO_FIT_R1: MODEL_EXP_TYPE_NOREX_R1RHO_FIT_R1,
    MODEL_LM63: MODEL_EXP_TYPE_LM63,
    MODEL_LM63_3SITE: MODEL_EXP_TYPE_LM63_3SITE,
    MODEL_CR72: MODEL_EXP_TYPE_CR72,
    MODEL_CR72_FULL: MODEL_EXP_TYPE_CR72_FULL,
    MODEL_IT99: MODEL_EXP_TYPE_IT99,
    MODEL_TSMFK01: MODEL_EXP_TYPE_TSMFK01,
    MODEL_B14: MODEL_EXP_TYPE_B14,
    MODEL_B14_FULL: MODEL_EXP_TYPE_B14_FULL,
    MODEL_M61: MODEL_EXP_TYPE_M61,
    MODEL_M61B: MODEL_EXP_TYPE_M61B,
    MODEL_DPL94: MODEL_EXP_TYPE_DPL94,
    MODEL_DPL94_FIT_R1: MODEL_EXP_TYPE_DPL94_FIT_R1,
    MODEL_TP02: MODEL_EXP_TYPE_TP02,
    MODEL_TP02_FIT_R1: MODEL_EXP_TYPE_TP02_FIT_R1,
    MODEL_TAP03: MODEL_EXP_TYPE_TAP03,
    MODEL_TAP03_FIT_R1: MODEL_EXP_TYPE_TAP03_FIT_R1,
    MODEL_MP05: MODEL_EXP_TYPE_MP05,
    MODEL_MP05_FIT_R1: MODEL_EXP_TYPE_MP05_FIT_R1,
    MODEL_NS_CPMG_2SITE_3D: MODEL_EXP_TYPE_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_EXP_TYPE_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_EXP_TYPE_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_EXP_TYPE_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_2SITE_FIT_R1: MODEL_EXP_TYPE_NS_R1RHO_2SITE_FIT_R1,
    MODEL_NS_R1RHO_3SITE: MODEL_EXP_TYPE_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_EXP_TYPE_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_EXP_TYPE_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_EXP_TYPE_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_EXP_TYPE_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_EXP_TYPE_NS_MMQ_3SITE_LINEAR
}

# Full list of number of chemical exchange sites.
MODEL_SITES = {
    MODEL_R2EFF: MODEL_SITES_R2EFF,
    MODEL_NOREX: MODEL_SITES_NOREX,
    MODEL_NOREX_R1RHO: MODEL_SITES_NOREX_R1RHO,
    MODEL_NOREX_R1RHO_FIT_R1: MODEL_SITES_NOREX_R1RHO_FIT_R1,
    MODEL_LM63: MODEL_SITES_LM63,
    MODEL_LM63_3SITE: MODEL_SITES_LM63_3SITE,
    MODEL_CR72: MODEL_SITES_CR72,
    MODEL_CR72_FULL: MODEL_SITES_CR72_FULL,
    MODEL_IT99: MODEL_SITES_IT99,
    MODEL_TSMFK01: MODEL_SITES_TSMFK01,
    MODEL_B14: MODEL_SITES_B14,
    MODEL_B14_FULL: MODEL_SITES_B14_FULL,
    MODEL_M61: MODEL_SITES_M61,
    MODEL_M61B: MODEL_SITES_M61B,
    MODEL_DPL94: MODEL_SITES_DPL94,
    MODEL_DPL94_FIT_R1: MODEL_SITES_DPL94_FIT_R1,
    MODEL_TP02: MODEL_SITES_TP02,
    MODEL_TP02_FIT_R1: MODEL_SITES_TP02_FIT_R1,
    MODEL_TAP03: MODEL_SITES_TAP03,
    MODEL_TAP03_FIT_R1: MODEL_SITES_TAP03_FIT_R1,
    MODEL_MP05: MODEL_SITES_MP05,
    MODEL_MP05_FIT_R1: MODEL_SITES_MP05_FIT_R1,
    MODEL_NS_CPMG_2SITE_3D: MODEL_SITES_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_SITES_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_SITES_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_SITES_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_SITES_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_SITES_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_2SITE_FIT_R1: MODEL_SITES_NS_R1RHO_2SITE_FIT_R1,
    MODEL_NS_R1RHO_3SITE: MODEL_SITES_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_SITES_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_SITES_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_SITES_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_SITES_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_SITES_NS_MMQ_3SITE_LINEAR
}

# Full list of equation type.
MODEL_EQ = {
    MODEL_R2EFF: MODEL_EQ_R2EFF,
    MODEL_NOREX: MODEL_EQ_NOREX,
    MODEL_NOREX_R1RHO: MODEL_EQ_NOREX_R1RHO,
    MODEL_NOREX_R1RHO_FIT_R1: MODEL_EQ_NOREX_R1RHO_FIT_R1,
    MODEL_LM63: MODEL_EQ_LM63,
    MODEL_LM63_3SITE: MODEL_EQ_LM63_3SITE,
    MODEL_CR72: MODEL_EQ_CR72,
    MODEL_CR72_FULL: MODEL_EQ_CR72_FULL,
    MODEL_IT99: MODEL_EQ_IT99,
    MODEL_TSMFK01: MODEL_EQ_TSMFK01,
    MODEL_B14: MODEL_EQ_B14,
    MODEL_B14_FULL: MODEL_EQ_B14_FULL,
    MODEL_M61: MODEL_EQ_M61,
    MODEL_M61B: MODEL_EQ_M61B,
    MODEL_DPL94: MODEL_EQ_DPL94,
    MODEL_DPL94_FIT_R1: MODEL_EQ_DPL94_FIT_R1,
    MODEL_TP02: MODEL_EQ_TP02,
    MODEL_TP02_FIT_R1: MODEL_EQ_TP02_FIT_R1,
    MODEL_TAP03: MODEL_EQ_TAP03,
    MODEL_TAP03_FIT_R1: MODEL_EQ_TAP03_FIT_R1,
    MODEL_MP05: MODEL_EQ_MP05,
    MODEL_MP05_FIT_R1: MODEL_EQ_MP05_FIT_R1,
    MODEL_NS_CPMG_2SITE_3D: MODEL_EQ_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_EQ_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_EQ_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_EQ_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_EQ_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_EQ_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_2SITE_FIT_R1: MODEL_EQ_NS_R1RHO_2SITE_FIT_R1,
    MODEL_NS_R1RHO_3SITE: MODEL_EQ_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_EQ_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_EQ_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_EQ_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_EQ_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_EQ_NS_MMQ_3SITE_LINEAR
}


# Define class for describing the model.
# This class is defined to be able to make better sorting of the models.
class model_class:
    def __init__(self, model=None, desc=None, exp_type=None, eq=None, sites=None, year=None, params=None, params_nr=None):
        """Class for storing model information.

        @keyword model:     Current model
        @type model:        str
        @keyword desc:      Model description.
        @type desc:         str
        @keyword exp_type:  Model experiment type.
        @type exp_type:     str
        @keyword eq:        Model equation type.
        @type eq:           str
        @keyword sites:     Number of chemical sites in model.
        @type site:         int
        @keyword year:      Which year model was described or published.
        @type year:         int
        @keyword params:    Parameters belonging to model.
        @type params:       list of str
        @keyword params_nr: Nr of parameters belonging to model.
        @type params_nr:    int
        """

        # Save the info to variables.
        self.model = model
        self.desc = desc
        self.exp_type = exp_type
        self.eq = eq
        self.sites = sites
        self.year = year
        self.params = params
        self.params_nr = params_nr

        # Define the order of how exp type ranks.
        order_exp_type = [EXP_TYPE_R2EFF, EXP_TYPE_NOREX, EXP_TYPE_NOREX_R1RHO, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_MMQ, EXP_TYPE_R1RHO]

        # Save the index of current model to order of equation type.
        self.exp_type_i = order_exp_type.index(self.exp_type)

        # Define the order of how equation type ranks.
        order_eq = [EQ_NUMERIC, EQ_SILICO, EQ_ANALYTIC]

        # Save the index of current model to order of equation type.
        self.eq_i = order_eq.index(self.eq)

        # Define the order of how equation type ranks, when sorting before auto analyses.
        order_s = [EQ_SILICO, EQ_ANALYTIC, EQ_NUMERIC]

        # Save the index of current model to order of equation type.
        self.eq_s = order_s.index(self.eq)

        # Save the difference in year from now, to implemented model.
        self.year_diff = date.today().year - self.year

    # Make a readable presentation of the class object. Here a tuple.
    def __repr__(self):
        return repr((self.model, self.desc, self.exp_type, self.eq, self.sites, self.year, self.params, self.params_nr))


# Define function, to return model info.
def models_info(models=None):
    """Get model info for list of models.

    @keyword model:   The list of all models analysed.
    @type model:      list of str
    @return:          List of tuples, where each tuple contains model info.
    @rtype:           List of tuples with str.
    """

    # Define list of return.
    models_info = []

    # Loop over models.
    for model in models:
        # model description.
        model_DESC = MODEL_DESC[model]

        # model equation type: analytic, silico or numeric.
        model_EQ = MODEL_EQ[model]

        # The model experiment type.
        model_EXP_TYPE = MODEL_EXP_TYPE[model]

        # model parameters.
        model_PARAMS = MODEL_PARAMS[model]

        # model number of parameters.
        model_PARAMS_NR = len(model_PARAMS)

        # The number of chemical sites.
        model_SITES = MODEL_SITES[model]

        # year where model was developed or published.
        model_YEAR = MODEL_YEAR[model]

        # Append to the list, the class instance of model info.
        models_info.append(model_class(model=model, desc=model_DESC, exp_type=model_EXP_TYPE, eq=model_EQ, sites=model_SITES, year=model_YEAR, params=model_PARAMS, params_nr=model_PARAMS_NR))

    # Return the list of model info.
    return models_info


# Define function, to determine which model to nest from.
def nesting_model(self_models=None, model=None):
    """Determine if the current model can use nested results from any of the previous analysed models.

    @keyword self_models:   The list of all models analysed.
    @type self_models:      list of str
    @keyword model:         The current model to analyse.
    @type model:            str
    @return:                The current model info, the possible nest model info.
    @rtype:                 class, class
    """


    # Get the list index for the current model in all models.
    model_index = self_models.index(model)

    # Define the list of models which can be tested. This is the number of models which have already been tested.
    completed_models = self_models[:model_index]

    # Get the current models information.
    model_info = models_info([model])[0]

    # Get the info of the completed models.
    completed_models_info = models_info(completed_models)

    # Sort the models according to: exp_type, equation type, chemical sites, year for model, number of parameters.
    completed_models_info = sorted(completed_models_info, key=attrgetter('exp_type_i', 'eq_i', 'sites', 'year_diff', 'params_nr'))

    # Define list of comparable models
    compa_models = []

    # Loop over the list of model info.
    for compl_model_info in completed_models_info:
        # If the exp_type is the same, add to list of comparable models.
        if compl_model_info.exp_type == model_info.exp_type:
            compa_models.append(compl_model_info)

    # Now determine how to report the nested models, if there exist comparable models.
    if len(compa_models) >= 1:
        # Loop over the list of comparable models, if the parameters are the same, return that as nested model.
        for compa_model in compa_models:
            if compa_model.params == model_info.params:
                return model_info, compa_model

        # Loop over the list of comparable models, if the parameters (other than R20 params) are the same, return that as nested model.
        for compa_model in compa_models:
            # Remove R20 params.
            part_compa_model_params = compa_model.params
            part_model_params = model_info.params
            for r20 in PARAMS_R20:
                part_compa_model_params = filter(partial(ne, r20), part_compa_model_params)
                part_model_params = filter(partial(ne, r20), part_model_params)

            # If the partial params are the same, then return that model.
            if part_compa_model_params == part_model_params:
                return model_info, compa_model

        # Loop over the list of comparable models, if the parameters are part of the more complex model, return that as nested model.
        for compa_model in compa_models:
            # If the params list are within the parameter list, then return that model.
            param_in = False

            # Loop over the parameters.
            for param in compa_model.params:
                if param in model_info.params:
                    param_in = True

                # Special situation, where 'kex' can still be nested from DPL94 model.
                elif param == 'phi_ex' and compa_model.model in MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY and model in MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY:
                    continue

                # Special situation, where 'kex' can still be nested from LM63 model.
                elif param == 'phi_ex' and compa_model.model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG and model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG:
                    continue

                # Special situation, where 'kex'=1/tex can still be nested from IT99 model.
                elif param == 'tex' and compa_model.model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG and model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG:
                    continue

                # Else break out of the loop.
                else:
                    # Break the for loop, if not found.
                    param_in = False
                    break

            # If all parameters are found in the more complex model.
            if param_in:
                return model_info, compa_model

        # Special case for LM63
        if model == MODEL_LM63_3SITE:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_LM63, return this.
                if compa_model.model == MODEL_LM63:
                    return model_info, compa_model

        # Special case for MODEL_NS_MMQ_3SITE or MODEL_NS_MMQ_3SITE_LINEAR, getting parameters from MODEL_NS_MMQ_2SITE.
        elif model in [MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_NS_MMQ_2SITE, return this.
                if compa_model.model == MODEL_NS_MMQ_2SITE:
                    return model_info, compa_model

        # Special case for MODEL_NS_R1RHO_3SITE or MODEL_NS_R1RHO_3SITE_LINEAR, getting parameters from MODEL_NS_R1RHO_2SITE.
        elif model in [MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_NS_MMQ_2SITE, return this.
                if compa_model.model == MODEL_NS_R1RHO_2SITE:
                    return model_info, compa_model

        # Special case for DPL94.
        elif model in [MODEL_DPL94, MODEL_DPL94_FIT_R1]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is in list with R1rho R1, return this.
                if compa_model.model in MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY:
                    return model_info, compa_model

        # Special case for IT99.
        elif model in [MODEL_IT99]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is in list with R1rho R1, return this.
                if compa_model.model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG:
                    return model_info, compa_model

        # If all fails.
        return model_info, None

    # If there is no comparable models according to EXP_TYPE, check if some models can be nested anyway.
    else:
        # Define list of comparable models, to be all completed models.
        compa_models = completed_models_info

        # Special case for MODEL_MMQ_CR72.
        if model == MODEL_MMQ_CR72:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_CR72, return this.
                if compa_model.model == MODEL_CR72:
                    return model_info, compa_model

        else:
            return model_info, None


# Define function, to sort models.
def sort_models(models=None):
    """Determine how to order the models for analyses.

    @keyword models:   The list of all models to be analysed.
    @type models:      list of str
    @return:           The ordered list how models should be analysed.
    @rtype:            list of str
    """

    # Get the info of the models selected for analysis.
    all_models_info = models_info(models)

    # Sort the models according to: exp_type, equation type, chemical sites, year for model, number of parameters.
    all_models_info_sorted = sorted(all_models_info, key=attrgetter('exp_type_i', 'eq_s', 'sites', 'year_diff', 'params_nr'))

    # Define list of sorted models.
    sorted_models = []

    # Loop over the models info, and extract model.
    for model_info in all_models_info_sorted:
        sorted_models.append(model_info.model)

    # Return sorted list of models.
    return sorted_models

