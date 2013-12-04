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
from math import pi

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
