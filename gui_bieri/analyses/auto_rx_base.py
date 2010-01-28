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
from gui_bieri.message import exec_relax
from gui_bieri.paths import IMAGE_PATH



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

        # The parent GUI element for this class.
        self.parent = wx.Panel(notebook, -1)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        main_box = self.build_main_box()
        self.parent.SetSizer(main_box)

        # Set the frame font size.
        self.parent.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))


    def build_main_box(self):
        # R1 no. 1
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.parent, -1, wx.Bitmap(self.bitmap, wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy = wx.StaticText(self.parent, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy = wx.StaticText(self.parent, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11 = wx.TextCtrl(self.parent, -1, str(self.data.frq))
        self.label_2_copy_copy_3_copy_copy = wx.StaticText(self.parent, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11 = wx.TextCtrl(self.parent, -1, self.data.save_dir)
        self.results_directory_copy_copy = wx.Button(self.parent, -1, "Change")
        self.structure_file = wx.StaticText(self.parent, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11 = StructureTextCtrl(self.parent, -1, self.gui.structure_file_pdb_msg)
        self.structure_r11.SetEditable(False)
        self.results_directory_copy_copy_copy = wx.Button(self.parent, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy = wx.StaticText(self.parent, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r11 = wx.TextCtrl(self.parent, -1, "")
        self.panel_2 = wx.Panel(self.parent, -1)
        self.addr11 = wx.Button(self.panel_1, -1, "add")
        self.refreshr11 = wx.Button(self.panel_1, -1, "refresh")
        self.label_3 = wx.StaticText(self.panel_3, -1, "R1 relaxation peak list                                                              ")
        self.label_6 = wx.StaticText(self.panel_3, -1, "Relaxation time [s]")
        self.r1_list_1 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_1 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_2 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_2 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_3 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_3 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_4 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_4 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_5 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_5 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_6 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_6 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_7 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_7 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_8 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_8 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_9 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_9 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_10 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_10 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_11 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_11 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_12 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_12 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_1_copy_11 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_13 = wx.TextCtrl(self.panel_3, -1, "")
        self.r1_list_14 = wx.StaticText(self.panel_3, -1, "")
        self.r1_time_1_4 = wx.TextCtrl(self.panel_3, -1, "")
        self.label_5_copy_1_copy = wx.StaticText(self.parent, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1 = wx.BitmapButton(self.parent, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #button actions
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_1, self.results_directory_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_r11.open_file, self.results_directory_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r1_1, self.addr11)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_1, self.refreshr11)


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
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)

        sizer_10.Add(self.bitmap_1_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11.Add(self.label_4_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy.Add(self.label_2_copy_copy_copy_2_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy.Add(self.nmrfreq_value_r11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(nmr_freq_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy.Add(self.label_2_copy_copy_3_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy.Add(self.resultsdir_r11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy.Add(self.results_directory_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11.Add(results_dir_copy_copy, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy.Add(self.structure_file, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy.Add(self.structure_r11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy.Add(self.results_directory_copy_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11.Add(results_dir_copy_copy_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy.Add(self.label_2_copy_copy_copy_2_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy.Add(self.unresolved_r11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(nmr_freq_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11.Add(self.panel_2, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13.Add(self.addr11, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13.Add(self.refreshr11, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12.Add(sizer_13, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.label_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_1_copy_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_13, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_list_14, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.r1_time_1_4, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3.SetSizer(grid_sizer_1)
        sizer_12.Add(self.panel_3, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1.SetSizer(sizer_12)
        sizer_11.Add(self.panel_1, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy.Add(self.label_5_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy.Add(self.relax_start_r1_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(exec_relax_copy_1_copy, 0, wx.ALIGN_RIGHT, 0)
        sizer_10.Add(sizer_11, 0, 0, 0)
        self.parent.SetSizer(sizer_10)
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
        self.label_4_copy_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy.SetMinSize((230, 17))
        self.nmrfreq_value_r11.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy.SetMinSize((230, 17))
        self.resultsdir_r11.SetMinSize((350, 27))
        self.results_directory_copy_copy.SetMinSize((103, 27))
        self.structure_file.SetMinSize((230, 17))
        self.structure_r11.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy.SetMinSize((230, 17))
        self.unresolved_r11.SetMinSize((350, 27))
        self.panel_2.SetMinSize((688, 5))
        self.addr11.SetMinSize((60, 27))
        self.refreshr11.SetMinSize((60, 27))
        self.label_3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.r1_time_1.SetMinSize((80, 20))
        self.r1_time_2.SetMinSize((80, 20))
        self.r1_time_3.SetMinSize((80, 20))
        self.r1_time_4.SetMinSize((80, 20))
        self.r1_time_5.SetMinSize((80, 20))
        self.r1_time_6.SetMinSize((80, 20))
        self.r1_time_7.SetMinSize((80, 20))
        self.r1_time_8.SetMinSize((80, 20))
        self.r1_time_9.SetMinSize((80, 20))
        self.r1_time_10.SetMinSize((80, 20))
        self.r1_time_11.SetMinSize((80, 20))
        self.r1_time_12.SetMinSize((80, 20))
        self.r1_time_13.SetMinSize((80, 20))
        self.r1_time_1_4.SetMinSize((80, 20))
        self.panel_3.SetMinSize((620, 300))
        self.panel_3.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1.SetMinSize((688, 300))
        self.panel_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy.SetMinSize((118, 17))
        self.relax_start_r1_1.SetName('hello')
        self.relax_start_r1_1.SetSize(self.relax_start_r1_1.GetBestSize())
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


    def add_r1_1(self, event): # add a r1 peak list

        if len(r1_list) < 14:
            r1_entry = multi_openfile('Select R1 peak list file', self.resultsdir_r11_copy.GetValue(), '*.*', 'all files (*.*)|*.*')
            if not r1_entry == None:
                r1_list.append(r1_entry)

        if len(r1_list) >= 1:
            self.r1_list_1.SetLabel(r1_list[0])
        if len(r1_list) >= 2:
            self.r1_list_2.SetLabel(r1_list[1])
        if len(r1_list) >= 3:
            self.r1_list_3.SetLabel(r1_list[2])
        if len(r1_list) >= 4:
            self.r1_list_4.SetLabel(r1_list[3])
        if len(r1_list) >= 5:
            self.r1_list_5.SetLabel(r1_list[4])
        if len(r1_list) >= 6:
            self.r1_list_6.SetLabel(r1_list[5])
        if len(r1_list) >= 7:
            self.r1_list_7.SetLabel(r1_list[6])
        if len(r1_list) >= 8:
            self.r1_list_8.SetLabel(r1_list[7])
        if len(r1_list) >= 9:
            self.r1_list_9.SetLabel(r1_list[8])
        if len(r1_list) >= 10:
            self.r1_list_10.SetLabel(r1_list[9])
        if len(r1_list) >= 11:
            self.r1_list_11.SetLabel(r1_list[10])
        if len(r1_list) >= 12:
            self.r1_list_12.SetLabel(r1_list[11])
        if len(r1_list) >= 13:
            self.r1_list_1_copy_11.SetLabel(r1_list[12])
        if len(r1_list) >= 14:
            self.r1_list_14.SetLabel(r1_list[13])
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
            start_rx(self.resultsdir_r21.GetValue(), r2_list, relax_times_r2_1, self.structure_r11.GetValue(), self.nmrfreq_value_r11.GetValue(), 2, 1, self.unresolved_r11.GetValue(), self, 1, global_setting, file_setting, sequencefile)
        event.Skip()


    def refresh_r1_1(self, event): # refresh r1 list no. 1
        self.r1_list_1.SetLabel('')
        self.r1_list_2.SetLabel('')
        self.r1_list_3.SetLabel('')
        self.r1_list_4.SetLabel('')
        self.r1_list_5.SetLabel('')
        self.r1_list_6.SetLabel('')
        self.r1_list_7.SetLabel('')
        self.r1_list_8.SetLabel('')
        self.r1_list_9.SetLabel('')
        self.r1_list_10.SetLabel('')
        self.r1_list_11.SetLabel('')
        self.r1_list_12.SetLabel('')
        self.r1_list_1_copy_11.SetLabel('')
        self.r1_list_14.SetLabel('')
        del r1_list[0:len(r1_list)]
        event.Skip()


    def resdir_r1_1(self, event): # R1 results dir 1
        backup = self.resultsdir_r11.GetValue()
        r1_savedir[0] = opendir('Select results directory', default=self.resultsdir_r11.GetValue())
        if r1_savedir[0] == None:
            r1_savedir[0] = backup
        self.resultsdir_r11.SetValue(r1_savedir[0])

        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the rx analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # Dummy function (for the time being).
