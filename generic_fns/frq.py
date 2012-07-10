###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for manipulating the spectrometer frequency of experiments."""

# relax module imports.
from generic_fns import pipes
from relax_errors import RelaxError


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


def set(id=None, frq=None):
    """Set the spectrometer frequency of the experiment.

    @keyword id:    The experimental identification string (allowing for multiple experiments per
                    data pipe).
    @type id:       str
    @keyword frq:   The spectrometer frequency in Hertz.
    @type frq:      float
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Set up the dictionary data structure if it doesn't exist yet.
    if not hasattr(cdp, 'frq'):
        cdp.frq = {}

    # Test the frequency has not already been set.
    if id in cdp.frq:
        raise RelaxError("The frequency for the experiment " + repr(id) + " has already been set.")

    # Set the frequency.
    cdp.frq[id] = frq

