###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
"""Main module for the relax graphical user interface."""

# Python module imports.
import os
from os import F_OK, access, getcwd, mkdir, sep
import platform
import sys
from textwrap import wrap
import webbrowser
import wx
from wx.lib import buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.gui import Gui
from info import Info_box
from generic_fns import state
from generic_fns.reset import reset
from relax_errors import RelaxError
from relax_io import io_streams_restore
from status import Status; status = Status()
from version import version

# relaxGUI module imports.
from gui.about import About_gui, About_relax
from gui.analyses.auto_model_free import Auto_model_free
from gui.analyses.auto_noe import Auto_noe
from gui.analyses.auto_r1 import Auto_r1
from gui.analyses.auto_r2 import Auto_r2
from gui.analyses.results import Results_summary
from gui.analyses.results_analysis import see_results
from gui.analyses.wizard import Analysis_wizard
from gui.base_classes import Container
from gui.components.spin_view import Spin_view_window
from gui.controller import Controller
from gui.filedialog import opendir, openfile, savefile
from gui.menu import Menu
from gui.message import dir_message, error_message, question
from gui import paths
from gui.references import References
from gui.relax_prompt import Prompt
from gui.settings import Free_file_format, Global_params, load_sequence
from gui.user_functions import User_functions


# Variables.
GUI_version = '1.00'



class Main(wx.Frame):
    """The main GUI class."""

    # Hard coded variables.
    min_width = 1000
    min_height = 600
    sequence_file_msg = "please insert sequence file"
    structure_file_pdb_msg = "please insert .pdb file"

    def __init__(self, parent=None, id=-1, title="", script=None):
        """Initialise the main relax GUI frame."""

        # Execute the base class __init__ method.
        super(Main, self).__init__(parent=parent, id=id, title=title, style=wx.DEFAULT_FRAME_STYLE)

        # Initialise some variables for the GUI.
        self.init_state = True
        self.launch_dir = getcwd()

        # Set up the frame.
        self.Layout()
        self.SetSize((self.min_width, self.min_height))
        self.SetMinSize((self.min_width, self.min_height))
        self.Centre()

        # The analysis window object storage.
        self.analyses = []

        # The calculation threads list.
        self.calc_threads = []

        # Initialise the GUI data.
        self.init_data()

        # Set up some standard interface-wide fonts.
        self.setup_fonts()

        # The user function GUI elements.
        self.user_functions = User_functions(self)

        # Build the menu bar.
        self.menu = Menu(self)

        # Build the controller, but don't show it.
        self.controller = Controller(None, -1, "")

        # Set the title.
        self.SetTitle("relaxGUI " + GUI_version)

        # Set up the program icon (disabled on Macs).
        if not 'darwin' in sys.platform:
            icon = wx.EmptyIcon()
            icon.CopyFromBitmap(wx.Bitmap(paths.IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
            self.SetIcon(icon)

        # Statusbar fields.
        self.frame_1_statusbar = self.CreateStatusBar(3, 0)
        self.frame_1_statusbar.SetStatusWidths([800, 50, -1])
        frame_1_statusbar_fields = ["relaxGUI (C) 2009 Michael Bieri and (C) 2010-2011 the relax development team", "relax:", version]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)

        # Add the start screen.
        self.add_start_screen()

        # Close Box event
        self.Bind(wx.EVT_CLOSE, self.exit_gui)

        # Run a script.
        if script:
            self.user_functions.script.script_exec(script)


    def about_gui(self, event):
        """The about message for the relax GUI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the dialog.
        dialog = About_gui(None, -1, "")

        # The dialog.
        dialog.Show()


    def about_relax(self, event):
        """The about message for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the dialog.
        dialog = About_relax(None, -1, "")

        # The dialog.
        dialog.Show()


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


    def add_start_screen(self):
        """Create a start screen for the main window when no analyses exist."""

        # The sizer for the main GUI window.
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # The relax icon.
        image = wx.StaticBitmap(self, -1, wx.Bitmap(paths.IMAGE_PATH+'ulysses_shadowless_400x168.png', wx.BITMAP_TYPE_ANY))

        # Add the icon to the main spacer with spacing.
        sizer.AddStretchSpacer()
        sizer.Add(image, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer.AddStretchSpacer()

        # Re-perform the layout of the GUI elements, and refresh.
        self.Layout()
        self.Refresh()


    def close_analysis(self, event):
        """Close the currently opened analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the current analysis index.
        index = self.notebook.GetSelection()

        # Ask if this should be done.
        msg = "Are you sure you would like to close the current %s analysis tab?" % ds.relax_gui.analyses[index].analysis_type
        if not question(msg, default=False):
            return

        # Delete.
        self.delete_analysis(index)


    def contact_relax(self, event):
        """Write an email to the relax mailing-list using the standard mailing program."""
        webbrowser.open_new('mailto:relax-users@gna.org')


    def delete_analysis(self, index):
        """Delete the analysis tab and data store corresponding to the index.

        @param index:   The index of the analysis to delete.
        @type index:    int
        """

        # Delete the data store object.
        ds.relax_gui.analyses.pop(index)

        # Delete the tab.
        self.notebook.DeletePage(index)

        # Delete the tab object.
        self.analyses.pop(index)

        # No more analyses, so in the initial state.
        if len(ds.relax_gui.analyses) == 0:
            # Reset the flag.
            self.init_state = True

            # Delete the previous sizer.
            old_sizer = self.GetSizer()
            old_sizer.DeleteWindows()

            # Recreate the start screen.
            self.add_start_screen()


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
            for line in wrap(info.bib['Bieri11'].cite_short(), width):
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

        # Table of relax Results
        ds.relax_gui.table_residue = []
        ds.relax_gui.table_model = []
        ds.relax_gui.table_s2 = []
        ds.relax_gui.table_rex = []
        ds.relax_gui.table_te = []


    def new(self, event):
        """Launch a wizard to select the new analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the analysis wizard, and obtain the user specified data.
        self.new_wizard = Analysis_wizard()
        data = self.new_wizard.run()

        # Failure, so do nothing.
        if data == None:
            return

        # Unpack the data.
        analysis_type, analysis_name, pipe_name = data

        # Initialise the new analysis.
        self.new_analysis(analysis_type, analysis_name, pipe_name)

        # Delete the wizard data.
        del self.new_wizard


    def new_analysis(self, analysis_type=None, analysis_name=None, pipe_name=None, index=None):
        """Initialise a new analysis.

        @keyword analysis_type: The type of analysis to initialise.  This can be one of 'noe', 'r1', 'r2', or 'mf'.
        @type analysis_type:    str
        @keyword analysis_name: The name of the analysis to initialise.
        @type analysis_name:    str
        @keyword index:         The index of the analysis in the relax data store (set to None if no data currently exists).
        @type index:            None or int
        """

        # Starting from the initial state.
        if self.init_state:
            # A new sizer for the notebook (to replace the current sizer).
            sizer = wx.BoxSizer(wx.VERTICAL)

            # Create a notebook and add it to the sizer.
            self.notebook = wx.Notebook(self, -1, style=wx.NB_TOP)
            sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)

            # Delete the previous sizer.
            old_sizer = self.GetSizer()
            old_sizer.DeleteWindows()

            # Add the new sizer to the main window.
            self.SetSizer(sizer)
            sizer.Layout()

            # Set the flag.
            self.init_state = False

        # The analysis classes.
        classes = {'noe': Auto_noe,
                   'r1':  Auto_r1,
                   'r2':  Auto_r2,
                   'mf':  Auto_model_free}

        # Bad analysis type.
        if analysis_type not in classes.keys():
            raise RelaxError("The analysis '%s' is unknown." % analysis_type)

        # Get the class.
        analysis = classes[analysis_type]

        # Initialise the class and append it to the analysis window object.
        self.analyses.append(analysis(gui=self, notebook=self.notebook, analysis_name=analysis_name, pipe_name=pipe_name, data_index=index))

        # Add to the notebook.
        self.notebook.AddPage(self.analyses[-1].parent, analysis_name)

        # Reset the main window layout.
        self.Layout()


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


    def free_file_format_settings(self, event):
        """Open the free file format settings window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the window.
        win = Free_file_format()

        # Show the window.
        win.Show()


    def global_parameters(self, event):
        """Open the global parameters window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the window.
        win = Global_params()

        # Show the window.
        win.Show()


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
        file = status.install_path + sep+"docs"+sep+"relax.pdf"

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
        if question('Do you realy want to change relax settings?'):
            ds.relax_gui.global_setting = ['1.02 * 1e-10', '-172 * 1e-6', 'N', 'H', '11', 'newton', '500']
            ds.relax_gui.free_file_format.reset()


    def setup_fonts(self):
        """Initialise a series of fonts to be used throughout the GUI."""

        # The fonts.
        self.font_smaller =     wx.Font(6,  wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.font_small =       wx.Font(8,  wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.font_button =      wx.Font(8,  wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.font_normal =      wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.font_normal_bold = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD,   0, "Sans")
        self.font_subtitle =    wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD,   0, "Sans")
        self.font_14 =          wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.font_title =       wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")


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

        # Build the relax prompt if needed.
        if not hasattr(self, 'relax_prompt'):
            self.relax_prompt = Prompt(None, -1, "", parent=self)

        # Open the window.
        self.relax_prompt.Show()


    def show_tree(self, event):
        """Display the molecule, residue, and spin tree window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the spin view window.
        if not hasattr(self, 'spin_view'):
            self.spin_view = Spin_view_window(None, -1, "", parent=self)

        # Open the window.
        self.spin_view.Show()


    def state_load(self, event):
        """Load the program state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Warning.
        if not self.init_state:
            # The message.
            msg = "Loading a saved relax state file will cause all unsaved data to be lost.  Are you sure you would to open a save file?"

            # The dialog.
            if not question(msg, default=True):
                return

        # Open the dialog.
        filename = openfile(msg='Select file to open', filetype='state.bz2', default='relax save files (*.bz2)|*.bz2|all files (*.*)|*.*')

        # No file has been selected.
        if not filename:
            # Don't do anything.
            return

        # Yield to allow the cursor to be changed.
        wx.Yield()

        # Change the cursor to waiting.
        orig_cursor = self.GetCursor()
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))

        # Delete the current tabs.
        while len(self.analyses):
            # Remove the last analysis, until there is nothing left.
            self.delete_analysis(len(self.analyses)-1)

        # Reset the relax data store.
        reset()

        # The new save file name.
        self.save_file = filename

        # Load the relax state.
        state.load_state(filename, verbosity=0)

        # Reconstruct the analysis tabs.
        map = {'NOE': 'noe',
               'R1': 'r1',
               'R2': 'r2',
               'model-free': 'mf'}
        for i in range(len(ds.relax_gui.analyses)):
            # The analysis name.
            if hasattr(ds.relax_gui.analyses[i], 'analysis_name'):
                analysis_name = ds.relax_gui.analyses[i].analysis_name
            elif ds.relax_gui.analyses[i].analysis_type == 'NOE':
                analysis_name = 'Steady-state NOE'
            elif ds.relax_gui.analyses[i].analysis_type == 'R1':
                analysis_name = 'R1 relaxation'
            elif ds.relax_gui.analyses[i].analysis_type == 'R2':
                analysis_name = 'R2 relaxation'
            elif ds.relax_gui.analyses[i].analysis_type == 'model-free':
                analysis_name = 'Model-free'

            # Set up the analysis.
            self.new_analysis(map[ds.relax_gui.analyses[i].analysis_type], analysis_name, index=i)

        # Update the core of the GUI to match the new data store.
        self.sync_ds(upload=False)

        # Reset the cursor.
        self.SetCursor(orig_cursor)


    def state_save(self):
        """Save the program state."""

        # Update the data store to match the GUI.
        self.sync_ds(upload=True)

        # Save the relax state.
        state.save_state(self.save_file, verbosity=0, force=True)


    def sync_ds(self, upload=False):
        """Synchronise the GUI and the relax data store, both ways.

        This method allows the GUI information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the GUI.

        @keyword upload:    A flag which if True will cause the GUI to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the GUI.
        @type upload:       bool
        """

        # Loop over each analysis.
        for i in range(len(self.analyses)):
            # Execute the analysis frame specific update methods.
            if hasattr(self.analyses[i], 'sync_ds'):
                self.analyses[i].sync_ds(upload)


