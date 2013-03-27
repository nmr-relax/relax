###############################################################################
#                                                                             #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""The relaxation dispersion equations."""

# Python module imports.
from math import tanh


def fast_2site(params=None, cpmg_frqs=None, back_calc=None, num_times=None):
    """Back calculate the effective transversal relaxation rate (R2eff).

    The currently supported equation is that for CPMG relaxation dispersion in the fast exchange limit:

        - Millet et al., JACS, 2000, 122, 2867-2877 (equation 19)
        - Kovrigin et al., J. Mag. Res., 2006, 180, 93-104 (equation 1)

    In the future, back-calculation should be available for CPMG relaxation dispersion in the slow exchange limit:
            - Tollinger et al., JACS, 2001, 123, 11341-11352 (equation 2)
    """

    # Loop over the time points.
    for i in range(num_times):
        # Back calculate.
        back_calc[i] = params[0] + params[1] * (1 - 2 * tanh(params[2] / (2 * 4 * cpmg_frqs[i])) * ((4 * cpmg_frqs[i] ) / params[2]))
