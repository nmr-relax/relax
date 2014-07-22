###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Paul Schanda (https://gna.org/users/pasa)           #
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
"""The numerical fit of 2-site Bloch-McConnell equations for CPMG-type experiments, the U{NS CPMG 2-site 3D<http://wiki.nmr-relax.com/NS_CPMG_2-site_3D>} and U{NS CPMG 2-site 3D full<http://wiki.nmr-relax.com/NS_CPMG_2-site_3D_full>} models.

Description
===========

The function uses an explicit matrix that contains relaxation, exchange and chemical shift terms.  It does the 180deg pulses in the CPMG train.  The approach of Bloch-McConnell can be found in chapter 3.1 of Palmer, A. G. Chem Rev 2004, 104, 3623-3640.  This function was written, initially in MATLAB, in 2010.


Code origin
===========

This is the model of the numerical solution for the 2-site Bloch-McConnell equations.  It originates as optimization function number 1 from the fitting_main_kex.py script from Mathilde Lescanne, Paul Schanda, and Dominique Marion (see U{http://thread.gmane.org/gmane.science.nmr.relax.devel/4138}, U{https://gna.org/task/?7712#comment2} and U{https://gna.org/support/download.php?file_id=18262}).


Links
=====

More information on the NS CPMG 2-site 3D model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_CPMG_2-site_3D>},
    - U{relax manual<http://www.nmr-relax.com/manual/reduced_NS_2_site_3D_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_CPMG_2-site_3D>}.

More information on the NS CPMG 2-site 3D full model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_CPMG_2-site_3D_full>},
    - U{relax manual<http://www.nmr-relax.com/manual/full_NS_2_site_3D_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_CPMG_2-site_3D_full>}.
"""

# Python module imports.
from numpy import array, dot, fabs, float64, einsum, isfinite, log, min, multiply, rollaxis, sum
from numpy.linalg import matrix_power
from numpy.ma import fix_invalid, masked_where

# relax module imports.
from lib.float import isNaN
from lib.dispersion.matrix_exponential import matrix_exponential_rank_NE_NS_NM_NO_ND_x_x

# Repetitive calculations (to speed up calculations).
m_r10a = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [1,  0,  0, -1,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0]], float64)

m_pA = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [2,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0]], float64)

m_r10b = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [1,  0,  0,  0,  0,  0, -1]], float64)

m_pB = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [2,  0,  0,  0,  0,  0,  0]], float64)

m_r20a = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0, -1,  0,  0,  0,  0,  0],
    [0,  0, -1,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0]], float64)

m_r20b = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0, -1,  0,  0],
    [0,  0,  0,  0,  0, -1,  0],
    [0,  0,  0,  0,  0,  0,  0]], float64)

m_k_AB = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0, -1,  0,  0,  0,  0,  0],
    [0,  0, -1,  0,  0,  0,  0],
    [0,  0,  0, -1,  0,  0,  0],
    [0,  1,  0,  0,  0,  0,  0],
    [0,  0,  1,  0,  0,  0,  0],
    [0,  0,  0,  1,  0,  0,  0]], float64)

m_k_BA = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  1,  0,  0],
    [0,  0,  0,  0,  0,  1,  0],
    [0,  0,  0,  0,  0,  0,  1],
    [0,  0,  0,  0, -1,  0,  0],
    [0,  0,  0,  0,  0, -1,  0],
    [0,  0,  0,  0,  0,  0, -1]], float64)

m_wA = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0, -1,  0,  0,  0,  0],
    [0,  1,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0]], float64)

m_wB = array([
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0, -1,  0],
    [0,  0,  0,  0,  1,  0,  0],
    [0,  0,  0,  0,  0,  0,  0]], float64)


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


def r2eff_ns_cpmg_2site_3D(r180x=None, M0=None, M0_T=None, r10a=0.0, r10b=0.0, r20a=None, r20b=None, pA=None, dw=None, dw_orig=None, kex=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation.

    This function calculates and stores the R2eff values.


    @keyword r180x:         The X-axis pi-pulse propagator.
    @type r180x:            numpy float64, rank-2, 7D array
    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float array of rank [NE][NS][NM][NO][ND][7][1]
    @keyword M0_T:          This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations, where the outer two axis has been swapped for efficient dot operations.
    @type M0_T:             numpy float array of rank [NE][NS][NM][NO][ND][1][7]
    @keyword r10a:          The R1 value for state A.
    @type r10a:             float
    @keyword r10b:          The R1 value for state B.
    @type r10b:             float
    @keyword r20a:          The R2 value for state A in the absence of exchange.
    @type r20a:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r20b:          The R2 value for state B in the absence of exchange.
    @type r20b:             numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw_orig:       The chemical exchange difference between states A and B in ppm. This is only for faster checking of zero value, which result in no exchange.
    @type dw_orig:          numpy float array of rank-1
    @keyword kex:           The kex parameter value (the exchange rate in rad/s).
    @type kex:              float
    @keyword inv_tcpmg:     The inverse of the total duration of the CPMG element (in inverse seconds).
    @type inv_tcpmg:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword tcp:           The tau_CPMG times (1 / 4.nu1).
    @type tcp:              numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:     The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:        numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword num_points:    The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:       numpy int array of rank [NE][NS][NM][NO]
    @keyword power:         The matrix exponential power array.
    @type power:            numpy int array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced if math function is violated.
    t_dw_zero = False

    # Catch parameter values that will result in no exchange, returning flat R2eff = R20 lines (when kex = 0.0, k_AB = 0.0).
    if pA == 1.0 or kex == 0.0:
        back_calc[:] = r20a
        return

    # Test if dw is zero. Create a mask for the affected spins to replace these with R20 at the end of the calculationWait for replacement, since this is spin specific.
    if min(fabs(dw_orig)) == 0.0:
        t_dw_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)

    # Once off parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex

    # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    M0_T[:, :, :, :, :, 0, 1] = pA
    M0_T[:, :, :, :, :, 0, 4] = pB
    M0[:, :, :, :, :, 1, 0] = pA
    M0[:, :, :, :, :, 4, 0] = pB

    # Extract the total numbers of experiments, number of spins, number of magnetic field strength, number of offsets, maximum number of dispersion point.
    NE, NS, NM, NO, ND = back_calc.shape

    # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R_mat = rcpmg_3d_rankN(R1A=r10a, R1B=r10b, R2A=r20a, R2B=r20b, pA=pA, pB=pB, dw=dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)

    # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
    Rexpo_mat = matrix_exponential_rank_NE_NS_NM_NO_ND_x_x(R_mat)

    # The the essential evolution matrix.
    # This is a dot product of the outer [7][7] matrix of the Rexpo_mat and r180x matrixes, which
    # have the shape [NE][NS][NM][NO][ND][7][7] and [7][7].
    # This can be achieved by using numpy einsum, and where ellipsis notation will use the last axis.
    evolution_matrix_mat = einsum('...ij,...jk', Rexpo_mat, r180x)
    evolution_matrix_mat = einsum('...ij,...jk', evolution_matrix_mat, Rexpo_mat)
    evolution_matrix_mat = einsum('...ij,...jk', evolution_matrix_mat, evolution_matrix_mat)

    # Roll axis around.
    evolution_matrix_T_mat = rollaxis(evolution_matrix_mat, 6, 5)

    # Preform the initial magnetisation.
    evolution_matrix_T_M0_mat = einsum('...ij,...jk', M0_T, evolution_matrix_T_mat)

    # Loop over the spins
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Extract number of points.
            num_points_si_mi = int(num_points[0, si, mi, 0])

            # Loop over the time points, back calculating the R2eff values.
            for di in range(num_points_si_mi):
                # Extract the values from the higher dimensional arrays.
                inv_tcpmg_si_mi_di = inv_tcpmg[0, si, mi, 0, di]
                power_si_mi_di = int(power[0, si, mi, 0, di])
                r20a_si_mi_di = r20a[0, si, mi, 0, di]

                # Initial magnetisation.
                Mint_T_i = evolution_matrix_T_M0_mat[0, si, mi, 0, di]

                # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
                evolution_matrix_T_i = evolution_matrix_T_mat[0, si, mi, 0, di]

                # Get which power to raise the matrix to.
                l = int(power_si_mi_di-1)

                # Raise the square evolution matrix to the power l.
                evolution_matrix_T_power_i = matrix_power(evolution_matrix_T_i, l)

                # Evolve the magnetisation.
                Mint_T_i = dot(Mint_T_i, evolution_matrix_T_power_i)

                # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                Mx = Mint_T_i[0][1] / pA
                if Mx <= 0.0 or isNaN(Mx):
                    back_calc[0, si, mi, 0, di] = r20a_si_mi_di
                else:
                    back_calc[0, si, mi, 0, di] = - inv_tcpmg_si_mi_di * log(Mx)

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20a[mask_dw_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
