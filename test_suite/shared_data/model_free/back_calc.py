###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Functions for the back-calculation of relaxation data from model-free data."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import float64, zeros


# Physical constants.
h = 6.62606876 * 1e-34
h_bar = h / (2.0 * pi)
mu0 = 4.0 * pi * 1e-7
g13C = 6.728 * 1e7
g1H = 26.7522212 * 1e7
g15N = -2.7126 * 1e7


def csa_const(wX=None, csa=None):
    """Calculate the CSA constant.

    @keyword wX:    The heteronucleus frequency.
    @type wX:       float
    @keyword csa:   The chemical shift anisotropy (unitless).
    @type csa:      float
    @return:        The CSA constant.
    @rtype:         float
    """

    # Calculate and return.
    return (wX * csa) **2 / 3.0


def dipolar_const(gX, r):
    """Calculate the dipolar constant.

    @param gX:  The heteronucleus gyromagnetic ratio.
    @type gX:   float
    @param r:   The heteronucleus-proton bond length in meters.
    @type r:    float
    @return:    The dipolar constant.
    @rtype:     float
    """

    # Calculate and return.
    return 0.25 * (mu0 / (4.0*pi))**2 * (gX * g1H * h_bar)**2 / r**6


def relaxation_data(J, frq=None, heteronuc='15N', rex=0.0, r=1.02e-10, csa=-172e-6):
    """Calculate the R1, R2, and NOE values for the given spectral density values.

    @param J:           The spectral density values.  The first dimension of this 2D array are the different proton frequencies.  The second dimension is the 5 frequencies.
    @type J:            numpy rank-2 array
    @keyword frq:       The array of proton frequencies to calculate the spectral densities at.
    @type frq:          numpy rank-1 array
    @keyword heteronuc: The heteronucleus type, i.e. 15N, 13C, etc.
    @type heteronuc:    str
    @keyword rex:       The chemical exchange factor.
    @type rex:          float
    @keyword r:         The heteronucleus-proton bond length in meters.
    @type r:            float
    @keyword csa:       The chemical shift anisotropy (unitless).
    @type csa:          float
    @return:            The R1, R2, and NOE relaxation values at all spectrometer frequencies.  The first dimension are the different spectrometer frequencies.  The second dimension is the R1, R2, and NOE.
    @rtype:             numpy rank-2 array
    """

    # Initialise.
    Ri_prime = zeros((len(J), 3), float64)
    Ri =       zeros((len(J), 3), float64)

    # The heteronucleus gyromagnetic ratio.
    if heteronuc == '15N':
        gX = g15N
    elif heteronuc == '13C':
        gX = g13C

    # Calculate the dipolar constant.
    d = dipolar_const(gX, r)

    # Loop over the frequencies.
    for i in range(len(J)):
        # Calculate the 5 effective frequencies.
        omega = calc_omega(frq[i], heteronuc=heteronuc)

        # The CSA constant.
        c = csa_const(wX=omega[1], csa=csa)

        # The R1.
        Ri[i, 0] = Ri_prime[i, 0] = d * (3.0*J[i, 1] + J[i, 2] + 6.0*J[i, 4])  +  c * J[i, 1]

        # The R2.
        Ri[i, 1] = Ri_prime[i, 1] = 0.5 * d * (4.0*J[i, 0] + 3.0*J[i, 1] + J[i, 2] + 6.0*J[i, 3] + 6.0*J[i, 4])  +  c/6.0 * (4.0*J[i, 0] + 3.0*J[i, 1])  +  rex * (2.0 * pi * omega[3])**2

        # The sigma NOE.
        Ri_prime[i, 2] = d * (6.0*J[i, 4] - J[i, 2])

        # Calculate the NOE.
        Ri[i, 2] = 1.0  +  g1H/gX * Ri_prime[i, 2] / Ri_prime[i, 0]

    # Return the relaxation data.
    return Ri


def calc_omega(frq, heteronuc='15N'):
    """Calculate the 5 effective frequencies for the spectral density function.

    @param frq:         The proton frequency.
    @type frq:          float
    @keyword heteronuc: The heteronucleus type, i.e. 15N, 13C, etc.
    @type heteronuc:    str
    @return:            The 5 effective frequencies in rad/s.
    @rtype:             numpy rank-1, 5D array.
    """

    # Init.
    omega = zeros(5, float64)

    # The proton frequency in rad/s.
    frqH = frq * 2.0 * pi

    # The heteronucleus gyromagnetic ratio.
    if heteronuc == '15N':
        gX = g15N
    elif heteronuc == '13C':
        gX = g13C

    # The heteronucleus frequency.
    frqX = gX / g1H * frqH

    # The 5 frequencies.
    omega[0] = 0.0
    omega[1] = frqX
    omega[2] = frqH - frqX
    omega[3] = frqH
    omega[4] = frqH + frqX

    # Return the frequencies.
    return omega


def spectral_density_mf_orig(frq=None, tm=None, s2=1.0, te=0.0, heteronuc='15N'):
    """Calculate the spectral density values using the original Lipari and Szabo model-free theory.

    @keyword frq:       The array of proton frequencies to calculate the spectral densities at.
    @type frq:          numpy rank-1 array
    @keyword tm:        The global correlation time in seconds.
    @type tm:           float
    @keyword s2:        The generalised order parameter.
    @type s2:           float
    @keyword te:        The effective internal correlation time.
    @type te:           float
    @keyword heteronuc: The heteronucleus type, i.e. 15N, 13C, etc.
    @type heteronuc:    str
    @return:            The spectral density values.  The first dimension of this 2D array are the different proton frequencies.  The second dimension is the 5 frequencies.
    @rtype:             numpy rank-2 array
    """

    # Initialise.
    J = zeros((len(frq), 5), float64)

    # Loop over the frequencies.
    for i in range(len(frq)):
        # Calculate the 5 effective frequencies.
        omega = calc_omega(frq[i], heteronuc=heteronuc)

        # Loop over the effective frequencies.
        for j in range(5):
            # tau.
            if te == 0.0:
                tau = 0.0
            else:
                tau = 1.0 / (1.0/tm + 1.0/te)

            # The spectral density value.
            J[i, j] = s2 * tm / (1.0 + (tm*omega[j])**2)
            J[i, j] = J[i, j]  +  (1.0 - s2) * tau / (1.0 + (tau*omega[j])**2)
            J[i, j] = 0.4 * J[i, j]

    # Return the spectral density values.
    return J


def spectral_density_mf_ext(frq=None, tm=None, s2=1.0, s2f=1.0, tf=0.0, ts=0.0, heteronuc='15N'):
    """Calculate the spectral density values using the extended Lipari and Szabo model-free theory.

    @keyword frq:       The array of proton frequencies to calculate the spectral densities at.
    @type frq:          numpy rank-1 array
    @keyword tm:        The global correlation time in seconds.
    @type tm:           float
    @keyword s2:        The generalised order parameter (S2 = S2f*S2s).
    @type s2:           float
    @keyword s2f:       The generalised order parameter for the faster motion.
    @type s2f:          float
    @keyword tf:        The effective internal correlation time for the faster motion.
    @type tf:           float
    @keyword ts:        The effective internal correlation time for the slower motion.
    @type ts:           float
    @keyword heteronuc: The heteronucleus type, i.e. 15N, 13C, etc.
    @type heteronuc:    str
    @return:            The spectral density values.  The first dimension of this 2D array are the different proton frequencies.  The second dimension is the 5 frequencies.
    @rtype:             numpy rank-2 array
    """

    # Initialise.
    J = zeros((len(frq), 5), float64)

    # Loop over the frequencies.
    for i in range(len(frq)):
        # Calculate the 5 effective frequencies.
        omega = calc_omega(frq[i], heteronuc=heteronuc)

        # Loop over the effective frequencies.
        for j in range(5):
            # tf_prime.
            if tf == 0.0:
                tf_prime = 0.0
            else:
                tf_prime = 1.0 / (1.0/tm + 1.0/tf)

            # ts_prime.
            if ts == 0.0:
                ts_prime = 0.0
            else:
                ts_prime = 1.0 / (1.0/tm + 1.0/ts)

            # The spectral density value, part 1.
            part1 = s2 * tm / (1.0 + (tm*omega[j])**2)

            # The spectral density value, part 2.
            part2 = (1.0 - s2f) * tf_prime / (1.0 + (tf_prime*omega[j])**2)

            # The spectral density value, part 3.
            part3 = (s2f - s2) * ts_prime / (1.0 + (ts_prime*omega[j])**2)

            # Combine it all.
            J[i, j] = 0.4 * (part1 + part2 + part3)

    # Return the spectral density values.
    return J
