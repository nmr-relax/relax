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
from copy import deepcopy
from string import upper
import sys
import wx
import wx.lib.mixins.listctrl

# relax module imports.
from graphics import fetch_icon
from relax_errors import RelaxError
from status import Status; status = Status()

# relax GUI module imports.
from gui.components.combo_list import Combo_list
from gui.errors import gui_raise
from gui.filedialog import RelaxDirDialog, RelaxFileDialog
from gui.fonts import font
from gui.misc import add_border, bool_to_gui, float_to_gui, gui_to_bool, gui_to_float, gui_to_int, gui_to_list, gui_to_str, gui_to_tuple, int_to_gui, list_to_gui, nothing, str_to_gui, tuple_to_gui
from gui import paths


class Selector_bool:
    """Wizard GUI element for boolean selection."""

    def __init__(self, name=None, parent=None, element_type='default', sizer=None, desc=None, tooltip=None, divider=None, padding=0, spacer=None, default=True):
        """Build the boolean selector widget for selecting between True and False.

        @keyword name:          The name of the element to use in titles, etc.
        @type name:             str
        @keyword parent:        The wizard GUI element.
        @type parent:           wx.Panel instance
        @keyword element_type:  The type of GUI element to create.  This is currently unused, but can in the future specify alternative selector widgets.
        @type element_type:     str
        @keyword sizer:         The sizer to put the combo box widget into.
        @type sizer:            wx.Sizer instance
        @keyword desc:          The text description.
        @type desc:             str
        @keyword tooltip:       The tooltip which appears on hovering over the text or input field.
        @type tooltip:          str
        @keyword divider:       The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:          None or int
        @keyword padding:       Spacing to the left and right of the widgets.
        @type padding:          int
        @keyword spacer:        The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:           None or int
        @keyword default:       The default boolean value.
        @type default:          bool
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
            divider = parent._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The combo box element.
        style = wx.CB_DROPDOWN | wx.CB_READONLY
        self.combo = wx.ComboBox(parent, -1, value=bool_to_gui(default), style=style, choices=['True', 'False'])
        self.combo.SetMinSize((50, parent.height_element))
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



class Selector_dir:
    """Wizard GUI element for selecting directories."""

    def __init__(self, name=None, default=None, parent=None, sizer=None, desc=None, message='File selection', style=wx.FD_DEFAULT_STYLE, tooltip=None, divider=None, padding=0, spacer=None, read_only=False):
        """Build the file selection element.

        @keyword name:      The name of the element to use in titles, etc.
        @type name:         str
        @keyword default:   The default value of the element.
        @type default:      str
        @keyword parent:    The wizard GUI element.
        @type parent:       wx.Panel instance
        @keyword sizer:     The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @keyword desc:      The text description.
        @type desc:         str
        @keyword message:   The file selector prompt string.
        @type message:      String
        @keyword style:     The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:        long
        @keyword tooltip:   The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @keyword read_only: A flag which if True means that the text of the element cannot be edited.
        @type read_only:    bool
        """

        # Store the args.
        self.name = name

        # Argument translation.
        if default == None:
            default = wx.EmptyString

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
        if not hasattr(parent, 'file_selection_field'):
            parent.file_selection_field = []
        parent.file_selection_field.append(wx.TextCtrl(parent, -1, default))
        self._field = parent.file_selection_field[-1]
        self._field.SetMinSize((-1, parent.height_element))
        self._field.SetFont(font.normal)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The directory selection object.
        obj = RelaxDirDialog(parent, field=self._field, message=message, defaultPath=default, style=style)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-open-folder'), wx.BITMAP_TYPE_ANY))
        button.SetMinSize((parent.height_element, parent.height_element))
        button.SetToolTipString("Select the directory.")
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        parent.Bind(wx.EVT_BUTTON, obj.select_event, button)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer (followed by stretchable spacing).
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

        # Clear the value from the TextCtrl.
        self._field.Clear()


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The string value.
        @rtype:     list of str
        """

        # Convert and return the value from a TextCtrl.
        return gui_to_str(self._field.GetValue())


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    str
        """

        # Convert and set the value for a TextCtrl.
        self._field.SetValue(str_to_gui(value))



class Selector_file:
    """Wizard GUI element for selecting files."""

    def __init__(self, name=None, default=None, parent=None, sizer=None, desc=None, message='File selection', wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE, tooltip=None, divider=None, padding=0, spacer=None, preview=True, read_only=False):
        """Build the file selection element.

        @keyword name:      The name of the element to use in titles, etc.
        @type name:         str
        @keyword default:   The default value of the element.
        @type default:      str
        @keyword parent:    The wizard GUI element.
        @type parent:       wx.Panel instance
        @keyword sizer:     The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @keyword desc:      The text description.
        @type desc:         str
        @keyword message:   The file selector prompt string.
        @type message:      String
        @keyword wildcard:  The file wildcard pattern.  For example for opening PDB files, this could be "PDB files (*.pdb)|*.pdb;*.PDB".
        @type wildcard:     String
        @keyword style:     The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:        long
        @keyword tooltip:   The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @keyword preview:   A flag which if true will allow the file to be previewed.
        @type preview:      bool
        @keyword read_only: A flag which if True means that the text of the element cannot be edited.
        @type read_only:    bool
        """

        # Store the args.
        self.name = name

        # Argument translation.
        if default == None:
            default = wx.EmptyString

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
        if not hasattr(parent, 'file_selection_field'):
            parent.file_selection_field = []
        parent.file_selection_field.append(wx.TextCtrl(parent, -1, default))
        self._field = parent.file_selection_field[-1]
        self._field.SetMinSize((-1, parent.height_element))
        self._field.SetFont(font.normal)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The file selection object.
        obj = RelaxFileDialog(parent, field=self._field, message=message, defaultFile=default, wildcard=wildcard, style=style)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(parent, -1, wx.Bitmap(paths.icon_16x16.open, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((parent.height_element, parent.height_element))
        button.SetToolTipString("Select the file.")
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        parent.Bind(wx.EVT_BUTTON, obj.select_event, button)

        # File preview.
        if not hasattr(parent, 'file_selection_preview_button'):
            parent.file_selection_preview_button = []
        if not preview:
            parent.file_selection_preview_button.append(None)
        else:
            # A little spacing.
            sub_sizer.AddSpacer(5)

            # The preview button.
            parent.file_selection_preview_button.append(wx.BitmapButton(parent, -1, wx.Bitmap(paths.icon_16x16.document_preview, wx.BITMAP_TYPE_ANY)))
            button = parent.file_selection_preview_button[-1]
            button.SetMinSize((parent.height_element, parent.height_element))
            button.SetToolTipString("Preview")
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            parent.Bind(wx.EVT_BUTTON, parent.preview_file, button)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer (followed by stretchable spacing).
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

        # Clear the value from the TextCtrl.
        self._field.Clear()


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The string value.
        @rtype:     list of str
        """

        # Convert and return the value from a TextCtrl.
        return gui_to_str(self._field.GetValue())


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    str
        """

        # Convert and set the value for a TextCtrl.
        self._field.SetValue(str_to_gui(value))



class Sequence:
    """Wizard GUI element for the input of all types of Python sequence objects.

    The supported Python types include:
        - list of floats
        - list of integers
        - list of strings
        - tuple of floats
        - tuple of integers
        - tuple of strings
    """

    def __init__(self, name=None, default=None, parent=None, element_type='default', seq_type=None, value_type=None, dim=None, min=0, max=1000, sizer=None, desc=None, combo_choices=None, combo_data=None, combo_list_size=None, tooltip=None, divider=None, padding=0, spacer=None, single_value=False, read_only=False, can_be_none=False):
        """Set up the element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value of the element.
        @type default:              sequence object
        @keyword parent:            The wizard GUI element.
        @type parent:               wx.Panel instance
        @keyword element_type:      The type of GUI element to create.  If set to 'default', the wx.TextCtrl element with a button to bring up a dialog with ListCtrl will be used.  If set to 'combo_list', the special gui.components.combo_list.Combo_list element will be used.
        @type element_type:         str
        @keyword seq_type:          The type of Python sequence.  This should be one of 'list' or 'tuple'.
        @type seq_type:             str
        @keyword value_type:        The type of Python object that the value should be.  This can be one of 'float', 'int', or 'str'.
        @type value_type:           str
        @keyword dim:               The dimensions that a list or tuple must conform to.  For a 1D sequence, this can be a single value or a tuple of possible sizes.  For a 2D sequence (a numpy matrix or list of lists), this must be a tuple of the fixed dimension sizes, e.g. a 3x5 matrix should be specified as (3, 5).
        @type dim:                  int, tuple of int or None
        @keyword min:               For a SpinCtrl, the minimum value allowed.
        @type min:                  int
        @keyword max:               For a SpinCtrl, the maximum value allowed.
        @type max:                  int
        @keyword sizer:             The sizer to put the input field widget into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword combo_choices:     The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:        list of str
        @keyword combo_data:        The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:           list
        @keyword combo_list_size:   The number of initial entries in a Combo_list object.
        @type combo_list_size:      int or None
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword divider:           The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:              None or int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword single_value:      A flag which if True will cause single input values to be treated as single values rather than a list or tuple.
        @type single_value:         bool
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Store the args.
        self.name = name
        self.default = default
        self.element_type = element_type
        self.seq_type = seq_type
        self.value_type = value_type
        self.dim = dim
        self.min = min
        self.max = max
        self.single_value = single_value

        # The sequence types.
        if seq_type == 'list':
            self.convert_from_gui = gui_to_list
            self.convert_to_gui =   list_to_gui
        elif seq_type == 'tuple':
            self.convert_from_gui = gui_to_tuple
            self.convert_to_gui =   tuple_to_gui
        else:
            raise RelaxError("Unknown sequence type '%s'." % seq_type)

        # Initialise the default element.
        if self.element_type == 'default':
            # Translate the read_only flag if None.
            if read_only == None:
                read_only = True

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

            # Read-only.
            if read_only:
                self._field.SetEditable(False)
                colour = parent.GetBackgroundColour()
                self._field.SetOwnBackgroundColour(colour)

            # A little spacing.
            sub_sizer.AddSpacer(5)

            # The edit button.
            button = wx.BitmapButton(parent, -1, wx.Bitmap(paths.icon_16x16.edit_rename, wx.BITMAP_TYPE_ANY))
            button.SetMinSize((parent.height_element, parent.height_element))
            button.SetToolTipString("Edit the values.")
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            parent.Bind(wx.EVT_BUTTON, self.open_dialog, button)

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

            # Set the default value.
            if self.default != None:
                self._field.SetValue(self.convert_to_gui(self.default))

        # Initialise the combo list input field.
        elif self.element_type == 'combo_list':
            # Translate the read_only flag if None.
            if read_only == None:
                read_only = False

            # Set up the Combo_list object.
            self._field = Combo_list(parent, sizer, desc, value_type=value_type, n=combo_list_size, choices=combo_choices, data=combo_data, default=default, tooltip=tooltip, read_only=read_only)

        # Unknown field.
        else:
            raise RelaxError("Unknown element type '%s'." % self.element_type)


    def Clear(self):
        """Special method for clearing or resetting the GUI element."""

        # Clear the value from a TextCtrl or ComboBox.
        if self.element_type in ['default', 'combo_list']:
            self._field.Clear()


    def GetValue(self):
        """Special method for returning the sequence values of the GUI element.

        @return:    The sequence of values.
        @rtype:     sequence type
        """

        # The value.
        value = self._field.GetValue()

        # Convert, handling bad user behaviour.
        try:
            value = self.convert_from_gui(value)
        except RelaxError:
            if self.seq_type == 'list':
                value = []
            else:
                value = ()

        # Handle single values.
        if self.single_value and len(value) == 1:
            if self.seq_type == 'list' and not isinstance(value, list):
                value = [value]
            elif self.seq_type == 'tuple' and not isinstance(value, tuple):
                value = (value,)

        # Handle empty values.
        if len(value) == 0:
            return None

        # Return the value.
        return value


    def ResetChoices(self, combo_choices=None, combo_data=None, combo_default=None):
        """Special wizard method for resetting the list of choices in a ComboBox type element.

        @param key:             The key corresponding to the desired GUI element.
        @type key:              str
        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo_list'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo_list'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo_list'.
        @type combo_default:    str or None
        """

        # The ComboBox list.
        if self.element_type == 'combo_list':
            self._field.ResetChoices(combo_choices=combo_choices, combo_data=combo_data, combo_default=combo_default)


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    list of str
        """

        # Handle single values.
        if self.single_value and len(value) == 1:
            value = value[0]

        # Convert and set the value.
        self._field.SetValue(self.convert_to_gui(value))


    def open_dialog(self, event):
        """Open a special dialog for inputting a list of text values.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the model selection window.
        win = Sequence_window(name=self.name, seq_type=self.seq_type, value_type=self.value_type, dim=self.dim)

        # Set the model selector window selections.
        win.SetValue(self.GetValue())

        # Show the model selector window.
        if status.show_gui:
            win.ShowModal()
            win.Close()

        # Get the value.
        value = win.GetValue()

        # No sequence data.
        if not len(value):
            self.Clear()

        # Set the values.
        else:
            self.SetValue(value)

        # Destroy the window.
        del win



class Sequence_2D(Sequence):
    """Wizard GUI element for the input of all types of 2D Python sequence objects.

    The supported Python types include:
        - list of floats
        - list of integers
        - list of strings
        - tuple of floats
        - tuple of integers
        - tuple of strings
    """

    def __init__(self, name=None, default=None, parent=None, sizer=None, element_type='default', seq_type=None, value_type=None, dim=None, min=0, max=1000, titles=None, desc=None, combo_choices=None, combo_data=None, combo_list_size=None, tooltip=None, divider=None, padding=0, spacer=None, read_only=False, can_be_none=False):
        """Set up the element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value of the element.
        @type default:              2D sequence object
        @keyword parent:            The wizard GUI element.
        @type parent:               wx.Panel instance
        @keyword sizer:             The sizer to put the input field widget into.
        @type sizer:                wx.Sizer instance
        @keyword element_type:      The type of GUI element to create.  If set to 'default', the wx.TextCtrl element with a button to bring up a dialog with ListCtrl will be used.  If set to 'combo_list', the special gui.components.combo_list.Combo_list element will be used.
        @type element_type:         str
        @keyword seq_type:          The type of Python sequence.  This should be one of 'list' or 'tuple'.
        @type seq_type:             str
        @keyword value_type:        The type of Python object that the value should be.  This can be one of 'float', 'int', or 'str'.
        @type value_type:           str
        @keyword dim:               The dimensions that a list or tuple must conform to.  For a 1D sequence, this can be a single value or a tuple of possible sizes.  For a 2D sequence (a numpy matrix or list of lists), this must be a tuple of the fixed dimension sizes, e.g. a 3x5 matrix should be specified as (3, 5).
        @type dim:                  int, tuple of int or None
        @keyword min:               For a SpinCtrl, the minimum value allowed.
        @type min:                  int
        @keyword max:               For a SpinCtrl, the maximum value allowed.
        @type max:                  int
        @keyword titles:            The titles of each of the elements of the fixed width second dimension.
        @type titles:               list of str
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword combo_choices:     The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:        list of str
        @keyword combo_data:        The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:           list
        @keyword combo_list_size:   The number of initial entries in a Combo_list object.
        @type combo_list_size:      int or None
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword divider:           The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:              None or int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Store some of the args.
        self.titles = titles

        # Initialise the base class.
        Sequence.__init__(self, name=name, default=default, parent=parent, sizer=sizer, element_type=element_type, seq_type=seq_type, value_type=value_type, dim=dim, min=min, max=max, desc=desc, combo_choices=combo_choices, combo_data=combo_data, combo_list_size=combo_list_size, tooltip=tooltip, divider=divider, padding=padding, spacer=spacer, read_only=read_only)


    def open_dialog(self, event):
        """Open a special dialog for inputting a list of text values.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the model selection window.
        win = Sequence_window_2D(name=self.name, seq_type=self.seq_type, value_type=self.value_type, titles=self.titles, dim=self.dim)

        # Set the model selector window selections.
        win.SetValue(self.GetValue())

        # Show the model selector window.
        if status.show_gui:
            win.ShowModal()
            win.Close()

        # Get the value.
        value = win.GetValue()

        # No sequence data.
        if not len(value):
            self.Clear()

        # Set the values.
        else:
            self.SetValue(value)

        # Destroy the window.
        del win



class Sequence_list_ctrl(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    """The string list ListCtrl object."""

    def __init__(self, parent):
        """Initialise the control.

        @param parent:  The parent window.
        @type parent:   wx.Frame instance
        """

        # Execute the parent __init__() methods.
        wx.ListCtrl.__init__(self, parent, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        wx.lib.mixins.listctrl.TextEditMixin.__init__(self)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)



class Sequence_window(wx.Dialog):
    """The Python sequence object editor window."""

    # The window size.
    SIZE = (600, 600)

    # A border.
    BORDER = 10

    # Sizes.
    SIZE_BUTTON = (150, 33)

    def __init__(self, name='', seq_type='list', value_type='str', dim=None):
        """Set up the string list editor window.

        @keyword name:          The name of the window.
        @type name:             str
        @keyword seq_type:      The type of Python sequence.  This should be one of 'list' or 'tuple'.
        @type seq_type:         str
        @keyword value_type:    The type of Python data expected in the sequence.  This should be one of 'float', 'int', or 'str'.
        @type value_type:       str
        @keyword dim:           The fixed dimension that the sequence must conform to.
        @type dim:              int or None
        """

        # Store the args.
        self.name = name
        self.seq_type = seq_type
        self.value_type = value_type
        self.dim = dim

        # The base types.
        if value_type in ['float', 'num']:
            self.convert_from_gui = gui_to_float
            self.convert_to_gui =   float_to_gui
        elif value_type == 'int':
            self.convert_from_gui = gui_to_int
            self.convert_to_gui =   int_to_gui
        elif value_type == 'str':
            self.convert_from_gui = gui_to_str
            self.convert_to_gui =   str_to_gui
        else:
            raise RelaxError("Unknown base data type '%s'." % value_type)

        # The title of the dialog.
        title = "Edit the %s values." % name

        # Set up the dialog.
        wx.Dialog.__init__(self, None, id=-1, title=title)

        # Initialise some values
        self.width = self.SIZE[0] - 2*self.BORDER

        # Set the frame properties.
        self.SetSize(self.SIZE)
        self.Centre()
        self.SetFont(font.normal)

        # The main box sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=self.BORDER, packing=wx.VERTICAL)

        # Add the list control.
        self.add_list(sizer)

        # Some spacing.
        sizer.AddSpacer(self.BORDER)

        # Add the bottom buttons.
        self.add_buttons(sizer)


    def GetValue(self):
        """Return the values as a sequence of values.

        @return:    The sequence of values.
        @rtype:     sequence type
        """

        # Init.
        values = []

        # Loop over the entries.
        for i in range(self.sequence.GetItemCount()):
            values.append(self.convert_from_gui(self.sequence.GetItemText(i)))

        # Sequence conversion.
        if self.seq_type == 'tuple':
            values = tuple(values)

        # Return the sequence.
        return values


    def SetValue(self, values):
        """Set up the list values.

        @param values:  The list of values to add to the list.
        @type values:   list of str or None
        """

        # No value.
        if values == None:
            return

        # Loop over the entries.
        for i in range(len(values)):
            # Fixed dimension sequences - set the values of the pre-created list.
            if self.dim:
                self.sequence.SetStringItem(index=i, col=0, label=self.convert_to_gui(values[i]))

            # Variable dimension sequences - append the item to the end of the blank list.
            else:
                self.sequence.InsertStringItem(i, self.convert_to_gui(values[i]))


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 0)

        # The non-fixed sequence buttons.
        if not self.dim:
            # The add button.
            button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Add")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.add, wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
            button.SetToolTipString("Add a row to the list.")
            button.SetMinSize(self.SIZE_BUTTON)
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.append_row, button)

            # Spacer.
            button_sizer.AddSpacer(20)

            # The delete all button.
            button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Delete all")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.edit_delete, wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
            button.SetToolTipString("Delete all items.")
            button.SetMinSize(self.SIZE_BUTTON)
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.delete_all, button)

            # Spacer.
            button_sizer.AddSpacer(20)

        # The Ok button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Ok")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.dialog_ok, wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.close, button)


    def add_list(self, sizer):
        """Set up the list control.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The control.
        self.sequence = Sequence_list_ctrl(self)

        # Set the column title.
        title = "%s%s" % (upper(self.name[0]), self.name[1:])

        # Add a single column, full width.
        self.sequence.InsertColumn(0, title)
        self.sequence.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        # Add the table to the sizer.
        sizer.Add(self.sequence, 1, wx.ALL|wx.EXPAND, 0)

        # The fixed dimension sequence - add all the rows needed.
        if self.dim:
            for i in range(self.dim):
                self.append_row(None)


    def append_row(self, event):
        """Append a new row to the list.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The next index.
        next = self.sequence.GetItemCount()

        # Add a new empty row.
        self.sequence.InsertStringItem(next, '')


    def close(self, event):
        """Close the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Destroy the window.
        self.Destroy()


    def delete_all(self, event):
        """Remove all items from the list.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Delete.
        self.sequence.DeleteAllItems()



class Sequence_window_2D(Sequence_window):
    """The Python 2D sequence object editor window."""

    def __init__(self, name='', seq_type='list', value_type='str', dim=None, titles=None):
        """Set up the string list editor window.

        @keyword name:          The name of the window.
        @type name:             str
        @keyword seq_type:      The type of Python sequence.  This should be one of 'list' or 'tuple'.
        @type seq_type:         str
        @keyword value_type:    The type of Python data expected in the sequence.  This should be one of 'float', 'int', or 'str'.
        @type value_type:       str
        @keyword dim:           The fixed dimensions that the sequence must conform to.
        @type dim:              tuple of int or None
        @keyword titles:        The titles of each of the elements of the fixed width second dimension.  If the dim argument is given, the length of this list must match the second number.
        @type titles:           list of str
        """

        # Store the titles.
        self.titles = titles
        if titles == None:
            self.titles = [wx.EmptyString] * dim[1]

        # Determine the dimensions if not given.
        if dim == None:
            dim = (None, len(self.titles))

        # Initialise the base class.
        Sequence_window.__init__(self, name=name, seq_type=seq_type, value_type=value_type, dim=dim)


    def GetValue(self):
        """Return the values as a 2D sequence of values.

        @return:    The list of lists of values.
        @rtype:     list of lists of str
        """

        # Init.
        values = []

        # Loop over the entries.
        for i in range(self.sequence.GetItemCount()):
            # Append a new list.
            values.append([])

            # Loop over the items.
            for j in range(self.dim[1]):
                # The item.
                item = self.sequence.GetItem(i, j)

                # Append the value.
                values[-1].append(self.convert_from_gui(item.GetText()))

            # Sequence conversion.
            if self.seq_type == 'tuple':
                values[-1] = tuple(values[-1])

        # Sequence conversion.
        if self.seq_type == 'tuple':
            values = tuple(values)

        # Return the list.
        return values


    def SetValue(self, values):
        """Set up the list of lists values.

        @param values:  The list of lists of values to add to the list.
        @type values:   list of lists of str or None
        """

        # No value.
        if values == None:
            return

        # Loop over the entries.
        for i in range(len(values)):
            # Fixed dimension sequences - set the first value of the pre-created list.
            if self.dim:
                self.sequence.SetStringItem(index=i, col=0, label=self.convert_to_gui(values[i][0]))

            # Variable dimension sequences - append the first value to the end of the blank list.
            else:
                self.sequence.InsertStringItem(sys.maxint, self.convert_to_gui(values[i][0]))

            # Loop over the values.
            for j in range(1, self.dim[1]):
                # Set the value.
                self.sequence.SetStringItem(i, j, self.convert_to_gui(values[i][j]))

        # Refresh.
        self.Refresh()


    def add_list(self, sizer):
        """Set up the list control.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The control.
        self.sequence = Sequence_list_ctrl(self)

        # Set the column title.
        title = "%s%s" % (upper(self.name[0]), self.name[1:])

        # Add the columns.
        print `self.dim`
        for i in range(self.dim[1]):
            print `i`
            self.sequence.InsertColumn(i, self.titles[i])
            self.sequence.SetColumnWidth(i, self.width/self.dim[1])

        # Add the table to the sizer.
        sizer.Add(self.sequence, 1, wx.ALL|wx.EXPAND, 0)

        # The fixed dimension sequence - add all the rows needed.
        if self.dim:
            for i in range(self.dim[0]):
                self.append_row(None)



class Value:
    """Wizard GUI element for the input of all types of simple Python objects.

    The supported Python types include:
        - floats
        - integers
        - strings
    """

    def __init__(self, name=None, default=None, parent=None, element_type='default', value_type=None, sizer=None, desc=None, combo_choices=None, combo_data=None, min=0, max=1000, tooltip=None, divider=None, padding=0, spacer=None, read_only=False, can_be_none=False):
        """Set up the base value element.

        @keyword name:          The name of the element to use in titles, etc.
        @type name:             str
        @keyword default:       The default value of the element.
        @type default:          float or int or str
        @keyword parent:        The wizard GUI element.
        @type parent:           wx.Panel instance
        @keyword element_type:  The type of GUI element to create.  This can be set to:
                                    - 'text', a wx.TextCtrl element will be used.
                                    - 'combo', a wx.ComboBox element will be used.
                                    - 'spin', a wx.SpinCtrl element will be used.  This is only valid for integer types!
        @type element_type:     str
        @keyword value_type:    The type of Python object that the value should be.  This can be one of 'float', 'int', or 'str'.
        @type value_type:       str
        @keyword sizer:         The sizer to put the input field widget into.
        @type sizer:            wx.Sizer instance
        @keyword desc:          The text description.
        @type desc:             str
        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword min:           For a SpinCtrl, the minimum value allowed.
        @type min:              int
        @keyword max:           For a SpinCtrl, the maximum value allowed.
        @type max:              int
        @keyword tooltip:       The tooltip which appears on hovering over the text or input field.
        @type tooltip:          str
        @keyword divider:       The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:          None or int
        @keyword padding:       Spacing to the left and right of the widgets.
        @type padding:          int
        @keyword spacer:        The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:           None or int
        @keyword read_only:     A flag which if True means that the text of the element cannot be edited.
        @type read_only:        bool
        @keyword can_be_none:   A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:      bool
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
            divider = parent._div_left

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
            self.ResetChoices(combo_choices=combo_choices, combo_data=combo_data, combo_default=default)

        # Unknown field.
        else:
            raise RelaxError("Unknown element type '%s'." % self.element_type)

        # Set up the input field.
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


    def Clear(self):
        """Special method for clearing or resetting the GUI element."""

        # Clear the value from a TextCtrl or ComboBox.
        if self.element_type in ['text', 'combo']:
            self._field.Clear()


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
            return self.convert_from_gui(self._field.GetClientData(self._field.GetSelection()))


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

        # A TextCtrl?!
        if self.element_type == 'text':
            raise RelaxError("Cannot reset the list of ComboBox choices as this is a TextCtrl!")

        # A SpinCtrl?!
        if self.element_type == 'spin':
            raise RelaxError("Cannot reset the list of ComboBox choices as this is a SpinCtrl!")

        # Reset the choices for a ComboBox.
        if self.element_type == 'combo':
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
            if combo_default:
                # Translate if needed.
                if combo_default in combo_choices:
                    string = combo_default
                elif combo_default not in combo_data:
                    string = combo_default
                else:
                    string = combo_choices[combo_data.index(combo_default)]

                # Set the selection.
                self._field.SetStringSelection(string)


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    list of str or None
        """

        # No value.
        if values == None:
            return

        # Convert and set the value for a TextCtrl.
        if self.element_type == 'text':
            self._field.SetValue(self.convert_to_gui(value))

        # Set the value for a SpinCtrl.
        elif self.element_type == 'spin':
            self._field.SetValue(value)

        # Convert and set the value for a ComboBox.
        elif self.element_type == 'combo':
            # Loop until the proper client data is found.
            for i in range(self._field.GetCount()):
                if self._field.GetClientData(i) == value:
                    self._field.SetSelection(i)
                    break
