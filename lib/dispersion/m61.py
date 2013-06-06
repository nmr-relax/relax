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
"""The Meiboom (1961) 2-site fast exchange R1rho model.

This module is for the function, gradient and Hessian of the M61 model.  The model is named after the reference:

    Meiboom S. (1961).  Nuclear magnetic resonance study of the proton transfer in water.  J. Chem. Phys., 34, 375-388.  (U{DOI: 10.1063/1.1700960<http://dx.doi.org/10.1063/1.1700960>}).

The equation used is:

                                      phi_ex * kex
    R1rho = R1rho' + sin^2(theta) * ----------------- ,
                                    kex^2 + omega_e^2

where R1rho' is the R1rho value in the absence of exchange, theta is the rotating frame tilt angle,

    phi_ex = pA * pB * delta_omega^2 ,

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, delta_omega is the chemical shift difference between the two states, and omega_e is the effective field in the rotating frame.
"""

# Python module imports.
from math import pi, sin


def r2eff_M61(r1rho_prime=None, phi_ex=None, kex=None, theta=pi/2, spin_lock_fields=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the M61 model.

    See the module docstring for details.


    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          float
    @keyword phi_ex:            The phi_ex parameter value (pA * pB * delta_omega^2).
    @type phi_ex:               float
    @keyword kex:               The kex parameter value (the exchange rate in rad/s).
    @type kex:                  float
    @keyword theta:             The rotating frame tilt angle.
    @type theta:                float
    @keyword spin_lock_fields:  The CPMG nu1 frequencies.
    @type spin_lock_fields:     numpy rank-1 float array
    @keyword back_calc:         The array for holding the back calculated R1rho values.  Each element corresponds to one of the spin-lock fields.
    @type back_calc:            numpy rank-1 float array
    @keyword num_points:        The number of points on the dispersion curve, equal to the length of the spin_lock_fields and back_calc arguments.
    @type num_poinst:           int
    """

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Catch zeros (to avoid pointless mathematical operations).
        if phi_ex == 0.0 or kex == 0.0:
            back_calc[i] = r1rho_prime

        # Avoid divide by zero.
        elif kex == 0.0 and spin_lock_fields[i] == 0.0:
            back_calc[i] = 1e100

        # The full formula.
        else:
            back_calc[i] = r1rho_prime + sin(theta) * phi_ex * kex / (kex**2 + spin_lock_fields[i]**2)
