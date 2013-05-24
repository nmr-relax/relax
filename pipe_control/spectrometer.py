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
from math import modf, pi
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoFrqError
from lib.physical_constants import g1H
from lib.warnings import RelaxWarning
from pipe_control import pipes


def copy_frequencies(pipe_from=None, pipe_to=None, id=None):
    """Copy the frequency information from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the frequency information from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the frequency information to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param id:          The experiment ID string.
    @type id:           str
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Test if the pipe_from and pipe_to data pipes exist.
    pipes.test(pipe_from)
    pipes.test(pipe_to)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test if the pipe_from pipe has frequency data.
    if not hasattr(dp_from, 'spectrometer_frq'):
        raise RelaxNoFrqError(pipe_from)
    elif id not in dp_from.spectrometer_frq:
        raise RelaxNoFrqError(pipe_from, id=id)

    # Set up the data structures if missing.
    if not hasattr(dp_to, 'spectrometer_frq'):
        dp_to.spectrometer_frq = {}
        dp_to.spectrometer_frq_list = []
        dp_to.spectrometer_frq_count = 0

    # Copy the frequency.
    dp_to.spectrometer_frq[id] = dp_from.spectrometer_frq[id]

    # New frequency.
    if dp_to.spectrometer_frq[id] not in dp_to.spectrometer_frq_list:
        dp_to.spectrometer_frq_list.append(dp_to.spectrometer_frq[id])
        dp_to.spectrometer_frq_count += 1


def delete_frequencies(id=None):
    """Delete the spectrometer frequency corresponding to the experiment ID.

    @keyword id:    The experiment ID string.
    @type id:       str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if data exists.
    if not hasattr(cdp, 'spectrometer_frq') or id not in cdp.spectrometer_frq:
        raise RelaxNoFrqError(id)

    # Delete the frequency.
    frq = cdp.spectrometer_frq[id]
    del cdp.spectrometer_frq[id]

    # Update the structures as needed.
    if frq in cdp.spectrometer_frq_list and frq not in cdp.spectrometer_frq.values():
        cdp.spectrometer_frq_list.pop(cdp.spectrometer_frq_list.index(frq))
    cdp.spectrometer_frq_count = len(cdp.spectrometer_frq_list)

    # Cleanup.
    if len(cdp.spectrometer_frq) == 0:
        del cdp.spectrometer_frq
        del cdp.spectrometer_frq_list
        del cdp.spectrometer_frq_count


def frequency_checks(frq):
    """Perform a number of checks on the given proton frequency.

    @param frq:     The proton frequency value in Hertz.
    @type frq:      float or None
    """

    # No frequency given.
    if frq == None:
        return

    # Make sure the precise value has been supplied.
    frac, integer = modf(frq / 1e6)
    if frac == 0.0 or frac > 0.99999:
        warn(RelaxWarning("The precise spectrometer frequency should be suppled, a value such as 500000000 or 5e8 for a 500 MHz machine is not acceptable.  Please see the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file."))

    # Check that the frequency value is reasonable.
    if frq < 1e8:
        warn(RelaxWarning("The proton frequency of %s Hz appears to be too low." % frq))
    if frq > 2e9:
        warn(RelaxWarning("The proton frequency of %s Hz appears to be too high." % frq))


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
        elif units == 'T':
            frq.append(value * 2.0 * pi / g1H)

        # Unknown units.
        else:
            raise RelaxError("The units of '%s' should be one of 'Hz', 'MHz', or 'T'.")

    # Return the frqs.
    return frq


def loop_frequencies():
    """Generator function for looping over the spectrometer frequencies.

    @return:    The frequency.
    @rtype:     float
    """

    # Loop over the frequencies.
    for frq in cdp.spectrometer_frq_list:
        yield frq


def set_frequency(id=None, frq=None, units='Hz'):
    """Set the spectrometer frequency of the experiment.

    @keyword id:    The experiment ID string (allowing for multiple experiments per data pipe).
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

    # Some checks.
    frequency_checks(cdp.spectrometer_frq[id])

    # New frequency.
    if cdp.spectrometer_frq[id] not in cdp.spectrometer_frq_list:
        cdp.spectrometer_frq_list.append(cdp.spectrometer_frq[id])
        cdp.spectrometer_frq_count += 1


def set_temperature(id=None, temp=None):
    """Set the experimental temperature.

    @keyword id:    The experiment ID string (allowing for multiple experiments per data pipe).
    @type id:       str
    @keyword temp:  The temperature in Kelvin.
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
