###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""The combo list GUI element."""

# Python module imports.
import wx

# relax GUI module imports.
from gui.misc import str_to_gui
from gui.paths import icon_16x16


class Combo_list:
    """The combo list GUI element."""

    def __init__(self, parent, sizer, desc, n=1, choices=[], evt_fn=None, tooltip=None, divider=None, padding=0, spacer=None, read_only=True):
        """Build the combo box list widget for a list of list selections.

        @param parent:      The parent GUI element.
        @type parent:       wx object instance
        @param sizer:       The sizer to put the combo box widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword n:         The number of initial entries.
        @type n:            int
        @keyword choices:   The list of choices (all combo boxes will have the same list).
        @type choices:      list of str
        @keyword evt_fn:    The event handling function.
        @type evt_fn:       func
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the parent class variable _div_left will be used if present.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @keyword read_only: A flag which if True means that text cannot be typed into the combo box widget.
        @type read_only:    bool
        """

        # Store some args.
        self._parent = parent
        self._sizer = sizer
        self._desc = desc
        self._choices = choices
        self._evt_fn = evt_fn
        self._tooltip = tooltip
        self._padding = padding
        self._read_only = read_only

        # Init.
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._combo_boxes = []
        self._sub_sizers = []

        # The divider.
        if not divider:
            self._divider = self._parent._div_left
        else:
            self._divider = divider

        # Build the first rows.
        for i in range(n):
            self._build_row()

        # Add the main sizer.
        self._sizer.Add(self._main_sizer, 0, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            self._sizer.AddStretchSpacer()
        else:
            self._sizer.AddSpacer(spacer)


    def _add(self, event):
        """Add a new combo box.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Add another row.
        self._build_row()

        # Re-perform the window layout.
        self._parent.Layout()


    def _build_row(self, text=None):
        """Construct a row of the GUI element.

        @param text:    The text description of the 
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        index = len(self._combo_boxes)

        # Left padding.
        sub_sizer.AddSpacer(self._padding)

        # The description.
        if index == 0:
            text = wx.StaticText(self._parent, -1, self._desc, style=wx.ALIGN_LEFT)
            sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

            # Spacing.
            x, y = text.GetSize()
            sub_sizer.AddSpacer((self._divider - x, 0))

        # No description for other rows, so add a blank space.
        else:
            sub_sizer.AddSpacer((self._divider, 0))

        # The combo box element.
        style = wx.CB_DROPDOWN
        if self._read_only:
            style = style | wx.CB_READONLY
        combo = wx.ComboBox(self._parent, -1, value='', style=style, choices=self._choices)
        combo.SetMinSize((50, 27))
        sub_sizer.Add(combo, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        self._combo_boxes.append(combo)

        # The add button.
        if index == 0:
            button = wx.BitmapButton(self._parent, -1, wx.Bitmap(icon_16x16.add, wx.BITMAP_TYPE_ANY))
            button.SetMinSize((27, 27))
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            self._parent.Bind(wx.EVT_BUTTON, self._add, button)

        # The delete button.
        elif index == 1:
            button = wx.BitmapButton(self._parent, -1, wx.Bitmap(icon_16x16.remove, wx.BITMAP_TYPE_ANY))
            button.SetMinSize((27, 27))
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            self._parent.Bind(wx.EVT_BUTTON, self._delete, button)

        # Otherwise empty spacing.
        else:
            sub_sizer.AddSpacer((27, 0))

        # Right padding.
        sub_sizer.AddSpacer(self._padding)

        # Add to the main sizer.
        self._sub_sizers.append(sub_sizer)
        self._main_sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Bind events.
        if self._evt_fn:
            self._parent.Bind(wx.EVT_COMBOBOX, self._evt_fn, combo)

        # Tooltip.
        if self._tooltip:
            if index == 0:
                text.SetToolTipString(self._tooltip)
            combo.SetToolTipString(self._tooltip)
            if index <= 1:
                button.SetToolTipString(self._tooltip)


    def _delete(self, event):
        """Add a new combo box.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Remove the combo box element from the list.
        self._combo_boxes.pop()

        # Destroy the subsizer.
        sub_sizer = self._sub_sizers.pop()
        sub_sizer.DeleteWindows()
        self._main_sizer.Remove(sub_sizer)

        # Re-perform the window layout.
        self._parent.Layout()


    def GetValue(self):
        """Return the value represented by this GUI element.

        @return:    The list of choices as a GUI string.
        @rtype:     unicode
        """

        # Build the string form of the list.
        text = u'['

        # Loop over the combo boxes.
        for i in range(len(self._combo_boxes)):
            # Get the value.
            val = self._combo_boxes[i].GetValue()

            # Nothing, so skip.
            if not len(val):
                continue

            # Add a comma.
            if len(text) > 1:
                text = "%s, " % text

            # Add the value.
            text = "%s'%s'" % (text, val)

        # End.
        text = "%s]" % text

        # Return the list.
        return text


    def ResetChoices(self, combo_choices=None, combo_data=None, combo_default=None):
        """Special wizard method for resetting the list of choices in a ComboBox type element.

        @param key:             The key corresponding to the desired GUI element.
        @type key:              str
        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo'.
        @type combo_default:    str or None
        """

        # Loop over the combo boxes.
        for i in range(len(self._combo_boxes)):
            # First clear all data.
            self._combo_boxes[i].Clear()

            # Loop over the choices and data, adding both to the end.
            for j in range(len(combo_choices)):
                self._combo_boxes[i].Insert(str_to_gui(combo_choices[j]), j, combo_data[j])

            # Set the default selection.
            if combo_default:
                self._combo_boxes[i].SetStringSelection(combo_default)
