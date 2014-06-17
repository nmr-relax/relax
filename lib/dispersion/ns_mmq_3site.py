###############################################################################
#                                                                             #
# Copyright (C) 2013 Mathilde Lescanne                                        #
# Copyright (C) 2013 Dominique Marion                                         #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""The numeric solution for the 3-site Bloch-McConnell equations for MMQ CPMG data, the U{NS MMQ 3-site linear<http://wiki.nmr-relax.com/NS_MMQ_3-site_linear>} and U{NS MMQ 3-site<http://wiki.nmr-relax.com/NS_MMQ_3-site>} models.

Description
===========

This handles proton-heteronuclear SQ, ZQ, DQ and MQ CPMG data.


References
==========

It uses the equations of:

    - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  I{J. Am. Chem. Soc.}, B{127}, 15602-15611.  (U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}).


Links
=====

More information on the NS MMQ 3-site linear model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_MMQ_3-site_linear>},
    - U{relax manual<http://www.nmr-relax.com/manual/NS_MMQ_3_site_linear_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_MMQ_3-site_linear>}.

More information on the NS MMQ 3-site model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_MMQ_3-site>},
    - U{relax manual<http://www.nmr-relax.com/manual/NS_MMQ_3_site_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_MMQ_3-site>}.
"""

# Python module imports.
from math import floor
from numpy import array, conj, dot, float64, log

# relax module imports.
from lib.float import isNaN
from lib.linear_algebra.matrix_exponential import matrix_exponential
from lib.linear_algebra.matrix_power import square_matrix_power


def populate_matrix(matrix=None, R20A=None, R20B=None, R20C=None, dw_AB=None, dw_AC=None, k_AB=None, k_BA=None, k_BC=None, k_CB=None, k_AC=None, k_CA=None):
    """The Bloch-McConnell matrix for 3-site exchange.

    @keyword matrix:        The matrix to populate.
    @type matrix:           numpy rank-2, 3D complex64 array
    @keyword R20A:          The transverse, spin-spin relaxation rate for state A.
    @type R20A:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20B:          The transverse, spin-spin relaxation rate for state B.
    @type R20B:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20C:          The transverse, spin-spin relaxation rate for state C.
    @type R20C:             numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_AB:         The combined chemical exchange difference parameters between states A and B in rad/s.  This can be any combination of dw and dwH.
    @type dw_AB:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_AC:         The combined chemical exchange difference parameters between states A and C in rad/s.  This can be any combination of dw and dwH.
    @type dw_AC:            numpy float array of rank [NS][NM][NO][ND]
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword k_BC:          The rate of exchange from site B to C (rad/s).
    @type k_BC:             float
    @keyword k_CB:          The rate of exchange from site C to B (rad/s).
    @type k_CB:             float
    @keyword k_AC:          The rate of exchange from site A to C (rad/s).
    @type k_AC:             float
    @keyword k_CA:          The rate of exchange from site C to A (rad/s).
    @type k_CA:             float
    """

    # The first row.
    matrix[0, 0] = -k_AB - k_AC - R20A
    matrix[0, 1] = k_BA
    matrix[0, 2] = k_CA

    # The second row.
    matrix[1, 0] = k_AB
    matrix[1, 1] = -k_BA - k_BC + 1.j*dw_AB - R20B
    matrix[1, 2] = k_CB

    # The third row.
    matrix[2, 0] = k_AC
    matrix[2, 1] = k_BC
    matrix[2, 2] = -k_CB - k_CA + 1.j*dw_AC - R20C


def r2eff_ns_mmq_3site_mq(M0=None, F_vector=array([1, 0, 0], float64), m1=None, m2=None, R20A=None, R20B=None, R20C=None, pA=None, pB=None, pC=None, dw_AB=None, dw_AC=None, dwH_AB=None, dwH_AC=None, k_AB=None, k_BA=None, k_BC=None, k_CB=None, k_AC=None, k_CA=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 3-site numerical solution to the Bloch-McConnell equation for MQ data.

    The notation used here comes from:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    and:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword F_vector:      The observable magnitisation vector.  This defaults to [1, 0] for X observable magnitisation.
    @type F_vector:         numpy rank-1, 3D float64 array
    @keyword m1:            A complex numpy matrix to be populated.
    @type m1:               numpy rank-2, 3D complex64 array
    @keyword m2:            A complex numpy matrix to be populated.
    @type m2:               numpy rank-2, 3D complex64 array
    @keyword R20A:          The transverse, spin-spin relaxation rate for state A.
    @type R20A:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20B:          The transverse, spin-spin relaxation rate for state B.
    @type R20B:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20C:          The transverse, spin-spin relaxation rate for state C.
    @type R20C:             numpy float array of rank [NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword pC:            The population of state C.
    @type pC:               float
    @keyword dw_AB:         The chemical exchange difference between states A and B in rad/s.
    @type dw_AB:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_AC:         The chemical exchange difference between states A and C in rad/s.
    @type dw_AC:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_AB:        The proton chemical exchange difference between states A and B in rad/s.
    @type dwH_AB:           numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_AC:        The proton chemical exchange difference between states A and C in rad/s.
    @type dwH_AC:           numpy float array of rank [NS][NM][NO][ND]
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword k_BC:          The rate of exchange from site B to C (rad/s).
    @type k_BC:             float
    @keyword k_CB:          The rate of exchange from site C to B (rad/s).
    @type k_CB:             float
    @keyword k_AC:          The rate of exchange from site A to C (rad/s).
    @type k_AC:             float
    @keyword k_CA:          The rate of exchange from site C to A (rad/s).
    @type k_CA:             float
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NS][NM][NO][ND]
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:       numpy int array of rank [NS][NM][NO]
    @keyword power:         The matrix exponential power array.
    @type power:            numpy int array of rank [NS][NM][NO][ND]
    """

    # Extract shape of experiment.
    NS, NM, NO = num_points.shape

    # Loop over spins.
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Loop over offsets:
            for oi in range(NO):

                r20a_i = R20A[si, mi, oi, 0]
                r20b_i = R20B[si, mi, oi, 0]
                r20c_i = R20C[si, mi, oi, 0]

                dw_AB_i=dw_AB[si, mi, oi, 0]
                dw_AC_i=dw_AC[si, mi, oi, 0]
                dwH_AB_i=dwH_AB[si, mi, oi, 0]
                dwH_AC_i=dwH_AC[si, mi, oi, 0]
                num_points_i = num_points[si, mi, oi]

                # Populate the m1 and m2 matrices (only once per function call for speed).
                populate_matrix(matrix=m1, R20A=r20a_i, R20B=r20b_i, R20C=r20c_i, dw_AB=-dw_AB_i - dwH_AB_i, dw_AC=-dw_AC_i - dwH_AC_i, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA)     # D+ matrix component.
                populate_matrix(matrix=m2, R20A=r20a_i, R20B=r20b_i, R20C=r20c_i, dw_AB=dw_AB_i - dwH_AB_i, dw_AC=dw_AC_i - dwH_AC_i, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA)    # Z- matrix component.

                # Loop over the time points, back calculating the R2eff values.
                for i in range(num_points_i):
                    # The M1 and M2 matrices.
                    M1 = matrix_exponential(m1*tcp[si, mi, oi, i])    # Equivalent to D+.
                    M2 = matrix_exponential(m2*tcp[si, mi, oi, i])    # Equivalent to Z-.

                    # The complex conjugates M1* and M2*
                    M1_star = conj(M1)    # Equivalent to D+*.
                    M2_star = conj(M2)    # Equivalent to Z-*.

                    # Repetitive dot products (minimised for speed).
                    M1_M2 = dot(M1, M2)
                    M2_M1 = dot(M2, M1)
                    M1_M2_M2_M1 = dot(M1_M2, M2_M1)
                    M2_M1_M1_M2 = dot(M2_M1, M1_M2)
                    M1_M2_star = dot(M1_star, M2_star)
                    M2_M1_star = dot(M2_star, M1_star)
                    M1_M2_M2_M1_star = dot(M1_M2_star, M2_M1_star)
                    M2_M1_M1_M2_star = dot(M2_M1_star, M1_M2_star)

                    # Special case of 1 CPMG block - the power is zero.
                    if power[si, mi, oi, i] == 1:
                        # M1.M2.
                        A = M1_M2

                        # M1*.M2*.
                        B = M1_M2_star

                        # M2.M1.
                        C = M2_M1

                        # M2*.M1*.
                        D = M2_M1_star

                    # Matrices for even number of CPMG blocks.
                    elif power[si, mi, oi, i] % 2 == 0:
                        # The power factor (only calculate once).
                        fact = int(floor(power[si, mi, oi, i] / 2))

                        # (M1.M2.M2.M1)^(n/2).
                        A = square_matrix_power(M1_M2_M2_M1, fact)

                        # (M2*.M1*.M1*.M2*)^(n/2).
                        B = square_matrix_power(M2_M1_M1_M2_star, fact)

                        # (M2.M1.M1.M2)^(n/2).
                        C = square_matrix_power(M2_M1_M1_M2, fact)

                        # (M1*.M2*.M2*.M1*)^(n/2).
                        D = square_matrix_power(M1_M2_M2_M1_star, fact)

                    # Matrices for odd number of CPMG blocks.
                    else:
                        # The power factor (only calculate once).
                        fact = int(floor((power[si, mi, oi, i] - 1) / 2))

                        # (M1.M2.M2.M1)^((n-1)/2).M1.M2.
                        A = square_matrix_power(M1_M2_M2_M1, fact)
                        A = dot(A, M1_M2)

                        # (M1*.M2*.M2*.M1*)^((n-1)/2).M1*.M2*.
                        B = square_matrix_power(M1_M2_M2_M1_star, fact)
                        B = dot(B, M1_M2_star)

                        # (M2.M1.M1.M2)^((n-1)/2).M2.M1.
                        C = square_matrix_power(M2_M1_M1_M2, fact)
                        C = dot(C, M2_M1)

                        # (M2*.M1*.M1*.M2*)^((n-1)/2).M2*.M1*.
                        D = square_matrix_power(M2_M1_M1_M2_star, fact)
                        D = dot(D, M2_M1_star)

                    # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                    A_B = dot(A, B)
                    C_D = dot(C, D)
                    Mx = dot(dot(F_vector, (A_B + C_D)), M0)
                    Mx = Mx.real / 2.0
                    if Mx <= 0.0 or isNaN(Mx):
                        back_calc[si, mi, oi, i] = 1e99
                    else:
                        back_calc[si, mi, oi, i]= -inv_tcpmg[si, mi, oi, i] * log(Mx / pA)


def r2eff_ns_mmq_3site_sq_dq_zq(M0=None, F_vector=array([1, 0, 0], float64), m1=None, m2=None, R20A=None, R20B=None, R20C=None, pA=None, pB=None, pC=None, dw_AB=None, dw_AC=None, dwH_AB=None, dwH_AC=None, k_AB=None, k_BA=None, k_BC=None, k_CB=None, k_AC=None, k_CA=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 3-site numerical solution to the Bloch-McConnell equation for SQ, ZQ, and DQ data.

    The notation used here comes from:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword F_vector:      The observable magnitisation vector.  This defaults to [1, 0] for X observable magnitisation.
    @type F_vector:         numpy rank-1, 3D float64 array
    @keyword m1:            A complex numpy matrix to be populated.
    @type m1:               numpy rank-2, 3D complex64 array
    @keyword m2:            A complex numpy matrix to be populated.
    @type m2:               numpy rank-2, 3D complex64 array
    @keyword R20A:          The transverse, spin-spin relaxation rate for state A.
    @type R20A:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20B:          The transverse, spin-spin relaxation rate for state B.
    @type R20B:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20C:          The transverse, spin-spin relaxation rate for state C.
    @type R20C:             numpy float array of rank [NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword pC:            The population of state C.
    @type pC:               float
    @keyword dw_AB:         The combined chemical exchange difference between states A and B in rad/s.  It should be set to dwH for 1H SQ data, dw for heteronuclear SQ data, dwH-dw for ZQ data, and dwH+dw for DQ data.
    @type dw_AB:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_AC:         The combined chemical exchange difference between states A and C in rad/s.  It should be set to dwH for 1H SQ data, dw for heteronuclear SQ data, dwH-dw for ZQ data, and dwH+dw for DQ data.
    @type dw_AC:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_AB:        Unused - this is simply to match the r2eff_mmq_3site_mq() function arguments.
    @type dwH_AB:           numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_AC:        Unused - this is simply to match the r2eff_mmq_3site_mq() function arguments.
    @type dwH_AC:           numpy float array of rank [NS][NM][NO][ND]
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        numpy float array of rank [NS][NM][NO][ND]
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NS][NM][NO][ND]
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:       numpy int array of rank [NS][NM][NO]
    @keyword power:         The matrix exponential power array.
    @type power:            numpy int array of rank [NS][NM][NO][ND]
    """

    # Extract shape of experiment.
    NS, NM, NO = num_points.shape

    # Loop over spins.
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Loop over offsets:
            for oi in range(NO):

                r20a_i = R20A[si, mi, oi, 0]
                r20b_i = R20B[si, mi, oi, 0]
                r20c_i = R20C[si, mi, oi, 0]

                dw_AB_i=dw_AB[si, mi, oi, 0]
                dw_AC_i=dw_AC[si, mi, oi, 0]
                dwH_AB_i=dwH_AB[si, mi, oi, 0]
                dwH_AC_i=dwH_AC[si, mi, oi, 0]
                num_points_i = num_points[si, mi, oi]

                # Populate the m1 and m2 matrices (only once per function call for speed).
                populate_matrix(matrix=m1, R20A=r20a_i, R20B=r20b_i, R20C=r20c_i, dw_AB=dw_AB_i, dw_AC=dw_AC_i, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA)
                populate_matrix(matrix=m2, R20A=r20a_i, R20B=r20b_i, R20C=r20c_i, dw_AB=-dw_AB_i, dw_AC=-dw_AC_i, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA)

                # Loop over the time points, back calculating the R2eff values.
                for i in range(num_points_i):
                    # The A+/- matrices.
                    A_pos = matrix_exponential(m1*tcp[si, mi, oi, i])
                    A_neg = matrix_exponential(m2*tcp[si, mi, oi, i])

                    # The evolution for one n.
                    evol_block = dot(A_pos, dot(A_neg, dot(A_neg, A_pos)))

                    # The full evolution.
                    evol = square_matrix_power(evol_block, power[si, mi, oi, i])

                    # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                    Mx = dot(F_vector, dot(evol, M0))
                    Mx = Mx.real
                    if Mx <= 0.0 or isNaN(Mx):
                        back_calc[si, mi, oi, i] = 1e99
                    else:
                        back_calc[si, mi, oi, i] = -inv_tcpmg[si, mi, oi, i] * log(Mx / pA)
