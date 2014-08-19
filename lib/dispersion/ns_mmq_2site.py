###############################################################################
#                                                                             #
# Copyright (C) 2013 Mathilde Lescanne                                        #
# Copyright (C) 2013 Dominique Marion                                         #
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
"""The numeric solution for the 2-site Bloch-McConnell equations for MMQ CPMG data, the U{NS MMQ 2-site<http://wiki.nmr-relax.com/NS_MMQ_2-site>} model.

Description
===========

This handles proton-heteronuclear SQ, ZQ, DQ and MQ CPMG data.


References
==========

It uses the equations of:

    - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  I{J. Am. Chem. Soc.}, B{127}, 15602-15611.  (U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}).


Links
=====

More information on the NS MMQ 2-site model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_MMQ_2-site>},
    - U{relax manual<http://www.nmr-relax.com/manual/NS_MMQ_2_site_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_MMQ_2-site>}.
"""

# Python module imports.
from math import floor
from numpy import array, conj, complex64, dot, einsum, float64, log, multiply
from numpy.linalg import matrix_power

# relax module imports.
from lib.float import isNaN
from lib.dispersion.matrix_exponential import matrix_exponential

# Repetitive calculations (to speed up calculations).
m_r20a = array([
    [-1,  0],
    [ 0,  0]], float64)

m_r20b = array([
    [ 0,  0],
    [ 0, -1]], float64)

m_k_AB = array([
    [-1,  0],
    [ 1,  0]], float64)

m_k_BA = array([
    [ 0,  1],
    [ 0, -1]], float64)

m_dw = array([
    [ 0,  0],
    [ 0,  1]], float64)


def rmmq_2site_rankN(R20A=None, R20B=None, dw=None, k_AB=None, k_BA=None, tcp=None):
    """The Bloch-McConnell matrix for 2-site exchange, for rank [NE][NS][NM][NO][ND][2][2].

    @keyword R20A:          The transverse, spin-spin relaxation rate for state A.
    @type R20A:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword R20B:          The transverse, spin-spin relaxation rate for state B.
    @type R20B:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw:            The combined chemical exchange difference parameters between states A and B in rad/s.  This can be any combination of dw and dwH.
    @type dw:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NE][NS][NM][NO][ND]
    @return:                The relaxation matrix.
    @rtype:                 numpy float array of rank [NE][NS][NM][NO][ND][2][2]
    """

    # Pre-multiply with tcp.
    r20a_tcp = R20A * tcp
    r20b_tcp = R20B * tcp
    k_AB_tcp = k_AB * tcp
    k_BA_tcp = k_BA * tcp
    # Complex dw.
    dw_tcp_C = dw * tcp * 1j

    # Fill in the elements.
    #matrix[0, 0] = -k_AB - R20A
    #matrix[0, 1] = k_BA
    #matrix[1, 0] = k_AB
    #matrix[1, 1] = -k_BA + 1.j*dw - R20B

    # Multiply and expand.
    m_r20a_tcp = multiply.outer( r20a_tcp, m_r20a )
    m_r20b_tcp = multiply.outer( r20b_tcp, m_r20b )

    # Multiply and expand.
    m_k_AB_tcp = multiply.outer( k_AB_tcp, m_k_AB )
    m_k_BA_tcp = multiply.outer( k_BA_tcp, m_k_BA )

    # Multiply and expand.
    m_dw_tcp_C = multiply.outer( dw_tcp_C, m_dw )

    # Collect matrix.
    matrix = (m_r20a_tcp + m_r20b_tcp + m_k_AB_tcp + m_k_BA_tcp + m_dw_tcp_C)

    return matrix


def r2eff_ns_mmq_2site_mq(M0=None, F_vector=array([1, 0], float64), R20A=None, R20B=None, pA=None, dw=None, dwH=None, kex=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation for MQ data.

    The notation used here comes from:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    and:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword F_vector:      The observable magnitisation vector.  This defaults to [1, 0] for X observable magnitisation.
    @type F_vector:         numpy rank-1, 2D float64 array
    @keyword R20A:          The transverse, spin-spin relaxation rate for state A.
    @type R20A:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20B:          The transverse, spin-spin relaxation rate for state B.
    @type R20B:             numpy float array of rank [NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH:           The proton chemical exchange difference between states A and B in rad/s.
    @type dwH:              numpy float array of rank [NS][NM][NO][ND]
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
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

    # Once off parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex

    # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    M0[0] = pA
    M0[1] = pB

    # Extract shape of experiment.
    NS, NM, NO = num_points.shape

    # Populate the m1 and m2 matrices (only once per function call for speed).
    # D+ matrix component.
    m1_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=-dw - dwH, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
    # Z- matrix component.
    m2_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=dw - dwH, k_AB=k_AB, k_BA=k_BA, tcp=tcp)

    # The M1 and M2 matrices.
    # Equivalent to D+.
    M1_mat = matrix_exponential(m1_mat, dtype=complex64)
    # Equivalent to Z-.
    M2_mat = matrix_exponential(m2_mat, dtype=complex64)

    # The complex conjugates M1* and M2*
    # Equivalent to D+*.
    M1_star_mat = conj(M1_mat)
    # Equivalent to Z-*.
    M2_star_mat = conj(M2_mat)

    # Repetitive dot products (minimised for speed).
    M1_M2_mat = einsum('...ij, ...jk', M1_mat, M2_mat)
    M2_M1_mat = einsum('...ij, ...jk', M2_mat, M1_mat)
    M1_M2_M2_M1_mat = einsum('...ij, ...jk', M1_M2_mat, M2_M1_mat)
    M2_M1_M1_M2_mat = einsum('...ij, ...jk', M2_M1_mat, M1_M2_mat)
    M1_M2_star_mat = einsum('...ij, ...jk', M1_star_mat, M2_star_mat)
    M2_M1_star_mat = einsum('...ij, ...jk', M2_star_mat, M1_star_mat)
    M1_M2_M2_M1_star_mat = einsum('...ij, ...jk', M1_M2_star_mat, M2_M1_star_mat)
    M2_M1_M1_M2_star_mat = einsum('...ij, ...jk', M2_M1_star_mat, M1_M2_star_mat)

    # Loop over spins.
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Loop over offsets:
            for oi in range(NO):
                num_points_i = num_points[si, mi, oi]

                # Loop over the time points, back calculating the R2eff values.
                for i in range(num_points_i):
                    # Extract data from array.
                    power_i = int(power[si, mi, oi, i])
                    M1_M2_i = M1_M2_mat[si, mi, oi, i]
                    M1_M2_star_i = M1_M2_star_mat[si, mi, oi, i]
                    M2_M1_i = M2_M1_mat[si, mi, oi, i]
                    M2_M1_star_i = M2_M1_star_mat[si, mi, oi, i]
                    M1_M2_M2_M1_i = M1_M2_M2_M1_mat[si, mi, oi, i]
                    M2_M1_M1_M2_star_i = M2_M1_M1_M2_star_mat[si, mi, oi, i]
                    M2_M1_M1_M2_i = M2_M1_M1_M2_mat[si, mi, oi, i]
                    M1_M2_M2_M1_star_i = M1_M2_M2_M1_star_mat[si, mi, oi, i]

                    # Special case of 1 CPMG block - the power is zero.
                    if power_i == 1:
                        # M1.M2.
                        A = M1_M2_i

                        # M1*.M2*.
                        B = M1_M2_star_i

                        # M2.M1.
                        C = M2_M1_i

                        # M2*.M1*.
                        D = M2_M1_star_i

                    # Matrices for even number of CPMG blocks.
                    elif power_i % 2 == 0:
                        # The power factor (only calculate once).
                        fact = int(floor(power_i / 2))

                        # (M1.M2.M2.M1)^(n/2).
                        A = matrix_power(M1_M2_M2_M1_i, fact)

                        # (M2*.M1*.M1*.M2*)^(n/2).
                        B = matrix_power(M2_M1_M1_M2_star_i, fact)

                        # (M2.M1.M1.M2)^(n/2).
                        C = matrix_power(M2_M1_M1_M2_i, fact)

                        # (M1*.M2*.M2*.M1*)^(n/2).
                        D = matrix_power(M1_M2_M2_M1_star_i, fact)

                    # Matrices for odd number of CPMG blocks.
                    else:
                        # The power factor (only calculate once).
                        fact = int(floor((power_i - 1) / 2))

                        # (M1.M2.M2.M1)^((n-1)/2).M1.M2.
                        A = matrix_power(M1_M2_M2_M1_i, fact)
                        A = dot(A, M1_M2_i)

                        # (M1*.M2*.M2*.M1*)^((n-1)/2).M1*.M2*.
                        B = matrix_power(M1_M2_M2_M1_star_i, fact)
                        B = dot(B, M1_M2_star_i)

                        # (M2.M1.M1.M2)^((n-1)/2).M2.M1.
                        C = matrix_power(M2_M1_M1_M2_i, fact)
                        C = dot(C, M2_M1_i)

                        # (M2*.M1*.M1*.M2*)^((n-1)/2).M2*.M1*.
                        D = matrix_power(M2_M1_M1_M2_star_i, fact)
                        D = dot(D, M2_M1_star_i)

                    # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                    A_B = dot(A, B)
                    C_D = dot(C, D)
                    Mx = dot(dot(F_vector, (A_B + C_D)), M0)
                    Mx = Mx.real / 2.0
                    if Mx <= 0.0 or isNaN(Mx):
                        back_calc[si, mi, oi, i] = 1e99
                    else:
                        back_calc[si, mi, oi, i]= -inv_tcpmg[si, mi, oi, i] * log(Mx / pA)


def r2eff_ns_mmq_2site_sq_dq_zq(M0=None, F_vector=array([1, 0], float64), R20A=None, R20B=None, pA=None, dw=None, dwH=None, kex=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation for SQ, ZQ, and DQ data.

    The notation used here comes from:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword F_vector:      The observable magnitisation vector.  This defaults to [1, 0] for X observable magnitisation.
    @type F_vector:         numpy rank-1, 2D float64 array
    @keyword R20A:          The transverse, spin-spin relaxation rate for state A.
    @type R20A:             numpy float array of rank [NS][NM][NO][ND]
    @keyword R20B:          The transverse, spin-spin relaxation rate for state B.
    @type R20B:             numpy float array of rank [NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The combined chemical exchange difference between states A and B in rad/s.  It should be set to dwH for 1H SQ data, dw for heteronuclear SQ data, dwH-dw for ZQ data, and dwH+dw for DQ data.
    @type dw:               numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH:           Unused - this is simply to match the r2eff_ns_mmq_2site_mq() function arguments.
    @type dwH:              numpy float array of rank [NS][NM][NO][ND]
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
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

    # Once off parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex

    # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    M0[0] = pA
    M0[1] = pB

    # Extract shape of experiment.
    NS, NM, NO = num_points.shape

    # Populate the m1 and m2 matrices (only once per function call for speed).
    m1_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
    m2_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=-dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)

    # The A+/- matrices.
    A_pos_mat = matrix_exponential(m1_mat, dtype=complex64)
    A_neg_mat = matrix_exponential(m2_mat, dtype=complex64)

    # The evolution for one n.
    evol_block_mat = einsum('...ij, ...jk', A_neg_mat, A_pos_mat)
    evol_block_mat = einsum('...ij, ...jk', A_neg_mat, evol_block_mat)
    evol_block_mat = einsum('...ij, ...jk', A_pos_mat, evol_block_mat)

    # Loop over spins.
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Loop over offsets:
            for oi in range(NO):
                # Extract number of points.
                num_points_i = num_points[si, mi, oi]

                # Loop over the time points, back calculating the R2eff values.
                for i in range(num_points_i):
                    # Extract data from array.
                    power_i = int(power[si, mi, oi, i])
                    evol_block_i = evol_block_mat[si, mi, oi, i]

                    # The full evolution.
                    evol = matrix_power(evol_block_i, power_i)

                    # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                    Mx = dot(F_vector, dot(evol, M0))
                    Mx = Mx.real
                    if Mx <= 0.0 or isNaN(Mx):
                        back_calc[si, mi, oi, i] = 1e99
                    else:
                        back_calc[si, mi, oi, i] = -inv_tcpmg[si, mi, oi, i] * log(Mx / pA)
