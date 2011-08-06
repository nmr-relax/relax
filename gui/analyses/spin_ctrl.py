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
"""Module containing the base class for all frames."""

# Python module imports.
import wx

# relax GUI module imports.
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
        @keyword tooltip:   	The tooltip which appears on hovering over the text or spin control.
        @type tooltip:      	str
        @keyword control:       The control class to use.
        @type control:          wx.SpinCtrl derived class
        @keyword width_text:    The width of the text element.
        @type width_text:       int
        @keyword width_button:  The width of the button.
        @type width_button:     int
        @keyword spacer:        The horizontal spacing between the elements.
        @type spacer:           int
        @return:                The text control object.
        @rtype:                 control object
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        self.label = self.add_static_text(sizer, parent, text=text, width=width_text)

        # The size for all elements, based on this text.
        size = self.label.GetSize()
        size_horizontal = size[1] + 8

        # Spacer.
        sizer.AddSpacer((spacer, -1))

        # The spin control.
        self.control = control(parent, -1, text, min=min, max=max)
        self.control.SetFont(font.normal)
        box.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacer.
        sizer.AddSpacer((spacer, -1))

        # No button, so add a spacer.
        sizer.AddSpacer((width_button, -1))

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Tooltip.
        if tooltip:
            self.label.SetToolTipString(tooltip)
            self.control.SetToolTipString(tooltip)


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
