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
from float import floatAsByteArray
from generic_fns import pipes
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from relax_errors import RelaxError
from version import version

# relaxGUI module imports.
from about import about_relax
from analyses.auto_model_free import Auto_model_free
from analyses.project import create_save_file, open_file
from analyses.relax_control import start_modelfree, start_noe, start_rx
from analyses.results_analysis import color_code_noe, model_free_results, results_table, see_results
from analyses.select_model_calc import check_entries, whichmodel
from derived_wx_classes import StructureTextCtrl
from filedialog import multi_openfile, opendir, openfile, savefile
from message import dir_message, exec_relax, missing_data, question, relax_run_ok
from paths import ABOUT_RELAX_ICON, ABOUT_RELAXGUI_ICON, CONTACT_ICON, EXIT_ICON, IMAGE_PATH, LOAD_ICON, MANUAL_ICON, NEW_ICON, OPEN_ICON, REF_ICON, SAVE_AS_ICON, SETTINGS_ICON, SETTINGS_GLOBAL_ICON, SETTINGS_RESET_ICON
from settings import import_file_settings, load_sequence, relax_global_settings


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# Variables

######################
GUI_version = '1.00'
######################

# Define Global Variables
unresolved = ""
results_noe = []
results_rx = []
results_model_free = []
global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
file_setting = ['0', '1', '2', '3', '4', '5', '6']
sequencefile = ''
LOCAL_TM = False

# Table of relax Results
table_residue = []
table_model = []
table_s2 = []
table_rex = []
table_te = []

#NOE3 variables
noeref = ["","",""]
noesat = ["","",""]
noerefrmsd = [1000, 1000, 1000]
noesatrmsd = [1000, 1000, 1000]
nmrfreq = [600, 800, 900]
noe_sourcedir = [getcwd(),getcwd(),getcwd()]
noe_savedir = [getcwd(),getcwd(),getcwd()]

#R1 variables
r1_num = 0
r1_list = []
r1_list2 = []
r1_list3 = []
r1_time = []
r1_time2 = []
r1_time3 = []
r1_sourcedir = [getcwd(),getcwd(),getcwd()]
r1_savedir = [getcwd(),getcwd(),getcwd()]

#R2 variables
r2_num = 0
r2_list = []
r2_list2 = []
r2_list3 = []
r2_time = []
r2_time2 = []
r2_time3 = []
r2_sourcedir = [getcwd(),getcwd(),getcwd()]
r2_savedir = [getcwd(),getcwd(),getcwd()]


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# generating the GUI


class Main(wx.Frame):
    """The main GUI class."""

    # Hard coded variables.
    structure_file_pdb_msg = "please insert .pdb file"

    def __init__(self, *args, **kwds):
        # begin
        kwds["style"] = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.notebook_2 = wx.Notebook(self, -1, style=wx.NB_LEFT)
        self.results = wx.Panel(self.notebook_2, -1)
        self.modelfree = wx.Panel(self.notebook_2, -1)
        self.frq3 = wx.Panel(self.notebook_2, -1)
        self.notebook_3_copy_1 = wx.Notebook(self.frq3, -1, style=0)
        self.r2_1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)
        self.panel_1_copy_copy_1 = wx.Panel(self.r2_1_copy_1, -1)
        self.panel_3_copy_copy_1 = wx.Panel(self.panel_1_copy_copy_1, -1)
        self.r1_1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)
        self.panel_1_copy_2 = wx.Panel(self.r1_1_copy_1, -1)
        self.panel_3_copy_2 = wx.Panel(self.panel_1_copy_2, -1)
        self.noe1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)
        self.frq2 = wx.Panel(self.notebook_2, -1)
        self.notebook_3_copy = wx.Notebook(self.frq2, -1, style=0)
        self.r2_1_copy = wx.Panel(self.notebook_3_copy, -1)
        self.panel_1_copy_copy = wx.Panel(self.r2_1_copy, -1)
        self.panel_3_copy_copy = wx.Panel(self.panel_1_copy_copy, -1)
        self.r1_1_copy = wx.Panel(self.notebook_3_copy, -1)
        self.panel_1_copy_1 = wx.Panel(self.r1_1_copy, -1)
        self.panel_3_copy_1 = wx.Panel(self.panel_1_copy_1, -1)
        self.noe1_copy = wx.Panel(self.notebook_3_copy, -1)
        self.frq1 = wx.Panel(self.notebook_2, -1)
        self.notebook_3 = wx.Notebook(self.frq1, -1, style=0)
        self.r2_1 = wx.Panel(self.notebook_3, -1)
        self.panel_1_copy = wx.Panel(self.r2_1, -1)
        self.panel_3_copy = wx.Panel(self.panel_1_copy, -1)
        self.r1_1 = wx.Panel(self.notebook_3, -1)
        self.panel_1 = wx.Panel(self.r1_1, -1)
        self.panel_3 = wx.Panel(self.panel_1, -1)
        self.noe1 = wx.Panel(self.notebook_3, -1)


        # Menu Bar
        ##########

        # Create the menu bar GUI item and add it to the main frame.
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # The 'File' menu.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=1, text="&New", icon=NEW_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=2, text="&Open", icon=OPEN_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=3, text="S&ave as...", icon=SAVE_AS_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=4, text="E&xit", icon=EXIT_ICON))
        menubar.Append(menu, "&File")

        # The 'Molecule' menu.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=11, text="Load &PDB File", icon=LOAD_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=12, text="Load se&quence file", icon=LOAD_ICON))
        menubar.Append(menu, "&Molecule")

        # The 'Settings' menu.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=7, text="&Global relax settings", icon=SETTINGS_GLOBAL_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=13, text="&Parameter file settings", icon=SETTINGS_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=14, text="Reset a&ll settings", icon=SETTINGS_RESET_ICON))
        menubar.Append(menu, "&Settings")

        # The 'Extras' menu.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=8, text="&Contact relaxGUI", icon=CONTACT_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=9, text="&References", icon=REF_ICON))
        menubar.Append(menu, "&Extras")

        # The 'Help' menu.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(id=10, text="&Manual", icon=MANUAL_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=5, text="About relaxG&UI", icon=ABOUT_RELAXGUI_ICON))
        menu.AppendItem(self.build_menu_sub_item(id=6, text="About rela&x", icon=ABOUT_RELAX_ICON))
        menubar.Append(menu, "&Help")


        # NOE 1 no. 1
        self.frame_1_statusbar = self.CreateStatusBar(3, 0)
        self.bitmap_1_copy_1 = wx.StaticBitmap(self.noe1, -1, wx.Bitmap(IMAGE_PATH+'noe.gif', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1 = wx.StaticText(self.noe1, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3 = wx.StaticText(self.noe1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1 = wx.TextCtrl(self.noe1, -1, str(nmrfreq[0]) )
        self.label_2_copy_copy_5 = wx.StaticText(self.noe1, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1 = wx.TextCtrl(self.noe1, -1, noesat[0])
        self.sat_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2 = wx.StaticText(self.noe1, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1 = wx.TextCtrl(self.noe1, -1, str(noesatrmsd[0]))
        self.label_2_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1 = wx.TextCtrl(self.noe1, -1, noeref[0])
        self.noe_ref_err_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1 = wx.StaticText(self.noe1, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1 = wx.TextCtrl(self.noe1, -1, str(noerefrmsd[0]))
        self.label_2_copy_copy_2_copy_1 = wx.StaticText(self.noe1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1 = StructureTextCtrl(self.noe1, -1, self.structure_file_pdb_msg)
        self.structure_noe1.SetEditable(False)
        self.ref_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1 = wx.TextCtrl(self.noe1, -1, "")
        self.label_2_copy_copy_3_copy_1 = wx.StaticText(self.noe1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1 = wx.TextCtrl(self.noe1, -1, noe_savedir[0])
        self.chandir_noe1 = wx.Button(self.noe1, -1, "Change")
        self.label_2_copy_2 = wx.StaticText(self.noe1, -1, "")
        self.label_5_copy_1 = wx.StaticText(self.noe1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1 = wx.BitmapButton(self.noe1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        # R1 no. 1
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.r1_1, -1, wx.Bitmap(IMAGE_PATH+'r1.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy = wx.StaticText(self.r1_1, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy = wx.StaticText(self.r1_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11 = wx.TextCtrl(self.r1_1, -1, str(nmrfreq[0]))
        self.label_2_copy_copy_3_copy_copy = wx.StaticText(self.r1_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11 = wx.TextCtrl(self.r1_1, -1, r1_savedir[0])
        self.results_directory_copy_copy = wx.Button(self.r1_1, -1, "Change")
        self.structure_file = wx.StaticText(self.r1_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11 = StructureTextCtrl(self.r1_1, -1, self.structure_file_pdb_msg)
        self.structure_r11.SetEditable(False)
        self.results_directory_copy_copy_copy = wx.Button(self.r1_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy = wx.StaticText(self.r1_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r11 = wx.TextCtrl(self.r1_1, -1, "")
        self.panel_2 = wx.Panel(self.r1_1, -1)
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
        self.label_5_copy_1_copy = wx.StaticText(self.r1_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1 = wx.BitmapButton(self.r1_1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #R2 no. 1
        self.bitmap_1_copy_copy_copy = wx.StaticBitmap(self.r2_1, -1, wx.Bitmap(IMAGE_PATH+'r2.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy = wx.StaticText(self.r2_1, -1, "Set-up for R2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1 = wx.StaticText(self.r2_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r21 = wx.TextCtrl(self.r2_1, -1, str(nmrfreq[0]))
        self.label_2_copy_copy_3_copy_copy_copy = wx.StaticText(self.r2_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21 = wx.TextCtrl(self.r2_1, -1, r2_savedir[0])
        self.results_directory_r21 = wx.Button(self.r2_1, -1, "Change")
        self.structure_file_copy = wx.StaticText(self.r2_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21 = StructureTextCtrl(self.r2_1, -1, self.structure_file_pdb_msg)
        self.structure_r21.SetEditable(False)
        self.chan_struc_r21 = wx.Button(self.r2_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy = wx.StaticText(self.r2_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r21 = wx.TextCtrl(self.r2_1, -1, "")
        self.panel_2_copy = wx.Panel(self.r2_1, -1)
        self.addr21 = wx.Button(self.panel_1_copy, -1, "add")
        self.refreshr21 = wx.Button(self.panel_1_copy, -1, "refresh")
        self.label_3_copy = wx.StaticText(self.panel_3_copy, -1, "R2 relaxation peak list                                                              ")
        self.label_6_copy = wx.StaticText(self.panel_3_copy, -1, "Relaxation time [s]")
        self.r2_list_1 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_1 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_2 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_2 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_3 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_3 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_4 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_4 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_5 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_5 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_6 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_6 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_7 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_7 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_8 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_8 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_9 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_9 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_10 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_10 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_11 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_11 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_12 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_12 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_13 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_13 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.r2_list_14 = wx.StaticText(self.panel_3_copy, -1, "")
        self.r2_time_14 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.label_5_copy_1_copy_copy = wx.StaticText(self.r2_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1_copy = wx.BitmapButton(self.r2_1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #Noe no.2
        self.bitmap_1_copy_1_copy = wx.StaticBitmap(self.noe1_copy, -1, wx.Bitmap(IMAGE_PATH+'noe.gif', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3_copy = wx.StaticText(self.noe1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, str(nmrfreq[1]))
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
        self.res_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, noe_savedir[1])
        self.chandir_noe1_copy = wx.Button(self.noe1_copy, -1, "Change")
        self.label_2_copy_2_copy = wx.StaticText(self.noe1_copy, -1, "")
        self.label_5_copy_1_copy_1 = wx.StaticText(self.noe1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy = wx.BitmapButton(self.noe1_copy, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #R1 no. 2
        self.bitmap_1_copy_copy_copy_1 = wx.StaticBitmap(self.r1_1_copy, -1, wx.Bitmap(IMAGE_PATH+'r1.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_2 = wx.StaticText(self.r1_1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11_copy = wx.TextCtrl(self.r1_1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_3_copy_copy_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11_copy = wx.TextCtrl(self.r1_1_copy, -1, r1_savedir[1])
        self.results_directory_copy_copy_copy_1 = wx.Button(self.r1_1_copy, -1, "Change")
        self.structure_file_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11_copy = StructureTextCtrl(self.r1_1_copy, -1, self.structure_file_pdb_msg)
        self.results_directory_copy_copy_copy_copy = wx.Button(self.r1_1_copy, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r11_copy = wx.TextCtrl(self.r1_1_copy, -1, "")
        self.panel_2_copy_1 = wx.Panel(self.r1_1_copy, -1)
        self.addr11_copy = wx.Button(self.panel_1_copy_1, -1, "add")
        self.refreshr11_copy = wx.Button(self.panel_1_copy_1, -1, "refresh")
        self.label_3_copy_1 = wx.StaticText(self.panel_3_copy_1, -1, "R1 relaxation peak list                                                              ")
        self.label_6_copy_1 = wx.StaticText(self.panel_3_copy_1, -1, "Relaxation time [s]")
        self.r1_list_1_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_1_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_2_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_2_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_3_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_3_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_4_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_4_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_5_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_5_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_6_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_6_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_7_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_7_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_8_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_8_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_9_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_9_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_10_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_10_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_11_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_11_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_12_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_12_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_1_copy_11_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_13_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.r1_list_14_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.r1_time_1_4_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.label_5_copy_1_copy_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1_copy_1 = wx.BitmapButton(self.r1_1_copy, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #R2 no. 2
        self.bitmap_1_copy_copy_copy_copy = wx.StaticBitmap(self.r2_1_copy, -1, wx.Bitmap(IMAGE_PATH+'r2.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Set-up for R2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1_copy = wx.StaticText(self.r2_1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r21_copy = wx.TextCtrl(self.r2_1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_3_copy_copy_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21_copy = wx.TextCtrl(self.r2_1_copy, -1, r2_savedir[1])
        self.results_directory_r21_copy = wx.Button(self.r2_1_copy, -1, "Change")
        self.structure_file_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21_copy = StructureTextCtrl(self.r2_1_copy, -1, self.structure_file_pdb_msg)
        self.structure_r21_copy.SetEditable(False)
        self.chan_struc_r21_copy = wx.Button(self.r2_1_copy, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r21_copy = wx.TextCtrl(self.r2_1_copy, -1, "")
        self.panel_2_copy_copy = wx.Panel(self.r2_1_copy, -1)
        self.addr21_copy = wx.Button(self.panel_1_copy_copy, -1, "add")
        self.refreshr21_copy = wx.Button(self.panel_1_copy_copy, -1, "refresh")
        self.label_3_copy_copy = wx.StaticText(self.panel_3_copy_copy, -1, "R2 relaxation peak list                                                              ")
        self.label_6_copy_copy = wx.StaticText(self.panel_3_copy_copy, -1, "Relaxation time [s]")
        self.r2_list_1_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_1_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_2_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_2_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_3_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_3_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_4_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_4_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_5_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_5_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_6_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_6_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_7_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_7_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_8_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_8_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_9_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_9_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_10_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_10_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_11_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_11_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_12_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_12_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_13_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_13_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.r2_list_14_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.r2_time_14_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.label_5_copy_1_copy_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1_copy_copy = wx.BitmapButton(self.r2_1_copy, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #NOE no. 3
        self.bitmap_1_copy_1_copy_1 = wx.StaticBitmap(self.noe1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'noe.gif', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, str(nmrfreq[2]))
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
        self.res_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, noe_savedir[2])
        self.chandir_noe1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Change")
        self.label_2_copy_2_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "")
        self.label_5_copy_1_copy_2 = wx.StaticText(self.noe1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy_1 = wx.BitmapButton(self.noe1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #R1 no. 3
        self.bitmap_1_copy_copy_copy_2 = wx.StaticBitmap(self.r1_1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'r1.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_3 = wx.StaticText(self.r1_1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11_copy_1 = wx.TextCtrl(self.r1_1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_3_copy_copy_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11_copy_1 = wx.TextCtrl(self.r1_1_copy_1, -1, r1_savedir[2])
        self.results_directory_copy_copy_copy_2 = wx.Button(self.r1_1_copy_1, -1, "Change")
        self.structure_file_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11_copy_1 = StructureTextCtrl(self.r1_1_copy_1, -1, self.structure_file_pdb_msg)
        self.structure_r11_copy_1.SetEditable(False)
        self.results_directory_copy_copy_copy_copy_1 = wx.Button(self.r1_1_copy_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r11_copy_1 = wx.TextCtrl(self.r1_1_copy_1, -1, "")
        self.panel_2_copy_2 = wx.Panel(self.r1_1_copy_1, -1)
        self.addr11_copy_1 = wx.Button(self.panel_1_copy_2, -1, "add")
        self.refreshr11_copy_1 = wx.Button(self.panel_1_copy_2, -1, "refresh")
        self.label_3_copy_2 = wx.StaticText(self.panel_3_copy_2, -1, "R1 relaxation peak list                                                              ")
        self.label_6_copy_2 = wx.StaticText(self.panel_3_copy_2, -1, "Relaxation time [s]")
        self.r1_list_1_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_1_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_2_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_2_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_3_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_3_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_4_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_4_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_5_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_5_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_6_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_6_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_7_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_7_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_8_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_8_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_9_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_9_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_10_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_10_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_11_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_11_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_12_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_12_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_1_copy_11_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_13_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.r1_list_14_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.r1_time_1_4_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.label_5_copy_1_copy_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1_copy_2 = wx.BitmapButton(self.r1_1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #R2 no. 3
        self.bitmap_1_copy_copy_copy_copy_1 = wx.StaticBitmap(self.r2_1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'r2.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Set-up for R2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r21_copy_1 = wx.TextCtrl(self.r2_1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_3_copy_copy_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21_copy_1 = wx.TextCtrl(self.r2_1_copy_1, -1, r2_savedir[2])
        self.results_directory_r21_copy_1 = wx.Button(self.r2_1_copy_1, -1, "Change")
        self.structure_file_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21_copy_1 = StructureTextCtrl(self.r2_1_copy_1, -1, self.structure_file_pdb_msg)
        self.structure_r21_copy_1.SetEditable(False)
        self.chan_struc_r21_copy_1 = wx.Button(self.r2_1_copy_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r21_copy_1 = wx.TextCtrl(self.r2_1_copy_1, -1, "")
        self.panel_2_copy_copy_1 = wx.Panel(self.r2_1_copy_1, -1)
        self.addr21_copy_1 = wx.Button(self.panel_1_copy_copy_1, -1, "add")
        self.refreshr21_copy_1 = wx.Button(self.panel_1_copy_copy_1, -1, "refresh")
        self.label_3_copy_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "R2 relaxation peak list                                                              ")
        self.label_6_copy_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "Relaxation time [s]")
        self.r2_list_1_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_1_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_2_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_2_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_3_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_3_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_4_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_4_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_5_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_5_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_6_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_6_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_7_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_7_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_8_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_8_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_9_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_9_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_10_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_10_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_11_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_11_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_12_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_12_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_13_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_13_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.r2_list_14_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.r2_time_14_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.label_5_copy_1_copy_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_r1_1_copy_copy_1 = wx.BitmapButton(self.r2_1_copy_1, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        # The automatic model-free protocol GUI element.
        Auto_model_free(self)

        ## results
        self.label_11 = wx.StaticText(self.results, -1, "NOE analysis")
        self.list_noe = wx.ListBox(self.results, -1, choices=results_noe)
        self.open_noe_results = wx.Button(self.results, -1, "open")
        self.label_11_copy = wx.StaticText(self.results, -1, "R1 and R2 relaxation analysis")
        self.list_rx = wx.ListBox(self.results, -1, choices=results_rx)
        self.open_rx_results = wx.Button(self.results, -1, "open")
        self.label_11_copy_copy = wx.StaticText(self.results, -1, "Model-free analysis")
        self.list_modelfree = wx.ListBox(self.results, -1, choices=results_model_free)
        self.open_model_results = wx.Button(self.results, -1, "open")

        self.__set_properties()
        self.__do_layout()

        # Menu actions
        self.Bind(wx.EVT_MENU, self.newGUI, id=1)
        self.Bind(wx.EVT_MENU, self.openGUI, id=2)
        self.Bind(wx.EVT_MENU, self.saveGUI, id=3)
        self.Bind(wx.EVT_MENU, self.exitGUI, id=4)
        self.Bind(wx.EVT_MENU, self.aboutGUI, id=5)
        self.Bind(wx.EVT_MENU, self.aboutrelax, id=6)
        self.Bind(wx.EVT_MENU, self.settings, id=7)
        self.Bind(wx.EVT_MENU, self.references, id=9)
        #self.Bind(wx.EVT_MENU, self.structure_pdb, id=11)
        self.Bind(wx.EVT_MENU, self.import_seq, id=12)
        self.Bind(wx.EVT_MENU, self.param_file_setting, id=13)
        self.Bind(wx.EVT_MENU, self.reset_setting, id=14)

        #button actions
        self.Bind(wx.EVT_BUTTON, self.sat_noe1, self.sat_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe, self.noe_ref_err_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_noe1.open_file, self.ref_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe1, self.chandir_noe1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe1, self.relax_start_noe1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_1, self.results_directory_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_r11.open_file, self.results_directory_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r1_1, self.addr11)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_1, self.refreshr11)
        self.Bind(wx.EVT_BUTTON, self.exec_r2_1, self.relax_start_r1_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r2_1, self.results_directory_r21)
        self.Bind(wx.EVT_BUTTON, self.structure_r21.open_file, self.chan_struc_r21)
        self.Bind(wx.EVT_BUTTON, self.add_r2_1, self.addr21)
        self.Bind(wx.EVT_BUTTON, self.refresh_r2_1, self.refreshr21)
        self.Bind(wx.EVT_BUTTON, self.exec_r1_1, self.relax_start_r1_1_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe2, self.sat_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.ref_noe2, self.noe_ref_err_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_noe1_copy.open_file, self.ref_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe2, self.chandir_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_noe2, self.relax_start_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_2, self.results_directory_copy_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_r11_copy.open_file, self.results_directory_copy_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r1_2, self.addr11_copy)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_2, self.refreshr11_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_r1_2, self.relax_start_r1_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r2_2, self.results_directory_r21_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_r21_copy.open_file, self.chan_struc_r21_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r2_2, self.addr21_copy)
        self.Bind(wx.EVT_BUTTON, self.refresh_r2_2, self.refreshr21_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_r2_2, self.relax_start_r1_1_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe3, self.sat_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe3, self.noe_ref_err_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_noe1_copy_1.open_file, self.ref_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe3, self.chandir_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe3, self.relax_start_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_3, self.results_directory_copy_copy_copy_2)
        self.Bind(wx.EVT_BUTTON, self.structure_r11_copy_1.open_file, self.results_directory_copy_copy_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.add_r1_3, self.addr11_copy_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_3, self.refreshr11_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_r1_3, self.relax_start_r1_1_copy_2)
        self.Bind(wx.EVT_BUTTON, self.resdir_r2_3, self.results_directory_r21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_r21_copy_1.open_file, self.chan_struc_r21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.add_r2_3, self.addr21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_r2_3, self.refreshr21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_r2_3, self.relax_start_r1_1_copy_copy_1)
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
        noe_ref_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
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
        noe_ref_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
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
        self.r1_1.SetSizer(sizer_10)
        sizer_10_copy.Add(self.bitmap_1_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(self.label_4_copy_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_1.Add(self.nmrfreq_value_r21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy.Add(nmr_freq_copy_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1.Add(self.label_2_copy_copy_3_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1.Add(self.resultsdir_r21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1.Add(self.results_directory_r21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(results_dir_copy_copy_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy.Add(self.structure_file_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy.Add(self.structure_r21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy.Add(self.chan_struc_r21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(results_dir_copy_copy_copy_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy.Add(self.unresolved_r21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy.Add(nmr_freq_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy.Add(self.panel_2_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy.Add(self.addr21, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy.Add(self.refreshr21, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy.Add(sizer_13_copy, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_13, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_13, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_list_14, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.r2_time_14, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy.SetSizer(grid_sizer_1_copy)
        sizer_12_copy.Add(self.panel_3_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy.SetSizer(sizer_12_copy)
        sizer_11_copy.Add(self.panel_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy.Add(self.label_5_copy_1_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy.Add(self.relax_start_r1_1_copy, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy.Add(exec_relax_copy_1_copy_copy, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy.Add(sizer_11_copy, 0, 0, 0)
        self.r2_1.SetSizer(sizer_10_copy)
        self.notebook_3.AddPage(self.noe1, "steady-state NOE")
        self.notebook_3.AddPage(self.r1_1, "R1 relaxation")
        self.notebook_3.AddPage(self.r2_1, "R2 relaxation")
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
        sizer_10_copy_1.Add(self.bitmap_1_copy_copy_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_1.Add(self.label_4_copy_copy_copy_1, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_2.Add(self.label_2_copy_copy_copy_2_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_2.Add(self.nmrfreq_value_r11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_1.Add(nmr_freq_copy_copy_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_2.Add(self.label_2_copy_copy_3_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_2.Add(self.resultsdir_r11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_2.Add(self.results_directory_copy_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_1.Add(results_dir_copy_copy_copy_2, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_1.Add(self.structure_file_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_1.Add(self.structure_r11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_1.Add(self.results_directory_copy_copy_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_1.Add(results_dir_copy_copy_copy_copy_1, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_1.Add(self.unresolved_r11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_1.Add(nmr_freq_copy_copy_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_1.Add(self.panel_2_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_1.Add(self.addr11_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_1.Add(self.refreshr11_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_1.Add(sizer_13_copy_1, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_1.Add(self.label_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.label_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_1_copy_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_13_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_list_14_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.r1_time_1_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_1.SetSizer(grid_sizer_1_copy_1)
        sizer_12_copy_1.Add(self.panel_3_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_1.SetSizer(sizer_12_copy_1)
        sizer_11_copy_1.Add(self.panel_1_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_1.Add(self.label_5_copy_1_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_1.Add(self.relax_start_r1_1_copy_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_1.Add(exec_relax_copy_1_copy_copy_1, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_1.Add(sizer_11_copy_1, 0, 0, 0)
        self.r1_1_copy.SetSizer(sizer_10_copy_1)
        sizer_10_copy_copy.Add(self.bitmap_1_copy_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy.Add(self.label_4_copy_copy_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_1_copy.Add(self.nmrfreq_value_r21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy.Add(nmr_freq_copy_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_3_copy_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy.Add(self.resultsdir_r21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy.Add(self.results_directory_r21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy.Add(results_dir_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_copy.Add(self.structure_file_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy.Add(self.structure_r21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy.Add(self.chan_struc_r21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy.Add(results_dir_copy_copy_copy_copy_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy.Add(self.unresolved_r21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy.Add(nmr_freq_copy_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_copy.Add(self.panel_2_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_copy.Add(self.addr21_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_copy.Add(self.refreshr21_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_copy.Add(sizer_13_copy_copy, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_copy.Add(self.label_3_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.label_6_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_13_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_13_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_list_14_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.r2_time_14_copy, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_copy.SetSizer(grid_sizer_1_copy_copy)
        sizer_12_copy_copy.Add(self.panel_3_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_copy.SetSizer(sizer_12_copy_copy)
        sizer_11_copy_copy.Add(self.panel_1_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_copy.Add(self.label_5_copy_1_copy_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_copy.Add(self.relax_start_r1_1_copy_copy, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy.Add(exec_relax_copy_1_copy_copy_copy, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_copy.Add(sizer_11_copy_copy, 0, 0, 0)
        self.r2_1_copy.SetSizer(sizer_10_copy_copy)
        self.notebook_3_copy.AddPage(self.noe1_copy, "steady-state NOE")
        self.notebook_3_copy.AddPage(self.r1_1_copy, "R1 relaxation")
        self.notebook_3_copy.AddPage(self.r2_1_copy, "R2 relaxation")
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
        sizer_10_copy_2.Add(self.bitmap_1_copy_copy_copy_2, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_2.Add(self.label_4_copy_copy_copy_2, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_3.Add(self.label_2_copy_copy_copy_2_copy_copy_3, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_3.Add(self.nmrfreq_value_r11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_2.Add(nmr_freq_copy_copy_copy_3, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_3.Add(self.label_2_copy_copy_3_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_3.Add(self.resultsdir_r11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_3.Add(self.results_directory_copy_copy_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_2.Add(results_dir_copy_copy_copy_3, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_2.Add(self.structure_file_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_2.Add(self.structure_r11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_2.Add(self.results_directory_copy_copy_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_2.Add(results_dir_copy_copy_copy_copy_2, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_2.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_2.Add(self.unresolved_r11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_2.Add(nmr_freq_copy_copy_copy_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_2.Add(self.panel_2_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_2.Add(self.addr11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_2.Add(self.refreshr11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_2.Add(sizer_13_copy_2, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_2.Add(self.label_3_copy_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.label_6_copy_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_1_copy_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_13_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_list_14_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.r1_time_1_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_2.SetSizer(grid_sizer_1_copy_2)
        sizer_12_copy_2.Add(self.panel_3_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_2.SetSizer(sizer_12_copy_2)
        sizer_11_copy_2.Add(self.panel_1_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_2.Add(self.label_5_copy_1_copy_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_2.Add(self.relax_start_r1_1_copy_2, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_2.Add(exec_relax_copy_1_copy_copy_2, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_2.Add(sizer_11_copy_2, 0, 0, 0)
        self.r1_1_copy_1.SetSizer(sizer_10_copy_2)
        sizer_10_copy_copy_1.Add(self.bitmap_1_copy_copy_copy_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy_1.Add(self.label_4_copy_copy_copy_copy_1, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_1_copy_1.Add(self.nmrfreq_value_r21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy_1.Add(nmr_freq_copy_copy_copy_1_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1_copy_1.Add(self.label_2_copy_copy_3_copy_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_1.Add(self.resultsdir_r21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_1.Add(self.results_directory_r21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy_1.Add(results_dir_copy_copy_copy_1_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_copy_1.Add(self.structure_file_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1.Add(self.structure_r21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1.Add(self.chan_struc_r21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy_1.Add(results_dir_copy_copy_copy_copy_copy_1, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy_1.Add(self.unresolved_r21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy_1.Add(nmr_freq_copy_copy_copy_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_copy_1.Add(self.panel_2_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_copy_1.Add(self.addr21_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_copy_1.Add(self.refreshr21_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_copy_1.Add(sizer_13_copy_copy_1, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_copy_1.Add(self.label_3_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.label_6_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_13_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_13_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_list_14_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.r2_time_14_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_copy_1.SetSizer(grid_sizer_1_copy_copy_1)
        sizer_12_copy_copy_1.Add(self.panel_3_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_copy_1.SetSizer(sizer_12_copy_copy_1)
        sizer_11_copy_copy_1.Add(self.panel_1_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_copy_1.Add(self.label_5_copy_1_copy_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_copy_1.Add(self.relax_start_r1_1_copy_copy_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy_1.Add(exec_relax_copy_1_copy_copy_copy_1, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_copy_1.Add(sizer_11_copy_copy_1, 0, 0, 0)
        self.r2_1_copy_1.SetSizer(sizer_10_copy_copy_1)
        self.notebook_3_copy_1.AddPage(self.noe1_copy_1, "steady-state NOE")
        self.notebook_3_copy_1.AddPage(self.r1_1_copy_1, "R1 relaxation")
        self.notebook_3_copy_1.AddPage(self.r2_1_copy_1, "R2 relaxation")
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
        self.notebook_2.AddPage(self.modelfree, "Model-free")
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
        self.resultsdir_r21.SetMinSize((350, 27))
        self.results_directory_r21.SetMinSize((103, 27))
        self.structure_file_copy.SetMinSize((230, 17))
        self.structure_r21.SetMinSize((350, 27))
        self.chan_struc_r21.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy.SetMinSize((230, 17))
        self.unresolved_r21.SetMinSize((350, 27))
        self.panel_2_copy.SetMinSize((688, 5))
        self.addr21.SetMinSize((60, 27))
        self.refreshr21.SetMinSize((60, 27))
        self.label_3_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.r2_time_1.SetMinSize((80, 20))
        self.r2_time_2.SetMinSize((80, 20))
        self.r2_time_3.SetMinSize((80, 20))
        self.r2_time_4.SetMinSize((80, 20))
        self.r2_time_5.SetMinSize((80, 20))
        self.r2_time_6.SetMinSize((80, 20))
        self.r2_time_7.SetMinSize((80, 20))
        self.r2_time_8.SetMinSize((80, 20))
        self.r2_time_9.SetMinSize((80, 20))
        self.r2_time_10.SetMinSize((80, 20))
        self.r2_time_11.SetMinSize((80, 20))
        self.r2_time_12.SetMinSize((80, 20))
        self.r2_time_13.SetMinSize((80, 20))
        self.r2_time_14.SetMinSize((80, 20))
        self.panel_3_copy.SetMinSize((620, 300))
        self.panel_3_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy.SetMinSize((688, 300))
        self.panel_1_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy.SetMinSize((118, 17))
        self.relax_start_r1_1_copy.SetName('hello')
        self.relax_start_r1_1_copy.SetSize(self.relax_start_r1_1_copy.GetBestSize())
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
        self.label_4_copy_copy_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_2.SetMinSize((230, 17))
        self.nmrfreq_value_r11_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_1.SetMinSize((230, 17))
        self.resultsdir_r11_copy.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_1.SetMinSize((103, 27))
        self.structure_file_copy_1.SetMinSize((230, 17))
        self.structure_r11_copy.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_1.SetMinSize((230, 17))
        self.unresolved_r11_copy.SetMinSize((350, 27))
        self.panel_2_copy_1.SetMinSize((688, 5))
        self.addr11_copy.SetMinSize((60, 27))
        self.refreshr11_copy.SetMinSize((60, 27))
        self.label_3_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.r1_time_1_copy.SetMinSize((80, 20))
        self.r1_time_2_copy.SetMinSize((80, 20))
        self.r1_time_3_copy.SetMinSize((80, 20))
        self.r1_time_4_copy.SetMinSize((80, 20))
        self.r1_time_5_copy.SetMinSize((80, 20))
        self.r1_time_6_copy.SetMinSize((80, 20))
        self.r1_time_7_copy.SetMinSize((80, 20))
        self.r1_time_8_copy.SetMinSize((80, 20))
        self.r1_time_9_copy.SetMinSize((80, 20))
        self.r1_time_10_copy.SetMinSize((80, 20))
        self.r1_time_11_copy.SetMinSize((80, 20))
        self.r1_time_12_copy.SetMinSize((80, 20))
        self.r1_time_13_copy.SetMinSize((80, 20))
        self.r1_time_1_4_copy.SetMinSize((80, 20))
        self.panel_3_copy_1.SetMinSize((620, 300))
        self.panel_3_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_1.SetMinSize((688, 300))
        self.panel_1_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_1.SetMinSize((118, 17))
        self.relax_start_r1_1_copy_1.SetName('hello')
        self.relax_start_r1_1_copy_1.SetSize(self.relax_start_r1_1_copy_1.GetBestSize())
        self.label_4_copy_copy_copy_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_1_copy.SetMinSize((230, 17))
        self.nmrfreq_value_r21_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy.SetMinSize((230, 17))
        self.resultsdir_r21_copy.SetMinSize((350, 27))
        self.results_directory_r21_copy.SetMinSize((103, 27))
        self.structure_file_copy_copy.SetMinSize((230, 17))
        self.structure_r21_copy.SetMinSize((350, 27))
        self.chan_struc_r21_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy.SetMinSize((230, 17))
        self.unresolved_r21_copy.SetMinSize((350, 27))
        self.panel_2_copy_copy.SetMinSize((688, 5))
        self.addr21_copy.SetMinSize((60, 27))
        self.refreshr21_copy.SetMinSize((60, 27))
        self.label_3_copy_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.r2_time_1_copy.SetMinSize((80, 20))
        self.r2_time_2_copy.SetMinSize((80, 20))
        self.r2_time_3_copy.SetMinSize((80, 20))
        self.r2_time_4_copy.SetMinSize((80, 20))
        self.r2_time_5_copy.SetMinSize((80, 20))
        self.r2_time_6_copy.SetMinSize((80, 20))
        self.r2_time_7_copy.SetMinSize((80, 20))
        self.r2_time_8_copy.SetMinSize((80, 20))
        self.r2_time_9_copy.SetMinSize((80, 20))
        self.r2_time_10_copy.SetMinSize((80, 20))
        self.r2_time_11_copy.SetMinSize((80, 20))
        self.r2_time_12_copy.SetMinSize((80, 20))
        self.r2_time_13_copy.SetMinSize((80, 20))
        self.r2_time_14_copy.SetMinSize((80, 20))
        self.panel_3_copy_copy.SetMinSize((620, 300))
        self.panel_3_copy_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_copy.SetMinSize((688, 300))
        self.panel_1_copy_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_copy.SetMinSize((118, 17))
        self.relax_start_r1_1_copy_copy.SetName('hello')
        self.relax_start_r1_1_copy_copy.SetSize(self.relax_start_r1_1_copy_copy.GetBestSize())
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
        self.label_4_copy_copy_copy_2.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_3.SetMinSize((230, 17))
        self.nmrfreq_value_r11_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_2.SetMinSize((230, 17))
        self.resultsdir_r11_copy_1.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_2.SetMinSize((103, 27))
        self.structure_file_copy_2.SetMinSize((230, 17))
        self.structure_r11_copy_1.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_2.SetMinSize((230, 17))
        self.unresolved_r11_copy_1.SetMinSize((350, 27))
        self.panel_2_copy_2.SetMinSize((688, 5))
        self.addr11_copy_1.SetMinSize((60, 27))
        self.refreshr11_copy_1.SetMinSize((60, 27))
        self.label_3_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.r1_time_1_copy_1.SetMinSize((80, 20))
        self.r1_time_2_copy_1.SetMinSize((80, 20))
        self.r1_time_3_copy_1.SetMinSize((80, 20))
        self.r1_time_4_copy_1.SetMinSize((80, 20))
        self.r1_time_5_copy_1.SetMinSize((80, 20))
        self.r1_time_6_copy_1.SetMinSize((80, 20))
        self.r1_time_7_copy_1.SetMinSize((80, 20))
        self.r1_time_8_copy_1.SetMinSize((80, 20))
        self.r1_time_9_copy_1.SetMinSize((80, 20))
        self.r1_time_10_copy_1.SetMinSize((80, 20))
        self.r1_time_11_copy_1.SetMinSize((80, 20))
        self.r1_time_12_copy_1.SetMinSize((80, 20))
        self.r1_time_13_copy_1.SetMinSize((80, 20))
        self.r1_time_1_4_copy_1.SetMinSize((80, 20))
        self.panel_3_copy_2.SetMinSize((620, 300))
        self.panel_3_copy_2.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_2.SetMinSize((688, 300))
        self.panel_1_copy_2.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_2.SetMinSize((118, 17))
        self.relax_start_r1_1_copy_2.SetName('hello')
        self.relax_start_r1_1_copy_2.SetSize(self.relax_start_r1_1_copy_2.GetBestSize())
        self.label_4_copy_copy_copy_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_1_copy_1.SetMinSize((230, 17))
        self.nmrfreq_value_r21_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy_1.SetMinSize((230, 17))
        self.resultsdir_r21_copy_1.SetMinSize((350, 27))
        self.results_directory_r21_copy_1.SetMinSize((103, 27))
        self.structure_file_copy_copy_1.SetMinSize((230, 17))
        self.structure_r21_copy_1.SetMinSize((350, 27))
        self.chan_struc_r21_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1.SetMinSize((230, 17))
        self.unresolved_r21_copy_1.SetMinSize((350, 27))
        self.panel_2_copy_copy_1.SetMinSize((688, 5))
        self.addr21_copy_1.SetMinSize((60, 27))
        self.refreshr21_copy_1.SetMinSize((60, 27))
        self.label_3_copy_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.r2_time_1_copy_1.SetMinSize((80, 20))
        self.r2_time_2_copy_1.SetMinSize((80, 20))
        self.r2_time_3_copy_1.SetMinSize((80, 20))
        self.r2_time_4_copy_1.SetMinSize((80, 20))
        self.r2_time_5_copy_1.SetMinSize((80, 20))
        self.r2_time_6_copy_1.SetMinSize((80, 20))
        self.r2_time_7_copy_1.SetMinSize((80, 20))
        self.r2_time_8_copy_1.SetMinSize((80, 20))
        self.r2_time_9_copy_1.SetMinSize((80, 20))
        self.r2_time_10_copy_1.SetMinSize((80, 20))
        self.r2_time_11_copy_1.SetMinSize((80, 20))
        self.r2_time_12_copy_1.SetMinSize((80, 20))
        self.r2_time_13_copy_1.SetMinSize((80, 20))
        self.r2_time_14_copy_1.SetMinSize((80, 20))
        self.panel_3_copy_copy_1.SetMinSize((620, 300))
        self.panel_3_copy_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_copy_1.SetMinSize((688, 300))
        self.panel_1_copy_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_copy_1.SetMinSize((118, 17))
        self.relax_start_r1_1_copy_copy_1.SetName('hello')
        self.relax_start_r1_1_copy_copy_1.SetSize(self.relax_start_r1_1_copy_copy_1.GetBestSize())


    def aboutGUI(self, event): # About
        about_relax()
        event.Skip()


    def aboutrelax(self, event): # abour relax
        webbrowser.open_new('http://www.nmr-relax.com')
        event.Skip()


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


    def add_r1_2(self, event): # wxGlade: main.<event_handler>
        if len(r1_list2) < 14:
            r1_entry2 = multi_openfile('Select R1 peak list file', self.resultsdir_r11_copy.GetValue(), '*.*', 'all files (*.*)|*.*')
            if not r1_entry2 == None:
                for i in range(0, (len(r1_entry2))):
                    r1_list2.append(str(r1_entry2[i]))
        if len(r1_list2) >= 1:
            self.r1_list_1_copy.SetLabel(r1_list2[0])
        if len(r1_list2) >= 2:
            self.r1_list_2_copy.SetLabel(r1_list2[1])
        if len(r1_list2) >= 3:
            self.r1_list_3_copy.SetLabel(r1_list2[2])
        if len(r1_list2) >= 4:
            self.r1_list_4_copy.SetLabel(r1_list2[3])
        if len(r1_list2) >= 5:
            self.r1_list_5_copy.SetLabel(r1_list2[4])
        if len(r1_list2) >= 6:
            self.r1_list_6_copy.SetLabel(r1_list2[5])
        if len(r1_list2) >= 7:
            self.r1_list_7_copy.SetLabel(r1_list2[6])
        if len(r1_list2) >= 8:
            self.r1_list_8_copy.SetLabel(r1_list2[7])
        if len(r1_list2) >= 9:
            self.r1_list_9_copy.SetLabel(r1_list2[8])
        if len(r1_list2) >= 10:
            self.r1_list_10_copy.SetLabel(r1_list2[9])
        if len(r1_list2) >= 11:
            self.r1_list_11_copy.SetLabel(r1_list2[10])
        if len(r1_list2) >= 12:
            self.r1_list_12_copy.SetLabel(r1_list2[11])
        if len(r1_list2) >= 13:
            self.r1_list_1_copy_11_copy.SetLabel(r1_list2[12])
        if len(r1_list2) >= 14:
            self.r1_list_14_copy.SetLabel(r1_list2[13])
        event.Skip()


    def add_r1_3(self, event): # add file
        if len(r1_list3) < 14:
            r1_entry3 = multi_openfile('Select R1 peak list file', self.resultsdir_r11_copy_1.GetValue(), '*.*', 'all files (*.*)|*.*')
            if not r1_entry3 == None:
                for i in range(0, (len(r1_entry3))):
                    r1_list3.append(str(r1_entry3[i]))

        if len(r1_list3) >= 1:
            self.r1_list_1_copy_1.SetLabel(r1_list3[0])
        if len(r1_list3) >= 2:
            self.r1_list_2_copy_1.SetLabel(r1_list3[1])
        if len(r1_list3) >= 3:
            self.r1_list_3_copy_1.SetLabel(r1_list3[2])
        if len(r1_list3) >= 4:
            self.r1_list_4_copy_1.SetLabel(r1_list3[3])
        if len(r1_list3) >= 5:
            self.r1_list_5_copy_1.SetLabel(r1_list3[4])
        if len(r1_list3) >= 6:
            self.r1_list_6_copy_1.SetLabel(r1_list3[5])
        if len(r1_list3) >= 7:
            self.r1_list_7_copy_1.SetLabel(r1_list3[6])
        if len(r1_list3) >= 8:
            self.r1_list_8_copy_1.SetLabel(r1_list3[7])
        if len(r1_list3) >= 9:
            self.r1_list_9_copy_1.SetLabel(r1_list3[8])
        if len(r1_list3) >= 10:
            self.r1_list_10_copy_1.SetLabel(r1_list3[9])
        if len(r1_list3) >= 11:
            self.r1_list_11_copy_1.SetLabel(r1_list3[10])
        if len(r1_list3) >= 12:
            self.r1_list_12_copy_1.SetLabel(r1_list3[11])
        if len(r1_list3) >= 13:
            self.r1_list_1_copy_11_copy_1.SetLabel(r1_list3[12])
        if len(r1_list3) >= 14:
            self.r1_list_14_copy_1.SetLabel(r1_list3[13])
        event.Skip()


    def add_r2_1(self, event): # add a r2 peak list
        if len(r2_list) < 14:
            r2_entry = multi_openfile('Select R2 peak list file', self.resultsdir_r21.GetValue(), '*.*', 'all files (*.*)|*.*')
            if not r2_entry == None:
                for i in range(0, (len(r2_entry))):
                    r2_list.append(str(r2_entry[i]))
        if len(r2_list) >= 1:
            self.r2_list_1.SetLabel(r2_list[0])
        if len(r2_list) >= 2:
            self.r2_list_2.SetLabel(r2_list[1])
        if len(r2_list) >= 3:
            self.r2_list_3.SetLabel(r2_list[2])
        if len(r2_list) >= 4:
            self.r2_list_4.SetLabel(r2_list[3])
        if len(r2_list) >= 5:
            self.r2_list_5.SetLabel(r2_list[4])
        if len(r2_list) >= 6:
            self.r2_list_6.SetLabel(r2_list[5])
        if len(r2_list) >= 7:
            self.r2_list_7.SetLabel(r2_list[6])
        if len(r2_list) >= 8:
            self.r2_list_8.SetLabel(r2_list[7])
        if len(r2_list) >= 9:
            self.r2_list_9.SetLabel(r2_list[8])
        if len(r2_list) >= 10:
            self.r2_list_10.SetLabel(r2_list[9])
        if len(r2_list) >= 11:
            self.r2_list_11.SetLabel(r2_list[10])
        if len(r2_list) >= 12:
            self.r2_list_12.SetLabel(r2_list[11])
        if len(r2_list) >= 13:
            self.r2_list_13.SetLabel(r2_list[12])
        if len(r2_list) >= 14:
            self.r2_list_14.SetLabel(r2_list[13])
        event.Skip()


    def add_r2_2(self, event): # add a r2 peak list
        if len(r2_list2) < 14:
            r2_entry2 = multi_openfile('Select R2 peak list file', self.resultsdir_r21_copy.GetValue(), '*.*', 'all files (*.*)|*.*')
            if not r2_entry2 == None:
                for i in range(0, (len(r2_entry2))):
                    r2_list2.append(str(r2_entry2[i]))
        if len(r2_list2) >= 1:
            self.r2_list_1_copy.SetLabel(r2_list2[0])
        if len(r2_list2) >= 2:
            self.r2_list_2_copy.SetLabel(r2_list2[1])
        if len(r2_list2) >= 3:
            self.r2_list_3_copy.SetLabel(r2_list2[2])
        if len(r2_list2) >= 4:
            self.r2_list_4_copy.SetLabel(r2_list2[3])
        if len(r2_list2) >= 5:
            self.r2_list_5_copy.SetLabel(r2_list2[4])
        if len(r2_list2) >= 6:
            self.r2_list_6_copy.SetLabel(r2_list2[5])
        if len(r2_list2) >= 7:
            self.r2_list_7_copy.SetLabel(r2_list2[6])
        if len(r2_list2) >= 8:
            self.r2_list_8_copy.SetLabel(r2_list2[7])
        if len(r2_list2) >= 9:
            self.r2_list_9_copy.SetLabel(r2_list2[8])
        if len(r2_list2) >= 10:
            self.r2_list_10_copy.SetLabel(r2_list2[9])
        if len(r2_list2) >= 11:
            self.r2_list_11_copy.SetLabel(r2_list2[10])
        if len(r2_list2) >= 12:
            self.r2_list_12_copy.SetLabel(r2_list2[11])
        if len(r2_list2) >= 13:
            self.r2_list_13_copy.SetLabel(r2_list2[12])
        if len(r2_list2) >= 14:
            self.r2_list_14_copy.SetLabel(r2_list2[13])
        event.Skip()


    def add_r2_3(self, event): # add R2 peakfile no. 3
        if len(r2_list3) < 14:
            r2_entry3 = multi_openfile('Select R2 peak list file', self.resultsdir_r21_copy_1.GetValue(), '*.*', 'all files (*.*)|*.*')
            if not r2_entry3 == None:
                for i in range(0, (len(r2_entry3))):
                    r2_list3.append(str(r2_entry3[i]))
        if len(r2_list3) >= 1:
            self.r2_list_1_copy_1.SetLabel(r2_list3[0])
        if len(r2_list3) >= 2:
            self.r2_list_2_copy_1.SetLabel(r2_list3[1])
        if len(r2_list3) >= 3:
            self.r2_list_3_copy_1.SetLabel(r2_list3[2])
        if len(r2_list3) >= 4:
            self.r2_list_4_copy_1.SetLabel(r2_list3[3])
        if len(r2_list3) >= 5:
            self.r2_list_5_copy_1.SetLabel(r2_list3[4])
        if len(r2_list3) >= 6:
            self.r2_list_6_copy_1.SetLabel(r2_list3[5])
        if len(r2_list3) >= 7:
            self.r2_list_7_copy_1.SetLabel(r2_list3[6])
        if len(r2_list3) >= 8:
            self.r2_list_8_copy_1.SetLabel(r2_list3[7])
        if len(r2_list3) >= 9:
            self.r2_list_9_copy_1.SetLabel(r2_list3[8])
        if len(r2_list3) >= 10:
            self.r2_list_10_copy_1.SetLabel(r2_list3[9])
        if len(r2_list3) >= 11:
            self.r2_list_11_copy_1.SetLabel(r2_list3[10])
        if len(r2_list3) >= 12:
            self.r2_list_12_copy_1.SetLabel(r2_list3[11])
        if len(r2_list3) >= 13:
            self.r2_list_13_copy_1.SetLabel(r2_list3[12])
        if len(r2_list3) >= 14:
            self.r2_list_14_copy_1.SetLabel(r2_list3[13])
        event.Skip()


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


    def exec_model_free(self, event):     # start model-free calculation by relax
        global LOCAL_TM

        checkpoint = check_entries(self)
        if checkpoint == False:
            which_model = None
        else:
            which_model = whichmodel(LOCAL_TM)

        # start individual calculations
        if not which_model == None:

            if not which_model == 'full':
                if not which_model == 'final':

                    # run sphere, prolate, oblate or ellipsoid
                    enable_models = False
                    enable_models = start_modelfree(self, which_model, False, global_setting, file_setting, sequencefile)

                    if enable_models:
                        LOCAL_TM = True
                else:

                    # run final run
                    results_for_table = startmodelfree(self, which_model, False, global_setting, file_setting, sequencefile)

                    # import global variables for results table
                    global table_residue
                    global table_model
                    global table_s2
                    global table_rex
                    global table_te

                    # set global results variables
                    table_residue = results_for_table[0]
                    table_model = results_for_table[1]
                    table_s2 = results_for_table[2]
                    table_rex = results_for_table[3]
                    table_te = results_for_table[4]


            # start full automatic model-free analysis
            if which_model == 'full':
                model1 = start_modelfree(self, 'local_tm', True, global_setting, file_setting, sequencefile)    # execute local_tm
                if model1 == 'successful':
                    model2 = start_modelfree(self, 'sphere', True, global_setting, file_setting, sequencefile)        # execute sphere
                    if model2 == 'successful':
                        model3 = start_modelfree(self, 'prolate', True, global_setting, file_setting, sequencefile)         # execute prolate
                        if model3 == 'successful':
                            model4 = start_modelfree(self, 'oblate', True, global_setting, file_setting, sequencefile)         # execute oblate
                            if model4 == 'successful':
                                model5 = start_modelfree(self, 'ellipsoid', True, global_setting, file_setting, sequencefile)      # execute ellipsoid
                                if model5 == 'successful':
                                    model6 = start_modelfree(self, 'final', False, global_setting, file_setting, sequencefile)        # execute final analysis
        event.Skip()


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


    def exec_r1_2(self, event): # execute r1 calculation no. 2
        relax_times_r1_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list

        relax_times_r1_2[0] = str(self.r1_time_1_copy.GetValue())
        relax_times_r1_2[1] = str(self.r1_time_2_copy.GetValue())
        relax_times_r1_2[2] = str(self.r1_time_3_copy.GetValue())
        relax_times_r1_2[3] = str(self.r1_time_4_copy.GetValue())
        relax_times_r1_2[4] = str(self.r1_time_5_copy.GetValue())
        relax_times_r1_2[5] = str(self.r1_time_6_copy.GetValue())
        relax_times_r1_2[6] = str(self.r1_time_7_copy.GetValue())
        relax_times_r1_2[7] = str(self.r1_time_8_copy.GetValue())
        relax_times_r1_2[8] = str(self.r1_time_9_copy.GetValue())
        relax_times_r1_2[9] = str(self.r1_time_10_copy.GetValue())
        relax_times_r1_2[10] = str(self.r1_time_11_copy.GetValue())
        relax_times_r1_2[11] = str(self.r1_time_12_copy.GetValue())
        relax_times_r1_2[12] = str(self.r1_time_13_copy.GetValue())
        relax_times_r1_2[13] = str(self.r1_time_1_4_copy.GetValue())

        start_relax = exec_relax()
        if start_relax == True:
            start_rx(self.resultsdir_r11_copy.GetValue(), r1_list2, relax_times_r1_2, self.structure_r11_copy.GetValue(), self.nmrfreq_value_r11_copy.GetValue(), 1, 2, self.unresolved_r11_copy.GetValue(), self, 2, global_setting, file_setting, sequencefile)
        event.Skip()


    def exec_r1_3(self, event): # wxGlade: main.<event_handler>
        relax_times_r1_3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_r1_3[0] = str(self.r1_time_1_copy_1.GetValue())
        relax_times_r1_3[1] = str(self.r1_time_2_copy_1.GetValue())
        relax_times_r1_3[2] = str(self.r1_time_3_copy_1.GetValue())
        relax_times_r1_3[3] = str(self.r1_time_4_copy_1.GetValue())
        relax_times_r1_3[4] = str(self.r1_time_5_copy_1.GetValue())
        relax_times_r1_3[5] = str(self.r1_time_6_copy_1.GetValue())
        relax_times_r1_3[6] = str(self.r1_time_7_copy_1.GetValue())
        relax_times_r1_3[7] = str(self.r1_time_8_copy_1.GetValue())
        relax_times_r1_3[8] = str(self.r1_time_9_copy_1.GetValue())
        relax_times_r1_3[9] = str(self.r1_time_10_copy_1.GetValue())
        relax_times_r1_3[10] = str(self.r1_time_11_copy_1.GetValue())
        relax_times_r1_3[11] = str(self.r1_time_12_copy_1.GetValue())
        relax_times_r1_3[12] = str(self.r1_time_13_copy_1.GetValue())
        relax_times_r1_3[13] = str(self.r1_time_1_4_copy_1.GetValue())
        start_relax = exec_relax()
        if start_relax == True:
            start_rx(self.resultsdir_r11_copy_1.GetValue(), r1_list3, relax_times_r1_3, self.structure_r11_copy_1.GetValue(), self.nmrfreq_value_r11_copy_1.GetValue(), 1, 3, self.unresolved_r11_copy_1.GetValue(), self, 3, global_setting, file_setting, sequencefile)
        event.Skip()


    def exec_r2_1(self, event): # start r1 calculation no. 1
        relax_times_r1_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_r1_1[0] = str(self.r1_time_1.GetValue())
        relax_times_r1_1[1] = str(self.r1_time_2.GetValue())
        relax_times_r1_1[2] = str(self.r1_time_3.GetValue())
        relax_times_r1_1[3] = str(self.r1_time_4.GetValue())
        relax_times_r1_1[4] = str(self.r1_time_5.GetValue())
        relax_times_r1_1[5] = str(self.r1_time_6.GetValue())
        relax_times_r1_1[6] = str(self.r1_time_7.GetValue())
        relax_times_r1_1[7] = str(self.r1_time_8.GetValue())
        relax_times_r1_1[8] = str(self.r1_time_9.GetValue())
        relax_times_r1_1[9] = str(self.r1_time_10.GetValue())
        relax_times_r1_1[10] = str(self.r1_time_11.GetValue())
        relax_times_r1_1[11] = str(self.r1_time_12.GetValue())
        relax_times_r1_1[12] = str(self.r1_time_13.GetValue())
        relax_times_r1_1[13] = str(self.r1_time_1_4.GetValue())
        start_relax = exec_relax()
        if start_relax == True:
            start_rx(self.resultsdir_r11.GetValue(), r1_list, relax_times_r1_1, self.structure_r11.GetValue(), self.nmrfreq_value_r11.GetValue(), 1, 1, self.unresolved_r11.GetValue(), self, 1, global_setting, file_setting, sequencefile)
        event.Skip()


    def exec_r2_2(self, event): # wxGlade: main.<event_handler>
        relax_times_r2_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_r2_2[0] = str(self.r2_time_1_copy.GetValue())
        relax_times_r2_2[1] = str(self.r2_time_2_copy.GetValue())
        relax_times_r2_2[2] = str(self.r2_time_3_copy.GetValue())
        relax_times_r2_2[3] = str(self.r2_time_4_copy.GetValue())
        relax_times_r2_2[4] = str(self.r2_time_5_copy.GetValue())
        relax_times_r2_2[5] = str(self.r2_time_6_copy.GetValue())
        relax_times_r2_2[6] = str(self.r2_time_7_copy.GetValue())
        relax_times_r2_2[7] = str(self.r2_time_8_copy.GetValue())
        relax_times_r2_2[8] = str(self.r2_time_9_copy.GetValue())
        relax_times_r2_2[9] = str(self.r2_time_10_copy.GetValue())
        relax_times_r2_2[10] = str(self.r2_time_11_copy.GetValue())
        relax_times_r2_2[11] = str(self.r2_time_12_copy.GetValue())
        relax_times_r2_2[12] = str(self.r2_time_13_copy.GetValue())
        relax_times_r2_2[13] = str(self.r2_time_14_copy.GetValue())

        start_relax = exec_relax()
        if start_relax == True:
            start_rx(self.resultsdir_r21_copy.GetValue(), r2_list2, relax_times_r2_2, self.structure_r11_copy.GetValue(), self.nmrfreq_value_r11_copy.GetValue(), 2, 2, self.unresolved_r11_copy.GetValue(), self, 2, global_setting, file_setting, sequencefile)
        event.Skip()


    def exec_r2_3(self, event): # wxGlade: main.<event_handler>
        relax_times_r2_3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_r2_3[0] = str(self.r2_time_1_copy_1.GetValue())
        relax_times_r2_3[1] = str(self.r2_time_2_copy_1.GetValue())
        relax_times_r2_3[2] = str(self.r2_time_3_copy_1.GetValue())
        relax_times_r2_3[3] = str(self.r2_time_4_copy_1.GetValue())
        relax_times_r2_3[4] = str(self.r2_time_5_copy_1.GetValue())
        relax_times_r2_3[5] = str(self.r2_time_6_copy_1.GetValue())
        relax_times_r2_3[6] = str(self.r2_time_7_copy_1.GetValue())
        relax_times_r2_3[7] = str(self.r2_time_8_copy_1.GetValue())
        relax_times_r2_3[8] = str(self.r2_time_9_copy_1.GetValue())
        relax_times_r2_3[9] = str(self.r2_time_10_copy_1.GetValue())
        relax_times_r2_3[10] = str(self.r2_time_11_copy_1.GetValue())
        relax_times_r2_3[11] = str(self.r2_time_12_copy_1.GetValue())
        relax_times_r2_3[12] = str(self.r2_time_13_copy_1.GetValue())
        relax_times_r2_3[13] = str(self.r2_time_14_copy_1.GetValue())

        start_relax = exec_relax()
        if start_relax == True:
            start_rx(self.resultsdir_r21_copy_1.GetValue(), r2_list3, relax_times_r2_3, self.structure_r11_copy_1.GetValue(), self.nmrfreq_value_r11_copy_1.GetValue(), 2, 3, self.unresolved_r11_copy_1.GetValue(), self, 3, global_setting, file_setting, sequencefile)
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
            self.structure_r11.SetValue(structure_file_pdb)
            self.structure_r21.SetValue(structure_file_pdb)
            self.structure_noe1_copy.SetValue(structure_file_pdb)
            self.structure_r11_copy.SetValue(structure_file_pdb)
            self.structure_r21_copy.SetValue(structure_file_pdb)
            self.structure_noe1_copy_1.SetValue(structure_file_pdb)
            self.structure_r11_copy_1.SetValue(structure_file_pdb)
            self.structure_r21_copy_1.SetValue(structure_file_pdb)
        event.Skip()


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


    def openGUI(self, event): # Open
        filename = openfile('Select file to open', sys.path[-1], 'save.relaxGUI', 'relaxGUI files (*.relaxGUI)|*.relaxGUI|all files (*.*)|*.*')
        if not filename == None:
            global_return = open_file(self, filename)

            # import global parameters
            global global_setting
            global file_setting
            global sequencefile
            global table_residue
            global table_model
            global table_s2
            global table_rex
            global table_te

            # set global parameters
            global_setting = global_return[0]
            file_setting = global_return[1]
            sequencefile = global_return[2]
            table_residue = global_return[3]
            table_model = global_return[4]
            table_s2 = global_return[5]
            table_rex = global_return[6]
            table_te = global_return[7]
        event.Skip()


    def param_file_setting(self, event): # set up parameter files
        global file_setting # import global variable
        tmp_setting = import_file_settings(file_setting)
        if not tmp_setting == None:
            if question('Do you realy want to change import file settings?'):
                file_setting = tmp_setting
        event.Skip()


    def ref_noe(self, event): # reference noe 1
        backup = self.noe_ref_1.GetValue()
        noeref[0] = openfile('Select reference NOE', self.res_noe1.GetValue() + sep, '*.*', 'all files (*.*)|*.*')
        if noeref[0] == None:
            noeref[0] = backup
        self.noe_ref_1.SetValue(noeref[0])
        event.Skip()


    def ref_noe2(self, event): # reference noe no. 2
        backup = self.noe_ref_1_copy.GetValue()
        noeref[1] = openfile('Select reference NOE file', self.res_noe1_copy.GetValue(), '*.*', 'all files (*.*)|*.*')
        if noeref[1] == None:
            noeref[1] = backup
        self.noe_ref_1_copy.SetValue(noeref[1])
        event.Skip()


    def ref_noe3(self, event): # refererence noe 3
        backup = self.noe_ref_1_copy_1.GetValue()
        noeref[2] = openfile('Select reference NOE file', self.res_noe1_copy_1.GetValue(), '*.*', 'all files (*.*)|*.*')
        if noeref[2] == None:
            noeref[2] = backup
        self.noe_ref_1_copy_1.SetValue(noeref[2])
        event.Skip()


    def references(self, event):
        webbrowser.open_new('http://www.nmr-relax.com/refs.html')
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


    def refresh_r1_2(self, event): # refresh R1 no. 2
        self.r1_list_1_copy.SetLabel('')
        self.r1_list_2_copy.SetLabel('')
        self.r1_list_3_copy.SetLabel('')
        self.r1_list_4_copy.SetLabel('')
        self.r1_list_5_copy.SetLabel('')
        self.r1_list_6_copy.SetLabel('')
        self.r1_list_7_copy.SetLabel('')
        self.r1_list_8_copy.SetLabel('')
        self.r1_list_9_copy.SetLabel('')
        self.r1_list_10_copy.SetLabel('')
        self.r1_list_11_copy.SetLabel('')
        self.r1_list_12_copy.SetLabel('')
        self.r1_list_1_copy_11_copy.SetLabel('')
        self.r1_list_14_copy.SetLabel('')
        del r1_list2[0:len(r1_list2)]
        event.Skip()


    def refresh_r1_3(self, event): # wxGlade: main.<event_handler>
        self.r1_list_1_copy_1.SetLabel('')
        self.r1_list_2_copy_1.SetLabel('')
        self.r1_list_3_copy_1.SetLabel('')
        self.r1_list_4_copy_1.SetLabel('')
        self.r1_list_5_copy_1.SetLabel('')
        self.r1_list_6_copy_1.SetLabel('')
        self.r1_list_7_copy_1.SetLabel('')
        self.r1_list_8_copy_1.SetLabel('')
        self.r1_list_9_copy_1.SetLabel('')
        self.r1_list_10_copy_1.SetLabel('')
        self.r1_list_11_copy_1.SetLabel('')
        self.r1_list_12_copy_1.SetLabel('')
        self.r1_list_1_copy_11_copy_1.SetLabel('')
        self.r1_list_14_copy_1.SetLabel('')
        del r1_list3[0:len(r1_list3)]
        event.Skip()


    def refresh_r2_1(self, event): # refresh r2 list no. 1
        self.r2_list_1.SetLabel('')
        self.r2_list_2.SetLabel('')
        self.r2_list_3.SetLabel('')
        self.r2_list_4.SetLabel('')
        self.r2_list_5.SetLabel('')
        self.r2_list_6.SetLabel('')
        self.r2_list_7.SetLabel('')
        self.r2_list_8.SetLabel('')
        self.r2_list_9.SetLabel('')
        self.r2_list_10.SetLabel('')
        self.r2_list_11.SetLabel('')
        self.r2_list_12.SetLabel('')
        self.r2_list_13.SetLabel('')
        self.r2_list_14.SetLabel('')
        del r2_list[0:len(r2_list)]
        event.Skip()


    def refresh_r2_2(self, event): # refresh r2 list no. 1
        self.r2_list_1_copy.SetLabel('')
        self.r2_list_2_copy.SetLabel('')
        self.r2_list_3_copy.SetLabel('')
        self.r2_list_4_copy.SetLabel('')
        self.r2_list_5_copy.SetLabel('')
        self.r2_list_6_copy.SetLabel('')
        self.r2_list_7_copy.SetLabel('')
        self.r2_list_8_copy.SetLabel('')
        self.r2_list_9_copy.SetLabel('')
        self.r2_list_10_copy.SetLabel('')
        self.r2_list_11_copy.SetLabel('')
        self.r2_list_12_copy.SetLabel('')
        self.r2_list_13_copy.SetLabel('')
        self.r2_list_14_copy.SetLabel('')
        del r2_list2[0:len(r2_list2)]
        event.Skip()


    def refresh_r2_3(self, event): # refresh r2 list no. 3
        self.r2_list_1_copy_1.SetLabel('')
        self.r2_list_2_copy_1.SetLabel('')
        self.r2_list_3_copy_1.SetLabel('')
        self.r2_list_4_copy_1.SetLabel('')
        self.r2_list_5_copy_1.SetLabel('')
        self.r2_list_6_copy_1.SetLabel('')
        self.r2_list_7_copy_1.SetLabel('')
        self.r2_list_8_copy_1.SetLabel('')
        self.r2_list_9_copy_1.SetLabel('')
        self.r2_list_10_copy_1.SetLabel('')
        self.r2_list_11_copy_1.SetLabel('')
        self.r2_list_12_copy_1.SetLabel('')
        self.r2_list_13_copy_1.SetLabel('')
        self.r2_list_14_copy_1.SetLabel('')
        del r2_list3[0:len(r2_list3)]
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


    def resdir_r1_1(self, event): # R1 results dir 1
        backup = self.resultsdir_r11.GetValue()
        r1_savedir[0] = opendir('Select results directory', default=self.resultsdir_r11.GetValue())
        if r1_savedir[0] == None:
            r1_savedir[0] = backup
        self.resultsdir_r11.SetValue(r1_savedir[0])

        event.Skip()


    def resdir_r1_2(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r11_copy.GetValue()
        r1_savedir[1] = opendir('Select results directory', self.resultsdir_r11_copy.GetValue())
        if r1_savedir[1] == None:
            r1_savedir[1] = backup
        self.resultsdir_r11_copy.SetValue(r1_savedir[1])
        event.Skip()


    def resdir_r1_3(self, event): # results R1 no 3
        backup = self.resultsdir_r11_copy_1.GetValue()
        r1_savedir[2] = opendir('Select results directory', self.resultsdir_r11_copy_1.GetValue())
        if r1_savedir[2] == None:
            r1_savedir[2] = backup
        self.resultsdir_r11_copy_1.SetValue(r1_savedir[2])
        event.Skip()


    def resdir_r2_1(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r21.GetValue()
        r2_savedir[0] = opendir('Select results directory)', self.resultsdir_r21.GetValue())
        if r2_savedir[0] == None:
            r2_savedir[0] = backup
        self.resultsdir_r21.SetValue(r2_savedir[0])


    def resdir_r2_2(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r21_copy.GetValue()
        r2_savedir[1] = opendir('Select results directory)', self.resultsdir_r21_copy.GetValue() + '/')
        if r2_savedir[1] == None:
            r2_savedir[1] = backup
        self.resultsdir_r21_copy.SetValue(r2_savedir[1])
        event.Skip()


    def resdir_r2_3(self, event): # results dir R2 3
        backup = self.resultsdir_r21_copy_1.GetValue()
        r2_savedir[2] = opendir('Select results directory', self.resultsdir_r21_copy_1.GetValue())
        if r2_savedir[2] == None:
            r2_savedir[2] = backup
        self.resultsdir_r21_copy_1.SetValue(r2_savedir[2])
        event.Skip()


    def reset_setting(self, event): #reset all settings
        global global_setting #import global variable
        global file_setting # import global variable
        if question('Do you realy want to change relax settings?'):
            global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
            file_setting = ['0', '1', '2', '3', '4', '5', '6']


    def sat_noe1(self, event): # saturated noe 1
        backup = self.noe_sat_1.GetValue()
        noesat[0] = openfile('Select saturated NOE', self.res_noe1.GetValue() + sep, '*.*', 'all files (*.*)|*.*')
        if noesat[0] == None:
            noesat[0] = backup
        self.noe_sat_1.SetValue(noesat[0])
        event.Skip()


    def sat_noe2(self, event): # saturated noe no. 2
        backup = self.noe_sat_1_copy.GetValue()
        noesat[1] = openfile('Select saturated NOE file', self.res_noe1_copy.GetValue(), '*.*', 'all files (*.*)|*.*')
        if noesat[1] == None:
            noesat[1] = backup
        self.noe_sat_1_copy.SetValue(noesat[1])
        event.Skip()


    def sat_noe3(self, event): # saturated noe no. 3
        backup = self.noe_sat_1_copy_1.GetValue()
        noesat[2] = openfile('Select saturated NOE file', self.res_noe1_copy_1.GetValue(), '*.*', 'all files (*.*)|*.*')
        if noesat[2] == None:
            noesat[2] = backup
        self.noe_sat_1_copy_1.SetValue(noesat[2])
        event.Skip()


    def saveGUI(self, event): # Save
        filename = savefile('Select file to save', sys.path[-1], 'save.relaxGUI', 'relaxGUI files (*.relaxGUI)|*.relaxGUI|all files (*.*)|*.*')
        if not filename == None:
            model_result = [table_residue, table_model, table_s2, table_rex, table_te] # relax results values
            create_save_file(self, filename, model_result, global_setting, file_setting, sequencefile)
        event.Skip()


    def sel_aic(self, event):
        selection = "AIC"
        event.Skip()


    def sel_bic(self, event):
        selection = "BIC"
        event.Skip()


    def settings(self, event): # set up for relax variables
        global global_setting #import global variable
        tmp_global = relax_global_settings(global_setting)
        if not tmp_global == None:
            if question('Do you realy want to change relax settings?'):
                global_setting = tmp_global
        event.Skip()
