###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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

# Python module imports.
from re import search
from string import split

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin
from generic_fns.xplor import parse_noe_restraints
from relax_errors import RelaxError, RelaxNoSequenceError
from relax_io import open_read_file


def __file_format(lines):
    """Determine the format of the NOE restraints data.

    @param lines:   The file data converted to a list of file lines.
    @type lines:    list of str
    @return:        The format of the file.
    @rtype:         str
    """

    # Loop over the lines.
    for line in lines:
        # Xplor format.
        if search('^assign ', line):
            print "Xplor formatted file."
            return 'xplor'

    # Print out.
    print "Generic formatted file."
    return 'generic'


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

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Open the file.
    file = open_read_file(file_name=file, dir=dir)
    lines = file.readlines()
    file.close()

    # Determine the file type.
    format = __file_format(lines)

    # Generic format checks.
    if format == 'generic':
        # Columns must be specified.
        if proton1_col == None:
            raise RelaxError, "The proton1_col argument must be specified for the generically formatted NOE restraint file."
        if proton2_col == None:
            raise RelaxError, "The proton2_col argument must be specified for the generically formatted NOE restraint file."
        if lower_col == None:
            raise RelaxError, "The lower_col argument must be specified for the generically formatted NOE restraint file."
        if upper_col == None:
            raise RelaxError, "The upper_col argument must be specified for the generically formatted NOE restraint file."

    # Parse and extract the NOE restraints.
    if format == 'xplor':
        cdp.noe_restraints = parse_noe_restraints(lines)

    # Check for the presence of the spin containers corresponding to the atom ids.
    for restraint in cdp.noe_restraints:
        if not return_spin(restraint[0]):
            raise RelaxError, "The spin container corresponding to '%s' cannot be found." % restraint[0]
        if not return_spin(restraint[1]):
            raise RelaxError, "The spin container corresponding to '%s' cannot be found." % restraint[1]
