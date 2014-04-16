###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""Module for all of the steady-state heteronuclear NOE specific user functions."""

# relax module imports.
from lib.errors import RelaxError
from pipe_control import pipes


def spectrum_type(spectrum_type=None, spectrum_id=None):
    """Set the spectrum type corresponding to the spectrum_id.

    @keyword spectrum_type: The type of NOE spectrum, one of 'ref' or 'sat'.
    @type spectrum_type:    str
    @keyword spectrum_id:   The spectrum id string.
    @type spectrum_id:      str
    """

    # Test if the current pipe exists
    pipes.test()

    # Test the spectrum id string.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxError("The peak intensities corresponding to the spectrum id '%s' does not exist." % spectrum_id)

    # Initialise or update the spectrum_type data structure as necessary.
    if not hasattr(cdp, 'spectrum_type'):
        cdp.spectrum_type = {}

    # Set the error.
    cdp.spectrum_type[spectrum_id] = spectrum_type
