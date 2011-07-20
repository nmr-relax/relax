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

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from gui.misc import add_border, float_to_gui
from gui import paths


class Spectra_list:
    """The GUI element for listing loaded spectral data."""

    # Class variables.
    col_label_width = 40

    def __init__(self, gui=None, parent=None, box=None, id=None, fn_add=None, buttons=True):
        """Build the spectral list GUI element.

        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword box:       The vertical box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        @keyword id:        A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:           str
        @keyword fn_add:    The function to execute when clicking on the 'Add' button.
        @type fn_add:       func
        @keyword buttons:   A flag which if True will display the buttons at the top.
        @type buttons:      bool
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent
        self.fn_add = fn_add

        # GUI variables.
        self.spacing = 5
        self.border = 5

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

        # Initialise the grid.
        box_centre.AddSpacer(self.spacing)
        self.init_grid(box_centre)
        box_centre.AddSpacer(self.spacing)

        # Build the grid.
        self.build_grid()

        # Initialise observer name.
        self.name = 'spectra list: %s' % id

        # Register the grid for updating when a user function completes.
        status.observers.uf_gui.register(self.name, self.build_grid)


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


    def build_grid(self):
        """Build the spectra listing grid."""

        # First freeze the grid, so that the GUI element doesn't update until the end.
        self.grid.Freeze()

        # Initialise the column index for the data.
        index = 1

        # Delete the rows and columns (leaving one row and column).
        self.grid.DeleteRows(numRows=self.grid.GetNumberRows()-1)
        self.grid.DeleteCols(numCols=self.grid.GetNumberCols()-1)

        # Expand the number of rows to match the number of spectrum IDs, and add the IDs.
        if hasattr(cdp, 'spectrum_ids'):
            # The number of IDs.
            n = len(cdp.spectrum_ids)

            # Append the appropriate number of rows.
            self.grid.AppendRows(numRows=n-1)

            # Set the IDs.
            for i in range(n):
                self.grid.SetCellValue(i, 0, cdp.spectrum_ids[i])

        # Set the headers.
        self.grid.SetColLabelValue(0, "Spectrum ID string")

        # The NOE spectrum type.
        if self.noe_spectrum_type(index):
            index += 1

        # The relaxation times.
        if self.relax_times(index):
            index += 1

        # Set the grid properties once finalised.
        for i in range(self.grid.GetNumberRows()):
            # Row properties.
            self.grid.SetRowSize(i, 27)

            # Loop over the columns.
            for j in range(self.grid.GetNumberCols()):
                # Cell properties.
                self.grid.SetReadOnly(i, j)

        # Size the columns.
        self.size_cols()

        # Unfreeze.
        self.grid.Thaw()


    def delete(self):
        """Unregister the class."""

        # Unregister the class.
        status.observers.uf_gui.unregister(self.name)


    def init_grid(self, sizer):
        """Initialise the grid for the spectra listing.

        @param box:     The sizer element to pack the grid into.
        @type box:      wx.BoxSizer instance
        """

        # Grid of peak list file names and relaxation time.
        self.grid = wx.grid.Grid(self.parent, -1)

        # Initialise to a single row and column.
        self.grid.CreateGrid(1, 1)

        # Properties.
        self.grid.SetDefaultCellFont(self.gui.font_normal)
        self.grid.SetLabelFont(self.gui.font_normal_bold)

        # Set the row label widths.
        self.grid.SetRowLabelSize(self.col_label_width)

        # No cell resizing allowed.
        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        # Bind some events.
        self.grid.Bind(wx.EVT_SIZE, self.resize)

        # Add grid to sizer, with spacing.
        sizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 0)


    def resize(self, event):
        """Catch the resize to allow the grid to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def noe_spectrum_type(self, index):
        """Add the NOE spectral type info to the grid.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if a spectrum type exists, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'spectrum_type') or not len(cdp.spectrum_type):
            return False

        # Append a column.
        self.grid.AppendCols(numCols=1)

        # Set the column heading.
        self.grid.SetColLabelValue(index, "NOE spectrum type")

        # Translation table.
        table = {
            'sat': 'Saturated',
            'ref': 'Reference'
        }

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.spectrum_type.keys():
                continue

            # Set the value.
            self.grid.SetCellValue(i, index, table[cdp.spectrum_type[cdp.spectrum_ids[i]]])

        # Successful.
        return True


    def relax_times(self, index):
        """Add the relaxation delay time info to the grid.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if relaxation times exist, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'relax_times') or not len(cdp.relax_times):
            return False

        # Append a column.
        self.grid.AppendCols(numCols=1)

        # Set the column heading.
        self.grid.SetColLabelValue(index, "Delay times")

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.relax_times.keys():
                continue

            # Set the value.
            self.grid.SetCellValue(i, index, float_to_gui(cdp.relax_times[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def size_cols(self):
        """Set the column sizes."""

        # The grid size.
        x, y = self.grid.GetSize()

        # The expandable column width.
        width = x - self.col_label_width - 20

        # Number of columns.
        n = self.grid.GetNumberCols()

        # Set to equal sizes.
        width = int(width / n)

        # Set the column sizes.
        for i in range(n):
            self.grid.SetColSize(i, width)
