###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The Trott and Palmer (2002) 2-site exchange R1rho U{TP02<http://wiki.nmr-relax.com/TP02>} model.

Description
===========

This module is for the function, gradient and Hessian of the U{TP02<http://wiki.nmr-relax.com/TP02>} model.


References
==========

The model is named after the reference:

    - Trott, O. and Palmer, 3rd, A. G. (2002). R1rho relaxation outside of the fast-exchange limit. I{J. Magn. Reson.}, B{154}(1), 157-160. (U{DOI: 10.1006/jmre.2001.2466<http://dx.doi.org/10.1006/jmre.2001.2466>}).


Code origin
===========

The code originates as the funTrottPalmer.m Matlab file from the sim_all.tar file attached to task #7712 (U{https://gna.org/task/?7712}).  This is code from Nikolai Skrynnikov and Martin Tollinger.

Links to the copyright licensing agreements from all authors are:

    - Nikolai Skrynnikov, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4279},
    - Martin Tollinger, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4276}.


Links
=====

More information on the TP02 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/TP02>},
    - U{relax manual<http://www.nmr-relax.com/manual/TP02_2_site_exchange_R1_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#TP02>}.
"""

# Python module imports.
from numpy import abs, arctan2, array, isfinite, min, sin, sum


def r1rho_TP02(r1rho_prime=None, omega=None, offset=None, pA=None, pB=None, dw=None, kex=None, R1=0.0, spin_lock_fields=None, spin_lock_fields2=None, num_points=None):
    """Calculate the R1rho' values for the TP02 model.

    See the module docstring for details.  This is the Trott and Palmer (2002) equation according to Korzhnev (J. Biomol. NMR (2003), 26, 39-48).


    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          float
    @keyword omega:             The chemical shift for the spin in rad/s.
    @type omega:                float
    @keyword offset:            The spin-lock offsets for the data.
    @type offset:               numpy rank-1 float array
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword pB:                The population of state B.
    @type pB:                   float
    @keyword dw:                The chemical exchange difference between states A and B in rad/s.
    @type dw:                   float
    @keyword kex:               The kex parameter value (the exchange rate in rad/s).
    @type kex:                  float
    @keyword R1:                The R1 relaxation rate.
    @type R1:                   float
    @keyword spin_lock_fields:  The R1rho spin-lock field strengths (in rad.s^-1).
    @type spin_lock_fields:     numpy rank-1 float array
    @keyword spin_lock_fields2: The R1rho spin-lock field strengths squared (in rad^2.s^-2).  This is for speed.
    @type spin_lock_fields2:    numpy rank-1 float array
    @keyword num_points:        The number of points on the dispersion curve, equal to the length of the spin_lock_fields.
    @type num_points:           int
    """

    # Repetitive calculations (to speed up calculations).
    Wa = omega                  # Larmor frequency [s^-1].
    Wb = omega + dw             # Larmor frequency [s^-1].
    kex2 = kex**2
    W = pA*Wa + pB*Wb           # Pop-averaged Larmor frequency [s^-1].
    da = Wa - offset            # Offset of spin-lock from A.
    db = Wb - offset            # Offset of spin-lock from B.
    d = W - offset              # Offset of spin-lock from pop-average.
    da2 = da**2
    db2 = db**2
    d2 = d**2

    # The numerator.
    numer = pA * pB * dw**2 * kex

    # We assume that A resonates at 0 [s^-1], without loss of generality.
    waeff2 = spin_lock_fields2 + da2       # Effective field at A.
    wbeff2 = spin_lock_fields2 + db2       # Effective field at B.
    weff2 = spin_lock_fields2 + d2         # Effective field at pop-average.

    # Catch math domain error of dividing with 0.
    # This is when weff2 = 0.
    if min(abs(weff2)) == 0:
        R2eff = array([1e100]*num_points)

        return R2eff

    # The rotating frame flip angle.
    theta = arctan2(spin_lock_fields, d)

    # Repetitive calculations (to speed up calculations).
    sin_theta2 = sin(theta)**2
    R1_cos_theta2 = R1 * (1.0 - sin_theta2)
    R1rho_prime_sin_theta2 = r1rho_prime * sin_theta2

    # Denominator.
    denom = waeff2 * wbeff2 / weff2 + kex2
    #denom_extended = waeff2*wbeff2/weff2+kex2-2*sin_theta2*pA*pB*dw**2
 
    # Catch math domain error of dividing with 0.
    # This is when denom=0.
    if min(abs(denom)) == 0:
        R1rho = array([1e100]*num_points)

        return R1rho

    # R1rho calculation.
    R1rho = R1_cos_theta2 + R1rho_prime_sin_theta2 + sin_theta2 * numer / denom

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(R1rho)):
        R1rho = array([1e100]*num_points)

    return R1rho
