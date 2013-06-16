###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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
"""Module containing a set of special GUI elements to be used in the relax wizards."""

# Python module imports.
import wx

# relax module imports.
from gui.fonts import font
from gui.string_conv import bool_to_gui, gui_to_bool
from lib.errors import RelaxError
from status import Status; status = Status()


class Selector_bool:
    """Wizard GUI element for boolean selection."""

    def __init__(self, name=None, parent=None, element_type='default', sizer=None, desc=None, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, default=True):
        """Build the boolean selector widget for selecting between True and False.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword parent:            The wizard GUI element.
        @type parent:               wx.Panel instance
        @keyword element_type:      The type of GUI element to create.  This is currently unused, but can in the future specify alternative selector widgets.
        @type element_type:         str
        @keyword sizer:             The sizer to put the combo box widget into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword divider:           The position of the divider.
        @type divider:              int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword height_element:    The height in pixels of the GUI element.
        @type height_element:       int
        @keyword default:           The default boolean value.
        @type default:              bool
        """

        # Store the args.
        self.default = default
        self.name = name
        self.element_type = element_type

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(parent, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            raise RelaxError("The divider position has not been supplied.")

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The combo box element.
        style = wx.CB_DROPDOWN | wx.CB_READONLY
        self.combo = wx.ComboBox(parent, -1, value=bool_to_gui(default), style=style, choices=['True', 'False'])
        self.combo.SetMinSize((50, height_element))
        self.combo.SetFont(font.normal)
        sub_sizer.Add(self.combo, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer.
        sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Tooltip.
        if tooltip:
            text.SetToolTipString(tooltip)
            self.combo.SetToolTipString(tooltip)


    def Clear(self):
        """Special method for clearing or resetting the GUI element."""

        # Reset to the default.
        self.combo.SetStringSelection(bool_to_gui(self.default))


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The string list value.
        @rtype:     list of str
        """

        # Convert and return the value from a ComboBox.
        return gui_to_bool(self.combo.GetValue())


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    list of str
        """

        # Set the selection.
        self.combo.SetStringSelection(bool_to_gui(value))
