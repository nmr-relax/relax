###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Module containing the classes for GUI components involving spectral data."""

# Python module imports.
from os import sep
import wx
import wx.lib.buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relaxGUI module imports.
from gui_bieri.controller import Redirect_text, Thread_container
from gui_bieri.derived_wx_classes import StructureTextCtrl
from gui_bieri.filedialog import multi_openfile, opendir
from gui_bieri.message import error_message
from gui_bieri import paths



class Peak_intensity:
    """The peak list selection class."""

    def __init__(self, gui=None, parent=None, data=None, label=None, width=688, height=300, box=None):
        """Build the peak list reading GUI element.

        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword parent:    The parent GUI element that this is to be attached to.
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword label:     The type of analysis.
        @type label:        str
        @keyword width:     The initial width of the GUI element.
        @type width:        int
        @keyword height:    The initial height of the GUI element.
        @type height:       int
        @keyword box:       The box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent
        self.data = data
        self.label = label
        self.box = box

        # Some fixed sizes.
        button_width  = 80
        button_height = 40
        panel_width = width - button_width - 5
        time_width = 150
        time_height = 20
        time_field_width  = 80
        time_field_height = 20
        file_width = panel_width - time_width
        file_height = 20

        # The number of peak list elements (update the data store to match).
        self.peak_list_count = 14
        self.data.file_list = [''] * self.peak_list_count
        self.data.relax_times = [''] * self.peak_list_count

        # The background panel (only used for layout purposes).
        panel_back = wx.Panel(self.parent, -1)
        panel_back.SetMinSize((width, 5))

        # A Horizontal layout sizer (to separate the buttons from the grid).
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        # The panel for both the buttons and the grid.
        panel_main = wx.Panel(self.parent, -1)
        panel_main.SetMinSize((width, height))
        panel_main.SetBackgroundColour(wx.Colour(192, 192, 192))
        panel_main.SetSizer(sizer_main)

        # A Vertical layout sizer (for the buttons).
        sizer_buttons = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(sizer_buttons, 1, wx.EXPAND, 0)

        # The add button.
        button = wx.BitmapButton(panel_main, -1, bitmap=wx.Bitmap(paths.icon_16x16.add, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((button_width, button_height))
        button.SetToolTipString("Add new peak lists")
        self.gui.Bind(wx.EVT_BUTTON, self.peak_list_add_action, button)
        sizer_buttons.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # The remove single item button.
        button = wx.BitmapButton(panel_main, -1, bitmap=wx.Bitmap(paths.icon_16x16.remove, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((button_width, button_height))
        button.SetToolTipString("Removed selected items (disabled)")
        sizer_buttons.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # The cancel button.
        button = wx.BitmapButton(panel_main, -1, bitmap=wx.Bitmap(paths.icon_16x16.cancel, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((button_width, button_height))
        button.SetToolTipString("Clear the list")
        self.gui.Bind(wx.EVT_BUTTON, self.empty_list, button)
        sizer_buttons.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # The panel for the grid.
        panel_grid = wx.Panel(panel_main, -1)
        panel_grid.SetMinSize((width-button_width-5, height))
        panel_grid.SetBackgroundColour(wx.Colour(192, 192, 192))
        sizer_main.Add(panel_grid, 0, wx.EXPAND|wx.SHAPED, 0)

        # A grid sizer for the peak list info.
        sizer_grid = wx.FlexGridSizer(10, 2, 0, 0)

        # The file title.
        label = wx.StaticText(panel_grid, -1, "R1 relaxation peak list")
        label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        label.SetMinSize((file_width, file_height))
        sizer_grid.Add(label, 0, wx.ADJUST_MINSIZE, 0)

        # The time title.
        label = wx.StaticText(panel_grid, -1, "Relaxation time [s]")
        label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_grid.Add(label, 0, wx.ADJUST_MINSIZE, 0)

        # Build the grid of file names and relaxation times.
        self.field_rx_list = []
        self.field_rx_time = []
        for i in range(1, self.peak_list_count+1):
            # The peak list file name GUI elements.
            self.field_rx_list.append(wx.StaticText(panel_grid, -1, ""))
            sizer_grid.Add(self.field_rx_list[-1], 0, wx.ADJUST_MINSIZE, 0)

            # The time GUI elements.
            self.field_rx_time.append(wx.TextCtrl(panel_grid, -1, ""))
            self.field_rx_time[-1].SetMinSize((time_field_width, time_field_height))
            sizer_grid.Add(self.field_rx_time[-1], 0, wx.ADJUST_MINSIZE, 0)

        # Place the grid inside the panel.
        panel_grid.SetSizer(sizer_grid)

        # Add the panels to the box (this order adds a spacer at the top).
        self.box.Add(panel_back, 0, wx.EXPAND|wx.SHAPED, 0)
        self.box.Add(panel_main, 0, wx.EXPAND|wx.SHAPED, 0)


    def count_peak_lists(self):
        """Count the number of peak lists already loaded.

        @return:    The number of loaded peak lists.
        @rtype:     int
        """

        # Loop over the GUI elements.
        count = 0
        for i in range(self.peak_list_count):
            # Stop when blank.
            if self.data.file_list[i] == '':
                break

            # Increment.
            count = count + 1

        # Return the count.
        return count


    def empty_list(self, event):
        """Remove all peak lists and times.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Reset the data storage.
        self.data.file_list = [''] * self.peak_list_count
        self.data.relax_times = [''] * self.peak_list_count

        # Refresh the grid.
        self.refresh_peak_list_display()

        # Terminate the event.
        event.Skip()


    def peak_list_add_action(self, event):
        """Add additional peak lists.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current number of peak lists.
        count = self.count_peak_lists()

        # Full!
        if count >= self.peak_list_count:
            # Show an error dialog.
            error_message("No more peak lists can be added, the maximum number has been reached.")

            # Terminate the event and finish.
            event.Skip()
            return

        # Open the file selection dialog.
        files = multi_openfile(msg='Select %s peak list file' % self.label, filetype='*.*', default='all files (*.*)|*.*')

        # No files selected, so terminate the event and exit.
        if not files:
            event.Skip()
            return

        # Too many files selected.
        if len(files) + count > self.peak_list_count:
            # Show an error dialog.
            error_message("Too many peak lists selected, the maximum number has been exceeded.")

            # Terminate the event and finish.
            event.Skip()
            return

        # Store the files.
        for i in range(len(files)):
            self.data.file_list[count+i] = str(files[i])

        # Sync any set times and refresh the GUI element.
        self.sync_ds(upload=True)
        self.refresh_peak_list_display()

        # Terminate the event.
        event.Skip()


    def refresh_peak_list_display(self):
        """Refresh the display of peak lists."""

        # Loop over all elements.
        for i in range(self.peak_list_count):
            # The file names.
            self.field_rx_list[i].SetLabel(self.data.file_list[i])

            # The times.
            self.field_rx_time[i].SetValue(self.data.relax_times[i])


    def sync_ds(self, upload=False):
        """Synchronise the rx analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The peak lists and relaxation times.
        if upload:
            for i in range(self.peak_list_count):
                # Set the relaxation time.
                self.data.relax_times[i] = str(self.field_rx_time[i].GetValue())
        else:
            for i in range(self.peak_list_count):
                # The file name.
                self.field_rx_list[i].SetLabel(self.data.file_list[i])

                # The relaxation time.
                self.field_rx_time[i].SetValue(str(self.data.relax_times[i]))
