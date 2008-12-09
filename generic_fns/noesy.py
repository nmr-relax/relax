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
"""Module for NOESY related operations."""

# relax module imports.
from generic_fns import pipes


def read_restraints(file=None, dir=None, proton1_col=None, proton2_col=None, lower_col=None, upper_col=None, sep=None):
    """Load NOESY or ROESY constraint information from file.

    If the input file is a pre-formatted Xplor file, the column number and separator arguments will
    be ignored.


    @keyword file:          The name of the file containing the relaxation data.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              None or str
    @keyword proton1_col:   The column containing the first proton of the NOE or ROE cross peak.
    @type proton1_col:      None or int
    @keyword proton2_col:   The column containing the second proton of the NOE or ROE cross peak.
    @type proton2_col:      None or int
    @keyword lower_col:     The column containing the lower NOE bound.
    @type lower_col:        None or int
    @keyword upper_col:     The column containing the upper NOE bound.
    @type upper_col:        None or int
    @keyword sep:           The column separator (the default is white space).
    @type sep:              None or str
    """

    # Test if the current data pipe exists.
    pipes.test()


