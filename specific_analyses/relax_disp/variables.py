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

# Module docstring.
"""Variables for the relaxation dispersion specific analysis."""


# Experiment types.
EXP_TYPE_CPMG_SQ = 'SQ CPMG'
EXP_TYPE_CPMG_DQ = 'DQ CPMG'
EXP_TYPE_CPMG_MQ = 'MQ CPMG'
EXP_TYPE_CPMG_ZQ = 'ZQ CPMG'
EXP_TYPE_CPMG_PROTON_SQ = '1H SQ CPMG'
EXP_TYPE_CPMG_PROTON_MQ = '1H MQ CPMG'
EXP_TYPE_R1RHO = 'R1rho'

# Experiment type descriptions.
EXP_TYPE_DESC_CPMG_SQ = "the standard single quantum (SQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_DQ = "the double quantum (DQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_MQ = "the multiple quantum (MQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_ZQ = "the zero quantum (ZQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_PROTON_SQ = "the 1H single quantum (SQ) CPMG-type experiment"
EXP_TYPE_DESC_CPMG_PROTON_MQ = "the 1H multiple quantum (MQ) CPMG-type experiment"
EXP_TYPE_DESC_R1RHO = "the R1rho-type experiment"


# The experiment type lists.
EXP_TYPE_LIST = [EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_R1RHO]
"""The list of all dispersion experiment types."""

EXP_TYPE_LIST_CPMG = [EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]
"""The list of all dispersion experiment types for CPMG-type data."""

EXP_TYPE_LIST_R1RHO = [EXP_TYPE_R1RHO]
"""The list of all dispersion experiment types for R1rho-type data."""


# The model names, parameters, and descriptions.
MODEL_R2EFF = 'R2eff'
MODEL_DESC_R2EFF = "The model for determining the R2eff/R1rho values from peak intensities."
MODEL_PARAMS_R2EFF = ['r2eff', 'i0']    # The 'i0' parameter is only for the exponential curve-fitting.

MODEL_NOREX = 'No Rex'
MODEL_DESC_NOREX = "The model for no chemical exchange relaxation."
MODEL_PARAMS_NOREX = ['r2']

MODEL_LM63 = 'LM63'
MODEL_DESC_LM63 = "The Luz and Meiboom (1963) 2-site fast exchange model for SQ-CPMG experiments."
MODEL_PARAMS_LM63 = ['r2', 'phi_ex', 'kex']

MODEL_LM63_3SITE = 'LM63 3-site'
MODEL_DESC_LM63_3SITE = "The Luz and Meiboom (1963) 3-site fast exchange model for SQ-CPMG experiments."
MODEL_PARAMS_LM63_3SITE = ['r2', 'phi_ex_B', 'phi_ex_C', 'kB', 'kC']

MODEL_CR72 = 'CR72'
MODEL_DESC_CR72 = "The reduced Carver and Richards (1972) 2-site model for all time scales for SQ-CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_CR72 = ['r2', 'pA', 'dw', 'kex']

MODEL_CR72_FULL = 'CR72 full'
MODEL_DESC_CR72_FULL = "The full Carver and Richards (1972) 2-site model for all time scales for SQ-CPMG experiments."
MODEL_PARAMS_CR72_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']

MODEL_IT99 = 'IT99'
MODEL_DESC_IT99 = "The Ishima and Torchia (1999) 2-site CPMG model for all time scales for SQ-CPMG experiments, with skewed populations (pA >> pB)."
MODEL_PARAMS_IT99 = ['r2', 'pA', 'dw', 'tex']

MODEL_TSMFK01 = 'TSMFK01'
MODEL_DESC_TSMFK01 = "The Tollinger et al. (2001) 2-site very-slow exchange model for SQ-CPMG experiments."
MODEL_PARAMS_TSMFK01 = ['r2a', 'dw', 'k_AB']

MODEL_B14 = 'B14'
MODEL_DESC_B14 = "The Baldwin (2014) 2-site CPMG exact solution model for all time scales for SQ-CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_B14 = ['r2', 'pA', 'dw', 'kex']

MODEL_B14_FULL = 'B14 full'
MODEL_DESC_B14_FULL = "The Baldwin (2014) 2-site CPMG exact solution model for all time scales for SQ-CPMG experiments."
MODEL_PARAMS_B14_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']

MODEL_M61 = 'M61'
MODEL_DESC_M61 = "The Meiboom (1961) on-resonance 2-site fast exchange model for R1rho-type experiments."
MODEL_PARAMS_M61 = ['r2', 'phi_ex', 'kex']

MODEL_M61B = 'M61 skew'
MODEL_DESC_M61B = "The Meiboom (1961) on-resonance 2-site model for R1rho-type experiments, with skewed populations (pA >> pB)."
MODEL_PARAMS_M61B = ['r2', 'pA', 'dw', 'kex']

MODEL_DPL94 = 'DPL94'
"""The R1rho 2-site fast exchange model of Davis, Perlman and London (1994)."""
MODEL_DESC_DPL94 = "The Davis, Perlman and London (1994) extension of the Meiboom (1961) model for off-resonance data."
MODEL_PARAMS_DPL94 = ['r2', 'phi_ex', 'kex']

MODEL_TP02 = 'TP02'
MODEL_DESC_TP02 = "The Trott and Palmer (2002) off-resonance 2-site model for R1rho-type experiments."
MODEL_PARAMS_TP02 = ['r2', 'pA', 'dw', 'kex']

MODEL_TAP03 = 'TAP03'
MODEL_DESC_TAP03 = "The Trott, Abergel and Palmer (2003) off-resonance 2-site model for R1rho-type experiments."
MODEL_PARAMS_TAP03 = ['r2', 'pA', 'dw', 'kex']

MODEL_MP05 = 'MP05'
"""The R1rho 2-site off-resonance exchange model of Miloushev and Palmer (2005)."""
MODEL_DESC_MP05 = "The Miloushev and Palmer (2005) off-resonance 2-site model for R1rho-type experiments."
MODEL_PARAMS_MP05 = ['r2', 'pA', 'dw', 'kex']


# The Numerical model names.
MODEL_NS_CPMG_2SITE_3D = 'NS CPMG 2-site 3D'
MODEL_DESC_NS_CPMG_2SITE_3D = "The reduced numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for SQ CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_CPMG_2SITE_3D = ['r2', 'pA', 'dw', 'kex']

MODEL_NS_CPMG_2SITE_3D_FULL = 'NS CPMG 2-site 3D full'
MODEL_DESC_NS_CPMG_2SITE_3D_FULL = "The full numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for SQ CPMG experiments."
MODEL_PARAMS_NS_CPMG_2SITE_3D_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']

MODEL_NS_CPMG_2SITE_STAR = 'NS CPMG 2-site star'
MODEL_DESC_NS_CPMG_2SITE_STAR = "The numerical reduced solution for the 2-site Bloch-McConnell equations using complex conjugate matrices for SQ CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_CPMG_2SITE_STAR = ['r2', 'pA', 'dw', 'kex']

MODEL_NS_CPMG_2SITE_STAR_FULL = 'NS CPMG 2-site star full'
MODEL_DESC_NS_CPMG_2SITE_STAR_FULL = "The full numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices for SQ CPMG experiments."
MODEL_PARAMS_NS_CPMG_2SITE_STAR_FULL = ['r2a', 'r2b', 'pA', 'dw', 'kex']

MODEL_NS_CPMG_2SITE_EXPANDED = 'NS CPMG 2-site expanded'
MODEL_DESC_NS_CPMG_2SITE_EXPANDED = "The numerical solution for the 2-site Bloch-McConnell equations for SQ CPMG experiments, expanded using Maple by Nikolai Skrynnikov."
MODEL_PARAMS_NS_CPMG_2SITE_EXPANDED = ['r2', 'pA', 'dw', 'kex']

MODEL_NS_R1RHO_2SITE = 'NS R1rho 2-site'
MODEL_DESC_NS_R1RHO_2SITE = "The reduced numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_R1RHO_2SITE = ['r2', 'pA', 'dw', 'kex']

MODEL_NS_R1RHO_3SITE = 'NS R1rho 3-site'
MODEL_DESC_NS_R1RHO_3SITE = "The numerical solution for the 3-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_R1RHO_3SITE = ['r2', 'pA', 'dw_AB', 'kex_AB', 'pB', 'dw_BC', 'kex_BC', 'kex_AC']

MODEL_NS_R1RHO_3SITE_LINEAR = 'NS R1rho 3-site linear'
MODEL_DESC_NS_R1RHO_3SITE_LINEAR = "The numerical solution for the 3-site Bloch-McConnell equations using 3D magnetisation vectors for R1rho-type experiments, linearised with kAC = kCA = 0 and whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR = ['r2', 'pA', 'dw_AB', 'kex_AB', 'pB', 'dw_BC', 'kex_BC']


# The multi-quantum data model names.
MODEL_MMQ_CR72 = 'MMQ CR72'
MODEL_DESC_MMQ_CR72 = "The Carver and Richards (1972) 2-site model for all time scales expanded for MMQ CPMG experiments by Korzhnev et al., 2004."
MODEL_PARAMS_MMQ_CR72 = ['r2', 'pA', 'dw', 'dwH', 'kex']

MODEL_NS_MMQ_2SITE = 'NS MMQ 2-site'
MODEL_DESC_NS_MMQ_2SITE = "The reduced numerical solution for the 2-site Bloch-McConnell equations for MMQ CPMG experiments, whereby the simplification R20A = R20B is assumed."
MODEL_PARAMS_NS_MMQ_2SITE = ['r2', 'pA', 'dw', 'dwH', 'kex']

MODEL_NS_MMQ_3SITE = 'NS MMQ 3-site'
MODEL_DESC_NS_MMQ_3SITE = "The numerical solution for the 3-site Bloch-McConnell equations for MMQ CPMG experiments, whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_MMQ_3SITE = ['r2', 'pA', 'dw_AB', 'dwH_AB', 'kex_AB', 'pB', 'dw_BC', 'dwH_BC', 'kex_BC', 'kex_AC']

MODEL_NS_MMQ_3SITE_LINEAR = 'NS MMQ 3-site linear'
MODEL_DESC_NS_MMQ_3SITE_LINEAR = "The numerical solution for the 3-site Bloch-McConnell equations for MMQ CPMG experiments, linearised with kAC = kCA = 0 and whereby the simplification R20A = R20B = R20C is assumed."
MODEL_PARAMS_NS_MMQ_3SITE_LINEAR = ['r2', 'pA', 'dw_AB', 'dwH_AB', 'kex_AB', 'pB', 'dw_BC', 'dwH_BC', 'kex_BC']

# The parameters.
PARAMS_R20 = ['r2', 'r2a', 'r2b']


# The model lists.
MODEL_LIST_DISP = [MODEL_NOREX, MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_M61, MODEL_M61B, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of all dispersion models (excluding the R2eff model)."""

MODEL_LIST_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_M61, MODEL_M61B, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of the R2eff model together with all dispersion models."""

MODEL_LIST_CPMG = [MODEL_NOREX, MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED]
"""The list of all dispersion models specifically for CPMG-type experiments (excluding the R2eff model)."""

MODEL_LIST_CPMG_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED]
"""The list of the R2eff model together with all dispersion models specifically for CPMG-type experiments."""

MODEL_LIST_R1RHO = [MODEL_NOREX, MODEL_M61, MODEL_M61B, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]
"""The list of all dispersion models specifically for R1rho-type experiments (excluding the R2eff model)."""

MODEL_LIST_R1RHO_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_M61, MODEL_M61B, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]
"""The list of the R2eff model together with all dispersion models specifically for R1rho-type experiments."""

MODEL_LIST_MQ_CPMG = [MODEL_NOREX, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of all dispersion models specifically for MQ CPMG-type experiments (excluding the R2eff model)."""

MODEL_LIST_MQ_CPMG_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of the R2eff model together with all dispersion models specifically for MQ CPMG-type experiments."""

MODEL_LIST_MMQ = [MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of all dispersion models specifically for MMQ CPMG-type experiments."""

MODEL_LIST_ANALYTIC = [MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_M61, MODEL_M61B, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MMQ_CR72, MODEL_MP05]
"""The list of all analytic models."""

MODEL_LIST_NUMERIC = [MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of all numeric models."""

MODEL_LIST_NUMERIC_CPMG = [MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]
"""The list of all numeric models."""

# Full model description list.
MODEL_DESC = {
    MODEL_R2EFF: MODEL_DESC_R2EFF,
    MODEL_NOREX: MODEL_DESC_NOREX,
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
    MODEL_TP02: MODEL_DESC_TP02,
    MODEL_TAP03: MODEL_DESC_TAP03,
    MODEL_MP05: MODEL_DESC_MP05,
    MODEL_NS_CPMG_2SITE_3D: MODEL_DESC_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_DESC_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_DESC_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_DESC_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_DESC_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_DESC_NS_R1RHO_2SITE,
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
    MODEL_TP02: MODEL_PARAMS_TP02,
    MODEL_TAP03: MODEL_PARAMS_TAP03,
    MODEL_MP05: MODEL_PARAMS_MP05,
    MODEL_NS_CPMG_2SITE_3D: MODEL_PARAMS_NS_CPMG_2SITE_3D,
    MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_PARAMS_NS_CPMG_2SITE_3D_FULL,
    MODEL_NS_CPMG_2SITE_STAR: MODEL_PARAMS_NS_CPMG_2SITE_STAR,
    MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_PARAMS_NS_CPMG_2SITE_STAR_FULL,
    MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_PARAMS_NS_CPMG_2SITE_EXPANDED,
    MODEL_NS_R1RHO_2SITE: MODEL_PARAMS_NS_R1RHO_2SITE,
    MODEL_NS_R1RHO_3SITE: MODEL_PARAMS_NS_R1RHO_3SITE,
    MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR,
    MODEL_MMQ_CR72: MODEL_PARAMS_MMQ_CR72,
    MODEL_NS_MMQ_2SITE: MODEL_PARAMS_NS_MMQ_2SITE,
    MODEL_NS_MMQ_3SITE: MODEL_PARAMS_NS_MMQ_3SITE,
    MODEL_NS_MMQ_3SITE_LINEAR: MODEL_PARAMS_NS_MMQ_3SITE_LINEAR
}
