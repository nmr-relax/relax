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
"""Module containing the base class for the automatic R1 and R2 analysis frames."""

# Python module imports.
from os import sep
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relaxGUI module imports.
from gui_bieri.analyses.project import open_file
from gui_bieri.derived_wx_classes import StructureTextCtrl
from gui_bieri.filedialog import multi_openfile, opendir
from gui_bieri.message import error_message, exec_relax
from gui_bieri.paths import ADD_ICON, CANCEL_ICON, IMAGE_PATH, REMOVE_ICON



class Auto_rx:
    """The base class for the R1 and R2 frames."""

    # Hardcoded variables.
    analysis_type = None
    bitmap = None
    label = None

    def __init__(self, gui, notebook, hardcoded_index=None):
        """Build the automatic R1 and R2 analysis GUI frame elements.

        @param gui:                 The main GUI class.
        @type gui:                  gui_bieri.relax_gui.Main instance
        @param notebook:            The notebook to pack this frame into.
        @type notebook:             wx.Notebook instance
        @keyword hardcoded_index:   Kludge for the current GUI layout.
        @type hardcoded_index:      int
        """

        # Store the main class.
        self.gui = gui

        # Alias the storage container in the relax data store.
        self.data = ds.relax_gui.analyses[hardcoded_index]

        # The number of peak list elements (update the data store to match).
        self.peak_list_count = 14
        self.data.file_list = [''] * self.peak_list_count
        self.data.relax_times = [''] * self.peak_list_count

        # The parent GUI element for this class.
        self.parent = wx.Panel(notebook, -1)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        main_box = self.build_main_box()
        self.parent.SetSizer(main_box)

        # Set the frame font size.
        self.parent.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))


    def __do_layout(self):
        # begin wxGlade: main.__do_layout
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_22_copy_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_23_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_22_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_23_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_22 = wx.BoxSizer(wx.VERTICAL)
        sizer_23 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17_copy_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_copy_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_copy_1 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_2 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_2 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_2 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_copy = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_copy = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_1 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1_copy = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)

        # A grid sizer for the peak list info.
        sizer_11.Add(results_dir_copy_copy, 1, wx.EXPAND, 0)
        sizer_10_copy.Add(self.bitmap_1_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(self.label_4_copy_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        sizer_8.Add(self.notebook_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_8)
        self.Layout()
        self.SetSize((1000, 600))
        self.Centre()


    def __set_properties(self):
        # begin wxGlade: main.__set_properties
        self.label_4_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3.SetMinSize((230, 17))
        self.label_2_copy_copy_5.SetMinSize((230, 17))
        self.label_2_copy_copy_2_copy_1.SetMinSize((230, 17))
        self.label_2_copy_copy_3_copy_1.SetMinSize((230, 17))
        self.label_4_copy_copy_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_1.SetMinSize((230, 17))
        self.nmrfreq_value_r21.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy.SetMinSize((230, 17))

        self.panel_3_copy_copy_1.SetMinSize((620, 300))
        self.panel_3_copy_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_copy_1.SetMinSize((688, 300))
        self.panel_1_copy_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_copy_1.SetMinSize((118, 17))
        self.relax_start_r1_1_copy_copy_1.SetName('hello')
        self.relax_start_r1_1_copy_copy_1.SetSize(self.relax_start_r1_1_copy_copy_1.GetBestSize())


    def add_execute_relax(self, box):
        """Create and add the relax execution GUI element to the given box.

        @param box:     The box element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # A horizontal sizer for the contents.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        label.SetMinSize((118, 17))
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.BitmapButton(self.parent, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        button.SetName('hello')
        button.SetSize(button.GetBestSize())
        self.gui.Bind(wx.EVT_BUTTON, self.exec_r1_1, button)
        sizer.Add(button, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALIGN_RIGHT, 0)


    def add_frame_title(self, box):
        """Create and add the frame title to the given box.

        @param box:     The box element to pack the frame title into.
        @type box:      wx.BoxSizer instance
        """

        # The title.
        label = wx.StaticText(self.parent, -1, "Set-up for %s relaxation analysis:" % self.label)

        # The font properties.
        label.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))

        # Pack the title.
        box.Add(label, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)


    def add_frq(self, box):
        """Create and add the frequency selection GUI element to the given box.

        @param box:     The box element to pack the PDB file selection GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_nmr_frq = wx.TextCtrl(self.parent, -1, str(self.data.frq))
        self.field_nmr_frq.SetMinSize((350, 27))
        sizer.Add(self.field_nmr_frq, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_peak_list_selection(self, box):
        """Create and add the peak list selection GUI element to the given box.

        @param box:             The box element to pack the peak list selection GUI element into.
        @type box:              wx.BoxSizer instance
        """

        # The background panel (only used for layout purposes).
        panel_back = wx.Panel(self.parent, -1)
        panel_back.SetMinSize((688, 5))

        # A Horizontal layout sizer (to separate the buttons from the grid).
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        # The panel for both the buttons and the grid.
        panel_main = wx.Panel(self.parent, -1)
        panel_main.SetMinSize((688, 300))
        panel_main.SetBackgroundColour(wx.Colour(192, 192, 192))
        panel_main.SetSizer(sizer_main)

        # A Vertical layout sizer (for the buttons).
        sizer_buttons = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(sizer_buttons, 1, wx.EXPAND, 0)

        # Button sizes.
        size_button = [60, 60]

        # The add button.
        button = wx.BitmapButton(panel_main, -1, wx.Bitmap(ADD_ICON, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((size_button[0], size_button[1]))
        self.gui.Bind(wx.EVT_BUTTON, self.peak_list_add_action, button)
        sizer_buttons.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # The remove single item button.
        button = wx.BitmapButton(panel_main, -1, wx.Bitmap(REMOVE_ICON, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((size_button[0], size_button[1]))
        self.gui.Bind(wx.EVT_BUTTON, self.empty_list, button)
        sizer_buttons.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # The cancel button.
        button = wx.BitmapButton(panel_main, -1, wx.Bitmap(CANCEL_ICON, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((size_button[0], size_button[1]))
        self.gui.Bind(wx.EVT_BUTTON, self.empty_list, button)
        sizer_buttons.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # The panel for the grid.
        panel_grid = wx.Panel(panel_main, -1)
        panel_grid.SetMinSize((620, 300))
        panel_grid.SetBackgroundColour(wx.Colour(192, 192, 192))
        sizer_main.Add(panel_grid, 0, wx.EXPAND|wx.SHAPED, 0)

        # A grid sizer for the peak list info.
        sizer_grid = wx.FlexGridSizer(10, 2, 0, 0)

        # The file title.
        label = wx.StaticText(panel_grid, -1, "R1 relaxation peak list                                                              ")
        label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
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
            self.field_rx_time[-1].SetMinSize((80, 20))
            sizer_grid.Add(self.field_rx_time[-1], 0, wx.ADJUST_MINSIZE, 0)

        # Place the grid inside the panel.
        panel_grid.SetSizer(sizer_grid)

        # Add the panels to the box (this order adds a spacer at the top).
        box.Add(panel_back, 0, wx.EXPAND|wx.SHAPED, 0)
        box.Add(panel_main, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_results_dir(self, box):
        """Create and add the results directory GUI element to the given box.

        @param box:     The box element to pack the results directory GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Results directory", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_results_dir = wx.TextCtrl(self.parent, -1, self.data.save_dir)
        self.field_results_dir.SetMinSize((350, 27))
        sizer.Add(self.field_results_dir, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.Button(self.parent, -1, "Change")
        button.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.results_directory, button)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)

        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_structure_selection(self, box):
        """Create and add the structure file selection GUI element to the given box.

        @param box:     The box element to pack the structure file selection GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_structure = StructureTextCtrl(self.parent, -1, self.gui.structure_file_pdb_msg)
        self.field_structure.SetEditable(False)
        self.field_structure.SetMinSize((350, 27))
        sizer.Add(self.field_structure, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.Button(self.parent, -1, "Change")
        button.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.field_structure.open_file, button)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)

        # Add the element to the box.
        box.Add(sizer, 1, wx.EXPAND, 0)


    def add_unresolved_spins(self, box):
        """Create and add the unresolved spins GUI element to the given box.

        @param box:     The box element to pack the unresolved spins GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_unresolved = wx.TextCtrl(self.parent, -1, "")
        self.field_unresolved.SetMinSize((350, 27))
        sizer.Add(self.field_unresolved, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        
        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def build_main_box(self):
        """Construct the highest level box to pack into the automatic Rx analysis frame.

        @return:    The main box element containing all Rx GUI elements to pack directly into the automatic Rx analysis frame.
        @rtype:     wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        box = wx.BoxSizer(wx.HORIZONTAL)

        # Add the model-free bitmap picture.
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.parent, -1, wx.Bitmap(self.bitmap, wx.BITMAP_TYPE_ANY))
        box.Add(self.bitmap_1_copy_copy, 0, wx.ADJUST_MINSIZE, 10)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 0, 0, 0)

        # Return the box.
        return box


    def build_right_box(self):
        """Construct the right hand box to pack into the main Rx box.

        @return:    The right hand box element containing all Rx GUI elements (excluding the bitmap) to pack into the main Rx box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_frame_title(box)

        # Add the frequency selection GUI element.
        self.add_frq(box)

        # Add the results directory GUI element.
        self.add_results_dir(box)

        # Add the structure file selection GUI element.
        self.add_structure_selection(box)

        # Add the unresolved spins GUI element.
        self.add_unresolved_spins(box)

        # Add the peak list selection GUI element.
        self.add_peak_list_selection(box)

        # Add the execution GUI element.
        self.add_execute_relax(box)

        # Return the box.
        return box


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


    def exec_r1_1(self, event): # start r2 calculation
        relax_times_r2_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_r2_1[0] = str(self.r2_time_1.GetValue())
        relax_times_r2_1[1] = str(self.r2_time_2.GetValue())
        relax_times_r2_1[2] = str(self.r2_time_3.GetValue())
        relax_times_r2_1[3] = str(self.r2_time_4.GetValue())
        relax_times_r2_1[4] = str(self.r2_time_5.GetValue())
        relax_times_r2_1[5] = str(self.r2_time_6.GetValue())
        relax_times_r2_1[6] = str(self.r2_time_7.GetValue())
        relax_times_r2_1[7] = str(self.r2_time_8.GetValue())
        relax_times_r2_1[8] = str(self.r2_time_9.GetValue())
        relax_times_r2_1[9] = str(self.r2_time_10.GetValue())
        relax_times_r2_1[10] = str(self.r2_time_11.GetValue())
        relax_times_r2_1[11] = str(self.r2_time_12.GetValue())
        relax_times_r2_1[12] = str(self.r2_time_13.GetValue())
        relax_times_r2_1[13] = str(self.r2_time_14.GetValue())
        start_relax = exec_relax()
        if start_relax == True:
            start_rx(self.resultsdir_r21.GetValue(), r2_list, relax_times_r2_1, self.field_structure.GetValue(), self.nmrfreq_value_r11.GetValue(), 2, 1, self.field_unresolved.GetValue(), self, 1, global_setting, file_setting, sequencefile)
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
            self.data.file_list[count+i] = files[i]

        # Refresh the GUI element.
        self.refresh_peak_list_display()

        # Terminate the event.
        event.Skip()


    def refresh_peak_list_display(self):
        """Refresh the display of peak list file names in the GUI element."""

        # Loop over all elements.
        for i in range(self.peak_list_count):
            self.field_rx_list[i].SetLabel(self.data.file_list[i])


    def results_directory(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = self.field_results_dir.GetValue()

        # Select the file.
        self.data.save_dir = opendir('Select results directory', default=self.field_results_dir.GetValue())

        # Restore the backup file if no file was chosen.
        if not self.data.save_dir:
            self.data.save_dir = backup

        # Place the path in the text box.
        self.field_results_dir.SetValue(self.data.save_dir)

        # Terminate the event.
        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the rx analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The frequency.
        if upload:
            self.data.frq = str(self.field_nmr_frq.GetValue())
        else:
            self.field_nmr_frq.SetValue(str(self.data.frq))

        # The results directory.
        if upload:
            self.data.save_dir = str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str(self.data.save_dir))

        # The structure file.
        if upload:
            self.data.structure_file = str(self.field_structure.GetValue())
        else:
            self.field_structure.SetValue(str(self.data.structure_file))

        # Unresolved residues.
        if upload:
            self.data.unresolved = str(self.field_unresolved.GetValue())
        else:
            self.field_unresolved.SetValue(str(self.data.unresolved))

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
