###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
import re
from string import replace


def search(pattern, id):
    """Determine if id matches the pattern, or vice versa, allowing for regular expressions.

    This method converts from relax's RE syntax to that of the re python module.

    The changes include:

        1.  All '*' to '.*'.
        2.  The identifier is bracketed, '^' is added to the start and '$' to the end.

    After conversion of both the string and patterns, the comparison is then performed both ways from the converted string matching the original string (using re.search()).


    @param pattern:     The pattern to match the string to.  This can be a list of patterns.  All elements will be converted to strings, so the pattern or list can consist of anything.
    @type pattern:      anything
    @param id:          The identification object.
    @type id:           None, str, or number
    @return:            True if there is a match, False otherwise.
    @rtype:             bool
    """

    # Catch None.
    if id == None:
        return False

    # Convert to a string.
    id = str(id)

    # If pattern is not a list, convert it to one.
    if not isinstance(pattern, list):
        patterns = [pattern]
    else:
        patterns = pattern

    # Loop over the patterns.
    for pattern in patterns:
        # Force a conversion to str.
        pattern = str(pattern)

        # First replace any '*' with '.*' (relax to re conversion).
        pattern_re = replace(pattern, '*', '.*')
        id_re =      replace(id,      '*', '.*')

        # Bracket the pattern.
        pattern_re = '^%s$' % pattern_re
        id_re = '^%s$' % id_re

        # String matches (both ways).
        if re.search(pattern_re, id):
            return True
        if re.search(id_re, pattern):
            return True

    # No matches.
    return False
