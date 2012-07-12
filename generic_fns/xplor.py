###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""Module containing functions for the parsing and creation of Xplor formatted files."""

# Python module imports.
from re import search
from string import split

# relax module imports.
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
            raise RelaxError("Cannot convert the Xplor atom string '%s' to relax format." % string)

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
    @return:        The NOE restraint list in the format of two atom identification strings (or list
                    of str for pseudoatoms) and the lower and upper restraints.
    @rtype:         list of lists of str, str, float, float
    """

    # Strip all comments from the data.
    lines = strip_comments(lines)

    # Init.
    data = []

    # First level pass (assign statements).
    for id1, id2, noe, lower, upper in first_parse(lines):
        # Second parse (pseudoatoms).
        id1 = second_parse(id1)
        id2 = second_parse(id2)

        # Convert to relax spin IDs.
        if isinstance(id1, list):
            relax_id1 = []
            for i in range(len(id1)):
                relax_id1.append(__convert_to_id(id1[i]))
        else:
            relax_id1 = __convert_to_id(id1)

        if isinstance(id2, list):
            relax_id2 = []
            for i in range(len(id2)):
                relax_id2.append(__convert_to_id(id2[i]))
        else:
            relax_id2 = __convert_to_id(id2)

        # Convert to upper and lower bounds.
        lower_bound = noe - lower
        upper_bound = noe + upper

        # Add the data to the list.
        data.append([relax_id1, relax_id2, lower_bound, upper_bound])

    # Return the data.
    return data


def first_parse(lines):
    """Generator function to parse and extract the 2 atom IDs and NOE info from the lines.

    The first parse loops over and returns the data from assign statements, returning pseudo atoms
    as single strings.  The second parse splits the pseudoatoms.

    @param lines:   The Xplor formatted file, or file fragment, split into lines.
    @type lines:    list of str
    @return:        The 2 atom IDs, and NOE info (NOE, upper, and lower bounds).
    @rtype:         str, str, float, float, float
    """

    # Extract the data.
    line_index = 0
    while True:
        # Break out!
        if line_index >= len(lines):
            break

        # Find the assign statements.
        if search('^assign', lines[line_index]):
            # Init.
            char_index = -1

            # Extract the atom ID strings.
            id = ['', '']
            id_index = 0
            inside = 0
            while True:
                # Inc the character index.
                char_index = char_index + 1

                # Break out!
                if line_index >= len(lines):
                    break

                # Check if we need to go to the next line.
                if char_index >= len(lines[line_index]):
                    line_index = line_index + 1
                    char_index = -1
                    continue

                # A starting bracket, so increment the inside counter.
                if lines[line_index][char_index] == '(':
                    inside = inside + 1

                    # Don't include the first bracket in the ID string.
                    if inside == 1:
                        continue

                # Not inside, so jump to the next character.
                if not inside:
                    continue

                # An ending bracket.
                elif lines[line_index][char_index] == ')':
                    inside = inside - 1

                # A logical test (debugging).
                if inside < 0:
                    raise RelaxError("Improperly formatted Xplor file, unmatched ')'.")

                # Append the character.
                if inside:
                    id[id_index] = id[id_index] + lines[line_index][char_index]

                # Go to the second id_index, or break.
                if inside == 0:
                    if id_index == 1:
                        break
                    else:
                        id_index = 1

            # The rest of the data (NOE restraint info).
            info = split(lines[line_index][char_index+1:])

            # NOE dist, lower, upper.
            noe = float(info[0])
            lower = float(info[1])
            upper = float(info[2])

        # Non-data line.
        else:
            # Line index.
            line_index = line_index + 1

            # Skip to the next line without yielding.
            continue

        # Line index.
        line_index = line_index + 1

        # Return the data.
        yield id[0], id[1], noe, lower, upper


def second_parse(id):
    """Split up pseudoatoms.

    @param id:  The Xplor atom id without outer brackets, i.e. a single atom or a list of atoms in
                the case of pseudoatoms.
    @type id:   str
    @return:    For normal atoms, the id string is returned unmodified.  For pseudoatoms, a list of
                strings, with brackets removed, is returned.
    @rtype:     str or list of str
    """

    # Loop over the characters.
    atoms = ['']
    index = -1
    inside = False
    while True:
        # Inc the character index.
        index = index + 1

        # Break out.
        if index >= len(id):
            break

        # A starting bracket, so flip the inside flag.
        if id[index] == '(':
            # 2 brackets?!?
            if inside:
                raise RelaxError("The Xplor pseudoatom ID string '%s' is invalid." % id)

            # The flag.
            inside = True

            # Don't include the first bracket in the ID string.
            continue

        # Not inside, so jump to the next character.
        if not inside:
            continue

        # An ending bracket.
        if id[index] == ')':
            inside = False

        # Append the character.
        if inside:
            atoms[-1] = atoms[-1] + id[index]

        # Add another atom.
        if not inside:
            atoms.append('')

    # Remove the last empty atom string.
    if atoms[0] and atoms[-1] == '':
        atoms = atoms[:-1]

    # Return the data.
    if not atoms[0]:
        return id
    else:
        return atoms


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
