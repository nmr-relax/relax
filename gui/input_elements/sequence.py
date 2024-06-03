###############################################################################
#                                                                             #
# Copyright (C) 2012,2014,2019 Edward d'Auvergne                              #
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
import wx.lib.mixins.listctrl

# relax module imports.
import dep_check
from graphics import fetch_icon
from gui.input_elements.combo_list import Combo_list
from gui.fonts import font
from gui.misc import add_border
from gui.string_conv import float_to_gui, gui_to_float, gui_to_int, gui_to_list, gui_to_py, gui_to_str, gui_to_tuple, int_to_gui, list_to_gui, py_to_gui, str_to_gui, tuple_to_gui
from lib.check_types import is_list
from lib.errors import RelaxError
from status import Status; status = Status()


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

    def __init__(self, name=None, default=None, parent=None, element_type='default', seq_type=None, value_type=None, dim=None, min=0, max=1000, sizer=None, titles=None, desc=None, combo_choices=None, combo_data=None, combo_list_min=None, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, single_value=False, read_only=False, can_be_none=False):
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
        @keyword titles:            The titles of each of the elements of the fixed dimension elements.
        @type titles:               list of str
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword combo_choices:     The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:        list of str
        @keyword combo_data:        The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:           list
        @keyword combo_list_min:    The minimum length for the Combo_list object.
        @type combo_list_min:       int or None
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
        @keyword single_value:      A flag which if True will cause single input values to be treated as single values rather than a list or tuple.
        @type single_value:         bool
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Store the args.
        self.parent = parent
        self.name = name
        self.default = default
        self.element_type = element_type
        self.seq_type = seq_type
        self.value_type = value_type
        self.dim = dim
        self.min = min
        self.max = max
        self.titles = titles
        self.single_value = single_value
        self.can_be_none = can_be_none

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
            self.convert_from_gui = gui_to_py
            self.convert_to_gui =   py_to_gui

        # The sequence types.
        if seq_type == 'list':
            self.convert_from_gui_seq = gui_to_list
            self.convert_to_gui_seq =   list_to_gui
        elif seq_type == 'tuple':
            self.convert_from_gui_seq = gui_to_tuple
            self.convert_to_gui_seq =   tuple_to_gui
        else:
            raise RelaxError("Unknown sequence type '%s'." % seq_type)

        # Initialise the default element.
        if self.element_type == 'default':
            # Translate the read_only flag if None.
            if read_only == None:
                read_only = False

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
            dc = wx.ScreenDC()
            dc.SetFont(font.normal)
            x, y = dc.GetTextExtent(desc)
            if dep_check.wx_classic:
                sub_sizer.AddSpacer((divider - x, 0))
            else:
                sub_sizer.AddSpacer(int(divider - x))

            # The input field.
            self._field = wx.TextCtrl(parent, -1, '')
            self._field.SetMinSize((50, height_element))
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
            button = wx.BitmapButton(parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.edit-rename', "16x16"), wx.BITMAP_TYPE_ANY))
            button.SetMinSize((-1, height_element))
            button.SetToolTip(wx.ToolTip("Edit the values."))
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
                text.SetToolTip(wx.ToolTip(tooltip))
                self._field.SetToolTip(wx.ToolTip(tooltip))

            # Set the default value.
            if self.default is not None:
                self._field.SetValue(self.convert_to_gui_seq(self.default))

        # Initialise the combo list input field.
        elif self.element_type == 'combo_list':
            # Translate the read_only flag if None.
            if read_only == None:
                read_only = False

            # Correct the min_length argument.
            if combo_list_min == None:
                combo_list_min = 1

            # Set up the Combo_list object.
            self._field = Combo_list(parent, sizer, desc, value_type=value_type, min_length=combo_list_min, choices=combo_choices, data=combo_data, default=default, tooltip=tooltip, read_only=read_only, can_be_none=can_be_none)

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

        # Handle Combo_list elements.
        if self.element_type == 'combo_list':
            # Empty lists.
            if value == [] or value == None:
                return None

        # Non Combo_list elements.
        else:
            # Handle single values.
            value_set = False
            if self.single_value:
                try:
                    # Convert.
                    value = self.convert_from_gui(value)

                    # Check that the conversion was successful.
                    if value == None and self.can_be_none:
                        value_set = True
                    elif self.value_type == None:
                        value_set = True
                    elif self.value_type in ['float', 'num']:
                        if isinstance(value, int) or isinstance(value, float):
                            value_set = True
                    elif self.value_type == 'int':
                        if isinstance(value, int):
                            value_set = True
                    elif self.value_type == 'str':
                        if self.seq_type == 'list' and value[0] != '[':
                            value_set = True
                        elif self.seq_type == 'tuple' and value[0] != '(':
                            value_set = True
                except:
                    pass

            # Convert to a sequence, handling bad user behaviour.
            if not value_set:
                try:
                    value = self.convert_from_gui_seq(value)

                # Set the value to None or an empty sequence.
                except RelaxError:
                    if self.can_be_none:
                        value = None
                    elif self.seq_type == 'list':
                        value = []
                    else:
                        value = ()

                # Handle all other errors.
                except:
                    value = None

        # Nothing to do.
        if value == None:
            return None

        # Convert sequences to single values as needed.
        if self.single_value:
            if (isinstance(value, list) or isinstance(value, tuple)) and len(value) == 1:
                value = value[0]

        # Convert single values to sequences as needed.
        elif value != None:
            if self.seq_type == 'list' and not isinstance(value, list):
                value = [value]
            elif self.seq_type == 'tuple' and not isinstance(value, tuple):
                value = (value,)

        # Handle empty list and tuple values.
        if not self.single_value and len(value) == 0:
            return None

        # Return the value.
        return value


    def SetValue(self, value=None, index=None):
        """Special method for setting the value of the GUI element.

        @keyword value: The value to set.
        @type value:    value or list of values
        @keyword index: The index of the value to set, if the full list is not given.
        @type index:    int or None
        """

        # The ComboBox list.
        if self.element_type == 'combo_list':
            self._field.SetValue(value=value, index=index)

        # The other elements.
        else:
            # Handle single values.
            if self.single_value and isinstance(value, list) and len(value) == 1:
                value = value[0]

            # Convert and set the value.
            self._field.SetValue(self.convert_to_gui_seq(value))


    def UpdateChoices(self, combo_choices=None, combo_data=None, combo_default=None):
        """Special wizard method for updating the list of choices in a ComboBox type element.

        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo_list'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo_list'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo_list'.
        @type combo_default:    str or None
        """

        # The ComboBox list.
        if self.element_type == 'combo_list':
            self._field.UpdateChoices(combo_choices=combo_choices, combo_data=combo_data, combo_default=combo_default)


    def open_dialog(self, event):
        """Open a special dialog for inputting a list of text values.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show the window.
        self.selection_win_show()

        # Extract the data from the selection window once closed.
        self.selection_win_data()

        # Destroy the window.
        self.sel_win.Destroy()
        del self.sel_win


    def selection_win_data(self):
        """Extract the data from the selection window."""

        # Get the value.
        value = self.sel_win.GetValue()

        # No sequence data.
        if value == None or not len(value):
            self.Clear()

        # Set the values.
        else:
            self.SetValue(value)


    def selection_win_show(self):
        """Show the selection window."""

        # Destroy any pre-existing sequence window.
        if hasattr(self, 'sel_win'):
            self.sel_win.Destroy()
            del self.sel_win

        # Initialise the model selection window.
        self.sel_win = Sequence_window(parent=self.parent, name=self.name, seq_type=self.seq_type, value_type=self.value_type, titles=self.titles, dim=self.dim)

        # Set the model selector window selections.
        self.sel_win.SetValue(self.GetValue())

        # Show the model selector window.
        if status.show_gui:
            self.sel_win.ShowModal()
            self.sel_win.Close()



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

        # Catch edits.
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.begin_label_edit)


    def begin_label_edit(self, event):
        """Catch edits to make the first column read only.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Prevent edits in the first column.
        if event.m_col == 0:
            event.Veto()

        # Otherwise the user is free to edit.
        else:
            event.Skip()



class Sequence_window(wx.Dialog):
    """The Python sequence object editor window."""

    # The window size.
    SIZE = (800, 600)

    # A border.
    BORDER = 10

    # Sizes.
    SIZE_BUTTON = (150, 33)

    def __init__(self, parent=None, name='', seq_type='list', value_type='str', dim=None, titles=None):
        """Set up the string list editor window.

        @keyword parent:        The parent GUI element.
        @type parent:           wx.Window instance or None
        @keyword name:          The name of the window.
        @type name:             str
        @keyword seq_type:      The type of Python sequence.  This should be one of 'list' or 'tuple'.
        @type seq_type:         str
        @keyword value_type:    The type of Python data expected in the sequence.  This should be one of 'float', 'int', or 'str'.
        @type value_type:       str
        @keyword dim:           The fixed dimension that the sequence must conform to.
        @type dim:              int or None
        @keyword titles:        The titles of each of the elements of the fixed dimension elements.
        @type titles:           list of str
        """

        # Store the args.
        self.name = name
        self.seq_type = seq_type
        self.value_type = value_type
        self.dim = dim
        self.titles = titles

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

        # Variable length.
        if not hasattr(self, 'variable_length'):
            self.variable_length = False
            self.offset = 0
            if dim == None:
                self.variable_length = True
                self.offset = 1

        # The title of the dialog.
        title = "Edit the %s values." % name

        # Set up the dialog.
        wx.Dialog.__init__(self, parent, id=-1, title=title)

        # Initialise some values
        self.width = self.SIZE[0] - 2*self.BORDER

        # Set the frame properties.
        self.SetSize(self.SIZE)
        if not dep_check.wx_classic and status.show_gui:
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

        # Initialise the list of elements to a single element.
        if not self.sequence.GetItemCount():
            self.add_element()


    def GetValue(self):
        """Return the values as a sequence of values.

        @return:    The sequence of values.
        @rtype:     sequence type
        """

        # Init.
        values = []

        # Loop over the entries.
        for i in range(self.sequence.GetItemCount()):
            # Get the text.
            item = self.sequence.GetItem(i, col=1)
            text = item.GetText()

            # Store the text.
            try:
                value = self.convert_from_gui(text)
            except:
                value = None
            values.append(value)

        # Sequence conversion.
        if self.seq_type == 'tuple':
            values = tuple(values)

        # Check that something is set.
        empty = True
        for i in range(len(values)):
            if values[i] != None:
                empty = False
                break

        # Return nothing.
        if empty:
            return None

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

        # Invalid list, so do nothing.
        if not self.variable_length and is_list(values) and len(values) != self.dim:
            return

        # Single values.
        try:
            len(values)
        except TypeError:
            if self.seq_type == 'list':
                values = [values]
            elif self.seq_type == 'tuple':
                values = (values,)

        # Loop over the entries.
        for i in range(len(values)):
            # Fixed dimension sequences - set the values of the pre-created list.
            if not self.variable_length:
                if dep_check.wx_classic:
                    self.sequence.SetStringItem(i, 1, self.convert_to_gui(values[i]))
                else:
                    self.sequence.SetItem(i, 1, self.convert_to_gui(values[i]))

            # Variable dimension sequences - append the item to the end of the blank list.
            else:
                # The first element already exists.
                if i != 0:
                    # First add the index+1.
                    if dep_check.wx_classic:
                        self.sequence.InsertStringItem(i, int_to_gui(i+1))
                    else:
                        self.sequence.InsertItem(i, int_to_gui(i+1))

                # Then set the value.
                if dep_check.wx_classic:
                    self.sequence.SetStringItem(i, 1, self.convert_to_gui(values[i]))
                else:
                    self.sequence.SetItem(i, 1, self.convert_to_gui(values[i]))


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 0)

        # The non-fixed sequence buttons.
        if self.variable_length:
            # The add button.
            button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Add")
            button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"), wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
            button.SetToolTip(wx.ToolTip("Add an item to the list."))
            button.SetMinSize(self.SIZE_BUTTON)
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.add_element, button)

            # Spacer.
            button_sizer.AddSpacer(20)

            # The delete button.
            button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Delete")
            button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.list-remove', "22x22"), wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
            button.SetToolTip(wx.ToolTip("Delete the last item."))
            button.SetMinSize(self.SIZE_BUTTON)
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.delete, button)

            # Spacer.
            button_sizer.AddSpacer(20)

            # The delete all button.
            button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Delete all")
            button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.edit-delete', "22x22"), wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
            button.SetToolTip(wx.ToolTip("Delete all items."))
            button.SetMinSize(self.SIZE_BUTTON)
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.delete_all, button)

            # Spacer.
            button_sizer.AddSpacer(20)

        # The Ok button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Ok")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.dialog-ok', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.close, button)


    def add_element(self, event=None):
        """Append a new row to the list.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The next index.
        next = self.sequence.GetItemCount()

        # Add a new row with the index at the start.
        if self.variable_length:
            if dep_check.wx_classic:
                self.sequence.InsertStringItem(next, int_to_gui(next+1))
            else:
                self.sequence.InsertItem(next, int_to_gui(next+1))

        # Add a new empty row.
        else:
            if dep_check.wx_classic:
                self.sequence.InsertStringItem(next, str_to_gui(''))
            else:
                self.sequence.InsertItem(next, str_to_gui(''))


    def add_list(self, sizer):
        """Set up the list control.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The control.
        self.sequence = Sequence_list_ctrl(self)

        # Set the column title.
        title = "%s%s" % (self.name[0].upper(), self.name[1:])

        # Add the index column.
        if self.titles:
            self.sequence.InsertColumn(0, "Title")
            self.sequence.SetColumnWidth(0, 200)
        else:
            self.sequence.InsertColumn(0, "Number")
            self.sequence.SetColumnWidth(0, 70)

        # Add a single column, full width.
        self.sequence.InsertColumn(1, title)
        self.sequence.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        # Add the table to the sizer.
        sizer.Add(self.sequence, 1, wx.ALL|wx.EXPAND, 0)

        # The fixed dimension sequence - add all the rows needed.
        if not self.variable_length:
            for i in range(self.dim):
                # Add a new row.
                self.add_element()

                # Add a title to the first column.
                if self.titles:
                    if dep_check.wx_classic:
                        self.sequence.SetStringItem(i, 0, str_to_gui(self.titles[i]))
                    else:
                        self.sequence.SetItem(i, 0, str_to_gui(self.titles[i]))

                # Otherwise add numbers starting from 1.
                else:
                    if dep_check.wx_classic:
                        self.sequence.SetStringItem(i, 0, int_to_gui(i+1))
                    else:
                        self.sequence.SetItem(i, 0, int_to_gui(i+1))


    def close(self, event):
        """Close the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Close()


    def delete(self, event):
        """Remove the last item from the list.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Delete the last item.
        item = self.sequence.GetItemCount()
        self.sequence.DeleteItem(item-1)

        # If the list is empty, start again with a single blank element.
        if not self.sequence.GetItemCount():
            self.add_element()


    def delete_all(self, event):
        """Remove all items from the list.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Delete.
        self.sequence.DeleteAllItems()

        # Start again with a single blank element.
        self.add_element()
