###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
"""Module for manipulating the spectrometer experimental information."""

# Python module imports.
from math import pi
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.physical_constants import g1H
from lib.warnings import RelaxWarning
from pipe_control import pipes


def get_frequencies(units='Hz'):
    """Return a list of all the current spectrometer frequencies.

    The returned values can be changed with the units argument which can have the following values:

        - 'Hz' will return the proton frequency (wH),
        - 'MHz' will return the proton frequency in megahertz,
        - 'T' will return the B0 field in Tesla.


    @keyword units: The magnetic field units to return.  This can be one of 'Hz', 'MHz', or 'T'.
    @type units:    str
    @return:        The frequency list for the current data pipe.
    @rtype:         list of float
    """

    # No frequency data.
    if not hasattr(cdp, 'spectrometer_frq'):
        return []

    # Convert the values.
    frq = []
    for value in cdp.spectrometer_frq_list:
        # Hertz.
        if units == 'Hz':
            frq.append(value)

        # MHz.
        elif units == 'MHz':
            frq.append(value * 1e-6)

        # Tesla.
        elif unit == 'T':
            frq.append(value * 2.0 * pi / g1H)

        # Unknown units.
        else:
            raise RelaxError("The units of '%s' should be one of 'Hz', 'MHz', or 'T'.")

    # Return the frqs.
    return frq


def set_frequency(id=None, frq=None, units='Hz'):
    """Set the spectrometer frequency of the experiment.

    @keyword id:    The experimental identification string (allowing for multiple experiments per data pipe).
    @type id:       str
    @keyword frq:   The spectrometer frequency in Hertz.
    @type frq:      float
    @keyword units: The units of frequency.  This can be one of "Hz", "kHz", "MHz", or "GHz".
    @type units:    str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Set up the data structures if missing.
    if not hasattr(cdp, 'spectrometer_frq'):
        cdp.spectrometer_frq = {}
        cdp.spectrometer_frq_list = []
        cdp.spectrometer_frq_count = 0

    # Test the frequency has not already been set.
    if id in cdp.spectrometer_frq and cdp.spectrometer_frq[id] != frq:
        raise RelaxError("The frequency for the experiment '%s' has already been set to %s Hz." % (id, cdp.spectrometer_frq[id]))

    # Unit conversion.
    if units == 'Hz':
        conv = 1.0
    elif units == 'kHz':
        conv = 1e3
    elif units == 'MHz':
        conv = 1e6
    elif units == 'GHz':
        conv = 1e9
    else:
        raise RelaxError("The frequency units of '%s' are unknown." % units)

    # Set the frequency.
    cdp.spectrometer_frq[id] = frq * conv

    # Warnings.
    if cdp.spectrometer_frq[id] < 1e8:
        warn(RelaxWarning("The proton frequency of %s Hz appears to be too low." % cdp.spectrometer_frq[id]))
    if cdp.spectrometer_frq[id] > 2e9:
        warn(RelaxWarning("The proton frequency of %s Hz appears to be too high." % cdp.spectrometer_frq[id]))

    # New frequency.
    if cdp.spectrometer_frq[id] not in cdp.spectrometer_frq_list:
        cdp.spectrometer_frq_list.append(cdp.spectrometer_frq[id])
        cdp.spectrometer_frq_count += 1


def set_temperature(id=None, temp=None):
    """Set the experimental temperature.

    @keyword id:    The experimental identification string (allowing for multiple experiments per data pipe).
    @type id:       str
    @keyword temp:  The temperature in kelvin.
    @type temp:     float
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Set up the dictionary data structure if it doesn't exist yet.
    if not hasattr(cdp, 'temperature'):
        cdp.temperature = {}

    # Convert to a float.
    temp = float(temp)

    # Test the temperature has not already been set.
    if id in cdp.temperature and cdp.temperature[id] != temp:
        raise RelaxError("The temperature for the experiment '%s' has already been set to %s K." % (id, cdp.temperature[id]))

    # Set the temperature.
    cdp.temperature[id] = temp
