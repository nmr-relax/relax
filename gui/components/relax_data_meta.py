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
"""Module containing the classes for GUI components involving relaxation data."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from graphics import fetch_icon
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.components.menu import build_menu_item
from gui.fonts import font
from gui.misc import add_border
from gui.string_conv import float_to_gui, gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Relax_data_meta_list:
    """The GUI element for listing loaded relaxation data."""

    # Some IDs for the menu entries.
    MENU_RELAX_DATA_DISPLAY = wx.NewId()
    MENU_RELAX_DATA_PEAK_INTENSITY_TYPE = wx.NewId()
    MENU_RELAX_DATA_TEMP_CALIBRATION = wx.NewId()
    MENU_RELAX_DATA_TEMP_CONTROL = wx.NewId()


    def __init__(self, parent=None, box=None, id=None, stretch=False):
        """Build the relaxation data list GUI element.

        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword box:       The vertical box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        @keyword id:        A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:           str
        @keyword stretch:   A flag which if True will allow the static box to stretch with the window.
        @type stretch:      bool
        """

        # Store the arguments.
        self.parent = parent
        self.stretch = stretch

        # Stretching.
        self.proportion = 0
        if stretch:
            self.proportion = 1

        # GUI variables.
        self.spacing = 5
        self.border = 5

        # First create a panel.
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

        # Initialise the element.
        box_centre.AddSpacer(self.spacing)
        self.init_element(box_centre)

        # Build the element.
        self.build_element()

        # Initialise observer name.
        self.name = 'relaxation metadata list: %s' % id

        # Register the element for updating when a user function completes.
        self.observer_register()


    def Enable(self, enable=True):
        """Enable or disable the element.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """


    def action_relax_data_display(self, event):
        """Launch the relax_data.display user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # Launch the dialog.
        uf_store['relax_data.display'](wx_parent=self.parent, ri_id=id)


    def action_relax_data_peak_intensity_type(self, event):
        """Launch the relax_data.peak_intensity_type user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current type.
        type = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'peak_intensity_type') and id in cdp.exp_info.peak_intensity_type.keys():
            type = cdp.exp_info.peak_intensity_type[id]

        # Launch the dialog.
        if type == None:
            uf_store['relax_data.peak_intensity_type'](wx_parent=self.parent, ri_id=id)
        else:
            uf_store['relax_data.peak_intensity_type'](wx_parent=self.parent, ri_id=id, type=type)


    def action_relax_data_temp_calibration(self, event):
        """Launch the relax_data.temp_calibration user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current method.
        method = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_calibration') and id in cdp.exp_info.temp_calibration.keys():
            method = cdp.exp_info.temp_calibration[id]

        # Launch the dialog.
        if method == None:
            uf_store['relax_data.temp_calibration'](wx_parent=self.parent, ri_id=id)
        else:
            uf_store['relax_data.temp_calibration'](wx_parent=self.parent, ri_id=id, method=method)


    def action_relax_data_temp_control(self, event):
        """Launch the relax_data.temp_control user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current method.
        method = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_control') and id in cdp.exp_info.temp_control.keys():
            method = cdp.exp_info.temp_control[id]

        # Launch the dialog.
        if method == None:
            uf_store['relax_data.temp_control'](wx_parent=self.parent, ri_id=id)
        else:
            uf_store['relax_data.temp_control'](wx_parent=self.parent, ri_id=id, method=method)


    def build_element(self):
        """Build the relaxation data listing grid."""

        # Execution lock, so do nothing.
        if status.exec_lock.locked():
            return

        # Build the GUI element in a thread safe way.
        wx.CallAfter(self.build_element_safe)


    def build_element_safe(self):
        """Build the spectra listing GUI element in a thread safe wx.CallAfter call."""

        # First freeze the element, so that the GUI element doesn't update until the end.
        self.element.Freeze()

        # Update the label.
        self.set_box_label()

        # Delete the previous data.
        self.element.DeleteAllItems()

        # Expand the number of rows to match the number of relaxation IDs, and add the IDs.
        n = 0
        if hasattr(cdp, 'ri_ids'):
            # The number of IDs.
            n = len(cdp.ri_ids)

            # Add all the data.
            for i in range(n):
                # Set the IDs.
                id = cdp.ri_ids[i]
                self.element.InsertStringItem(i, str_to_gui(id))

                # Set the peak intensity types.
                if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'peak_intensity_type') and id in cdp.exp_info.peak_intensity_type.keys():
                    self.element.SetStringItem(i, 1, str_to_gui(cdp.exp_info.peak_intensity_type[id]))

                # Set the temperature calibration methods.
                if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_calibration') and id in cdp.exp_info.temp_calibration.keys():
                    self.element.SetStringItem(i, 2, str_to_gui(cdp.exp_info.temp_calibration[id]))

                # Set the temperature control methods.
                if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_control') and id in cdp.exp_info.temp_control.keys():
                    self.element.SetStringItem(i, 3, str_to_gui(cdp.exp_info.temp_control[id]))

        # Size the columns.
        self.size_cols()

        # Post a size event to get the scroll panel to update correctly.
        event = wx.PyCommandEvent(wx.EVT_SIZE.typeId, self.parent.GetId())
        wx.PostEvent(self.parent.GetEventHandler(), event)

        # Set the minimum height.
        if not self.stretch:
            head = self.height_char + 10
            centre = (self.height_char + 6) * n
            foot = wx.SystemSettings_GetMetric(wx.SYS_HSCROLL_Y)
            height = head + centre + foot
            self.element.SetMinSize((-1, height))
            self.element.Layout()

        # Unfreeze.
        self.element.Thaw()


    def delete(self):
        """Unregister the class."""

        # Unregister the observer methods.
        self.observer_register(remove=True)


    def init_element(self, sizer):
        """Initialise the GUI element for the relaxation data listing.

        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.BoxSizer instance
        """

        # List of relaxation data.
        self.element = wx.ListCtrl(self.panel, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Initialise to 4 columns.
        self.element.InsertColumn(0, str_to_gui("Relaxation data ID"))
        self.element.InsertColumn(1, str_to_gui("Peak intensity type"))
        self.element.InsertColumn(2, str_to_gui("Temperature calibration"))
        self.element.InsertColumn(3, str_to_gui("Temperature control"))

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
        """Determine if the data input is complete.

        @return:    The answer to the question.
        @rtype:     bool
        """

        # The number of IDs.
        n = len(cdp.ri_ids)

        # Add all the data.
        for i in range(n):
            # The ID.
            id = cdp.ri_ids[i]

            # Check the peak intensity types.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'peak_intensity_type') or not id in cdp.exp_info.peak_intensity_type.keys():
                return False


            # Check the temperature calibration methods.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'temp_calibration') or not id in cdp.exp_info.temp_calibration.keys():
                return False

            # Check the temperature control methods.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'temp_control') or not id in cdp.exp_info.temp_control.keys():
                return False

        # Data input is complete!
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

        # Execution lock, so do nothing.
        if status.exec_lock.locked():
            return

        # Initialise the menu.
        menu = wx.Menu()

        # Add some menu items for the spin user functions.
        menu.AppendItem(build_menu_item(menu, id=self.MENU_RELAX_DATA_DISPLAY, text="Dis&play the relaxation data", icon=fetch_icon(uf_info.get_uf('relax_data.display').gui_icon)))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_RELAX_DATA_PEAK_INTENSITY_TYPE, text="Set the peak &intensity type", icon=fetch_icon(uf_info.get_uf('relax_data.peak_intensity_type').gui_icon)))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_RELAX_DATA_TEMP_CALIBRATION, text="Set the temperature &calibration", icon=fetch_icon(uf_info.get_uf('relax_data.temp_calibration').gui_icon)))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_RELAX_DATA_TEMP_CONTROL, text="Set the temperature c&ontrol", icon=fetch_icon(uf_info.get_uf('relax_data.temp_control').gui_icon)))

        # Bind clicks.
        self.element.Bind(wx.EVT_MENU, self.action_relax_data_display, id=self.MENU_RELAX_DATA_DISPLAY)
        self.element.Bind(wx.EVT_MENU, self.action_relax_data_peak_intensity_type, id=self.MENU_RELAX_DATA_PEAK_INTENSITY_TYPE)
        self.element.Bind(wx.EVT_MENU, self.action_relax_data_temp_calibration, id=self.MENU_RELAX_DATA_TEMP_CALIBRATION)
        self.element.Bind(wx.EVT_MENU, self.action_relax_data_temp_control, id=self.MENU_RELAX_DATA_TEMP_CONTROL)

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

        # Determine if the data input is complete.
        label = "Relaxation data metadata "
        if self.is_complete():
            label += "(complete)"
        else:
            label += "(incomplete)"

        # Set the label.
        self.data_box.SetLabel(label)


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
