###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Module for manipulating the spectrometer frequency of experiments."""

# relax module imports.
from generic_fns import pipes
from relax_errors import RelaxError


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

    # Alias the current data pipe.
    cdp = pipes.get_pipe()

    # Set up the dictionary data structure if it doesn't exist yet.
    if not hasattr(cdp, 'frq'):
        cdp.frq = {}

    # Test the frequency has not already been set.
    if id in cdp.frq:
        raise RelaxError("The frequency for the experiment " + repr(id) + " has already been set.")

    # Set the frequency.
    cdp.frq[id] = frq

