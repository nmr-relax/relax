###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
from re import search
from string import split
import sys
from textwrap import wrap
from thread import start_new_thread
from time import sleep
import webbrowser
import wx
from wx.lib import buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.gui import Gui
from info import Info_box
from generic_fns import state
from generic_fns.pipes import cdp_name
from generic_fns.reset import reset
from relax_errors import RelaxError
from relax_io import io_streams_restore
from status import Status; status = Status()
from version import version

# relaxGUI module imports.
from gui.about import About_gui, About_relax
from gui.analyses import Analysis_controller
from gui.base_classes import Container
from gui.spin_viewer.frame import Spin_view_window
from gui.controller import Controller
from gui.filedialog import RelaxFileDialog
from gui.fonts import font
from gui.icons import Relax_task_bar_icon, relax_icons
from gui.interpreter import Interpreter
from gui.menu import Menu
from gui.message import error_message, Question
from gui.misc import gui_to_str, open_file, protected_exec
from gui import paths
from gui.pipe_editor import Pipe_editor
from gui.references import References
from gui.relax_prompt import Prompt
from gui.results_viewer import Results_viewer
from gui.settings import Free_file_format, load_sequence
from gui.user_functions import User_functions; user_functions = User_functions()
import test_suite


class Main(wx.Frame):
    """The main GUI class."""

    # Hard coded variables.
    min_width = 1000
    min_height = 600

    def __init__(self, parent=None, id=-1, title="", script=None):
        """Initialise the main relax GUI frame."""

        # Store the wxPython info for os/machine/version specific hacks.
        status.wx_info = {}
        status.wx_info["version"] = split(wx.__version__, '.')
        status.wx_info["minor"] = "%s.%s" % (status.wx_info["version"][0], status.wx_info["version"][1])
        status.wx_info["os"] = sys.platform
        status.wx_info["build"] = None
        if search('gtk2', wx.version()):
            status.wx_info["build"] = 'gtk'
        elif search('cocoa', wx.version()):
            status.wx_info["build"] = 'cocoa'
        elif search('mac-unicode', wx.version()):
            status.wx_info["build"] = 'carbon'
        status.wx_info["full"] = None
        if status.wx_info["build"]:
            status.wx_info["full"] = "%s-%s" % (status.wx_info["os"], status.wx_info["build"])


        # The main window style.
        style = wx.DEFAULT_FRAME_STYLE
        if not status.debug and status.wx_info["os"] != 'darwin':
            style = style | wx.MAXIMIZE

        # Execute the base class __init__ method.
        super(Main, self).__init__(parent=parent, id=id, title=title, style=style)

        # Force the main window to start maximised (needed for MS Windows).
        if not status.debug and status.wx_info["os"] != 'darwin':
            self.Maximize()

        # Set up some standard interface-wide fonts.
        font.setup()

        # Set up the relax icons.
        relax_icons.setup()
        self.SetIcons(relax_icons)

        # Set up the Mac OS X task bar icon.
        if status.wx_info["os"] == 'darwin' and status.wx_info["build"] != 'gtk':
            self.taskbar_icon = Relax_task_bar_icon(self)

        # Initialise some variables for the GUI.
        self.launch_dir = getcwd()

        # Set up the frame.
        self.Layout()
        self.SetSize((self.min_width, self.min_height))
        self.SetMinSize((self.min_width, self.min_height))
        self.Centre()

        # The analysis window object storage.
        self.analysis = Analysis_controller(self)

        # The calculation threads list.
        self.calc_threads = []

        # Initialise the GUI data.
        self.init_data()

        # Build the menu bar.
        self.menu = Menu(self)

        # Build the toolbar.
        self.toolbar()

        # Build the controller, but don't show it.
        self.controller = Controller(self)

        # Set the title.
        self.SetTitle("relax " + version)

        # Set up the status bar.
        self.status_bar = self.CreateStatusBar(3, 0)
        self.status_bar.SetStatusWidths([-4, -1, -2])
        self.update_status_bar()

        # Add the start screen.
        self.add_start_screen()

        # Close Box event.
        self.Bind(wx.EVT_CLOSE, self.exit_gui)

        # Initialise the special interpreter thread object.
        self.interpreter = Interpreter()

        # Register functions with the observer objects.
        status.observers.pipe_alteration.register('status bar', self.update_status_bar)
        status.observers.result_file.register('gui', self.show_results_viewer_no_warn)
        status.observers.exec_lock.register('gui', self.enable)

        # Run a script.
        if script:
            wx.CallAfter(user_functions.script.script_exec, script)


    def about_gui(self, event):
        """The about message for the relax GUI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the dialog.
        dialog = About_gui(None, -1, "")

        # The dialog.
        if status.show_gui:
            dialog.Show()


    def about_relax(self, event):
        """The about message for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the dialog.
        dialog = About_relax(None, -1)

        # The dialog.
        if status.show_gui:
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

        # The dialog.
        dialog = RelaxFileDialog(parent=self, message='Select the relax save state file', defaultFile='state.bz2', wildcard='relax save file (*.bz2)|*.bz2', style=wx.FD_SAVE)

        # Show the dialog and catch if no file has been selected.
        if status.show_gui and dialog.ShowModal() != wx.ID_OK:
            # Don't do anything.
            return

        # The file.
        file_name = dialog.get_file()

        # Set the file name.
        self.save_file = file_name

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


    def close_windows(self):
        """Throw a warning to close all of the non-essential windows when execution is locked.

        This is to speed up the calculations by avoiding window updates.
        """

        # Init the window list.
        win_list = []

        # Is the spin viewer window open?
        if hasattr(self, 'spin_viewer') and self.spin_viewer.IsShown():
            win_list.append('The spin viewer window')

        # Is the pipe editor window open?
        if hasattr(self, 'pipe_editor') and self.pipe_editor.IsShown():
            win_list.append('The data pipe editor window')

        # Is the results viewer window open?
        if hasattr(self, 'results_viewer') and self.results_viewer.IsShown():
            win_list.append('The results viewer window')

        # The windows are not open, so quit.
        if not len(win_list):
            return

        # The text.
        text = "The following windows are currently open:\n\n"
        for win in win_list:
            text = "%s\t%s.\n" % (text, win)
        text = text + "\nClosing these will significantly speed up the calculations."

        # Display the error message dialog.
        dlg = wx.MessageDialog(self, text, caption="Close windows", style=wx.OK|wx.ICON_EXCLAMATION|wx.STAY_ON_TOP)
        if status.show_gui:
            dlg.ShowModal()

        # Otherwise output to stderr.
        else:
            sys.stderr.write(text)


    def contact_relax(self, event):
        """Write an email to the relax mailing-list using the standard mailing program."""
        webbrowser.open_new('mailto:relax-users@gna.org')


    def enable(self):
        """Enable and disable certain parts of the main window with the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # The toolbar.
        wx.CallAfter(self.toolbar.EnableTool, self.TB_FILE_NEW, enable)
        wx.CallAfter(self.toolbar.EnableTool, self.TB_FILE_CLOSE, enable)
        wx.CallAfter(self.toolbar.EnableTool, self.TB_FILE_CLOSE_ALL, enable)
        wx.CallAfter(self.toolbar.EnableTool, self.TB_FILE_OPEN, enable)
        wx.CallAfter(self.toolbar.EnableTool, self.TB_FILE_SAVE, enable)
        wx.CallAfter(self.toolbar.EnableTool, self.TB_FILE_SAVE_AS, enable)


    def exit_gui(self, event=None):
        """Catch the main window closure and perform the exit procedure.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if the user is sure they would like to exit.
        doexit = wx.ID_YES
        if status.show_gui:
            doexit = Question('Are you sure you would like to quit relax?  All unsaved data will be lost.', title='Exit relax', default=True).ShowModal()

        # Exit.
        if doexit == wx.ID_YES:
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
            sys.stdout.write(text)

            # Remove the Mac OS X task bar icon.
            if hasattr(self, 'taskbar_icon'):
                self.taskbar_icon.Destroy()

            # End application.
            wx.Exit()


    def init_data(self):
        """Initialise the data used by the GUI interface."""

        # Temporary data:  the save file.
        self.save_file = None

        # Add the GUI object to the data store.
        ds.relax_gui = Gui()


    def free_file_format_settings(self, event):
        """Open the free file format settings window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the window.
        win = Free_file_format()

        # Show the window.
        if status.show_gui:
            win.Show()


    def references(self, event):
        """Display the references relevant for relax.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build and show the references window.
        self.references = References(self)
        if status.show_gui:
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
            return

        # Open the relax PDF manual using the native PDF reader.
        open_file(file)


    def run_test_suite(self, event):
        """Execute the full test suite.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "In running the test suite, relax will be reset and all data lost.  Are you sure you would like to run the test suite?"
        if Question(msg, parent=self, default=False).ShowModal() == wx.ID_NO:
            return

        # Change the cursor to waiting.
        wx.BeginBusyCursor()

        # Reset relax.
        reset()

        # Show the relax controller.
        self.show_controller(event)

        # Yield
        wx.GetApp().Yield(True)

        # Prevent all new GUI elements from being shown.
        status.show_gui = False

        # Run the tests.
        runner = test_suite.test_suite_runner.Test_suite_runner([], from_gui=True)
        runner.run_all_tests()

        # Reactive the GUI.
        status.show_gui = True

        # Turn off the busy cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()


    def show_controller(self, event):
        """Display the relax controller window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Bring the window to the front.
        if self.controller.IsShown():
            self.controller.Raise()
            return

        # Open the window.
        if status.show_gui:
            self.controller.Show()


    def show_pipe_editor(self, event):
        """Display the data pipe editor window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Throw a warning if the execution lock is on.
        if status.exec_lock.locked():
            dlg = wx.MessageDialog(self, "Leaving the pipe editor window open will slow down the calculations.", caption="Warning", style=wx.OK|wx.ICON_EXCLAMATION|wx.STAY_ON_TOP)
            if status.show_gui:
                dlg.ShowModal()

        # Build the pipe editor if needed.
        if not hasattr(self, 'pipe_editor'):
            self.pipe_editor = Pipe_editor(gui=self)

        # Bring the window to the front.
        if self.pipe_editor.IsShown():
            self.pipe_editor.Raise()
            return

        # Open the window.
        if status.show_gui and not self.pipe_editor.IsShown():
            self.pipe_editor.Show()


    def show_prompt(self, event):
        """Display the relax prompt window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the relax prompt if needed.
        if not hasattr(self, 'relax_prompt'):
            self.relax_prompt = Prompt(None, -1, "", parent=self)

        # Bring the window to the front.
        if self.relax_prompt.IsShown():
            self.relax_prompt.Raise()
            return

        # Open the window.
        if status.show_gui:
            self.relax_prompt.Show()


    def show_results_viewer(self, event=None):
        """Display the analysis results.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show the results viewer in a thread safe way.
        wx.CallAfter(self.show_results_viewer_safe, warn=True)


    def show_results_viewer_safe(self, warn=False):
        """Display the analysis results in a thread safe wx.CallAfter call.

        @keyword warn:  A flag which if True will cause a message dialog to appear warning about keeping the window open with the execution lock.
        @type warn:     bool
        """

        # Throw a warning if the execution lock is on.
        if warn and status.exec_lock.locked():
            dlg = wx.MessageDialog(self, "Leaving the results viewer window open will slow down the calculations.", caption="Warning", style=wx.OK|wx.ICON_EXCLAMATION|wx.STAY_ON_TOP)
            if status.show_gui:
                wx.CallAfter(dlg.ShowModal)

        # Create the results viewer window if needed.
        if not hasattr(self, 'results_viewer'):
            self.results_viewer = Results_viewer(self)

        # Bring the window to the front.
        if self.results_viewer.IsShown():
            self.results_viewer.Raise()
            return

        # Open the window.
        if status.show_gui and not self.results_viewer.IsShown():
            self.results_viewer.Show()


    def show_results_viewer_no_warn(self):
        """Display the analysis results."""

        # Show the results viewer in a thread safe way with no warning dialog.
        wx.CallAfter(self.show_results_viewer_safe, warn=False)


    def show_tree(self, event):
        """Display the molecule, residue, and spin tree window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Throw a warning if the execution lock is on.
        if status.exec_lock.locked():
            dlg = wx.MessageDialog(self, "Leaving the spin viewer window open will slow down the calculations.", caption="Warning", style=wx.OK|wx.ICON_EXCLAMATION|wx.STAY_ON_TOP)
            if status.show_gui:
                dlg.ShowModal()

        # Build the spin view window.
        if not hasattr(self, 'spin_viewer'):
            self.spin_viewer = Spin_view_window(None, -1, "", parent=self)

        # Bring the window to the front.
        if self.spin_viewer.IsShown():
            self.spin_viewer.Raise()
            return

        # Open the window (the GUI flag check is inside the Show method).
        if status.show_gui and not self.spin_viewer.IsShown():
            self.spin_viewer.Show()


    def state_load(self, event=None, file_name=None):
        """Load the program state.

        @param event:       The wx event.
        @type event:        wx event
        @keyword file_name: The name of the file to load (for dialogless operation).
        @type file_name:    str
        """

        # Execution lock.
        if status.exec_lock.locked():
            return

        # Warning.
        if not self.analysis.init_state:
            # The message.
            msg = "Loading a saved relax state file will cause all unsaved data to be lost.  Are you sure you would to open a save file?"

            # The dialog.
            if status.show_gui and Question(msg, default=True, size=(400, 150)).ShowModal() == wx.ID_NO:
                return

        # Open the dialog.
        if not file_name:
            dialog = RelaxFileDialog(parent=self, message='Select the relax save state file', defaultFile='state.bz2', wildcard='relax save files (*.bz2;*.gz)|*.bz2;*.gz|All files (*)|*', style=wx.FD_OPEN)

            # Show the dialog and catch if no file has been selected.
            if status.show_gui and dialog.ShowModal() != wx.ID_OK:
                # Don't do anything.
                return

            # The file.
            file_name = gui_to_str(dialog.get_file())

        # Yield to allow the cursor to be changed.
        wx.Yield()

        # Change the cursor to waiting, and freeze the GUI.
        wx.BeginBusyCursor()
        self.Freeze()

        # Make sure the GUI returns to normal if a failure occurs.
        try:
            # Delete the current tabs.
            self.analysis.delete_all()

            # Reset the relax data store.
            reset()

            # The new save file name.
            self.save_file = file_name

            # Load the relax state.
            if protected_exec(state.load_state, file_name, verbosity=0):
                # Reconstruct the analyses.
                self.analysis.load_from_store()

                # Update the core of the GUI to match the new data store.
                self.sync_ds(upload=False)

            # File loading failure.
            else:
                # Reinitialise the GUI data store structure.
                self.init_data()

        # Reset the cursor, and thaw the GUI.
        finally:
            self.Thaw()

            # Turn off the busy cursor.
            if wx.IsBusy():
                wx.EndBusyCursor()


    def state_save(self):
        """Save the program state."""

        # Update the data store to match the GUI.
        self.sync_ds(upload=True)

        # Save the relax state (with save user feedback).
        try:
            wx.BeginBusyCursor()
            state.save_state(self.save_file, verbosity=0, force=True)

            # Sleep a little so the user sees the busy cursor and knows that a save has occurred!
            sleep(1)

        # Turn off the user feedback.
        finally:
            if wx.IsBusy():
                wx.EndBusyCursor()


    def sync_ds(self, upload=False):
        """Synchronise the GUI and the relax data store, both ways.

        This method allows the GUI information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the GUI.

        @keyword upload:    A flag which if True will cause the GUI to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the GUI.
        @type upload:       bool
        """

        # Loop over each analysis.
        for page in self.analysis.analysis_loop():
            # Execute the analysis page specific update methods.
            if hasattr(page, 'sync_ds'):
                page.sync_ds(upload)


    def toolbar(self):
        """Create the toolbar."""

        # Init.
        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.TB_FLAT)

        # The new analysis button.
        self.TB_FILE_NEW = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_FILE_NEW, "New analysis", wx.Bitmap(paths.icon_22x22.new, wx.BITMAP_TYPE_ANY), shortHelp="New analysis")
        self.Bind(wx.EVT_TOOL, self.analysis.menu_new, id=self.TB_FILE_NEW)

        # The close analysis button.
        self.TB_FILE_CLOSE = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_FILE_CLOSE, "Close analysis", wx.Bitmap(paths.icon_22x22.document_close, wx.BITMAP_TYPE_ANY), shortHelp="Close analysis")
        self.Bind(wx.EVT_TOOL, self.analysis.menu_close, id=self.TB_FILE_CLOSE)

        # The close all analyses button.
        self.TB_FILE_CLOSE_ALL = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_FILE_CLOSE_ALL, "Close all analyses", wx.Bitmap(paths.icon_22x22.dialog_close, wx.BITMAP_TYPE_ANY), shortHelp="Close all analyses")
        self.Bind(wx.EVT_TOOL, self.analysis.menu_close_all, id=self.TB_FILE_CLOSE_ALL)

        # A separator.
        self.toolbar.AddSeparator()

        # The open state button.
        self.TB_FILE_OPEN = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_FILE_OPEN, "Open relax state", wx.Bitmap(paths.icon_22x22.document_open, wx.BITMAP_TYPE_ANY), shortHelp="Open relax state")
        self.Bind(wx.EVT_TOOL, self.state_load, id=self.TB_FILE_OPEN)

        # The save state button.
        self.TB_FILE_SAVE = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_FILE_SAVE, "Save relax state", wx.Bitmap(paths.icon_22x22.document_save, wx.BITMAP_TYPE_ANY), shortHelp="Save relax state")
        self.Bind(wx.EVT_TOOL, self.action_state_save, id=self.TB_FILE_SAVE)

        # The save as button.
        self.TB_FILE_SAVE_AS = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_FILE_SAVE_AS, "Save as", wx.Bitmap(paths.icon_22x22.document_save_as, wx.BITMAP_TYPE_ANY), shortHelp="Save as")
        self.Bind(wx.EVT_TOOL, self.action_state_save_as, id=self.TB_FILE_SAVE_AS)

        # A separator.
        self.toolbar.AddSeparator()

        # The relax controller button.
        self.TB_VIEW_CONTROLLER = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_VIEW_CONTROLLER, "Controller", wx.Bitmap(paths.icon_22x22.preferences_system_performance, wx.BITMAP_TYPE_ANY), shortHelp="relax controller")
        self.Bind(wx.EVT_TOOL, self.show_controller, id=self.TB_VIEW_CONTROLLER)

        # The spin viewer button.
        self.TB_VIEW_SPIN_VIEW = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_VIEW_SPIN_VIEW, "Spin viewer", wx.Bitmap(paths.icon_22x22.spin, wx.BITMAP_TYPE_ANY), shortHelp="Spin viewer window")
        self.Bind(wx.EVT_TOOL, self.show_tree, id=self.TB_VIEW_SPIN_VIEW)

        # The results viewer button.
        self.TB_VIEW_RESULTS = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_VIEW_RESULTS, "Results viewer", wx.Bitmap(paths.icon_22x22.view_statistics, wx.BITMAP_TYPE_ANY), shortHelp="Results viewer window")
        self.Bind(wx.EVT_TOOL, self.show_results_viewer, id=self.TB_VIEW_RESULTS)

        # The data pipe editor button.
        self.TB_VIEW_PIPE_EDIT = wx.NewId()
        self.toolbar.AddLabelTool(self.TB_VIEW_PIPE_EDIT, "Data pipe editor", wx.Bitmap(paths.icon_22x22.pipe, wx.BITMAP_TYPE_ANY), shortHelp="Data pipe editor")
        self.Bind(wx.EVT_TOOL, self.show_pipe_editor, id=self.TB_VIEW_PIPE_EDIT)

        # Build the toolbar.
        self.toolbar.Realize()


    def update_status_bar(self):
        """Update the status bar info."""

        # Set the current data pipe info.
        pipe = cdp_name()

        # No data pipe.
        if pipe == None:
            pipe = ''

        # Set the status.
        wx.CallAfter(self.status_bar.SetStatusText, "(C) 2001-2012 the relax development team", 0)
        wx.CallAfter(self.status_bar.SetStatusText, "Current data pipe:", 1)
        wx.CallAfter(self.status_bar.SetStatusText, pipe, 2)
