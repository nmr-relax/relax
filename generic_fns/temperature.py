###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
"""Module for setting the experimental temperature."""

# relax module imports.
from generic_fns import pipes
from relax_errors import RelaxError


def set(id=None, temp=None):
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
