###############################################################################
#                                                                             #
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
"""This function performs a numerical fit of 2-site Bloch-McConnell equations for MQ CPMG-type experiments.

The function uses an explicit matrix that contains relaxation, exchange and chemical shift terms.  It does the 180deg pulses in the CPMG train.  The approach of Bloch-McConnell can be found in chapter 3.1 of Palmer, A. G. Chem Rev 2004, 104, 3623-3640.

This is the model of the numerical solution for the 2-site Bloch-McConnell equations for multi-quantum CPMG-type data.  It originates as the m1 and m2 matrices and the fp0() optimization function from the fitting_main_kex.py script from Mathilde Lescanne and Dominique Marion (https://gna.org/task/?7712#comment7 and the files attached in that comment).
"""

# Dependency check module.
import dep_check

# Python module imports.
from math import fabs, log
from numpy import array, conj, dot, float64

# relax module imports.
from lib.dispersion.ns_matrices import rcpmg_3d
from lib.float import isNaN
from lib.linear_algebra.matrix_exponential import matrix_exponential
from lib.linear_algebra.matrix_power import square_matrix_power


def populate_matrix(matrix=None, r20=None, dw=None, dwH=None, k_AB=None, k_BA=None):
    """Matrix for HMQC experiments.

    This corresponds to matrix m1 and m2 matrices of equation 2.2 from:

        - Korzhnev, D. M., Kloiber, K., Kanelis, V., Tugarinov, V., and Kay, L. E. (2004).  Probing slow dynamics in high molecular weight proteins by methyl-TROSY NMR spectroscopy: Application to a 723-residue enzyme.  J. Am. Chem. Soc., 126, 3964-3973.  (U{DOI: 10.1021/ja039587i<http://dx.doi.org/10.1021/ja039587i>}).

    @keyword matrix:        The matrix to populate.
    @type matrix:           numpy rank-2, 2D complex64 array
    @keyword r20:           The R2 value in the absence of exchange.
    @type r20:              float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword dwH:           The proton chemical exchange difference between states A and B in rad/s.
    @type dwH:              float
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
    """

    # Fill in the elements.
    matrix[0, 0] = -k_AB - r20
    matrix[0, 1] = k_BA
    matrix[1, 0] = k_AB
    matrix[1, 1] = -k_BA - 1.j*(dwH + dw) - r20


def r2eff_mq_ns_cpmg_2site(M0=None, F_vector=array([1, 0], float64), m1=None, m2=None, r20=None, pA=None, pB=None, dw=None, dwH=None, k_AB=None, k_BA=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation.

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
    @keyword F_vector:      The observable magnitisation vector.  This defaults to [1, 0] for X observable magnitisation.
    @type F_vector:         numpy rank-1, 2D float64 array
    @keyword m1:            A complex numpy matrix to be populated.
    @type m1:               numpy rank-2, 2D complex64 array
    @keyword m2:            A complex numpy matrix to be populated.
    @type m2:               numpy rank-2, 2D complex64 array
    @keyword r20:           The R2 value in the absence of exchange.
    @type r20:              float
    @keyword pA:            The population of state A.
    @type pA:               float
    @keyword pB:            The population of state B.
    @type pB:               float
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               float
    @keyword dwH:           The proton chemical exchange difference between states A and B in rad/s.
    @type dwH:              float
    @keyword k_AB:          The rate of exchange from site A to B (rad/s).
    @type k_AB:             float
    @keyword k_BA:          The rate of exchange from site B to A (rad/s).
    @type k_BA:             float
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

    # Populate the m1 and m2 matrices (only once per function call for speed).
    populate_matrix(matrix=m1, r20=r20, dw=dw, dwH=dwH, k_AB=k_AB, k_BA=k_BA)
    populate_matrix(matrix=m2, r20=r20, dw=-dw, dwH=dwH, k_AB=k_AB, k_BA=k_BA)

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # The M1 and M2 matrices.
        M1 = matrix_exponential(m1*tcp[i])
        M2 = matrix_exponential(m2*tcp[i])

        # The complex conjugates M1* and M2*
        M1_star = conj(M1)
        M2_star = conj(M2)

        # Repetitive dot products (minimised for speed).
        M1_M2 = dot(M1, M2)
        M2_M1 = dot(M2, M1)
        M1_M2_M2_M1 = dot(M1_M2, M2_M1)
        M2_M1_M1_M2 = dot(M2_M1, M1_M2)
        M1_M2_star = dot(M1_star, M2_star)
        M2_M1_star = dot(M2_star, M1_star)
        M1_M2_M2_M1_star = dot(M1_M2_star, M2_M1_star)
        M2_M1_M1_M2_star = dot(M2_M1_star, M1_M2_star)

        # Matrices for even n.
        if power[i] % 2 == 0:
            # The power factor (only calculate once).
            fact = int(power[i] / 2)

            # (M1.M2.M2.M1)^(n/2)
            A = square_matrix_power(M1_M2_M2_M1, fact)

            # (M2*.M1*.M1*.M2*)^(n/2)
            B = square_matrix_power(M2_M1_M1_M2_star, fact)

            # (M2.M1.M1.M2)^(n/2)
            C = square_matrix_power(M2_M1_M1_M2, fact)

            # (M1*.M2*.M2*.M1*)^(n/2)
            D = square_matrix_power(M1_M2_M2_M1_star, fact)

        # Matrices for odd n.
        else:
            # The power factor (only calculate once).
            fact = int((power[i] - 1) / 2)

            # (M1.M2.M2.M1)^((n-1)/2).M1.M2
            A = square_matrix_power(M1_M2_M2_M1, fact)
            A = dot(A, M1_M2)

            # (M1*.M2*.M2*.M1*)^((n-1)/2).M1*.M2*
            B = square_matrix_power(M1_M2_M2_M1_star, fact)
            B = dot(B, M1_M2_star)

            # (M2.M1.M1.M2)^((n-1)/2).M2.M1
            C = square_matrix_power(M2_M1_M1_M2, fact)
            C = dot(C, M2_M1)

            # (M2*.M1*.M1*.M2*)^((n-1)/2).M2*.M1*
            D = square_matrix_power(M2_M1_M1_M2_star, fact)
            D = dot(D, M2_M1_star)

        # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
        A_B = dot(A, B)
        C_D = dot(C, D)
        Mx = dot(dot(F_vector, (A_B + C_D)), M0)
        Mx = Mx.real / (2.0 * pA)
        if Mx <= 0.0 or isNaN(Mx):
            back_calc[i] = 1e99
        else:
            back_calc[i]= -inv_tcpmg * log(Mx)
