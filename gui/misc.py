###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""Miscellaneous functions used throughout the GUI."""

# Python module imports.
import os
import platform
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
