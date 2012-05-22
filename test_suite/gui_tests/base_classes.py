###############################################################################
#                                                                             #
# Copyright (C) 2006-2012 Edward d'Auvergne                                   #
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
"""Base classes for the GUI tests."""

# Python module imports.
from os import sep
import Queue
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
import wx

# Dependency checks.
import dep_check

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.gui import Gui
from generic_fns.reset import reset
from relax_io import delete
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.wizard import Wiz_window
from gui.uf_objects import Uf_page


class GuiTestCase(TestCase):
    """The GUI test base class."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the TestCase __init__ method.
        super(GuiTestCase, self).__init__(methodName)

        # The directory where the tests are located, and a string used for classifying skipped tests.
        self._test_dir = 'test_suite' + sep + 'gui_tests'
        self._skip_type = 'gui'

        # Get the wx app, if the test suite is launched from the gui.
        self.app = wx.GetApp()

        # Flag for the GUI.
        self._gui_launch = False
        if self.app != None:
            self._gui_launch = True


    def _execute_uf(self, uf_name=None, **kargs):
        """Execute the given user function.

        @keyword uf_name:   The name of the user function.
        @type uf_name:      str
        """

        # Create and store a wizard instance to be used in all user function pages (if needed).
        if not hasattr(self, '_wizard'):
            self._wizard = Wiz_window(self.app.gui)

        # Get the user function data object.
        uf_data = uf_info.get_uf(uf_name)

        # Merge the file and directory args, as needed.
        for i in range(len(uf_data.kargs)):
            # Alias.
            arg = uf_data.kargs[i]

            # File selection and associated directory arg.
            if arg['arg_type'] == 'dir' and arg['name'] in kargs:
                # Find the associated file selection arg name.
                for j in range(len(uf_data.kargs)):
                    if uf_data.kargs[i]['arg_type'] == 'file sel':
                        file_sel_name = uf_data.kargs[i]['name']

                # Prepend the directory to the file, if needed.
                if file_sel_name in kargs:
                    kargs[file_sel_name] = kargs[arg['name']] + sep + kargs[file_sel_name]

        # Create the page.
        uf_page = Uf_page(uf_name, parent=self._wizard, sync=True)

        # Update the user function page.
        uf_page.on_display()

        # Set all the values.
        for key in kargs:
            uf_page.SetValue(key=key, value=kargs[key])

        # Execute the user function.
        uf_page.on_execute()

        # Flush the interpreter to force synchronous user functions operation.
        interpreter.flush()


    def check_exceptions(self):
        """Check that no exception has occurred."""

        # Check.
        try:
            # Get the exception from the queue.
            index, exc = status.exception_queue.get(block=False)

            # Fail.
            self.fail()

        # No exception.
        except Queue.Empty:
            pass


    def script_exec(self, script):
        """Execute a GUI script within the GUI test framework.

        @param script:  The full path of the script to execute.
        @type script:   str
        """

        # Execute the script.
        execfile(script, globals(), locals())


    def setUp(self):
        """Set up for all the functional tests."""

        # Create a temporary directory for the results.
        ds.tmpdir = mkdtemp()

        # Start the GUI if not launched from the GUI.
        if not self._gui_launch:
            self.app = wx.App(redirect=False)

            # relax GUI imports (here to prevent a circular import from the test suite in the GUI).
            if dep_check.wx_module:
                from gui.relax_gui import Main

            # Build the GUI.
            self.app.gui = Main(parent=None, id=-1, title="")


    def tearDown(self):
        """Default tearDown operation - delete temp directories and files and reset relax."""

        # Remove the temporary directories.
        if hasattr(ds, 'tmpdir'):
            # Delete the directory.
            rmtree(ds.tmpdir)

            # Remove the variable.
            del ds.tmpdir

        # Remove the temporary directories.
        if hasattr(self, 'tmpdir'):
            # Delete the directory.
            rmtree(self.tmpdir)

            # Remove the variable.
            del self.tmpdir

        # Remove temporary files.
        if hasattr(ds, 'tmpfile'):
            # Delete the file.
            delete(ds.tmpfile, fail=False)

            # Remove the variable.
            del ds.tmpfile

        # Remove temporary files.
        if hasattr(self, 'tmpfile'):
            # Delete the file.
            delete(self.tmpfile, fail=False)

            # Remove the variable.
            del self.tmpfile

        # Delete all the GUI analysis tabs.
        self.app.gui.analysis.delete_all()

        # Reset relax.
        reset()

        # Reset the observers.
        status._setup_observers()

        # Destroy some GUI windows, if open.
        windows = ['pipe_editor', 'relax_prompt', 'results_viewer', 'spin_viewer']
        for window in windows:
            if hasattr(self.app.gui, window):
                # Get the object.
                win_obj = getattr(self.app.gui, window)

                # Destroy the wxWidget part.
                win_obj.Destroy()

                # Destroy the Python object part.
                delattr(self.app.gui, window)

        # Destroy the GUI.
        if not self._gui_launch and hasattr(self.app, 'gui'):
            self.app.gui.Destroy()

        # Recreate the GUI data object.
        ds.relax_gui = Gui()

        # Delete any wizard objects.
        if hasattr(self, '_wizard'):
            del self._wizard

        # Flush all wx events to make sure the GUI is ready for the next test.
        wx.Yield()
