###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Paul Schanda (https://gna.org/users/pasa)           #
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

The function uses an explicit matrix that contains relaxation, exchange and chemical shift terms. It does the 180deg pulses in the CPMG train with conjugate complex matrices.  The approach of Bloch-McConnell can be found in chapter 3.1 of Palmer, A. G. Chem Rev 2004, 104, 3623-3640.  This function was written, initially in MATLAB, in 2010.

The code was submitted at http://thread.gmane.org/gmane.science.nmr.relax.devel/4132 by Paul Schanda.
"""

# Dependency check module.
import dep_check

# Python module imports.
from math import log
from numpy import conj, dot, matrix
if dep_check.scipy_module:
    from scipy.linalg import expm

# relax module imports.
from lib.linear_algebra.matrix_power import square_matrix_power


def r2eff_ns_2site_star(r20a=None, r20b=None, fg=None, kge=None, keg=None, tcpmg=None, cpmg_frqs=None, back_calc=None, num_points=None):
    """The 2-site numerical solution to the Bloch-McConnell equation using complex conjugate matrices.

    This function calculates and stores the R2eff values.


    @keyword r20a:          The R2 value for state A in the absence of exchange.
    @type r20a:             float
    @keyword r20b:          The R2 value for state A in the absence of exchange.
    @type r20b:             float
    @keyword fg:            The frequency of the ground state.
    @type fg:               unknown
    @keyword kge:           The forward exchange rate from state A to state B.
    @type kge:              float
    @keyword keg:           The reverse exchange rate from state B to state A.
    @type keg:              float
    @keyword tcpmg:         Total duration of the CPMG element (in seconds).
    @type tcpmg:            float
    @keyword cpmg_frqs:     The CPMG nu1 frequencies.
    @type cpmg_frqs:        numpy rank-1 float array
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy rank-1 float array
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the cpmg_frqs and back_calc arguments.
    @type num_points:       int
    """

    # The matrix that contains only the R2 relaxation terms ("Redfield relaxation", i.e. non-exchange broadening).
    Rr  = -1.0 * matrix([[r20b, 0.0], [0.0, r20a]])

    # The matrix that contains the exchange terms between the two states G and E.
    Rex = -1.0 * matrix([[kge, -keg], [-kge, keg]])

    # The matrix that contains the chemical shift evolution.  It works here only with X magnetization, and the complex notation allows to evolve in the transverse plane (x, y).
    RCS = complex(0.0, -1.0) * matrix([[0.0, 0.0], [0.0, fg]])

    # The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R = Rr + Rex + RCS

    # This is the complex conjugate of the above.  It allows the chemical shift to run in the other direction, i.e. it is used to evolve the shift AFTER a 180 deg pulse.  The factor of 2 
    cR2 = conj(R) * 2.0

    # Conversion of kinetic rates.
    kex = kge + keg

    # Calculate relative populations - will be used for generating the equilibrium magnetizations.
    IGeq = keg / kex

    # As the preceding line but for the excited state.
    IEeq = kge / kex

    # This is a vector that contains the initial magnetizations corresponding to ground (G) and excited (E) state transverse magnetizations.
    M0 = matrix([[IGeq], [IEeq]])

    # Replicated calculations for faster operation.
    inv_tcpmg = 1.0 / tcpmg

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Replicated calculations for faster operation.
        tcp = 0.25 / cpmg_frqs[i]

        # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
        expm_R_tcp = expm(R*tcp)

        # This is the propagator for an element of [delay tcp; 180 deg pulse; 2 times delay tcp; 180 deg pulse; delay tau], i.e. for 2 times tau-180-tau.
        prop_2 = dot(dot(expm_R_tcp, expm(cR2*tcp)), expm_R_tcp)

        # Now create the total propagator that will evolve the magnetization under the CPMG train, i.e. it applies the above tau-180-tau-tau-180-tau so many times as required for the CPMG frequency under consideration.
        prop_total = square_matrix_power(prop_2, cpmg_frqs[i]*tcpmg)

        # Now we apply the above propagator to the initial magnetization vector - resulting in the magnetization that remains after the full CPMG pulse train.  It is called M of t (t is the time after the CPMG train).
        Moft = prop_total * M0

        # This and the next line calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
        Mgx = Moft[0].real / M0[0]
        back_calc[i]= -inv_tcpmg * log(Mgx)
