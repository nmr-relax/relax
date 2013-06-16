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
"""The Meiboom (1961) 2-site on-resonance skewed population R1rho model.

This module is for the function, gradient and Hessian of the M61 skew model.  The model is named after the reference:

    - Meiboom S. (1961).  Nuclear magnetic resonance study of the proton transfer in water.  J. Chem. Phys., 34, 375-388.  (U{DOI: 10.1063/1.1700960<http://dx.doi.org/10.1063/1.1700960>}).

The equation used is::

                           pA^2.pB.delta_omega^2.kex
    R1rho = R1rho' + -------------------------------------- ,
                     kex^2 + pA^2.delta_omega^2 + omega_1^2

where R1rho' is the R1rho value in the absence of exchange, kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, delta_omega is the chemical shift difference between the two states, and omega_1 = omega_e is the effective field in the rotating frame.
"""

# Python module imports.
from math import pi


def r1rho_M61b(r1rho_prime=None, pA=None, dw=None, kex=None, spin_lock_fields=None, back_calc=None, num_points=None):
    """Calculate the R1rho values for the M61 skew model.

    See the module docstring for details.


    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          float
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword dw:                The chemical exchange difference between states A and B in rad/s.
    @type dw:                   float
    @keyword kex:               The kex parameter value (the exchange rate in rad/s).
    @type kex:                  float
    @keyword spin_lock_fields:  The spin-lock field strengths (Hz).
    @type spin_lock_fields:     numpy rank-1 float array
    @keyword back_calc:         The array for holding the back calculated R1rho values.  Each element corresponds to one of the spin-lock fields.
    @type back_calc:            numpy rank-1 float array
    @keyword num_points:        The number of points on the dispersion curve, equal to the length of the spin_lock_fields and back_calc arguments.
    @type num_points:           int
    """

    # The B population.
    pB = 1.0 - pA

    # Repetitive calculations (to speed up calculations).
    pA2dw2 = pA**2 * dw**2
    kex2_pA2dw2 = kex**2 + pA2dw2

    # The numerator.
    numer = pA2dw2 * pB * kex

    # Loop over the dispersion points, back calculating the R1rho values.
    for i in range(num_points):
        # Catch zeros (to avoid pointless mathematical operations).
        if numer == 0.0:
            back_calc[i] = r1rho_prime
            continue

        # Denominator.
        denom = kex2_pA2dw2 + (2.0*pi*spin_lock_fields[i])**2

        # Avoid divide by zero.
        if denom == 0.0:
            back_calc[i] = 1e100
            continue

        # R1rho calculation.
        back_calc[i] = r1rho_prime + numer / denom
