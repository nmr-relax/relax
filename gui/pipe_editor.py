###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""The pipe editor GUI element."""

# Python module imports.
import wx

# relax module imports.
from generic_fns.pipes import cdp_name, delete, get_type, pipe_names, switch
from status import Status; status = Status()

# relax GUI module imports.
from gui.components.menu import build_menu_item
from gui.message import question
from gui.misc import add_border, gui_to_str, str_to_gui
from gui.paths import icon_16x16, icon_22x22, WIZARD_IMAGE_PATH


class Pipe_editor(wx.Frame):
    """The pipe editor window object."""

    def __init__(self, gui=None, size_x=800, size_y=500, border=10):
        """Set up the relax controller frame.
        
        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword size_x:    The initial and minimum width of the window.
        @type size_x:       int
        @keyword size_y:    The initial and minimum height of the window.
        @type size_y:       int
        @keyword border:    The size of the internal border of the window.
        @type border:       int
        """

        # Store the args.
        self.gui = gui
        self.border = border

        # Create GUI elements
        wx.Frame.__init__(self, None, id=-1, title="Data pipe editor")

        # Initialise some data.
        self.width_col_label = 40

        # Set the normal and minimum window sizes.
        self.SetMinSize((size_x, size_y))
        self.SetSize((size_x, size_y))

        # The main box sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=border, packing=wx.VERTICAL)

        # Add the contents.
        sizer.AddSpacer(10)
        self.add_logo(sizer)
        sizer.AddSpacer(20)
        self.add_buttons(sizer)
        sizer.AddSpacer(10)
        self.add_table(sizer)

        # Bind some events.
        self.grid.Bind(wx.EVT_SIZE, self.resize)
        self.Bind(wx.EVT_CLOSE, self.handler_close)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.menu)

        # Centre the frame.
        self.Centre()

        # Update the grid.
        self.update_grid()

        # Register the grid for updating when a user function completes.
        status.observers.uf_gui.register('pipe editor', self.update_grid)
        status.observers.pipe_switch.register('pipe editor', self.update_grid)


    def menu(self, event):
        """The pop up menu.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the row.
        row = event.GetRow()

        # Get the name of the data pipe.
        self.selected_pipe = gui_to_str(self.grid.GetCellValue(0, row))

        # No data pipe.
        if not self.selected_pipe:
            return

        # Initialise the menu.
        menu = wx.Menu()

        # Menu entry:  delete the data pipe.
        menu.AppendItem(build_menu_item(menu, parent=self, text="&Delete the pipe", icon=icon_16x16.remove, fn=self.pipe_delete))
 
        # Menu entry:  switch to this data pipe.
        menu.AppendItem(build_menu_item(menu, parent=self, text="&Switch to this pipe", icon=icon_16x16.pipe_switch, fn=self.pipe_switch))
 
        # Show the menu.
        self.PopupMenu(menu)

        # Kill the menu once done.
        menu.Destroy()


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   The sizer element to pack the buttons into.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # The create button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Create")
        button.SetBitmapLabel(wx.Bitmap(icon_22x22.add, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Create a new data pipe.")
        button_sizer.Add(button, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.create, button)

        # The copy button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Copy")
        button.SetBitmapLabel(wx.Bitmap(icon_22x22.copy, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Copy a data pipe.")
        button_sizer.Add(button, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.copy, button)

        # The delete button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Delete")
        button.SetBitmapLabel(wx.Bitmap(icon_22x22.list_remove, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Delete a data pipe.")
        button_sizer.Add(button, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.delete, button)

        # The switch button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Switch")
        button.SetBitmapLabel(wx.Bitmap(icon_22x22.pipe_switch, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Switch data pipes.")
        button_sizer.Add(button, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.switch, button)


    def add_logo(self, box):
        """Add the logo to the sizer.

        @param sizer:   The sizer element to pack the logo into.
        @type sizer:    wx.Sizer instance
        """

        # The pipe logo.
        logo = wx.StaticBitmap(self, -1, wx.Bitmap(WIZARD_IMAGE_PATH+'pipe_200x90.png', wx.BITMAP_TYPE_ANY))

        # Pack the logo.
        box.Add(logo, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)


    def add_table(self, sizer):
        """Add the table to the sizer.

        @param sizer:   The sizer element to pack the table into.
        @type sizer:    wx.Sizer instance
        """

        # Grid of all data pipes.
        self.grid = wx.grid.Grid(self, -1)

        # Initialise to a single row and 4 columns.
        self.grid.CreateGrid(1, 4)

        # Set the headers.
        self.grid.SetColLabelValue(0, "Data pipe")
        self.grid.SetColLabelValue(1, "Type")
        self.grid.SetColLabelValue(2, "Current")
        self.grid.SetColLabelValue(3, "Analysis tab")

        # Properties.
        self.grid.SetDefaultCellFont(self.gui.font_normal)
        self.grid.SetLabelFont(self.gui.font_normal_bold)

        # Set the row label widths.
        self.grid.SetRowLabelSize(self.width_col_label)

        # No cell resizing allowed.
        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        # Add grid to sizer.
        sizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 0)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Hide()


    def pipe_delete(self, event):
        """Delete the date pipe.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete the '%s' data pipe?  This operation cannot be undone." % self.selected_pipe
        if not question(msg, default=False):
            return

        # Delete the data pipe.
        delete(self.selected_pipe)


    def pipe_switch(self, event):
        """Switch to the selected date pipe.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Switch to the selected data pipe.
        switch(self.selected_pipe)


    def resize(self, event):
        """Catch the resize to allow the grid to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def size_cols(self):
        """Set the column sizes."""

        # The grid size.
        x, y = self.grid.GetSize()

        # Number of columns.
        n = 4

        # The width of the current data pipe column.
        width_col_curr = 80

        # Set to equal sizes.
        width = int((x - self.width_col_label - width_col_curr) / (n - 1))

        # Set the column sizes.
        for i in range(n):
            # The cdp column.
            if i == 2:
                self.grid.SetColSize(i, width_col_curr)

            # All others.
            else:
                self.grid.SetColSize(i, width)


    def update_grid(self):
        """Update the grid with the pipe data."""

        # First freeze the grid, so that the GUI element doesn't update until the end.
        self.grid.Freeze()

        # Delete the rows, leaving a single row.
        self.grid.DeleteRows(numRows=self.grid.GetNumberRows()-1)

        # The data pipes.
        pipe_list = pipe_names()
        n = len(pipe_list)

        # Append the appropriate number of rows.
        if n >= 1:
            self.grid.AppendRows(numRows=n-1)

        # Loop over the data pipes.
        for i in range(n):
            # Set the pipe name.
            self.grid.SetCellValue(i, 0, str_to_gui(pipe_list[i]))

            # Set the pipe type.
            self.grid.SetCellValue(i, 1, str_to_gui(get_type(pipe_list[i])))

            # Set the current pipe.
            if pipe_list[i] == cdp_name():
                self.grid.SetCellValue(i, 2, str_to_gui("cdp"))

            # Set the tab the pipe belongs to.
            self.grid.SetCellValue(i, 3, str_to_gui(self.gui.analysis.page_name_from_pipe(pipe_list[i])))

        # Set the grid properties once finalised.
        for i in range(self.grid.GetNumberRows()):
            # Row properties.
            self.grid.SetRowSize(i, 27)

            # Loop over the columns.
            for j in range(self.grid.GetNumberCols()):
                # Cell properties.
                self.grid.SetReadOnly(i, j)

        # Unfreeze.
        self.grid.Thaw()
