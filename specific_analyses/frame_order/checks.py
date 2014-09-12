###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for checks for the frame order analysis."""

# relax module imports.
from lib.errors import RelaxError
from pipe_control.pipes import cdp_name, get_pipe


def check_pivot(pipe_name=None):
    """Check that the pivot point has been set.

    @keyword pipe_name: The data pipe to check the pivot for.  This defaults to the current data pipe if not set.
    @type pipe_name:    str
    @raises RelaxError: If the pivot point has not been set.
    """

    # The data pipe.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Check for the pivot_x parameter.
    if not hasattr(dp, 'pivot_x'):
        raise RelaxError("The pivot point has not been set, please use the frame_order.pivot user function to define the point.")


