###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
from graphics import fetch_icon
from gui.fonts import font
from gui.string_conv import str_to_gui


class Boolean_ctrl:
    """The analysis specific text control.

    This consists of three elements:  wx.StaticText, wx.TextCtrl, and wx.Button.
    """

    def __init__(self, box, parent, text="", default=True, tooltip=None, tooltip_button=None, button_text=" Toggle", control=wx.TextCtrl, width_text=200, width_button=80, spacer=0):
        """Create a text selection element for the frame.

        This consists of a horizontal layout with a static text element, a text control, and an optional button.

        @param box:                 The box element to pack the structure file selection GUI element into.
        @type box:                  wx.BoxSizer instance
        @param parent:              The parent GUI element.
        @type parent:               wx object
        @keyword text:              The static text.
        @type text:                 str
        @keyword default:           The default value of the control.
        @type default:              bool
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword tooltip_button:    The separate tooltip for the button.
        @type tooltip_button:       str
        @keyword button_text:       The text to display on the button.
        @type button_text:          str
        @keyword control:           The control class to use.
        @type control:              wx.TextCtrl derived class
        @keyword width_text:        The width of the text element.
        @type width_text:           int
        @keyword width_button:      The width of the button.
        @type width_button:         int
        @keyword spacer:            The horizontal spacing between the elements.
        @type spacer:               int
        """

        # Store the state.
        self.state = default

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        self.label = wx.StaticText(parent, -1, text)
        self.label.SetMinSize((width_text, -1))
        self.label.SetFont(font.normal)
        sizer.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The size for all elements, based on this text.
        size = self.label.GetSize()
        size_horizontal = size[1] + 8

        # Spacer.
        sizer.AddSpacer((spacer, -1))

        # The text input field.
        self.field = control(parent, -1, str_to_gui(default))
        self.field.SetMinSize((-1, size_horizontal))
        self.field.SetFont(font.normal)
        colour = parent.GetBackgroundColour()
        self.field.SetOwnBackgroundColour(colour)
        sizer.Add(self.field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Spacer.
        sizer.AddSpacer((spacer, -1))

        # Add the button.
        self.button = wx.lib.buttons.ThemedGenBitmapTextButton(parent, -1, None, str_to_gui(button_text))
        if default == True:
            self.button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.media-record-relax-green'), wx.BITMAP_TYPE_ANY))
        else:
            self.button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.media-record'), wx.BITMAP_TYPE_ANY))
        self.button.SetMinSize((width_button, size_horizontal))
        self.button.SetFont(font.normal)
        parent.Bind(wx.EVT_BUTTON, self.toggle, self.button)
        sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Tooltip.
        if tooltip:
            self.label.SetToolTipString(tooltip)
            self.field.SetToolTipString(tooltip)
        if tooltip_button:
            self.button.SetToolTipString(tooltip_button)


    def Enable(self, enable=True):
        """Enable or disable the element for user input.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """

        # Call the button method.
        self.button.Enable(enable)


    def GetValue(self):
        """Set the value of the control.

        @return:    The value of the text control.
        @rtype:     int
        """

        # Return the state.
        return self.state


    def SetValue(self, value):
        """Set the value of the control.

        @param value:   The value to set the boolean control to.
        @type value:    bool
        """

        # True.
        if value == True:
            self.field.SetValue('True')
            self.button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.media-record-relax-green'), wx.BITMAP_TYPE_ANY))
            self.state = True

        # False:
        else:
            self.field.SetValue('False')
            self.button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.media-record'), wx.BITMAP_TYPE_ANY))
            self.state = False


    def toggle(self, event=None):
        """Switch the state."""

        # From False to True.
        if self.state == False:
            self.field.SetValue('True')
            self.button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.media-record-relax-green'), wx.BITMAP_TYPE_ANY))
            self.state = True

        # From True to False.
        else:
            self.field.SetValue('False')
            self.button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.media-record'), wx.BITMAP_TYPE_ANY))
            self.state = False
