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
"""The Luz and Meiboom (1963) 2-site fast exchange model."""

MODEL_CR72 = 'CR72'
"""The Carver and Richards (1972) 2-site model for all time scales."""

MODEL_LIST_DISP = [MODEL_NOREX, MODEL_LM63, MODEL_CR72]
"""The list of all dispersion models (excluding the R2eff model)."""

MODEL_LIST_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_CR72]
"""The list of the R2eff model together with all dispersion models."""
