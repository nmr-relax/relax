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
import __main__
import os
from os import F_OK, access, getcwd, mkdir, sep
import platform
import sys
from textwrap import wrap
import webbrowser
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.gui import Gui
from info import Info_box
from generic_fns import state
from generic_fns.reset import reset
from relax_io import io_streams_restore
from version import version

# relaxGUI module imports.
from about import About_gui, About_relax
from analyses.auto_model_free import Auto_model_free
from analyses.auto_noe import Auto_noe
from analyses.auto_r1 import Auto_r1
from analyses.auto_r2 import Auto_r2
from analyses.results import Results_summary
from analyses.results_analysis import see_results
from base_classes import Container
from components.mol_res_spin_tree import Tree_window
from controller import Controller
from filedialog import opendir, openfile, savefile
from menu import Menu
from message import dir_message, error_message, question
from gui_bieri import paths
from references import References
from relax_prompt import Prompt
from settings import Inputfile, load_sequence, relax_global_settings
from user_functions import User_functions


# Variables.
GUI_version = '1.00'



class Main(wx.Frame):
    """The main GUI class."""

    # Hard coded variables.
    sequence_file_msg = "please insert sequence file"
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

        # The user function GUI elements.
        self.user_functions = User_functions(self)

        # Build the main window.
        self.build_main_window()

        # Build Notebooks
        self.build_notebooks()

        # Build the menu bar.
        self.menu = Menu(self)

        # Build the controller, but don't show it.
        self.controller = Controller(None, -1, "")

        # Build the relax prompt, but don't show it.
        self.relax_prompt = Prompt(None, -1, "", parent=self)

        # Build the tree view window, but don't show it.
        self.mol_res_spin_tree = Tree_window(None, -1, "", parent=self)

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
        _icon.CopyFromBitmap(wx.Bitmap(paths.IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
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


    def about_relax(self, event):
        """The about message for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The dialog.
        self.dialog_about_relax.Show()


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


    def action_state_save_as(self, event):
        """Save the program state with file name selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the dialog.
        filename = savefile(msg='Select file to save', filetype='state.bz2', default='relax save files (*.bz2)|*.bz2|all files (*.*)|*.*')

        # Do nothing - no file was selected.
        if not filename:
            return

        # Set the file name.
        self.save_file = filename

        # Save.
        self.state_save()


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

        # Model-free tab.
        self.notebook_left.AddPage(self.analysis_frames[self.hardcoded_index_mf].parent, "Model-free")

        # Results tab.
        self.results = wx.Panel(self.notebook_left, -1)
        results_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.results_frame = Results_summary(self, self.results)
        results_sizer.Add(results_sizer, 1, wx.EXPAND, 0)
        self.notebook_left.AddPage(self.results, "Results")

        # Pack main notebook.
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook_left, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)


    def contact_relax(self, event):
        """Write an email to the relax mailing-list using the standard mailing program."""
        webbrowser.open_new('mailto:relax-users@gna.org')


    def exit_gui(self, event=None):
        """Catch the main window closure and perform the exit procedure.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if the user is sure they would like to exit.
        doexit = question('Are you sure you would like to quit relax?  All unsaved data will be lost.', default=True)

        # Exit.
        if doexit:
            # Restore the IO streams.
            io_streams_restore(verbosity=0)

            # The relax information box.
            info = Info_box()

            # The width of the printout.
            if platform.uname()[0] in ['Windows', 'Microsoft']:
                width = 80
            else:
                width = 100

            # A print out.
            text = "\n\nThank you for citing:\n"
            text = text + "\n\nrelaxGUI\n========\n\n"
            for line in wrap(info.bib['Bieri10'].cite_short(), width):
                text = text + line + '\n'
            text = text + "\n\n\nrelax\n=====\n\n"
            for line in wrap(info.bib['dAuvergneGooley08a'].cite_short(), width):
                text = text + line + '\n'
            text = text + '\n'
            for line in wrap(info.bib['dAuvergneGooley08b'].cite_short(), width):
                text = text + line + '\n'
            text = text + '\n'
            sys.__stdout__.write(text)

            # End application.
            sys.exit()


    def import_seq(self, event):
        """Open sequence loading GUI element."""

        # The dialog.
        file = load_sequence()

        # Nothing selected.
        if file == None:
            return

        # The selected file.
        sequencefile = str(file)

        # Set entries in pdb text box.
        structure_file_pdb = '!!! Sequence file selected !!!'

        # Add file to NOE tabs.
        self.analysis_frames[self.hardcoded_index_noe_1].field_structure.SetValue(structure_file_pdb)
        self.analysis_frames[self.hardcoded_index_noe_2].field_structure.SetValue(structure_file_pdb)
        self.analysis_frames[self.hardcoded_index_noe_3].field_structure.SetValue(structure_file_pdb)

        # Add file to R1 tabs.
        self.analysis_frames[self.hardcoded_index_r1_1].field_structure.SetValue(structure_file_pdb)
        self.analysis_frames[self.hardcoded_index_r1_2].field_structure.SetValue(structure_file_pdb)
        self.analysis_frames[self.hardcoded_index_r1_3].field_structure.SetValue(structure_file_pdb)

        # Add file to R2 tabs.
        self.analysis_frames[self.hardcoded_index_r2_1].field_structure.SetValue(structure_file_pdb)
        self.analysis_frames[self.hardcoded_index_r2_2].field_structure.SetValue(structure_file_pdb)
        self.analysis_frames[self.hardcoded_index_r2_3].field_structure.SetValue(structure_file_pdb)

        # Load sequence file into the relax data store.
        for i in range(10):
            ds.relax_gui.analyses[i].sequence_file = sequencefile

        # Update the core of the GUI to match the new data store.
        self.sync_ds(upload=False)


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
        ds.relax_gui.file_setting = [1, 2, 3, 4, 5, 6, 7]

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


    def open_model_results_exe(self, event):    # open model-free results
        choice = self.list_modelfree.GetStringSelection()
        model_result = [ds.relax_gui.table_residue, ds.relax_gui.table_model, ds.relax_gui.table_s2, ds.relax_gui.table_rex, ds.relax_gui.table_te] # relax results values
        see_results(choice, model_result)


    def open_noe_results_exe(self, event): #open results of noe run
        choice = self.list_noe.GetStringSelection()
        see_results(choice, None)


    def open_rx_results_exe(self, event): # open results of r1 and r2 runs
        choice = self.list_rx.GetStringSelection()
        see_results(choice, None)


    def param_file_setting(self, event): # set up parameter files
        set_relax_params = Inputfile(self, -1, "")
        set_relax_params.Show()


    def references(self, event):
        """Display the references relevant for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build and show the references window.
        self.references = References(self)
        self.references.Show()


    def relax_manual(self, event):
        """Display the relax manual.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The PDF manual.
        file = __main__.install_path + sep+"docs"+sep+"relax.pdf"

        # Test if it exists.
        if not access(file, F_OK):
            error_message("The relax manual '%s' cannot be found.  Please compile using the scons program." % file)

        # Open the relax PDF manual using the native PDF reader.
        else:
            # Windows.
            if platform.uname()[0] in ['Windows', 'Microsoft']:
                os.startfile(file)

            # Mac OS X.
            elif platform.uname()[0] == 'Darwin':
                os.system('open %s' % file)

            # POSIX Systems with xdg-open.
            else:
                os.system('/usr/bin/xdg-open %s' % file)


    def reset_setting(self, event): #reset all settings
        global global_setting #import global variable
        if question('Do you realy want to change relax settings?'):
            ds.relax_gui.global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
            ds.relax_gui.file_setting = [1, 2, 3, 4, 5, 6, 7]


    def settings(self, event): # set up for relax variables
        tmp_global = relax_global_settings(ds.relax_gui.global_setting)
        if not tmp_global == None:
            if question('Do you realy want to change relax settings?'):
                ds.relax_gui.global_setting = tmp_global


    def show_controller(self, event):
        """Display the relax controller window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the window.
        self.controller.Show()


    def show_prompt(self, event):
        """Display the relax prompt window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the window.
        self.relax_prompt.Show()


    def show_tree(self, event):
        """Display the molecule, residue, and spin tree window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the window.
        self.mol_res_spin_tree.Show()


    def state_load(self, event):
        """Load the program state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the dialog.
        filename = openfile(msg='Select file to open', filetype='state.bz2', default='relax save files (*.bz2)|*.bz2|all files (*.*)|*.*')

        # No file has been selected.
        if not filename:
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


    def structure_pdb(self, event): # open load sequence panel
        temp = openfile('Select PDB file to open', '', '', 'PDB files (*.pdb)|*.pdb|all files (*.*)|*.*')
        if not temp == None:
            structure_file_pdb = str(temp) #set sequence file

            # Add file to NOE tabs.
            self.analysis_frames[self.hardcoded_index_noe_1].field_structure.SetValue(structure_file_pdb)
            self.analysis_frames[self.hardcoded_index_noe_2].field_structure.SetValue(structure_file_pdb)
            self.analysis_frames[self.hardcoded_index_noe_3].field_structure.SetValue(structure_file_pdb)

            # Add file to R1 tabs.
            self.analysis_frames[self.hardcoded_index_r1_1].field_structure.SetValue(structure_file_pdb)
            self.analysis_frames[self.hardcoded_index_r1_2].field_structure.SetValue(structure_file_pdb)
            self.analysis_frames[self.hardcoded_index_r1_3].field_structure.SetValue(structure_file_pdb)

            # Add file to R2 tabs.
            self.analysis_frames[self.hardcoded_index_r2_1].field_structure.SetValue(structure_file_pdb)
            self.analysis_frames[self.hardcoded_index_r2_2].field_structure.SetValue(structure_file_pdb)
            self.analysis_frames[self.hardcoded_index_r2_3].field_structure.SetValue(structure_file_pdb)


    def sync_ds(self, upload=False):
        """Synchronise the GUI and the relax data store, both ways.

        This method allows the GUI information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the GUI.

        @keyword upload:    A flag which if True will cause the GUI to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the GUI.
        @type upload:       bool
        """

        # Synchronise each frame.
        for frame in self.analysis_frames:
            frame.sync_ds(upload)
