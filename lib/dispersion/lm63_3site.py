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
"""The Luz and Meiboom (1963) 3-site fast exchange U{LM63 3-site<http://wiki.nmr-relax.com/LM63_3-site>} model.

Description
===========

This module is for the function, gradient and Hessian of the U{LM63 3-site<http://wiki.nmr-relax.com/LM63_3-site>} model.


References
==========

The model is named after the reference:

    - Luz, S. and Meiboom S., (1963)  Nuclear Magnetic Resonance study of protolysis of trimethylammonium ion in aqueous solution - order of reaction with respect to solvent, I{J. Chem. Phys}. B{39}, 366-370 (U{DOI: 10.1063/1.1734254<http://dx.doi.org/10.1063/1.1734254>}).


Equations
=========

The equation used is::

                   _3_
                   \    phi_ex_i   /     4 * nu_cpmg         /     ki      \ \ 
    R2eff = R20 +   >   -------- * | 1 - -----------  * tanh | ----------- | | .
                   /__     ki      \         ki              \ 4 * nu_cpmg / /
                   i=2

For deconvoluting the parameters, see the relax user manual or the reference:

    - O'Connell, N. E., Grey, M. J., Tang, Y., Kosuri, P., Miloushev, V. Z., Raleigh, D. P., and Palmer, 3rd, A. G. (2009). Partially folded equilibrium intermediate of the villin headpiece HP67 defined by 13C relaxation dispersion. I{J. Biomol. NMR}, B{45}(1-2), 85-98. (U{DOI: 10.1007/s10858-009-9340-0<http://dx.doi.org/10.1007/s10858-009-9340-0>}).


Links
=====

More information on the LM63 3-site model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/LM63_3-site>},
    - U{relax manual<http://www.nmr-relax.com/manual/LM63_3_site_fast_exchange_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#LM63_3-site>}.
"""

# Python module imports.
from numpy import any, fabs, min, tanh, isfinite, sum
from numpy.ma import fix_invalid, masked_where


def r2eff_LM63_3site(r20=None, rex_B=None, rex_C=None, quart_kB=None, quart_kC=None, cpmg_frqs=None, back_calc=None):
    """Calculate the R2eff values for the LM63 3-site model.

    See the module docstring for details.


    @keyword r20:           The R20 parameter value (R2 with no exchange).
    @type r20:              numpy float array of rank [NS][NM][NO][ND]
    @keyword rex_B:         The phi_ex_B / kB parameter value.
    @type rex_B:            numpy float array of rank [NS][NM][NO][ND]
    @keyword rex_C:         The phi_ex_C / kC parameter value.
    @type rex_C:            numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword quart_kB:      Approximate chemical exchange rate constant between sites A and B (the exchange rate in rad/s) divided by 4.
    @type quart_kB:         float
    @keyword quart_kC:      Approximate chemical exchange rate constant between sites A and C (the exchange rate in rad/s) divided by 4.
    @type quart_kC:         float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced.
    t_rex_zero = False
    t_quart_kB_zero = False
    t_quart_kC_zero = False
    t_quart_kB_kC_zero = False

    # Avoid divide by zero.
    if quart_kB == 0.0:
        t_quart_kB_zero = True

    if quart_kC == 0.0:
        t_quart_kC_zero = True

    # Test it both is zero.
    if t_quart_kB_zero and t_quart_kC_zero:
        t_quart_kB_kC_zero = True

    # Test if rex is zero. Wait for replacement, since this is spin specific.
    if min(fabs(rex_B)) == 0.0 and min(fabs(rex_C)) == 0.0:
        t_rex_zero = True
        mask_rex_B_zero = masked_where(rex_B == 0.0, rex_B)
        mask_rex_C_zero = masked_where(rex_C == 0.0, rex_C)

    # Replace data in array.
    # If both quart_kB and quart_kC is zero.
    if t_quart_kB_kC_zero:
        back_calc[:] = r20
    elif t_quart_kB_zero:
        back_calc[:] = r20 + rex_C * (1.0 - cpmg_frqs * tanh(quart_kC / cpmg_frqs) / quart_kC)
    elif t_quart_kC_zero:
        back_calc[:] = r20 + rex_B * (1.0 - cpmg_frqs * tanh(quart_kB / cpmg_frqs) / quart_kB)
    else:
        # Calc R2eff.
        back_calc[:] = r20 + rex_B * (1.0 - cpmg_frqs * tanh(quart_kB / cpmg_frqs) / quart_kB) + rex_C * (1.0 - cpmg_frqs * tanh(quart_kC / cpmg_frqs) / quart_kC)

    # If rex is zero.
    if t_rex_zero:
        back_calc[mask_rex_B_zero.mask] = r20[mask_rex_B_zero.mask]
        back_calc[mask_rex_C_zero.mask] = r20[mask_rex_C_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)