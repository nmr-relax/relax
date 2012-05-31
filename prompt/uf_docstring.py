###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""The base class for all the user function classes."""

# Python module imports.
from string import split
from textwrap import wrap

# relax module imports.
import ansi
import help
from relax_string import strip_lead
from status import Status; status = Status()


def bold_text(text):
    """Convert the text to bold.

    This is for use in the help system.

    @param text:    The text to make bold.
    @type text:     str
    @return:        The bold text.
    @rtype:         str
    """

    # Init.
    new_text = ''

    # Add the bold character to all characters.
    for i in range(len(text)):
        new_text += "%s\b%s" % (text[i], text[i])

    # Return the text.
    return new_text


def build_subtitle(text, bold=True):
    """Create the formatted subtitle string.

    @param text:        The name of the subtitle.
    @type text:         str
    @keyword colour:    A flag which if true will return bold text.  Otherwise an underlined title will be returned.
    @type colour:       bool
    @return:            The formatted subtitle.
    @rtype:             str
    """

    # Bold.
    if bold:
        new = "\n%s\n\n" % bold_text(text)

    # Underline.
    else:
        new = "\n%s\n%s\n\n" % (text, "~"*len(text))

    # Return the subtitle.
    return new


def create_table(table):
    """Format and return the table as text.

    @param table:   The table data.
    @type table:    list of lists of str
    @return:        The formatted table.
    @rtype:         str
    """

    # Initialise some variables.
    text = ''
    num_rows = len(table)
    num_cols = len(table[0])

    # The column widths.
    widths = [0] * num_cols
    for i in range(len(table)):
        for j in range(num_cols):
            # The element is larger than the previous.
            if len(table[i][j]) > widths[j]:
                widths[j] = len(table[i][j])

    # The free space for the text.
    used = 0
    used += 2    # Start of the table '| '.
    used += 2    # End of the table ' |'.
    used += 3 * (num_cols - 1)   # Middle of the table ' | '.
    free_space = status.text_width - used

    # The total table width.
    total_width = sum(widths)

    # The header.
    text += "_" * (total_width+used) + "\n"    # Top rule.
    text += table_line(widths=widths)    # Blank line.
    text += table_line(text=table[0], widths=widths)    # The headers.
    text += table_line(widths=widths, bottom=True)    # Middle rule.

    # The table contents.
    for i in range(1, num_rows):
        text += table_line(widths=widths)    # Blank line.
        text += table_line(text=table[i], widths=widths)    # The contents.

    # The bottom.
    text += table_line(widths=widths, bottom=True)    # Bottom rule.

    # Add a newline.
    text += '\n'

    # Return the table text.
    return text


def format_text(text):
    """Format the line of text by wrapping.

    @param text:    The line of text to wrap.
    @type text:     str
    @return:        The wrapped text.
    @rtype:         str
    """

    # Then wrap each line.
    new_text = ""

    # Wrap the line.
    for wrapped_line in wrap(text, status.text_width):
        new_text += wrapped_line + "\n"

    # Return the formatted text.
    return new_text


def table_line(text=None, widths=None, bottom=False):
    """Format a line of a table.

    @keyword text:      The list of table elements.  If not given, an empty line will be be produced.
    @type text:         list of str or None
    @keyword widths:    The list of column widths for the table.
    @type widths:       list of int
    @keyword botton:    A flag which if True will cause a table bottom line to be produced.
    @type bottom:       bool
    @return:            The table line.
    @rtype:             str
    """

    # Initialise.
    if bottom:
        line = "|_"
    else:
        line = "| "

    # Loop over the columns.
    for i in range(len(widths)):
        # The column separator.
        if i > 0:
            if bottom:
                line += "_|_"
            else:
                line += " | "

        # A bottom line.
        if bottom:
            line += "_" * widths[i]

        # Empty line.
        elif text == None:
            line += " " * widths[i]

        # The text.
        else:
            line += text[i]
            line += " " * (widths[i] - len(text[i]))

    # Close the line.
    if bottom:
        line += "_|\n"
    else:
        line += " |\n"

    # Return the text.
    return line
