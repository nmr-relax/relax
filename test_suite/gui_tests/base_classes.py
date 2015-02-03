###############################################################################
#                                                                             #
# Copyright (C) 2006-2015 Edward d'Auvergne                                   #
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
"""Base classes for the GUI tests."""

# Python module imports.
from math import pi    # This is needed for relax scripts as pi is located in the relax prompt namespace.
from os import sep
from tempfile import mktemp, mkdtemp
from unittest import TestCase
import wx

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from gui.string_conv import str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizards.wiz_objects import Wiz_window
from lib.compat import queue
from lib.errors import RelaxError
from pipe_control.reset import reset
from prompt.interpreter import exec_script
from status import Status; status = Status()
from test_suite.clean_up import deletion
from user_functions.data import Uf_info; uf_info = Uf_info()


class GuiTestCase(TestCase):
    """The GUI test base class."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # A string used for classifying skipped tests.
        if not hasattr(self, '_skip_type'):
            self._skip_type = 'gui'

        # Execute the TestCase __init__ method.
        super(GuiTestCase, self).__init__(methodName)


    def _execute_uf(self, *args, **kargs):
        """Execute the given user function.

        @keyword uf_name:   The name of the user function.
        @type uf_name:      str
        """

        # Checks.
        if 'uf_name' not in kargs:
            raise RelaxError("The user function name argument 'uf_name' has not been supplied.")

        # Process the user function name.
        uf_name = kargs.pop('uf_name')

        # Get the user function data object.
        uf_data = uf_info.get_uf(uf_name)

        # Convert the args into keyword args.
        for i in range(len(args)):
            # The keyword name for this arg.
            name = uf_data.kargs[i]['name']

            # Check.
            if name in kargs:
                raise RelaxError("The argument '%s' clashes with the %s keyword argument of '%s'." % (arg[i], name, kargs[name]))

            # Set the keyword arg.
            kargs[name] = args[i]

        # Add the keyword args not supplied, using the default value.
        for i in range(len(uf_data.kargs)):
            # Alias.
            arg = uf_data.kargs[i]

            # Already set.
            if arg['name'] in kargs:
                continue

            # Set the default.
            kargs[arg['name']] = arg['default']

        # Merge the file and directory args, as needed.
        for i in range(len(uf_data.kargs)):
            # Alias.
            arg = uf_data.kargs[i]

            # File selection and associated directory arg.
            if arg['arg_type'] == 'dir' and arg['name'] in kargs:
                # Find the associated file selection arg name.
                for j in range(len(uf_data.kargs)):
                    if uf_data.kargs[j]['arg_type'] == 'file sel':
                        file_sel_name = uf_data.kargs[j]['name']

                # Prepend the directory to the file, if needed and supplied.
                if file_sel_name in kargs and kargs[arg['name']]:
                    kargs[file_sel_name] = kargs[arg['name']] + sep + kargs[file_sel_name]

                # Remove the directory argument.
                kargs.pop(arg['name'])

        # The user function object.
        uf = uf_store[uf_name]

        # Force synchronous operation of the user functions.
        status.gui_uf_force_sync = True

        # Call the GUI user function object with all keyword args, but do not execute the wizard.
        uf(wx_wizard_run=False, **kargs)

        # Execute the user function, by mimicking a click on 'ok'.
        uf.wizard._ok()

        # Restore the synchronous or asynchronous operation of the user functions so the GUI can return to normal.
        status.gui_uf_force_sync = False

        # Destroy the user function object.
        uf.Destroy()


    def check_exceptions(self):
        """Check that no exception has occurred."""

        # Check.
        try:
            # Get the exception from the queue.
            index, exc = status.exception_queue.get(block=False)

            # Print out.
            print("Exception found, failing the test with an AssertionError:\n")

            # Fail.
            self.fail()

        # No exception.
        except queue.Empty:
            pass


    def clean_up_windows(self):
        """Kill all windows."""

        # Destroy all user function windows to save memory (specifically to avoid the 10,000 USER Object limit in MS Windows).
        for name in uf_store:
            uf_store[name].Destroy()

        # Kill the spin viewer window.
        if hasattr(self.app.gui, 'spin_viewer'):
            self.app.gui.spin_viewer.Destroy()
            del self.app.gui.spin_viewer

        # Kill the pipe editor window.
        if hasattr(self.app.gui, 'pipe_editor'):
            self.app.gui.pipe_editor.Destroy()
            del self.app.gui.pipe_editor

        # Kill the results viewer window.
        if hasattr(self.app.gui, 'results_viewer'):
            self.app.gui.results_viewer.Destroy()
            del self.app.gui.results_viewer


    def new_analysis_wizard(self, analysis_type=None, analysis_name=None, pipe_name=None, pipe_bundle=None):
        """Simulate the new analysis wizard, and return the analysis page.

        @keyword analysis_type: The type of the analysis to use in the first wizard page.
        @type analysis_type:    str
        @keyword analysis_name: The name of the analysis to use in the first wizard page.
        @type analysis_name:    str
        @keyword pipe_name:     The name of the data pipe to create, if different from the default.
        @type pipe_name:        None or str
        @keyword pipe_bundle:   The name of the data pipe bundle to create, if different from the default.
        @type pipe_bundle:      None or str
        """

        # Simulate the menu selection, but don't destroy the GUI element.
        self.app.gui.analysis.menu_new(None, destroy=False)

        # The first page.
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        if analysis_type == 'noe':
            page.select_noe(None)
        elif analysis_type == 'r1':
            page.select_r1(None)
        elif analysis_type == 'r2':
            page.select_r2(None)
        elif analysis_type == 'mf':
            page.select_mf(None)
        elif analysis_type == 'disp':
            page.select_disp(None)
        else:
            raise RelaxError("Unknown analysis type '%s'." % analysis_type)
        if analysis_name:
            page.analysis_name.SetValue(str_to_gui(analysis_name))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # The second page.
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        if pipe_name:
            page.pipe_name.SetValue(str_to_gui(pipe_name))
        if pipe_bundle:
            page.pipe_bundle.SetValue(str_to_gui(pipe_bundle))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data, then clean up.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Wizard cleanup.
        wx.Yield()
        self.app.gui.analysis.new_wizard.Destroy()
        del self.app.gui.analysis.new_wizard

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle)

        # Return the analysis page.
        return self.app.gui.analysis.get_page_from_name(analysis_name)


    def script_exec(self, script):
        """Execute a GUI script within the GUI test framework.

        @param script:  The full path of the script to execute.
        @type script:   str
        """

        # The namespace to pass into the script execution environment.
        space = locals()

        # Place some objects in the local namespace.
        space.update({'pi': pi})

        # Execute the script.
        exec_script(script, space)


    def setUp(self):
        """Set up for all the functional tests."""

        # Create a temporary file for the tests that need it.
        ds.tmpfile = mktemp()

        # Create a temporary directory for the results.
        ds.tmpdir = mkdtemp()

        # Get the wx app.
        self.app = wx.GetApp()


    def tearDown(self):
        """Default tearDown operation - delete temp directories and files and reset relax."""

        # Flush all wx events prior to the clean up operations of this method.  This prevents these events from occurring after the GUI elements have been deleted.
        wx.Yield()

        # Remove the temporary directory and variable.
        deletion(obj=ds, name='tmpdir', dir=True)
        deletion(obj=self, name='tmpdir', dir=True)

        # Remove temporary file and variable.
        deletion(obj=ds, name='tmpfile', dir=False)
        deletion(obj=self, name='tmpfile', dir=False)

        # Reset relax.
        reset()

        # Get the wx app.
        self.app = wx.GetApp()

        # Close all windows to unregister the observer objects.
        if hasattr(self.app.gui, 'pipe_editor'):
            self.app.gui.pipe_editor.Close()
        if hasattr(self.app.gui, 'results_viewer'):
            self.app.gui.results_viewer.Close()
        wx.Yield()

        # Kill all windows.
        wx.CallAfter(self.clean_up_windows)

        # Flush all wx events again to allow the reset event to propagate throughout the GUI and the execution lock to be released before the next test starts.
        wx.Yield()

        # Print out a list of all living windows to help ensure that custom Close() and Destroy() methods are cleaning up all objects.
        print("\n\nList of all living GUI elements - this must only include the main GUI window and the relax controller:")
        for window in wx.GetTopLevelWindows():
            print("    Window: %s" % window)
            if isinstance(window, Wiz_window):
                print("        Wizard name: %s" % window.name)
                print("        Wizard pages: %s" % window._pages)
        print("\n\n\n")
