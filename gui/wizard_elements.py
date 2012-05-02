###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module containing a set of special GUI elements to be used in the relax wizards."""

# Python module imports.
import wx

# relax GUI module imports.
from gui.fonts import font


class String_list:
    """Wizard GUI element for the input of lists of strings."""

    def __init__(self, parent, sizer, desc, tooltip=None, divider=None, padding=0, spacer=None):
        """Set up the element.

        @param parent:      The wizard GUI element.
        @type parent:       wx.Panel instance
        @param sizer:       The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        """

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
            divider = parent._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        self._field = wx.TextCtrl(parent, -1, '')
        self._field.SetMinSize((50, parent.height_element))
        self._field.SetFont(font.normal)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

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
            self._field.SetToolTipString(tooltip)


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The string list value.
        @rtype:     list of str
        """

        # Convert and return the value.
        return gui_to_list(self._field.GetValue())


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    list of str
        """

        # Convert and set the value.
        self._field.SetValue(list_to_gui(value))
