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
from string import upper
import wx
import wx.lib.mixins.listctrl

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from gui.fonts import font
from gui.misc import add_border, gui_to_list, gui_to_str, list_to_gui, str_to_gui
from gui import paths


class String_list:
    """Wizard GUI element for the input of lists of strings."""

    def __init__(self, name=None, parent=None, sizer=None, desc=None, tooltip=None, divider=None, padding=0, spacer=None):
        """Set up the element.

        @keyword name:      The name of the element to use in titles, etc.
        @type name:         str
        @keyword parent:    The wizard GUI element.
        @type parent:       wx.Panel instance
        @keyword sizer:     The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @keyword desc:      The text description.
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

        # Store the args.
        self.name = name

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
        self._field.SetEditable(False)
        colour = parent.GetBackgroundColour()
        self._field.SetOwnBackgroundColour(colour)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(parent, -1, wx.Bitmap(paths.icon_16x16.edit_rename, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((parent.height_element, parent.height_element))
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


    def open_dialog(self, event):
        """Open a special dialog for inputting a list of text values.

        @param event:   The wx event.
        @type event:    wx event
        """


        # Initialise the model selection window.
        win = String_list_window(name=self.name)

        # Set the model selector window selections.
        win.SetValue(self.GetValue())

        # Show the model selector window.
        if status.show_gui:
            win.ShowModal()
            win.Close()

        # Set the values.
        self.SetValue(win.GetValue())

        # Destroy the window.
        del win



class String_list_ctrl(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
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



class String_list_window(wx.Dialog):
    """The string list editor window."""

    # The window size.
    SIZE = (600, 600)

    # A border.
    BORDER = 10

    # Sizes.
    SIZE_BUTTON = (150, 33)

    def __init__(self, name=''):
        """Set up the string list editor window.

        @keyword name:  The name of the window.
        @type name:     str
        """

        # Store the args.
        self.name = name

        # The title of the dialog.
        title = "The list of %s" % name

        # Set up the dialog.
        wx.Dialog.__init__(self, None, id=-1, title=title)

        # Initialise some values
        width = self.SIZE[0] - 2*self.BORDER

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
        """Return the values as a list of strings.

        @return:    The list of values.
        @rtype:     list of str
        """

        # Init.
        values = []

        # Loop over the entries.
        for i in range(self.list.GetItemCount()):
            values.append(gui_to_str(self.list.GetItemText(i)))

        # Return the list.
        return values


    def SetValue(self, values):
        """Set up the list values.

        @param values:  The list of values to add to the list.
        @type values:   list of str
        """

        # Loop over the entries.
        for i in range(len(values)):
            self.list.InsertStringItem(i, str_to_gui(values[i]))


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
        self.list = String_list_ctrl(self)

        # Set the column title.
        title = "%s%s" % (upper(self.name[0]), self.name[1:])

        # Add a single column, full width.
        self.list.InsertColumn(0, title)
        self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        # Add the table to the sizer.
        sizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 0)


    def append_row(self, event):
        """Append a new row to the list.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The next index.
        next = self.list.GetItemCount()

        # Add a new empty row.
        self.list.InsertStringItem(next, '')


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
        self.list.DeleteAllItems()
