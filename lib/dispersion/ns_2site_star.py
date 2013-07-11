###############################################################################
#                                                                             #
# Copyright (C) 2010 Paul Schanda (https://gna.org/users/pasa)                #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""This function that does a numerical fit of CPMG.

The function uses an explicit matrix that contains relaxation, exchange and chemical shift terms. It does the 180deg pulses in the CPMG train with conjugate complex matrices.  The approach of Bloch-McConnell can be found in chapter 3.1 of Palmer, A. G. Chem Rev 2004, 104, 3623–3640.  This function was written, initially in MATLAB, in 2010.

The code was submitted at http://thread.gmane.org/gmane.science.nmr.relax.devel/4132 by Paul Schanda.
"""

# Dependency check module.
import dep_check

# Python module imports.
from math import log
from numpy import conj, dot, matrix
if dep_check.scipy_module:
    from scipy.linalg import expm


def r2eff_ns_2site_star(R2E=None, R2G=None, fg=None, kge=None, keg=None, tcpmg=None, cpmg_frqs=None, back_calc=None, num_points=None):
    """The 2-site numerical solution to the Bloch-McConnell equation using complex conjugate matrices.

    This function calculates and stores the R2eff values.


    @keyword R2E:           Unknown.
    @type R2E:              unknown
    @keyword R2G:           Unknown.
    @type R2G:              unknown
    @keyword fg:            Unknown.
    @type fg:               unknown
    @keyword kge:           Unknown.
    @type kge:              unknown
    @keyword keg:           Unknown.
    @type keg:              unknown
    @keyword tcpmg:         Unknown.
    @type tcpmg:            unknown
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # Initialise some structures.
    Rr  = -1.0 * matrix([[R2G, 0.0],[0.0, R2E]])
    Rex = -1.0 * matrix([[kge, -keg],[-kge, keg]])
    RCS = complex(0.0, -1.0) * matrix([[0.0, 0.0],[0.0, fg]])
    R = Rr + Rex + RCS
    cR = conj(R)

    IGeq = keg / kex
    IEeq = kge / kex
    M0 = matrix([[IGeq], [IEeq]])

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        tcp = 1.0 / (4.0 * cpmg_frqs[i])
        prop_2 = dot(dot(expm(R*tcp), expm(cR*2.0*tcp)), expm(R*tcp))

        prop_total = mpower(prop_2, cpmg_frqs[i]*tcpmg)

        Moft = prop_total * M0

        Mgx = Moft[0].real / M0[0]
        back_calc[i]= -(1.0/tcpmg) * log(Mgx)
