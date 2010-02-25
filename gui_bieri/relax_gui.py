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
import platform
from re import search
from string import lower, lowercase, replace
from textwrap import wrap
import time
import webbrowser
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.gui import Gui
from info import Info_box
from float import floatAsByteArray
from generic_fns import pipes, state
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns.reset import reset
from relax_errors import RelaxError
from version import version

# relaxGUI module imports.
from about import About_gui, About_relax
from analyses.auto_model_free import Auto_model_free
from analyses.auto_noe import Auto_noe
from analyses.auto_r1 import Auto_r1
from analyses.auto_r2 import Auto_r2
from analyses.project import create_save_file, open_file
from analyses.results_analysis import color_code_noe, model_free_results, results_table, see_results
from base_classes import Container
from controller import Controller
from derived_wx_classes import StructureTextCtrl
from filedialog import multi_openfile, opendir, openfile, savefile
from message import dir_message, exec_relax, missing_data, question, relax_run_ok
from paths import ABOUT_RELAX_ICON, ABOUT_RELAXGUI_ICON, CONTACT_ICON, CONTROLLER_ICON, EXIT_ICON, IMAGE_PATH, LOAD_ICON, MANUAL_ICON, NEW_ICON, OPEN_ICON, REF_ICON, SAVE_ICON, SAVE_AS_ICON, SETTINGS_ICON, SETTINGS_GLOBAL_ICON, SETTINGS_RESET_ICON
from references import References
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
        kwds["style"] = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN

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

        # Build Notebooks
        self.build_notebooks()

        # Build the menu bar.
        self.build_menu_bar()

        # Build the controller, but don't show it.
        self.controller = Controller(None, -1, "")

        rx_data = ds.relax_gui.analyses[self.noe_index[0]]
        self.frame_1_statusbar = self.CreateStatusBar(3, 0)

        self.__set_properties()
        self.__do_layout()

        # Close Box event
        self.Bind(wx.EVT_CLOSE, self.exit_gui)

        # Pre-build the about dialogs, but do not show them.
        self.dialog_about_gui = About_gui(None, -1, "")
        self.dialog_about_relax = About_relax(None, -1, "")


    def __do_layout(self):
        # Build layout
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


    def about_gui(self, event):
        """The about message for the relax GUI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The dialog.
        self.dialog_about_gui.Show()

        # Terminate the event.
        event.Skip()


    def about_relax(self, event):
        """The about message for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The dialog.
        self.dialog_about_relax.Show()

        # Terminate the event.
        event.Skip()


    def action_state_save(self, event):
        """Save the program state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Not saved yet, therefore pass execution to state_save_as().
        if not self.save_file:
            self.action_state_save_as(event)
            return

        # Save.
        self.state_save()

        # Skip the event.
        event.Skip()


    def action_state_save_as(self, event):
        """Save the program state with file name selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the dialog.
        filename = savefile(msg='Select file to save', filetype='state.bz2', default='relax save files (*.bz2)|*.bz2|all files (*.*)|*.*')

        # Set the file name.
        self.save_file = filename

        # Save.
        self.state_save()

        # Skip the event.
        event.Skip()


    def build_main_window(self):
        """Construct the main relax GUI window."""


        self.notebook_left = wx.Notebook(self, -1, style=wx.NB_LEFT)
        #self.results = wx.Panel(self.notebook_left, -1)

        # The 5th notebook (freq 3).
        self.frq3 = wx.Panel(self.notebook_left, -1)
        self.notebook_frq_3 = wx.Notebook(self.frq3, -1, style=0)

        # The automatic relaxation data analysis frames.
        self.analysis_frames[self.hardcoded_index_r1_3] = Auto_r1(self, self.notebook_frq_3, hardcoded_index=self.r1_index[2])
        self.analysis_frames[self.hardcoded_index_r2_3] = Auto_r2(self, self.notebook_frq_3, hardcoded_index=self.r2_index[2])
        self.analysis_frames[self.hardcoded_index_noe_3] = Auto_noe(self, self.notebook_frq_3, hardcoded_index=self.noe_index[2])

        # The 4th notebook (freq 2).
        self.frq2 = wx.Panel(self.notebook_left, -1)
        self.notebook_frq_2 = wx.Notebook(self.frq2, -1, style=0)

        # The automatic relaxation data analysis frames.
        self.analysis_frames[self.hardcoded_index_r1_2] = Auto_r1(self, self.notebook_frq_2, hardcoded_index=self.r1_index[1])
        self.analysis_frames[self.hardcoded_index_r2_2] = Auto_r2(self, self.notebook_frq_2, hardcoded_index=self.r2_index[1])
        self.analysis_frames[self.hardcoded_index_noe_2] = Auto_noe(self, self.notebook_frq_2, hardcoded_index=self.noe_index[1])

        # The 3rd notebook (freq 1).
        self.frq1 = wx.Panel(self.notebook_left, -1)
        self.notebook_frq_1 = wx.Notebook(self.frq1, -1, style=0)

        # The automatic relaxation data analysis frames.
        self.analysis_frames[self.hardcoded_index_r1_1] = Auto_r1(self, self.notebook_frq_1, hardcoded_index=self.r1_index[0])
        self.analysis_frames[self.hardcoded_index_r2_1] = Auto_r2(self, self.notebook_frq_1, hardcoded_index=self.r2_index[0])
        self.analysis_frames[self.hardcoded_index_noe_1] = Auto_noe(self, self.notebook_frq_1, hardcoded_index=self.noe_index[0])

        # The automatic model-free protocol frame.
        self.analysis_frames[self.hardcoded_index_mf] = Auto_model_free(self, self.notebook_left)


    def build_menu_bar(self):
        """Build the menu bar."""

        # Create the menu bar GUI item and add it to the main frame.
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # The 'File' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(menu, id=0, text="&New\tCtrl+N", icon=NEW_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=1, text="&Open\tCtrl+O", icon=OPEN_ICON))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_sub_item(menu, id=2, text="S&ave\tCtrl+S", icon=SAVE_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=3, text="Save as...\tCtrl+Shift+S", icon=SAVE_AS_ICON))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_sub_item(menu, id=4, text="E&xit\tCtrl+Q", icon=EXIT_ICON))
        menubar.Append(menu, "&File")

        # The 'File' menu actions.
        self.Bind(wx.EVT_MENU, self.newGUI,     id=0)
        self.Bind(wx.EVT_MENU, self.state_load, id=1)
        self.Bind(wx.EVT_MENU, self.action_state_save, id=2)
        self.Bind(wx.EVT_MENU, self.action_state_save_as, id=3)
        self.Bind(wx.EVT_MENU, self.exit_gui,   id=4)

        # The 'View' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(menu, id=50, text="&Controller\tCtrl+Z", icon=CONTROLLER_ICON))
        menubar.Append(menu, "&View")

        # The 'View' actions.
        self.Bind(wx.EVT_MENU, self.show_controller,    id=50)

        # The 'Molecule' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(menu, id=10, text="Load &PDB File", icon=LOAD_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=11, text="Load se&quence file", icon=LOAD_ICON))
        menubar.Append(menu, "&Molecule")

        # The 'Molecule' menu actions.
        #self.Bind(wx.EVT_MENU, self.structure_pdb,  id=10)
        self.Bind(wx.EVT_MENU, self.import_seq,     id=11)

        # The 'Settings' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(menu, id=20, text="&Global relax settings", icon=SETTINGS_GLOBAL_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=21, text="&Parameter file settings", icon=SETTINGS_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=22, text="Reset a&ll settings", icon=SETTINGS_RESET_ICON))
        menubar.Append(menu, "&Settings")

        # The 'Settings' menu actions.
        self.Bind(wx.EVT_MENU, self.settings,           id=20)
        self.Bind(wx.EVT_MENU, self.param_file_setting, id=21)
        self.Bind(wx.EVT_MENU, self.reset_setting,      id=22)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_sub_item(menu, id=40, text="&Manual\tF1", icon=MANUAL_ICON))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_sub_item(menu, id=30, text="&Contact relaxGUI", icon=CONTACT_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=31, text="&References", icon=REF_ICON))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_sub_item(menu, id=41, text="About relaxG&UI", icon=ABOUT_RELAXGUI_ICON))
        menu.AppendItem(self.build_menu_sub_item(menu, id=42, text="About rela&x", icon=ABOUT_RELAX_ICON))
        menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.Bind(wx.EVT_MENU, self.references, id=31)
        self.Bind(wx.EVT_MENU, self.about_gui,  id=41)
        self.Bind(wx.EVT_MENU, self.about_relax, id=42)


    def build_menu_sub_item(self, menu, id=None, text='', tooltip='', icon=None):
        """Construct and return the menu sub-item.

        @param menu:        The menu object to place this entry in.
        @type menu:         wx.Menu instance
        @keyword id:        The element identification number.
        @type id:           int
        @keyword text:      The text for the menu entry.
        @type text:         None or str
        @keyword tooltip:   A tool tip.
        @type tooltip:      str
        @keyword icon:      The bitmap icon path.
        @type icon:         None or str
        @return:            The initialised wx.MenuItem() instance.
        @rtype:             wx.MenuItem() instance
        """

        # Initialise the GUI element.
        element = wx.MenuItem(menu, id, text, tooltip)

        # Set the icon.
        if icon:
            element.SetBitmap(wx.Bitmap(icon))

        # Return the element.
        return element


    def build_notebooks(self):
        """Build the notebooks for the 3 frequencies and analysis modes"""

        # Add NOE, R1 and R2 tabs to main notebook (1. frequency).
        frq1sub = wx.BoxSizer(wx.HORIZONTAL)
        # Create sub-tabs.
        self.notebook_frq_1.AddPage(self.analysis_frames[self.hardcoded_index_noe_1].parent, "steady-state NOE")
        self.notebook_frq_1.AddPage(self.analysis_frames[self.hardcoded_index_r1_1].parent, "R1 relaxation")
        self.notebook_frq_1.AddPage(self.analysis_frames[self.hardcoded_index_r2_1].parent, "R2 relaxation")
        frq1sub.Add(self.notebook_frq_1, 1, wx.EXPAND, 0)
        self.frq1.SetSizer(frq1sub)
        # Pack frequency 1 tab.
        self.notebook_left.AddPage(self.frq1, "Frq. 1")

        # Add NOE, R1 and R2 tabs to main notebook (2. frequency).
        frq2sub = wx.BoxSizer(wx.HORIZONTAL)
        # Create sub-tabs.
        self.notebook_frq_2.AddPage(self.analysis_frames[self.hardcoded_index_noe_2].parent, "steady-state NOE")
        self.notebook_frq_2.AddPage(self.analysis_frames[self.hardcoded_index_r1_2].parent, "R1 relaxation")
        self.notebook_frq_2.AddPage(self.analysis_frames[self.hardcoded_index_r2_2].parent, "R2 relaxation")
        frq2sub.Add(self.notebook_frq_2, 1, wx.EXPAND, 0)
        self.frq2.SetSizer(frq2sub)
        # Pack frequency 2 tab.
        self.notebook_left.AddPage(self.frq2, "Frq. 2")

        # Add NOE, R1 and R2 tabs to main notebook (3. frequency).
        frq3sub = wx.BoxSizer(wx.HORIZONTAL)
        # Create sub-tabs.
        self.notebook_frq_3.AddPage(self.analysis_frames[self.hardcoded_index_noe_3].parent, "steady-state NOE")
        self.notebook_frq_3.AddPage(self.analysis_frames[self.hardcoded_index_r1_3].parent, "R1 relaxation")
        self.notebook_frq_3.AddPage(self.analysis_frames[self.hardcoded_index_r2_3].parent, "R2 relaxation")
        frq3sub.Add(self.notebook_frq_3, 1, wx.EXPAND, 0)
        self.frq3.SetSizer(frq3sub)
        # Pack frequency 3 tab.
        self.notebook_left.AddPage(self.frq3, "Frq. 3")

        # Results tab.
        self.results = wx.Panel(self.notebook_left, -1)

        # Model-free tab.
        self.notebook_left.AddPage(self.analysis_frames[self.hardcoded_index_mf].parent, "Model-free")
        self.notebook_left.AddPage(self.results, "Results")

        # Pack main notebook.
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook_left, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)


    def exit_gui(self, event):
        """Catch the main window closure and perform the exit procedure.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if the user is sure they would like to exit.
        doexit = question('Are you sure you would like to quit relax?  All unsaved data will be lost.', default=True)

        # Exit.
        if doexit:
            # The relax information box.
            info = Info_box()

            # The width of the printout.
            if platform.uname()[0] in ['Windows', 'Microsoft']:
                width = 80
            else:
                width = 100

            # A print out.
            text = "\n\nThank you for citing:\n"
            text = text + "\n\nrelaxGUI\n========\n\nBieri et al., in progress."
            text = text + "\n\n\nrelax\n=====\n\n"
            for line in wrap(info.bib['dAuvergneGooley08a'].cite_short(), width):
                text = text + line + '\n'
            text = text + '\n'
            for line in wrap(info.bib['dAuvergneGooley08b'].cite_short(), width):
                text = text + line + '\n'
            text = text + '\n'
            print(text)

            # Destroy all dialogs.
            self.controller.Destroy()
            self.dialog_about_gui.Destroy()
            self.dialog_about_relax.Destroy()

            # Destroy the main window.
            self.Destroy()

        # Terminate the event.
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

        # Temporary data:  the save file.
        self.save_file = None

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
        tmp_setting = import_file_settings(ds.relax_gui.file_setting)
        if not tmp_setting == None:
            if question('Do you realy want to change import file settings?'):
                ds.relax_gui.file_setting = tmp_setting
        event.Skip()


    def references(self, event):
        """Display the references relevant for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build and show the references window.
        self.references = References(self)
        self.references.Show()

        # Terminate the event.
        event.Skip()


    def reset_setting(self, event): #reset all settings
        global global_setting #import global variable
        if question('Do you realy want to change relax settings?'):
            ds.relax_gui.global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
            ds.relax_gui.file_setting = ['0', '1', '2', '3', '4', '5', '6']


    def settings(self, event): # set up for relax variables
        tmp_global = relax_global_settings(ds.relax_gui.global_setting)
        if not tmp_global == None:
            if question('Do you realy want to change relax settings?'):
                ds.relax_gui.global_setting = tmp_global
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

        # The new save file name.
        self.save_file = filename

        # Load the relax state.
        state.load_state(filename, verbosity=0)

        # FIXME: (commented out until analyses are dynamically loaded and unloaded).
        ## Build the analysis frames
        #for i in range(len(ds.relax_gui.analyses)):
        #    # The automatic model-free protocol frame
        #    if ds.relax_gui.analyses[i].analysis_type == 'model-free':
        #        self.analysis_frames.append(Auto_model_free(self))

        # FIXME:  Temporary fix - set the data structures explicitly.
        # R1 frames.
        self.analysis_frames[self.hardcoded_index_r1_1].link_data(ds.relax_gui.analyses[self.r1_index[0]])
        self.analysis_frames[self.hardcoded_index_r1_2].link_data(ds.relax_gui.analyses[self.r1_index[1]])
        self.analysis_frames[self.hardcoded_index_r1_3].link_data(ds.relax_gui.analyses[self.r1_index[2]])

        # R2 frames.
        self.analysis_frames[self.hardcoded_index_r2_1].link_data(ds.relax_gui.analyses[self.r2_index[0]])
        self.analysis_frames[self.hardcoded_index_r2_2].link_data(ds.relax_gui.analyses[self.r2_index[1]])
        self.analysis_frames[self.hardcoded_index_r2_3].link_data(ds.relax_gui.analyses[self.r2_index[2]])

        # NOE frames
        self.analysis_frames[self.hardcoded_index_noe_1].link_data(ds.relax_gui.analyses[self.noe_index[0]])
        self.analysis_frames[self.hardcoded_index_noe_2].link_data(ds.relax_gui.analyses[self.noe_index[1]])
        self.analysis_frames[self.hardcoded_index_noe_3].link_data(ds.relax_gui.analyses[self.noe_index[2]])

        # Model-free frame.
        self.analysis_frames[self.hardcoded_index_mf].link_data(ds.relax_gui.analyses[9])

        # Update the core of the GUI to match the new data store.
        self.sync_ds(upload=False)

        # Execute the analysis frame specific update methods.
        for analysis in self.analysis_frames:
            if hasattr(analysis, 'sync_ds'):
                analysis.sync_ds(upload=False)

        # Skip the event.
        event.Skip()


    def state_save(self):
        """Save the program state."""

        # Update the data store to match the GUI.
        self.sync_ds(upload=True)

        # Analyses updates of the new data store.
        for i in range(len(self.analysis_frames)):
            # Execute the analysis frame specific update methods.
            if hasattr(self.analysis_frames[i], 'sync_ds'):
                self.analysis_frames[i].sync_ds(upload=True)

        # Save the relax state.
        state.save_state(self.save_file, verbosity=0, force=True)


    def sync_ds(self, upload=False):
        """Synchronise the GUI and the relax data store, both ways.

        This method allows the GUI information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the GUI.

        @keyword upload:    A flag which if True will cause the GUI to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the GUI.
        @type upload:       bool
        """

        # Dummy function (for the time being).
