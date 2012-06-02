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
from copy import deepcopy
from string import split
from textwrap import wrap

# relax module imports.
import ansi
import help
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


def create_table(label, spacing=True):
    """Format and return the table as text.

    @param label:       The unique table label.
    @type label:        str
    @keyword spacing:   A flag which if True will cause empty rows to be placed between elements.
    @type spacing:      bool
    @return:            The formatted table.
    @rtype:             str
    """

    # Get the table.
    table = uf_tables.get_table(label)

    # Initialise some variables.
    text = ''
    num_rows = len(table.cells)
    num_cols = len(table.headings)

    # The column widths.
    widths = []
    for j in range(num_cols):
        widths.append(len(table.headings[j]))
    for i in range(num_rows):
        for j in range(num_cols):
            # The element is larger than the previous.
            if len(table.cells[i][j]) > widths[j]:
                widths[j] = len(table.cells[i][j])

    # The free space for the text.
    used = 0
    used += 2    # Start of the table '| '.
    used += 2    # End of the table ' |'.
    used += 3 * (num_cols - 1)   # Middle of the table ' | '.
    free_space = status.text_width - used

    # The maximal width for all cells.
    free_width = sum(widths)

    # Column wrapping.
    if free_width > free_space:
        # Debugging printouts.
        if status.debug:
            print
            print("Table column wrapping algorithm:")
            print("%-20s %s" % ("num_cols:", num_cols))
            print("%-20s %s" % ("free space:", free_space))

        # New structures.
        new_widths = deepcopy(widths)
        num_cols_wrap = num_cols
        free_space_wrap = free_space
        col_wrap = [True] * num_cols

        # Loop.
        while 1:
            # The average column width.
            ave_width = free_space_wrap / num_cols_wrap

            # Debugging printout.
            if status.debug:
                print("    %-20s %s" % ("ave_width:", ave_width))

            # Rescale.
            rescale = False
            for i in range(num_cols):
                # Remove the column from wrapping if smaller than the average wrapped width.
                if col_wrap[i] and new_widths[i] < ave_width:
                    # Recalculate.
                    free_space_wrap = free_space_wrap - new_widths[i]
                    num_cols_wrap -= 1
                    rescale = True

                    # Remove the column from wrapping.
                    col_wrap[i] = False

                    # Debugging printout.
                    if status.debug:
                        print("        %-20s %s" % ("remove column:", i))

            # Done.
            if not rescale:
                # Set the column widths.
                for i in range(num_cols):
                    if new_widths[i] > ave_width:
                        new_widths[i] = ave_width
                break

        # Debugging printouts.
        if status.debug:
            print("    %-20s %s" % ("widths:", widths))
            print("    %-20s %s" % ("new_widths:", new_widths))
            print("    %-20s %s" % ("num_cols:", num_cols))
            print("    %-20s %s" % ("num_cols_wrap:", num_cols_wrap))
            print("    %-20s %s" % ("free_space:", free_space))
            print("    %-20s %s" % ("free_space_wrap:", free_space_wrap))
            print("    %-20s %s" % ("col_wrap:", col_wrap))

    # No column wrapping.
    else:
        new_widths = widths
        col_wrap = [False] * num_cols

    # The total table width.
    total_width = sum(new_widths) + used

    # The header.
    text += "_" * total_width + "\n"    # Top rule.
    text += table_line(widths=new_widths)    # Blank line.
    text += table_line(text=table.headings, widths=new_widths)    # The headings.
    text += table_line(widths=new_widths, bottom=True)    # Middle rule.

    # The table contents.
    for i in range(num_rows):
        # Column text, with wrapping.
        col_text = [table.cells[i]]
        num_lines = 1
        for j in range(num_cols):
            if col_wrap[j]:
                # Wrap.
                lines = wrap(col_text[0][j], new_widths[j])

                # Count the lines.
                num_lines = len(lines)

                # Replace the column text.
                for k in range(num_lines):
                    # New row of empty text.
                    if len(col_text) <= k:
                        col_text.append(['']*num_cols)

                    # Pack the data.
                    col_text[k][j] = lines[k]

        # Blank line (between rows when asked, and for the first row after the header).
        if spacing or i == 1:
            text += table_line(widths=new_widths)

        # The contents.
        for k in range(num_lines):
            text += table_line(text=col_text[k], widths=new_widths)

    # The bottom.
    text += table_line(widths=new_widths, bottom=True)    # Bottom rule.

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
