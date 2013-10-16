###############################################################################
#                                                                             #
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
"""This function performs a numerical fit of CR72 model extended for MQ CPMG data.

The Carver and Richards (1972) 2-site model for all times scales was extended for multiple quantum (MQ) CPMG data by:

    - Korzhnev, D. M., Kloiber, K., Kanelis, V., Tugarinov, V., and Kay, L. E. (2004).  Probing slow dynamics in high molecular weight proteins by methyl-TROSY NMR spectroscopy: Application to a 723-residue enzyme.  J. Am. Chem. Soc., 126, 3964-3973.  (U{DOI: 10.1021/ja039587i<http://dx.doi.org/10.1021/ja039587i>}).
"""

# Python module imports.
from numpy import arccosh, cos, cosh, log, sin, sqrt


def r2eff_mq_cr72(r20=None, pA=None, pB=None, dw=None, dwH=None, kex=None, k_AB=None, k_BA=None, cpmg_frqs=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The CR72 model extended to MQ CPMG data.

    This function calculates and stores the R2eff values.


    @keyword r20:           The R2 value in the absence of exchange.
    @type r20:              float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword dwH:           The proton chemical exchange difference between states A and B in rad/s.
    @type dwH:              float
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy rank-1 float array
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:       int
    @keyword power:         The matrix exponential power array.
    @type power:            numpy int16, rank-1 array
    """

    # Repetitive calculations (to speed up calculations).
    dw2 = dw**2
    r20_kex = r20 + kex/2.0
    pApBkex2 = k_AB * k_BA
    sqrt_pApBkex2 = sqrt(pApBkex2)
    isqrt_pApBkex2 = 1.j*sqrt_pApBkex2
    sqrt_pBpA = sqrt(pB/pA)
    ikex = 1.j*kex

    # The d+/- values.
    d = dwH + dw
    dpos = d + ikex
    dneg = d - ikex

    # The z+/- values.
    z = dwH - dw
    zpos = z + ikex
    zneg = z - ikex

    # The Psi and zeta values.
    fact = 1.j*dwH + k_BA - k_AB
    Psi = fact**2 - dw2 + 4.0*pApBkex2
    zeta = -2.0*dw * fact

    # More repetitive calculations.
    sqrt_psi2_zeta2 = sqrt(Psi**2 + zeta**2)

    # The D+/- values.
    D_part = (Psi + 2.0*dw2) / sqrt_psi2_zeta2
    Dpos = 0.5 * (1.0 + D_part)
    Dneg = 0.5 * (-1.0 + D_part)

    # Partial eta+/- values.
    eta_scale = sqrt(2.0)
    etapos_part = eta_scale * sqrt(Psi + sqrt_psi2_zeta2)
    etaneg_part = eta_scale * sqrt(-Psi + sqrt_psi2_zeta2)

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Alias delta.
        delta = tcp[i]

        # The full eta+/- values.
        etapos = etapos_part * delta
        etaneg = etaneg_part * delta

        # The mD value.
        mD = isqrt_pApBkex2 / (dpos * zpos) * (zpos + 2.0*dw*sin(zpos*delta)/sin((dpos + zpos)*delta))

        # The mZ value.
        mZ = -isqrt_pApBkex2 / (dneg * zneg) * (dneg - 2.0*dw*sin(dneg*delta)/sin((dneg + zneg)*delta))

        # The Q value.
        Q = 1 - mD**2 + mD*mZ - mZ**2 + 0.5*(mD + mZ)*sqrt_pBpA
        Q = Q.real

        # Part of the equation (catch values < 1 to prevent math domain errors).
        part = Dpos * cosh(etapos) - Dneg * cos(etaneg)
        if part.real < 1.0:
            back_calc[i] = 1e100
            continue

        # The first eigenvalue.
        lambda1 = r20_kex - cpmg_frqs[i] * arccosh(part)

        # The full formula.
        back_calc[i] = lambda1.real - cpmg_frqs[i] * log(Q) / power[i]
