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
from numpy import add, complex, conj, dot
from numpy.linalg import matrix_power
if dep_check.scipy_module:
    from scipy.linalg import expm


def r2eff_ns_2site_star(Rr=None, Rex=None, RCS=None, R=None, M0=None, r20a=None, r20b=None, fA=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation using complex conjugate matrices.

    This function calculates and stores the R2eff values.


    @keyword Rr:            The matrix that contains only the R2 relaxation terms ("Redfield relaxation", i.e. non-exchange broadening).
    @type Rr:               numpy complex64, rank-2, 2D array
    @keyword Rex:           The matrix that contains the exchange terms between the two states A and B.
    @type Rex:              numpy complex64, rank-2, 2D array
    @keyword RCS:           The matrix that contains the chemical shift evolution.  It works here only with X magnetization, and the complex notation allows to evolve in the transverse plane (x, y).
    @type RCS:              numpy complex64, rank-2, 2D array
    @keyword R:             The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    @type R:                numpy complex64, rank-2, 2D array
    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 2D array
    @keyword r20a:          The R2 value for state A in the absence of exchange.
    @type r20a:             float
    @keyword r20b:          The R2 value for state A in the absence of exchange.
    @type r20b:             float
    @keyword fA:            The frequency of state A.
    @type fA:               float
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

    # The matrix that contains only the R2 relaxation terms ("Redfield relaxation", i.e. non-exchange broadening).
    Rr[0, 0] = -r20a
    Rr[1, 1] = -r20b

    # The matrix that contains the chemical shift evolution.  It works here only with X magnetization, and the complex notation allows to evolve in the transverse plane (x, y).
    RCS[1, 1] = complex(0.0, -fA)

    # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    add(Rr, Rex, out=R)
    add(R, RCS, out=R)

    # This is the complex conjugate of the above.  It allows the chemical shift to run in the other direction, i.e. it is used to evolve the shift after a 180 deg pulse.  The factor of 2 is to minimise the number of multiplications for the prop_2 matrix calculation.
    cR2 = conj(R) * 2.0

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
        expm_R_tcp = expm(R*tcp[i])

        # This is the propagator for an element of [delay tcp; 180 deg pulse; 2 times delay tcp; 180 deg pulse; delay tau], i.e. for 2 times tau-180-tau.
        prop_2 = dot(dot(expm_R_tcp, expm(cR2*tcp[i])), expm_R_tcp)

        # Now create the total propagator that will evolve the magnetization under the CPMG train, i.e. it applies the above tau-180-tau-tau-180-tau so many times as required for the CPMG frequency under consideration.
        prop_total = matrix_power(prop_2, power[i])

        # Now we apply the above propagator to the initial magnetization vector - resulting in the magnetization that remains after the full CPMG pulse train.  It is called M of t (t is the time after the CPMG train).
        Moft = dot(prop_total, M0)

        # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
        Mgx = Moft[0].real / M0[0]
        if Mgx == 0.0:
            back_calc[i] = 1e99
        else:
            back_calc[i]= -inv_tcpmg * log(Mgx)
