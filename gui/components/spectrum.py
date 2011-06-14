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
from re import search
import wx
import wx.lib.buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()

# relaxGUI module imports.
from gui.filedialog import multi_openfile, opendir, openfile
from gui.message import error_message
from gui.misc import add_border
from gui import paths


class Delay_num_cell_editor(wx.grid.PyGridCellEditor):
    """Custom GridCellEditor for the number of delays grid cells.

    Changing these cells will update the relaxation delay times.
    """

    def __init__(self, min=None, max=None, parent=None):
        """Initialise the class.
        
        @keyword min:       The minimum value for wx.SpinCtrl.
        @type min:          None or int
        @keyword max:       The maximum value for wx.SpinCtrl.
        @type max:          None or int
        @keyword parent:    The parent wx object.
        @type parent:       wx object
        """

        # Store the args.
        self.min = min
        self.max = max
        self.parent = parent

        # Initialise the base class.
        super(Delay_num_cell_editor, self).__init__()

        # A flag for a resetting event.
        self.reset = False


    def BeginEdit(self, row, col, grid):
        """Start the editing.

        @param row:     The row index.
        @type row:      int
        @param col:     The column index.
        @type col:      int
        @param grid:    The grid GUI element.
        @type grid:     wx.grid.Grid instance.
        """

        # The previous value.
        self.prev_val = grid.GetTable().GetValue(row, col)

        # Set the starting value.
        self.cell.SetValueString(self.prev_val)

        # Set the focus to the cell.
        self.cell.SetFocus()


    def Clone(self):
        """Create and return a new class instance."""

        # Initialise and return the class.
        return Delay_num_cell_editor(self.min, self.max, self.parent)


    def Create(self, parent, id, evtHandler):
        """Create the control for the cell.

        @param parent:      The parent wx object.
        @type parent:       wx object
        @param id:          The ID number.
        @type id:           int
        @param evtHandler:  The event handler function.
        @type evtHandler:   func
        """

        # Set the cell to be a spin control.
        self.cell = wx.SpinCtrl(parent, id, "", min=self.min, max=self.max)
        self.SetControl(self.cell)

        # Handle the event handler.
        if evtHandler:
            self.cell.PushEventHandler(evtHandler)


    def EndEdit(self, row, col, grid):
        """End the editing.

        @param row:     The row index.
        @type row:      int
        @param col:     The column index.
        @type col:      int
        @param grid:    The grid GUI element.
        @type grid:     wx.grid.Grid instance.
        """

        # A reset.
        if self.reset:
            # Reset the reset flag.
            self.reset = False

            # No starting value, so do nothing.
            if self.prev_val == '':
                return False

        # The new value.
        value = self.cell.GetValue()

        # No change.
        if value == self.prev_val:
            return False

        # Set the value in the table (the value of zero shows nothing).
        if value == 0:
            text = ''
        else:
            text = str(value)
        grid.GetTable().SetValue(row, col, text)

        # The delay cycle time.
        time = self.parent.delay_time.GetValue()

        # No times to update.
        if time == '':
            # A change occurred.
            return True

        # Update the relaxation delay time.
        delay_time = float(time) * float(value)
        grid.GetTable().SetValue(row, col-1, str(delay_time))

        # A change occurred.
        return True


    def Reset(self):
        """Reset the cell to the previous value."""

        # Set the previous value.
        self.cell.SetValueString(self.prev_val)

        # Set a flag for EndEdit to catch a reset.
        self.reset = True


    def StartingKey(self, event):
        """Catch the starting key stroke to add the value to the cell.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The value.
        key = event.GetKeyCode()

        # Acceptable integers.
        if key >= 49 and key <= 57:
            # The number.
            num = int(chr(key))

            # Set the value.
            self.cell.SetValue(num)

            # Set the insertion point to the end.
            self.cell.SetSelection(1,1)

        # Skip everything else.
        else:
            event.Skip()



class Peak_intensity:
    """The peak list selection class."""

    # Class variables.
    col_label_width = 40
    col1_width = 160
    col2_width = 140

    def __init__(self, gui=None, parent=None, subparent=None, data=None, label=None, width=688, height=300, box=None):
        """Build the peak list reading GUI element.

        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword subparent: The subparent GUI element that this is to be attached to (the analysis object).
        @type subparent:    wx object
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
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent
        self.subparent = subparent
        self.data = data
        self.label = label

        # GUI variables.
        self.spacing = 5
        self.border = 5

        # The number of rows.
        self.num_rows = 50

        # A static box to hold all the widgets, and its sizer.
        stat_box = wx.StaticBox(self.parent, -1, "Peak lists")
        stat_box.SetFont(self.gui.font_subtitle)
        sub_sizer = wx.StaticBoxSizer(stat_box, wx.VERTICAL)

        # Add the sizer to the static box and the static box to the main box.
        box.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add a border.
        box_centre = add_border(sub_sizer, border=self.border)

        # Add the cycle delay time element.
        box_centre.AddSpacer(self.spacing)
        self.delay_time = self.subparent.add_text_sel_element(box_centre, self.parent, text="Single delay cycle time [s]")

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
        width = x - self.col_label_width - self.col1_width - self.col2_width - 10

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
            self.gui.Bind(wx.EVT_BUTTON, lambda event, vc=True: self.load_delay(event, vc), add_vc)

        # Pack buttons
        sizer.Add(button_sizer, 0, 0, 0)


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

        # Column properties.
        for i in range(self.grid.GetNumberRows()):
            # Make the relaxation delay column read only.
            self.grid.SetReadOnly(i, 1)

            # Set the editor for the number of cycles column.
            self.grid.SetCellEditor(i, 2, Delay_num_cell_editor(0, 200, self))

        # No cell resizing allowed.
        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        # Bind some events.
        self.grid.GetGridWindow().Bind(wx.EVT_LEFT_DCLICK, self.event_left_dclick)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.event_key_down)
        self.grid.Bind(wx.EVT_SIZE, self.resize)

        # Add grid to sizer, with spacing.
        sizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 0)


    def change_delay_down(self, event):
        """Handle changes to the delay time.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The key.
        key = event.GetKeyCode()

        # Get the text.
        text = str(self.delay_time.GetString(0, self.delay_time.GetLastPosition()))

        # Allowed keys.
        allowed = []
        allowed += [8]    # Backspace.
        if not search('\.', text):
            allowed += [46]    # Only one full stop.
        allowed += [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]    # Numbers.
        allowed += [127]    # Delete.
        allowed += [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_HOME, wx.WXK_END]    # Navigation keys.

        # Disallowed values, so do nothing.
        if key not in allowed:
            return

        # Normal event handling.
        event.Skip()


    def change_delay_up(self, event):
        """Handle updates to the delay time.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Normal event handling.
        event.Skip()

        # Update the grid.
        self.update_grid()


    def event_left_dclick(self, event):
        """Handle the left mouse double click.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The row and column.
        col = self.grid.GetGridCursorCol()
        row = self.grid.GetGridCursorRow()

        # File selection.
        if col == 0:
            # The file.
            filename = openfile(msg='Select file.', filetype='*.*', default='all files (*.*)|*')

            # Abort if nothing selected.
            if not filename:
                return

            # Set the file name.
            self.grid.SetCellValue(row, col, str(filename))

        # Skip the event to allow for normal operation.
        event.Skip()


    def event_key_down(self, event):
        """Control what happens when a key is pressed.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear cell contents (delete key).
        if event.GetKeyCode() == wx.WXK_DELETE:
            # Get the cell selection.
            cells = self.get_selection()

            # Debugging printout.
            if status.debug:
                print(cells)

            # Loop over the cells.
            for cell in cells:
                # Set to the empty string.
                self.grid.SetCellValue(cell[0], cell[1], '')

            # Update the grid.
            self.update_grid()

            # Do nothing else.
            return

        # Skip the event to allow for normal operation.
        event.Skip()


    def get_all_coordinates(self, top_left, bottom_right):
        """Convert the cell range into a coordinate list.

        @param top_left:        The top left hand coordinate.
        @type top_left:         list or tuple
        @param bottom_right:    The bottom right hand coordinate.
        @type bottom_right:     list or tuple
        @return:                The list of tuples of coordinates of all cells.
        @rtype:                 list of tuples
        """

        # Init.
        cells = []

        # Loop over the x-range.
        for x in range(top_left[0], bottom_right[0]+1):
            # Loop over the y-range.
            for y in range(top_left[1], bottom_right[1]+1):
                # Append the coordinate.
                cells.append((x, y))

        # Return the coordinates.
        return cells


    def get_selection(self):
        """Determine which cells are selected.

        There are three possibilities for cell selections in a wx.grid.  These are:

            - Single cell selection (this is not highlighted).
            - Multiple cells are selected.
            - Column selection.
            - Row selection.

        @return:    An array of the cell selection coordinates.
        @rtype:     list of tuples of int
        """

        # First try to get the coordinates.
        top_left = self.grid.GetSelectionBlockTopLeft()
        bottom_right = self.grid.GetSelectionBlockBottomRight()

        # Or the selection.
        selection = self.grid.GetSelectedCells()
        col = self.grid.GetSelectedCols()
        row = self.grid.GetSelectedRows()

        # Debugging printout.
        if status.debug:
            print("\nTop left: %s" % top_left)
            print("Bottom right: %s" % bottom_right)
            print("selection: %s" % selection)
            print("col: %s" % col)
            print("row: %s" % row)

        # Column selection.
        if col:
            # Debugging printout.
            if status.debug:
                print("Column selection")

            # Return the coordinates of the selected columns.
            return self.get_all_coordinates([0, col[0]], [self.num_rows-1, col[-1]])

        # Row selection.
        elif row:
            # Debugging printout.
            if status.debug:
                print("Row selection")

            # Return the coordinates of the selected rows.
            return self.get_all_coordinates([row[0], 0], [row[-1], 1])

        # Multiple block selection.
        elif top_left and not selection:
            # Debugging printout.
            if status.debug:
                print("Multiple block selection.")

            # The cell list.
            cells = []

            # Loop over the n blocks.
            for n in range(len(top_left)):
                # Append the cells.
                cells = cells + self.get_all_coordinates(top_left[n], bottom_right[n])

            # Return the selected cells.
            return cells

        # Single cell.
        elif not selection and not top_left:
            # Debugging printout.
            if status.debug:
                print("Single cell.")

            # The position.
            pos = self.grid.GetGridCursorRow(), self.grid.GetGridCursorCol()

            # Return the coordinate as a list.
            return [pos]

        # Complex selection.
        elif selection:
            # Debugging printout.
            if status.debug:
                print("Complex selection.")

            # The cell list.
            cells = []

            # Loop over the n blocks.
            for n in range(len(top_left)):
                # Append the cells.
                cells = cells + self.get_all_coordinates(top_left[n], bottom_right[n])

            # Return the selection.
            return cells + selection

        # Unknown.
        else:
            # Debugging printout.
            if status.debug:
                print("Should not be here.")


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
            self.grid.SetCellValue(index, 1, str(t*vc_factor))

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
            if str(self.grid.GetCellValue(i, 0)) == '':
                # Write peak file
                self.grid.SetCellValue(i, 0, str(files[index]))

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

        # The peak lists and relaxation times.
        if upload:
            # The delay time.
            self.data.delay_time = str(self.delay_time.GetString(0, self.delay_time.GetLastPosition()))

            # Loop over the rows.
            for i in range(self.num_rows):
                # The cell data.
                file_name = str(self.grid.GetCellValue(i, 0))
                ncyc = str(self.grid.GetCellValue(i, 1))
                relax_time = str(self.grid.GetCellValue(i, 2))

                # No data, so stop.
                if file_name == '' and ncyc == '':
                    break

                # New row needed.
                if i >= len(self.data.file_list):
                    self.data.file_list.append('')
                if i >= len(self.data.ncyc):
                    self.data.ncyc.append('')
                if i >= len(self.data.relax_times):
                    self.data.relax_times.append('')

                # Set the file name and relaxation time.
                self.data.file_list[i] = file_name
                self.data.ncyc[i] = ncyc
                self.data.relax_times[i] = relax_time

        else:
            # The delay time.
            if hasattr(self.data, 'delay_time'):
                self.delay_time.SetValue(self.data.delay_time)

            # Loop over the rows.
            for i in range(len(self.data.file_list)):
                # The file name.
                if hasattr(self.data, 'file_list'):
                    self.grid.SetCellValue(i, 0, str(self.data.file_list[i]))

                # The number of cycles.
                if hasattr(self.data, 'ncyc'):
                    self.grid.SetCellValue(i, 1, str(self.data.ncyc[i]))

                # The relaxation time.
                if hasattr(self.data, 'relax_times'):
                    self.grid.SetCellValue(i, 2, str(self.data.relax_times[i]))

            # Update the grid.
            self.update_grid()


    def update_grid(self):
        """Update the grid, changing the relaxation delay times as needed."""

        # The time value.
        time = self.delay_time.GetString(0, self.delay_time.GetLastPosition())
        try:
            time = float(time)
        except ValueError:
            time = ''

        # Loop over the rows.
        for i in range(self.grid.GetNumberRows()):
            # The number of cycles.
            ncyc = str(self.grid.GetCellValue(i, 1))

            # No time or no cycles, so set the value to nothing.
            if time == '' or ncyc in ['', '0']:
                self.grid.SetCellValue(i, 2, '')

            # Update the relaxation time.
            else:
                self.grid.SetCellValue(i, 2, str(int(ncyc) * time))
