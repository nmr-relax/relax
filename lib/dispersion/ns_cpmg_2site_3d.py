###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Paul Schanda (https://gna.org/users/pasa)           #
# Copyright (C) 2013 Mathilde Lescanne                                        #
# Copyright (C) 2013 Dominique Marion                                         #
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
"""This function performs a numerical fit of 2-site Bloch-McConnell equations for CPMG-type experiments.

The function uses an explicit matrix that contains relaxation, exchange and chemical shift terms.  It does the 180deg pulses in the CPMG train.  The approach of Bloch-McConnell can be found in chapter 3.1 of Palmer, A. G. Chem Rev 2004, 104, 3623-3640.  This function was written, initially in MATLAB, in 2010.

This is the model of the numerical solution for the 2-site Bloch-McConnell equations.  It originates as optimization function number 1 from the fitting_main_kex.py script from Mathilde Lescanne, Paul Schanda, and Dominique Marion (see http://thread.gmane.org/gmane.science.nmr.relax.devel/4138, https://gna.org/task/?7712#comment2 and https://gna.org/support/download.php?file_id=18262).
"""

# Dependency check module.
import dep_check

# Python module imports.
from math import fabs, log
from numpy import dot

# relax module imports.
from lib.dispersion.ns_matrices import rcpmg_3d
from lib.float import isNaN
from lib.linear_algebra.matrix_exponential import matrix_exponential


def r2eff_ns_cpmg_2site_3D(r180x=None, M0=None, r10a=0.0, r10b=0.0, r20a=None, r20b=None, pA=None, pB=None, dw=None, k_AB=None, k_BA=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation.

    This function calculates and stores the R2eff values.


    @keyword r180x:         The X-axis pi-pulse propagator.
    @type r180x:            numpy float64, rank-2, 7D array
    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword r10a:          The R1 value for state A.
    @type r10a:             float
    @keyword r10b:          The R1 value for state B.
    @type r10b:             float
    @keyword r20a:          The R2 value for state A in the absence of exchange.
    @type r20a:             float
    @keyword r20b:          The R2 value for state B in the absence of exchange.
    @type r20b:             float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:       int
    @keyword power:         The matrix exponential power array.
    @type power:            numpy int16, rank-1 array
    """

    # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R = rcpmg_3d(R1A=r10a, R1B=r10b, R2A=r20a, R2B=r20b, pA=pA, pB=pB, dw=dw, k_AB=k_AB, k_BA=k_BA)

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Initial magnetisation.
        Mint = M0

        # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
        Rexpo = matrix_exponential(R*tcp[i])

        # Loop over the CPMG elements, propagating the magnetisation.
        for j in range(2*power[i]):
            Mint = dot(Rexpo, Mint)
            Mint = dot(r180x, Mint)
            Mint = dot(Rexpo, Mint)

        # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
        Mx = fabs(Mint[1] / pA)
        if Mx <= 0.0 or isNaN(Mx):
            back_calc[i] = 1e99
        else:
            back_calc[i]= -inv_tcpmg * log(Mx)
