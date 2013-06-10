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
"""The Ishima and Torchia (1999) 2-site model for all time scales with pA >> pB.

This module is for the function, gradient and Hessian of the IT99 model.  The model is named after the reference:

    Ishima R. and Torchia D.A. (1999).  Estimating the time scale of chemical exchange of proteins from measurements of transverse relaxation rates in solution.  J. Biomol. NMR, 14, 369-372.  (U{DOI: 10.1023/A:1008324025406<http://dx.doi.org/10.1023/A:1008324025406>}).

The equation used is:

              phi_ex * tex
    Rex ~= ------------------- ,
           1 + omega_a^2*tex^2

    phi_ex = pA * pB * delta_omega^2 ,
    
    omega_a^2 = sqrt(omega_1^4 + pA^2*delta_omega^4) ,

    R2eff = R20 + Rex ,

where tex = 1/(2kex), kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states.
"""

# Python module imports.
from math import sqrt


def r2eff_IT99(r20=None, phi_ex=None, padw2=None, tex=None, cpmg_frqs=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the IT99 model.

    See the module docstring for details.


    @keyword r20:           The R20 parameter value (R2 with no exchange).
    @type r20:              float
    @keyword phi_ex:        The phi_ex parameter value (pA * pB * delta_omega^2).
    @type phi_ex:           float
    @keyword padw2:         The pA.dw^2 parameter value.
    @type padw2:            float
    @keyword tex:           The tex parameter value (the time of exchange in s/rad).
    @type tex:              float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_poinst:       int
    """

    # Repetitive calculations (to speed up calculations).
    kex = 0.5 / tex
    tex2 = tex**2
    pa2dw4 = padw2**2

    # The numerator.
    numer = phi_ex * tex

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Catch zeros (to avoid pointless mathematical operations).
        if numer == 0.0:
            back_calc[i] = r20
            continue

        # Denominator.
        omega_a2 = sqrt((2.0*pi*cpmg_frqs[i])**4 + pa2dw4
        denom = 1.0 + omega_a2 * tex2

        # Avoid divide by zero.
        if denom == 0.0:
            back_calc[i] = 1e100
            continue

        # R2eff calculation.
        back_calc[i] = r20 + numer / demon
