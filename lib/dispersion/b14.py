###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
# Copyright (C) 2014 Andrew Baldwin                                           #
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

Comparison to CR72 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/CR72>},
    - U{relax manual<http://www.nmr-relax.com/manual/reduced_CR72_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#CR72>}.

Comparison to CR72 full model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/CR72_full>},
    - U{relax manual<http://www.nmr-relax.com/manual/full_CR72_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#CR72_full>}.
"""

# Python module imports.
import numpy
from numpy import arccosh, cos, cosh, log, sin, sinh, sqrt, power


def r2eff_B14(r20a=None, r20b=None, deltaR2=None, alpha_m=None, pA=None, pB=None, dw=None, zeta=None, Psi=None, g_fact=None, kex=None, k_AB=None, k_BA=None, ncyc=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the CR72 model.

    See the module docstring for details.


    @keyword r20a:          The R20 parameter value of state A (R2 with no exchange).
    @type r20a:             float
    @keyword r20b:          The R20 parameter value of state B (R2 with no exchange).
    @type r20b:             float
    @keyword deltaR2:       The difference r20a - r20b.
    @type deltaR2:          float
    @keyword alpha_m:       The Carver and Richards (1972) alpha_minus short notation. alpha_m = deltaR2 + k_AB - k_BA = r20a - r20b + k_AB - k_BA.
    @type alpha_m:          float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword zeta:          The Carver and Richards (1972) zeta notation. zeta = 2 * dw * alpha_m.
    @type zeta:             float
    @keyword Psi:           The Carver and Richards (1972) Psi notation. Psi =  alpha_m**2 + 4 * k_BA * k_AB - dw**2.
    @type Psi:              float
    @keyword g_fact:        The factor g = 1/sqrt(2). This is calculated outside library function, to only be calculated once.
    @type g_fact:           float
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword ncyc:          The matrix exponential power array. The number of CPMG blocks.
    @type ncyc:             numpy int16, rank-1 array
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # Repetitive calculations (to speed up calculations).
    dw2 = dw**2
    zeta2 = zeta**2
    Psi2 = Psi**2
    two_tcp = 2.0 * tcp
    sqrt_zeta2_Psi2 = sqrt(zeta2 + Psi2)

    # Get the real and imaginary components of the exchange induced shift.
    g3 = g_fact * sqrt( Psi + sqrt_zeta2_Psi2)
    g4 = g_fact * sqrt(-Psi + sqrt_zeta2_Psi2)

    # Repetitive calculations (to speed up calculations).
    g32 = g3**2
    g42 = g4**2

    # Time independent factors.
    # N = oG + oE.
    N = complex(g3, g4)

    NNc = g32 + g42

    # f0.
    f0 = (dw2 + g32) / NNc

    # f2.
    f2 = (dw2 - g42) / NNc

    # t1 = (-dw + g4) * (complex(-dw, -g3)) / NNc #t1.

    # t2.
    t2 = (dw + g4) * complex(dw, -g3) / NNc

    # t1 + t2.
    t1pt2 = complex(2. * dw2, zeta) / NNc

    # -2 * oG * t2.
    oGt2 = complex(-alpha_m - g3, dw - g4) * t2

    # -1/Trel * log(LpreDyn).
    Rpre = (r20a + r20b + kex) / 2.0

    # Derived from relaxation.
    # E0 = -2.0 * tcp * (f00R - f11R).
    E0 =  two_tcp * g3

    # Derived from chemical shifts  #E2 = complex(0,-2.0 * tcp * (f00I - f11I)).
    E2 =  two_tcp * g4

    # Mixed term (complex) (E0 - iE2)/2.
    E1 = complex(g3, -g4) * tcp

    # Real. The v_1c in paper.
    ex0b = f0 * cosh(E0) - f2 * cos(E2)

    # Complex.
    ex0c = f0 * sinh(E0) - f2 * sin(E2) * complex(0, 1.0)

    # Complex.
    ex1c = sinh(E1)

    # Exact result for v2v3.
    v3 = sqrt(ex0b**2 - 1.)

    y = power( (ex0b - v3) / (ex0b + v3), ncyc)

    # Off diagonal common factor. sinh fuctions.
    v2pPdN = complex(-deltaR2 + kex, dw) * ex0c + (-oGt2 - k_AB * t1pt2) * 2. * ex1c

    Tog = (1. + y) / 2. + (1. - y) / (2. * v3) * v2pPdN / N

    # Estimate R2eff. relax_time = Trel = 1/inv_tcpmg.
    Minty = Rpre - ncyc * inv_tcpmg * arccosh(ex0b.real) - inv_tcpmg * log(Tog.real)

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):

        # The full formula.
        back_calc[i] = Minty[i]
