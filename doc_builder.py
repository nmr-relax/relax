###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Module for building documentation."""


# Some constants.
TITLE = 3
SECTION = 2
SUBSECTION = 1
PARAGRAPH = 0
LIST = 10


def to_docstring(data):
    """Convert the text to that of a docstring, dependent on the text level.

    @param data:    The lists of constants and text to convert into a properly formatted docstring.
    @type text:     list of lists of int and str
    """

    # Init.
    doc = ''
    for i in range(len(data)):
        # The level and text.
        level, text = data[i]

        # Title level.
        if level == TITLE:
            doc += text + '\n\n'

        # Section level.
        if level == SECTION:
            doc += '\n\n' + text + '\n' + '='*len(text) + '\n\n'

        # Subsection level.
        if level == SUBSECTION:
            doc += '\n\n' + text + '\n' + '-'*len(text) + '\n\n'

        # Paragraph level.
        elif level == PARAGRAPH:
            # Starting newline.
            if i and data[i-1][0] == PARAGRAPH:
                doc += '\n'

            # The text.
            doc += text + '\n'

        # List level.
        elif level == LIST:
            # Start of list.
            if i and data[i-1][0] != LIST:
                doc += '\n'

            # The text.
            doc += "    - %s\n" % text

            # End of list.
            if i < len(data) and data[i+1][0] == PARAGRAPH:
                doc += '\n'
 
    # Return the docstring.
    return doc
