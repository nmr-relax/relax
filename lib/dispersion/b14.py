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
    R2eff = ------------------ -  ------ * cosh^-1 * v1c - ------ ln( --- + ------------------ * (v2 + 2*kAB*pD ) )   
                  2                Trel                     Trel    (  2    2*sqrt(v1c^2 -1 )                     )

                            1      ( 1+y            1-y                          )
          = R2eff(CR72) - ------ ln( --- + ------------------ * (v2 + 2*kAB*pD ) )   
                           Trel    (  2    2*sqrt(v1c^2 -1 )                     )

Which have these following definitions::
    v1c = F0 * cosh(tauCP * E0)- F2 * cosh(tauCP * E2) 
    v1s = F0 * sinh(tauCP * E0)- F2 * sinh(tauCP * E2) 
    v2*N = v1s * (OB-OA) + 4OB * F1^a * sinh(tauCP * E1) 
    pD N = v1s + (F1^a + F1^b) * sinh(tauCP * E1)
    v3 = ( v2^2 + 4 * kBA * kAB * pD^2 )^1/2 
    y = ( (v1c-v3)/(v1c+v3) )^NCYC

Note, E2 is complex. If |x| denotes the complex modulus:<br>
    cosh(tauCP * E2) = cos(tauCP * |E2|)
    sinh(tauCP * E2) = i sin(tauCP * |E2|)

The term pD is based on product of the off diagonal elements in the CPMG propagator (Supplementary Section 3).

It is interesting to consider the region of validity of the Carver Richards result.
The two results are equal when the correction is zero, which is true when

    sqrt(v1c^2-1) ~ v2 + 2*kAB * pD

This occurs when 2*kAB * pD tends to zero, and so v2=v3.
Setting "kAB * pD" to zero, amounts to neglecting magnetisation that starts on the ground state ensemble and end on the excited state ensemble and vice versa.
This will be a good approximation when pA >> p_B.

In practise, significant deviations from the Carver Richards equation can be incurred if pB > 1 %.
Incorporation of the correction term into equation (50), results in an improved description of the CPMG experiment over the Carver Richards equation.

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
from numpy import arccosh, cos, cosh, sqrt


def r2eff_B14(r20a=None, r20b=None, pA=None, dw=None, kex=None, cpmg_frqs=None, back_calc=None, num_points=None):
    """
    """

    return None
