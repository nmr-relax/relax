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
"""The Ishima and Torchia (1999) 2-site all time scale exchange (with pA >> pB) U{IT99<http://wiki.nmr-relax.com/IT99>} model.

Description
===========

This module is for the function, gradient and Hessian of the U{IT99<http://wiki.nmr-relax.com/IT99>} model.


References
==========

The model is named after the reference:

    - Ishima R. and Torchia D.A. (1999).  Estimating the time scale of chemical exchange of proteins from measurements of transverse relaxation rates in solution.  I{J. Biomol. NMR}, B{14}, 369-372.  (U{DOI: 10.1023/A:1008324025406<http://dx.doi.org/10.1023/A:1008324025406>}).


Equations
=========

The equation used is::

              phi_ex * tex
    Rex ~= ------------------- ,
           1 + omega_a^2*tex^2

    phi_ex = pA * pB * delta_omega^2 ,

    omega_a^2 = sqrt(omega_1eff^4 + pA^2*delta_omega^4) ,

    R2eff = R20 + Rex ,

where tex = 1/(2kex), kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states.  The effective rotating frame field for a CPMG-type experiment is given by::

    omega_1eff = 4*sqrt(3) * nu_cpmg

and therefore::

    omega_1eff^4 = 2304 * nu_cpmg^4


Links
=====

More information on the IT99 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/IT99>},
    - U{relax manual<http://www.nmr-relax.com/manual/IT99_2_site_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#IT99>}.

"""

# Python module imports.
from numpy import array, isfinite, fabs, sqrt, sum
from numpy.ma import fix_invalid, masked_where


def r2eff_IT99(r20=None, pA=None, dw=None, dw_orig=None, tex=None, cpmg_frqs=None, back_calc=None):
    """Calculate the R2eff values for the IT99 model.

    See the module docstring for details.


    @keyword r20:           The R20 parameter value (R2 with no exchange).
    @type r20:              numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw_orig:       The chemical exchange difference between states A and B in ppm. This is only for faster checking of zero value, which result in no exchange.
    @type dw_orig:          numpy float array of rank-1
    @keyword tex:           The tex parameter value (the time of exchange in s/rad).
    @type tex:              float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced if numer is zero.
    t_dw_zero = False

    # Catch divide with zeros (to avoid pointless mathematical operations).
    if tex == 0.0 or pA == 1.0:
        back_calc[:] = r20
        return

    # Test if dw is zero. Wait for replacement, since this is spin specific.
    if min(fabs(dw_orig)) == 0.0:
        t_dw_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)

    # Parameter conversions.
    pB = 1.0 - pA

    # Repetitive calculations (to speed up calculations).
    dw2 = dw**2
    tex2 = tex**2
    padw2 = pA * dw2
    pa2dw4 = padw2**2

    # The numerator.
    numer = padw2 * pB * tex

    # The effective rotating frame field.
    omega_1eff4 = 2304.0 * cpmg_frqs**4

    # Denominator.
    omega_a2 = sqrt(omega_1eff4 + pa2dw4)
    denom = 1.0 + omega_a2 * tex2

    # R2eff calculation.
    back_calc[:] = r20 + numer / denom

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20[mask_dw_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)