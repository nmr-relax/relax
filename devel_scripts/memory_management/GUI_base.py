###############################################################################
#                                                                             #
# Copyright (C) 2013-2015 Edward d'Auvergne                                   #
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

"""Script for relaxation curve fitting.

Run with a normal version of Python, i.e. a debugging version is not needed, with:

$ ./relax devel_scripts/memory_leak_test_GUI_uf.py
"""

# Python module imports.
from os import sep
from pympler import muppy
import sys
import wx

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from gui import relax_gui
from gui.fonts import font
from gui.interpreter import Interpreter
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from lib.errors import RelaxError
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()



class Dummy_controller:
    """Dummy relax controller."""

    def __init__(self):
        self.log_panel = Dummy_log_panel()



class Dummy_log_panel:
    """Dummy relax controller log panel."""

    def on_goto_end(self, arg1):
        """Dummy function."""



class Testing_frame(wx.Frame):
    """Testing frame."""

    def __init__(self, parent, title, num=10000):
        """Set up a minimal relax GUI."""

        # Store the args.
        self.num = num

        # Initialise the frame.
        wx.Frame.__init__(self, parent, title=title, size=(200,100))

        # Set up a pseudo-relax GUI.
        app = wx.GetApp()
        app.gui = self

        # Set up some standard interface-wide fonts.
        font.setup()

        # Initialise the special interpreter thread object.
        self.interpreter = Interpreter()

        # Build the controller, but don't show it.
        self.controller = Dummy_controller()

        # Open the muppy results file.
        self.file = open('muppy_log', 'w')

        # Run the test.
        self.test()
        print("Finished!")

        # Show the frame.
        self.Show(True)


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


    def muppy_loop(self):
        """Generator method for looping over the iterations and writing out the muppy output."""

        # Loop over the desired number of iterations.
        for i in range(self.num):
            # Muppy output, only output at every 100th iteration.
            if not i % 100:
                self.file.write("Iteration %i\n" % i)
                self.file.write("Muppy heap:\n")
                for line in muppy.summary.format_(muppy.summary.summarize(muppy.get_objects())):
                    self.file.write("%s\n" % line)
                self.file.write("\n\n\n")
                self.file.flush()

            # Yield the loop index.
            yield i


    def show_controller(self, arg1):
        """Dummy function."""
