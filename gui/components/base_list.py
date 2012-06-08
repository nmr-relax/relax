###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""Module containing the base GUI element for listing things."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.components.menu import build_menu_item
from gui.fonts import font
from gui.misc import add_border
from gui.string_conv import str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Base_list(object):
    """The GUI element for listing the software used in the analysis."""

    def __init__(self, gui=None, parent=None, box=None, id=None, stretch=False, button_placement='default'):
        """Build the base list GUI element.

        @keyword gui:               The main GUI object.
        @type gui:                  wx.Frame instance
        @keyword parent:            The parent GUI element that this is to be attached to.
        @type parent:               wx object
        @keyword box:               The box sizer to pack this GUI component into.
        @type box:                  wx.BoxSizer instance
        @keyword id:                A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:                   str
        @keyword stretch:           A flag which if True will allow the static box to stretch with the window.
        @type stretch:              bool
        @keyword button_placement:  Override the button visibility and placement.  The value of 'default' will leave the buttons at the default setting.  The value of 'top' will place the buttons at the top, 'bottom' will place them at the bottom, and None will turn off the buttons.
        @type button_placement:     str or None
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent
        self.stretch = stretch

        # Variables to be overridden.
        self.title = ""
        self.spacing = 5
        self.border = 5
        self.observer_base_name = None
        self.columns = []
        self.button_placement = None
        self.button_size = (80, 40)
        self.button_info = []
        self.popup_menus = []

        # Override these base values.
        self.setup()

        # Button placement second override on initialisation.
        if button_placement != 'default':
            self.button_placement = button_placement

        # Stretching.
        self.proportion = 0
        if stretch:
            self.proportion = 1

        # First create a panel (to allow for tooltips on the buttons).
        self.panel = wx.Panel(self.parent)
        box.Add(self.panel, self.proportion, wx.ALL|wx.EXPAND, 0)

        # Add a sizer to the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(panel_sizer)

        # A static box to hold all the widgets, and its sizer.
        self.data_box = wx.StaticBox(self.panel, -1)
        self.set_box_label()
        self.data_box.SetFont(font.subtitle)
        sub_sizer = wx.StaticBoxSizer(self.data_box, wx.VERTICAL)

        # Add the sizer to the static box and the static box to the main box.
        panel_sizer.Add(sub_sizer, self.proportion, wx.ALL|wx.EXPAND, 0)

        # Add a border.
        box_centre = add_border(sub_sizer, border=self.border)

        # Add buttons to the top.
        if self.button_placement == 'top':
            self.add_buttons(box_centre)

        # Initialise the element.
        box_centre.AddSpacer(self.spacing)
        self.init_element(box_centre)

        # Build the element.
        self.build_element()

        # Add buttons to the bottom.
        if self.button_placement == 'bottom':
            self.add_buttons(box_centre)

        # Initialise observer name.
        if self.observer_base_name:
            self.name = '%s: %s' % (self.observer_base_name, id)
        else:
            self.name = id

        # Register the element for updating when a user function completes.
        self.observer_register()


    def Enable(self, enable=True):
        """Enable or disable the element.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """

        # Call the buttons' methods.
        for i in range(len(self.button_info)):
            # Get the button.
            button = getattr(self, self.button_info[i]['object'])

            # Call the botton's method.
            button.Enable(enable)


    def add_buttons(self, sizer):
        """Add the buttons for manipulating the data.

        @param sizer:   The sizer element to pack the buttons into.
        @type sizer:    wx.BoxSizer instance
        """

        # Button Sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Loop over the buttons.
        for i in range(len(self.button_info)):
            # The button.
            button = wx.lib.buttons.ThemedGenBitmapTextButton(self.panel, -1, None, self.button_info[i]['label'])
            button.SetBitmapLabel(wx.Bitmap(self.button_info[i]['icon']))

            # Format.
            button.SetFont(font.normal)
            button.SetMinSize(self.button_size)

            # Add to the sizer.
            button_sizer.Add(button, 0, 0, 0)

            # Bind the method.
            self.parent.Bind(wx.EVT_BUTTON, self.button_info[i]['method'], button)

            # Set the tooltip.
            button.SetToolTipString(self.button_info[i]['tooltip'])

            # Store as a class object.
            setattr(self, self.button_info[i]['object'], button)


    def build_element(self):
        """Build the grid."""

        # Execution lock, so do nothing.
        if status.exec_lock.locked():
            return

        # Build the GUI element in a thread safe way.
        wx.CallAfter(self.build_element_safe)


    def build_element_safe(self):
        """Build the spectra listing GUI element in a thread safe wx.CallAfter call."""

        # First freeze the element, so that the GUI element doesn't update until the end.
        self.element.Freeze()

        # Update the label if needed.
        self.set_box_label()

        # Delete the previous data.
        self.element.DeleteAllItems()

        # Update the data.
        self.update_data()

        # Size the columns.
        self.size_cols()

        # Post a size event to get the scroll panel to update correctly.
        event = wx.PyCommandEvent(wx.EVT_SIZE.typeId, self.parent.GetId())
        wx.PostEvent(self.parent.GetEventHandler(), event)

        # Set the minimum height.
        if not self.stretch:
            # The number of rows.
            n = self.element.GetItemCount()

            # Size of the header, plus a bit.
            head = self.height_char + 10

            # Size of the table central element.
            centre = (self.height_char + 6) * n 

            # Size of the scrollbar for the end of the table.
            foot = wx.SystemSettings_GetMetric(wx.SYS_HSCROLL_Y)

            # Sum.
            height = head + centre + foot

            # Set the minimum size, and force a redraw.
            self.element.SetMinSize((-1, height))
            self.element.Layout()

        # Unfreeze.
        self.element.Thaw()


    def init_element(self, sizer):
        """Initialise the GUI element.

        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.BoxSizer instance
        """

        # The list.
        self.element = wx.ListCtrl(self.panel, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Initialise the columns.
        for i in range(len(self.columns)):
            self.element.InsertColumn(i, str_to_gui(self.columns[i]))

        # Properties.
        self.element.SetFont(font.normal)

        # Store the base heights.
        self.height_char = self.element.GetCharHeight()

        # Bind some events.
        self.element.Bind(wx.EVT_SIZE, self.resize)
        self.element.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.on_right_click)  # For wxMSW!
        self.element.Bind(wx.EVT_RIGHT_UP, self.on_right_click)   # For wxGTK!

        # Add list to sizer.
        sizer.Add(self.element, self.proportion, wx.ALL|wx.EXPAND, 0)


    def is_complete(self):
        """Base method which always returns True.

        @return:    The answer to the question.
        @rtype:     bool
        """

        # Assume everything is complete.
        return True


    def observer_register(self, remove=False):
        """Register and unregister methods with the observer objects.

        @keyword remove:    If set to True, then the methods will be unregistered.
        @type remove:       False
        """

        # Register.
        if not remove:
            status.observers.gui_uf.register(self.name, self.build_element)

        # Unregister.
        else:
            status.observers.gui_uf.unregister(self.name)


    def on_right_click(self, event):
        """Pop up menu for the right click.

        @param event:   The wx event.
        @type event:    wx event
        """

        # No popup menus defined.
        if self.popup_menus == []:
            return

        # Execution lock, so do nothing.
        if status.exec_lock.locked():
            return

        # Initialise the menu.
        menu = wx.Menu()

        # Loop over the menu items.
        for i in range(len(self.popup_menus)):
            # Alias.
            info = self.popup_menus[i]

            # Add the menu item.
            menu.AppendItem(build_menu_item(menu, id=info['id'], text=info['text'], icon=info['icon']))

            # Bind clicks.
            self.element.Bind(wx.EVT_MENU, info['method'], id=info['id'])

        # Pop up the menu.
        if status.show_gui:
            self.element.PopupMenu(menu)
            menu.Destroy()


    def resize(self, event):
        """Catch the resize to allow the element to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def set_box_label(self):
        """Set the label of the StaticBox."""

        # Set the label.
        self.data_box.SetLabel(self.title)


    def size_cols(self):
        """Set the column sizes."""

        # The element size.
        x, y = self.element.GetSize()

        # Number of columns.
        n = self.element.GetColumnCount()

        # Set to equal sizes.
        if n == 0:
            width = x
        else:
            width = int(x / n)

        # Set the column sizes.
        for i in range(n):
            self.element.SetColumnWidth(i, width)
