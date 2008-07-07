###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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
"""Module implementing relax regular expression."""

# Python module imports.
from re import search
from string import replace


def search(id, patterns):
    """Determine if id is in the list of patterns, or vice versa, allowing for regular expressions.

    This method converts from relax's RE syntax to that of the re python module.

    The changes include:

        1.  All '*' to '.*'.
        2.  The identifier is bracketed, '^' is added to the start and '$' to the end.

    After conversion of both the id and patterns, the comparison is then performed both ways from
    the converted string matching the original string (using re.search()).


    @param id:          The identification object.
    @type id:           None, str, or number
    @param patterns:    A list of patterns to match.  The elements will be converted to strings,
                        so the list can consist of anything.
    @type patterns:     list
    @return:            True if there is a match, False otherwise.
    @rtype:             bool
    """

    # Catch None.
    if id == None:
        return False

    # If a number, convert to a string.
    if type(id) == int or type(id) == float:
        id = str(id)

    # Loop over the patterns.
    for pattern in patterns:
        # Force a conversion to str.
        pattern = str(pattern)

        # First replace any '*' with '.*' (relax to re conversion).
        pattern_re = replace(pattern, '*', '.*')
        id_re =      replace(id,      '*', '.*')

        # Bracket the pattern.
        pattern_re = '^' + pattern_re + '$'
        id_re = '^' + id_re + '$'

        # String matches (both ways).
        if search(pattern_re, id):
            return True
        if search(id_re, pattern):
            return True

    # No matches.
    return False
