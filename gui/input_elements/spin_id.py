###############################################################################
#                                                                             #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""GUI element for the user input of spin IDs."""

# Python module imports.
from copy import deepcopy
import wx

# relax module imports.
from generic_fns.mol_res_spin import id_string_doc
from relax_errors import RelaxError

# relax GUI module imports.
from gui.fonts import font
from gui.string_conv import gui_to_str, str_to_gui


class Spin_id:
    """GUI element for the input of spin ID strings."""

    def __init__(self, name=None, default=None, parent=None, element_type='default', sizer=None, desc="spin ID string", combo_choices=None, combo_data=None, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, can_be_none=True):
        """Set up the base spin ID element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value.
        @type default:              str or None
        @keyword parent:            The parent GUI element.
        @type parent:               wx.Panel instance
        @keyword element_type:      The type of GUI element to create.  This currently only supports the 'default' type.
        @type element_type:         str
        @keyword sizer:             The sizer to put the input field widget into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword combo_choices:     The list of choices to present to the user.
        @type combo_choices:        list of str
        @keyword combo_data:        The data returned by a call to GetValue().  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:           list
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword choices:           The list of choices to present to the user.
        @type choices:              list of str
        @keyword divider:           The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:              None or int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword height_element:    The height in pixels of the GUI element.
        @type height_element:       int
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Check the element type.
        types = ['default']
        if element_type not in types:
            raise RelaxError("The %s element type '%s' must be one of %s." % (name, element_type, types))

        # Store the args.
        self.name = name
        self.default = default
        self.can_be_none = can_be_none

        # The combo choices, if not supplied.
        if combo_choices == None or combo_choices == []:
            combo_choices = ['@N', '@N*', '@C', '@C*', '@H', '@H*', '@O', '@O*', '@P', '@P*']

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

        # The input field.
        style = wx.CB_DROPDOWN
        self._field = wx.ComboBox(parent, -1, '', style=style)

        # Update the choices.
        self.UpdateChoices(combo_choices=combo_choices, combo_data=combo_data, combo_default=default)

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

        # Initialise the tooltip string, if not supplied.
        if tooltip == None:
            tooltip = ''

        # Add the ID string documentation to the tooltip.
        for type, element in id_string_doc.element_loop():
            if type == 'paragraph':
                # Initial spacing.
                tooltip += '\n\n'

                # The text.
                tooltip += element

        # Set the tooltip.
        text.SetToolTipString(tooltip)
        self._field.SetToolTipString(tooltip)


    def Clear(self):
        """Special method for clearing or resetting the GUI element."""

        # Clear the value.
        self._field.Clear()
        self._field.SetValue('')


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The spin ID value.
        @rtype:     str or None
        """

        # An element selected from the list.
        sel_index = self._field.GetSelection()
        if sel_index == wx.NOT_FOUND:
            value = None
        else:
            value = gui_to_str(self._field.GetClientData(sel_index))

        # A non-list value.
        if value == None:
            value = gui_to_str(self._field.GetValue())

        # Return the value.
        return value


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The spin ID to set.
        @type value:    str or None
        """

        # Loop until the proper client data is found.
        found = False
        for i in range(self._field.GetCount()):
            if self._field.GetClientData(i) == value:
                self._field.SetSelection(i)
                found = True
                break

        # No value found.
        if not found:
            self._field.SetSelection(wx.NOT_FOUND)
            self._field.SetValue(str_to_gui(value))


    def UpdateChoices(self, combo_choices=None, combo_data=None, combo_default=None):
        """Special wizard method for updating the list of choices in a ComboBox type element.

        @keyword combo_choices: The list of choices to present to the user.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo'.
        @type combo_default:    str or None
        """

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

        # Loop over the choices and data, adding both to the end.
        for i in range(len(combo_choices)):
            self._field.Insert(str_to_gui(combo_choices[i]), i, combo_data[i])

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
