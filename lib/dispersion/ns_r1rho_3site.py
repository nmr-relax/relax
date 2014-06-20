###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
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
"""The numerical solution for the 3-site Bloch-McConnell equations for R1rho-type data, the U{NS R1rho 3-site linear<http://wiki.nmr-relax.com/NS_R1rho_3-site_linear>} and U{NS R1rho 3-site<http://wiki.nmr-relax.com/NS_R1rho_3-site>} model.

Description
===========

This is the model of the numerical solution for the 3-site Bloch-McConnell equations.  It originates from the funNumrho.m file from the Skrynikov & Tollinger code (the sim_all.tar file U{https://gna.org/support/download.php?file_id=18404} attached to U{https://gna.org/task/?7712#comment5}).


References
==========

The solution has been modified to use the from presented in:

    - Korzhnev, D. M., Orekhov, V. Y., and Kay, L. E. (2005).  Off-resonance R(1rho) NMR studies of exchange dynamics in proteins with low spin-lock fields:  an application to a Fyn SH3 domain.  I{J. Am. Chem. Soc.}, B{127}, 713-721. (U{DOI: 10.1021/ja0446855<http://dx.doi.org/10.1021/ja0446855>}).


Links
=====

More information on the NS R1rho 3-site linear model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_R1rho_3-site_linear>},
    - U{relax manual<http://www.nmr-relax.com/manual/NS_3_site_linear_R1_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_R1rho_3-site_linear>}.

More information on the NS R1rho 3-site model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_R1rho_3-site>},
    - U{relax manual<http://www.nmr-relax.com/manual/NS_3_site_R1_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_R1rho_3-site>}.
"""

# Python module imports.
from math import atan2, cos, log, sin
from numpy import dot, sum

# relax module imports.
from lib.dispersion.ns_matrices import rr1rho_3d_3site, rr1rho_3d_3site_rankN
from lib.float import isNaN
from lib.linear_algebra.matrix_exponential import matrix_exponential, matrix_exponential_rankN


def ns_r1rho_3site(M0=None, matrix=None, r1rho_prime=None, omega=None, offset=None, r1=0.0, pA=None, pB=None, dw_AB=None, dw_AC=None, kex_AB=None, kex_BC=None, kex_AC=None, spin_lock_fields=None, relax_time=None, inv_relax_time=None, back_calc=None, num_points=None):
    """The 3-site numerical solution to the Bloch-McConnell equation for R1rho data.

    This function calculates and stores the R1rho values.


    @keyword M0:                This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:                   numpy float64, rank-1, 7D array
    @keyword matrix:            A numpy array to be populated to create the evolution matrix.
    @type matrix:               numpy rank-2, 9D float64 array
    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          numpy float array of rank [NS][NM][NO][ND]
    @keyword omega:             The chemical shift for the spin in rad/s.
    @type omega:                numpy float array of rank [NS][NM][NO][ND]
    @keyword offset:            The spin-lock offsets for the data.
    @type offset:               numpy float array of rank [NS][NM][NO][ND]
    @keyword r1:                The R1 relaxation rate.
    @type r1:                   numpy float array of rank [NS][NM][NO][ND]
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword pB:                The population of state B.
    @type pB:                   float
    @keyword dw_AB:             The chemical exchange difference between states A and B in rad/s.
    @type dw_AB:                numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_AC:             The chemical exchange difference between states A and C in rad/s.
    @type dw_AC:                numpy float array of rank [NS][NM][NO][ND]
    @keyword kex_AB:            The exchange rate between sites A and B for 3-site exchange with kex_AB = k_AB + k_BA (rad.s^-1)
    @type kex_AB:               float
    @keyword kex_BC:            The exchange rate between sites A and C for 3-site exchange with kex_AC = k_AC + k_CA (rad.s^-1)
    @type kex_BC:               float
    @keyword kex_AC:            The exchange rate between sites B and C for 3-site exchange with kex_BC = k_BC + k_CB (rad.s^-1)
    @type kex_AC:               float
    @keyword spin_lock_fields:  The R1rho spin-lock field strengths (in rad.s^-1).
    @type spin_lock_fields:     numpy float array of rank [NS][NM][NO][ND]
    @keyword relax_time:        The total relaxation time period for each spin-lock field strength (in seconds).
    @type relax_time:           numpy float array of rank [NS][NM][NO][ND]
    @keyword inv_relax_time:    The inverse of the relaxation time period for each spin-lock field strength (in inverse seconds).  This is used for faster calculations.
    @type inv_relax_time:       numpy float array of rank [NS][NM][NO][ND]
    @keyword back_calc:         The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:            numpy float array of rank [NS][NM][NO][ND]
    @keyword num_points:        The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:           numpy int array of rank [NS][NM][NO]
    """

    # Once off parameter conversions.
    pC = 1.0 - pA - pB
    pA_pB = pA + pB
    pA_pC = pA + pC
    pB_pC = pB + pC
    k_BA = pA * kex_AB / pA_pB
    k_AB = pB * kex_AB / pA_pB
    k_CB = pB * kex_BC / pB_pC
    k_BC = pC * kex_BC / pB_pC
    k_CA = pA * kex_AC / pA_pC
    k_AC = pC * kex_AC / pA_pC

    # Extract shape of experiment.
    NE, NS, NM, NO = num_points.shape

    # The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R_mat = rr1rho_3d_3site_rankN(R1=r1, r1rho_prime=r1rho_prime, pA=pA, pB=pB, pC=pC, dw_AB=dw_AB, dw_AC=dw_AC, omega=omega, offset=offset, w1=spin_lock_fields, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, relax_time=relax_time)

    # This matrix is a propagator that will evolve the magnetization with the matrix R.
    Rexpo_mat = matrix_exponential_rankN(R_mat)

    # Loop over spins.
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Loop over offsets:
            for oi in range(NO):
                # Extract parameters from array.
                num_points_i = num_points[0, si, mi, oi]

                # Loop over the time points, back calculating the R2eff values.
                for j in range(num_points_i):
                    # Offset of spin-lock from A.
                    dA = omega[0, si, mi, oi, j] - offset[0, si, mi, oi, j]

                    # The following lines rotate the magnetization previous to spin-lock into the weff frame.
                    theta = atan2(spin_lock_fields[0, si, mi, oi, j], dA)
                    M0[0] = sin(theta)    # The A state initial X magnetisation.
                    M0[2] = cos(theta)    # The A state initial Z magnetisation.

                    # This matrix is a propagator that will evolve the magnetization with the matrix R.
                    Rexpo_j = Rexpo_mat[0, si, mi, oi, j]

                    # Magnetization evolution.
                    MA = dot(M0, dot(Rexpo_j, M0))

                    # The next lines calculate the R1rho using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                    if MA <= 0.0 or isNaN(MA):
                        back_calc[0, si, mi, oi, j] = 1e99
                    else:
                        back_calc[0, si, mi, oi, j]= -inv_relax_time[0, si, mi, oi, j] * log(MA)
