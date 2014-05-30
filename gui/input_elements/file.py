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
from wx.lib import scrolledpanel
import wx.lib.mixins.listctrl

# relax module imports.
from graphics import fetch_icon
from gui.filedialog import RelaxFileDialog
from gui.fonts import font
from gui.misc import add_border, open_file
from gui.string_conv import gui_to_list, gui_to_str, list_to_gui, str_to_gui
from lib.errors import RelaxError
from status import Status; status = Status()


class File_element:
    """A single file element for the multiple file input GUI element."""

    def __init__(self, default='', parent=None, index=None, wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE, padding=3, height_spacer=1, width_spacer=2, height_element=27, preview=True, can_be_none=False):
        """Set up the file GUI element.

        @keyword default:           The default value of the element.
        @type default:              str
        @keyword parent:            The parent GUI element.
        @type parent:               wx.Panel instance
        @keyword index:             The index of the file element, to display its sequence number in the GUI element.
        @type index:                int
        @keyword wildcard:          The file wildcard pattern.  For example for opening PDB files, this could be "PDB files (*.pdb)|*.pdb;*.PDB".
        @type wildcard:             String
        @keyword style:             The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:                long
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword height_spacer:     The amount of spacing to add below the field in pixels.
        @type height_spacer:        int
        @keyword width_spacer:      The amount of spacing to add horizontally between the TextCtrl and buttons in pixels.
        @type width_spacer:         int
        @keyword height_element:    The height in pixels of the GUI element.
        @type height_element:       int
        @keyword preview:           A flag which if true will allow the file to be previewed.
        @type preview:              bool
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Store the arguments.
        self.default = default
        self.parent = parent
        self.wildcard = wildcard
        self.style = style
        self.can_be_none = can_be_none

        # A vertical sizer for the two elements of the file selection GUI elements and a spacer element.
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a sizer for the elements.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The file index.
        desc = str_to_gui("%i:  " % (index+1))
        text = wx.StaticText(self.parent, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal_bold)
        text.SetMinSize((35, -1))
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # A little spacing.
        sub_sizer.AddSpacer(width_spacer)

        # The input field.
        self.field = wx.TextCtrl(self.parent, -1, self.default)
        self.field.SetMinSize((-1, height_element))
        self.field.SetFont(font.normal)
        sub_sizer.Add(self.field, 1, wx.EXPAND|wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # A little spacing.
        sub_sizer.AddSpacer(width_spacer)

        # The file selection button.
        button = wx.BitmapButton(self.parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-open', "16x16"), wx.BITMAP_TYPE_ANY))
        button.SetMinSize((height_element, height_element))
        button.SetToolTipString("Select the file.")
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        self.parent.Bind(wx.EVT_BUTTON, self.select_file, button)

        # File preview.
        if preview:
            # A little spacing.
            sub_sizer.AddSpacer(width_spacer)

            # The preview button.
            button = wx.BitmapButton(self.parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-preview', "16x16"), wx.BITMAP_TYPE_ANY))
            button.SetMinSize((height_element, height_element))
            button.SetToolTipString("Preview")
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            self.parent.Bind(wx.EVT_BUTTON, self.preview_file, button)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add the sizer to the main sizer.
        self.sizer.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add spacing.
        self.sizer.AddSpacer(height_spacer)


    def GetValue(self):
        """Return the file name.

        @return:    The file name.
        @rtype:     str
        """

        # Return the current value.
        return gui_to_str(self.field.GetValue())


    def SetValue(self, value):
        """Set up the list of file.

        @param value:   The list of values to add to the list.
        @type value:    list of str or None
        """

        # Set the value.
        self.field.SetValue(str_to_gui(value))


    def preview_file(self, event=None):
        """Preview a file.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The file name.
        file = gui_to_str(self.field.GetValue())

        # No file, so do nothing.
        if file == None:
            return

        # Open the file as text.
        open_file(file, force_text=True)


    def select_file(self, event=None):
        """Select a file.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The file selection object (initialised in this function and not __init__() so that the working directory is more logical).
        dialog = RelaxFileDialog(self.parent, field=self.field, message="File selection", defaultFile=self.default, wildcard=self.wildcard, style=self.style)

        # Show the dialog and catch if no file has been selected.
        if status.show_gui:
            dialog.select_event(event)



class Selector_file:
    """Wizard GUI element for selecting files."""

    def __init__(self, name=None, default=None, parent=None, sizer=None, desc=None, message='File selection', wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, preview=True, read_only=False):
        """Build the file selection element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value of the element.
        @type default:              str
        @keyword parent:            The wizard GUI element.
        @type parent:               wx.Panel instance
        @keyword sizer:             The sizer to put the input field into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword message:           The file selector prompt string.
        @type message:              String
        @keyword wildcard:          The file wildcard pattern.  For example for opening PDB files, this could be "PDB files (*.pdb)|*.pdb;*.PDB".
        @type wildcard:             String
        @keyword style:             The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:                long
        @keyword tooltip:           The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:              str
        @keyword divider:           The position of the divider.
        @type divider:              int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword height_element:    The height in pixels of the GUI element.
        @type height_element:       int
        @keyword preview:           A flag which if true will allow the file to be previewed.
        @type preview:              bool
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
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
            raise RelaxError("The divider position has not been supplied.")

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        self._field = wx.TextCtrl(parent, -1, default)
        self._field.SetMinSize((-1, height_element))
        self._field.SetFont(font.normal)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The file selection object.
        obj = RelaxFileDialog(parent, field=self._field, message=message, defaultFile=default, wildcard=wildcard, style=style)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-open', "16x16"), wx.BITMAP_TYPE_ANY))
        button.SetMinSize((height_element, height_element))
        button.SetToolTipString("Select the file.")
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        parent.Bind(wx.EVT_BUTTON, obj.select_event, button)

        # File preview.
        if preview:
            # A little spacing.
            sub_sizer.AddSpacer(5)

            # The preview button.
            button = wx.BitmapButton(parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-preview', "16x16"), wx.BITMAP_TYPE_ANY))
            button.SetMinSize((height_element, height_element))
            button.SetToolTipString("Preview")
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            parent.Bind(wx.EVT_BUTTON, self.preview_file, button)

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


    def preview_file(self, event=None):
        """Preview a file.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The file name.
        file = gui_to_str(self._field.GetValue())

        # No file, so do nothing.
        if file == None:
            return

        # Open the file as text.
        open_file(file, force_text=True)



class Selector_file_multiple:
    """Wizard GUI element for selecting files."""

    def __init__(self, name=None, default=None, parent=None, sizer=None, desc=None, message='File selection', wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, preview=True, read_only=False, can_be_none=False):
        """Build the file selection element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value of the element.
        @type default:              str
        @keyword parent:            The wizard GUI element.
        @type parent:               wx.Panel instance
        @keyword sizer:             The sizer to put the input field into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword message:           The file selector prompt string.
        @type message:              String
        @keyword wildcard:          The file wildcard pattern.  For example for opening PDB files, this could be "PDB files (*.pdb)|*.pdb;*.PDB".
        @type wildcard:             String
        @keyword style:             The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:                long
        @keyword tooltip:           The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:              str
        @keyword divider:           The position of the divider.
        @type divider:              int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword height_element:    The height in pixels of the GUI element.
        @type height_element:       int
        @keyword preview:           A flag which if true will allow the file to be previewed.
        @type preview:              bool
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
        @keyword can_be_none:       A flag which specifies if the element is allowed to have the None value.
        @type can_be_none:          bool
        """

        # Store the args.
        self.name = name
        self.parent = parent
        self.can_be_none = can_be_none

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
            raise RelaxError("The divider position has not been supplied.")

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        self._field = wx.TextCtrl(parent, -1, default)
        self._field.SetMinSize((-1, height_element))
        self._field.SetFont(font.normal)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The file selection object.
        obj = RelaxFileDialog(parent, field=self._field, message=message, defaultFile=default, wildcard=wildcard, style=style)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The edit button.
        button = wx.BitmapButton(parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-open', "16x16"), wx.BITMAP_TYPE_ANY))
        button.SetMinSize((height_element, height_element))
        button.SetToolTipString("Choose the file(s).")
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        parent.Bind(wx.EVT_BUTTON, self.open_dialog, button)

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

        # The value.
        value = self._field.GetValue()

        # Handle single values.
        value_set = False
        try:
            # Convert.
            value = gui_to_str(value)

            # Check that the conversion was successful.
            if value == None and self.can_be_none:
                value_set = True
            else:
                if value[0] != '[':
                    value_set = True
        except:
            pass

        # Convert to a list, handling bad user behaviour.
        if not value_set:
            try:
                value = gui_to_list(value)

            # Set the value to None or an empty sequence.
            except:
                if self.can_be_none:
                    value = None
                else:
                    value = []

        # Convert sequences to single values as needed.
        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        # Handle empty list and tuple values.
        if len(value) == 0:
            return None

        # Return the value.
        return value


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    str
        """

        # Handle single values.
        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        # Convert and set the value.
        self._field.SetValue(list_to_gui(value))


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


    def preview_file(self, event=None):
        """Preview a file.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The file name.
        file = gui_to_str(self._field.GetValue())

        # No file, so do nothing.
        if file == None:
            return

        # Open the file as text.
        open_file(file, force_text=True)


    def selection_win_data(self):
        """Extract the data from the file list selection window."""

        # Get the value.
        value = self.sel_win.GetValue()

        # No sequence data.
        if not len(value):
            self.Clear()

        # Set the values.
        else:
            self.SetValue(value)


    def selection_win_show(self):
        """Show the file list selection window."""

        # Initialise the model selection window.
        self.sel_win = Selector_file_window(parent=self.parent, name=self.name)

        # Set the model selector window selections.
        self.sel_win.SetValue(self.GetValue())

        # Show the model selector window.
        if status.show_gui:
            self.sel_win.ShowModal()
            self.sel_win.Close()



class Selector_file_window(wx.Dialog):
    """The file list selection window."""

    # The window size.
    SIZE = (800, 600)

    # A border.
    BORDER = 10

    # Sizes.
    SIZE_BUTTON = (150, 33)

    def __init__(self, parent=None, name='', spacing=10):
        """Set up the file list selection window.

        @keyword parent:    The parent GUI element.
        @type parent:       wx.Window instance or None
        @keyword name:      The name of the window.
        @type name:         str
        @keyword spacing:   The spacing between elements in pixels.
        @type spacing:      int
        """

        # Store the args.
        self.name = name
        self.spacing = spacing

        # The title of the dialog.
        title = "Multiple %s selection." % name

        # Set up the dialog.
        wx.Dialog.__init__(self, parent, id=-1, title=title)

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

        # Add the file list element.
        self.add_file_list(sizer)

        # Some spacing.
        sizer.AddSpacer(self.BORDER)

        # Add the bottom buttons.
        self.add_buttons(sizer)

        # Initialise the list of file selection elements to a single element.
        self.elements = []
        self.add_element()


    def GetValue(self):
        """Return the file names as a list.

        @return:    The list of file names.
        @rtype:     list of str
        """

        # Init.
        values = []

        # Loop over the entries.
        for i in range(len(self.elements)):
            values.append(self.elements[i].GetValue())

        # Return the file name list.
        return values


    def SetValue(self, values):
        """Set up the list of file names.

        @param values:  The list of file names to add.
        @type values:   list of str or None
        """

        # No value.
        if values == None:
            return

        # Single values.
        if isinstance(values, str):
            values = [values]

        # Reset the elements. 
        self.delete_all()

        # Loop over the file paths, creating the elements.
        for i in range(len(values)):
            # The first element already exists.
            if i == 0:
                self.elements[0].SetValue(values[i])

            # Otherwise create a new element.
            else:
                self.add_element(path=values[i])


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 0)

        # The add button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Add")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Add a file selection item to the list.")
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.add_element, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The delete button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Delete")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.list-remove', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Delete the last file selection item.")
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.delete, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The delete all button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Delete all")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.edit-delete', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Delete all items.")
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


    def add_element(self, event=None, path=None):
        """Add a new file selection element to the list.

        @keyword event:     The wx event.
        @type event:        wx event
        @keyword path:      The file path to set the element value to.
        @type path:         str or None
        """

        # Initialise the element.
        element = File_element(parent=self.panel, index=len(self.elements))

        # Set its value.
        if path != None:
            element.SetValue(path)

        # Add the element's sizer to the main element sizer.
        self.element_sizer.Add(element.sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Store the element.
        self.elements.append(element)

        # Reinitialise the scrolling for the panel, just in case the number of elements is bigger than the window.
        self.panel.SetupScrolling(scroll_x=False, scroll_y=True)

        # Redraw.
        self.panel.Layout()


    def add_file_list(self, sizer):
        """Initialise the control.

        @param sizer:       A sizer object.
        @type sizer:        wx.Sizer instance
        """

        # Create a scrolled panel.
        self.panel = scrolledpanel.ScrolledPanel(self, -1, name="file list")

        # A sizer for the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Set the title.
        title = "File list"
        text = wx.StaticText(self.panel, -1, title, style=wx.TE_MULTILINE)
        text.SetFont(font.subtitle)
        panel_sizer.Add(text, 0, wx.ALIGN_LEFT, 0)
        panel_sizer.AddSpacer(self.spacing)

        # Create a sizer for the file selection elements.
        self.element_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(self.element_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Set up and add the panel to the sizer.
        self.panel.SetSizer(panel_sizer)
        self.panel.SetAutoLayout(1)
        self.panel.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer.Add(self.panel, 1, wx.ALL|wx.EXPAND, 0)


    def close(self, event):
        """Close the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Close()


    def delete(self, event=None):
        """Remove the last file selection item from the list.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Destroy the last subsizer.
        self.elements[-1].sizer.DeleteWindows()
        self.element_sizer.Remove(self.elements[-1].sizer)

        # Destroy the Python structures.
        self.elements.pop()

        # If the list is empty, start again with a single blank element.
        if not len(self.elements):
            self.add_element()

        # Redraw.
        self.panel.Layout()


    def delete_all(self, event=None):
        """Remove all file selection items from the list.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Destroy the subsizer.
        for i in range(len(self.elements)):
            self.elements[i].sizer.DeleteWindows()
            self.element_sizer.Remove(self.elements[i].sizer)

        # Destroy all Python structures.
        del self.elements

        # Reset the elements, starting again with a single blank element.
        self.elements = []
        self.add_element()

        # Redraw.
        self.panel.Layout()
