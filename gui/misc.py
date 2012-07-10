###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Miscellaneous functions used throughout the GUI."""

# Python module imports.
from copy import deepcopy
import os
import platform
from textwrap import wrap
import wx

# relax module imports.
from relax_errors import AllRelaxErrors
from status import Status; status = Status()

# relax GUI module imports.
from gui.errors import gui_raise


def add_border(box, border=0, packing=wx.VERTICAL, debug=False):
    """Create the main part of the frame, returning the central sizer.

    @param box:         The box sizer element to pack the borders into.
    @type box:          wx.BoxSizer instance
    @keyword border:    The size of the border in pixels.
    @type border:       int
    @keyword packing:   Specify if the central sizer should be vertically or horizontally packed.
    @type packing:      wx.VERTICAL or wx.HORIZONTAL
    @keyword debug:     A flag which if true will make colourful borders.
    @type debug:        bool
    @return:            The central sizer.
    @rtype:             wx.BoxSizer instance
    """

    # The orientation of the sub sizer.
    orient = box.GetOrientation()
    if orient == wx.HORIZONTAL:
        orient_sub = wx.VERTICAL
    else:
        orient_sub = wx.HORIZONTAL

    # Some sizers.
    sizer_sub = wx.BoxSizer(orient_sub)
    sizer_cent = wx.BoxSizer(packing)

    # Left and right borders (debugging).
    if debug:
        # Left coloured panel.
        panel = wx.Panel(box.GetContainingWindow(), -1)
        panel.SetSize((border, border))
        panel.SetBackgroundColour("Red")
        box.Add(panel, 0, wx.EXPAND|wx.ALL)

        # Centre.
        box.Add(sizer_sub, 1, wx.EXPAND|wx.ALL)

        # Top coloured panel.
        panel = wx.Panel(box.GetContainingWindow(), -1)
        panel.SetSize((border, border))
        panel.SetBackgroundColour("Yellow")
        box.Add(panel, 0, wx.EXPAND|wx.ALL)
 
    # Left and right borders.
    else:
        box.AddSpacer(border)
        box.Add(sizer_sub, 1, wx.EXPAND|wx.ALL)
        box.AddSpacer(border)

    # Top and bottom borders (debugging).
    if debug:
        # Top coloured panel.
        panel = wx.Panel(box.GetContainingWindow(), -1)
        panel.SetSize((border, border))
        panel.SetBackgroundColour("Blue")
        sizer_sub.Add(panel, 0, wx.EXPAND|wx.ALL)

        # Centre.
        sizer_sub.Add(sizer_cent, 1, wx.EXPAND|wx.ALL)

        # Bottom coloured panel.
        panel = wx.Panel(box.GetContainingWindow(), -1)
        panel.SetSize((border, border))
        panel.SetBackgroundColour("Green")
        sizer_sub.Add(panel, 0, wx.EXPAND|wx.ALL)
 
    # Top and bottom borders.
    else:
        sizer_sub.AddSpacer(border)
        sizer_sub.Add(sizer_cent, 1, wx.EXPAND|wx.ALL)
        sizer_sub.AddSpacer(border)
 
    # Return the central sizer.
    return sizer_cent


def bitmap_setup(path):
    """Build and return the bitmap, handling transparency for all operating systems.

    This function is required to handle alpha in bitmap on MS Windows so that regions with partial transparency are not blended into the default dark grey colour of Windows' windows.

    @param path:    The absolute path to the bitmap image.
    @type path:     str
    @return:        The processed bitmap object.
    @rtype:         wx.Bitmap instance
    """

    # Create the bitmap object.
    bitmap = wx.Bitmap(path, wx.BITMAP_TYPE_ANY)

    # Unset the mask if an alpha mask is detected (only on GNU/Linux and MS Windows).
    if bitmap.HasAlpha() and status.wx_info["os"] != "darwin":
        bitmap.SetMaskColour(None)

    # Return the bitmap object.
    return bitmap


def format_table(table):
    """Format the text by stripping whitespace.

    @param table:       The table.
    @type table:        lists of lists of str
    @return:            The formatted table.
    @rtype:             str
    """

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
    used += 2    # Start of the table '  '.
    used += 2    # End of the table '  '.
    used += 3 * (num_cols - 1)   # Middle of the table '   '.
    free_space = status.text_width - used

    # The maximal width for all cells.
    free_width = sum(widths)

    # Column wrapping.
    if free_width > free_space:
        # New structures.
        new_widths = deepcopy(widths)
        num_cols_wrap = num_cols
        free_space_wrap = free_space
        col_wrap = [True] * num_cols

        # Loop.
        while 1:
            # The average column width.
            ave_width = free_space_wrap / num_cols_wrap

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

            # Done.
            if not rescale:
                # Set the column widths.
                for i in range(num_cols):
                    if new_widths[i] > ave_width:
                        new_widths[i] = ave_width
                break

    # No column wrapping.
    else:
        new_widths = widths
        col_wrap = [False] * num_cols

    # The total table width.
    total_width = sum(new_widths) + used

    # The header.
    text += " " + "_" * (total_width - 2) + "\n\n"    # Top rule and black line.
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
        if table.spacing or i == 1:
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


def open_file(file, force_text=False):
    """Open the file in the platform's native editor/viewer.

    @param file:            The path of the file to open.
    @type file:             str
    @keyword force_text:    A flag which if True will cause a text editor to be launched.
    @type force_text:       bool
    """

    # Windows.
    if platform.uname()[0] in ['Windows', 'Microsoft']:
        # Text file.
        if force_text:
            os.system('notepad %s' % os.path.normpath(file))

        # All other files.
        else:
            os.startfile(os.path.normpath(file))

    # Mac OS X.
    elif platform.uname()[0] == 'Darwin':
        # Text file.
        if force_text:
            os.system('open -t %s' % file)

        # All other files.
        else:
            os.system('open %s' % file)

    # POSIX Systems with xdg-open.
    else:
        os.system('/usr/bin/xdg-open %s' % file)


def protected_exec(fn, *args, **kargs):
    """Apply the given function, catching all RelaxErrors.

    All args and keyword args supplied will be directly applied to the given function.

    @param fn:      The function to apply.
    @type fn:       func
    @return:        The status of execution.
    @rtype:         bool
    """

    # Apply the function.
    try:
        apply(fn, args, kargs)

    # Catch RelaxErrors.
    except AllRelaxErrors, instance:
        # Raise the error in debugging mode.
        if status.debug:
            raise

        # Display a dialog with the error.
        gui_raise(instance, raise_flag=False)

        # Failure.
        return False

    # Success.
    return True


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
