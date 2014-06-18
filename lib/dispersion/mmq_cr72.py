###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The CR72 model extended for MMQ CPMG data, called the U{MMQ CR72<http://wiki.nmr-relax.com/MMQ_CR72>} model.

Description
===========

This module is for the function, gradient and Hessian of the U{MMQ CR72<http://wiki.nmr-relax.com/MMQ_CR72>} model.


References
==========

The Carver and Richards (1972) 2-site model for all times scales was extended for multiple-MQ (MMQ) CPMG data by:

    - Korzhnev, D. M., Kloiber, K., Kanelis, V., Tugarinov, V., and Kay, L. E. (2004).  Probing slow dynamics in high molecular weight proteins by methyl-TROSY NMR spectroscopy: Application to a 723-residue enzyme.  I{J. Am. Chem. Soc.}, B{126}, 3964-3973.  (U{DOI: 10.1021/ja039587i<http://dx.doi.org/10.1021/ja039587i>}).


Links
=====

More information on the MMQ CR72 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/MMQ_CR72>},
    - U{relax manual<http://www.nmr-relax.com/manual/MMQ_CR72_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#MMQ_CR72>}.
"""

# Python module imports.
from numpy import arccosh, cos, cosh, isfinite, fabs, log, min, max, sin, sqrt, sum
from numpy.ma import fix_invalid, masked_greater_equal, masked_where

# Repetitive calculations (to speed up calculations).
eta_scale = 2.0**(-3.0/2.0)


def r2eff_mmq_cr72(r20=None, pA=None, dw=None, dwH=None, kex=None, cpmg_frqs=None, inv_tcpmg=None, tcp=None, back_calc=None):
    """The CR72 model extended to MMQ CPMG data.

    This function calculates and stores the R2eff values.


    @keyword r20:           The R2 value in the absence of exchange.
    @type r20:              numpy float array of rank [NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH:           The proton chemical exchange difference between states A and B in rad/s.
    @type dwH:              numpy float array of rank [NS][NM][NO][ND]
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy float array of rank [NS][NM][NO][ND]
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        numpy float array of rank [NS][NM][NO][ND]
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NS][NM][NO][ND]
    """

    # Once off parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex

    # Flag to tell if values should be replaced if max_etapos in cosh function is violated.
    t_dw_dw_H_zero = False
    t_max_etapos = False

    # Test if pA or kex is zero.
    if kex == 0.0 or pA == 1.0:
        back_calc[:] = r20
        return

    # Test if dw and dwH is zero. Create a mask for the affected spins to replace these with R20 at the end of the calculationWait for replacement, since this is spin specific.
    if min(fabs(dw)) == 0.0 and min(fabs(dwH)) == 0.0:
        t_dw_dw_H_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)
        mask_dw_H_zero = masked_where(dwH == 0.0, dwH)

    # Repetitive calculations (to speed up calculations).
    dw2 = dw**2
    r20_kex = r20 + kex/2.0
    pApBkex2 = k_AB * k_BA
    isqrt_pApBkex2 = 1.j*sqrt(pApBkex2)
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
    etapos_part = eta_scale * sqrt(Psi + sqrt_psi2_zeta2)
    etaneg_part = eta_scale * sqrt(-Psi + sqrt_psi2_zeta2)

    # The full eta+ values.
    etapos = etapos_part / cpmg_frqs

    # Catch math domain error of cosh(val > 710).
    # This is when etapos > 710.
    if max(etapos) > 700:
        t_max_etapos = True
        mask_max_etapos = masked_greater_equal(etapos, 700.0)
        # To prevent math errors, set etapos to 1.
        etapos[mask_max_etapos.mask] = 1.0

    # The full eta - values.
    etaneg = etaneg_part / cpmg_frqs

    # The mD value.
    mD = isqrt_pApBkex2 / (dpos * zpos) * (zpos + 2.0*dw*sin(zpos*tcp)/sin((dpos + zpos)*tcp))

    # The mZ value.
    mZ = -isqrt_pApBkex2 / (dneg * zneg) * (dneg - 2.0*dw*sin(dneg*tcp)/sin((dneg + zneg)*tcp))

    # The Q value.
    Q = 1 - mD**2 + mD*mZ - mZ**2 + 0.5*(mD + mZ)*sqrt_pBpA
    Q = Q.real

    # The first eigenvalue.
    lambda1 = r20_kex - cpmg_frqs * arccosh(Dpos * cosh(etapos) - Dneg * cos(etaneg))

    # The full formula.
    back_calc[:] = lambda1.real - inv_tcpmg * log(Q)

    # Replace data in array.
    # If eta_pos above 700.
    if t_max_etapos:
        back_calc[mask_max_etapos.mask] = r20[mask_max_etapos.mask]

    # Replace data in array.
    # If dw and dwH is zero.
    if t_dw_dw_H_zero:
        back_calc[mask_dw_zero.mask] = r20[mask_dw_zero.mask]
        back_calc[mask_dw_H_zero.mask] = r20[mask_dw_H_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=r20)