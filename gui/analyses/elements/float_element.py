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
from gui.fonts import font
from gui.string_conv import str_to_gui


class Float_ctrl:
    """The analysis specific floating point number control.

    This consists of two elements:  wx.StaticText and wx.TextCtrl.
    """

    def __init__(self, box, parent, text="", default="", tooltip=None, editable=True, width_text=200, width_button=80, spacer=0):
        """Create a text selection element for the frame.

        This consists of a horizontal layout with a static text element, a text control, and an optional button.

        @param box:                 The box element to pack the structure file selection GUI element into.
        @type box:                  wx.BoxSizer instance
        @param parent:              The parent GUI element.
        @type parent:               wx object
        @keyword text:              The static text.
        @type text:                 str
        @keyword default:           The default text of the control.
        @type default:              str
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword editable:          A flag specifying if the control is editable or not.
        @type editable:             bool
        @keyword width_text:        The width of the text element.
        @type width_text:           int
        @keyword width_button:      The width of the standard button used in the other elements.
        @type width_button:         int
        @keyword spacer:            The horizontal spacing between the elements.
        @type spacer:               int
        """

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

        # The floating point number input field.
        self.field = wx.TextCtrl(parent, -1, str_to_gui(default))
        self.field.SetMinSize((-1, size_horizontal))
        self.field.SetFont(font.normal)
        self.field.SetEditable(editable)
        if not editable:
            colour = parent.GetBackgroundColour()
            self.field.SetOwnBackgroundColour(colour)
        sizer.Add(self.field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Catch all input to ensure that it is a float.
        self.field.Bind(wx.EVT_KEY_DOWN, self.pre_input)
        self.field.Bind(wx.EVT_TEXT, self.post_input)
        self.field.Bind(wx.EVT_KEY_UP, self.end_input)

        # Spacer.
        sizer.AddSpacer((spacer, -1))

        # Empty space where buttons normally are.
        sizer.AddSpacer((width_button, -1))

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Tooltip.
        if tooltip:
            self.label.SetToolTipString(tooltip)
            self.field.SetToolTipString(tooltip)


    def Enable(self, enable=True):
        """Enable or disable the element for user input.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """

        # Call the text control method.
        self.field.Enable(enable)


    def GetValue(self):
        """Set the value of the control.

        @return:    The value of the text control.
        @rtype:     int
        """

        # Get the value from the text control.
        return self.field.GetValue()


    def SetValue(self, value):
        """Set the value of the control.

        @param value:   The value to set the text control to.
        @type value:    text
        """

        # Set the value of the text control.
        return self.field.SetValue(value)


    def end_input(self, event):
        """Restore the cursor position at the end if needed.

        This does not work so well as multiple wx.EVT_KEY_DOWN events can occur for a single wx.EVT_TEXT.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Restore the input position.
        if self._restore_pos_flag:
            self.field.SetInsertionPoint(self._pos)

        # Thaw the field to allow the text to be displayed.
        self.field.Thaw()


    def pre_input(self, event):
        """Catch all key presses to store the original value and position and freeze the element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the restore position flag.
        self._restore_pos_flag = False

        # Store the value and position to restore if the input is bad.
        self._value = self.field.GetValue()
        self._pos = self.field.GetInsertionPoint()

        # Freeze the field so that the changed text is only shown at the end.
        self.field.Freeze()

        # Continue the event to allow text to be entered.
        event.Skip()


    def post_input(self, event):
        """Check that the user input is a float when the text changes, restoring the value if not.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the value.
        value = self.field.GetValue()

        # Initialise the restore flag.
        flag = False

        # Check if it is a number and, if not, restore the original text.
        try:
            float(value)
        except ValueError:
            flag = True

        # Do not allow spaces.
        if ' ' in value:
            flag = True

        # Do not allow 'e' for the exponent.
        if 'e' in value or 'E' in value:
            flag = True

        # Restore the original text and set the flag to restore the cursor position.
        if flag:
            self.field.SetValue(self._value)
            self._restore_pos_flag = True

        # Continue the event.
        event.Skip()
