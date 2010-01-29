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
"""Main module for the relax graphical user interface."""

# Python module imports.
from os import getcwd, mkdir, sep
from re import search
from string import lower, lowercase, replace
import sys
import time
import webbrowser
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.gui import Gui
from float import floatAsByteArray
from generic_fns import pipes, state
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns.reset import reset
from relax_errors import RelaxError
from version import version

# relaxGUI module imports.
from about import about_relax
from analyses.auto_model_free import Auto_model_free
from analyses.auto_r1 import Auto_r1
from analyses.auto_r2 import Auto_r2
from analyses.project import create_save_file, open_file
from analyses.results_analysis import color_code_noe, model_free_results, results_table, see_results
from base_classes import Container
from controller import Controller
from derived_wx_classes import StructureTextCtrl
from filedialog import multi_openfile, opendir, openfile, savefile
from message import dir_message, exec_relax, missing_data, question, relax_run_ok
from paths import ABOUT_RELAX_ICON, ABOUT_RELAXGUI_ICON, CONTACT_ICON, CONTROLLER_ICON, EXIT_ICON, IMAGE_PATH, LOAD_ICON, MANUAL_ICON, NEW_ICON, OPEN_ICON, REF_ICON, SAVE_AS_ICON, SETTINGS_ICON, SETTINGS_GLOBAL_ICON, SETTINGS_RESET_ICON
from settings import import_file_settings, load_sequence, relax_global_settings


# Variables.
GUI_version = '1.00'



class Main(wx.Frame):
    """The main GUI class."""

    # Hard coded variables.
    structure_file_pdb_msg = "please insert .pdb file"

    def __init__(self, *args, **kwds):
        """Initialise the main relax GUI frame."""

        # Add the style keyword value.
        kwds["style"] = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN

        # Execute the base class __init__ method.
        super(Main, self).__init__(*args, **kwds)

        # The analysis frame object storage.
        self.analysis_frames = []

        # FIXME:  This is only for the current fixed interface.
        self.hardcoded_index_noe_1 = 0
        self.hardcoded_index_r1_1  = 1
        self.hardcoded_index_r2_1  = 2
        self.hardcoded_index_noe_2 = 3
        self.hardcoded_index_r1_2  = 4
        self.hardcoded_index_r2_2  = 5
        self.hardcoded_index_noe_3 = 6
        self.hardcoded_index_r1_3  = 7
        self.hardcoded_index_r2_3  = 8
        self.hardcoded_index_mf    = 9
        for i in range(10):
            self.analysis_frames.append(Container())

        # A fixed set of indices for 3 NOE, 3 R1, and 3 R2 frames used for accessing the relax data store.
        # FIXME:  Eliminate these!  There should be a flexible number of these frames.
        self.noe_index = [0, 1, 2]
        self.r1_index =  [3, 4, 5]
        self.r2_index =  [6, 7, 8]

        # The calculation threads list.
        self.calc_threads = []

        # Initialise the GUI data.
        self.init_data()

        # Build the main window.
        self.build_main_window()

        # Build the menu bar.
        self.build_menu_bar()

        # Build the controller, but don't show it.
        self.controller = Controller(None, -1, "")

        # NOE 1 no. 1
        rx_data = ds.relax_gui.analyses[self.noe_index[0]]
        self.frame_1_statusbar = self.CreateStatusBar(3, 0)
        self.bitmap_1_copy_1 = wx.StaticBitmap(self.noe1, -1, wx.Bitmap(IMAGE_PATH+'noe.gif', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1 = wx.StaticText(self.noe1, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3 = wx.StaticText(self.noe1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1 = wx.TextCtrl(self.noe1, -1, str(rx_data.frq) )
        self.label_2_copy_copy_5 = wx.StaticText(self.noe1, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1 = wx.TextCtrl(self.noe1, -1, rx_data.sat_file)
        self.sat_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2 = wx.StaticText(self.noe1, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1 = wx.TextCtrl(self.noe1, -1, str(rx_data.sat_rmsd))
        self.label_2_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1 = wx.TextCtrl(self.noe1, -1, rx_data.sat_file)
        self.noe_ref_err_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1 = wx.StaticText(self.noe1, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1 = wx.TextCtrl(self.noe1, -1, str(rx_data.ref_rmsd))
        self.label_2_copy_copy_2_copy_1 = wx.StaticText(self.noe1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1 = StructureTextCtrl(self.noe1, -1, self.structure_file_pdb_msg)
        self.structure_noe1.SetEditable(False)
        self.ref_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1 = wx.TextCtrl(self.noe1, -1, "")
        self.label_2_copy_copy_3_copy_1 = wx.StaticText(self.noe1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1 = wx.TextCtrl(self.noe1, -1, rx_data.save_dir)
        self.chandir_noe1 = wx.Button(self.noe1, -1, "Change")
        self.label_2_copy_2 = wx.StaticText(self.noe1, -1, "")
        self.label_5_copy_1 = wx.StaticText(self.noe1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1 = wx.BitmapButton(self.noe1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #Noe no.2
        rx_data = ds.relax_gui.analyses[self.noe_index[1]]
        self.bitmap_1_copy_1_copy = wx.StaticBitmap(self.noe1_copy, -1, wx.Bitmap(IMAGE_PATH+'noe.gif', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3_copy = wx.StaticText(self.noe1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, str(rx_data.frq))
        self.label_2_copy_copy_5_copy = wx.StaticText(self.noe1_copy, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.sat_noe_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2_copy = wx.StaticText(self.noe1_copy, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1_copy = wx.TextCtrl(self.noe1_copy, -1, "1000")
        self.label_2_copy_copy_1_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.noe_ref_err_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1_copy = wx.TextCtrl(self.noe1_copy, -1, "1000")
        self.label_2_copy_copy_2_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1_copy = StructureTextCtrl(self.noe1_copy, -1, self.structure_file_pdb_msg)
        self.structure_noe1_copy.SetEditable(False)
        self.ref_noe_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.label_2_copy_copy_3_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, rx_data.save_dir)
        self.chandir_noe1_copy = wx.Button(self.noe1_copy, -1, "Change")
        self.label_2_copy_2_copy = wx.StaticText(self.noe1_copy, -1, "")
        self.label_5_copy_1_copy_1 = wx.StaticText(self.noe1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy = wx.BitmapButton(self.noe1_copy, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #NOE no. 3
        rx_data = ds.relax_gui.analyses[self.noe_index[2]]
        self.bitmap_1_copy_1_copy_1 = wx.StaticBitmap(self.noe1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'noe.gif', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, str(rx_data.frq))
        self.label_2_copy_copy_5_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.sat_noe_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "1000")
        self.label_2_copy_copy_1_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.noe_ref_err_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "1000")
        self.label_2_copy_copy_2_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1_copy_1 = StructureTextCtrl(self.noe1_copy_1, -1, self.structure_file_pdb_msg)
        self.structure_noe1_copy_1.SetEditable(False)
        self.ref_noe_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.label_2_copy_copy_3_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, rx_data.save_dir)
        self.chandir_noe1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Change")
        self.label_2_copy_2_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "")
        self.label_5_copy_1_copy_2 = wx.StaticText(self.noe1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy_1 = wx.BitmapButton(self.noe1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        # The automatic model-free protocol frame.
        self.analysis_frames[self.hardcoded_index_mf] = Auto_model_free(self, self.notebook_2)

        ## results
        self.label_11 = wx.StaticText(self.results, -1, "NOE analysis")
        self.list_noe = wx.ListBox(self.results, -1, choices=ds.relax_gui.results_noe)
        self.open_noe_results = wx.Button(self.results, -1, "open")
        self.label_11_copy = wx.StaticText(self.results, -1, "R1 and R2 relaxation analysis")
        self.list_rx = wx.ListBox(self.results, -1, choices=ds.relax_gui.results_rx)
        self.open_rx_results = wx.Button(self.results, -1, "open")
        self.label_11_copy_copy = wx.StaticText(self.results, -1, "Model-free analysis")
        self.list_modelfree = wx.ListBox(self.results, -1, choices=ds.relax_gui.results_model_free)
        self.open_model_results = wx.Button(self.results, -1, "open")

        self.__set_properties()
        self.__do_layout()

        #button actions
        self.Bind(wx.EVT_BUTTON, self.sat_noe1, self.sat_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe, self.noe_ref_err_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_noe1.open_file, self.ref_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe1, self.chandir_noe1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe1, self.relax_start_noe1)
        self.Bind(wx.EVT_BUTTON, self.sat_noe2, self.sat_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.ref_noe2, self.noe_ref_err_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_noe1_copy.open_file, self.ref_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe2, self.chandir_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_noe2, self.relax_start_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe3, self.sat_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe3, self.noe_ref_err_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_noe1_copy_1.open_file, self.ref_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe3, self.chandir_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe3, self.relax_start_noe1_copy_1)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_noe_results_exe, self.list_noe)
        self.Bind(wx.EVT_BUTTON, self.open_noe_results_exe, self.open_noe_results)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_rx_results_exe, self.list_rx)
        self.Bind(wx.EVT_BUTTON, self.open_rx_results_exe, self.open_rx_results)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_model_results_exe, self.list_modelfree)
        self.Bind(wx.EVT_BUTTON, self.open_model_results_exe, self.open_model_results)


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
        exec_relax_copy_1_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_copy_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_copy_1 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        exec_relax_copy_1_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
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
        noe_ref_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        exec_relax_copy_1_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_copy = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        exec_relax_copy_1_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
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
        noe_ref_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy = wx.BoxSizer(wx.HORIZONTAL)
        exec_relax_copy_1_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        exec_relax_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
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
        noe_ref_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1.Add(self.bitmap_1_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(self.label_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1.Add(self.label_2_copy_copy_copy_3, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1.Add(self.nmrfreq_value_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(nmr_freq_copy_1, 1, wx.EXPAND, 0)
        noe_sat_copy_1.Add(self.label_2_copy_copy_5, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1.Add(self.noe_sat_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1.Add(self.sat_noe_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(noe_sat_copy_1, 1, wx.EXPAND, 0)
        noe_sat_err_copy_1.Add(self.label_2_copy_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_err_copy_1.Add(self.noe_sat_err_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(noe_sat_err_copy_1, 1, wx.EXPAND, 0)
        noe_ref_copy_1.Add(self.label_2_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1.Add(self.noe_ref_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1.Add(self.noe_ref_err_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(noe_ref_copy_1, 1, wx.EXPAND, 0)
        sizer_8_copy_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_8_copy_copy_copy_copy_1.Add(self.noe_ref_err_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(sizer_8_copy_copy_copy_copy_1, 1, wx.EXPAND, 0)
        pdbfile_copy_1.Add(self.label_2_copy_copy_2_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1.Add(self.structure_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1.Add(self.ref_noe_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(pdbfile_copy_1, 1, wx.EXPAND, 0)
        unresolved_resi_copy_1.Add(self.label_2_copy_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        unresolved_resi_copy_1.Add(self.unres_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(unresolved_resi_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_1.Add(self.label_2_copy_copy_3_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1.Add(self.res_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1.Add(self.chandir_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(results_dir_copy_1, 1, wx.EXPAND, 0)
        sizer_2_copy_1.Add(self.label_2_copy_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(sizer_2_copy_1, 1, wx.EXPAND, 0)
        exec_relax_copy_1.Add(self.label_5_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1.Add(self.relax_start_noe1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(exec_relax_copy_1, 1, wx.ALIGN_RIGHT, 0)
        sizer_5_copy_1.Add(sizer_6_copy_1, 1, wx.EXPAND|wx.SHAPED, 0)
        self.noe1.SetSizer(sizer_5_copy_1)

        self.notebook_3.AddPage(self.noe1, "steady-state NOE")
        self.notebook_3.AddPage(self.analysis_frames[self.hardcoded_index_r1_1].parent, "R1 relaxation")
        self.notebook_3.AddPage(self.analysis_frames[self.hardcoded_index_r2_1].parent, "R2 relaxation")
        frq1sub.Add(self.notebook_3, 1, wx.EXPAND, 0)
        self.frq1.SetSizer(frq1sub)
        sizer_5_copy_1_copy.Add(self.bitmap_1_copy_1_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(self.label_4_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy.Add(self.label_2_copy_copy_copy_3_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy.Add(self.nmrfreq_value_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(nmr_freq_copy_1_copy, 1, wx.EXPAND, 0)
        noe_sat_copy_1_copy.Add(self.label_2_copy_copy_5_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy.Add(self.noe_sat_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy.Add(self.sat_noe_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(noe_sat_copy_1_copy, 1, wx.EXPAND, 0)
        noe_sat_err_copy_1_copy.Add(self.label_2_copy_copy_copy_copy_2_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_err_copy_1_copy.Add(self.noe_sat_err_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(noe_sat_err_copy_1_copy, 1, wx.EXPAND, 0)
        noe_ref_copy_1_copy.Add(self.label_2_copy_copy_1_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy.Add(self.noe_ref_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy.Add(self.noe_ref_err_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(noe_ref_copy_1_copy, 1, wx.EXPAND, 0)
        sizer_8_copy_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_8_copy_copy_copy_copy_1_copy.Add(self.noe_ref_err_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(sizer_8_copy_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)
        pdbfile_copy_1_copy.Add(self.label_2_copy_copy_2_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy.Add(self.structure_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy.Add(self.ref_noe_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(pdbfile_copy_1_copy, 1, wx.EXPAND, 0)
        unresolved_resi_copy_1_copy.Add(self.label_2_copy_copy_copy_1_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        unresolved_resi_copy_1_copy.Add(self.unres_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(unresolved_resi_copy_1_copy, 1, wx.EXPAND, 0)
        results_dir_copy_1_copy.Add(self.label_2_copy_copy_3_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy.Add(self.res_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy.Add(self.chandir_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(results_dir_copy_1_copy, 1, wx.EXPAND, 0)
        sizer_2_copy_1_copy.Add(self.label_2_copy_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(sizer_2_copy_1_copy, 1, wx.EXPAND, 0)
        exec_relax_copy_1_copy_1.Add(self.label_5_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_1.Add(self.relax_start_noe1_copy, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(exec_relax_copy_1_copy_1, 1, wx.ALIGN_RIGHT, 0)
        sizer_5_copy_1_copy.Add(sizer_6_copy_1_copy, 1, wx.EXPAND|wx.SHAPED, 0)
        self.noe1_copy.SetSizer(sizer_5_copy_1_copy)

        self.notebook_3_copy.AddPage(self.noe1_copy, "steady-state NOE")
        self.notebook_3_copy.AddPage(self.analysis_frames[self.hardcoded_index_r1_2].parent, "R1 relaxation")
        self.notebook_3_copy.AddPage(self.analysis_frames[self.hardcoded_index_r2_2].parent, "R2 relaxation")
        frq1sub_copy.Add(self.notebook_3_copy, 1, wx.EXPAND, 0)
        self.frq2.SetSizer(frq1sub_copy)
        sizer_5_copy_1_copy_1.Add(self.bitmap_1_copy_1_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(self.label_4_copy_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy_1.Add(self.label_2_copy_copy_copy_3_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy_1.Add(self.nmrfreq_value_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(nmr_freq_copy_1_copy_1, 1, wx.EXPAND, 0)
        noe_sat_copy_1_copy_1.Add(self.label_2_copy_copy_5_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy_1.Add(self.noe_sat_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy_1.Add(self.sat_noe_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(noe_sat_copy_1_copy_1, 1, wx.EXPAND, 0)
        noe_sat_err_copy_1_copy_1.Add(self.label_2_copy_copy_copy_copy_2_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_err_copy_1_copy_1.Add(self.noe_sat_err_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(noe_sat_err_copy_1_copy_1, 1, wx.EXPAND, 0)
        noe_ref_copy_1_copy_1.Add(self.label_2_copy_copy_1_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy_1.Add(self.noe_ref_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy_1.Add(self.noe_ref_err_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(noe_ref_copy_1_copy_1, 1, wx.EXPAND, 0)
        sizer_8_copy_copy_copy_copy_1_copy_1.Add(self.label_2_copy_copy_copy_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_8_copy_copy_copy_copy_1_copy_1.Add(self.noe_ref_err_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(sizer_8_copy_copy_copy_copy_1_copy_1, 1, wx.EXPAND, 0)
        pdbfile_copy_1_copy_1.Add(self.label_2_copy_copy_2_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy_1.Add(self.structure_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy_1.Add(self.ref_noe_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(pdbfile_copy_1_copy_1, 1, wx.EXPAND, 0)
        unresolved_resi_copy_1_copy_1.Add(self.label_2_copy_copy_copy_1_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        unresolved_resi_copy_1_copy_1.Add(self.unres_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(unresolved_resi_copy_1_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_1_copy_1.Add(self.label_2_copy_copy_3_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy_1.Add(self.res_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy_1.Add(self.chandir_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(results_dir_copy_1_copy_1, 1, wx.EXPAND, 0)
        sizer_2_copy_1_copy_1.Add(self.label_2_copy_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(sizer_2_copy_1_copy_1, 1, wx.EXPAND, 0)
        exec_relax_copy_1_copy_2.Add(self.label_5_copy_1_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_2.Add(self.relax_start_noe1_copy_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(exec_relax_copy_1_copy_2, 1, wx.ALIGN_RIGHT, 0)
        sizer_5_copy_1_copy_1.Add(sizer_6_copy_1_copy_1, 1, wx.EXPAND|wx.SHAPED, 0)
        self.noe1_copy_1.SetSizer(sizer_5_copy_1_copy_1)

        self.notebook_3_copy_1.AddPage(self.noe1_copy_1, "steady-state NOE")
        self.notebook_3_copy_1.AddPage(self.analysis_frames[self.hardcoded_index_r1_3].parent, "R1 relaxation")
        self.notebook_3_copy_1.AddPage(self.analysis_frames[self.hardcoded_index_r2_3].parent, "R2 relaxation")
        frq1sub_copy_1.Add(self.notebook_3_copy_1, 1, wx.EXPAND, 0)
        self.frq3.SetSizer(frq1sub_copy_1)
        sizer_22.Add(self.label_11, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_23.Add(self.list_noe, 0, wx.ADJUST_MINSIZE, 0)
        sizer_23.Add(self.open_noe_results, 0, wx.ADJUST_MINSIZE, 0)
        sizer_22.Add(sizer_23, 1, wx.LEFT|wx.EXPAND, 10)
        sizer_9.Add(sizer_22, 1, wx.EXPAND, 0)
        sizer_22_copy.Add(self.label_11_copy, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_23_copy.Add(self.list_rx, 0, wx.ADJUST_MINSIZE, 0)
        sizer_23_copy.Add(self.open_rx_results, 0, wx.ADJUST_MINSIZE, 0)
        sizer_22_copy.Add(sizer_23_copy, 1, wx.LEFT|wx.EXPAND, 10)
        sizer_9.Add(sizer_22_copy, 1, wx.EXPAND, 0)
        sizer_22_copy_copy.Add(self.label_11_copy_copy, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_23_copy_copy.Add(self.list_modelfree, 0, wx.ADJUST_MINSIZE, 0)
        sizer_23_copy_copy.Add(self.open_model_results, 0, wx.ADJUST_MINSIZE, 0)
        sizer_22_copy_copy.Add(sizer_23_copy_copy, 1, wx.LEFT|wx.EXPAND, 10)
        sizer_9.Add(sizer_22_copy_copy, 1, wx.EXPAND, 0)
        self.results.SetSizer(sizer_9)
        self.notebook_2.AddPage(self.frq1, "Frq. 1")
        self.notebook_2.AddPage(self.frq2, "Frq. 2")
        self.notebook_2.AddPage(self.frq3, "Frq. 3")
        self.notebook_2.AddPage(self.analysis_frames[self.hardcoded_index_mf].parent, "Model-free")
        self.notebook_2.AddPage(self.results, "Results")
        sizer_8.Add(self.notebook_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_8)
        self.Layout()
        self.SetSize((1000, 600))
        self.Centre()


    def __set_properties(self):
        # begin wxGlade: main.__set_properties
        self.SetTitle("relaxGUI " + GUI_version)
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((1000, 600))
        self.frame_1_statusbar.SetStatusWidths([800, 50, -1])
        # statusbar fields
        frame_1_statusbar_fields = ["relaxGUI (C) by Michael Bieri 2009", "relax:", version]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)

        self.label_4_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3.SetMinSize((230, 17))
        self.nmrfreq_value_noe1.SetMinSize((350, 27))
        self.label_2_copy_copy_5.SetMinSize((230, 17))
        self.noe_sat_1.SetMinSize((350, 27))
        self.sat_noe_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_2.SetMinSize((230, 17))
        self.noe_sat_err_1.SetMinSize((350, 27))
        self.label_2_copy_copy_1_copy_1.SetMinSize((230, 17))
        self.noe_ref_1.SetMinSize((350, 27))
        self.noe_ref_err_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_copy_1.SetMinSize((230, 17))
        self.noe_ref_err_1.SetMinSize((350, 27))
        self.label_2_copy_copy_2_copy_1.SetMinSize((230, 17))
        self.structure_noe1.SetMinSize((350, 27))
        self.ref_noe_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_1_copy_1.SetMinSize((230, 34))
        self.unres_noe1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_1.SetMinSize((230, 17))
        self.res_noe1.SetMinSize((350, 27))
        self.chandir_noe1.SetMinSize((103, 27))
        self.label_5_copy_1.SetMinSize((118, 17))
        self.relax_start_noe1.SetName('hello')
        self.relax_start_noe1.SetSize(self.relax_start_noe1.GetBestSize())

        self.label_4_copy_1_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3_copy.SetMinSize((230, 17))
        self.nmrfreq_value_noe1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_5_copy.SetMinSize((230, 17))
        self.noe_sat_1_copy.SetMinSize((350, 27))
        self.sat_noe_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_2_copy.SetMinSize((230, 17))
        self.noe_sat_err_1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_1_copy_1_copy.SetMinSize((230, 17))
        self.noe_ref_1_copy.SetMinSize((350, 27))
        self.noe_ref_err_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_copy_1_copy.SetMinSize((230, 17))
        self.noe_ref_err_1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_2_copy_1_copy.SetMinSize((230, 17))
        self.structure_noe1_copy.SetMinSize((350, 27))
        self.ref_noe_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_1_copy_1_copy.SetMinSize((230, 34))
        self.unres_noe1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_1_copy.SetMinSize((230, 17))
        self.res_noe1_copy.SetMinSize((350, 27))
        self.chandir_noe1_copy.SetMinSize((103, 27))
        self.label_5_copy_1_copy_1.SetMinSize((118, 17))
        self.relax_start_noe1_copy.SetName('hello')
        self.relax_start_noe1_copy.SetSize(self.relax_start_noe1_copy.GetBestSize())

        self.label_4_copy_1_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3_copy_1.SetMinSize((230, 17))
        self.nmrfreq_value_noe1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_5_copy_1.SetMinSize((230, 17))
        self.noe_sat_1_copy_1.SetMinSize((350, 27))
        self.sat_noe_copy_1_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_2_copy_1.SetMinSize((230, 17))
        self.noe_sat_err_1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_1_copy_1_copy_1.SetMinSize((230, 17))
        self.noe_ref_1_copy_1.SetMinSize((350, 27))
        self.noe_ref_err_copy_1_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_copy_1_copy_1.SetMinSize((230, 17))
        self.noe_ref_err_1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_2_copy_1_copy_1.SetMinSize((230, 17))
        self.structure_noe1_copy_1.SetMinSize((350, 27))
        self.ref_noe_copy_1_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_1_copy_1_copy_1.SetMinSize((230, 34))
        self.unres_noe1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_1_copy_1.SetMinSize((230, 17))
        self.res_noe1_copy_1.SetMinSize((350, 27))
        self.chandir_noe1_copy_1.SetMinSize((103, 27))
        self.label_5_copy_1_copy_2.SetMinSize((118, 17))
        self.relax_start_noe1_copy_1.SetName('hello')
        self.relax_start_noe1_copy_1.SetSize(self.relax_start_noe1_copy_1.GetBestSize())


    def aboutGUI(self, event): # About
        about_relax()
        event.Skip()


    def aboutrelax(self, event): # abour relax
        webbrowser.open_new('http://www.nmr-relax.com')
        event.Skip()


    def build_main_window(self):
        """Construct the main relax GUI window."""

        self.notebook_2 = wx.Notebook(self, -1, style=wx.NB_LEFT)
        self.results = wx.Panel(self.notebook_2, -1)

        # The 5th notebook (freq 3).
        self.frq3 = wx.Panel(self.notebook_2, -1)
        self.notebook_3_copy_1 = wx.Notebook(self.frq3, -1, style=0)

        # The automatic relaxation data analysis frames.
        self.analysis_frames[self.hardcoded_index_r1_3] = Auto_r1(self, self.notebook_3_copy_1, hardcoded_index=self.r1_index[2])
        self.analysis_frames[self.hardcoded_index_r2_3] = Auto_r2(self, self.notebook_3_copy_1, hardcoded_index=self.r2_index[2])
        self.noe1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)

        # The 4th notebook (freq 2).
        self.frq2 = wx.Panel(self.notebook_2, -1)
        self.notebook_3_copy = wx.Notebook(self.frq2, -1, style=0)

        # The automatic relaxation data analysis frames.
        self.analysis_frames[self.hardcoded_index_r1_2] = Auto_r1(self, self.notebook_3_copy, hardcoded_index=self.r1_index[1])
        self.analysis_frames[self.hardcoded_index_r2_2] = Auto_r2(self, self.notebook_3_copy, hardcoded_index=self.r2_index[1])
        self.noe1_copy = wx.Panel(self.notebook_3_copy, -1)

        # The 3rd notebook (freq 1).
        self.frq1 = wx.Panel(self.notebook_2, -1)
        self.notebook_3 = wx.Notebook(self.frq1, -1, style=0)

        # The automatic relaxation data analysis frames.
        self.analysis_frames[self.hardcoded_index_r1_1] = Auto_r1(self, self.notebook_3, hardcoded_index=self.r1_index[0])
        self.analysis_frames[self.hardcoded_index_r2_1] = Auto_r2(self, self.notebook_3, hardcoded_index=self.r2_index[0])
        self.noe1 = wx.Panel(self.notebook_3, -1)


    def build_menu_bar(self):
        """Build the menu bar."""

        # Create the menu bar GUI item and add it to the main frame.
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # The 'File' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=0, text="&New", icon=NEW_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=1, text="&Open", icon=OPEN_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=2, text="S&ave as...", icon=SAVE_AS_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=3, text="E&xit", icon=EXIT_ICON))
        menubar.Append(menu, "&File")

        # The 'File' menu actions.
        self.Bind(wx.EVT_MENU, self.newGUI,     id=0)
        self.Bind(wx.EVT_MENU, self.state_load, id=1)
        self.Bind(wx.EVT_MENU, self.state_save, id=2)
        self.Bind(wx.EVT_MENU, self.exitGUI,    id=3)

        # The 'View' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=50, text="&Controller", icon=CONTROLLER_ICON))
        menubar.Append(menu, "&View")

        # The 'View' actions.
        self.Bind(wx.EVT_MENU, self.show_controller,    id=50)

        # The 'Molecule' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=10, text="Load &PDB File", icon=LOAD_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=11, text="Load se&quence file", icon=LOAD_ICON))
        menubar.Append(menu, "&Molecule")

        # The 'Molecule' menu actions.
        #self.Bind(wx.EVT_MENU, self.structure_pdb,  id=10)
        self.Bind(wx.EVT_MENU, self.import_seq,     id=11)

        # The 'Settings' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=20, text="&Global relax settings", icon=SETTINGS_GLOBAL_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=21, text="&Parameter file settings", icon=SETTINGS_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=22, text="Reset a&ll settings", icon=SETTINGS_RESET_ICON))
        menubar.Append(menu, "&Settings")

        # The 'Settings' menu actions.
        self.Bind(wx.EVT_MENU, self.settings,           id=20)
        self.Bind(wx.EVT_MENU, self.param_file_setting, id=21)
        self.Bind(wx.EVT_MENU, self.reset_setting,      id=22)

        # The 'Extras' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=30, text="&Contact relaxGUI", icon=CONTACT_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=31, text="&References", icon=REF_ICON))
        menubar.Append(menu, "&Extras")

        # The 'Extras' menu actions.
        self.Bind(wx.EVT_MENU, self.references, id=31)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=40, text="&Manual", icon=MANUAL_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=41, text="About relaxG&UI", icon=ABOUT_RELAXGUI_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=42, text="About rela&x", icon=ABOUT_RELAX_ICON))
        menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.Bind(wx.EVT_MENU, self.aboutGUI,   id=41)
        self.Bind(wx.EVT_MENU, self.aboutrelax, id=42)


    def build_menu_sub_item(self, id=None, text=None, icon=None, kind=wx.ITEM_NORMAL):
        """Construct and return the menu sub-item.

        @keyword id:    The element identification number.
        @type id:       int
        @keyword text:  The text for the menu entry.
        @type text:     str
        @keyword icon:  The bitmap icon path.
        @type icon:     str
        @keyword kind:  The item type, which defaults to wx.ITEM_NORMAL.
        @type kind:     int
        @return:        The initialised wx.MenuItem() instance.
        @rtype:         wx.MenuItem() instance
        """

        # Initialise the GUI element.
        element = wx.MenuItem()

        # Set up the element.
        element.SetId(id)
        element.SetBitmap(wx.Bitmap(icon))
        element.SetText(text)
        element.SetKind(kind)

        # Return the element.
        return element


    def exec_noe1(self, event): # Start NOE calculation no. 1
        start_relax = exec_relax()

        if start_relax == True:
            start_noe(self.res_noe1.GetValue(), self.noe_ref_1.GetValue(), self.noe_sat_1.GetValue(), self.noe_ref_err_1.GetValue(), self.noe_sat_err_1.GetValue(), self.nmrfreq_value_noe1.GetValue(), self.structure_noe1.GetValue(), self.unres_noe1.GetValue(), start_relax, self, 1, global_setting, file_setting, sequencefile)
        event.Skip()


    def exec_noe2(self, event): # start noe 2 calculation
        start_relax = exec_relax()
        if start_relax == True:
            start_noe(self.res_noe1_copy.GetValue(), self.noe_ref_1_copy.GetValue(), self.noe_sat_1_copy.GetValue(), self.noe_ref_err_1_copy.GetValue(), self.noe_sat_err_1_copy.GetValue(), self.nmrfreq_value_noe1_copy.GetValue(), self.structure_noe1_copy.GetValue(), self.unres_noe1_copy.GetValue(), start_relax, self, 2, global_setting, file_setting, sequencefile)
        event.Skip()


    def exec_noe3(self, event): # calculate noe 3
        start_relax = exec_relax()
        if start_relax == True:
            start_noe(self.res_noe1_copy_1.GetValue(), self.noe_ref_1_copy_1.GetValue(), self.noe_sat_1_copy_1.GetValue(), self.noe_ref_err_1_copy_1.GetValue(), self.noe_sat_err_1_copy_1.GetValue(), self.nmrfreq_value_noe1_copy_1.GetValue(), self.structure_noe1_copy_1.GetValue(), self.unres_noe1_copy_1.GetValue(), start_relax, self, 3, global_setting, file_setting, sequencefile)
        event.Skip()


    def exitGUI(self, event): # Exit
        doexit = question('Do you wand to quit relaxGUI?')
        if doexit == True:
            print"\n==================================================\n\n"
            print "\nThank you for citing:"
            print ""
            print "relaxGUI:\nin progress...."
            print ""
            print "relax:"
            print "d'Auvergne, E.J. and Gooley, P.R. (2008). Optimisation of NMR dynamic models I. Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces. J. Biomol. NMR, 40(2), 107-119."
            print "d'Auvergne, E.J. and Gooley, P.R. (2008). Optimisation of NMR dynamic models II. A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor. J. Biomol. NMR, 40(2), 121-133."
            print "\nExiting relaxGUI......\n"
            sys.exit(0)
        event.Skip()


    def import_seq(self, event): # open load sequence panel
        global sequencefile  #load global variable
        temp = load_sequence(self)
        if not temp == None:
            sequencefile = temp #set sequence file

            # set entries in pdb text box
            structure_file_pdb = '!!! Sequence file selected !!!'
            self.structure_noe1.SetValue(structure_file_pdb)
            self.structure_noe1_copy.SetValue(structure_file_pdb)
            self.structure_noe1_copy_1.SetValue(structure_file_pdb)
        event.Skip()


    def init_data(self):
        """Initialise the data used by the GUI interface."""

        # Add the GUI object to the data store.
        ds.relax_gui = Gui()

        # Define Global Variables
        ds.relax_gui.unresolved = ""
        ds.relax_gui.results_noe = []
        ds.relax_gui.results_rx = []
        ds.relax_gui.results_model_free = []
        ds.relax_gui.global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
        ds.relax_gui.file_setting = ['0', '1', '2', '3', '4', '5', '6']
        ds.relax_gui.sequencefile = ''

        # Table of relax Results
        ds.relax_gui.table_residue = []
        ds.relax_gui.table_model = []
        ds.relax_gui.table_s2 = []
        ds.relax_gui.table_rex = []
        ds.relax_gui.table_te = []

        # Initialise the 3 NOE analyses.
        nmrfreq = [600, 800, 900]
        for i in range(3):
            # Add the element.
            ds.relax_gui.analyses.add('NOE')

            # Initialise the variables.
            ds.relax_gui.analyses[-1].frq = nmrfreq[i]
            ds.relax_gui.analyses[-1].ref_file = ''
            ds.relax_gui.analyses[-1].sat_file = ''
            ds.relax_gui.analyses[-1].ref_rmsd = 1000
            ds.relax_gui.analyses[-1].sat_rmsd = 1000

        # Initialise the 3 R1 and 3 R2 analyses.
        rx = ['R1']*3 + ['R2']*3
        nmrfreq = nmrfreq * 2
        for i in range(len(rx)):
            # Add the element.
            ds.relax_gui.analyses.add(rx[i])

            # Initialise the variables.
            ds.relax_gui.analyses[-1].frq = nmrfreq[i]
            ds.relax_gui.analyses[-1].num = 0
            ds.relax_gui.analyses[-1].file_list = []
            ds.relax_gui.analyses[-1].relax_times = []

        # Initialise all the source and save directories.
        for i in range(len(ds.relax_gui.analyses)):
            ds.relax_gui.analyses[i].source_dir = getcwd()
            ds.relax_gui.analyses[i].save_dir = getcwd()


    def newGUI(self, event): # New
        newdir = opendir('Select results directory', '*')
        if not newdir == None:
            #create directories
            mkdir(newdir + sep + 'NOE_1')
            mkdir(newdir + sep + 'NOE_2')
            mkdir(newdir + sep + 'NOE_3')
            mkdir(newdir + sep + 'R1_1')
            mkdir(newdir + sep + 'R1_2')
            mkdir(newdir + sep + 'R1_3')
            mkdir(newdir + sep + 'R2_1')
            mkdir(newdir + sep + 'R2_2')
            mkdir(newdir + sep + 'R2_3')
            mkdir(newdir + sep + 'model_free')

            #insert directories in set up menu
            self.res_noe1.SetValue(newdir + sep + 'NOE_1')
            self.res_noe1_copy.SetValue(newdir + sep + 'NOE_2')
            self.res_noe1_copy_1.SetValue(newdir + sep + 'NOE_3')
            self.resultsdir_r11.SetValue(newdir + sep + 'R1_1')
            self.resultsdir_r11_copy.SetValue(newdir + sep + 'R1_2')
            self.resultsdir_r11_copy_1.SetValue(newdir + sep + 'R1_3')
            self.resultsdir_r21.SetValue(newdir + sep + 'R2_1')
            self.resultsdir_r21_copy.SetValue(newdir + sep + 'R2_2')
            self.resultsdir_r21_copy_1.SetValue(newdir + sep + 'R2_3')
            self.resultsdir_r21_copy_2.SetValue(newdir + sep + 'model_free')

            dir_message('Folder structure created for Model-free analysis:\n\n\n' + newdir + sep + 'NOE_1\n' + newdir + sep + 'NOE_2\n' + newdir + sep + 'NOE_3\n' + newdir + sep + 'R1_1\n' + newdir + sep + 'R1_2\n' + newdir + sep + 'R1_3\n' + newdir + sep + 'R2_1\n' + newdir + sep + 'R2_2\n' + newdir + sep + 'R2_3\n' + newdir + sep + 'model-free')
        event.Skip()


    def open_model_results_exe(self, event):    # open model-free results
        choice = self.list_modelfree.GetStringSelection()
        model_result = [table_residue, table_model, table_s2, table_rex, table_te] # relax results values
        see_results(choice, model_result)
        event.Skip()


    def open_noe_results_exe(self, event): #open results of noe run
        choice = self.list_noe.GetStringSelection()
        see_results(choice, None)
        event.Skip()


    def open_rx_results_exe(self, event): # open results of r1 and r2 runs
        choice = self.list_rx.GetStringSelection()
        see_results(choice, None)
        event.Skip()


    def param_file_setting(self, event): # set up parameter files
        global file_setting # import global variable
        tmp_setting = import_file_settings(file_setting)
        if not tmp_setting == None:
            if question('Do you realy want to change import file settings?'):
                file_setting = tmp_setting
        event.Skip()


    def ref_noe(self, event):
        """Select the reference noe 1 file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original value.
        backup = self.noe_ref_1.GetValue()

        # Alias the data container.
        cont = ds.relax_gui.analyses[self.noe_index[0]]

        # Select the file.
        cont.ref_file = openfile(msg='Select reference NOE', filetype='*.*', default='all files (*.*)|*.*')

        # Restore the backup file if no file was chosen.
        if cont.ref_file == None:
            cont.ref_file = backup

        # Place the file path in the text box.
        self.noe_ref_1.SetValue(cont.ref_file)

        # Skip the event.
        event.Skip()


    def ref_noe2(self, event):
        """Select the reference noe 2 file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original value.
        backup = self.noe_ref_1_copy.GetValue()

        # Alias the data container.
        cont = ds.relax_gui.analyses[self.noe_index[1]]

        # Select the file.
        cont.ref_file = openfile(msg='Select reference NOE', filetype='*.*', default='all files (*.*)|*.*')

        # Restore the backup file if no file was chosen.
        if cont.ref_file == None:
            cont.ref_file = backup

        # Place the file path in the text box.
        self.noe_ref_1_copy.SetValue(cont.ref_file)

        # Skip the event.
        event.Skip()


    def ref_noe3(self, event):
        """Select the reference noe 3 file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original value.
        backup = self.noe_ref_1_copy_1.GetValue()

        # Alias the data container.
        cont = ds.relax_gui.analyses[self.noe_index[2]]

        # Select the file.
        cont.ref_file = openfile(msg='Select reference NOE', filetype='*.*', default='all files (*.*)|*.*')

        # Restore the backup file if no file was chosen.
        if cont.ref_file == None:
            cont.ref_file = backup

        # Place the file path in the text box.
        self.noe_ref_1_copy_1.SetValue(cont.ref_file)

        # Skip the event.
        event.Skip()


    def references(self, event):
        webbrowser.open_new('http://www.nmr-relax.com/refs.html')
        event.Skip()


    def resdir_modelfree(self, event):
        backup = self.resultsdir_r21_copy_2.GetValue()
        results_dir_model = opendir('Select results directory', backup)
        if results_dir_model == None:
            results_dir_model = backup
        self.resultsdir_r21_copy_2.SetValue(results_dir_model)
        event.Skip()


    def resdir_noe1(self, event): # noe 1 results dir
        backup = self.res_noe1.GetValue()
        noe_savedir[0] = opendir('Select results directory', self.res_noe1.GetValue())
        if noe_savedir[0] == None:
            noe_savedir[0] = backup
        self.res_noe1.SetValue(noe_savedir[0])
        event.Skip()


    def resdir_noe2(self, event): # noe results dir no. 2
        backup = self.res_noe1_copy.GetValue()
        noe_savedir[1] = opendir('Select results directory', self.res_noe1_copy.GetValue())
        if noe_savedir[1] == None:
            noe_savedir[1] = backup
        self.res_noe1_copy.SetValue(noe_savedir[1])
        event.Skip()


    def resdir_noe3(self, event): # noe 3 results dir
        backup = self.res_noe1_copy_1.GetValue()
        noe_savedir[2] = opendir('Select results directory', self.res_noe1_copy_1.GetValue() + sep)
        if noe_savedir[2] == None:
            noe_savedir[2] = backup
        self.res_noe1_copy_1.SetValue(noe_savedir[2])
        event.Skip()


    def reset_setting(self, event): #reset all settings
        global global_setting #import global variable
        global file_setting # import global variable
        if question('Do you realy want to change relax settings?'):
            global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
            file_setting = ['0', '1', '2', '3', '4', '5', '6']


    def sat_noe1(self, event):
        """Select the saturated noe 1 file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original value.
        backup = self.noe_sat_1.GetValue()

        # Alias the data container.
        cont = ds.relax_gui.analyses[self.noe_index[0]]

        # Select the file.
        cont.sat_file = openfile(msg='Select saturated NOE', filetype='*.*', default='all files (*.*)|*.*')

        # Restore the backup file if no file was chosen.
        if cont.sat_file == None:
            cont.sat_file = backup

        # Place the file path in the text box.
        self.noe_sat_1.SetValue(cont.sat_file)

        # Skip the event.
        event.Skip()


    def sat_noe2(self, event):
        """Select the saturated noe 2 file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original value.
        backup = self.noe_sat_1_copy.GetValue()

        # Alias the data container.
        cont = ds.relax_gui.analyses[self.noe_index[1]]

        # Select the file.
        cont.sat_file = openfile(msg='Select saturated NOE', filetype='*.*', default='all files (*.*)|*.*')

        # Restore the backup file if no file was chosen.
        if cont.sat_file == None:
            cont.sat_file = backup

        # Place the file path in the text box.
        self.noe_sat_1_copy.SetValue(cont.sat_file)

        # Skip the event.
        event.Skip()


    def sat_noe3(self, event):
        """Select the saturated noe 3 file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original value.
        backup = self.noe_sat_1_copy_1.GetValue()

        # Alias the data container.
        cont = ds.relax_gui.analyses[self.noe_index[2]]

        # Select the file.
        cont.sat_file = openfile(msg='Select saturated NOE', filetype='*.*', default='all files (*.*)|*.*')

        # Restore the backup file if no file was chosen.
        if cont.sat_file == None:
            cont.sat_file = backup

        # Place the file path in the text box.
        self.noe_sat_1_copy_1.SetValue(cont.sat_file)

        # Skip the event.
        event.Skip()


    def settings(self, event): # set up for relax variables
        global global_setting #import global variable
        tmp_global = relax_global_settings(global_setting)
        if not tmp_global == None:
            if question('Do you realy want to change relax settings?'):
                global_setting = tmp_global
        event.Skip()


    def show_controller(self, event):
        """Display the relax controller window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the window.
        self.controller.Show()

        # Terminate the event.
        event.Skip()


    def state_load(self, event):
        """Load the program state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the dialog.
        filename = openfile(msg='Select file to open', filetype='state.bz2', default='relax save files (*.bz2)|*.bz2|all files (*.*)|*.*')

        # No file has been selected.
        if not filename:
            # Skip the event.
            event.Skip()

            # Don't do anything.
            return

        # Reset the relax data store.
        reset()

        # Load the relax state.
        state.load_state(filename, verbosity=0)

        # FIXME: (commented out until analyses are dynamically loaded and unloaded).
        ## Build the analysis frames
        #for i in range(len(ds.relax_gui.analyses)):
        #    # The automatic model-free protocol frame
        #    if ds.relax_gui.analyses[i].analysis_type == 'model-free':
        #        self.analysis_frames.append(Auto_model_free(self))

        # FIXME:  Temporary fix - set the data structures explicitly.
        self.analysis_frames[self.hardcoded_index_r1_1].link_data(ds.relax_gui.analyses[self.r1_index[0]])
        self.analysis_frames[self.hardcoded_index_r1_2].link_data(ds.relax_gui.analyses[self.r1_index[1]])
        self.analysis_frames[self.hardcoded_index_r1_3].link_data(ds.relax_gui.analyses[self.r1_index[2]])
        self.analysis_frames[self.hardcoded_index_r2_1].link_data(ds.relax_gui.analyses[self.r2_index[0]])
        self.analysis_frames[self.hardcoded_index_r2_2].link_data(ds.relax_gui.analyses[self.r2_index[1]])
        self.analysis_frames[self.hardcoded_index_r2_3].link_data(ds.relax_gui.analyses[self.r2_index[2]])
        self.analysis_frames[self.hardcoded_index_mf].link_data(ds.relax_gui.analyses[9])

        # Update the core of the GUI to match the new data store.
        self.sync_ds(upload=False)

        # Execute the analysis frame specific update methods.
        for analysis in self.analysis_frames:
            if hasattr(analysis, 'sync_ds'):
                analysis.sync_ds(upload=False)

        # Skip the event.
        event.Skip()


    def state_save(self, event):
        """Save the program state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the dialog.
        filename = savefile(msg='Select file to save', filetype='state.bz2', default='relax save files (*.bz2)|*.bz2|all files (*.*)|*.*')

        # Update the data store to match the GUI.
        self.sync_ds(upload=True)

        # Analyses updates of the new data store.
        for i in range(len(self.analysis_frames)):
            # Execute the analysis frame specific update methods.
            if hasattr(self.analysis_frames[i], 'sync_ds'):
                self.analysis_frames[i].sync_ds(upload=True)

        # Save the relax state.
        state.save_state(filename, verbosity=0, force=True)

        # Skip the event.
        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the GUI and the relax data store, both ways.

        This method allows the GUI information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the GUI.

        @keyword upload:    A flag which if True will cause the GUI to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the GUI.
        @type upload:       bool
        """

        # Dummy function (for the time being).
