###############################################################################
#                                                                             #
# Copyright (C) 2010 Michael Bieri                                            #
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
"""Module containing the base class for the results frame."""

# Python module imports.
from string import lower, upper
import wx
from wx.lib import buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.pipes import cdp_name, pipe_names
from status import Status; status = Status()

# relax GUI module imports.
from gui.fonts import font
from gui.icons import relax_icons
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import add_border, gui_to_str, open_file, str_to_gui
from gui.paths import icon_22x22
from gui.user_functions import User_functions; user_functions = User_functions()


class Results_viewer(wx.Frame):
    """The results viewer frame."""

    # Some class variables.
    border = 10
    size = (800, 400)

    def __init__(self, parent):
        """Build the results frame.

        @param parent:  The parent wx object.
        @type parent:   wx object
        """

        # Initialise the base frame.
        wx.Frame.__init__(self, parent=parent, style=wx.DEFAULT_FRAME_STYLE)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Set the window title, size, etc.
        self.SetTitle("Results viewer")
        self.SetSize(self.size)

       # Place all elements within a panel (to remove the dark grey in MS Windows).
        self.main_panel = wx.Panel(self, -1)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.main_panel.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.VERTICAL)

        # Build the data pipe selector.
        self.build_pipe_sel(box_centre)

        # Spacer.
        box_centre.AddSpacer(self.border)

        # Add the list of results files.
        self.add_files(box_centre, fn=None)

        # Spacer.
        box_centre.AddSpacer(self.border)

        # Add the open button.
        self.button_open = buttons.ThemedGenBitmapTextButton(self.main_panel, -1, None, " Open")
        self.button_open.SetBitmapLabel(wx.Bitmap(icon_22x22.document_open, wx.BITMAP_TYPE_ANY))
        self.button_open.SetFont(font.normal)
        self.button_open.SetMinSize((103, 33))
        self.Bind(wx.EVT_BUTTON, self.open_result_file, self.button_open)
        box_centre.Add(self.button_open, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 5)

        # Relayout the main panel.
        self.main_panel.Layout()
        self.main_panel.Refresh()

        # Bind some events.
        self.Bind(wx.EVT_COMBOBOX, self.switch_pipes, self.pipe_name)
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Initialise observer name.
        self.name = 'results viewer'


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Register a few methods in the observer objects.
        status.observers.gui_uf.register(self.name, self.refresh)
        status.observers.pipe_alteration.register(self.name, self.refresh)
        status.observers.result_file.register(self.name, self.refresh)
        status.observers.exec_lock.register(self.name, self.activate)

        # First update.
        self.refresh()

        # Activate or deactivate the frame.
        self.activate()

        # Show the window using the base class method.
        if status.show_gui:
            super(Results_viewer, self).Show(show)


    def activate(self):
        """Activate or deactivate certain elements in response to the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # The pipe selector.
        self.pipe_name.Enable(enable)

        # The open button.
        self.button_open.Enable(enable)


    def add_files(self, box, fn=None):
        """Create the list of results files.

        @param box:     The box sizer to pack the box into.
        @type box:      wx.BoxSizer instance
        @keyword fn:    The function to bind double click events to.
        @type fn:       method
        @return:        The list box element.
        @rtype:         wx.ListBox element
        """

        # Initialise the list box.
        self.file_list = wx.ListCtrl(self.main_panel, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Properties.
        self.file_list.SetFont(font.normal)

        # Store the base heights.
        self.height_char = self.file_list.GetCharHeight()

        # The headers.
        self.file_list.InsertColumn(0, "File type")
        self.file_list.InsertColumn(1, "File path")

        # Add to the sizer.
        box.Add(self.file_list, 1, wx.ALL|wx.EXPAND, 0)

        # Bind events.
        self.file_list.Bind(wx.EVT_SIZE, self.resize)
        if fn:
            self.Bind(wx.EVT_LISTBOX_DCLICK, fn, self.file_list)


    def build_pipe_sel(self, box):
        """Create the data pipe selection element.

        @param box: The horizontal box element to pack the elements into.
        @type box:  wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The text.
        label = wx.StaticText(self.main_panel, -1, "Data pipe selection")

        # The font and label properties.
        label.SetFont(font.subtitle)

        # Add the label to the box.
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add a spacer.
        sizer.AddSpacer(self.border)

        # A combo box.
        self.pipe_name = wx.ComboBox(self.main_panel, -1, value='', style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=[])
        self.pipe_name.SetMinSize((50, 27))
        sizer.Add(self.pipe_name, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add the pipe sizer to the main sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Unregister the methods from the observers to avoid unnecessary updating.
        status.observers.gui_uf.unregister(self.name)
        status.observers.pipe_alteration.unregister(self.name)
        status.observers.result_file.unregister(self.name)
        status.observers.exec_lock.unregister(self.name)

        # Close the window.
        self.Hide()


    def open_result_file(self, event):
        """Open the results in the appropriate program.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Loop over all files.
        for i in range(self.file_list.GetItemCount()):
            # Not selected.
            if not self.file_list.IsSelected(i):
                continue

            # Get the type and file.
            type = self.file_data[i]
            file = gui_to_str(self.file_list.GetItem(i, 1).GetText())

            # Grace files.
            if type == 'grace':
                user_functions.grace.view(file=file)

            # PyMOL macro files.
            elif type == 'pymol':
                user_functions.pymol.macro_run(file=file)

            # Molmol macro files.
            elif type == 'molmol':
                user_functions.molmol.macro_run(file=file)

            # Diffusion tensor PDB.
            elif type == 'diff_tensor_pdb':
                interpreter.queue('pymol.view')
                interpreter.queue('pymol.cartoon')
                interpreter.queue('pymol.tensor_pdb', file=file)

            # A special table.
            elif type == 'Table_of_Results':
                # The data.
                model_result = [ds.relax_gui.table_residue, ds.relax_gui.table_model, ds.relax_gui.table_s2, ds.relax_gui.table_rex, ds.relax_gui.table_te]

            # Text files.
            elif type == 'text':
                open_file(file, force_text=True)

            # Open all other files in which ever editor the platform decides on.
            else:
                open_file(file)


    def refresh(self):
        """Update the list of result files."""

        # Thread safe.
        wx.CallAfter(self.refresh_safe)


    def refresh_safe(self):
        """Update the list of result files (thread safe)."""

        # Acquire the pipe lock.
        status.pipe_lock.acquire('results viewer window')
        try:
            # Update the data pipe selector.
            self.update_pipes()

            # Clear the list.
            self.file_list.DeleteAllItems()
            self.file_data = []

            # Nothing to do.
            if not hasattr(cdp, 'result_files'):
                return

            # Update the list.
            for i in range(len(cdp.result_files)):
                self.file_list.Append((str_to_gui(cdp.result_files[i][1]), str_to_gui(cdp.result_files[i][2])))
                self.file_data.append(cdp.result_files[i][0])

        # Release the locks.
        finally:
            status.pipe_lock.release('results viewer window')


    def resize(self, event):
        """Catch the resize to allow the element to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def switch_pipes(self, event):
        """Switch data pipes.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The name of the selected pipe.
        pipe = gui_to_str(event.GetString())

        # No pipe change.
        if pipe == cdp_name():
            return

        # Switch data pipes.
        interpreter.queue('pipe.switch', pipe)
        interpreter.flush()

        # Update the window.
        self.refresh()


    def update_pipes(self):
        """Update the data pipe list."""

        # Clear the previous data pipe.
        self.pipe_name.Clear()

        # The list of data pipes.
        for pipe in pipe_names():
            self.pipe_name.Append(str_to_gui(pipe))

        # Set the name to the current data pipe.
        self.pipe_name.SetValue(str_to_gui(cdp_name()))


    def size_cols(self):
        """Set the column sizes."""

        # The list size.
        x, y = self.file_list.GetSize()

        # Remove a little to prevent the horizontal scroll bar from appearing.
        x = x - 10

        # Set the column sizes.
        self.file_list.SetColumnWidth(0, int(x/3))
        self.file_list.SetColumnWidth(1, int(2*x/3))
