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
"""Module for the creation and parsing of an XML representation of a data pipe."""

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


def read(file, verbosity=1):
    """Parse a XML document representation of a data pipe, and load it into the relax data store.

    @param file:        The open file object.
    @type file:         file
    @keyword verbosity: A flag specifying the amount of information to print.  The higher the value,
                        the greater the verbosity.
    @type verbosity:    int
    """


def write(file):
    """Create a XML document representation of the current data pipe.

    @param file:        The open file object.
    @type file:         file
    """
