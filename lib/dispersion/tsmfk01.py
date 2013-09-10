###############################################################################
#                                                                             #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013 Edward d'Auvergne                                        #
# Copyright (C) 2013 Troels E. Linnet                                         #
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
"""The Tollinger et al. (2001) 2-site very-slow exchange model, range of microsecond to second time scale.
Applicable in the limit of slow exchange, when |R2A-R2B| << k_AB, kB << 1/tau_CP. R20A is the transverse relaxation rate of site A in the absence of exchange.
2*tau_CP is is the time between successive 180 deg. pulses.

This module is for the function, gradient and Hessian of the TSMFK01 model.  The model is named after the reference:

    - Martin Tollinger, Nikolai R. Skrynnikov, Frans A. A. Mulder, Julie D. Forman-Kay and Lewis E. Kay., (2001)  Slow Dynamics in Folded and Unfolded States of an SH3 Domain, J. Am. Chem. Soc., 2001, 123 (46) (U{DOI: 10.1021/ja011300z<http://dx.doi.org/10.1021/ja011300z>}).

The equation used is::

                                   sin(delta_omega * tau_CP)
    R2Aeff = R20A + k_AB - k_AB * -------------------------  ,
                                   delta_omega * tau_CP

where::

    tau_CP = 1.0/(4*nu_cpmg) ,

R20A is the transverse relaxation rate of site A in the absence of exchange, 2*tau_CP is is the time between successive 180 deg. pulses, k_AB is the forward chemical exchange rate constant, delta_omega is the chemical shift difference between the two states.
"""

# Python module imports.
from math import sin


def r2eff_TSMFK01(r20a=None, dw=None, k_AB=None, tcp=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the TSMFK01 model.

    See the module docstring for details.


    @keyword r20a:          The R20 parameter value of state A (R2 with no exchange).
    @type r20a:             float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword k_AB:          The k_AB parameter value (the forward exchange rate in rad/s).
    @type k_AB:             float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Denominator.
        denom = dw * tcp[i]

        # The numerator.
        numer = sin(denom)

        # Catch zeros (to avoid pointless mathematical operations).
        if numer == 0.0:
            back_calc[i] = r20a + k_AB
            continue

        # Avoid divide by zero.
        if denom == 0.0:
            back_calc[i] = 1e100
            continue

        # The full formula.
        else:
            back_calc[i] = r20a + k_AB - k_AB * numer / denom
