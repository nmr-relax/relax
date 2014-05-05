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
from math import cos,sin, sqrt


def r2eff_B14(r20a=None, r20b=None, pA=None, dw=None, kex=None, power=None, relax_time=None, tcp=None, back_calc=None, num_points=None):
    """Calculate the R2eff values for the CR72 model.

    See the module docstring for details.


    @keyword r20a:          The R20 parameter value of state A (R2 with no exchange).
    @type r20a:             float
    @keyword r20b:          The R20 parameter value of state B (R2 with no exchange).
    @type r20b:             float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword power:         The matrix exponential power array. The number of CPMG blocks.
    @type power:            numpy int16, rank-1 array
    @keyword relax_time:    The total relaxation time period (in seconds).
    @type relax_time:       float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # Conversion from relax parameters, to the exact code of Baldwin.
    pb = 1 - pA
    Trel = relax_time
    ncyc = power

    #########################################################################
    ##### Baldwins code.
    #########################################################################
    pa=(1-pb)
    keg=kex * (1-pb)
    kge=kex * pb
    deltaR2=r20a-r20b
    alpha_m = r20a - r20b  + kge - keg
    #  This is not used
    #nu_cpmg=ncyc/Trel
    #tcp=Trel/(4.0 * ncyc)  #time for one free precession element

    #########################################################################
    #get the real and imaginary components of the exchange induced shift
    g1=2 * dw * alpha_m                            #same as carver richards zeta
    g2=alpha_m**2+4 * keg * kge-dw**2   #same as carver richards psi
    g3=1/sqrt(2) * sqrt(g2+sqrt(g1**2+g2**2))   #trig faster than square roots
    g4=1/sqrt(2) * sqrt(-g2+sqrt(g1**2+g2**2))   #trig faster than square roots
    #########################################################################
    #time independent factors
    N=complex(kge+g3-kge,g4)            #N=oG+oE
    NNc=(g3**2+g4**2)
    f0=(dw**2+g3**2)/(NNc)              #f0
    f2=(dw**2-g4**2)/(NNc)              #f2
    #t1=(-dw+g4) * (complex(-dw,-g3))/(NNc) #t1
    t2=(dw+g4) * (complex(dw,-g3))/(NNc) #t2
    t1pt2=complex(2 * dw**2,g1)/(NNc)     #t1+t2
    oGt2=complex((-deltaR2+keg-kge-g3),(dw-g4)) * t2  #-2 * oG * t2
    Rpre=(r20a+r20b+kex)/2.0   #-1/Trel * log(LpreDyn)
    E0= 2.0 * tcp * g3  #derived from relaxation       #E0=-2.0 * tcp * (f00R-f11R)
    E2= 2.0 * tcp * g4  #derived from chemical shifts  #E2=complex(0,-2.0 * tcp * (f00I-f11I))
    E1=(complex(g3,-g4)) * tcp    #mixed term (complex) (E0-iE2)/2
    ex0b=(f0 * numpy.cosh(E0)-f2 * numpy.cos(E2))               #real
    ex0c=(f0 * numpy.sinh(E0)-f2 * numpy.sin(E2) * complex(0,1.)) #complex
    ex1c=(numpy.sinh(E1))                                   #complex
    v3=numpy.sqrt(ex0b**2-1)  #exact result for v2v3
    y=numpy.power((ex0b-v3)/(ex0b+v3),ncyc)
    v2pPdN=(( complex(-deltaR2+kex,dw) ) * ex0c+(-oGt2-kge * t1pt2) * 2 * ex1c)        #off diagonal common factor. sinh fuctions
    Tog=(((1+y)/2+(1-y)/(2 * v3) * (v2pPdN)/N))
    Minty=Rpre-ncyc/(Trel) * numpy.arccosh((ex0b).real)-1/Trel * numpy.log((Tog.real))  #estimate R2eff

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):

        # The full formula.
        back_calc[i] = Minty[i]
