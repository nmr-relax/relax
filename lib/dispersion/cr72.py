###############################################################################
#                                                                             #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""The Carver and Richards (1972) 2-site all time scale exchange U{CR72<http://wiki.nmr-relax.com/CR72>} and U{CR72 full<http://wiki.nmr-relax.com/CR72_full>} models.

Description
===========

This module is for the function, gradient and Hessian of the U{CR72<http://wiki.nmr-relax.com/CR72>} and U{CR72 full<http://wiki.nmr-relax.com/CR72_full>} models.


References
==========

The model is named after the reference:

    - Carver, J. P. and Richards, R. E. (1972).  General 2-site solution for chemical exchange produced dependence of T2 upon Carr-Purcell pulse separation.  I{J. Magn. Reson.}, B{6}, 89-105.  (U{DOI: 10.1016/0022-2364(72)90090-X<http://dx.doi.org/10.1016/0022-2364(72)90090-X>}).


Equations
=========

The equation used is::

    R2eff = 1/2 [ R2A0 + R2B0 + kex - 2.nu_cpmg.cosh^-1 (D+.cosh(eta+) - D-.cos(eta-)) ] ,

where::

           1 /        Psi + 2delta_omega^2 \ 
    D+/- = - | +/-1 + -------------------- | ,
           2 \        sqrt(Psi^2 + zeta^2) /

                           1
    eta+/- = 2^(-3/2) . -------- sqrt(+/-Psi + sqrt(Psi^2 + zeta^2)) ,
                        nu_cpmg

    Psi = (R2A0 - R2B0 - pA.kex + pB.kex)^2 - delta_omega^2 + 4pA.pB.kex^2 ,

    zeta = 2delta_omega (R2A0 - R2B0 - pA.kex + pB.kex).

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states in ppm.


CR72 model
----------

Importantly for the implementation of this model, it is assumed that R2A0 and R2B0 are identical.  This simplifies some of the equations to::

    R2eff = R20 + kex/2 - nu_cpmg.cosh^-1 (D+.cosh(eta+) - D-.cos(eta-) ,

where::

    Psi = kex^2 - delta_omega^2 ,

    zeta = -2delta_omega (pA.kex - pB.kex).


Links
=====

More information on the CR72 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/CR72>},
    - U{relax manual<http://www.nmr-relax.com/manual/reduced_CR72_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#CR72>}.

More information on the CR72 full model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/CR72_full>},
    - U{relax manual<http://www.nmr-relax.com/manual/full_CR72_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#CR72_full>}.
"""

# Python module imports.
from numpy import arccosh, array, cos, cosh, isfinite, fabs, min, max, multiply, sqrt, subtract, sum
from numpy.ma import fix_invalid, masked_greater_equal, masked_less, masked_where

# Repetitive calculations (to speed up calculations).
eta_scale = 2.0**(-3.0/2.0)

def r2eff_CR72(r20a=None, r20a_orig=None, r20b=None, r20b_orig=None, pA=None, dw=None, dw_orig=None, kex=None, cpmg_frqs=None, back_calc=None):
    """Calculate the R2eff values for the CR72 model.

    See the module docstring for details.


    @keyword r20a:          The R20 parameter value of state A (R2 with no exchange).
    @type r20a:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r20a_orig:     The R20 parameter value of state A (R2 with no exchange). This is only for faster checking of zero value, which result in no exchange.
    @type r20a_orig:        numpy float array of rank-1
    @keyword r20b:          The R20 parameter value of state B (R2 with no exchange).
    @type r20b:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r20b_orig:     The R20 parameter value of state B (R2 with no exchange). This is only for faster checking of zero value, which result in no exchange.
    @type r20b_orig:        numpy float array of rank-1
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy array of rank [NE][NS][NM][NO][ND]
    @keyword dw_orig:       The chemical exchange difference between states A and B in ppm. This is only for faster checking of zero value, which result in no exchange.
    @type dw_orig:          numpy float array of rank-1
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced if max_etapos in cosh function is violated.
    t_dw_zero = False
    t_max_etapos = False

    # Catch parameter values that will result in no exchange, returning flat R2eff = R20 lines (when kex = 0.0, k_AB = 0.0).
    # Test if pA or kex is zero.
    if kex == 0.0 or pA == 1.0:
        back_calc[:] = r20a
        return

    # Test if dw is zero. Create a mask for the affected spins to replace these with R20 at the end of the calculationWait for replacement, since this is spin specific.
    if min(fabs(dw_orig)) == 0.0:
        t_dw_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)

    # The B population.
    pB = 1.0 - pA

    # Repetitive calculations (to speed up calculations).
    dw2 = dw**2
    r20_kex = (r20a + r20b + kex) / 2.0
    k_BA = pA * kex
    k_AB = pB * kex

    # The Psi and zeta values.
    if sum(r20a_orig - r20b_orig) != 0.0:
        fact = r20a - r20b - k_BA + k_AB
        Psi = fact**2 - dw2 + 4.0*pA*pB*kex**2
        zeta = 2.0*dw * fact
    else:
        Psi = kex**2 - dw2
        zeta = -2.0*dw * (k_BA - k_AB)

    # More repetitive calculations.
    sqrt_psi2_zeta2 = sqrt(Psi**2 + zeta**2)

    # The D+/- values.
    D_part = (Psi + 2.0*dw2) / sqrt_psi2_zeta2
    Dpos = 0.5 * (1.0 + D_part)
    Dneg = 0.5 * (-1.0 + D_part)

    # Partial eta+/- values.
    etapos = eta_scale * sqrt(Psi + sqrt_psi2_zeta2) / cpmg_frqs
    etaneg = eta_scale * sqrt(-Psi + sqrt_psi2_zeta2) / cpmg_frqs

    # Catch math domain error of cosh(val > 710).
    # This is when etapos > 710.
    if max(etapos) > 700:
        t_max_etapos = True
        mask_max_etapos = masked_greater_equal(etapos, 700.0)
        # To prevent math errors, set etapos to 1.
        etapos[mask_max_etapos.mask] = 1.0

    # The arccosh argument - catch invalid values.
    fact = Dpos * cosh(etapos) - Dneg * cos(etaneg)
    if min(fact) < 1.0:
        back_calc[:] = r20_kex
        return

    # Calculate R2eff. This uses the temporary buffer and fill directly to back_calc.
    multiply(cpmg_frqs,  arccosh(fact), out=back_calc)
    subtract(r20_kex, back_calc, out=back_calc)

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20a[mask_dw_zero.mask]

    # If eta_pos above 700.
    if t_max_etapos:
        back_calc[mask_max_etapos.mask] = r20a[mask_max_etapos.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
