###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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

# The experiment type lists.
FIXED_TIME_EXP = ['cpmg fixed', 'r1rho fixed']
"""The list of fixed relaxation time period experiments."""

VAR_TIME_EXP = ['cpmg exponential', 'r1rho exponential']
"""The list of variable relaxation time period experiments."""

CPMG_EXP = ['cpmg fixed', 'cpmg exponential']
"""The list of CPMG-type experiments."""

R1RHO_EXP = ['r1rho fixed', 'r1rho exponential']
"""The list of R1rho-type experiments."""


# The model names.
MODEL_R2EFF = 'R2eff'
"""The model for determining the R2eff/R1rho values from peak intensities."""

MODEL_NOREX = 'No Rex'
"""The model for no chemical exchange relaxation."""

MODEL_LM63 = 'LM63'
"""The CPMG 2-site fast exchange model of Luz and Meiboom (1963)."""

MODEL_TSMFK01 = 'TSMFK01'
"""The CPMG 2-site very-slow exchange model, range of microsecond to second time scale, of M. Tollinger, N.R. Skrynnikov, F.A.A. Mulder, J.D.F. Kay and L.E. Kay (2001)."""

MODEL_LM63_3SITE = 'LM63 3-site'
"""The CPMG 3-site fast exchange model of Luz and Meiboom (1963)."""

MODEL_CR72 = 'CR72'
"""The CPMG 2-site model for all time scales of Carver and Richards (1972), whereby the simplification R20A = R20B is assumed."""

MODEL_CR72_FULL = 'CR72 full'
"""The CPMG 2-site model for all time scales of Carver and Richards (1972)."""

MODEL_IT99 = 'IT99'
"""The CPMG 2-site model for all time scales with pA >> pB of Ishima and Torchia (1999)."""

MODEL_DPL94 = 'DPL94'
"""The R1rho 2-site fast exchange model of Davis, Perlman and London (1994)."""

MODEL_M61 = 'M61'
"""The R1rho 2-site fast exchange model of Meiboom (1961)."""

MODEL_M61B = 'M61 skew'
"""The R1rho 2-site model for all time scales with pA >> pB of Meiboom (1961)."""

MODEL_TP02 = 'TP02'
"""The R1rho 2-site exchange model of Trott and Palmer (2002)."""


# The Numerical model names.
MODEL_NS_CPMG_2SITE_3D = 'NS CPMG 2-site 3D'
"""The numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors, whereby the simplification R20A = R20B is assumed."""

MODEL_NS_CPMG_2SITE_3D_FULL = 'NS CPMG 2-site 3D full'
"""The numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors."""

MODEL_NS_CPMG_2SITE_STAR = 'NS CPMG 2-site star'
"""The numerical solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices, whereby the simplification R20A = R20B is assumed."""

MODEL_NS_CPMG_2SITE_STAR_FULL = 'NS CPMG 2-site star full'
"""The numerical solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices."""

MODEL_NS_CPMG_2SITE_EXPANDED = 'NS CPMG 2-site expanded'
"""The numerical solution for the 2-site Bloch-McConnell equations for CPMG data expanded using Maple by Nikolai Skrynnikov."""

MODEL_NS_R1RHO_2SITE = 'NS R1rho 2-site'
"""The numerical solution for the 2-site Bloch-McConnell equations for R1rho data, whereby the simplification R20A = R20B is assumed."""


# The model lists.
MODEL_LIST_DISP = [MODEL_NOREX, MODEL_LM63, MODEL_TSMFK01, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_TP02, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_R1RHO_2SITE]
"""The list of all dispersion models (excluding the R2eff model)."""

MODEL_LIST_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_TSMFK01, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_TP02, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_R1RHO_2SITE]
"""The list of the R2eff model together with all dispersion models."""

MODEL_LIST_CPMG = [MODEL_NOREX, MODEL_LM63, MODEL_TSMFK01, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED]
"""The list of all dispersion models specifically for CPMG-type experiments (excluding the R2eff model)."""

MODEL_LIST_CPMG_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_TSMFK01, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_CPMG_2SITE_EXPANDED]
"""The list of the R2eff model together with all dispersion models specifically for CPMG-type experiments."""

MODEL_LIST_R1RHO = [MODEL_NOREX, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_TP02, MODEL_NS_R1RHO_2SITE]
"""The list of all dispersion models specifically for R1rho-type experiments (excluding the R2eff model)."""

MODEL_LIST_R1RHO_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_TP02, MODEL_NS_R1RHO_2SITE]
"""The list of the R2eff model together with all dispersion models specifically for R1rho-type experiments."""
