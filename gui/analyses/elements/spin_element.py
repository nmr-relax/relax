###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Michael Bieri                                       #
# Copyright (C) 2009-2011,2013,2016 Edward d'Auvergne                         #
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
"""Module containing the base class for all frames."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
import dep_check
from gui.fonts import font


class Spin_ctrl:
    """The analysis specific spin control."""

    def __init__(self, box, parent, text="", default=0, min=0, max=1000, tooltip=None, control=wx.SpinCtrl, width_text=200, width_button=80, spacer=0):
        """Create a text selection element using a spinner for the frame.

        This consists of a horizontal layout with a static text element and a spin control

        @param box:             The box element to pack the structure file selection GUI element into.
        @type box:              wx.BoxSizer instance
        @param parent:          The parent GUI element.
        @type parent:           wx object
        @keyword text:          The static text.
        @type text:             str
        @keyword default:       The default value of the control.
        @type default:          int
        @keyword min:           The minimum value allowed.
        @type min:              int
        @keyword max:           The maximum value allowed.
        @type max:              int
        @keyword tooltip:       The tooltip which appears on hovering over the text or spin control.
        @type tooltip:          str
        @keyword control:       The control class to use.
        @type control:          wx.SpinCtrl derived class
        @keyword width_text:    The width of the text element.
        @type width_text:       int
        @keyword width_button:  The width of the button.
        @type width_button:     int
        @keyword spacer:        The horizontal spacing between the elements.
        @type spacer:           int
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        self.label = wx.StaticText(parent, -1, text)
        self.label.SetMinSize((width_text, -1))
        self.label.SetFont(font.normal)
        sizer.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The size for all elements, based on this text.
        dc = wx.ScreenDC()
        dc.SetFont(font.normal)
        x, y = dc.GetTextExtent(text)
        size_horizontal = y + 8

        # Spacer.
        if dep_check.wx_classic:
            sizer.AddSpacer((spacer, -1))
        else:
            sizer.AddSpacer(spacer)

        # The spin control.
        self.control = control(parent, -1, text, min=min, max=max)
        self.control.SetMinSize((-1, size_horizontal))
        self.control.SetFont(font.normal)
        sizer.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        self.control.SetValue(default)

        # Spacer.
        if dep_check.wx_classic:
            sizer.AddSpacer((spacer, -1))
        else:
            sizer.AddSpacer(spacer)

        # No button, so add a spacer.
        if dep_check.wx_classic:
            sizer.AddSpacer((width_button, -1))
        else:
            sizer.AddSpacer(width_button)

        # Tooltip.
        if tooltip:
            self.label.SetToolTip(wx.ToolTip(tooltip))
            self.control.SetToolTip(wx.ToolTip(tooltip))

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def Enable(self, enable=True):
        """Enable or disable the window for user input.

        @keyword enable:    The flag specifying if the control should be enabled or disabled.
        @type enable:       bool
        """

        # Call the control's method.
        self.control.Enable(enable)


    def GetValue(self):
        """Set the value of the control.

        @return:    The value of the spin control.
        @rtype:     int
        """

        # Get the value from the spin control.
        return self.control.GetValue()


    def SetValue(self, value):
        """Set the value of the control.

        @param value:   The value to set the spin control to.
        @type value:    int
        """

        # Set the value of the spin control.
        return self.control.SetValue(value)
