###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
# Copyright (C) 2014 Andrew Baldwin                                           #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""The Baldwin (2014) 2-site exact solution model for all time scales U{B14<http://wiki.nmr-relax.com/B14>}.

Description
===========

This module is for the function, gradient and Hessian of the U{B14<http://wiki.nmr-relax.com/B14>} model.


References
==========

The model is named after the reference:

    - Andrew J. Baldwin (2014).  An exact solution for R2,eff in CPMG experiments in the case of two site chemical exchange.  I{J. Magn. Reson.}.  (U{DOI: 10.1016/j.jmr.2014.02.023 <http://dx.doi.org/10.1016/j.jmr.2014.02.023>}).


Equations
=========

The equation used is::

            R2A0 + R2B0 + kex      Ncyc                      1      ( 1+y            1-y                          )
    R2eff = ------------------ -  ------ * cosh^-1 * v1c - ------ ln( --- + ------------------ * (v2 + 2*kAB*pD ) ) ,
                  2                Trel                     Trel    (  2    2*sqrt(v1c^2 -1 )                     )

                            1      ( 1+y            1-y                          )
          = R2eff(CR72) - ------ ln( --- + ------------------ * (v2 + 2*kAB*pD ) ) ,
                           Trel    (  2    2*sqrt(v1c^2 -1 )                     )

Which have these following definitions::

    v1c = F0 * cosh(tauCP * E0)- F2 * cosh(tauCP * E2) ,
    v1s = F0 * sinh(tauCP * E0)- F2 * sinh(tauCP * E2) ,
    v2*N = v1s * (OB-OA) + 4OB * F1^a * sinh(tauCP * E1) ,
    pD N = v1s + (F1^a + F1^b) * sinh(tauCP * E1) ,
    v3 = ( v2^2 + 4 * kBA * kAB * pD^2 )^1/2 ,
    y = ( (v1c-v3)/(v1c+v3) )^NCYC ,

Note, E2 is complex. If |x| denotes the complex modulus::

    cosh(tauCP * E2) = cos(tauCP * |E2|) ,
    sinh(tauCP * E2) = i sin(tauCP * |E2|) ,

The term pD is based on product of the off diagonal elements in the CPMG propagator (Supplementary Section 3).

It is interesting to consider the region of validity of the Carver Richards result.  The two results are equal when the correction is zero, which is true when::

    sqrt(v1c^2-1) ~ v2 + 2*kAB * pD ,

This occurs when 2*kAB * pD tends to zero, and so v2=v3.  Setting "kAB * pD" to zero, amounts to neglecting magnetisation that starts on the ground state ensemble and end on the excited state ensemble and vice versa.  This will be a good approximation when pA >> p_B.

In practise, significant deviations from the Carver Richards equation can be incurred if pB > 1 %.  Incorporation of the correction term into equation (50), results in an improved description of the CPMG experiment over the Carver Richards equation.

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states in ppm.


Links
=====

More information on the B14 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/B14>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_reduced_B14_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#B14>}.

More information on the B14 full model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/B14_full>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_full_B14_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#B14_full>}.


Comparison to CR72 model
========================

Comparison to CR72 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/CR72>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_reduced_CR72_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#CR72>}.

Comparison to CR72 full model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/CR72_full>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_full_CR72_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#CR72_full>}.
"""

# Python module imports.
from numpy import any, arccosh, arctan2, cos, cosh, fabs, isfinite, log, max, min, power, sin, sinh, sqrt, sum
from numpy.ma import fix_invalid, masked_greater_equal, masked_where

# Repetitive calculations (to speed up calculations).
g_fact = 1/sqrt(2)


def r2eff_B14(r20a=None, r20b=None, pA=None, dw=None, dw_orig=None, kex=None, ncyc=None, inv_tcpmg=None, tcp=None, back_calc=None):
    """Calculate the R2eff values for the CR72 model.

    See the module docstring for details.


    @keyword r20a:          The R20 parameter value of state A (R2 with no exchange).
    @type r20a:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r20b:          The R20 parameter value of state B (R2 with no exchange).
    @type r20b:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw_orig:       The chemical exchange difference between states A and B in ppm. This is only for faster checking of zero value, which result in no exchange.
    @type dw_orig:          numpy float array of rank-1
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword ncyc:          The matrix exponential power array. The number of CPMG blocks.
    @type ncyc:             numpy int16 array of rank [NE][NS][NM][NO][ND]
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced if math function is violated.
    t_dw_zero = False
    t_max_e = False
    t_v3_N_zero = False
    t_log_tog_neg = False
    t_v1c_less_one = False

    # Catch parameter values that will result in no exchange, returning flat R2eff = R20 lines (when kex = 0.0, k_AB = 0.0).
    # Test if pA or kex is zero.
    if kex == 0.0 or pA == 1.0:
        back_calc[:] = r20a
        return

    # Test if dw is zero. Create a mask for the affected spins to replace these with R20 at the end of the calculationWait for replacement, since this is spin specific.
    if min(fabs(dw_orig)) == 0.0:
        t_dw_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)

    # Parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex

    # Repetitive calculations (to speed up calculations).
    deltaR2 = r20a - r20b
    dw2 = dw**2
    two_tcp = 2.0 * tcp

    # The Carver and Richards (1972) alpha_minus short notation.
    alpha_m = deltaR2 + k_AB - k_BA
    zeta = 2.0 * dw * alpha_m
    Psi = alpha_m**2 + 4.0 * k_BA * k_AB - dw2

    # Get the real and imaginary components of the exchange induced shift.
    # Trigonometric functions faster than square roots.
    quad_zeta2_Psi2 = (zeta**2 + Psi**2)**0.25
    fact = 0.5 * arctan2(-zeta, Psi)
    g3 = cos(fact) * quad_zeta2_Psi2
    g4 = sin(fact) * quad_zeta2_Psi2

    # Repetitive calculations (to speed up calculations).
    g32 = g3**2
    g42 = g4**2

    # Time independent factors.
    # N = oG + oE.
    N = g3 + g4*1j

    NNc = g32 + g42

    # F0.
    F0 = (dw2 + g32) / NNc

    # F2.
    F2 = (dw2 - g42) / NNc

    # t1 = (-dw + g4) * (complex(-dw, -g3)) / NNc #t1.

    # t2.
    F1b = (dw + g4) * (dw - g3*1j) / NNc

    # t1 + t2.
    F1a_plus_b = (2. * dw2 + zeta*1j) / NNc

    # Derived from relaxation.
    # E0 = -2.0 * tcp * (F00R - f11R).
    E0 = two_tcp * g3

    # Catch math domain error of sinh(val > 710).
    # This is when E0 > 710.
    if max(E0) > 700:
        t_max_e = True
        mask_max_e = masked_greater_equal(E0, 700.0)
        # To prevent math errors, set e_zero to 1.
        E0[mask_max_e.mask] = 1.0

    # Derived from chemical shifts  #E2 = complex(0, -2.0 * tcp * (F00I - f11I)).
    E2 = two_tcp * g4

    # Mixed term (complex) (E0 - iE2)/2.
    E1 = (g3 - g4*1j) * tcp

    # Complex.
    v1s = F0 * sinh(E0) - F2 * sin(E2)*1j

    # -2 * oG * t2.
    v4 = F1b * (-alpha_m - g3 ) + F1b * (dw - g4)*1j

    # Complex.
    ex1c = sinh(E1)

    # Off diagonal common factor. sinh fuctions.
    v5 = (-deltaR2 + kex + dw*1j) * v1s - 2. * (v4 + k_AB * F1a_plus_b) * ex1c

    # Real. The v_1c in paper.
    v1c = F0 * cosh(E0) - F2 * cos(E2)

    # Catch math domain error of sqrt of negative.
    # This is when v1c is less than 1.
    mask_v1c_less_one = v1c < 1.0
    if any(mask_v1c_less_one):
        t_v1c_less_one = True
        v1c[mask_v1c_less_one] = 1.0

    # Exact result for v2v3.
    v3 = sqrt(v1c**2 - 1.)

    y = power( (v1c - v3) / (v1c + v3), ncyc)

    Tog_div = 2. * v3 * N

    # Catch math domain error of division with 0.
    # This is when Tog_div is zero.
    mask_v3_N_zero = Tog_div == 0.0
    if any(mask_v3_N_zero):
        t_v3_N_zero = True
        Tog_div[mask_v3_N_zero] = 1.0

    Tog = 0.5 * (1. + y) + (1. - y) * v5 / Tog_div

    ## -1/Trel * log(LpreDyn).
    # Rpre = (r20a + r20b + kex) / 2.0

    ## Carver and Richards (1972)
    # R2eff_CR72 = Rpre - inv_tcpmg * ncyc *  arccosh(v1c.real)

    ## Baldwin final.
    # Estimate R2eff. relax_time = Trel = 1/inv_tcpmg.
    # R2eff = R2eff_CR72 - inv_tcpmg * log(Tog.real)

    # Catch math domain error of log of negative.
    # This is when Tog.real is negative.
    mask_log_tog_neg = Tog.real < 0.0
    if any(mask_log_tog_neg):
        t_log_tog_neg = True
        Tog.real[mask_log_tog_neg] = 1.0

    # Fastest calculation.
    back_calc[:] = (r20a + r20b + kex) / 2.0 - inv_tcpmg * ( ncyc * arccosh(v1c.real) + log(Tog.real) )

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20a[mask_dw_zero.mask]

    # If E0 is above 700.
    if t_max_e:
        back_calc[mask_max_e.mask] = r20a[mask_max_e.mask]

    # If v1c is less than 1.
    if t_v1c_less_one:
        back_calc[mask_v1c_less_one] = 1e100

    # If Tog_div is zero.
    if t_v3_N_zero:
        back_calc[mask_v3_N_zero] = 1e100

    # If Tog.real is negative.
    if t_log_tog_neg:
        back_calc[mask_log_tog_neg] = 1e100

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
