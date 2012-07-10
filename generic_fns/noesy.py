###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
"""Module for NOESY related operations."""

# Python module imports.
from re import search
from string import split
from warnings import warn

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, tokenise
from generic_fns import xplor
from relax_errors import RelaxError, RelaxNoSequenceError
from relax_io import open_read_file
from relax_warnings import RelaxWarning


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
            print("Xplor formatted file.")
            return 'xplor'

    # Print out.
    print("Generic formatted file.")
    return 'generic'


def parse_noe_restraints(lines, proton1_col=None, proton2_col=None, lower_col=None, upper_col=None, sep=None):
    """Parse and return the NOE restraints from the generic formatted file.

    @param lines:           The file, or file fragment, split into lines.
    @type lines:            list of str
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
    @return:                The NOE restraint list in the format of two atom identification strings
                            and the lower and upper restraints.
    @rtype:                 list of lists of [str, str, float, float]
    """

    # Default column numbers.
    if proton1_col == None:
        warn(RelaxWarning("The proton1_col argument has not been supplied, defaulting to column 1."))
        proton1_col = 1
    if proton2_col == None:
        warn(RelaxWarning("The proton2_col argument has not been supplied, defaulting to column 2."))
        proton2_col = 2
    if lower_col == None:
        warn(RelaxWarning("The lower_col argument has not been supplied, defaulting to column 3."))
        lower_col = 3
    if upper_col == None:
        warn(RelaxWarning("The upper_col argument has not been supplied, defaulting to column 4."))
        upper_col = 4

    # Loop over the lines.
    data = []
    for line in lines:
        # Split the line.
        row = split(line, sep)

        # Header lines:
        if len(row) < 4:
            continue
        try:
            tokenise(row[proton1_col-1])
        except RelaxError:
            continue

        # Pack the data.
        data.append([row[proton1_col-1], row[proton2_col-1], float(row[lower_col-1]), float(row[upper_col-1])])

    # Return the data.
    return data


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

    # Open the file.
    file = open_read_file(file_name=file, dir=dir)
    lines = file.readlines()
    file.close()

    # Determine the file type.
    format = __file_format(lines)

    # Parse and extract the NOE restraints.
    if format == 'xplor':
        noe_restraints = xplor.parse_noe_restraints(lines)
    elif format == 'generic':
        noe_restraints = parse_noe_restraints(lines, proton1_col=proton1_col, proton2_col=proton2_col, lower_col=lower_col, upper_col=upper_col, sep=sep)

    # Pseudoatom conversion.
    for i in range(len(noe_restraints)):
        # Loop over atom IDs.
        for j in range(2):
            # Skip normal atoms.
            if isinstance(noe_restraints[i][j], str):
                continue

            # Loop over the pseudoatoms.
            pseudo_name = None
            for k in range(len(noe_restraints[i][j])):
                # Get the spin.
                spin = return_spin(noe_restraints[i][j][k])

                # Check the pseudoatom consistency.
                if pseudo_name and pseudo_name != spin.pseudo_name:
                    raise RelaxError("The pseudoatom names '%s' and '%s' do not match." % (pseudo_name, spin.pseudo_name))

                # Set the name.
                pseudo_name = spin.pseudo_name

            # No pseudoatom.
            if not pseudo_name:
                raise RelaxError("Cannot find the pseudoatom corresponding to the atoms in %s." % noe_restraints[i][j])

            # Otherwise, place the pseudoatom name into the NOE restraint list.
            noe_restraints[i][j] = pseudo_name

    # Place the restraints into the current data pipe.
    cdp.noe_restraints = noe_restraints

    # Check for the presence of the spin containers corresponding to the atom ids.
    for restraint in cdp.noe_restraints:
        if not return_spin(restraint[0]):
            raise RelaxError("The spin container corresponding to '%s' cannot be found." % restraint[0])
        if not return_spin(restraint[1]):
            raise RelaxError("The spin container corresponding to '%s' cannot be found." % restraint[1])
