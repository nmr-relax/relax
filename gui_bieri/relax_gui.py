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

# Graphical User Interface for relax

# Python module imports.
from os import getcwd, listdir, sep
from re import search
from string import lower
import wx
import time
from string import replace
from string import lowercase
from os import getcwd
import sys
import os
import webbrowser

# relax module imports.
from float import floatAsByteArray
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError
from version import version

# relaxGUI module import
from res.about import *
from res.settings import *
from res.calc_noe import *
from res.calc_rx import *
from res.calc_modelfree import start_model_free
from res.filedialog import *
from res.message import *
from res.results_analysis import *
from res.select_model_calc import *
from res.project import *

 
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
structure_file_pdb = "please insert .pdb file"
unresolved = ""
results_noe = []
results_rx = []
results_model_free = []
runrelax = 'sleeping'

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

#Model-free variables 
model_source = getcwd()
model_save = getcwd()
selection = "AIC"
models = ["m0","m1","m2","m3","m4","m5","m6","m7","m8","m9"]
nmrfreq1 = 600
nmrfreq2 = 800
nmrfreq3 = 900
paramfiles1 = ["","",""]
paramfiles2 = ["","",""]
paramfiles3 = ["","",""]
results_dir_model = getcwd()

#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# GUI


class main(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: main.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.notebook_2 = wx.Notebook(self, -1, style=wx.NB_LEFT)
        self.results = wx.Panel(self.notebook_2, -1)
        self.modelfree = wx.Panel(self.notebook_2, -1)
        self.panel_4_copy_1 = wx.Panel(self.modelfree, -1)
        self.panel_4_copy = wx.Panel(self.modelfree, -1)
        self.panel_4 = wx.Panel(self.modelfree, -1)
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
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(1, "&New", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(2, "&Open", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(3, "S&ave as...", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(4, "E&xit", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&File")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(11, "Load &PDB File", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(12, "Load Se&quence File", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&Molecule")
        wxglade_tmp_menu = wx.Menu()
        self.SetMenuBar(self.frame_1_menubar)
        wxglade_tmp_menu.Append(7, "&Global relax Settings", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(13, "&Parameter File Settings", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(14, "Reset a&ll Settings", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&Settings")

        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(8, "&Contact relaxGUI", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(9, "&References", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&Extras")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(10, "&Manual", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(5, "About relaxG&UI", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(6, "About rela&x", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&Help")
        # Menu Bar end


        # NOE 1 no. 1
        self.frame_1_statusbar = self.CreateStatusBar(3, 0)
        self.bitmap_1_copy_1 = wx.StaticBitmap(self.noe1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'noe.gif', wx.BITMAP_TYPE_ANY))
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
        self.structure_noe1 = wx.TextCtrl(self.noe1, -1, structure_file_pdb)
        self.structure_noe1.SetEditable(False)
        self.ref_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1 = wx.TextCtrl(self.noe1, -1, "")
        self.label_2_copy_copy_3_copy_1 = wx.StaticText(self.noe1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1 = wx.TextCtrl(self.noe1, -1, noe_savedir[0])
        self.chandir_noe1 = wx.Button(self.noe1, -1, "Change")
        self.label_2_copy_2 = wx.StaticText(self.noe1, -1, "")
        self.label_5_copy_1 = wx.StaticText(self.noe1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1 = wx.BitmapButton(self.noe1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        # R1 no. 1
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.r1_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'r1.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy = wx.StaticText(self.r1_1, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy = wx.StaticText(self.r1_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11 = wx.TextCtrl(self.r1_1, -1, str(nmrfreq[0]))
        self.label_2_copy_copy_3_copy_copy = wx.StaticText(self.r1_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11 = wx.TextCtrl(self.r1_1, -1, r1_savedir[0])
        self.results_directory_copy_copy = wx.Button(self.r1_1, -1, "Change")
        self.structure_file = wx.StaticText(self.r1_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11 = wx.TextCtrl(self.r1_1, -1, structure_file_pdb)
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
        self.relax_start_r1_1 = wx.BitmapButton(self.r1_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #R2 no. 1
        self.bitmap_1_copy_copy_copy = wx.StaticBitmap(self.r2_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'r2.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy = wx.StaticText(self.r2_1, -1, "Set-up for R2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1 = wx.StaticText(self.r2_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r21 = wx.TextCtrl(self.r2_1, -1, str(nmrfreq[0]))
        self.label_2_copy_copy_3_copy_copy_copy = wx.StaticText(self.r2_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21 = wx.TextCtrl(self.r2_1, -1, r2_savedir[0])
        self.results_directory_r21 = wx.Button(self.r2_1, -1, "Change")
        self.structure_file_copy = wx.StaticText(self.r2_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21 = wx.TextCtrl(self.r2_1, -1, structure_file_pdb)
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
        self.relax_start_r1_1_copy = wx.BitmapButton(self.r2_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #Noe no.2
        self.bitmap_1_copy_1_copy = wx.StaticBitmap(self.noe1_copy, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'noe.gif', wx.BITMAP_TYPE_ANY))
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
        self.structure_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, structure_file_pdb)
        self.structure_noe1_copy.SetEditable(False)
        self.ref_noe_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.label_2_copy_copy_3_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, noe_savedir[1])
        self.chandir_noe1_copy = wx.Button(self.noe1_copy, -1, "Change")
        self.label_2_copy_2_copy = wx.StaticText(self.noe1_copy, -1, "")
        self.label_5_copy_1_copy_1 = wx.StaticText(self.noe1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy = wx.BitmapButton(self.noe1_copy, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #R1 no. 2
        self.bitmap_1_copy_copy_copy_1 = wx.StaticBitmap(self.r1_1_copy, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'r1.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_2 = wx.StaticText(self.r1_1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11_copy = wx.TextCtrl(self.r1_1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_3_copy_copy_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11_copy = wx.TextCtrl(self.r1_1_copy, -1, r1_savedir[1])
        self.results_directory_copy_copy_copy_1 = wx.Button(self.r1_1_copy, -1, "Change")
        self.structure_file_copy_1 = wx.StaticText(self.r1_1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11_copy = wx.TextCtrl(self.r1_1_copy, -1, structure_file_pdb)
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
        self.relax_start_r1_1_copy_1 = wx.BitmapButton(self.r1_1_copy, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #R2 no. 2
        self.bitmap_1_copy_copy_copy_copy = wx.StaticBitmap(self.r2_1_copy, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'r2.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Set-up for R2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1_copy = wx.StaticText(self.r2_1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r21_copy = wx.TextCtrl(self.r2_1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_3_copy_copy_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21_copy = wx.TextCtrl(self.r2_1_copy, -1, r2_savedir[1])
        self.results_directory_r21_copy = wx.Button(self.r2_1_copy, -1, "Change")
        self.structure_file_copy_copy = wx.StaticText(self.r2_1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21_copy = wx.TextCtrl(self.r2_1_copy, -1, structure_file_pdb)
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
        self.relax_start_r1_1_copy_copy = wx.BitmapButton(self.r2_1_copy, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #NOE no. 3
        self.bitmap_1_copy_1_copy_1 = wx.StaticBitmap(self.noe1_copy_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'noe.gif', wx.BITMAP_TYPE_ANY))
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
        self.structure_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, structure_file_pdb)
        self.structure_noe1_copy_1.SetEditable(False)
        self.ref_noe_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.label_2_copy_copy_3_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, noe_savedir[2])
        self.chandir_noe1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Change")
        self.label_2_copy_2_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "")
        self.label_5_copy_1_copy_2 = wx.StaticText(self.noe1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy_1 = wx.BitmapButton(self.noe1_copy_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #R1 no. 3
        self.bitmap_1_copy_copy_copy_2 = wx.StaticBitmap(self.r1_1_copy_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'r1.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Set-up for R1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_3 = wx.StaticText(self.r1_1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r11_copy_1 = wx.TextCtrl(self.r1_1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_3_copy_copy_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r11_copy_1 = wx.TextCtrl(self.r1_1_copy_1, -1, r1_savedir[2])
        self.results_directory_copy_copy_copy_2 = wx.Button(self.r1_1_copy_1, -1, "Change")
        self.structure_file_copy_2 = wx.StaticText(self.r1_1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r11_copy_1 = wx.TextCtrl(self.r1_1_copy_1, -1, structure_file_pdb)
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
        self.relax_start_r1_1_copy_2 = wx.BitmapButton(self.r1_1_copy_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        #R2 no. 3
        self.bitmap_1_copy_copy_copy_copy_1 = wx.StaticBitmap(self.r2_1_copy_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'r2.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Set-up for R2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_r21_copy_1 = wx.TextCtrl(self.r2_1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_3_copy_copy_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21_copy_1 = wx.TextCtrl(self.r2_1_copy_1, -1, r2_savedir[2])
        self.results_directory_r21_copy_1 = wx.Button(self.r2_1_copy_1, -1, "Change")
        self.structure_file_copy_copy_1 = wx.StaticText(self.r2_1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21_copy_1 = wx.TextCtrl(self.r2_1_copy_1, -1, structure_file_pdb)
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
        self.relax_start_r1_1_copy_copy_1 = wx.BitmapButton(self.r2_1_copy_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))


        #Model-free
        self.bitmap_2 = wx.StaticBitmap(self.modelfree, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'modelfree.png', wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy_1_copy = wx.StaticText(self.modelfree, -1, "Set-up for Model-free analysis:")
        self.label_7 = wx.StaticText(self.panel_4, -1, "NMR freq 1:")
        self.modelfreefreq1 = wx.TextCtrl(self.panel_4, -1, "")
        self.label_8 = wx.StaticText(self.panel_4, -1, "NOE")
        self.m_noe_1 = wx.TextCtrl(self.panel_4, -1, "")
        self.model_noe_1 = wx.Button(self.panel_4, -1, "+")
        self.label_8_copy = wx.StaticText(self.panel_4, -1, "R1")
        self.m_r1_1 = wx.TextCtrl(self.panel_4, -1, "")
        self.model_r1_1 = wx.Button(self.panel_4, -1, "+")
        self.label_8_copy_copy = wx.StaticText(self.panel_4, -1, "R2")
        self.m_r2_1 = wx.TextCtrl(self.panel_4, -1, "")
        self.model_r2_1 = wx.Button(self.panel_4, -1, "+")
        self.label_7_copy = wx.StaticText(self.panel_4_copy, -1, "NMR freq 2:")
        self.modelfreefreq2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.label_8_copy_1 = wx.StaticText(self.panel_4_copy, -1, "NOE")
        self.m_noe_2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.model_noe_2 = wx.Button(self.panel_4_copy, -1, "+")
        self.label_8_copy_copy_1 = wx.StaticText(self.panel_4_copy, -1, "R1")
        self.m_r1_2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.model_r1_2 = wx.Button(self.panel_4_copy, -1, "+")
        self.label_8_copy_copy_copy = wx.StaticText(self.panel_4_copy, -1, "R2")
        self.m_r2_2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.model_r2_2 = wx.Button(self.panel_4_copy, -1, "+")
        self.label_7_copy_copy = wx.StaticText(self.panel_4_copy_1, -1, "NMR freq 3:")
        self.modelfreefreq3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.label_8_copy_1_copy = wx.StaticText(self.panel_4_copy_1, -1, "NOE")
        self.m_noe_3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.model_noe_3 = wx.Button(self.panel_4_copy_1, -1, "+")
        self.label_8_copy_copy_1_copy = wx.StaticText(self.panel_4_copy_1, -1, "R1")
        self.m_r1_3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.model_r1_3 = wx.Button(self.panel_4_copy_1, -1, "+")
        self.label_8_copy_copy_copy_copy = wx.StaticText(self.panel_4_copy_1, -1, "R2")
        self.m_r2_3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.model_r2_3 = wx.Button(self.panel_4_copy_1, -1, "+")
        self.label_9 = wx.StaticText(self.modelfree, -1, "Select Model-free models (default = all):")
        self.m0 = wx.ToggleButton(self.modelfree, -1, "m0")
        self.m1 = wx.ToggleButton(self.modelfree, -1, "m1")
        self.m2 = wx.ToggleButton(self.modelfree, -1, "m2")
        self.m3 = wx.ToggleButton(self.modelfree, -1, "m3")
        self.m4 = wx.ToggleButton(self.modelfree, -1, "m4")
        self.m5 = wx.ToggleButton(self.modelfree, -1, "m5")
        self.m6 = wx.ToggleButton(self.modelfree, -1, "m6")
        self.m7 = wx.ToggleButton(self.modelfree, -1, "m7")
        self.m8 = wx.ToggleButton(self.modelfree, -1, "m8")
        self.m9 = wx.ToggleButton(self.modelfree, -1, "m9")
        self.label_10 = wx.StaticText(self.modelfree, -1, "Select Model-free selection mode:      ")
        self.aic = wx.RadioButton(self.modelfree, -1, "AIC")
        self.bic = wx.RadioButton(self.modelfree, -1, "BIC")
        self.structure_file_copy_copy_1_copy = wx.StaticText(self.modelfree, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21_copy_1_copy = wx.TextCtrl(self.modelfree, -1, structure_file_pdb)
        self.structure_r21_copy_1_copy.SetEditable(False)
        self.chan_struc_r21_copy_1_copy = wx.Button(self.modelfree, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy = wx.StaticText(self.modelfree, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r21_copy_1_copy = wx.TextCtrl(self.modelfree, -1, "")
        self.label_2_copy_copy_3_copy_copy_copy_copy_2 = wx.StaticText(self.modelfree, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21_copy_2 = wx.TextCtrl(self.modelfree, -1, results_dir_model)
        self.results_directory_r21_copy_2 = wx.Button(self.modelfree, -1, "Change")
        self.label_5_copy_1_copy_3 = wx.StaticText(self.modelfree, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_modelfree = wx.BitmapButton(self.modelfree, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))

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

        self.Bind(wx.EVT_MENU, self.newGUI, id=1)
        self.Bind(wx.EVT_MENU, self.openGUI, id=2)
        self.Bind(wx.EVT_MENU, self.saveGUI, id=3)
        self.Bind(wx.EVT_MENU, self.exitGUI, id=4)
        self.Bind(wx.EVT_MENU, self.aboutGUI, id=5)
        self.Bind(wx.EVT_MENU, self.aboutrelax, id=6)
        self.Bind(wx.EVT_MENU, self.settings, id=7)
        self.Bind(wx.EVT_MENU, self.references, id=9)
        self.Bind(wx.EVT_BUTTON, self.sat_noe1, self.sat_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe, self.noe_ref_err_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.ref_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe1, self.chandir_noe1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe1, self.relax_start_noe1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_1, self.results_directory_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.results_directory_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r1_1, self.addr11)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_1, self.refreshr11)
        self.Bind(wx.EVT_BUTTON, self.exec_r2_1, self.relax_start_r1_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r2_1, self.results_directory_r21)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_r21)
        self.Bind(wx.EVT_BUTTON, self.add_r2_1, self.addr21)
        self.Bind(wx.EVT_BUTTON, self.refresh_r2_1, self.refreshr21)
        self.Bind(wx.EVT_BUTTON, self.exec_r1_1, self.relax_start_r1_1_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe2, self.sat_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.ref_noe2, self.noe_ref_err_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.ref_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe2, self.chandir_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_noe2, self.relax_start_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_2, self.results_directory_copy_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.results_directory_copy_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r1_2, self.addr11_copy)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_2, self.refreshr11_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_r1_2, self.relax_start_r1_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r2_2, self.results_directory_r21_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_r21_copy)
        self.Bind(wx.EVT_BUTTON, self.add_r2_2, self.addr21_copy)
        self.Bind(wx.EVT_BUTTON, self.refresh_r2_2, self.refreshr21_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_r2_2, self.relax_start_r1_1_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe3, self.sat_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe3, self.noe_ref_err_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.ref_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe3, self.chandir_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe3, self.relax_start_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_r1_3, self.results_directory_copy_copy_copy_2)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.results_directory_copy_copy_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.add_r1_3, self.addr11_copy_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_r1_3, self.refreshr11_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_r1_3, self.relax_start_r1_1_copy_2)
        self.Bind(wx.EVT_BUTTON, self.resdir_r2_3, self.results_directory_r21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_r21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.add_r2_3, self.addr21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_r2_3, self.refreshr21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_r2_3, self.relax_start_r1_1_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.model_noe1, self.model_noe_1)
        self.Bind(wx.EVT_BUTTON, self.model_r11, self.model_r1_1)
        self.Bind(wx.EVT_BUTTON, self.model_r21, self.model_r2_1)
        self.Bind(wx.EVT_BUTTON, self.model_noe2, self.model_noe_2)
        self.Bind(wx.EVT_BUTTON, self.model_r12, self.model_r1_2)
        self.Bind(wx.EVT_BUTTON, self.model_r22, self.model_r2_2)
        self.Bind(wx.EVT_BUTTON, self.model_noe3, self.model_noe_3)
        self.Bind(wx.EVT_BUTTON, self.model_r13, self.model_r1_3)
        self.Bind(wx.EVT_BUTTON, self.model_r23, self.model_r2_3)
        self.Bind(wx.EVT_RADIOBUTTON, self.sel_aic, self.aic)
        self.Bind(wx.EVT_RADIOBUTTON, self.sel_bic, self.bic)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_r21_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_modelfree, self.results_directory_r21_copy_2)
        self.Bind(wx.EVT_BUTTON, self.exec_model_free, self.relax_start_modelfree)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_noe_results_exe, self.list_noe)
        self.Bind(wx.EVT_BUTTON, self.open_noe_results_exe, self.open_noe_results)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_rx_results_exe, self.list_rx)
        self.Bind(wx.EVT_BUTTON, self.open_rx_results_exe, self.open_rx_results)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_model_results_exe, self.list_modelfree)
        self.Bind(wx.EVT_BUTTON, self.open_model_results_exe, self.open_model_results)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: main.__set_properties
        self.SetTitle("relaxGUI " + GUI_version)
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((1000, 600))
        self.frame_1_statusbar.SetStatusWidths([770, 50, -1])
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
        self.label_4_copy_copy_copy_copy_1_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_7.SetMinSize((80, 17))
        self.modelfreefreq1.SetMinSize((80, 20))
        self.label_8.SetMinSize((80, 17))
        self.m_noe_1.SetMinSize((120, 20))
        self.model_noe_1.SetMinSize((20, 20))
        self.model_noe_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy.SetMinSize((80, 17))
        self.m_r1_1.SetMinSize((120, 20))
        self.model_r1_1.SetMinSize((20, 20))
        self.model_r1_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy.SetMinSize((80, 17))
        self.m_r2_1.SetMinSize((120, 20))
        self.model_r2_1.SetMinSize((20, 20))
        self.model_r2_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_4.SetMinSize((230, 85))
        self.panel_4.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_7_copy.SetMinSize((80, 17))
        self.modelfreefreq2.SetMinSize((80, 20))
        self.label_8_copy_1.SetMinSize((80, 17))
        self.m_noe_2.SetMinSize((120, 20))
        self.model_noe_2.SetMinSize((20, 20))
        self.model_noe_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_1.SetMinSize((80, 17))
        self.m_r1_2.SetMinSize((120, 20))
        self.model_r1_2.SetMinSize((20, 20))
        self.model_r1_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_2.SetMinSize((120, 20))
        self.model_r2_2.SetMinSize((20, 20))
        self.model_r2_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_4_copy.SetMinSize((230, 85))
        self.panel_4_copy.SetBackgroundColour(wx.Colour(176, 176, 176))
        self.label_7_copy_copy.SetMinSize((80, 17))
        self.modelfreefreq3.SetMinSize((80, 20))
        self.label_8_copy_1_copy.SetMinSize((80, 17))
        self.m_noe_3.SetMinSize((120, 20))
        self.model_noe_3.SetMinSize((20, 20))
        self.model_noe_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_1_copy.SetMinSize((80, 17))
        self.m_r1_3.SetMinSize((120, 20))
        self.model_r1_3.SetMinSize((20, 20))
        self.model_r1_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_3.SetMinSize((120, 20))
        self.model_r2_3.SetMinSize((20, 20))
        self.model_r2_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_4_copy_1.SetMinSize((230, 85))
        self.panel_4_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.m0.SetMinSize((70, 25))
        self.m0.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m0.SetToolTipString("{}")
        self.m0.SetValue(1)
        self.m1.SetMinSize((70, 25))
        self.m1.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m1.SetToolTipString("{S2}")
        self.m1.SetValue(1)
        self.m2.SetMinSize((70, 25))
        self.m2.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m2.SetToolTipString("{S2, te}")
        self.m2.SetValue(1)
        self.m3.SetMinSize((70, 25))
        self.m3.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m3.SetToolTipString("{S2, Rex}")
        self.m3.SetValue(1)
        self.m4.SetMinSize((70, 25))
        self.m4.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m4.SetToolTipString("{S2, te, Rex}")
        self.m4.SetValue(1)
        self.m5.SetMinSize((70, 25))
        self.m5.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m5.SetToolTipString("{S2, S2f, ts}")
        self.m5.SetValue(1)
        self.m6.SetMinSize((70, 25))
        self.m6.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m6.SetToolTipString("{S2, tf, S2f, ts}")
        self.m6.SetValue(1)
        self.m7.SetMinSize((70, 25))
        self.m7.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m7.SetToolTipString("{S2, S2f, ts, Rex}")
        self.m7.SetValue(1)
        self.m8.SetMinSize((70, 25))
        self.m8.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m8.SetToolTipString("{S2, tf, S2f, ts, Rex}")
        self.m8.SetValue(1)
        self.m9.SetMinSize((70, 25))
        self.m9.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m9.SetToolTipString("{Rex}")
        self.m9.SetValue(1)
        self.label_10.SetMinSize((240, 17))
        self.label_10.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.aic.SetMinSize((60, 22))
        self.structure_file_copy_copy_1_copy.SetMinSize((240, 17))
        self.structure_file_copy_copy_1_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.structure_r21_copy_1_copy.SetMinSize((350, 27))
        self.chan_struc_r21_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy.SetMinSize((240, 17))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.unresolved_r21_copy_1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy_2.SetMinSize((240, 17))
        self.label_2_copy_copy_3_copy_copy_copy_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.resultsdir_r21_copy_2.SetMinSize((350, 27))
        self.results_directory_r21_copy_2.SetMinSize((103, 27))
        self.label_5_copy_1_copy_3.SetMinSize((118, 17))
        self.label_5_copy_1_copy_3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.relax_start_modelfree.SetName('hello')
        self.relax_start_modelfree.SetSize(self.relax_start_modelfree.GetBestSize())
        self.modelfree.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_11.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.list_noe.SetMinSize((800, 150))
        self.list_noe.SetSelection(0)
        self.open_noe_results.SetMinSize((80, 32))
        self.label_11_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.list_rx.SetMinSize((800, 150))
        self.list_rx.SetSelection(0)
        self.open_rx_results.SetMinSize((80, 32))
        self.label_11_copy_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.list_modelfree.SetMinSize((800, 150))
        self.list_modelfree.SetSelection(0)
        self.open_model_results.SetMinSize((80, 32))
        # end wxGlade

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
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_20 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
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
        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
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
        sizer_14.Add(self.bitmap_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(self.label_4_copy_copy_copy_copy_1_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        sizer_18.Add(self.label_7, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18.Add(self.modelfreefreq1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_18, 0, 0, 0)
        sizer_19.Add(self.label_8, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19.Add(self.m_noe_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19.Add(self.model_noe_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy.Add(self.label_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy.Add(self.m_r1_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy.Add(self.model_r1_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy.Add(self.label_8_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy.Add(self.m_r2_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy.Add(self.model_r2_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_4.SetSizer(sizer_17)
        sizer_16.Add(self.panel_4, 0, 0, 0)
        sizer_18_copy.Add(self.label_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18_copy.Add(self.modelfreefreq2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_18_copy, 0, 0, 0)
        sizer_19_copy_1.Add(self.label_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1.Add(self.m_noe_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1.Add(self.model_noe_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_1.Add(self.label_8_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1.Add(self.m_r1_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1.Add(self.model_r1_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_copy.Add(self.label_8_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy.Add(self.m_r2_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy.Add(self.model_r2_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_4_copy.SetSizer(sizer_17_copy)
        sizer_16.Add(self.panel_4_copy, 0, 0, 0)
        sizer_18_copy_copy.Add(self.label_7_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18_copy_copy.Add(self.modelfreefreq3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_18_copy_copy, 0, 0, 0)
        sizer_19_copy_1_copy.Add(self.label_8_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1_copy.Add(self.m_noe_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1_copy.Add(self.model_noe_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_1_copy.Add(self.label_8_copy_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1_copy.Add(self.m_r1_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1_copy.Add(self.model_r1_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_copy_copy.Add(self.label_8_copy_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy_copy.Add(self.m_r2_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy_copy.Add(self.model_r2_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_4_copy_1.SetSizer(sizer_17_copy_copy)
        sizer_16.Add(self.panel_4_copy_1, 0, 0, 0)
        sizer_15.Add(sizer_16, 0, 0, 0)
        sizer_15.Add(self.label_9, 0, wx.TOP|wx.ADJUST_MINSIZE, 10)
        sizer_20.Add(self.m0, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m4, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m5, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m6, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m7, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m8, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m9, 0, wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(sizer_20, 1, wx.EXPAND, 0)
        sizer_21.Add(self.label_10, 0, wx.TOP|wx.ADJUST_MINSIZE, 1)
        sizer_21.Add(self.aic, 0, wx.ADJUST_MINSIZE, 0)
        sizer_21.Add(self.bic, 0, wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(sizer_21, 1, wx.TOP|wx.EXPAND, 5)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.structure_file_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.structure_r21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.chan_struc_r21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_15.Add(results_dir_copy_copy_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy_1_copy.Add(self.unresolved_r21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(nmr_freq_copy_copy_copy_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.label_2_copy_copy_3_copy_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.resultsdir_r21_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.results_directory_r21_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_15.Add(results_dir_copy_copy_copy_1_copy_2, 1, wx.EXPAND, 0)
        exec_relax_copy_1_copy_3.Add(self.label_5_copy_1_copy_3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_3.Add(self.relax_start_modelfree, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(exec_relax_copy_1_copy_3, 1, wx.ALIGN_RIGHT, 0)
        sizer_14.Add(sizer_15, 0, 0, 0)
        self.modelfree.SetSizer(sizer_14)
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
        # end wxGlade


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# GUI actions


#menu

    def newGUI(self, event): # New
        newdir = diropenbox(msg='Select results directory', title='relaxGUI', default='*')
        if not newdir == None:
            #create directories
            os.system('mkdir ' + newdir + sep + 'NOE_1')
            os.system('mkdir ' + newdir + sep + 'NOE_2')
            os.system('mkdir ' + newdir + sep + 'NOE_3')
            os.system('mkdir ' + newdir + sep + 'R1_1')
            os.system('mkdir ' + newdir + sep + 'R1_2')
            os.system('mkdir ' + newdir + sep + 'R1_3')
            os.system('mkdir ' + newdir + sep + 'R2_1')
            os.system('mkdir ' + newdir + sep + 'R2_2')
            os.system('mkdir ' + newdir + sep + 'R2_3')
            os.system('mkdir ' + newdir + sep + 'model_free')
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

            msgbox(msg = 'Folder structure created for Model-free analysis:\n\n\n' + newdir + sep + 'NOE_1\n' + newdir + sep + 'NOE_2\n' + newdir + sep + 'NOE_3\n' + newdir + sep + 'R1_1\n' + newdir + sep + 'R1_2\n' + newdir + sep + 'R1_3\n' + newdir + sep + 'R2_1\n' + newdir + sep + 'R2_2\n' + newdir + sep + 'R2_3\n' + newdir + sep + 'model-free', title = 'relaxGUI')
        event.Skip()


    def references(self, event):
        webbrowser.open_new('http://www.nmr-relax.com/refs.html')
        event.Skip()


    def import_seq(self, event): # open load sequence panel
        global sequencefile  #load global variable
        temp = load_sequence(self)
        if not temp == None:
           sequencefile = temp #set sequence file
          
           # set entries in pdb text box
           structure_file_pdb = '!!! Sequence file selected !!!'
           self.structure_noe1.SetValue(structure_file_pdb)
           self.structure_t11.SetValue(structure_file_pdb)
           self.structure_t21.SetValue(structure_file_pdb)
           self.structure_noe1_copy.SetValue(structure_file_pdb)
           self.structure_t11_copy.SetValue(structure_file_pdb)
           self.structure_t21_copy.SetValue(structure_file_pdb)
           self.structure_noe1_copy_1.SetValue(structure_file_pdb)
           self.structure_t11_copy_1.SetValue(structure_file_pdb)
           self.structure_t21_copy_1.SetValue(structure_file_pdb)
        event.Skip()


    def settings(self, event): # set up for relax variables
        global global_setting #import global variable
        tmp_global = relax_global_settings(global_setting)
        if not tmp_global == None:
            if question('Do you realy want to change relax settings?'):
              global_setting = tmp_global 
        event.Skip()


    def param_file_setting(self, event): # set up parameter files
        global file_setting # import global variable
        tmp_setting = import_file_settings(file_setting)
        if not tmp_setting == None:
            if question('Do you realy want to change import file settings?'):
             file_setting = tmp_setting
        event.Skip()


    def reset_setting(self, event): #reset all settings
        global global_setting #import global variable
        global file_setting # import global variable
        if question('Do you realy want to change relax settings?'):
            global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
            file_setting = ['0', '1', '2', '3', '4', '5', '6']


    def openGUI(self, event): # Open
        filename = fileopenbox(msg=None, title='Open relaxGUI save file', default = "*.relaxGUI")
        if not filename == None:
           open_file(self, filename)
        event.Skip()

    def saveGUI(self, event): # Save
     filename = filesavebox(msg=None, title='Save File as', default = "*.relaxGUI")
     if not filename == None: 
        create_save_file(self, filename)
     event.Skip()

    def exitGUI(self, event): # Exit
        doexit = ynbox(msg='Do you wand to quit relaxGUI?', title='relaxGUI', choices=('Yes', 'No'), image=None)
        if doexit == True:
           print "\n\n\nExiting relaxGUI......\n\n\n"
           sys.exit(0)
        event.Skip()

    def aboutGUI(self, event): # About
        about_relax()
        event.Skip()

    def aboutrelax(self, event): # abour relax
        webbrowser.open_new('http://www.nmr-relax.com')
        event.Skip()

### NOE no. 1


    def sat_noe1(self, event): # saturated noe 1
        backup = self.noe_sat_1.GetValue()
        noesat[0] = fileopenbox(msg='Select saturated NOE file ('+ str(nmrfreq[0]) + ' MHz)', title='relaxGUI', default=self.res_noe1.GetValue() + sep, filetypes=None)
        if noesat[0] == None:
           noesat[0] = backup
        self.noe_sat_1.SetValue(noesat[0])
        event.Skip()

    def ref_noe(self, event): # reference noe 1
        backup = self.noe_ref_1.GetValue()
        noeref[0] = fileopenbox(msg='Select reference NOE file ('+ str(nmrfreq[0]) + ' MHz)', title='relaxGUI', default=self.res_noe1.GetValue() + sep, filetypes=None)
        if noeref[0] == None:
           noeref[0] = backup
        self.noe_ref_1.SetValue(noeref[0])
        event.Skip()

    def structure_pdb(self, event): # structure file
        backup = self.structure_noe1.GetValue()
        structure_file_pdb = fileopenbox(msg='Select PDB file', title='relaxGUI', default=self.res_noe1.GetValue() + sep, filetypes=None)
        if structure_file_pdb == None:
           structure_file_pdb = backup
        self.structure_noe1.SetValue(structure_file_pdb)
        self.structure_r11.SetValue(structure_file_pdb)
        self.structure_r21.SetValue(structure_file_pdb)
        self.structure_noe1_copy.SetValue(structure_file_pdb)
        self.structure_r11_copy.SetValue(structure_file_pdb)
        self.structure_r21_copy.SetValue(structure_file_pdb)
        self.structure_noe1_copy_1.SetValue(structure_file_pdb)
        self.structure_r11_copy_1.SetValue(structure_file_pdb)
        self.structure_r21_copy_1.SetValue(structure_file_pdb)
        self.structure_r21_copy_1_copy.SetValue(structure_file_pdb)
        event.Skip()

    def resdir_noe1(self, event): # noe 1 results dir
        backup = self.res_noe1.GetValue()
        noe_savedir[0] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.res_noe1.GetValue() + sep)
        if noe_savedir[0] == None:
           noe_savedir[0] = backup
        self.res_noe1.SetValue(noe_savedir[0])
        event.Skip()

    def exec_noe1(self, event): # Start NOE calculation no. 1
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')

        if start_relax == True:
           make_noe(self.res_noe1.GetValue(), self.noe_ref_1.GetValue(), self.noe_sat_1.GetValue(), self.noe_ref_err_1.GetValue(), self.noe_sat_err_1.GetValue(), self.nmrfreq_value_noe1.GetValue(),self.structure_noe1.GetValue(), self.unres_noe1.GetValue(), start_relax, self, 1)
        event.Skip()

          

##### R1 no. 1

    def resdir_r1_1(self, event): # R1 results dir 1
        backup = self.resultsdir_r11.GetValue()
        r1_savedir[0] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.resultsdir_r11.GetValue() + sep)
        if r1_savedir[0] == None:
           r1_savedir[0] = backup
        self.resultsdir_r11.SetValue(r1_savedir[0])

        event.Skip()

    def add_r1_1(self, event): # add a r1 peak list

        if len(r1_list) < 14:
             r1_entry = fileopenbox(msg='Select R1 peak list file', title=None, default=self.resultsdir_r11.GetValue() + sep, filetypes=None)
             if not r1_entry == None:
                r1_list.append(r1_entry)

        if len(r1_list) == 1:
            self.r1_list_1.SetLabel(r1_list[0]) 
        if len(r1_list) == 2:
            self.r1_list_2.SetLabel(r1_list[1]) 
        if len(r1_list) == 3:
            self.r1_list_3.SetLabel(r1_list[2]) 
        if len(r1_list) == 4:
            self.r1_list_4.SetLabel(r1_list[3]) 
        if len(r1_list) == 5:
            self.r1_list_5.SetLabel(r1_list[4]) 
        if len(r1_list) == 6:
            self.r1_list_6.SetLabel(r1_list[5]) 
        if len(r1_list) == 7:
            self.r1_list_7.SetLabel(r1_list[6]) 
        if len(r1_list) == 8:
            self.r1_list_8.SetLabel(r1_list[7]) 
        if len(r1_list) == 9:
            self.r1_list_9.SetLabel(r1_list[8]) 
        if len(r1_list) == 10:
            self.r1_list_10.SetLabel(r1_list[9]) 
        if len(r1_list) == 11:
            self.r1_list_11.SetLabel(r1_list[10]) 
        if len(r1_list) == 12:
            self.r1_list_12.SetLabel(r1_list[11]) 
        if len(r1_list) == 13:
            self.r1_list_1_copy_11.SetLabel(r1_list[12]) 
        if len(r1_list) == 14:
            self.r1_list_14.SetLabel(r1_list[13])              
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
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_rx(self.resultsdir_r11.GetValue(), relax_times_r1_1, self.structure_r11.GetValue(), self.nmrfreq_value_r11.GetValue(), 1, 1, self.unresolved_r11.GetValue(), self, 1)
        event.Skip()

### Execute R2 no. 1

    def resdir_r2_1(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r21.GetValue()
        r2_savedir[0] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.resultsdir_r21.GetValue() + sep)
        if r2_savedir[0] == None:
           r2_savedir[0] = backup
        self.resultsdir_r21.SetValue(r2_savedir[0])
        event.Skip()

    def add_r2_1(self, event): # add a r2 peak list
        if len(r2_list) < 14:
             r2_entry = fileopenbox(msg='Select R2 peak list file', title='relaxGUI', default=self.resultsdir_r21.GetValue() + sep, filetypes=None)
             if not r2_entry == None:
                r2_list.append(r2_entry)
        if len(r2_list) == 1:
            self.r2_list_1.SetLabel(r2_list[0]) 
        if len(r2_list) == 2:
            self.r2_list_2.SetLabel(r2_list[1]) 
        if len(r2_list) == 3:
            self.r2_list_3.SetLabel(r2_list[2]) 
        if len(r2_list) == 4:
            self.r2_list_4.SetLabel(r2_list[3]) 
        if len(r2_list) == 5:
            self.r2_list_5.SetLabel(r2_list[4]) 
        if len(r2_list) == 6:
            self.r2_list_6.SetLabel(r2_list[5]) 
        if len(r2_list) == 7:
            self.r2_list_7.SetLabel(r2_list[6]) 
        if len(r2_list) == 8:
            self.r2_list_8.SetLabel(r2_list[7]) 
        if len(r2_list) == 9:
            self.r2_list_9.SetLabel(r2_list[8]) 
        if len(r2_list) == 10:
            self.r2_list_10.SetLabel(r2_list[9]) 
        if len(r2_list) == 11:
            self.r2_list_11.SetLabel(r2_list[10]) 
        if len(r2_list) == 12:
            self.r2_list_12.SetLabel(r2_list[11]) 
        if len(r2_list) == 13:
            self.r2_list_13.SetLabel(r2_list[12]) 
        if len(r2_list) == 14:
            self.r2_list_14.SetLabel(r2_list[13])              
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
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_rx(self.resultsdir_r21.GetValue(), relax_times_r2_1, self.structure_r11.GetValue(), self.nmrfreq_value_r11.GetValue(), 2, 1, self.unresolved_r11.GetValue(), self,1)
        event.Skip()

### NOE no. 2

    def sat_noe2(self, event): # saturated noe no. 2
        backup = self.noe_sat_1_copy.GetValue()
        noesat[1] = fileopenbox(msg='Select saturated NOE file ('+ str(nmrfreq[1]) + ' MHz)', title=None, default= self.res_noe1_copy.GetValue() + sep, filetypes=None)
        if noesat[1] == None:
           noesat[1] = backup
        self.noe_sat_1_copy.SetValue(noesat[1])
        event.Skip()

    def ref_noe2(self, event): # reference noe no. 2
        backup = self.noe_ref_1_copy.GetValue()
        noeref[1] = fileopenbox(msg='Select reference NOE file ('+ str(nmrfreq[1]) + ' MHz)', title=None, default=self.res_noe1_copy.GetValue() + sep, filetypes=None)
        if noeref[1] == None:
           noeref[1] = backup
        self.noe_ref_1_copy.SetValue(noeref[1])
        event.Skip()

    def resdir_noe2(self, event): # noe results dir no. 2
        backup = self.res_noe1_copy.GetValue()
        noe_savedir[1] = diropenbox(msg='Select results directory', title='relaxGUI', default = self.res_noe1_copy.GetValue() + sep)
        if noe_savedir[1] == None:
           noe_savedir[1] = backup
        self.res_noe1_copy.SetValue(noe_savedir[1])
        event.Skip()

    def exec_noe2(self, event): # start noe 2 calculation
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_noe(self.res_noe1_copy.GetValue(), self.noe_ref_1_copy.GetValue(), self.noe_sat_1_copy.GetValue(), self.noe_ref_err_1_copy.GetValue(), self.noe_sat_err_1_copy.GetValue(), self.nmrfreq_value_noe1_copy.GetValue(),self.structure_noe1_copy.GetValue(), self.unres_noe1_copy.GetValue(), start_relax, self, 2)
        event.Skip()

### R1 no. 2

    def resdir_r1_2(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r11_copy.GetValue()
        r1_savedir[1] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.resultsdir_r11_copy.GetValue() + sep)
        if r1_savedir[1] == None:
           r1_savedir[1] = backup
        self.resultsdir_r11_copy.SetValue(r1_savedir[1])
        event.Skip()

    def add_r1_2(self, event): # wxGlade: main.<event_handler>
        if len(r1_list2) < 14:
             r1_entry2 = fileopenbox(msg='Select R1 peak list file', title=None, default=self.resultsdir_r11_copy.GetValue() + sep, filetypes=None)
             if not r1_entry2 == None:
                r1_list2.append(r1_entry2)
        if len(r1_list2) == 1:
            self.r1_list_1_copy.SetLabel(r1_list2[0]) 
        if len(r1_list2) == 2:
            self.r1_list_2_copy.SetLabel(r1_list2[1]) 
        if len(r1_list2) == 3:
            self.r1_list_3_copy.SetLabel(r1_list2[2]) 
        if len(r1_list2) == 4:
            self.r1_list_4_copy.SetLabel(r1_list2[3]) 
        if len(r1_list2) == 5:
            self.r1_list_5_copy.SetLabel(r1_list2[4]) 
        if len(r1_list2) == 6:
            self.r1_list_6_copy.SetLabel(r1_list2[5]) 
        if len(r1_list2) == 7:
            self.r1_list_7_copy.SetLabel(r1_list2[6]) 
        if len(r1_list2) == 8:
            self.r1_list_8_copy.SetLabel(r1_list2[7]) 
        if len(r1_list2) == 9:
            self.r1_list_9_copy.SetLabel(r1_list2[8]) 
        if len(r1_list2) == 10:
            self.r1_list_10_copy.SetLabel(r1_list2[9]) 
        if len(r1_list2) == 11:
            self.r1_list_11_copy.SetLabel(r1_list2[10]) 
        if len(r1_list2) == 12:
            self.r1_list_12_copy.SetLabel(r1_list2[11]) 
        if len(r1_list2) == 13:
            self.r1_list_1_copy_11_copy.SetLabel(r1_list2[12]) 
        if len(r1_list2) == 14:
            self.r1_list_14_copy.SetLabel(r1_list2[13])              
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

        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_rx(self.resultsdir_r11_copy.GetValue(), relax_times_r1_2, self.structure_r11_copy.GetValue(), self.nmrfreq_value_r11_copy.GetValue(), 1, 2, self.unresolved_r11_copy.GetValue(), self,2)
        event.Skip()

### R2 no. 2

    def resdir_r2_2(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r21_copy.GetValue()
        r2_savedir[1] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.resultsdir_r21_copy.GetValue() + sep)
        if r2_savedir[1] == None:
           r2_savedir[1] = backup
        self.resultsdir_r21_copy.SetValue(r2_savedir[1])
        event.Skip()

    def add_r2_2(self, event): # add a r2 peak list
        if len(r2_list2) < 14:
             r2_entry2 = fileopenbox(msg='Select R2 peak list file', title='relaxGUI', default=self.resultsdir_r21_copy.GetValue() + sep, filetypes=None)
             if not r2_entry2 == None:
                r2_list2.append(r2_entry2)
        if len(r2_list2) == 1:
            self.r2_list_1_copy.SetLabel(r2_list2[0]) 
        if len(r2_list2) == 2:
            self.r2_list_2_copy.SetLabel(r2_list2[1]) 
        if len(r2_list2) == 3:
            self.r2_list_3_copy.SetLabel(r2_list2[2]) 
        if len(r2_list2) == 4:
            self.r2_list_4_copy.SetLabel(r2_list2[3]) 
        if len(r2_list2) == 5:
            self.r2_list_5_copy.SetLabel(r2_list2[4]) 
        if len(r2_list2) == 6:
            self.r2_list_6_copy.SetLabel(r2_list2[5]) 
        if len(r2_list2) == 7:
            self.r2_list_7_copy.SetLabel(r2_list2[6]) 
        if len(r2_list2) == 8:
            self.r2_list_8_copy.SetLabel(r2_list2[7]) 
        if len(r2_list2) == 9:
            self.r2_list_9_copy.SetLabel(r2_list2[8]) 
        if len(r2_list2) == 10:
            self.r2_list_10_copy.SetLabel(r2_list2[9]) 
        if len(r2_list2) == 11:
            self.r2_list_11_copy.SetLabel(r2_list2[10]) 
        if len(r2_list2) == 12:
            self.r2_list_12_copy.SetLabel(r2_list2[11]) 
        if len(r2_list2) == 13:
            self.r2_list_13_copy.SetLabel(r2_list2[12]) 
        if len(r2_list2) == 14:
            self.r2_list_14_copy.SetLabel(r2_list2[13])              
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

        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_rx(self.resultsdir_r21_copy.GetValue(), relax_times_r2_2, self.structure_r11_copy.GetValue(), self.nmrfreq_value_r11_copy.GetValue(), 2, 2, self.unresolved_r11_copy.GetValue(), self,2)
        event.Skip()

### NOE no. 3

    def sat_noe3(self, event): # saturated noe no. 3
        backup = self.noe_sat_1_copy_1.GetValue()
        noesat[2] = fileopenbox(msg='Select saturated NOE file ('+ str(nmrfreq[2]) + ' MHz)', title='relaxGUI', default= self.res_noe1_copy_1.GetValue() + sep, filetypes=None)
        if noesat[2] == None:
           noesat[2] = backup
        self.noe_sat_1_copy_1.SetValue(noesat[2])
        event.Skip()

    def ref_noe3(self, event): # refererence noe 3
        backup = self.noe_ref_1_copy_1.GetValue()
        noeref[2] = fileopenbox(msg='Select reference NOE file ('+ str(nmrfreq[2]) + ' MHz)', title=None, default=self.res_noe1_copy_1.GetValue() + sep, filetypes=None)
        if noeref[2] == None:
           noeref[2] = backup
        self.noe_ref_1_copy_1.SetValue(noeref[2])
        event.Skip()

    def resdir_noe3(self, event): # noe 3 results dir
        backup = self.res_noe1_copy_1.GetValue()
        noe_savedir[2] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.res_noe1_copy_1.GetValue() + sep)
        if noe_savedir[2] == None:
           noe_savedir[2] = backup
        self.res_noe1_copy_1.SetValue(noe_savedir[2])
        event.Skip()

    def exec_noe3(self, event): # calculate noe 3
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_noe(self.res_noe1_copy_1.GetValue(), self.noe_ref_1_copy_1.GetValue(), self.noe_sat_1_copy_1.GetValue(), self.noe_ref_err_1_copy_1.GetValue(), self.noe_sat_err_1_copy_1.GetValue(), self.nmrfreq_value_noe1_copy_1.GetValue(),self.structure_noe1_copy_1.GetValue(), self.unres_noe1_copy_1.GetValue(), start_relax, self, 3)
        event.Skip()

### R1 no. 3

    def resdir_r1_3(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_r11_copy_1.GetValue()
        r1_savedir[2] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.resultsdir_r11_copy_1.GetValue() + sep)
        if r1_savedir[2] == None:
           r1_savedir[2] = backup
        self.resultsdir_r11_copy_1.SetValue(r1_savedir[2])
        event.Skip()

    def add_r1_3(self, event): # wxGlade: main.<event_handler>
        if len(r1_list3) < 14:
             r1_entry3 = fileopenbox(msg='Select R1 peak list file', title=None, default=self.resultsdir_r11_copy_1.GetValue() + sep, filetypes=None)
             if not r1_entry3 == None:
                r1_list3.append(r1_entry3)

        if len(r1_list3) == 1:
            self.r1_list_1_copy_1.SetLabel(r1_list3[0]) 
        if len(r1_list3) == 2:
            self.r1_list_2_copy_1.SetLabel(r1_list3[1]) 
        if len(r1_list3) == 3:
            self.r1_list_3_copy_1.SetLabel(r1_list3[2]) 
        if len(r1_list3) == 4:
            self.r1_list_4_copy_1.SetLabel(r1_list3[3]) 
        if len(r1_list3) == 5:
            self.r1_list_5_copy_1.SetLabel(r1_list3[4]) 
        if len(r1_list3) == 6:
            self.r1_list_6_copy_1.SetLabel(r1_list3[5]) 
        if len(r1_list3) == 7:
            self.r1_list_7_copy_1.SetLabel(r1_list3[6]) 
        if len(r1_list3) == 8:
            self.r1_list_8_copy_1.SetLabel(r1_list3[7]) 
        if len(r1_list3) == 9:
            self.r1_list_9_copy_1.SetLabel(r1_list3[8]) 
        if len(r1_list3) == 10:
            self.r1_list_10_copy_1.SetLabel(r1_list3[9]) 
        if len(r1_list3) == 11:
            self.r1_list_11_copy_1.SetLabel(r1_list3[10]) 
        if len(r1_list3) == 12:
            self.r1_list_12_copy_1.SetLabel(r1_list3[11]) 
        if len(r1_list3) == 13:
            self.r1_list_1_copy_11_copy_1.SetLabel(r1_list3[12]) 
        if len(r1_list3) == 14:
            self.r1_list_14_copy_1.SetLabel(r1_list3[13])              
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
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_rx(self.resultsdir_r11_copy_1.GetValue(), relax_times_r1_3, self.structure_r11_copy_1.GetValue(), self.nmrfreq_value_r11_copy_1.GetValue(), 1, 3, self.unresolved_r11_copy_1.GetValue(), self,3)
        event.Skip()


### R2 no. 3

    def resdir_r2_3(self, event): # results dir R2 3
        backup = self.resultsdir_r21_copy_1.GetValue()
        r2_savedir[2] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.resultsdir_r21_copy_1.GetValue() + sep)
        if r2_savedir[2] == None:
           r2_savedir[2] = backup
        self.resultsdir_r21_copy_1.SetValue(r2_savedir[2])
        event.Skip()

    def add_r2_3(self, event): # add R2 peakfile no. 3
        if len(r2_list3) < 14:
             r2_entry3 = fileopenbox(msg='Select R2 peak list file', title='relaxGUI', default=self.resultsdir_r21_copy_1.GetValue() + sep, filetypes=None)
             if not r2_entry3 == None:
                r2_list3.append(r2_entry3)
        if len(r2_list3) == 1:
            self.r2_list_1_copy_1.SetLabel(r2_list3[0]) 
        if len(r2_list3) == 2:
            self.r2_list_2_copy_1.SetLabel(r2_list3[1]) 
        if len(r2_list3) == 3:
            self.r2_list_3_copy_1.SetLabel(r2_list3[2]) 
        if len(r2_list3) == 4:
            self.r2_list_4_copy_1.SetLabel(r2_list3[3]) 
        if len(r2_list3) == 5:
            self.r2_list_5_copy_1.SetLabel(r2_list3[4]) 
        if len(r2_list3) == 6:
            self.r2_list_6_copy_1.SetLabel(r2_list3[5]) 
        if len(r2_list3) == 7:
            self.r2_list_7_copy_1.SetLabel(r2_list3[6]) 
        if len(r2_list3) == 8:
            self.r2_list_8_copy_1.SetLabel(r2_list3[7]) 
        if len(r2_list3) == 9:
            self.r2_list_9_copy_1.SetLabel(r2_list3[8]) 
        if len(r2_list3) == 10:
            self.r2_list_10_copy_1.SetLabel(r2_list3[9]) 
        if len(r2_list3) == 11:
            self.r2_list_11_copy_1.SetLabel(r2_list3[10]) 
        if len(r2_list3) == 12:
            self.r2_list_12_copy_1.SetLabel(r2_list3[11]) 
        if len(r2_list3) == 13:
            self.r2_list_13_copy_1.SetLabel(r2_list3[12]) 
        if len(r2_list3) == 14:
            self.r2_list_14_copy_1.SetLabel(r2_list3[13])              
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

        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif')
        if start_relax == True:
           make_rx(self.resultsdir_r21_copy_1.GetValue(), relax_times_r2_3, self.structure_r11_copy_1.GetValue(), self.nmrfreq_value_r11_copy_1.GetValue(), 2, 3, self.unresolved_r11_copy_1.GetValue(), self,3)
        event.Skip()

### Model-free analysis

    def model_noe1(self, event): # load noe1
        backup = self.m_noe_1.GetValue() 
        paramfiles1[0] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_noe_1.GetValue() + sep, filetypes=None)
        if paramfiles1[0] == None:
           paramfiles1[0] = backup
        self.m_noe_1.SetValue(paramfiles1[0])
        event.Skip()

    def model_r11(self, event): # 
        backup = self.m_r1_1.GetValue() 
        paramfiles1[1] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r1_1.GetValue() + sep, filetypes=None)
        if paramfiles1[1] == None:
           paramfiles1[1] = backup
        self.m_r1_1.SetValue(paramfiles1[1])
        event.Skip()

    def model_r21(self, event): # 
        backup = self.m_r2_1.GetValue() 
        paramfiles1[2] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r2_1.GetValue() + sep, filetypes=None)
        if paramfiles1[2] == None:
           paramfiles1[2] = backup
        self.m_r2_1.SetValue(paramfiles1[2])
        event.Skip()

    def model_noe2(self, event): # load noe1
        backup = self.m_noe_2.GetValue() 
        paramfiles2[0] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_noe_2.GetValue() + sep, filetypes=None)
        if paramfiles2[0] == None:
           paramfiles2[0] = backup
        self.m_noe_2.SetValue(paramfiles2[0])
        event.Skip()

    def model_r12(self, event): # 
        backup = self.m_r1_2.GetValue() 
        paramfiles2[1] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r1_2.GetValue() + sep, filetypes=None)
        if paramfiles2[1] == None:
           paramfiles2[1] = backup
        self.m_r1_2.SetValue(paramfiles2[1])
        event.Skip()

    def model_r22(self, event): # 
        backup = self.m_r2_2.GetValue() 
        paramfiles2[2] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r2_2.GetValue() + sep, filetypes=None)
        if paramfiles2[2] == None:
           paramfiles2[2] = backup
        self.m_r2_2.SetValue(paramfiles2[2])
        event.Skip()

    def model_noe3(self, event): # load noe1
        backup = self.m_noe_3.GetValue() 
        paramfiles3[0] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_noe_3.GetValue() + sep, filetypes=None)
        if paramfiles3[0] == None:
           paramfiles3[0] = backup
        self.m_noe_3.SetValue(paramfiles3[0])
        event.Skip()

    def model_r13(self, event): 
        backup = self.m_r1_3.GetValue() 
        paramfiles3[1] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r1_3.GetValue() + sep, filetypes=None)
        if paramfiles3[1] == None:
           paramfiles3[1] = backup
        self.m_r1_3.SetValue(paramfiles3[1])
        event.Skip()

    def model_r23(self, event): 
        backup = self.m_r2_3.GetValue() 
        paramfiles3[2] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r2_3.GetValue() + sep, filetypes=None)
        if paramfiles3[2] == None:
           paramfiles3[2] = backup
        self.m_r2_3.SetValue(paramfiles3[2])
        event.Skip()

    def sel_aic(self, event): 
        selection = "AIC" 
        event.Skip()

    def sel_bic(self, event): 
        selection = "BIC"
        event.Skip()

    def resdir_modelfree(self, event): 
        backup = self.resultsdir_r21_copy_2.GetValue()
        results_dir_model = diropenbox(msg='Select results directory', title='relaxGUI', default=backup + sep)
        if results_dir_model == None:
           results_dir_model = backup
        self.resultsdir_r21_copy_2.SetValue(results_dir_model)
        event.Skip()

    def exec_model_free(self, event):
        which_model = buttonbox(msg='Start relax?', title='relaxGUI', choices=('local_tm', 'sphere', 'oblate', 'prolate', 'ellipsoid','final', 'cancel'), image=sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif', root=None) 
        if not which_model == 'cancel':
           start_model_free(self, which_model)
        event.Skip()   

    def open_noe_results_exe(self, event): 
        choice = self.list_noe.GetStringSelection()
        see_results(choice)
        event.Skip()

    def open_rx_results_exe(self, event): 
        choice = self.list_rx.GetStringSelection()
        see_results(choice)
        event.Skip()

    def open_model_results_exe(self, event): 
        choice = self.list_modelfree.GetStringSelection()
        see_results(choice)
        event.Skip()
