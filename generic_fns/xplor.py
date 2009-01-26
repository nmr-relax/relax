###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""Module containing functions for the parsing and creation of Xplor formatted files."""

# Python module imports.
from re import search
from string import split

# relax module imports.
from generic_fns.mol_res_spin import return_spin
from relax_errors import RelaxError


def __convert_to_id(string):
    """Convert the string into a relax atom id representation.

    @param string:  The Xplor atom string.
    @type string:   str
    @return:        The relax atom id.
    @rtype:         str
    """

    # Split up the string by the 'and' statements.
    data = split(string, 'and')

    # Loop over the data.
    relax_id = ''
    for i in range(len(data)):
        # Split by whitespace.
        info = split(data[i])

        # Don't know what this is!
        if len(info) != 2:
            raise RelaxError, "Cannot convert the Xplor atom string '%s' to relax format." % string

        # A molecule identifier.
        if info[0] == 'segid':
            relax_id = relax_id + '#' + info[1]

        # A residue identifier.
        elif info[0] == 'resid':
            relax_id = relax_id + ':' + info[1]

        # An atom identifier.
        elif info[0] == 'name':
            relax_id = relax_id + '@' + info[1]

    # Return the relax id.
    return relax_id


def parse_noe_restraints(lines):
    """Parse and return the NOE restraints from the Xplor lines.

    @param lines:   The Xplor formatted file, or file fragment, split into lines.
    @type lines:    list of str
    @return:        The NOE restraint list in the format of two atom identification strings and the
                    lower and upper restraints.
    @rtype:         list of lists of [str, str, float, float]
    """

    # Strip all comments from the data.
    lines = strip_comments(lines)

    # Extract the data.
    data = []
    line_index = 0
    while 1:
        # Break out!
        if line_index >= len(lines):
            break

        # Find the starting assign.
        if search('^assign', lines[line_index]):
            # Add a new data line.
            data.append([None, None, None, None])

            # Init.
            char_index = -1

            # Extract the first atom string.
            atom = ''
            inside = False
            while 1:
                # Inc the character index.
                char_index = char_index + 1

                # Start.
                if not inside:
                    if lines[line_index][char_index] == '(':
                        inside = True
                    continue

                # End.
                if inside and lines[line_index][char_index] == ')':
                    break

                # Append the character.
                atom = atom + lines[line_index][char_index]

            # Convert the atom data to a relax atom id.
            relax_id = __convert_to_id(atom)
            data[-1][0] = relax_id
            if not return_spin(relax_id):
                raise RelaxError, "The spin container corresponding to '%s' (or '%s' in Xplor format) cannot be found." % (relax_id, atom)

            # Extract the second atom string.
            atom = ''
            inside = False
            while 1:
                # Inc the character index.
                char_index = char_index + 1

                # Check if we need to go to the next line.
                if char_index > len(lines[line_index]):
                    line_index = line_index + 1
                    char_index = -1
                    continue

                # Start.
                if not inside:
                    if lines[line_index][char_index] == '(':
                        inside = True
                    continue

                # End.
                if inside and lines[line_index][char_index] == ')':
                    break

                # Append the character.
                atom = atom + lines[line_index][char_index]

            # Convert the atom data to a relax atom id.
            relax_id = __convert_to_id(atom)
            data[-1][1] = relax_id
            if not return_spin(relax_id):
                raise RelaxError, "The spin container corresponding to '%s' (or '%s' in Xplor format) cannot be found." % (relax_id, atom)

            # The rest of the data (NOE restraint info).
            info = split(lines[line_index][char_index+1:])

            # NOE dist, lower, upper.
            noe = float(info[0])
            lower = float(info[1])
            upper = float(info[2])

            # Convert to upper and lower bounds.
            data[-1][2] = noe - lower
            data[-1][3] = noe + upper

        # Line index.
        line_index = line_index + 1

    # Return the data.
    return data


def strip_comments(lines):
    """Remove all Xplor comments from the data.

    @param lines:   The Xplor formatted file, or file fragment, split into lines.
    @type lines:    list of str
    @return:        The file data with all comments removed.
    @rtype:         list of str
    """

    # Loop over the lines.
    new_lines = []
    for line in lines:
        # Comment lines.
        if search('^!', line):
            continue

        # Partial comment lines.
        new_line = ''
        for char in line:
            # Comment - so skip the rest of the line.
            if char == '!':
                continue

            # Build the new line.
            new_line = new_line + char

        # Add the new line.
        new_lines.append(new_line)

    # Return the stripped data.
    return new_lines
