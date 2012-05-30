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
"""GUI element for the user input of values."""

# Python module imports.
from copy import deepcopy
import wx

# relax module imports.
from relax_errors import RelaxError

# relax GUI module imports.
from gui.errors import gui_raise
from gui.fonts import font
from gui.string_conv import float_to_gui, gui_to_float, gui_to_int, gui_to_list, gui_to_str, int_to_gui, str_to_gui


class Value:
    """GUI element for the input of all types of simple Python objects.

    The supported Python types include:
        - floats
        - integers
        - strings
    """

    def __init__(self, name=None, default=None, parent=None, element_type='default', value_type=None, sizer=None, desc=None, combo_choices=None, combo_data=None, min=0, max=1000, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, read_only=False, can_be_none=False):
        """Set up the base value element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value of the element.
        @type default:              float or int or str
        @keyword parent:            The parent GUI element.
        @type parent:               wx.Panel instance
        @keyword element_type:      The type of GUI element to create.  This can be set to:
                                        - 'text', a wx.TextCtrl element will be used.
                                        - 'combo', a wx.ComboBox element will be used.
                                        - 'spin', a wx.SpinCtrl element will be used.  This is only valid for integer types!
        @type element_type:         str
        @keyword value_type:        The type of Python object that the value should be.  This can be one of 'float', 'int', or 'str'.
        @type value_type:           str
        @keyword sizer:             The sizer to put the input field widget into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword combo_choices:     The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:        list of str
        @keyword combo_data:        The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:           list
        @keyword min:               For a SpinCtrl, the minimum value allowed.
        @type min:                  int
        @keyword max:               For a SpinCtrl, the maximum value allowed.
        @type max:                  int
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
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Set the default.
        if element_type == 'default':
            # Set the default to a SpinCtrl for integers.
            if value_type == 'int' and not can_be_none:
                element_type = 'spin'

            # Set the default to a TextCtrl for all other types.
            else:
                element_type = 'text'

        # Check the spinner.
        if element_type == "spin" and value_type != 'int':
            raise RelaxError("A wx.SpinCtrl element can only be used together with integers.")

        # Store the args.
        self.name = name
        self.default = default
        self.element_type = element_type
        self.can_be_none = can_be_none
        self.read_only = read_only

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

        # Initialise the text input field.
        if self.element_type == 'text':
            # Set up the text control.
            self._field = wx.TextCtrl(parent, -1, '')

            # Read only field.
            if read_only:
                # Cannot edit.
                self._field.SetEditable(False)

                # Change the colour to the background.
                colour = parent.GetBackgroundColour()
                self._field.SetOwnBackgroundColour(colour)

            # Set the default value.
            if self.default != None:
                self._field.SetValue(self.convert_to_gui(self.default))

        # Initialise the spinner input field.
        elif self.element_type == 'spin':
            # Catch limits of None, and set to the wxSpinCtrl defaults.
            if min == None:
                min = 0
            if max == None:
                max = 100

            # Set up the text control.
            self._field = wx.SpinCtrl(parent, -1, min=min, max=max)

            # Read only field (really no such thing for a spin control).
            if read_only:
                # Change the colour to the background.
                colour = parent.GetBackgroundColour()
                self._field.SetOwnBackgroundColour(colour)

            # Set the default value.
            if self.default != None:
                self._field.SetValue(self.default)

        # Initialise the combo box input field.
        elif self.element_type == 'combo':
            # The style.
            style = wx.CB_DROPDOWN
            if read_only:
                style = style | wx.CB_READONLY

            # Set up the combo box.
            self._field = wx.ComboBox(parent, -1, '', style=style)

            # Update the choices.
            self.UpdateChoices(combo_choices=combo_choices, combo_data=combo_data, combo_default=default)

        # Unknown field.
        else:
            raise RelaxError("Unknown element type '%s'." % self.element_type)

        # Set up the input field.
        self._field.SetMinSize((50, height_element))
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


    def Clear(self):
        """Special method for clearing or resetting the GUI element."""

        # Clear the value from a TextCtrl.
        if self.element_type == 'text':
            self._field.Clear()

        # Clear the value from a ComboBox.
        if self.element_type == 'combo':
            self._field.Clear()
            self._field.SetValue('')


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The string list value.
        @rtype:     list of str
        """

        # Convert and return the value from a TextCtrl.
        if self.element_type == 'text':
            # The value.
            value = self._field.GetValue()

            # Convert.
            try:
                value = self.convert_from_gui(value)

            # Raise a clear error for user feedback.
            except:
                gui_raise(RelaxError("The value '%s' is not of the Python %s type." % (value, self.type_string)))
                return None

            return value

        # Return the integer value from a SpinCtrl.
        if self.element_type == 'spin':
            # The value.
            return self._field.GetValue()

        # Convert and return the value from a ComboBox.
        if self.element_type == 'combo':
            # An element selected from the list.
            sel_index = self._field.GetSelection()
            if sel_index == wx.NOT_FOUND:
                value = None
            else:
                value = self.convert_from_gui(self._field.GetClientData(sel_index))

            # A non-list value.
            if value == None:
                value = self.convert_from_gui(self._field.GetValue())

            # Return the value.
            return value


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    list of str or None
        """

        # Convert and set the value for a TextCtrl.
        if self.element_type == 'text':
            self._field.SetValue(self.convert_to_gui(value))

        # Set the value for a SpinCtrl.
        elif self.element_type == 'spin':
            self._field.SetValue(value)

        # Convert and set the value for a ComboBox.
        elif self.element_type == 'combo':
            # Loop until the proper client data is found.
            found = False
            for i in range(self._field.GetCount()):
                if self._field.GetClientData(i) == value:
                    self._field.SetSelection(i)
                    found = True
                    break

            # No value found.
            if not found:
                # Invalid value.
                if self.read_only:
                    raise RelaxError("The Value element is read only, cannot set the value '%s'." % value)

                # Set the unknown value, and remove the selection.
                else:
                    self._field.SetSelection(wx.NOT_FOUND)
                    self._field.SetValue(self.convert_to_gui(value))


    def UpdateChoices(self, combo_choices=None, combo_data=None, combo_default=None):
        """Special wizard method for updating the list of choices in a ComboBox type element.

        @param key:             The key corresponding to the desired GUI element.
        @type key:              str
        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo'.
        @type combo_default:    str or None
        """

        # A TextCtrl?!
        if self.element_type == 'text':
            raise RelaxError("Cannot update the list of ComboBox choices as this is a TextCtrl!")

        # A SpinCtrl?!
        if self.element_type == 'spin':
            raise RelaxError("Cannot update the list of ComboBox choices as this is a SpinCtrl!")

        # Update the choices for a ComboBox.
        if self.element_type == 'combo':
            # Store the current selection's client data to restore at the end.
            sel_index = self._field.GetSelection()
            if sel_index == wx.NOT_FOUND:
                sel = None
            else:
                sel = self._field.GetClientData(sel_index)

            # First clear all data.
            self.Clear()

            # Set the data if needed.
            if combo_data == None:
                combo_data = deepcopy(combo_choices)

            # Handle None in combo boxes by prepending a None element to the lists.
            if self.can_be_none:
                combo_choices.insert(0, '')
                combo_data.insert(0, None)

            # Loop over the choices and data, adding both to the end.
            for i in range(len(combo_choices)):
                self._field.Insert(self.convert_to_gui(combo_choices[i]), i, combo_data[i])

            # Set the default selection.
            if sel == None and combo_default != None:
                # Translate if needed.
                if combo_default in combo_choices:
                    string = combo_default
                    set_sel = True
                elif combo_default not in combo_data:
                    string = combo_default
                    set_sel = False
                else:
                    string = combo_choices[combo_data.index(combo_default)]
                    set_sel = True

                # Set the selection.
                if set_sel:
                    self._field.SetStringSelection(string)

                # Set the value.
                else:
                    self._field.SetValue(string)

            # Restore the selection.
            else:
                for j in range(self._field.GetCount()):
                    if self._field.GetClientData(j) == sel:
                        self._field.SetSelection(j)
