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
"""The Luz and Meiboom (1963) 2-site fast exchange model.

This module is for the function, gradient and Hessian of the LM63 model.  The model is named after the reference:

    - Luz, S. and Meiboom S., (1963)  Nuclear Magnetic Resonance study of protolysis of trimethylammonium ion in aqueous solution - order of reaction with respect to solvent, J. Chem. Phys. 39, 366-370 (U{DOI: 10.1063/1.1734254<http://dx.doi.org/10.1063/1.1734254>}).

The equation used is::

                  phi_ex   /     4 * nu_cpmg         /     kex     \ \ 
    R2eff = R20 + ------ * | 1 - -----------  * tanh | ----------- | | ,
                   kex     \         kex             \ 4 * nu_cpmg / /

where::

    phi_ex = pA * pB * delta_omega^2 ,

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states.
"""

# Python module imports.
from math import tanh


def r2eff_LM63(r20=None, phi_ex=None, kex=None, cpmg_frqs=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the LM63 model.

    See the module docstring for details.


    @keyword r20:           The R20 parameter value (R2 with no exchange).
    @type r20:              float
    @keyword phi_ex:        The phi_ex parameter value (pA * pB * delta_omega^2).
    @type phi_ex:           float
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # Repetitive calculations (to speed up calculations).
    rex = phi_ex / kex
    kex_4 = 4.0 / kex

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Catch zeros.
        if phi_ex == 0.0:
            back_calc[i] = r20

        # Avoid divide by zero.
        elif kex == 0.0:
            back_calc[i] = 1e100

        # The full formula.
        else:
            back_calc[i] = r20 + rex * (1.0 - kex_4 * cpmg_frqs[i] * tanh(kex / (4.0 * cpmg_frqs[i])))
