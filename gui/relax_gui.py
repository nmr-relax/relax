###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2009-2014,2019 Edward d'Auvergne                              #
# Copyright (C) 2016 Troels Schwarz-Linnet                                    #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Main module for the relax graphical user interface."""

# Python module imports.
from os import F_OK, access, getcwd, sep
import platform
from re import search
import sys
from time import sleep
from warnings import warn
import webbrowser
import wx

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from data_store.gui import Gui
import dep_check
from graphics import IMAGE_PATH, fetch_icon
from gui.about import About_relax
from gui.analyses import Analysis_controller
from gui.spin_viewer.frame import Spin_view_window
from gui.controller import Controller
from gui.export_bmrb import Export_bmrb_window
from gui.filedialog import RelaxDirDialog, RelaxFileDialog
from gui.fonts import font
from gui.icons import Relax_icons
from gui.interpreter import Interpreter
from gui.menu import Menu
from gui.message import error_message, Question
from gui.misc import bitmap_setup, gui_raise, open_file, protected_exec
from gui.pipe_editor import Pipe_editor
from gui.references import References
from gui.relax_prompt import Prompt
from gui.results_viewer import Results_viewer
from gui.components.free_file_format import Free_file_format_window
from gui.string_conv import gui_to_str
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from info import Info_box
from lib.errors import RelaxNoPipeError
from lib.warnings import RelaxWarning
from lib.io import io_streams_restore
from pipe_control import state
from pipe_control.pipes import cdp_name
from pipe_control.reset import reset
from pipe_control.system import pwd
from status import Status; status = Status()
from version import repo_head, version


# wx IDs for the toolbar.
TB_FILE_NEW = wx.NewId()
TB_FILE_CLOSE = wx.NewId()
TB_FILE_CLOSE_ALL = wx.NewId()
TB_FILE_CWD = wx.NewId()
TB_FILE_OPEN = wx.NewId()
TB_FILE_SAVE = wx.NewId()
TB_FILE_SAVE_AS = wx.NewId()
TB_VIEW_CONTROLLER = wx.NewId()
TB_VIEW_SPIN_VIEW = wx.NewId()
TB_VIEW_RESULTS = wx.NewId()
TB_VIEW_PIPE_EDIT = wx.NewId()
TB_VIEW_PROMPT = wx.NewId()



class Main(wx.Frame):
    """The main GUI class."""

    # Hard coded variables.
    min_width = 1000
    min_height = 600

    def __init__(self, parent=None, id=-1, title=""):
        """Initialise the main relax GUI frame."""

        # Store the wxPython info for os/machine/version specific hacks.
        status.wx_info = {}
        status.wx_info["version"] = wx.__version__.split('.')
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

        # Some internal variables.
        self.test_suite_flag = False

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
        relax_icons = Relax_icons()
        relax_icons.setup()
        self.SetIcons(relax_icons)

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
        self.build_toolbar()

        # Build the controller, but don't show it.
        self.controller = Controller(self)

        # Set the window title.
        if version == "repository commit":
            win_title = "relax %s %s" % (version, repo_head)
        else:
            win_title = "relax %s" % version
        self.SetTitle(win_title)

        # Set up the status bar.
        self.status_bar = self.CreateStatusBar(4, 0)
        self.status_bar.SetStatusWidths([-4, -4, -1, -2])
        self.update_status_bar()

        # Add the start screen.
        self.add_start_screen()

        # Close Box event.
        self.Bind(wx.EVT_CLOSE, self.exit_gui)

        # Initialise the special interpreter thread object.
        self.interpreter = Interpreter()

        # Register functions with the observer objects.
        status.observers.pipe_alteration.register('status bar', self.update_status_bar, method_name='update_status_bar')
        status.observers.system_cwd_path.register('status bar', self.update_status_bar, method_name='update_status_bar')
        status.observers.result_file.register('gui', self.show_results_viewer_no_warn, method_name='show_results_viewer_no_warn')
        status.observers.exec_lock.register('gui', self.enable, method_name='enab')

        # Assume a script has been run and there is data in the store.
        self.analysis.load_from_store()


    def about_relax(self, event=None):
        """The about message for relax.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Build the dialog.
        dialog = About_relax(None, -1)

        # The dialog.
        if status.show_gui:
            dialog.Show()


    def action_export_bmrb(self, event=None):
        """Export the contents of the current data pipe for BMRB deposition.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # No current data pipe.
        if not cdp_name():
            gui_raise(RelaxNoPipeError())
            return

        # Open the export window.
        Export_bmrb_window(self)


    def action_state_save(self, event=None):
        """Save the program state.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Not saved yet, therefore pass execution to state_save_as().
        if not self.save_file:
            self.action_state_save_as(event)
            return

        # Save.
        self.state_save()


    def action_state_save_as(self, event=None):
        """Save the program state with file name selection.

        @keyword event: The wx event.
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
        image = wx.StaticBitmap(self, -1, bitmap_setup(IMAGE_PATH+'ulysses_shadowless_400x168.png'))
        sizer.AddStretchSpacer()
        sizer.Add(image, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer.AddStretchSpacer()

        # wxPython-Phoenix instability warning text.
        if not dep_check.wx_stable:
            text = [
                "wxPython-Phoenix version %s.%s.%s detected." % (wx.VERSION[0], wx.VERSION[1], wx.VERSION[2]),
                "This version of Phoenix is not stable and relax support is experimental.",
                "Not all features of the GUI may be available or functional.",
                "Please use wxPython-Phoenix version >= 4.1.0 or \"Classic\" instead - otherwise use at your own risk."
            ]
            for i in range(len(text)):
                element = wx.StaticText(self, -1, text[i])
                element.SetFont(font.roman_font_18)
                element.SetForegroundColour("red")
                sizer.Add(element, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
            sizer.AddStretchSpacer()
            warn(RelaxWarning("  ".join(text)))

        # Re-perform the layout of the GUI elements, and refresh.
        self.Layout()
        self.Refresh()


    def build_toolbar(self):
        """Create the toolbar."""

        # Init.
        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.TB_FLAT)

        # The new analysis button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_NEW, "New analysis", wx.Bitmap(fetch_icon('oxygen.actions.document-new', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="New analysis")
        else:
            self.toolbar.AddTool(TB_FILE_NEW, "New analysis", wx.Bitmap(fetch_icon('oxygen.actions.document-new', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="New analysis")
        self.Bind(wx.EVT_TOOL, self.analysis.menu_new, id=TB_FILE_NEW)

        # The close analysis button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_CLOSE, "Close analysis", wx.Bitmap(fetch_icon('oxygen.actions.document-close', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Close analysis")
        else:
            self.toolbar.AddTool(TB_FILE_CLOSE, "Close analysis", wx.Bitmap(fetch_icon('oxygen.actions.document-close', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Close analysis")
        self.Bind(wx.EVT_TOOL, self.analysis.menu_close, id=TB_FILE_CLOSE)

        # The close all analyses button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_CLOSE_ALL, "Close all analyses", wx.Bitmap(fetch_icon('oxygen.actions.dialog-close', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Close all analyses")
        else:
            self.toolbar.AddTool(TB_FILE_CLOSE_ALL, "Close all analyses", wx.Bitmap(fetch_icon('oxygen.actions.dialog-close', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Close all analyses")
        self.Bind(wx.EVT_TOOL, self.analysis.menu_close_all, id=TB_FILE_CLOSE_ALL)

        # A separator.
        self.toolbar.AddSeparator()

        # The change working directory button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_CWD, "Change working directory", wx.Bitmap(fetch_icon('oxygen.places.folder-favorites', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Change working directory")
        else:
            self.toolbar.AddTool(TB_FILE_CWD, "Change working directory", wx.Bitmap(fetch_icon('oxygen.places.folder-favorites', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Change working directory")
        self.Bind(wx.EVT_TOOL, self.system_cwd, id=TB_FILE_CWD)

        # The open state button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_OPEN, "Open relax state", wx.Bitmap(fetch_icon('oxygen.actions.document-open', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Open relax state")
        else:
            self.toolbar.AddTool(TB_FILE_OPEN, "Open relax state", wx.Bitmap(fetch_icon('oxygen.actions.document-open', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Open relax state")
        self.Bind(wx.EVT_TOOL, self.state_load, id=TB_FILE_OPEN)

        # The save state button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_SAVE, "Save relax state", wx.Bitmap(fetch_icon('oxygen.actions.document-save', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Save relax state")
        else:
            self.toolbar.AddTool(TB_FILE_SAVE, "Save relax state", wx.Bitmap(fetch_icon('oxygen.actions.document-save', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Save relax state")
        self.Bind(wx.EVT_TOOL, self.action_state_save, id=TB_FILE_SAVE)

        # The save as button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_FILE_SAVE_AS, "Save as", wx.Bitmap(fetch_icon('oxygen.actions.document-save-as', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Save as")
        else:
            self.toolbar.AddTool(TB_FILE_SAVE_AS, "Save as", wx.Bitmap(fetch_icon('oxygen.actions.document-save-as', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Save as")
        self.Bind(wx.EVT_TOOL, self.action_state_save_as, id=TB_FILE_SAVE_AS)

        # A separator.
        self.toolbar.AddSeparator()

        # The relax controller button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_VIEW_CONTROLLER, "Controller", wx.Bitmap(fetch_icon('oxygen.apps.preferences-system-performance', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="relax controller")
        else:
            self.toolbar.AddTool(TB_VIEW_CONTROLLER, "Controller", wx.Bitmap(fetch_icon('oxygen.apps.preferences-system-performance', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="relax controller")
        self.Bind(wx.EVT_TOOL, self.show_controller, id=TB_VIEW_CONTROLLER)

        # The spin viewer button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_VIEW_SPIN_VIEW, "Spin viewer", wx.Bitmap(fetch_icon('relax.spin', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Spin viewer window")
        else:
            self.toolbar.AddTool(TB_VIEW_SPIN_VIEW, "Spin viewer", wx.Bitmap(fetch_icon('relax.spin', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Spin viewer window")
        self.Bind(wx.EVT_TOOL, self.show_tree, id=TB_VIEW_SPIN_VIEW)

        # The results viewer button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_VIEW_RESULTS, "Results viewer", wx.Bitmap(fetch_icon('oxygen.actions.view-statistics', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Results viewer window")
        else:
            self.toolbar.AddTool(TB_VIEW_RESULTS, "Results viewer", wx.Bitmap(fetch_icon('oxygen.actions.view-statistics', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Results viewer window")
        self.Bind(wx.EVT_TOOL, self.show_results_viewer, id=TB_VIEW_RESULTS)

        # The data pipe editor button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_VIEW_PIPE_EDIT, "Data pipe editor", wx.Bitmap(fetch_icon('relax.pipe', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Data pipe editor")
        else:
            self.toolbar.AddTool(TB_VIEW_PIPE_EDIT, "Data pipe editor", wx.Bitmap(fetch_icon('relax.pipe', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="Data pipe editor")
        self.Bind(wx.EVT_TOOL, self.show_pipe_editor, id=TB_VIEW_PIPE_EDIT)

        # The relax prompt button.
        if dep_check.wx_classic:
            self.toolbar.AddLabelTool(TB_VIEW_PROMPT, "relax prompt", wx.Bitmap(fetch_icon('oxygen.mimetypes.application-x-executable-script', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="The relax prompt GUI window")
        else:
            self.toolbar.AddTool(TB_VIEW_PROMPT, "relax prompt", wx.Bitmap(fetch_icon('oxygen.mimetypes.application-x-executable-script', "22x22"), wx.BITMAP_TYPE_ANY), shortHelp="The relax prompt GUI window")
        self.Bind(wx.EVT_TOOL, self.show_prompt, id=TB_VIEW_PROMPT)

        # Build the toolbar.
        self.toolbar.Realize()


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
            sys.stderr.flush()


    def contact_relax(self, event=None):
        """Write an email to the relax mailing-list using the standard mailing program.

        @keyword event: The wx event.
        @type event:    wx event
        """

        webbrowser.open_new('mailto:relax-users@gna.org')


    def enable(self):
        """Enable and disable certain parts of the main window with the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # The toolbar.
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_NEW, enable)
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_CLOSE, enable)
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_CLOSE_ALL, enable)
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_CWD, enable)
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_OPEN, enable)
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_SAVE, enable)
        wx.CallAfter(self.toolbar.EnableTool, TB_FILE_SAVE_AS, enable)


    def exit_gui(self, event=None):
        """Catch the main window closure and perform the exit procedure.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Ask if the user is sure they would like to exit.
        doexit = wx.ID_YES
        if status.show_gui and not ds.is_empty():
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

            # Remove the Mac OS X task bar icon.
            if hasattr(self, 'taskbar_icon'):
                self.taskbar_icon.Destroy()

            # Terminate the interpreter thread to allow for a cleaner exit.
            self.interpreter.exit()

            # End the GUI main loop.
            app = wx.GetApp()
            app.ExitMainLoop()


    def init_data(self):
        """Initialise the data used by the GUI interface."""

        # Temporary data:  the save file.
        self.save_file = None
        self.system_cwd_path = pwd(verbose=False)

        # Add the GUI object to the data store, if not present.
        if not hasattr(ds, 'relax_gui'):
            ds.relax_gui = Gui()


    def free_file_format_settings(self, event=None):
        """Open the free file format settings window.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Build the window.
        win = Free_file_format_window()

        # Show the window.
        if status.show_gui:
            win.Show()


    def references(self, event=None):
        """Display the references relevant for relax.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Build and show the references window.
        self.references = References(self)
        if status.show_gui:
            self.references.Show()


    def relax_manual(self, event=None):
        """Display the relax manual.

        @keyword event: The wx event.
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


    def reset(self):
        """Reset the GUI."""

        # Close some GUI windows, if open.
        windows = ['pipe_editor', 'relax_prompt', 'results_viewer', 'spin_viewer']
        for window in windows:
            if hasattr(self, window):
                # Get the object.
                win_obj = getattr(self, window)

                # Close the window.
                win_obj.Close()

        # Flush all wx events to make sure the GUI is ready for the next test.
        wx.Yield()

        # Reset the relax controller.
        self.controller.reset()


    def run_test_suite(self, event=None, categories=['system', 'unit', 'gui', 'verification']):
        """Execute the full test suite.

        @keyword event:         The wx event.
        @type event:            wx event
        @keyword categories:    The list of test categories to run, for example ['system', 'unit', 'gui', 'verification'] for all tests.
        @type categories:       list of str
        """

        # Ask if this should be done.
        msg = "In running the test suite, relax will be reset and all data lost.  Are you sure you would like to run the test suite?"
        if Question(msg, parent=self, size=(400, 150), default=False).ShowModal() == wx.ID_NO:
            return

        # Set the test suite flag.
        self.test_suite_flag = True

        # Change the cursor to waiting.
        wx.BeginBusyCursor()

        # Set a new style to stay on top, refreshing to update the style (needed for Mac OS X and MS Windows).
        orig_style = self.controller.GetWindowStyle()
        self.controller.SetWindowStyle(orig_style | wx.STAY_ON_TOP)
        self.controller.Refresh()

        # Make the relax controller modal so that all other windows are deactivated (to stop users from clicking on things).
        self.controller.MakeModal(True)

        # Close all open windows.
        if hasattr(self, 'spin_viewer'):
            self.spin_viewer.Close()
        if hasattr(self, 'pipe_editor'):
            self.pipe_editor.Close()
        if hasattr(self, 'results_viewer'):
            self.results_viewer.Close()
        if hasattr(self, 'relax_prompt'):
            self.relax_prompt.Close()

        # Reset relax.
        reset()

        # Show the relax controller.
        self.show_controller(event)

        # Yield
        wx.GetApp().Yield(True)

        # Prevent all new GUI elements from being shown.
        status.show_gui = False

        # Run the tests (with the import here to break a nasty circular import).
        import test_suite.test_suite_runner
        runner = test_suite.test_suite_runner.Test_suite_runner([], from_gui=True, categories=categories)
        runner.run_all_tests()

        # Reactive the GUI.
        status.show_gui = True

        # Turn off the busy cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Restore the controller.
        self.controller.SetWindowStyle(orig_style)
        self.controller.MakeModal(False)
        self.controller.Refresh()

        # Unset the test suite flag.
        self.test_suite_flag = False

        # Set the controller main gauge to 100%.
        wx.CallAfter(self.controller.main_gauge.SetValue, 100)


    def run_test_suite_gui(self, event=None):
        """Execute the GUI tests.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Forward the call.
        self.run_test_suite(event, categories=['gui'])


    def run_test_suite_sys(self, event=None):
        """Execute the system tests.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Forward the call.
        self.run_test_suite(event, categories=['system'])


    def run_test_suite_unit(self, event=None):
        """Execute the unit tests.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Forward the call.
        self.run_test_suite(event, categories=['unit'])


    def run_test_suite_verification(self, event=None):
        """Execute the verification tests.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Forward the call.
        self.run_test_suite(event, categories=['verification'])


    def show_controller(self, event=None):
        """Display the relax controller window.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Bring the window to the front.
        if self.controller.IsShown():
            self.controller.Raise()
            return

        # Open the window.
        if status.show_gui:
            self.controller.Show()


    def show_pipe_editor(self, event=None):
        """Display the data pipe editor window.

        @keyword event: The wx event.
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

        # Update the grid.
        self.pipe_editor.update_grid()
        self.pipe_editor.activate()

        # Register the grid for updating when a user function completes or when the GUI analysis tabs change (needed here for the window hiding and associated unregistering).
        self.pipe_editor.observer_setup(register=True)


    def show_prompt(self, event=None):
        """Display the relax prompt window.

        @keyword event: The wx event.
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

        @keyword event: The wx event.
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


    def show_tree(self, event=None):
        """Display the molecule, residue, and spin tree window.

        @keyword event: The wx event.
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
        if not self.spin_viewer.IsShown():
            self.spin_viewer.Show(show=status.show_gui)


    def state_load(self, event=None, file_name=None):
        """Load the program state.

        @keyword event:     The wx event.
        @type event:        wx event
        @keyword file_name: The name of the file to load (for dialogless operation).
        @type file_name:    str
        """

        # Execution lock.
        if status.exec_lock.locked():
            return

        # Warning.
        if not self.analysis.init_state or not ds.is_empty():
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
                # Update the core of the GUI to match the new data store.
                self.sync_ds(upload=False)

            # File loading failure.
            else:
                # Reset relax to clear any partially loaded data.
                reset()

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


    def system_cwd(self, event=None):
        """Change the system current working directory.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The dialog.
        dialog = RelaxDirDialog(parent=self, message="Select working directory", defaultPath=wx.EmptyString, style=wx.DD_CHANGE_DIR)

        # Show the dialog and catch if no directory has been selected.
        if status.show_gui and dialog.ShowModal() != wx.ID_OK:
            # Don't do anything.
            return

        # Call the get_path function to get the directory name and change path.
        self.system_cwd_path = dialog.get_path()

        # Update the status bar.
        self.update_status_bar()

        # Change the directory
        try:
            wx.BeginBusyCursor()

            # Sleep a little so the user sees the busy cursor and knows that the directory changes has occurred.
            sleep(1)

        # Turn off the user feedback.
        finally:
            if wx.IsBusy():
                wx.EndBusyCursor()


    def uf_call(self, event=None):
        """Catch the user function call to properly specify the parent window.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The user function ID.
        uf_id = event.GetId()

        # Get the user function name.
        name = uf_store.get_uf(uf_id)

        # Call the user function GUI object.
        uf_store[name](event=event, wx_parent=self)


    def update_status_bar(self):
        """Update the status bar info."""

        # Set the current data pipe info.
        pipe = cdp_name()

        # No data pipe.
        if pipe == None:
            pipe = ''

        # Get the current working directory
        self.system_cwd_path = pwd(verbose=False)

        # The relax information box.
        info = Info_box()

        # Set the status.
        wx.CallAfter(self.status_bar.SetStatusText, info.copyright_short, 0)
        wx.CallAfter(self.status_bar.SetStatusText, self.system_cwd_path, 1)
        wx.CallAfter(self.status_bar.SetStatusText, "Data pipe:", 2)
        wx.CallAfter(self.status_bar.SetStatusText, pipe, 3)
