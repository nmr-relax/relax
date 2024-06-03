###############################################################################
#                                                                             #
# Copyright (C) 2011-2012,2016 Edward d'Auvergne                              #
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
"""The combo list GUI element."""

# Python module imports.
from copy import deepcopy
import wx

# relax module imports.
import dep_check
from graphics import fetch_icon
from gui.fonts import font
from gui.string_conv import float_to_gui, gui_to_float, gui_to_int, gui_to_str, int_to_gui, str_to_gui
from lib.errors import RelaxError


class Combo_list:
    """The combo list GUI element."""

    def __init__(self, parent, sizer, desc, value_type=None, n=1, min_length=1, choices=None, data=None, default=None, evt_fn=None, tooltip=None, divider=None, padding=0, spacer=None, read_only=True, can_be_none=False):
        """Build the combo box list widget for a list of list selections.

        @param parent:          The parent GUI element.
        @type parent:           wx object instance
        @param sizer:           The sizer to put the combo box widget into.
        @type sizer:            wx.Sizer instance
        @param desc:            The text description.
        @type desc:             str
        @keyword value_type:    The type of Python object that the value should be.  This can be one of 'float', 'int', or 'str'.
        @type value_type:       str
        @keyword n:             The number of initial entries.
        @type n:                int
        @keyword min_length:    The minimum length for the Combo_list object.
        @type min_length:       int
        @keyword choices:       The list of choices (all combo boxes will have the same list).
        @type choices:          list of str
        @keyword data:          The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the choices list.  If not supplied, the choices list will be used for the returned data.
        @type data:             list
        @keyword default:       The default value of the ComboBox.  This is only used if the element_type is set to 'combo'.
        @type default:          str or None
        @keyword evt_fn:        The event handling function.
        @type evt_fn:           func
        @keyword tooltip:       The tooltip which appears on hovering over the text or input field.
        @type tooltip:          str
        @keyword divider:       The optional position of the divider.  If None, the parent class variable _div_left will be used if present.
        @type divider:          None or int
        @keyword padding:       Spacing to the left and right of the widgets.
        @type padding:          int
        @keyword spacer:        The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:           None or int
        @keyword read_only:     A flag which if True means that text cannot be typed into the combo box widget.
        @type read_only:        bool
        @keyword can_be_none:   A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:      bool
        """

        # Store some args.
        self._parent = parent
        self._sizer = sizer
        self._desc = desc
        self._choices = choices
        self._data = data
        self._default = default
        self._evt_fn = evt_fn
        self._tooltip = tooltip
        self._padding = padding
        self._read_only = read_only
        self._can_be_none = can_be_none
        self._min_length = min_length

        # Set the data if needed.
        if self._data == None:
            self._data = deepcopy(self._choices)

        # The value types.
        if value_type in ['float', 'num']:
            self.convert_from_gui = gui_to_float
            self.convert_to_gui =   float_to_gui
            self.type_string = 'float'
        elif value_type == 'int':
            self.convert_from_gui = gui_to_int
            self.convert_to_gui =   int_to_gui
            self.type_string = 'integer'
        elif value_type == 'str':
            self.convert_from_gui = gui_to_str
            self.convert_to_gui =   str_to_gui
            self.type_string = 'string'
        else:
            raise RelaxError("Unknown value type '%s'." % value_type)

        # Init.
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._combo_boxes = []
        self._sub_sizers = []

        # Set the initial size, if needed.
        if n == None:
            n = 1

        # The divider.
        if not divider:
            self._divider = self._parent._div_left
        else:
            self._divider = divider

        # Build the first rows.
        if n < min_length:
            n = min_length
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
            text.SetFont(font.normal)
            sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

            # Spacing.
            dc = wx.ScreenDC()
            dc.SetFont(font.normal)
            x, y = dc.GetTextExtent(self._desc)
            if dep_check.wx_classic:
                sub_sizer.AddSpacer((self._divider - x, 0))
            else:
                sub_sizer.AddSpacer(int(self._divider - x))

        # No description for other rows, so add a blank space.
        else:
            if dep_check.wx_classic:
                sub_sizer.AddSpacer((self._divider, 0))
            else:
                sub_sizer.AddSpacer(int(self._divider))

        # The combo box element.
        style = wx.CB_DROPDOWN
        if self._read_only:
            style = style | wx.CB_READONLY
        combo = wx.ComboBox(self._parent, -1, value='', style=style)
        combo.SetMinSize((50, 27))
        sub_sizer.Add(combo, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        self._combo_boxes.append(combo)

        # Choices.
        if self._choices != None:
            # Loop over the choices and data, adding both to the end.
            for j in range(len(self._choices)):
                self._combo_boxes[-1].Insert(self.convert_to_gui(self._choices[j]), j, self._data[j])

            # Set the default selection.
            if self._default:
                # A list.
                if isinstance(self._default, list):
                    if index < len(self._default):
                        self._combo_boxes[-1].SetStringSelection(self._default[index-1])

                # Single value.
                else:
                    self._combo_boxes[-1].SetStringSelection(self._default)

        # The add button.
        button = None
        if index == 0:
            button = wx.BitmapButton(self._parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.list-add-relax-blue', "16x16"), wx.BITMAP_TYPE_ANY))
            button.SetMinSize((-1, 27))
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            self._parent.Bind(wx.EVT_BUTTON, self._add, button)

        # The delete button.
        elif index == self._min_length:
            button = wx.BitmapButton(self._parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.list-remove', "16x16"), wx.BITMAP_TYPE_ANY))
            button.SetMinSize((-1, 27))
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            self._parent.Bind(wx.EVT_BUTTON, self._delete, button)

        # Otherwise empty spacing.
        else:
            if dep_check.wx_classic:
                sub_sizer.AddSpacer((27, 0))
            else:
                sub_sizer.AddSpacer(27)

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
                text.SetToolTip(wx.ToolTip(self._tooltip))
            combo.SetToolTip(wx.ToolTip(self._tooltip))
            if index <= 1 and button != None:
                button.SetToolTip(wx.ToolTip(self._tooltip))


    def _delete(self, event):
        """Add a new combo box.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Remove the combo box element from the list.
        self._combo_boxes.pop()

        # Destroy the subsizer.
        sub_sizer = self._sub_sizers.pop()
        sub_sizer.Clear(True)
        self._main_sizer.Remove(sub_sizer)

        # Re-perform the window layout.
        self._parent.Layout()


    def GetValue(self):
        """Return the value represented by this GUI element.

        @return:    The list of choices.
        @rtype:     list
        """

        # Loop over the combo boxes.
        data = []
        n = 0
        for i in range(len(self._combo_boxes)):
            # Get the value.
            sel_index = self._combo_boxes[i].GetSelection()
            if sel_index == wx.NOT_FOUND:
                val = None
            else:
                val = self.convert_from_gui(self._combo_boxes[i].GetClientData(sel_index))

            # Manually added value by the user.
            if val == None:
                val = self.convert_from_gui(self._combo_boxes[i].GetValue())
            # Nothing, so skip.
            if val == None:
                continue

            # Add the value.
            data.append(val)

            # Increment the number.
            n += 1

        # Return the list.
        if self._min_length != None and n < self._min_length:
            return None
        else:
            return data


    def SetValue(self, value=None, index=None):
        """Special method for setting the value of the GUI element.

        @keyword value: The value to set.
        @type value:    value or list of values
        @keyword index: The index of the value to set.
        @type index:    int
        """

        # Single element.
        if not isinstance(value, list):
            # The index default.
            if index == None:
                index = 0

            # Add elements as needed.
            if len(self._combo_boxes) <= index:
                for i in range(len(self._combo_boxes) - index + 1):
                    self._add(None)

            # Loop until the proper client data is found.
            found = False
            for j in range(self._combo_boxes[index].GetCount()):
                if self._combo_boxes[index].GetClientData(j) == value:
                    self._combo_boxes[index].SetSelection(j)
                    found = True
                    break

            # No value found.
            if not found:
                # Invalid value.
                if self._read_only:
                    if value != None:
                        raise RelaxError("The Value element is read only, cannot set the value '%s'." % value)

                # Set the unknown value, and remove the selection.
                else:
                    self._combo_boxes[index].SetSelection(wx.NOT_FOUND)
                    self._combo_boxes[index].SetValue(self.convert_to_gui(value))

        # A list of values.
        else:
            # Add elements as needed.
            if len(self._combo_boxes) <= len(value):
                for i in range(len(value) - len(self._combo_boxes)):
                    self._add(None)

            # Loop over the list.
            for i in range(len(value)):
                # Loop until the proper client data is found.
                found = False
                for j in range(self._combo_boxes[i].GetCount()):
                    if self._combo_boxes[i].GetClientData(j) == value[i]:
                        self._combo_boxes[i].SetSelection(j)
                        found = True
                        break

                # Otherwise set the value.
                if not found:
                    self._combo_boxes[i].SetValue(value[i])


    def UpdateChoices(self, combo_choices=None, combo_data=None, combo_default=None):
        """Special wizard method for updating the list of choices in a ComboBox type element.

        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo'.
        @type combo_default:    str or None
        """

        # Store the values.
        self._choices = combo_choices
        self._data = combo_data
        self._default = combo_default

        # Set the data if needed.
        if self._data == None:
            self._data = deepcopy(self._choices)

        # Handle None in combo boxes by prepending a None element to the lists.
        if self._can_be_none:
            self._choices.insert(0, '')
            self._data.insert(0, None)

        # Loop over the combo boxes.
        for i in range(len(self._combo_boxes)):
            # Store the current selection's client data to restore at the end.
            sel_index = self._combo_boxes[i].GetSelection()
            if sel_index == wx.NOT_FOUND:
                sel = None
            else:
                sel = self._combo_boxes[i].GetClientData(sel_index)

            # First clear all data.
            self._combo_boxes[i].Clear()

            # Loop over the choices and data, adding both to the end.
            for j in range(len(self._choices)):
                self._combo_boxes[i].Insert(self.convert_to_gui(self._choices[j]), j, self._data[j])

            # Set the default selection.
            if sel == None and self._default != None:
                # A list.
                if isinstance(self._default, list):
                    # Add rows as needed.
                    if len(self._default) > len(self._combo_boxes):
                        for k in range(len(self._default) - len(self._combo_boxes)):
                            self._add(None)

                    # Loop over the defaults.
                    for k in range(len(self._default)):
                        # Translate if needed.
                        if self._default[k] in self._choices:
                            string = self._default[k]
                        elif self._default[k] not in self._data:
                            string = self._default[k]
                        else:
                            string = self._choices[self._data.index(self._default[k])]

                        # Set the selection.
                        self._combo_boxes[i].SetStringSelection(string)

                # Single value.
                else:
                    # Translate if needed.
                    if self._default in self._choices:
                        string = self._default
                    elif self._default not in self._data:
                        string = self._default
                    else:
                        string = self._choices[self._data.index(self._default)]

                    # Set the selection.
                    self._combo_boxes[i].SetStringSelection(string)

            # Restore the selection.
            else:
                for j in range(self._combo_boxes[i].GetCount()):
                    if self._combo_boxes[i].GetClientData(j) == sel:
                        self._combo_boxes[i].SetSelection(j)
