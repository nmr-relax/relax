###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
from gui.controller import Redirect_text, Thread_container
from gui.derived_wx_classes import StructureTextCtrl
from gui.filedialog import multi_openfile, opendir, openfile
from gui.message import error_message
from gui import paths



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

        # The number of rows.
        self.num_rows = 50

        # Sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Button Sizer
        button_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add peaklist button
        add_pkl = wx.BitmapButton(self.parent, -1, bitmap=wx.Bitmap(paths.icon_16x16.add, wx.BITMAP_TYPE_ANY))
        add_pkl.SetMinSize((50, 50))
        self.gui.Bind(wx.EVT_BUTTON, self.load_peaklist, add_pkl)
        button_sizer.Add(add_pkl, 0, wx.ADJUST_MINSIZE, 0)

        # Add VD list import
        if self.label =='R1':
            add_vd = wx.Button(self.parent, -1, "+VD")
            add_vd.SetToolTipString("Add VD (variable delay) list to automatically fill in R1 relaxation times.")
            add_vd.SetMinSize((50, 50))
            self.gui.Bind(wx.EVT_BUTTON, self.load_delay, add_vd)
            button_sizer.Add(add_vd, 0, wx.ADJUST_MINSIZE, 0)

        # Add Vc list import
        if self.label =='R2':
            add_vc = wx.Button(self.parent, -1, "+VC")
            add_vc.SetToolTipString("Add VC (variable counter) list to automatically fill in R2 relaxation times.")
            add_vc.SetMinSize((50, 50))
            button_sizer.Add(add_vc, 0, wx.ADJUST_MINSIZE, 0)

            # Time of counter
            self.vc_time = wx.TextCtrl(self.parent, -1, "0")
            self.vc_time.SetToolTipString("Time of counter loop in seconds.")
            self.vc_time.SetMinSize((50, 20))
            self.vc_time.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            button_sizer.Add(self.vc_time, 0, 0 ,0)

            # Action of Button
            self.gui.Bind(wx.EVT_BUTTON, lambda evt, vc=True: self.load_delay(evt, vc), add_vc)

        # Pack buttons
        sizer.Add(button_sizer, 0, 0, 0)

        # Grid of peak list file names and relaxation time
        self.peaklist = wx.grid.Grid(self.parent, -1, size=(1, 300))

        # Create entries
        self.peaklist.CreateGrid(self.num_rows, 2)

        # Create headers
        self.peaklist.SetColLabelValue(0, "%s Peak lists" %self.label)
        self.peaklist.SetColSize(0, 370)
        self.peaklist.SetColLabelValue(1, "Relaxation time [s]")
        self.peaklist.SetColSize(1, 150)

        # Add grid to sizer
        sizer.Add(self.peaklist, -1, wx.EXPAND, 0)

        # Pack box
        box.Add(sizer, 0, wx.EXPAND, 0)


    def load_delay(self, event, vc=False):
        """The variable delay list loading GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # VD
        
        # VC time is not a number
        if vc:
            try:
                vc_factor = float(self.vc_time.GetValue())
            except:
                error_message('VC time is not a number.')
                return

        # VD
        else:
            vc_factor = 1

        # The file
        filename = openfile(msg='Select file.', filetype='*.*', default='all files (*.*)|*')

        # Abort if nothing selected
        if not filename:
            return

        # Open the file
        file = open(filename, 'r')

        # Read entries
        index = 0
        for line in file:
            # Evaluate if line is a number
            try:
                t = float(line.replace('/n', ''))
            except:
                continue

            # Write delay to peak list grid
            self.peaklist.SetCellValue(index, 1, str(t*vc_factor))

            # Next peak list
            index = index + 1

            # Too many entries in VD list
            if index == self.num_rows:
                error_message('Too many entries in list.')
                return


    def load_peaklist(self, event):
        """Function to load peak lists to data grid.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open files
        files = multi_openfile(msg='Select %s peak list file' % self.label, filetype='*.*', default='all files (*.*)|*')

        # Abort if no files have been selected
        if not files:
            return

        # Fill values in data grid
        index = 0
        for i in range(self.num_rows):
            # Add entry if nothing is filled in already
            if str(self.peaklist.GetCellValue(i, 0)) == '':
                # Write peak file
                self.peaklist.SetCellValue(i, 0, str(files[index]))

                # Next file
                index = index + 1

                # Stop if no files left
                if index == len(files):
                    break

        # Error message if not all files were loaded
        if index < (len(files)-1):
                error_message('Not all files could be loaded.')


    def sync_ds(self, upload=False):
        """Synchronise the rx analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # Sync the peaklists and relaxation times.
        self.sync_peaklist()

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


    def sync_peaklist(self):
        """Fucntion to read and store peaklists and relaxation times."""

        # Containers
        self.peakfiles = []
        self.rxtimes = []

        # read entries in data grid
        for i in range(self.num_rows):
            # Store peaklist
            self.peakfiles.append(str(self.peaklist.GetCellValue(i, 0)))

            # Store relaxation time
            self.rxtimes.append(str(self.peaklist.GetCellValue(i, 1)))
