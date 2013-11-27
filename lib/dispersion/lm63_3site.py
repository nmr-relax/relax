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
"""The Luz and Meiboom (1963) 3-site fast exchange model.

This module is for the function, gradient and Hessian of the 'LM63 3-site' model.  The model is named after the reference:

    - Luz, S. and Meiboom S., (1963)  Nuclear Magnetic Resonance study of protolysis of trimethylammonium ion in aqueous solution - order of reaction with respect to solvent, J. Chem. Phys. 39, 366-370 (U{DOI: 10.1063/1.1734254<http://dx.doi.org/10.1063/1.1734254>}).

The phi_ex_i and kex_i factors for the 3-site model were derived in the reference:


The equation used is::

                   _3_
                   \    phi_ex_i   /     4 * nu_cpmg         /     ki      \ \ 
    R2eff = R20 +   >   -------- * | 1 - -----------  * tanh | ----------- | | .
                   /__     ki      \         ki              \ 4 * nu_cpmg / /
                   i=2

For deconvoluting the parameters, see the relax user manual or the reference:

    - O'Connell, N. E., Grey, M. J., Tang, Y., Kosuri, P., Miloushev, V. Z., Raleigh, D. P., and Palmer, 3rd, A. G. (2009). Partially folded equilibrium intermediate of the villin headpiece HP67 defined by 13C relaxation dispersion. J. Biomol. NMR, 45(1-2), 85-98. (U{DOI: 10.1007/s10858-009-9340-0<http://dx.doi.org/10.1007/s10858-009-9340-0>}).

"""

# Python module imports.
from math import tanh


def r2eff_LM63_3site(r20=None, rex_B=None, rex_C=None, quart_kB=None, quart_kC=None, cpmg_frqs=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the LM63 3-site model.

    See the module docstring for details.


    @keyword r20:           The R20 parameter value (R2 with no exchange).
    @type r20:              float
    @keyword rex_B:         The phi_ex_B / kB parameter value.
    @type rex_B:            float
    @keyword rex_C:         The phi_ex_C / kC parameter value.
    @type rex_C:            float
    @keyword quart_kB:      Approximate chemical exchange rate constant between sites A and B (the exchange rate in rad/s) divided by 4.
    @type quart_kB:         float
    @keyword quart_kC:      Approximate chemical exchange rate constant between sites A and C (the exchange rate in rad/s) divided by 4.
    @type quart_kC:         float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Catch zeros.
        if rex_B == 0.0 and rex_C == 0.0:
            back_calc[i] = r20

        # Avoid divide by zero.
        elif quart_kB == 0.0 or quart_kC == 0.0:
            back_calc[i] = 1e100

        # The full formula.
        else:
            back_calc[i] = r20
            back_calc[i] += rex_B * (1.0 - cpmg_frqs[i] * tanh(quart_kB * cpmg_frqs[i]) / quart_kB)
            back_calc[i] += rex_C * (1.0 - cpmg_frqs[i] * tanh(quart_kC * cpmg_frqs[i]) / quart_kC)
