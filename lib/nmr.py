###############################################################################
#                                                                             #
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
"""Module containing functions related to basic NMR concepts."""

# Python module imports.
from math import atan2, pi, sqrt

# relax module imports.
from lib.physical_constants import g1H, return_gyromagnetic_ratio


def frequency_to_Hz(frq=None, B0=None, isotope=None):
    """Convert the given frequency from ppm to Hertz units.

    @keyword frq:       The frequency in ppm.
    @type frq:          float
    @keyword B0:        The magnetic field strength as the proton frequency in Hertz.
    @type B0:           float
    @keyword isotope:   The isotope type of the nucleus of interest.
    @type isotope:      str
    @return:            The frequency in Hertz.
    @rtype:             float
    """

    # Convert and return.
    return frq * B0 / g1H * return_gyromagnetic_ratio(isotope) * 1e-6


def frequency_to_ppm(frq=None, B0=None, isotope=None):
    """Convert the given frequency from Hertz to ppm units.

    @keyword frq:       The frequency in Hertz.
    @type frq:          float
    @keyword B0:        The magnetic field strength as the proton frequency in Hertz.
    @type B0:           float
    @keyword isotope:   The isotope type of the nucleus of interest.
    @type isotope:      str
    @return:            The frequency in ppm.
    @rtype:             float
    """

    # Convert and return.
    return frq / B0 * g1H / return_gyromagnetic_ratio(isotope) / 1e-6


def frequency_to_ppm_from_rad(frq=None, B0=None, isotope=None):
    """Convert the given frequency from rad/s to ppm units.

    @keyword frq:       The frequency in rad/s.
    @type frq:          float
    @keyword B0:        The magnetic field strength as the proton frequency in Hertz.
    @type B0:           float
    @keyword isotope:   The isotope type of the nucleus of interest.
    @type isotope:      str
    @return:            The frequency in ppm.
    @rtype:             float
    """

    # Convert and return.
    return frq / (2.0 * pi) / B0 * g1H / return_gyromagnetic_ratio(isotope) / 1e-6


def frequency_to_rad_per_s(frq=None, B0=None, isotope=None):
    """Convert the given frequency from ppm to rad/s units.

    @keyword frq:       The frequency in ppm.
    @type frq:          float
    @keyword B0:        The magnetic field strength as the proton frequency in Hertz.
    @type B0:           float
    @keyword isotope:   The isotope type of the nucleus of interest.
    @type isotope:      str
    @return:            The frequency in rad/s.
    @rtype:             float
    """

    # Convert and return.
    return frq * 2.0 * pi * B0 / g1H * return_gyromagnetic_ratio(isotope) * 1e-6


def rotating_frame_params(chemical_shift=None, spin_lock_offset=None, omega1=None):
    """Calculate the rotating frame paramaters.

    @keyword chemical_shift:    The chemical shift in rad/s.
    @type chemical_shift:       float
    @keyword spin_lock_offset:  spin-lock offset in rad/s.
    @type spin_lock_offset:     float
    @keyword omega1:            Spin-lock field strength in rad/s.
    @type omega1:               float
    @return:                    The average resonance offset in the rotating frame, angle describing the tilted rotating frame relative to the laboratory, effective field in rotating frame.
    @rtype:                     float, float, float
    """

    # The average resonance offset in the rotating frame.
    Delta_omega = chemical_shift - spin_lock_offset

    # Calculate the theta angle describing the tilted rotating frame relative to the laboratory.
    # theta = atan(omega1 / Delta_omega).
    # If Delta_omega is negative, there follow the symmetry of atan, that atan(-x) = - atan(x).
    # Then it should be: theta = pi + atan(-x) = pi - atan(x) = pi - abs(atan( +/- x)).
    # This is taken care of with the atan2(y, x) function, which return atan(y / x), in radians, and the result is between -pi and pi.
    if Delta_omega == 0.0:
        theta = pi / 2.0
    else:
        theta = atan2(omega1, Delta_omega)

    # Calculate effective field in rotating frame.
    w_eff = sqrt( Delta_omega*Delta_omega + omega1*omega1 )

    return Delta_omega, theta, w_eff
