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
    - U{relax manual<http://www.nmr-relax.com/manual/The_NS_MMQ_3_site_linear_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_MMQ_3-site_linear>}.

More information on the NS MMQ 3-site model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_MMQ_3-site>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_NS_MMQ_3_site_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_MMQ_3-site>}.
"""

# Python module imports.
from math import floor
from numpy import array, conj, dot, einsum, float64, log, multiply, isnan, any
from numpy.ma import fix_invalid
from numpy.linalg import matrix_power

# relax module imports.
from lib.float import isNaN
from lib.dispersion.matrix_exponential import matrix_exponential
from lib.errors import RelaxError

# Repetitive calculations (to speed up calculations).
# R20.
m_r20a = array([
    [-1, 0,  0],
    [ 0,  0,  0],
    [ 0,  0,  0]], float64)

m_r20b = array([
    [ 0,  0,  0],
    [ 0, -1,  0],
    [ 0,  0,  0]], float64)

m_r20c = array([
    [ 0,  0,  0],
    [ 0,  0,  0],
    [ 0,  0, -1]], float64)

# dw.
m_dw_AB = array([
    [ 0,  0,  0],
    [ 0,  1,  0],
    [ 0,  0,  0]], float64)

m_dw_AC = array([
    [ 0,  0,  0],
    [ 0,  0,  0],
    [ 0,  0,  1]], float64)

# k_x.
m_k_AB = array([
    [-1, 0,  0],
    [ 1, 0,  0],
    [ 0, 0,  0]], float64)

m_k_BA = array([
    [ 0,  1, 0],
    [ 0, -1, 0],
    [ 0, 0,  0]], float64)

m_k_BC = array([
    [ 0,  0,  0],
    [ 0, -1,  0],
    [ 0,  1,  0]], float64)

m_k_CB = array([
    [ 0,  0,  0],
    [ 0,  0,  1],
    [ 0,  0, -1]], float64)

m_k_AC = array([
    [-1, 0,  0],
    [ 0, 0,  0],
    [ 1, 0,  0]], float64)

m_k_CA = array([
    [ 0,  0,  1],
    [ 0,  0,  0],
    [ 0,  0, -1]], float64)


def rmmq_3site_rankN(R20A=None, R20B=None, R20C=None, dw_AB=None, dw_AC=None, k_AB=None, k_BA=None, k_BC=None, k_CB=None, k_AC=None, k_CA=None, tcp=None):
    """The Bloch-McConnell matrix for 3-site exchange.

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
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # The first row.
    #matrix[0, 0] = -k_AB - k_AC - R20A
    #matrix[0, 1] = k_BA
    #matrix[0, 2] = k_CA

    # The second row.
    #matrix[1, 0] = k_AB
    #matrix[1, 1] = -k_BA - k_BC + 1.j*dw_AB - R20B
    #matrix[1, 2] = k_CB

    # The third row.
    #matrix[2, 0] = k_AC
    #matrix[2, 1] = k_BC
    #matrix[2, 2] = -k_CB - k_CA + 1.j*dw_AC - R20C
    for x in [R20A,R20B,R20C,dw_AB,dw_AC,k_AB,k_BA,k_BC,k_CB,k_AC,k_CA]:
        if isinstance(x,float):
            pass
        if isinstance(x,list):
            for v in x:
                if v is None:
                    raise RelaxError('trying to start NS MMQ 3 sites rankN with None values')
        if x is None:
            raise RelaxError('trying to start NS MMQ 3 sites rankN with None values')


    # Pre-multiply with tcp.
    r20a_tcp = R20A * tcp
    r20b_tcp = R20B * tcp
    r20c_tcp = R20C * tcp

    # Complex dw.
    dw_AB_C_tcp = dw_AB * tcp * 1j
    dw_AC_C_tcp = dw_AC * tcp * 1j

    k_AB_tcp = k_AB * tcp
    k_BA_tcp = k_BA * tcp
    k_BC_tcp = k_BC * tcp
    k_CB_tcp = k_CB * tcp
    k_AC_tcp = k_AC * tcp
    k_CA_tcp = k_CA * tcp

    # Multiply and expand.
    m_r20a_tcp = multiply.outer( r20a_tcp, m_r20a )
    m_r20b_tcp = multiply.outer( r20b_tcp, m_r20b )
    m_r20c_tcp = multiply.outer( r20c_tcp, m_r20c )

    # Multiply and expand.
    m_dw_AB_C_tcp = multiply.outer( dw_AB_C_tcp, m_dw_AB )
    m_dw_AC_C_tcp = multiply.outer( dw_AC_C_tcp, m_dw_AC )

    # Multiply and expand.
    m_k_AB_tcp = multiply.outer( k_AB_tcp, m_k_AB )
    m_k_BA_tcp = multiply.outer( k_BA_tcp, m_k_BA )
    m_k_BC_tcp = multiply.outer( k_BC_tcp, m_k_BC )
    m_k_CB_tcp = multiply.outer( k_CB_tcp, m_k_CB )
    m_k_AC_tcp = multiply.outer( k_AC_tcp, m_k_AC )
    m_k_CA_tcp = multiply.outer( k_CA_tcp, m_k_CA )

    # Collect matrix.
    matrix = (m_r20a_tcp + m_r20b_tcp + m_r20c_tcp
            + m_dw_AB_C_tcp + m_dw_AC_C_tcp
            + m_k_AB_tcp + m_k_BA_tcp + m_k_BC_tcp
            + m_k_CB_tcp + m_k_AC_tcp + m_k_CA_tcp)

    #print(matrix)
    #thismask = isnan(matrix)
    isit = any(isnan(matrix))
    if isit == True:
        fix_invalid(matrix, copy=False, fill_value=1e100)


    return matrix


def r2eff_ns_mmq_3site_mq(M0=None, F_vector=array([1, 0, 0], float64), R20A=None, R20B=None, R20C=None, pA=None, pB=None, dw_AB=None, dw_BC=None, dwH_AB=None, dwH_BC=None, kex_AB=None, kex_BC=None, kex_AC=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
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
    @keyword dw_AB:         The chemical exchange difference between states A and B in rad/s.
    @type dw_AB:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_BC:         The chemical exchange difference between states B and C in rad/s.
    @type dw_BC:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_AB:        The proton chemical exchange difference between states A and B in rad/s.
    @type dwH_AB:           numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_BC:        The proton chemical exchange difference between states B and C in rad/s.
    @type dwH_BC:           numpy float array of rank [NS][NM][NO][ND]
    @keyword kex_AB:        The exchange rate between sites A and B for 3-site exchange with kex_AB = k_AB + k_BA (rad.s^-1)
    @type kex_AB:           float
    @keyword kex_BC:        The exchange rate between sites A and C for 3-site exchange with kex_AC = k_AC + k_CA (rad.s^-1)
    @type kex_BC:           float
    @keyword kex_AC:        The exchange rate between sites B and C for 3-site exchange with kex_BC = k_BC + k_CB (rad.s^-1)
    @type kex_AC:           float
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

    for x in [R20A,R20B,R20C,pA,pB,dw_AB,dw_BC,dwH_AB,dwH_BC,kex_AB,kex_BC,kex_AC]:
        if isinstance(x,float):
            pass
        if isinstance(x,list):
            for v in x:
                if v is None:
                    raise RelaxError('trying to start NS MMQ 3 sites with None values')
        if x is None:
            raise RelaxError('trying to start NS MMQ 3 sites with None values')


    # Once off parameter conversions.
    dw_AC = dw_AB + dw_BC
    dwH_AC = dwH_AB + dwH_BC
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

    # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    M0[0] = pA
    M0[1] = pB
    M0[2] = pC

    # Extract shape of experiment.
    NS, NM, NO = num_points.shape

    # Populate the m1 and m2 matrices (only once per function call for speed).
    # D+ matrix component.
    m1_mat = rmmq_3site_rankN(R20A=R20A, R20B=R20B, R20C=R20C, dw_AB=-dw_AB - dwH_AB, dw_AC=-dw_AC - dwH_AC, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, tcp=tcp)
    # Z- matrix component.
    m2_mat = rmmq_3site_rankN(R20A=R20A, R20B=R20B, R20C=R20C, dw_AB=dw_AB - dwH_AB, dw_AC=dw_AC - dwH_AC, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, tcp=tcp)

    # The M1 and M2 matrices.
    # Equivalent to D+.
    M1_mat = matrix_exponential(m1_mat)
    # Equivalent to Z-.
    M2_mat = matrix_exponential(m2_mat)

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
                # Extract parameters from array.
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


def r2eff_ns_mmq_3site_sq_dq_zq(M0=None, F_vector=array([1, 0, 0], float64), R20A=None, R20B=None, R20C=None, pA=None, pB=None, dw_AB=None, dw_BC=None, dwH_AB=None, dwH_BC=None, kex_AB=None, kex_BC=None, kex_AC=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 3-site numerical solution to the Bloch-McConnell equation for SQ, ZQ, and DQ data.

    The notation used here comes from:

        - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005).  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  J. Am. Chem. Soc., 127, 15602-15611.  (doi:  http://dx.doi.org/10.1021/ja054550e).

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword F_vector:      The observable magnitisation vector.  This defaults to [1, 0] for X observable magnitisation.
    @type F_vector:         numpy rank-1, 3D float64 array
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
    @keyword dw_AB:         The combined chemical exchange difference between states A and B in rad/s.  It should be set to dwH for 1H SQ data, dw for heteronuclear SQ data, dwH-dw for ZQ data, and dwH+dw for DQ data.
    @type dw_AB:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dw_BC:         The combined chemical exchange difference between states B and C in rad/s.  It should be set to dwH for 1H SQ data, dw for heteronuclear SQ data, dwH-dw for ZQ data, and dwH+dw for DQ data.
    @type dw_BC:            numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_AB:        Unused - this is simply to match the r2eff_mmq_3site_mq() function arguments.
    @type dwH_AB:           numpy float array of rank [NS][NM][NO][ND]
    @keyword dwH_BC:        Unused - this is simply to match the r2eff_mmq_3site_mq() function arguments.
    @type dwH_BC:           numpy float array of rank [NS][NM][NO][ND]
    @keyword kex_AB:        The exchange rate between sites A and B for 3-site exchange with kex_AB = k_AB + k_BA (rad.s^-1)
    @type kex_AB:           float
    @keyword kex_BC:        The exchange rate between sites A and C for 3-site exchange with kex_AC = k_AC + k_CA (rad.s^-1)
    @type kex_BC:           float
    @keyword kex_AC:        The exchange rate between sites B and C for 3-site exchange with kex_BC = k_BC + k_CB (rad.s^-1)
    @type kex_AC:           float
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
    for x in [R20A,R20B,R20C,pA,pB,dw_AB,dw_BC,dwH_AB,dwH_BC,kex_AB,kex_BC,kex_AC]:
        if isinstance(x,float):
            pass
        if isinstance(x,list):
            for v in x:
                if v is None:
                    raise RelaxError('trying to start NS MMQ 3 sites with None values')
        if x is None:
            raise RelaxError('trying to start NS MMQ 3 sites with None values')


    # Once off parameter conversions.
    dw_AC = dw_AB + dw_BC
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

    # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    M0[0] = pA
    M0[1] = pB
    M0[2] = pC

    # Extract shape of experiment.
    NS, NM, NO = num_points.shape

    # Populate the m1 and m2 matrices (only once per function call for speed).
    # D+ matrix component.
    m1_mat = rmmq_3site_rankN(R20A=R20A, R20B=R20B, R20C=R20C, dw_AB=dw_AB, dw_AC=dw_AC, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, tcp=tcp)
    # Z- matrix component.
    m2_mat = rmmq_3site_rankN(R20A=R20A, R20B=R20B, R20C=R20C, dw_AB=-dw_AB, dw_AC=-dw_AC, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, tcp=tcp)

    # The A+/- matrices.
    A_pos_mat = matrix_exponential(m1_mat)
    A_neg_mat = matrix_exponential(m2_mat)

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
                # Extract parameters from array.
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
