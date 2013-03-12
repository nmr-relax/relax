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
"""Functions for the text formatting of tables."""

# Python module imports.
from copy import deepcopy
from textwrap import wrap

# relax module imports.
from check_types import is_float
from relax_errors import RelaxError


# Special variables.
MULTI_COL = "@@MULTI@@"


def _blank(width=None, prefix=' ', postfix=' '):
    """Create a blank line for the table.

    @keyword width:     The total width of the table.
    @type width:        int
    @keyword prefix:    The text to add to the start of the line.
    @type prefix:       str
    @keyword postfix:   The text to add to the end of the line.
    @type postfix:      str
    @return:            The rule.
    @rtype:             str
    """

    # Return the blank line.
    return prefix + ' '*width + postfix + "\n"


def _convert_to_string(data=None, justification=None, custom_format=None):
    """Convert all elements of the given data structures to strings in place.

    @keyword data:          The headings or content to convert.
    @type data:             list of lists
    @keyword justification: The structure to store the cell justification in.
    @type justification:    list of lists
    @keyword custom_format: This list allows a custom format to be specified for each column.  The number of elements must match the number of columns.  If an element is None, then the default will be used.  Otherwise the elements must be valid string formatting constructs.
    @type custom_format:    None or list of None and str
    """

    # Loop over the rows.
    for i in range(len(data)):
        # Loop over the columns.
        for j in range(len(data[i])):
            # Skip multi-columns.
            if data[i][j] == MULTI_COL:
                continue

            # Default left justification.
            justification[i][j] = 'l'

            # Right justify numbers.
            if not isinstance(data[i][j], bool) and (isinstance(data[i][j], int) or is_float(data[i][j])):
                justification[i][j] = 'r'

            # None types.
            if data[i][j] == None:
                data[i][j] = ''

            # Custom format (defaulting to standard string conversion if all fails).
            elif custom_format and custom_format[j]:
                try:
                    data[i][j] = custom_format[j] % data[i][j]
                except TypeError:
                    data[i][j] = "%s" % data[i][j]

            # Bool types.
            elif isinstance(data[i][j], bool):
                data[i][j] = "%s" % data[i][j]

            # Int types.
            elif isinstance(data[i][j], int):
                data[i][j] = "%i" % data[i][j]

            # Float types.
            elif is_float(data[i][j]):
                data[i][j] = "%g" % data[i][j]

            # All other non-string types.
            elif not isinstance(data[i][j], str):
                data[i][j] = "%s" % data[i][j]


def _determine_widths(data=None, widths=None, separator=None):
    """Determine the maximum column widths needed given the data.

    @keyword data:      Either the headings or content converted to strings to check the widths of.
    @type data:         list of lists of str
    @keyword widths:    The list of widths to start with.  If data is found to be wider than this list, then the width of that column will be expanded.
    @type widths:       list of int
    @keyword separator: The column separation string.
    @type separator:    str
    """

    # The number of rows and columns.
    num_rows = len(data)
    num_cols = len(data[0])

    # Determine the maximum column widths.
    multi_col = False
    for i in range(num_rows):
        for j in range(num_cols):
            # Switch the flag.
            if data[i][j] == MULTI_COL:
                multi_col = True

            # Skip multicolumn entries.
            if data[i][j] == MULTI_COL or (j < num_cols-1 and data[i][j+1] == MULTI_COL):
                continue

            # The element is larger than the previous.
            if len(data[i][j]) > widths[j]:
                widths[j] = len(data[i][j])

    # Handle overfull multi-column cells.
    if multi_col:
        for i in range(num_rows):
            for j in range(num_cols):
                # End of multicolumn cell.
                if data[i][j] == MULTI_COL and (j == num_cols-1 or (j < num_cols-1 and data[i][j+1] != MULTI_COL)):
                    col_sum_width = widths[j]
                    while True:
                        # Walk back.
                        for k in range(j-1, -1, -1):
                            col_sum_width += len(separator) + widths[k]

                            # Out of the cell.
                            if data[i][k] != MULTI_COL:
                                break

                        # Nothing more to do.
                        break

                    # The multicolumn width.
                    multi_col_width = len(data[i][k])

                    # The multicolumn cell is wider than the columns it spans, so expand the last column.
                    if multi_col_width > col_sum_width:
                        widths[j] += multi_col_width - col_sum_width


def _rule(width=None, prefix=' ', postfix=' '):
    """Create a horizontal rule for the table.

    @keyword width:     The total width of the table.
    @type width:        int
    @keyword prefix:    The text to add to the start of the line.
    @type prefix:       str
    @keyword postfix:   The text to add to the end of the line.
    @type postfix:      str
    @return:            The rule.
    @rtype:             str
    """

    # Return the rule.
    return prefix + '_'*width + postfix + "\n"


def _table_line(text=None, widths=None, separator='   ', pad_left=' ', pad_right=' ', prefix=' ', postfix=' ', justification=None):
    """Format a line of a table.

    @keyword text:          The list of table elements.  If not given, an empty line will be be produced.
    @type text:             list of str or None
    @keyword widths:        The list of column widths for the table.
    @type widths:           list of int
    @keyword separator:     The column separation string.
    @type separator:        str
    @keyword pad_left:      The string to pad the left side of the table with.
    @type pad_left:         str
    @keyword pad_right:     The string to pad the right side of the table with.
    @type pad_right:        str
    @keyword prefix:        The text to add to the start of the line.
    @type prefix:           str
    @keyword postfix:       The text to add to the end of the line.
    @type postfix:          str
    @keyword justification: The cell justification structure.  The elements should be 'l' for left justification and 'r' for right.
    @type justification:    list of str
    @return:                The table line.
    @rtype:                 str
    """

    # Initialise.
    line = prefix + pad_left
    num_col = len(widths)

    # Loop over the columns.
    for i in range(num_col):
        # Multicolumn (middle/end).
        if text[i] == MULTI_COL:
            continue

        # The column separator.
        if i > 0:
            line += separator

        # Multicolumn (start).
        if i < num_col-1 and text[i+1] == MULTI_COL:
            # Find the full multicell width.
            width = widths[i]
            for j in range(i+1, num_col):
                if text[j] == MULTI_COL:
                    width += len(separator) + widths[j]
                else:
                    break

            # Add the padded text.
            if justification[i] == 'l':
                line += text[i]
            line += " " * (width - len(text[i]))
            if justification[i] == 'r':
                line += text[i]

        # Normal cell.
        else:
            if justification[i] == 'l':
                line += text[i]
            line += " " * (widths[i] - len(text[i]))
            if justification[i] == 'r':
                line += text[i]

    # Close the line.
    line += pad_right + postfix + "\n"

    # Return the text.
    return line


def format_table(headings=None, contents=None, max_width=None, separator='   ', pad_left=' ', pad_right=' ', prefix=' ', postfix=' ', custom_format=None, spacing=False, debug=False):
    """Format and return the table as text.

    If the heading or contents contains the value of the MULTI_COL constant defined in this module, then that cell will be merged with the previous cell to allow elements to span multiple columns.


    @keyword headings:      The table header.
    @type headings:         list of lists of str
    @keyword contents:      The table contents.
    @type contents:         list of lists of str
    @keyword max_width:     The maximum width of the table.
    @type max_width:        int
    @keyword separator:     The column separation string.
    @type separator:        str
    @keyword pad_left:      The string to pad the left side of the table with.
    @type pad_left:         str
    @keyword pad_right:     The string to pad the right side of the table with.
    @type pad_right:        str
    @keyword prefix:        The text to add to the start of the line.
    @type prefix:           str
    @keyword postfix:       The text to add to the end of the line.
    @type postfix:          str
    @keyword custom_format: This list allows a custom format to be specified for each column.  The number of elements must match the number of columns.  If an element is None, then the default will be used.  Otherwise the elements must be valid string formatting constructs.
    @type custom_format:    None or list of None and str
    @keyword spacing:       A flag which if True will add blank line between each row.
    @type spacing:          bool
    @keyword debug:         A flag which if True will activate a number of debugging printouts.
    @type debug:            bool
    @return:                The formatted table.
    @rtype:                 str
    """

    # Initialise some variables.
    text = ''
    num_rows = len(contents)
    num_cols = len(contents[0])
    if headings != None:
        num_head_rows = len(headings)

    # Column number checks.
    if custom_format != None and len(custom_format) != num_cols:
        raise RelaxError("The number of columns is %s but the number of elements in custom_format is %s." % (num_cols, len(custom_format)))
    if headings != None:
        for i in range(num_head_rows):
            if len(headings[i]) != num_cols:
                raise RelaxError("The %s columns does not match the %s elements in the heading row %s." % (num_cols, len(headings[i]), headings[i]))
    for i in range(num_rows):
        if len(contents[i]) != num_cols:
            raise RelaxError("The %s columns does not match the %s elements in the contents row %s." % (num_cols, len(contents[i]), contents[i]))


    # Deepcopy so that modifications to the data are not seen.
    if headings != None:
        headings = deepcopy(headings)
    contents = deepcopy(contents)

    # Create data structures for specifying the cell justification.
    if headings != None:
        justification_headings = deepcopy(headings)
    justification_contents = deepcopy(contents)

    # Convert all data to strings.
    if headings != None:
        _convert_to_string(data=headings, justification=justification_headings, custom_format=custom_format)
    _convert_to_string(data=contents, justification=justification_contents, custom_format=custom_format)

    # Determine the pre-wrapping column widths.
    prewrap_widths = [0] * num_cols
    if headings != None:
        data = headings + contents
    else:
        data = contents
    _determine_widths(data=data, widths=prewrap_widths, separator=separator)

    # The free space for the text (subtracting the space used for the formatting).
    used = len(pad_left)
    used += len(pad_right)
    used += len(separator) * (num_cols - 1)
    if max_width:
        free_space = max_width - used
    else:
        free_space = 1000

    # The maximal width for all cells.
    free_width = sum(prewrap_widths)

    # Column wrapping.
    if free_width > free_space:
        # Debugging printouts.
        if debug:
            print
            print("Table column wrapping algorithm:")
            print("%-20s %s" % ("num_cols:", num_cols))
            print("%-20s %s" % ("free space:", free_space))

        # New structures.
        new_widths = deepcopy(prewrap_widths)
        num_cols_wrap = num_cols
        free_space_wrap = free_space
        col_wrap = [True] * num_cols

        # Loop.
        while True:
            # The average column width.
            ave_width = int(free_space_wrap / num_cols_wrap)

            # Debugging printout.
            if debug:
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
                    if debug:
                        print("        %-20s %s" % ("remove column:", i))

            # Done.
            if not rescale:
                # Set the column widths.
                for i in range(num_cols):
                    if new_widths[i] > ave_width:
                        new_widths[i] = ave_width
                break

        # Debugging printouts.
        if debug:
            print("    %-20s %s" % ("prewrap_widths:", prewrap_widths))
            print("    %-20s %s" % ("new_widths:", new_widths))
            print("    %-20s %s" % ("num_cols:", num_cols))
            print("    %-20s %s" % ("num_cols_wrap:", num_cols_wrap))
            print("    %-20s %s" % ("free_space:", free_space))
            print("    %-20s %s" % ("free_space_wrap:", free_space_wrap))
            print("    %-20s %s" % ("col_wrap:", col_wrap))

    # No column wrapping.
    else:
        new_widths = prewrap_widths
        col_wrap = [False] * num_cols

    # The total table width.
    total_width = sum(new_widths) + used

    # The header.
    if headings != None:
        text += _rule(width=total_width)    # Top rule.
        text += _blank(width=total_width)    # Blank line.
        for i in range(num_head_rows):
            text += _table_line(text=headings[i], widths=new_widths, separator='   ', pad_left=pad_left, pad_right=pad_right, prefix=prefix, postfix=postfix, justification=justification_headings[i])
            if i < num_head_rows-1 and spacing:
                text += _blank(width=total_width)
        text += _rule(width=total_width)    # Middle rule.

    # No header.
    else:
        text += _rule(width=total_width)    # Top rule.

    # The table contents.
    for i in range(num_rows):
        # Column text, with wrapping.
        col_text = [contents[i]]
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
        if spacing or i == 0:
            text += _blank(width=total_width)

        # The contents.
        for k in range(num_lines):
            text += _table_line(text=col_text[k], widths=new_widths, separator=separator, pad_left=pad_left, pad_right=pad_right, prefix=prefix, postfix=postfix, justification=justification_contents[i])

    # The bottom rule, followed by a blank line.
    text += _rule(width=total_width)
    text += _blank(width=total_width)

    # Return the table text.
    return text
