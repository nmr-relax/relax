###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
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
"""The numerical fit of 2-site Bloch-McConnell equations for CPMG-type experiments, the U{NS CPMG 2-site star<http://wiki.nmr-relax.com/NS_CPMG_2-site_star>} and U{NS CPMG 2-site star full<http://wiki.nmr-relax.com/NS_CPMG_2-site_star_full>} models.

Description
===========

The function uses an explicit matrix that contains relaxation, exchange and chemical shift terms. It does the 180deg pulses in the CPMG train with conjugate complex matrices.  The approach of Bloch-McConnell can be found in chapter 3.1 of Palmer, A. G. 2004 I{Chem. Rev.}, B{104}, 3623-3640.  This function was written, initially in MATLAB, in 2010.


Code origin
===========

The code was submitted at U{http://thread.gmane.org/gmane.science.nmr.relax.devel/4132} by Paul Schanda.


Links
=====

More information on the NS CPMG 2-site star model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_CPMG_2-site_star>},
    - U{relax manual<http://www.nmr-relax.com/manual/reduced_NS_2_site_star_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_CPMG_2-site_star>}.

More information on the NS CPMG 2-site star full model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_CPMG_2-site_star_full>},
    - U{relax manual<http://www.nmr-relax.com/manual/full_NS_2_site_star_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_CPMG_2-site_star_full>}.
"""

# Python module imports.
from numpy import add, array, conj, dot, einsum, fabs, float64, isfinite, log, min, multiply, sum
from numpy.ma import fix_invalid, masked_where
from numpy.linalg import matrix_power

# relax module imports.
from lib.float import isNaN
from lib.dispersion.matrix_exponential import matrix_exponential_rank_NE_NS_NM_NO_ND_x_x

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


def rcpmg_star_rankN(R2A=None, R2B=None, dw=None, k_AB=None, k_BA=None, tcp=None):
    """Definition of the exchange matrix, for rank [NE][NS][NM][NO][ND][2][2].

    @keyword R2A:   The transverse, spin-spin relaxation rate for state A.
    @type R2A:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword R2B:   The transverse, spin-spin relaxation rate for state B.
    @type R2B:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw:    The chemical exchange difference between states A and B in rad/s.
    @type dw:       numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword k_AB:  The forward exchange rate from state A to state B.
    @type k_AB:     float
    @keyword k_BA:  The reverse exchange rate from state B to state A.
    @type k_BA:     float
    @keyword tcp:   The tau_CPMG times (1 / 4.nu1).
    @type tcp:      numpy float array of rank [NE][NS][NM][NO][ND]
    @return:        The relaxation matrix R and complex conjugate cR2.
    @rtype:         numpy float array of rank [NE][NS][NM][NO][ND][2][2]
    """

    # Pre-multiply with tcp.
    r20a_tcp = R2A * tcp
    r20b_tcp = R2B * tcp
    k_AB_tcp = k_AB * tcp
    k_BA_tcp = k_BA * tcp
    # Complex dw.
    dw_tcp_C = dw * tcp * -1j

    # Create matrix for collection of Rr matrix.
    # The matrix that contains only the R2 relaxation terms ("Redfield relaxation", i.e. non-exchange broadening).
    #Rr[0, 0] = -R2A_si_mi
    #Rr[1, 1] = -R2B_si_mi

    # Multiply and expand.
    m_r20a_tcp = multiply.outer( r20a_tcp, m_r20a )
    m_r20b_tcp = multiply.outer( r20b_tcp, m_r20b )

    # Collect Rr matrix.
    Rr_mat = (m_r20a_tcp + m_r20b_tcp)

    # Create matrix for collection of Rex.
    # Set up the matrix that contains the exchange terms between the two states A and B.
    #Rex[0, 0] = -k_AB
    #Rex[0, 1] = k_BA
    #Rex[1, 0] = k_AB
    #Rex[1, 1] = -k_BA

    # Multiply and expand.
    m_k_AB_tcp = multiply.outer( k_AB_tcp, m_k_AB )
    m_k_BA_tcp = multiply.outer( k_BA_tcp, m_k_BA )

    # Collect Rex matrix.
    Rex_mat = (m_k_AB_tcp + m_k_BA_tcp)

    # Create the matrix for RCS.
    # The matrix that contains the chemical shift evolution.  It works here only with X magnetization, and the complex notation allows to evolve in the transverse plane (x, y).  The chemical shift for state A is assumed to be zero.
    #RCS[1, 1] = complex(0.0, -dw_si_mi)

    # Multiply and expand.
    m_dw_tcp_C = multiply.outer( dw_tcp_C, m_dw )

    # Collect RCS matrix.
    RCS_mat = m_dw_tcp_C

    # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R_mat = add(Rr_mat, Rex_mat)
    R_mat = add(R_mat, RCS_mat)

    # This is the complex conjugate of the above.  It allows the chemical shift to run in the other direction, i.e. it is used to evolve the shift after a 180 deg pulse.  The factor of 2 is to minimise the number of multiplications for the prop_2 matrix calculation.
    cR2_mat = conj(R_mat) * 2.0

    # Return the matrixes.
    return R_mat, cR2_mat, Rr_mat, Rex_mat, RCS_mat


def r2eff_ns_cpmg_2site_star(M0=None, r20a=None, r20b=None, pA=None, dw=None, dw_orig=None, kex=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation using complex conjugate matrices.

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 2D array
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
    M0[0] = pA
    M0[1] = pB

    # Extract the total numbers of experiments, number of spins, number of magnetic field strength, number of offsets, maximum number of dispersion point.
    NE, NS, NM, NO, ND = back_calc.shape

    # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R_mat, cR2_mat, Rr_mat, Rex_mat, RCS_mat = rcpmg_star_rankN(R2A=r20a, R2B=r20b, dw=dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)

    # The the essential evolution matrix.
    # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
    eR_mat = matrix_exponential_rank_NE_NS_NM_NO_ND_x_x(R_mat)
    ecR2_mat = matrix_exponential_rank_NE_NS_NM_NO_ND_x_x(cR2_mat)

    # Preform the matrix.
    # This is the propagator for an element of [delay tcp; 180 deg pulse; 2 times delay tcp; 180 deg pulse; delay tau], i.e. for 2 times tau-180-tau.
    prop_2_mat = evolution_matrix_mat = einsum('...ij, ...jk', eR_mat, ecR2_mat)
    prop_2_mat = evolution_matrix_mat = einsum('...ij, ...jk', prop_2_mat, eR_mat)

    # Loop over the spins
    for si in range(NS):
        # Loop over the spectrometer frequencies.
        for mi in range(NM):
            # Extract the values from the higher dimensional arrays.
            num_points_si_mi = int(num_points[0, si, mi, 0])

            # Loop over the time points, back calculating the R2eff values.
            for di in range(num_points_si_mi):
                # Extract the values from the higher dimensional arrays.
                power_si_mi_di = int(power[0, si, mi, 0, di])

                # This is the propagator for an element of [delay tcp; 180 deg pulse; 2 times delay tcp; 180 deg pulse; delay tau], i.e. for 2 times tau-180-tau.
                prop_2_i = prop_2_mat[0, si, mi, 0, di]

                # Now create the total propagator that will evolve the magnetization under the CPMG train, i.e. it applies the above tau-180-tau-tau-180-tau so many times as required for the CPMG frequency under consideration.
                prop_total = matrix_power(prop_2_i, power_si_mi_di)

                # Now we apply the above propagator to the initial magnetization vector - resulting in the magnetization that remains after the full CPMG pulse train.  It is called M of t (t is the time after the CPMG train).
                Moft = dot(prop_total, M0)

                # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
                Mx = Moft[0].real / M0[0]
                if Mx <= 0.0 or isNaN(Mx):
                    back_calc[0, si, mi, 0, di] = 1e99
                else:
                    back_calc[0, si, mi, 0, di]= -inv_tcpmg[0, si, mi, 0, di] * log(Mx)

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20a[mask_dw_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
