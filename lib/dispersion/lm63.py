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
"""The Luz and Meiboom (1963) 2-site fast exchange U{LM63<http://wiki.nmr-relax.com/LM63>} model.

Description
===========

This module is for the function, gradient and Hessian of the U{LM63<http://wiki.nmr-relax.com/LM63>} model.


References
==========

The model is named after the reference:

    - Luz, S. and Meiboom S., (1963)  Nuclear Magnetic Resonance study of protolysis of trimethylammonium ion in aqueous solution - order of reaction with respect to solvent, I{J. Chem. Phys.}, B{39}, 366-370 (U{DOI: 10.1063/1.1734254<http://dx.doi.org/10.1063/1.1734254>}).


Equations
=========

The equation used is::

                  phi_ex   /     4 * nu_cpmg         /     kex     \ \ 
    R2eff = R20 + ------ * | 1 - -----------  * tanh | ----------- | | ,
                   kex     \         kex             \ 4 * nu_cpmg / /

where::

    phi_ex = pA * pB * delta_omega^2 ,

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states.


Links
=====

More information on the LM63 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/LM63>},
    - U{relax manual<http://www.nmr-relax.com/manual/LM63_2_site_fast_exchange_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#LM63>}.
"""

# Python module imports.
from numpy import any, array, isfinite, min, sum, tanh
from numpy.ma import fix_invalid, masked_where

def r2eff_LM63(r20=None, phi_ex=None, kex=None, cpmg_frqs=None, back_calc=None):
    """Calculate the R2eff values for the LM63 model.

    See the module docstring for details.


    @keyword r20:           The R20 parameter value (R2 with no exchange).
    @type r20:              numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword phi_ex:        The phi_ex parameter value (pA * pB * delta_omega^2).
    @type phi_ex:           numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced if phi_ex is zero.
    t_phi_ex_zero = False

    # Catch divide with zeros (to avoid pointless mathematical operations).
    if kex == 0.0:
        back_calc[:] = r20
        return

    # Catch zeros (to avoid pointless mathematical operations).
    # This will result in no exchange, returning flat lines.
    if min(phi_ex) == 0.0:
        t_phi_ex_zero = True
        mask_phi_ex_zero = masked_where(phi_ex == 0.0, phi_ex)

    # Repetitive calculations (to speed up calculations).
    rex = phi_ex / kex
    kex_4 = 4.0 / kex

    # Calculate R2eff.
    back_calc[:] = r20 + rex * (1.0 - kex_4 * cpmg_frqs * tanh(kex / (4.0 * cpmg_frqs)))

    # Replace data in array.
    # If phi_ex is zero.
    if t_phi_ex_zero:
        back_calc[mask_phi_ex_zero.mask] = r20[mask_phi_ex_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)