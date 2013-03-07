###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
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
"""The base class for all the user function classes."""

# Python module imports.
from copy import deepcopy
from textwrap import wrap

# relax module imports.
import ansi
import prompt.help
from lib.text.table import format_table
from relax_string import strip_lead
from status import Status; status = Status()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()


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


def build_subtitle(text, bold=True, start_nl=True):
    """Create the formatted subtitle string.

    @param text:        The name of the subtitle.
    @type text:         str
    @keyword bold:      A flag which if true will return bold text.  Otherwise an underlined title will be returned.
    @type bold:         bool
    @keyword start_nl:  A flag which if True will add a newline to the start of the text.
    @type start_nl:     bool
    @return:            The formatted subtitle.
    @rtype:             str
    """

    # Starting newline.
    if start_nl:
        new = "\n"
    else:
        new = ""

    # Bold.
    if bold:
        new += "%s\n\n" % bold_text(text)

    # Underline.
    else:
        new += "%s\n%s\n\n" % (text, "~"*len(text))

    # Return the subtitle.
    return new


def create_table(label):
    """Format and return the table as text.

    @param label:       The unique table label.
    @type label:        str
    @return:            The formatted table.
    @rtype:             str
    """

    # Get the table.
    table = uf_tables.get_table(label)

    # Initialise some variables.
    text = ''
    num_rows = len(table.cells)
    num_cols = len(table.headings)

    # Generate and return the table.
    return format_table(headings=[table.headings], contents=table.cells, max_width=status.text_width, debug=status.debug)


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
        line = " _"
    else:
        line = "  "

    # Loop over the columns.
    for i in range(len(widths)):
        # The column separator.
        if i > 0:
            if bottom:
                line += "___"
            else:
                line += "   "

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
        line += "_ \n"
    else:
        line += "  \n"

    # Return the text.
    return line
