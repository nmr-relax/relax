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
"""Module for manipulating the spectrometer frequency of experiments."""

# Python module imports.
from warnings import warn

# relax module imports.
from generic_fns import pipes
from lib.errors import RelaxError
from relax_warnings import RelaxWarning


def get_values():
    """Return a list of all the current frequencies.

    @return:    The frequency list for the current data pipe.
    @rtype:     list of float
    """

    # No frequency data.
    if not hasattr(cdp, 'frq'):
        return []

    # The frequency values.
    values = cdp.frq.values()

    # Build a list of the unique frequencies.
    frq = []
    for value in values:
        if value not in frq:
            frq.append(value)

    # Return the frqs.
    return frq


def set(id=None, frq=None, units='Hz'):
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

    # Set up the dictionary data structure if it doesn't exist yet.
    if not hasattr(cdp, 'frq'):
        cdp.frq = {}

    # Test the frequency has not already been set.
    if id in cdp.frq and cdp.frq[id] != frq:
        raise RelaxError("The frequency for the experiment '%s' has already been set to %s Hz." % (id, cdp.frq[id]))

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
    cdp.frq[id] = frq * conv

    # Warnings.
    if cdp.frq[id] < 1e8:
        warn(RelaxWarning("The proton frequency of %s Hz appears to be too low." % cdp.frq[id]))
    if cdp.frq[id] > 2e9:
        warn(RelaxWarning("The proton frequency of %s Hz appears to be too high." % cdp.frq[id]))
