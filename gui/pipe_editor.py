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
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.pipes import cdp_name, delete, get_type, pipe_names, switch
from status import Status; status = Status()

# relax GUI module imports.
from gui.components.menu import build_menu_item
from gui.fonts import font
from gui.icons import relax_icons
from gui.message import Question
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

        # Set up the window icon.
        self.SetIcons(relax_icons)

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

        # Initialise the observer name.
        self.name = 'pipe editor'


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Update the grid.
        self.update_grid()
        self.activate()

        # Register the grid for updating when a user function completes or when the GUI analysis tabs change.
        status.observers.pipe_alteration.register(self.name, self.update_grid)
        status.observers.gui_analysis.register(self.name, self.update_grid)
        status.observers.exec_lock.register(self.name, self.activate)

        # Show the window using the base class method.
        if status.show_gui:
            super(Pipe_editor, self).Show(show)


    def activate(self):
        """Activate or deactivate certain elements in response to the execution lock."""

        # Turn off all buttons.
        if status.exec_lock.locked():
            wx.CallAfter(self.button_create.Enable, False)
            wx.CallAfter(self.button_copy.Enable, False)
            wx.CallAfter(self.button_delete.Enable, False)
            wx.CallAfter(self.button_hybrid.Enable, False)
            wx.CallAfter(self.button_switch.Enable, False)

        # Turn on all buttons.
        else:
            wx.CallAfter(self.button_create.Enable, True)
            wx.CallAfter(self.button_copy.Enable, True)
            wx.CallAfter(self.button_delete.Enable, True)
            wx.CallAfter(self.button_hybrid.Enable, True)
            wx.CallAfter(self.button_switch.Enable, True)


    def menu(self, event):
        """The pop up menu.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the row.
        row = event.GetRow()

        # Get the name of the data pipe.
        self.selected_pipe = gui_to_str(self.grid.GetCellValue(row, 0))

        # No data pipe.
        if not self.selected_pipe:
            return

        # The pipe type.
        pipe_type = get_type(self.selected_pipe)

        # Initialise the menu.
        menu = wx.Menu()

        # Menu entry:  delete the data pipe.
        item = build_menu_item(menu, parent=self, text="&Delete the pipe", icon=icon_16x16.remove, fn=self.pipe_delete)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)
 
        # Menu entry:  switch to this data pipe.
        item = build_menu_item(menu, parent=self, text="&Switch to this pipe", icon=icon_16x16.pipe_switch, fn=self.pipe_switch)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)
 
        # Menu entry:  new auto-analysis tab.
        if self.gui.analysis.page_index_from_pipe(self.selected_pipe) == None and pipe_type in ['noe', 'r1', 'r2', 'mf']:
            item = build_menu_item(menu, parent=self, text="&Associate with a new auto-analysis", icon=icon_16x16.new, fn=self.associate_auto)
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)
 
        # Show the menu.
        if status.show_gui:
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
        self.button_create = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Create")
        self.button_create.SetBitmapLabel(wx.Bitmap(icon_22x22.add, wx.BITMAP_TYPE_ANY))
        self.button_create.SetFont(font.normal)
        self.button_create.SetToolTipString("Create a new data pipe.")
        button_sizer.Add(self.button_create, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.create, self.button_create)

        # The copy button.
        self.button_copy = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Copy")
        self.button_copy.SetBitmapLabel(wx.Bitmap(icon_22x22.copy, wx.BITMAP_TYPE_ANY))
        self.button_copy.SetFont(font.normal)
        self.button_copy.SetToolTipString("Copy a data pipe.")
        button_sizer.Add(self.button_copy, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.copy, self.button_copy)

        # The delete button.
        self.button_delete = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Delete")
        self.button_delete.SetBitmapLabel(wx.Bitmap(icon_22x22.list_remove, wx.BITMAP_TYPE_ANY))
        self.button_delete.SetFont(font.normal)
        self.button_delete.SetToolTipString("Delete a data pipe.")
        button_sizer.Add(self.button_delete, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.delete, self.button_delete)

        # The hybridise button.
        self.button_hybrid = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Hybridise")
        self.button_hybrid.SetBitmapLabel(wx.Bitmap(icon_22x22.pipe_hybrid, wx.BITMAP_TYPE_ANY))
        self.button_hybrid.SetFont(font.normal)
        self.button_hybrid.SetToolTipString("Hybridise data pipes.")
        button_sizer.Add(self.button_hybrid, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.hybridise, self.button_hybrid)

        # The switch button.
        self.button_switch = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Switch")
        self.button_switch.SetBitmapLabel(wx.Bitmap(icon_22x22.pipe_switch, wx.BITMAP_TYPE_ANY))
        self.button_switch.SetFont(font.normal)
        self.button_switch.SetToolTipString("Switch data pipes.")
        button_sizer.Add(self.button_switch, 1, wx.ALL|wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.gui.user_functions.pipe.switch, self.button_switch)


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
        self.grid.SetDefaultCellFont(font.normal)
        self.grid.SetLabelFont(font.normal_bold)

        # Set the row label widths.
        self.grid.SetRowLabelSize(self.width_col_label)

        # No cell resizing allowed.
        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        # Add grid to sizer.
        sizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 0)


    def associate_auto(self, event):
        """Associate the selected data pipe with a new auto-analysis.


        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the GUI data store object if needed.
        if not hasattr(ds, 'relax_gui'):
            self.gui.init_data()

        # The type.
        type = get_type(self.selected_pipe)

        # The name.
        names = {
            'noe': 'Steady-state NOE',
            'r1': 'R1 relaxation',
            'r2': 'R2 relaxation',
            'mf': 'Model-free'
        }

        # Create a new analysis with the selected data pipe.
        self.gui.analysis.new_analysis(analysis_type=type, analysis_name=names[type], pipe_name=self.selected_pipe)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Unregister the methods from the observers to avoid unnecessary updating.
        status.observers.pipe_alteration.unregister(self.name)
        status.observers.gui_analysis.unregister(self.name)
        status.observers.exec_lock.unregister(self.name)

        # Close the window.
        self.Hide()


    def pipe_delete(self, event):
        """Delete the date pipe.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete the '%s' data pipe?  This operation cannot be undone." % self.selected_pipe
        if Question(msg, default=False).ShowModal() == wx.ID_NO:
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
        """Update the grid in a thread safe way using wx.CallAfter."""

        # Thread safe.
        wx.CallAfter(self.update_grid_safe)

        # Flush the events.
        wx.Yield()


    def update_grid_safe(self):
        """Update the grid with the pipe data."""

        # First freeze the grid, so that the GUI element doesn't update until the end.
        self.grid.Freeze()

        # Acquire the pipe lock.
        status.pipe_lock.acquire()

        # Delete the rows, leaving a single row.
        self.grid.DeleteRows(numRows=self.grid.GetNumberRows()-1)

        # Clear the contents of the first row.
        for i in range(self.grid.GetNumberCols()):
            self.grid.SetCellValue(0, i, str_to_gui(""))

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

        # Release the lock.
        status.pipe_lock.release()

        # Unfreeze.
        self.grid.Thaw()
