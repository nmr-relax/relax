###############################################################################
#                                                                             #
# Copyright (C) 2012-2014 Edward d'Auvergne                                   #
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
from gui.input_elements.sequence import Sequence, Sequence_list_ctrl, Sequence_window
from gui.string_conv import int_to_gui
from lib.check_types import is_list_of_lists
from status import Status; status = Status()


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

    def __init__(self, name=None, default=None, parent=None, sizer=None, element_type='default', seq_type=None, value_type=None, dim=None, min=0, max=1000, titles=None, desc=None, combo_choices=None, combo_data=None, combo_list_min=None, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, read_only=False, can_be_none=False):
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
        @keyword combo_list_min:    The minimum length for the Combo_list object.
        @type combo_list_min:       int or None
        @keyword tooltip:           The tooltip which appears on hovering over the text or input field.
        @type tooltip:              str
        @keyword divider:           The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:              None or int
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

        # Store some of the args.
        self.titles = titles

        # Initialise the base class.
        Sequence.__init__(self, name=name, default=default, parent=parent, sizer=sizer, element_type=element_type, seq_type=seq_type, value_type=value_type, dim=dim, min=min, max=max, titles=titles, desc=desc, combo_choices=combo_choices, combo_data=combo_data, combo_list_min=combo_list_min, tooltip=tooltip, divider=divider, padding=padding, spacer=spacer, height_element=height_element, read_only=read_only, can_be_none=can_be_none)


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
        del self.sel_win


    def selection_win_show(self):
        """Show the selection window."""

        # Initialise the window.
        self.sel_win = Sequence_window_2D(name=self.name, seq_type=self.seq_type, value_type=self.value_type, titles=self.titles, dim=self.dim)

        # Set the values.
        self.sel_win.SetValue(self.GetValue())

        # Show the window.
        if status.show_gui:
            self.sel_win.ShowModal()
            self.sel_win.Close()



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

        # Variable length.
        self.variable_length = False
        self.offset = 0
        if dim[0] == None:
            self.variable_length = True
            self.offset = 1

        # Initialise the base class.
        Sequence_window.__init__(self, name=name, seq_type=seq_type, value_type=value_type, dim=dim, titles=self.titles)


    def GetValue(self):
        """Return the values as a 2D sequence of values.

        @return:    The list of lists of values.
        @rtype:     list of lists of str or None
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
                item = self.sequence.GetItem(i, j+self.offset)

                # Append the value.
                try:
                    value = self.convert_from_gui(item.GetText())
                except:
                    value = None
                values[-1].append(value)

            # Sequence conversion.
            if self.seq_type == 'tuple':
                values[-1] = tuple(values[-1])

        # Sequence conversion.
        if self.seq_type == 'tuple':
            values = tuple(values)

        # Check that something is set.
        empty = True
        for i in range(len(values)):
            for j in range(len(values[i])):
                if values[i][j] != None:
                    empty = False
                    break

        # Return nothing.
        if empty:
            return None

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

        # Not a list of lists.
        if not is_list_of_lists(values):
            return

        # Loop over the entries.
        for i in range(len(values)):
            # Append a row for variable dimension sequences (the first element already exists).
            if self.variable_length and i != 0:
                self.sequence.InsertStringItem(i, int_to_gui(i+1))

            # Loop over the values.
            for j in range(self.dim[1]):
                # Set the value.
                self.sequence.SetStringItem(i, j+self.offset, self.convert_to_gui(values[i][j]))

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
        title = "%s%s" % (self.name[0].upper(), self.name[1:])

        # Add a column for the indices.
        index_width = 0
        if self.variable_length:
            index_width = 70
            self.sequence.InsertColumn(0, "Number")
            self.sequence.SetColumnWidth(0, index_width)

        # Add the columns.
        for i in range(self.dim[1]):
            self.sequence.InsertColumn(i+self.offset, self.titles[i])
            self.sequence.SetColumnWidth(i+self.offset, (self.width - index_width)/self.dim[1])

        # Add the table to the sizer.
        sizer.Add(self.sequence, 1, wx.ALL|wx.EXPAND, 0)

        # The fixed dimension sequence - add all the rows needed.
        if not self.variable_length:
            for i in range(self.dim[0]):
                self.add_element(None)
