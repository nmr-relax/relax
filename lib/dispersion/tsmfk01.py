###############################################################################
#                                                                             #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
# Copyright (C) 2013 Troels E. Linnet                                         #
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
"""The Tollinger et al (2001) 2-site very-slow exchange U{TSMFK01<http://wiki.nmr-relax.com/TSMFK01>} model.

Description
===========

Applicable in the limit of slow exchange, range of microsecond to second time scale, when |R2A-R2B| << k_AB, kB << 1/tau_CP.  R20A is the transverse relaxation rate of site A in the absence of exchange.  2*tau_CP is is the time between successive 180 degree pulses.

This module is for the function, gradient and Hessian of the U{TSMFK01<http://wiki.nmr-relax.com/TSMFK01>} model


References
==========

The model is named after the reference:

    - Tollinger, M., Skrynnikov, N. R., Mulder, F. A. A., Forman-Kay, J. D. and Kay, L. E. (2001).  Slow Dynamics in Folded and Unfolded States of an SH3 Domain, I{J. Am. Chem. Soc.}, B{123} (46) (U{DOI: 10.1021/ja011300z<http://dx.doi.org/10.1021/ja011300z>}).


Equations
=========

The equation used is::

                                   sin(delta_omega * tau_CP)
    R2Aeff = R20A + k_AB - k_AB * -------------------------  ,
                                   delta_omega * tau_CP

where::

    tau_CP = 1.0/(4*nu_cpmg) ,

R20A is the transverse relaxation rate of site A in the absence of exchange, 2*tau_CP is is the time between successive 180 deg. pulses, k_AB is the forward chemical exchange rate constant, delta_omega is the chemical shift difference between the two states.


Links
=====

More information on the TSMFK01 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/TSMFK01>},
    - U{relax manual<http://www.nmr-relax.com/manual/TSMFK01_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#TSMFK01>}.
"""

# Python module imports.
from numpy import array, fabs, min, sin, isfinite, sum
from numpy.ma import fix_invalid, masked_where


def r2eff_TSMFK01(r20a=None, dw=None, dw_orig=None, k_AB=None, tcp=None, back_calc=None):
    """Calculate the R2eff values for the TSMFK01 model.

    See the module docstring for details.


    @keyword r20a:          The R20 parameter value of state A (R2 with no exchange).
    @type r20a:             numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword dw_orig:       The chemical exchange difference between states A and B in ppm. This is only for faster checking of zero value, which result in no exchange.
    @type dw_orig:          numpy float array of rank-1
    @keyword k_AB:          The k_AB parameter value (the forward exchange rate in rad/s).
    @type k_AB:             float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][[NM][NO][ND]
    """

    # Flag to tell if values should be replaced if max_etapos in cosh function is violated.
    t_dw_zero = False

    # Catch parameter values that will result in no exchange, returning flat R2eff = R20 lines (when kex = 0.0, k_AB = 0.0).
    # Test if k_AB is zero.
    if k_AB == 0.0:
        back_calc[:] = r20a
        return

    # Test if dw is zero. Wait for replacement, since this is spin specific.
    if min(fabs(dw_orig)) == 0.0:
        t_dw_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)

    # Denominator.
    denom = dw * tcp

    # The numerator.
    numer = sin(denom)

    # Catch zeros (to avoid pointless mathematical operations).
    # This will result in no exchange, returning flat lines.
    if min(fabs(numer)) == 0.0:
        # Calculate R2eff for forward.
        back_calc[:] = r20a + k_AB
    else:
        # Calculate R2eff.
        back_calc[:] = r20a + k_AB - k_AB * numer / denom

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20a[mask_dw_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
