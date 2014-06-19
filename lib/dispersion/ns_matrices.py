###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
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
"""A collection of functions for generating the relaxation matrices for the numerical solutions.

These are for the numerical solutions to the Bloch-McConnell equations for relaxation dispersion.
"""

# Python module imports.
from math import cos, sin, pi
from numpy import array, float64, matrix, multiply


def r180x_2d(flip=pi):
    """The 2D rotation matrix for an imperfect X-axis pi-pulse.

    @keyword flip:  The X-axis pi-pulse flip angle (in rad).  This is currently unused, hence perfect pi-pulses are assumed.
    @type flip:     float
    @return:        The 2D rotational matrix.
    @rtype:         numpy rank-2, 4D array
    """

    # Build the matrix.
    R = array([ 
        [ 1.0,  0.0,  0.0,  0.0],
        [ 0.0, -1.0,  0.0,  0.0],
        [ 0.0,  0.0,  1.0,  0.0],
        [ 0.0,  0.0,  0.0, -1.0]
    ], float64)

    # Return the matrix.
    return R


def r180x_3d(flip=pi):
    """The 3D rotation matrix for an imperfect X-axis pi-pulse.

    @keyword flip:  The X-axis pi-pulse flip angle (in rad).
    @type flip:     float
    @return:        The 3D rotational matrix.
    @rtype:         numpy rank-2, 7D array
    """

    # Replicated calculations.
    ct = cos(flip)
    st = sin(flip)

    # Build the matrix.
    R = array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0,  ct, -st, 0.0, 0.0, 0.0],
        [0.0, 0.0,  st,  ct, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0,  ct, -st],
        [0.0, 0.0, 0.0, 0.0, 0.0,  st,  ct]
    ], float64)

    # Return the matrix.
    return R


def rcpmg_2d(R2A=None, R2B=None, dw=None, k_AB=None, k_BA=None):
    """Definition of the 2D exchange matrix.

    @keyword R2A:   The transverse, spin-spin relaxation rate for state A.
    @type R2A:      float
    @keyword R2B:   The transverse, spin-spin relaxation rate for state B.
    @type R2B:      float
    @keyword dw:    The chemical exchange difference between states A and B in rad/s.  
    @type dw:       float
    @keyword k_AB:  The forward exchange rate from state A to state B.
    @type k_AB:     float
    @keyword k_BA:  The reverse exchange rate from state B to state A.
    @type k_BA:     float
    @return:        The relaxation matrix.
    @rtype:         numpy rank-2, 4D array
    """

    # The omega frequencies for states A and B (state A is assumed to be at zero frequency).
    wA = 0.0
    wB = wA + dw 

    # Create the matrix.
    temp = matrix([
        [ -R2A-k_AB,          -wA,       k_BA,        0.0],
        [        wA,    -R2A-k_AB,        0.0,       k_BA], 
        [      k_AB,          0.0,  -R2B-k_BA,        -wB], 
        [       0.0,         k_AB,         wB,  -R2B-k_BA]
    ])

    # Return the matrix.
    return temp


def rcpmg_3d(R1A=None, R1B=None, R2A=None, R2B=None, pA=None, pB=None, dw=None, k_AB=None, k_BA=None):
    """Definition of the 3D exchange matrix.

    @keyword R1A:   The longitudinal, spin-lattice relaxation rate for state A.
    @type R1A:      float
    @keyword R1B:   The longitudinal, spin-lattice relaxation rate for state B.
    @type R1B:      float
    @keyword R2A:   The transverse, spin-spin relaxation rate for state A.
    @type R2A:      float
    @keyword R2B:   The transverse, spin-spin relaxation rate for state B.
    @type R2B:      float
    @keyword pA:    The population of state A.
    @type pA:       float
    @keyword pB:    The population of state B.
    @type pB:       float
    @keyword dw:    The chemical exchange difference between states A and B in rad/s.
    @type dw:       float
    @keyword k_AB:  The forward exchange rate from state A to state B.
    @type k_AB:     float
    @keyword k_BA:  The reverse exchange rate from state B to state A.
    @type k_BA:     float
    @return:        The relaxation matrix.
    @rtype:         numpy rank-2, 7D array
    """

    # The omega frequencies for states A and B (state A is assumed to be at zero frequency).
    wA = 0.0
    wB = dw

    # Create the matrix.
    temp = matrix([
        [        0.0,       0.0,         0.0,       0.0,       0.0,        0.0,       0.0], 
        [        0.0, -R2A-k_AB,         -wA,       0.0,      k_BA,        0.0,       0.0],
        [        0.0,        wA,   -R2A-k_AB,       0.0,       0.0,       k_BA,       0.0], 
        [ 2.0*R1A*pA,       0.0,         0.0, -R1A-k_AB,       0.0,        0.0,      k_BA],
        [        0.0,      k_AB,         0.0,       0.0, -R2B-k_BA,        -wB,       0.0], 
        [        0.0,       0.0,        k_AB,       0.0,        wB,  -R2B-k_BA,       0.0],
        [ 2.0*R1B*pB,       0.0,         0.0,      k_AB,       0.0,        0.0, -R1B-k_BA]
    ])

    # Return the matrix.
    return temp


def rcpmg_3d_rankN(R1A=None, R1B=None, R2A=None, R2B=None, pA=None, pB=None, dw=None, k_AB=None, k_BA=None, tcp=None):
    """Definition of the 3D exchange matrix, for rank [NE][NS][NM][NO][ND][7][7].

    @keyword R1A:   The longitudinal, spin-lattice relaxation rate for state A.
    @type R1A:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword R1B:   The longitudinal, spin-lattice relaxation rate for state B.
    @type R1B:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword R2A:   The transverse, spin-spin relaxation rate for state A.
    @type R2A:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword R2B:   The transverse, spin-spin relaxation rate for state B.
    @type R2B:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword pA:    The population of state A.
    @type pA:       float
    @keyword pB:    The population of state B.
    @type pB:       float
    @keyword dw:    The chemical exchange difference between states A and B in rad/s.
    @type dw:       numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword k_AB:  The forward exchange rate from state A to state B.
    @type k_AB:     float
    @keyword k_BA:  The reverse exchange rate from state B to state A.
    @type k_BA:     float
    @keyword tcp:   The tau_CPMG times (1 / 4.nu1).
    @type tcp:      numpy float array of rank [NE][NS][NM][NO][ND]
    @return:        The relaxation matrix.
    @rtype:         numpy float array of rank [NE][NS][NM][NO][ND][7][7]
    """

    # The omega frequencies for states A and B (state A is assumed to be at zero frequency).
    wA = 0.0
    wB = dw

    r10a_tcp = R1A * tcp
    r10b_tcp = R1B * tcp
    r20a_tcp = R2A * tcp
    r20b_tcp = R2B * tcp
    pA_tcp = pA * tcp
    pB_tcp = pB * tcp
    dw_tcp = dw * tcp
    k_AB_tcp = k_AB * tcp
    k_BA_tcp = k_BA * tcp
    wA_tcp = wA * tcp
    wB_tcp = wB * tcp

    # Create the matrix.
    m_r10a = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_pA = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_r10b = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0], ])

    m_pB = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_r20a = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_r20b = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_k_AB = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0], ])

    m_k_BA = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0], ])

    m_wA = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_wB = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    # Multiply and expand.
    m_r10a_tcp = multiply.outer( r10a_tcp, m_r10a )
    m_pA_tcp = multiply.outer( pA_tcp, m_pA )

    m_r10b_tcp = multiply.outer( r10b_tcp, m_r10b )
    m_pB_tcp = multiply.outer( pB_tcp, m_pB )

    m_r20a_tcp = multiply.outer( r20a_tcp, m_r20a )
    m_r20b_tcp = multiply.outer( r20b_tcp, m_r20b )

    m_k_AB_tcp = multiply.outer( k_AB_tcp, m_k_AB )
    m_k_BA_tcp = multiply.outer( k_BA_tcp, m_k_BA )

    m_wA_tcp = multiply.outer( wA_tcp, m_wA )
    m_wB_tcp = multiply.outer( wB_tcp, m_wB )

    # Collect matrix.
    c_mat = (m_r10a_tcp * m_pA_tcp + m_r10b_tcp * m_pB_tcp
        + m_r20a_tcp + m_r20b_tcp
        + m_k_AB_tcp + m_k_BA_tcp
        + m_wA_tcp + m_wB_tcp )

    # Return the matrix.
    return c_mat


def rr1rho_3d_3site(matrix=None, R1=None, r1rho_prime=None, pA=None, pB=None, pC=None, wA=None, wB=None, wC=None, w1=None, k_AB=None, k_BA=None, k_BC=None, k_CB=None, k_AC=None, k_CA=None):
    """Definition of the 3D exchange matrix.

    @keyword matrix:        The matrix to fill.
    @type matrix:           numpy rank-2 9D array
    @keyword R1:            The longitudinal, spin-lattice relaxation rate.
    @type R1:               float
    @keyword r1rho_prime:   The R1rho transverse, spin-spin relaxation rate in the absence of exchange.
    @type r1rho_prime:      float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword pC:            The population of state C.
    @type pC:               float
    @keyword wA:            The chemical shift offset of state A from the spin-lock.
    @type wA:               float
    @keyword wB:            The chemical shift offset of state B from the spin-lock.
    @type wB:               float
    @keyword wC:            The chemical shift offset of state C from the spin-lock.
    @type wC:               float
    @keyword w1:            The spin-lock field strength in rad/s.
    @type w1:               float
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
    """

    # The AB auto-block.
    matrix[0, 0] = -r1rho_prime - k_AB - k_AC
    matrix[0, 1] = -wA
    matrix[1, 0] = wA
    matrix[1, 1] = -r1rho_prime - k_AB - k_AC
    matrix[1, 2] = -w1
    matrix[2, 1] = w1
    matrix[2, 2] = -R1 - k_AB - k_AC

    # The AC auto-block.
    matrix[3, 3] = -r1rho_prime - k_BA - k_BC
    matrix[3, 4] = -wB
    matrix[4, 3] = wB
    matrix[4, 4] = -r1rho_prime - k_BA - k_BC
    matrix[4, 5] = -w1
    matrix[5, 4] = w1
    matrix[5, 5] = -R1 - k_BA - k_BC

    # The BC auto-block.
    matrix[6, 6] = -r1rho_prime - k_CA - k_CB
    matrix[6, 7] = -wC
    matrix[7, 6] = wC
    matrix[7, 7] = -r1rho_prime - k_CA - k_CB
    matrix[7, 8] = -w1
    matrix[8, 7] = w1
    matrix[8, 8] = -R1 - k_CA - k_CB

    # The AB cross-block.
    matrix[0, 3] = k_BA
    matrix[1, 4] = k_BA
    matrix[2, 5] = k_BA
    matrix[3, 0] = k_AB
    matrix[4, 1] = k_AB
    matrix[5, 2] = k_AB

    # The AC cross-block.
    matrix[0, 6] = k_CA
    matrix[1, 7] = k_CA
    matrix[2, 8] = k_CA
    matrix[6, 0] = k_AC
    matrix[7, 1] = k_AC
    matrix[8, 2] = k_AC

    # The BC cross-block.
    matrix[3, 6] = k_CB
    matrix[4, 7] = k_CB
    matrix[5, 8] = k_CB
    matrix[6, 3] = k_BC
    matrix[7, 4] = k_BC
    matrix[8, 5] = k_BC


def rr1rho_3d(matrix=None, R1=None, r1rho_prime=None, pA=None, pB=None, wA=None, wB=None, w1=None, k_AB=None, k_BA=None):
    """Definition of the 3D exchange matrix.

    This code originates from the funNumrho.m file from the Skrynikov & Tollinger code (the sim_all.tar file https://gna.org/support/download.php?file_id=18404 attached to https://gna.org/task/?7712#comment5).


    @keyword matrix:        The matrix to fill.
    @type matrix:           numpy rank-2 6D array
    @keyword R1:            The longitudinal, spin-lattice relaxation rate.
    @type R1:               float
    @keyword r1rho_prime:   The R1rho transverse, spin-spin relaxation rate in the absence of exchange.
    @type r1rho_prime:      float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword wA:            The chemical shift offset of state A from the spin-lock.
    @type wA:               float
    @keyword wB:            The chemical shift offset of state A from the spin-lock.
    @type wB:               float
    @keyword w1:            The spin-lock field strength in rad/s.
    @type w1:               float
    @keyword k_AB:          The forward exchange rate from state A to state B.
    @type k_AB:             float
    @keyword k_BA:          The reverse exchange rate from state B to state A.
    @type k_BA:             float
    """

    # The AB auto-block.
    matrix[0, 0] = -r1rho_prime - k_AB
    matrix[0, 1] = -wA
    matrix[1, 0] = wA
    matrix[1, 1] = -r1rho_prime - k_AB
    matrix[1, 2] = -w1
    matrix[2, 1] = w1
    matrix[2, 2] = -R1 - k_AB

    # The BA auto-block.
    matrix[3, 3] = -r1rho_prime - k_BA
    matrix[3, 4] = -wB
    matrix[4, 3] = wB
    matrix[4, 4] = -r1rho_prime - k_BA
    matrix[4, 5] = -w1
    matrix[5, 4] = w1
    matrix[5, 5] = -R1 - k_BA

    # The AB cross-block.
    matrix[0, 3] = k_BA
    matrix[1, 4] = k_BA
    matrix[2, 5] = k_BA
    matrix[3, 0] = k_AB
    matrix[4, 1] = k_AB
    matrix[5, 2] = k_AB


def rr1rho_3d_rankN(R1=None, r1rho_prime=None, pA=None, pB=None, dw=None, omega=None, offset=None, w1=None, k_AB=None, k_BA=None, relax_time=None):
    """Definition of the multidimensional 3D exchange matrix, of rank [NE][NS][NM][NO][ND][6][6].

    This code originates from the funNumrho.m file from the Skrynikov & Tollinger code (the sim_all.tar file https://gna.org/support/download.php?file_id=18404 attached to https://gna.org/task/?7712#comment5).


    @keyword R1:            The longitudinal, spin-lattice relaxation rate.
    @type R1:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r1rho_prime:   The R1rho transverse, spin-spin relaxation rate in the absence of exchange.
    @type r1rho_prime:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NS][NM][NO][ND]
    @keyword omega:         The chemical shift for the spin in rad/s.
    @type omega:            numpy float array of rank [NS][NM][NO][ND]
    @keyword offset:        The spin-lock offsets for the data.
    @type offset:           numpy float array of rank [NS][NM][NO][ND]
    @keyword w1:            The spin-lock field strength in rad/s.
    @type w1:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword k_AB:          The forward exchange rate from state A to state B.
    @type k_AB:             float
    @keyword k_BA:          The reverse exchange rate from state B to state A.
    @type k_BA:             float
    @keyword k_BA:          The reverse exchange rate from state B to state A.
    @type k_BA:             float
    @keyword relax_time:    The total relaxation time period for each spin-lock field strength (in seconds).
    @type relax_time:       numpy float array of rank [NS][NM][NO][ND]
    @return:                The relaxation matrix.
    @rtype:                 numpy float array of rank [NE][NS][NM][NO][ND][6][6]
    """

    # Wa: The chemical shift offset of state A from the spin-lock. Larmor frequency [s^-1].
    Wa = omega
    # Wb: The chemical shift offset of state A from the spin-lock. Larmor frequency [s^-1].
    Wb = omega + dw

    # Population-averaged Larmor frequency [s^-1].
    W = pA*Wa + pB*Wb

    # Offset of spin-lock from A.
    dA = Wa - offset

    # Offset of spin-lock from B.
    dB = Wb - offset

    # Offset of spin-lock from population-average.
    d = W - offset

    wA=dA
    wB=dB


    m_r1rho_prime = array([
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_wA = array([
        [0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_wB = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ])

    m_w1 = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0], ])

    m_k_AB = array([
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0], ])

    m_k_BA = array([
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, -1.0], ])

    m_R1 = array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, -1.0], ])

    # Multiply and expand.
    mat_r1rho_prime = multiply.outer( r1rho_prime * relax_time, m_r1rho_prime )

    mat_wA = multiply.outer( wA * relax_time, m_wA )
    mat_wB = multiply.outer( wB * relax_time, m_wB )

    mat_w1 = multiply.outer( w1 * relax_time, m_w1 )

    mat_k_AB = multiply.outer( k_AB * relax_time, m_k_AB )
    mat_k_BA = multiply.outer( k_BA * relax_time, m_k_BA )

    mat_R1 = multiply.outer( R1 * relax_time, m_R1 )

    # Collect matrix.
    matrix = (mat_r1rho_prime + mat_wA + mat_wB
        + mat_w1 + mat_k_AB + mat_k_BA
        + mat_R1)

    # Return the matrix.
    return matrix