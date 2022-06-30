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
from graphics import fetch_icon
from gui.fonts import font
from gui.string_conv import str_to_gui


class Text_ctrl:
    """The analysis specific text control.

    This consists of three elements:  wx.StaticText, wx.TextCtrl, and wx.Button.
    """

    def __init__(self, box, parent, text="", default="", tooltip=None, tooltip_button=None, button_text=" Change", control=wx.TextCtrl, icon=fetch_icon('oxygen.actions.document-open', "16x16"), fn=None, editable=True, button=False, width_text=200, width_button=80, spacer=0):
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
        @keyword tooltip_button:    The separate tooltip for the button.
        @type tooltip_button:       str
        @keyword button_text:       The text to display on the button.
        @type button_text:          str
        @keyword control:           The control class to use.
        @type control:              wx.TextCtrl derived class
        @keyword icon:              The path of the icon to use for the button.
        @type icon:                 str
        @keyword fn:                The function or method to execute when clicking on the button.  If this is a string, then an equivalent function will be searched for in the control object.
        @type fn:                   func or str
        @keyword editable:          A flag specifying if the control is editable or not.
        @type editable:             bool
        @keyword button:            A flag which if True will cause a button to appear.
        @type button:               bool
        @keyword width_text:        The width of the text element.
        @type width_text:           int
        @keyword width_button:      The width of the button.
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
        dc = wx.ScreenDC()
        dc.SetFont(font.normal)
        x, y = dc.GetTextExtent(text)
        size_horizontal = y + 8

        # Spacer.
        if dep_check.wx_classic:
            sizer.AddSpacer((spacer, -1))
        else:
            sizer.AddSpacer(spacer)

        # The text input field.
        self.field = control(parent, -1, str_to_gui(default))
        self.field.SetMinSize((-1, size_horizontal))
        self.field.SetFont(font.normal)
        self.field.SetEditable(editable)
        if not editable:
            colour = parent.GetBackgroundColour()
            self.field.SetOwnBackgroundColour(colour)
        sizer.Add(self.field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Spacer.
        if dep_check.wx_classic:
            sizer.AddSpacer((spacer, -1))
        else:
            sizer.AddSpacer(spacer)

        # The button.
        if button:
            # Function is in the control class.
            if isinstance(fn, str):
                # The function.
                fn = getattr(field, fn)

            # Add the button.
            self.button = wx.lib.buttons.ThemedGenBitmapTextButton(parent, -1, None, str_to_gui(button_text))
            self.button.SetBitmapLabel(wx.Bitmap(icon, wx.BITMAP_TYPE_ANY))
            self.button.SetMinSize((width_button, size_horizontal))
            self.button.SetFont(font.normal)
            parent.Bind(wx.EVT_BUTTON, fn, self.button)
            sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # No button, so add a spacer.
        else:
            if dep_check.wx_classic:
                sizer.AddSpacer((width_button, -1))
            else:
                sizer.AddSpacer(width_button)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Tooltip.
        if tooltip:
            self.label.SetToolTip(wx.ToolTip(tooltip))
            self.field.SetToolTip(wx.ToolTip(tooltip))
        if button and tooltip_button:
            self.button.SetToolTip(wx.ToolTip(tooltip_button))


    def Enable(self, enable=True):
        """Enable or disable the element for user input.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """

        # Call the control and button methods.
        self.field.Enable(enable)
        if hasattr(self, 'button'):
            self.button.Enable(enable)


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
