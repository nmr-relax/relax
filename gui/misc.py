###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
from math import pow
from string import split
import wx

# relax module imports.
from relax_errors import AllRelaxErrors

# relax GUI module imports.
from gui.message import error_message


def add_border(box, border=0, packing=wx.VERTICAL):
    """Create the main part of the frame, returning the central sizer.

    @param box:         The box sizer element to pack the borders into.
    @type box:          wx.BoxSizer instance
    @keyword border:    The size of the border in pixels.
    @type border:       int
    @keyword packing:   Specify if the central sizer should be vertically or horizontally packed.
    @type packing:      wx.VERTICAL or wx.HORIZONTAL
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

    # Left and right borders.
    box.AddSpacer(border)
    box.Add(sizer_sub, 1, wx.EXPAND|wx.ALL)
    box.AddSpacer(border)

    # Top and bottom borders.
    sizer_sub.AddSpacer(border)
    sizer_sub.Add(sizer_cent, 1, wx.EXPAND|wx.ALL)
    sizer_sub.AddSpacer(border)

    # Return the central sizer.
    return sizer_cent


def bool_to_gui(bool):
    """Convert the bool into the GUI string.

    @param num:     The boolean value of True or False.
    @type num:      bool
    @return:        The GUI string.
    @rtype:         str
    """

    # Convert.
    return unicode(bool)


def convert_to_float(string):
    """Method to convert a string like '1.02*1e-10' to a float variable.

    @param string:  The number in string form.
    @type string:   str
    @return:        The floating point number.
    @rtype:         float
    """

    # Break the number up.
    entries = split('*')

    # The first part of the number.
    a = entries[0]
    a = float(a)

    # The second part of the number.
    b = entries[1]
    b = float(b[2:len(b)])

    # Recombine.
    result = a * pow(10, b)

    # Return the float.
    return result


def gui_to_float(string):
    """Convert the GUI obtained string to an float.

    @param string:  The number in string form.
    @type string:   str
    @return:        The float
    @rtype:         float or None
    """

    # No input.
    if string == '':
        return None

    # Convert.
    return float(string)


def gui_to_int(string):
    """Convert the GUI obtained string to an int.

    @param string:  The number in string form.
    @type string:   str
    @return:        The integer
    @rtype:         int or None
    """

    # No input.
    if string == '':
        return None

    # Convert.
    return int(string)


def float_to_gui(num):
    """Convert the float into the GUI string.

    @param num:     The number in float or None form.
    @type num:      float or None
    @return:        The GUI string.
    @rtype:         str
    """

    # No input.
    if num == None:
        num = ''

    # Convert.
    return unicode(num)


def int_to_gui(num):
    """Convert the int into the GUI string.

    @param num:     The number in int or None form.
    @type num:      int or None
    @return:        The GUI string.
    @rtype:         str
    """

    # No input.
    if num == None:
        num = ''

    # Convert.
    return unicode(num)


def gui_to_bool(string):
    """Convert the GUI obtained string to a bool.

    @param string:  The bool in string form.
    @type string:   str
    @return:        The bool.
    @rtype:         bool
    """

    # No value.
    if string == '':
        return None

    # Convert.
    return bool(string)


def gui_to_list(string):
    """Convert the GUI obtained string to a list.

    @param string:  The list in string form.
    @type string:   str
    @return:        The list.
    @rtype:         list
    """

    # No value.
    if string == '':
        return []

    # Convert.
    val = eval(string)
    if type(val) != list:
        val = [val]

    # Return the list.
    return val


def gui_to_str(string):
    """Convert the GUI obtained string to a string.

    @param string:  The number in string form.
    @type string:   str
    @return:        The string.
    @rtype:         str
    """

    # No value.
    if string == '':
        return None

    # Convert.
    return str(string)


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
        # Display a dialog with the error.
        error_message(instance.text, instance.__class__.__name__)

        # Failure.
        return False

    # Success.
    return True


def str_to_gui(string):
    """Convert the string into the GUI string.

    @param num:     The number in int or None form.
    @type num:      int or None
    @return:        The GUI string.
    @rtype:         str
    """

    # No input.
    if string == None:
        string = ''

    # Convert.
    return unicode(string)
