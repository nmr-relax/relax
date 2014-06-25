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
from numpy import array, einsum, float64, isfinite, log, min, multiply, sin, sum
from numpy.ma import fix_invalid, masked_less

# relax module imports.
from lib.dispersion.matrix_exponential import matrix_exponential_rank_NE_NS_NM_NO_ND_x_x

# Repetitive calculations (to speed up calculations).
m_R1 = array([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0, -1]], float64)

m_r1rho_prime = array([
    [-1, 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, -1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0, -1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

m_wA = array([
    [ 0, -1,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

m_wB = array([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
    [ 0,  0,  0,  1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

m_wC = array([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

m_w1 = array([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0,  0,  0,  0],
    [ 0,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0, -1],
    [ 0,  0,  0,  0,  0,  0,  0,  1, 0]], float64)

m_k_AB = array([
    [-1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, -1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  1,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

m_k_BA = array([
    [ 0,  0,  0,  1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  1,  0,  0,  0],
    [ 0,  0,  0, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

m_k_BC = array([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  1,  0,  0,  0]], float64)

m_k_CB = array([
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  1],
    [ 0,  0,  0,  0,  0,  0, -1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0, -1]], float64)

m_k_AC = array([
    [-1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, -1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  1,  0,  0,  0,  0,  0,  0]], float64)

m_k_CA = array([
    [ 0,  0,  0,  0,  0,  0,  1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  1],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0, -1,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0, -1]], float64)


def rr1rho_3d_3site_rankN(R1=None, r1rho_prime=None, dw_AB=None, dw_AC=None, omega=None, offset=None, w1=None, k_AB=None, k_BA=None, k_BC=None, k_CB=None, k_AC=None, k_CA=None, relax_time=None):
    """Definition of the 3D exchange matrix.

    @keyword R1:            The longitudinal, spin-lattice relaxation rate.
    @type R1:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r1rho_prime:   The R1rho transverse, spin-spin relaxation rate in the absence of exchange.
    @type r1rho_prime:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword omega:         The chemical shift for the spin in rad/s.
    @type omega:            numpy float array of rank [NS][NM][NO][ND]
    @keyword offset:        The spin-lock offsets for the data.
    @type offset:           numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw_AB:         The chemical exchange difference between states A and B in rad/s.
    @type dw_AB:            numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw_AC:         The chemical exchange difference between states A and C in rad/s.
    @type dw_AC:            numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword w1:            The spin-lock field strength in rad/s.
    @type w1:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword k_AB:          The forward exchange rate from state A to state B.
    @type k_AB:             float
    @keyword k_BA:          The reverse exchange rate from state B to state A.
    @type k_BA:             float
    @keyword k_BC:          The forward exchange rate from state B to state C.
    @type k_BC:             float
    @keyword k_CB:          The reverse exchange rate from state C to state B.
    @type k_CB:             float
    @keyword k_AC:          The forward exchange rate from state A to state C.
    @type k_AC:             float
    @keyword k_CA:          The reverse exchange rate from state C to state A.
    @type k_CA:             float
    @keyword relax_time:    The total relaxation time period for each spin-lock field strength (in seconds).
    @type relax_time:       numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # The AB auto-block.
    #matrix[0, 0] = -r1rho_prime - k_AB - k_AC
    #matrix[0, 1] = -wA
    #matrix[1, 0] = wA
    #matrix[1, 1] = -r1rho_prime - k_AB - k_AC
    #matrix[1, 2] = -w1
    #matrix[2, 1] = w1
    #matrix[2, 2] = -R1 - k_AB - k_AC

    # The AC auto-block.
    #matrix[3, 3] = -r1rho_prime - k_BA - k_BC
    #matrix[3, 4] = -wB
    #matrix[4, 3] = wB
    #matrix[4, 4] = -r1rho_prime - k_BA - k_BC
    #matrix[4, 5] = -w1
    #matrix[5, 4] = w1
    #matrix[5, 5] = -R1 - k_BA - k_BC

    # The BC auto-block.
    #matrix[6, 6] = -r1rho_prime - k_CA - k_CB
    #matrix[6, 7] = -wC
    #matrix[7, 6] = wC
    #matrix[7, 7] = -r1rho_prime - k_CA - k_CB
    #matrix[7, 8] = -w1
    #matrix[8, 7] = w1
    #matrix[8, 8] = -R1 - k_CA - k_CB

    # The AB cross-block.
    #matrix[0, 3] = k_BA
    #matrix[1, 4] = k_BA
    #matrix[2, 5] = k_BA
    #matrix[3, 0] = k_AB
    #matrix[4, 1] = k_AB
    #matrix[5, 2] = k_AB

    # The AC cross-block.
    #matrix[0, 6] = k_CA
    #matrix[1, 7] = k_CA
    #matrix[2, 8] = k_CA
    #matrix[6, 0] = k_AC
    #matrix[7, 1] = k_AC
    #matrix[8, 2] = k_AC

    # The BC cross-block.
    #matrix[3, 6] = k_CB
    #matrix[4, 7] = k_CB
    #matrix[5, 8] = k_CB
    #matrix[6, 3] = k_BC
    #matrix[7, 4] = k_BC
    #matrix[8, 5] = k_BC

    # Repetitive calculations (to speed up calculations).
    # The chemical shift offset of state A from the spin-lock. Larmor frequency for state A [s^-1].
    Wa = omega
    # The chemical shift offset of state B from the spin-lock. Larmor frequency for state B [s^-1].
    Wb = omega + dw_AB
    # The chemical shift offset of state C from the spin-lock. Larmor frequency for state C [s^-1].
    Wc = omega + dw_AC

    # Population-averaged Larmor frequency [s^-1].
    #W = pA*Wa + pB*Wb + pC*Wc
    # Offset of spin-lock from A.
    dA = Wa - offset
    # Offset of spin-lock from B.
    dB = Wb - offset
    # Offset of spin-lock from C.
    dC = Wc - offset
    # Offset of spin-lock from population-average 
    #d = W - offset_i

    # Parameter alias.
    wA=dA
    wB=dB
    wC=dC

    # Multiply and expand.
    mat_R1 = multiply.outer( R1 * relax_time, m_R1 )
    mat_r1rho_prime = multiply.outer( r1rho_prime * relax_time, m_r1rho_prime )

    mat_wA = multiply.outer( wA * relax_time, m_wA )
    mat_wB = multiply.outer( wB * relax_time, m_wB )
    mat_wC = multiply.outer( wC * relax_time, m_wC )
    mat_w1 = multiply.outer( w1 * relax_time, m_w1 )

    mat_k_AB = multiply.outer( k_AB * relax_time, m_k_AB )
    mat_k_BA = multiply.outer( k_BA * relax_time, m_k_BA )
    mat_k_BC = multiply.outer( k_BC * relax_time, m_k_BC )

    mat_k_CB = multiply.outer( k_CB * relax_time, m_k_CB )
    mat_k_AC = multiply.outer( k_AC * relax_time, m_k_AC )
    mat_k_CA = multiply.outer( k_CA * relax_time, m_k_CA )

    # Collect matrix.
    matrix = (mat_R1 + mat_r1rho_prime
            + mat_wA + mat_wB + mat_wC + mat_w1
            + mat_k_AB + mat_k_BA + mat_k_BC
            + mat_k_CB + mat_k_AC + mat_k_CA )

    # Return the matrix.
    return matrix


def ns_r1rho_3site(M0=None, M0_T=None, r1rho_prime=None, omega=None, offset=None, r1=0.0, pA=None, pB=None, dw_AB=None, dw_BC=None, kex_AB=None, kex_BC=None, kex_AC=None, spin_lock_fields=None, relax_time=None, inv_relax_time=None, back_calc=None, num_points=None):
    """The 3-site numerical solution to the Bloch-McConnell equation for R1rho data.

    This function calculates and stores the R1rho values.


    @keyword M0:                This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:                   numpy float array of rank [NE][NS][NM][NO][ND][9][1]
    @keyword M0_T:              This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations, where the outer two axis has been swapped for efficient dot operations.
    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          numpy float array of rank [NE][NS][NM][NO][ND][1][9]
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
    @keyword dw_BC:             The chemical exchange difference between states B and C in rad/s.
    @type dw_BC:                numpy float array of rank [NS][NM][NO][ND]
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

    # Extract shape of experiment.
    NE, NS, NM, NO = num_points.shape

    # The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R_mat = rr1rho_3d_3site_rankN(R1=r1, r1rho_prime=r1rho_prime, omega=omega, offset=offset, dw_AB=dw_AB, dw_AC=dw_AC, w1=spin_lock_fields, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, relax_time=relax_time)

    # This matrix is a propagator that will evolve the magnetization with the matrix R.
    Rexpo_mat = matrix_exponential_rank_NE_NS_NM_NO_ND_x_x(R_mat)

    # Magnetization evolution.
    Rexpo_M0_mat = einsum('...ij,...jk', Rexpo_mat, M0)

    # Magnetization evolution, which include all dimensions.
    MA_mat = einsum('...ij,...jk', M0_T, Rexpo_M0_mat)[:, :, :, :, :, 0, 0]

    # Insert safe checks.
    if min(MA_mat) < 0.0:
        mask_min_MA_mat = masked_less(MA_mat, 0.0)
        # Fill with high values.
        MA_mat[mask_min_MA_mat.mask] = 1e100

    # Do back calculation.
    back_calc[:] = -inv_relax_time * log(MA_mat)

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
