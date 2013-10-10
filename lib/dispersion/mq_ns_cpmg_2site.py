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
from numpy import dot
if dep_check.scipy_module:
    from scipy.linalg import expm

# relax module imports.
from lib.dispersion.ns_matrices import rcpmg_3d
from lib.float import isNaN


def m1(matrix=None, r20=None, dw=None, dwH=None, k_AB=None, k_BA=None):
    """Matrix for HMQC experiments.

    This corresponds to matrix m1 of equation 2.2 from:

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


def m2(matrix=None, r20=None, dw=None, dwH=None, k_AB=None, k_BA=None):
    """Matrix for HMQC experiments.

    This corresponds to matrix m1 of equation 2.2 from:

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
    matrix[1, 1] = -k_BA - 1.j*(dwH - dw) - r20


def r2eff_mq_ns_cpmg_2site(M0=None, m1=None, m2=None, r20=None, pA=None, pB=None, dw=None, dwH=None, k_AB=None, k_BA=None, inv_tcpmg=None, tcp=None, back_calc=None, num_points=None, power=None):
    """The 2-site numerical solution to the Bloch-McConnell equation.

    This function calculates and stores the R2eff values.


    @keyword M0:            This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:               numpy float64, rank-1, 7D array
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

    # Loop over the time points, back calculating the R2eff values.
    for i in range(num_points):
        # Initial magnetisation.
        Mint = M0

        # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
        Rexpo = expm(R*tcp[i])

        # Loop over the CPMG elements, propagating the magnetisation.
        for j in range(2*power[i]):
            Mint = dot(Rexpo, Mint)
            Mint = dot(r180x, Mint)
            Mint = dot(Rexpo, Mint)

        # The next lines calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential.
        Mx = fabs(Mint[1] / pA)
        if Mx <= 0.0 or isNaN(Mx):
            back_calc[i] = 1e99
        else:
            back_calc[i]= -inv_tcpmg * log(Mx)

    return

    Rcalc_array=np.zeros(len(nb_pulse))
    M0=np.matrix([[pg],[1-pg]])
    for k in range(len(nb_pulse)):
        tcp=Tc/(4.0*nb_pulse[k])
        M1=expm(m1(r22gg,dw, dwH,kex,pg)*tcp)        ##MULTIPLICATION BY 600MHz !!!!!!!
        M1c=np.conj(expm(m1(r22gg,dw,dwH,kex,pg)*tcp))    ##MULTIPLICATION BY 600MHz !!!!!!!
        M2=expm(m2(r22gg,dw, dwH,kex,pg)*tcp)        ##MULTIPLICATION BY 600MHz !!!!!!!
        M2c=np.conj(expm(m2(r22gg,dw,dwH,kex,pg)*tcp))    ##MULTIPLICATION BY 600MHz !!!!!!!
        if int(nb_pulse[k])%2==0:
            A=mpower(np.dot(np.dot(np.dot(M1,M2),M2),M1), int(nb_pulse[k])/2) #M1*M2*M2*M1
            B=mpower(np.dot(np.dot(np.dot(M2c,M1c),M1c),M2c), int(nb_pulse[k])/2) #(M2c*M1c*M1c*M2c,int(nb_pulse[k])/2)
            C=mpower(np.dot(np.dot(np.dot(M2,M1),M1),M2), int(nb_pulse[k])/2) #(M2*M1*M1*M2,int(nb_pulse[k])/2)
            D=mpower(np.dot(np.dot(np.dot(M1c,M2c),M2c),M1c), int(nb_pulse[k])/2) #mpower(M1c*M2c*M2c*M1c,int(nb_pulse[k])/2)
        else:
            A=np.dot(np.dot(mpower(np.dot(np.dot(np.dot(M1,M2),M2),M1),(int(nb_pulse[k])-1)/2),M1),M2)
            B=np.dot(np.dot(mpower(np.dot(np.dot(np.dot(M1c,M2c),M2c),M1c),(int(nb_pulse[k])-1)/2),M1c),M2c) 
            C=np.dot(np.dot(mpower(np.dot(np.dot(np.dot(M2,M1),M1),M2),(int(nb_pulse[k])-1)/2),M2),M1)
            D=np.dot(np.dot(mpower(np.dot(np.dot(np.dot(M2c,M1c),M1c),M2c),(int(nb_pulse[k])-1)/2),M2c),M1c)
        Rcalc_array[k]=-(1.0/Tc)*log(((0.5/pg)*np.matrix([1,0])*(np.dot(A,B)+np.dot(C,D))*M0).real)
    return Rcalc_array



