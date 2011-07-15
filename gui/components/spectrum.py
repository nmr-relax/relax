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
import wx
import wx.lib.buttons

# relaxGUI module imports.
from gui.misc import add_border
from gui import paths


class Spectra_list:
    """The GUI element for listing loaded spectral data."""

    # Class variables.
    col_label_width = 40
    col1_width = 160
    col2_width = 140

    def __init__(self, gui=None, parent=None, data=None, label=None, width=688, height=300, box=None, fn_add=None, buttons=True):
        """Build the spectral list GUI element.

        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword label:     The type of analysis.
        @type label:        str
        @keyword width:     The initial width of the GUI element.
        @type width:        int
        @keyword height:    The initial height of the GUI element.
        @type height:       int
        @keyword box:       The vertical box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        @keyword fn_add:    The function to execute when clicking on the 'Add' button.
        @type fn_add:       func
        @keyword buttons:   A flag which if True will display the buttons at the top.
        @type buttons:      bool
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent
        self.data = data
        self.label = label
        self.fn_add = fn_add

        # GUI variables.
        self.spacing = 5
        self.border = 5

        # The number of rows.
        self.num_rows = 50

        # A static box to hold all the widgets, and its sizer.
        stat_box = wx.StaticBox(self.parent, -1, "Spectra list")
        stat_box.SetFont(self.gui.font_subtitle)
        sub_sizer = wx.StaticBoxSizer(stat_box, wx.VERTICAL)

        # Add the sizer to the static box and the static box to the main box.
        box.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add a border.
        box_centre = add_border(sub_sizer, border=self.border)

        # Add buttons.
        if buttons:
            self.add_buttons(box_centre)

        # Add the grid.
        box_centre.AddSpacer(self.spacing)
        self.add_grid(box_centre)
        box_centre.AddSpacer(self.spacing)


    def resize(self, event):
        """Catch the resize to allow the grid to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The new grid size.
        x, y = event.GetSize()

        # The expandable column width.
        width = x - self.col_label_width - self.col1_width - self.col2_width - 20

        # Set the column sizes.
        self.grid.SetRowLabelSize(self.col_label_width)
        self.grid.SetColSize(0, width)
        self.grid.SetColSize(1, self.col1_width)
        self.grid.SetColSize(2, self.col2_width)

        # Continue with the normal resizing.
        event.Skip()


    def add_buttons(self, sizer):
        """Add the buttons for peak list manipulation.

        @param box:     The sizer element to pack the buttons into.
        @type box:      wx.BoxSizer instance
        """

        # A panel for the buttons (to allow for tooltips).
        panel = wx.Panel(self.parent, -1)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND, 0)

        # Button Sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(button_sizer)

        # Add button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(panel, -1, None, " Add")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.add, wx.BITMAP_TYPE_ANY))
        button.SetSize((80, 40))
        button_sizer.Add(button, 0, 0, 0)
        self.gui.Bind(wx.EVT_BUTTON, self.fn_add, button)
        button.SetToolTipString("Read a spectral data file.")


    def add_grid(self, sizer):
        """Add the grid for the peak list files and delay times.

        @param box:     The sizer element to pack the grid into.
        @type box:      wx.BoxSizer instance
        """

        # Grid of peak list file names and relaxation time.
        self.grid = wx.grid.Grid(self.parent, -1)

        # Create entries.
        self.grid.CreateGrid(self.num_rows, 3)

        # Create headers.
        self.grid.SetColLabelValue(0, "%s peak list" % self.label)
        self.grid.SetColLabelValue(1, "Relaxation delay [s]")
        self.grid.SetColLabelValue(2, "No. of cycles")

        # Properties.
        self.grid.SetDefaultCellFont(self.gui.font_normal)
        self.grid.SetLabelFont(self.gui.font_normal_bold)

        # Column properties.
        for i in range(self.grid.GetNumberRows()):
            # Row properties.
            self.grid.SetRowSize(i, 27)

        # No cell resizing allowed.
        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        # Bind some events.
        self.grid.Bind(wx.EVT_SIZE, self.resize)

        # Add grid to sizer, with spacing.
        sizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 0)


    def update_grid(self):
        """Update the grid, changing the relaxation delay times as needed."""

        # Loop over the rows.
        for i in range(self.grid.GetNumberRows()):
            # The number of cycles.
            ncyc = str(self.grid.GetCellValue(i, 2))

            # Update the relaxation time.
            if time != '' and ncyc not in ['', '0']:
                self.grid.SetCellValue(i, 1, str(int(ncyc) * time))

            # The relaxation time and number of cycles.
            relax_time = str(self.grid.GetCellValue(i, 1))

            # Clear the relaxation time if set to zero.
            if relax_time == '0.0':
                self.grid.SetCellValue(i, 1, '')
