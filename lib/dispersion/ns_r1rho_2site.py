###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
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
"""This function performs a numerical fit of 2-site Bloch-McConnell equations for R1rho-type experiments.

This is the model of the numerical solution for the 2-site Bloch-McConnell equations.  It originates from the funNumrho.m file from the Skrynikov & Tollinger code (the sim_all.tar file https://gna.org/support/download.php?file_id=18404 attached to https://gna.org/task/?7712#comment5).
"""

# Dependency check module.
import dep_check

# Python module imports.
from math import atan, cos, log, pi, sin, sqrt
from numpy import dot
if dep_check.scipy_module:
    from scipy.linalg import expm

# relax module imports.
from lib.dispersion.ns_matrices import rr1rho_3d
from lib.float import isNaN


def ns_r1rho_2site(M0=None, r1rho_prime=None, omega=None, offset=None, r1=0.0, pA=None, pB=None, dw=None, k_AB=None, k_BA=None, spin_lock_fields=None, relax_time=None, inv_relax_time=None, back_calc=None, num_points=None):
    """The 2-site numerical solution to the Bloch-McConnell equation for R1rho data.

    This function calculates and stores the R1rho values.


    @keyword M0:                This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:                   numpy float64, rank-1, 7D array
    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          float
    @keyword omega:             The chemical shift for the spin in rad/s.
    @type omega:                float
    @keyword offset:            The spin-lock offsets for the data.
    @type offset:               numpy rank-1 float array
    @keyword r1:                The R1 relaxation rate.
    @type r1:                   float
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword pB:                The population of state B.
    @type pB:                   float
    @keyword dw:                The chemical exchange difference between states A and B in rad/s.
    @type dw:                   float
    @keyword k_AB:              The rate of exchange from site A to B (rad/s).
    @type k_AB:                 float
    @keyword k_BA:              The rate of exchange from site B to A (rad/s).
    @type k_BA:                 float
    @keyword spin_lock_fields:  The R1rho spin-lock field strengths (in rad.s^-1).
    @type spin_lock_fields:     numpy rank-1 float array
    @keyword relax_time:        The total relaxation time period for each spin-lock field strength (in seconds).
    @type relax_time:           float
    @keyword inv_relax_time:    The inverse of the relaxation time period for each spin-lock field strength (in inverse seconds).  This is used for faster calculations.
    @type inv_relax_time:       float
    @keyword back_calc:         The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:            numpy rank-1 float array
    @keyword num_points:        The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:           int
    """

    # Repetitive calculations (to speed up calculations).
    Wa = omega                  # Larmor frequency [s^-1].
    Wb = omega + dw             # Larmor frequency [s^-1].

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        Wsl = offset[i]                     # Larmor frequency of spin lock [s^-1].
        dA = Wa - Wsl                       # Offset of spin-lock from A.
        dB = Wb - Wsl                       # Offset of spin-lock from B.

        # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
        R = rr1rho_3d(R1=r1, Rinf=r1rho_prime, pA=pA, pB=pB, wA=dA, wB=dB, w1=spin_lock_fields[i], k_AB=k_AB, k_BA=k_BA)

        # The following lines rotate the magnetization previous to spin-lock into the weff frame.
        # A new M0 is obtained:  M0 = [sin(thetaA)*pA sin(thetaB)*pB 0 0 cos(thetaA)*pA cos(thetaB)*pB].
        thetaA = atan(spin_lock_fields[i]/dA)
        thetaB = atan(spin_lock_fields[i]/dB)
        M0[0] = sin(thetaA) * pA
        M0[1] = sin(thetaB) * pB
        M0[4] = cos(thetaA) * pA
        M0[5] = cos(thetaB) * pB

        # This matrix is a propagator that will evolve the magnetization with the matrix R.
        Rexpo = expm(R*relax_time)

        # Magnetization evolution.
        Moft = dot(Rexpo, M0)
        MAx = Moft[0].real / pA
        MAy = Moft[2].real / pA
        MAz = Moft[4].real / pA
        MA = sqrt(MAx**2 + MAy**2 + MAz**2)    # For spin A, is equal to 1 if nothing happens (no relaxation).

        # The next lines calculate the R1rho using a two-point approximation, i.e. assuming that the decay is mono-exponential.
        if MA <= 0.0 or isNaN(MA):
            back_calc[i] = 1e99
        else:
            back_calc[i]= -inv_relax_time * log(MA)


