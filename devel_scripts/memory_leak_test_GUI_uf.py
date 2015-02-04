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
from gui.controller import Controller
from gui.fonts import font
from gui.interpreter import Interpreter
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from lib.errors import RelaxError
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()



class Controller:
    """Dummy relax controller."""

    def __init__(self):
        self.log_panel = Log_panel()



class Log_panel:
    """Dummy relax controller log panel."""

    def on_goto_end(self, arg1):
        """Dummy function."""



class Testing_frame(wx.Frame):
    """Testing frame."""

    def __init__(self, parent, title):
        """Set up a minimal relax GUI."""

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
        self.controller = Controller()

        self.test()
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


    def show_controller(self, arg1):
        """Dummy function."""


    def test(self):
        """Run the tests."""

        # Minimise via the GUI user function.
        file = open('muppy_log', 'w')
        for i in range(10000):
            self._execute_uf(uf_name='minimise.execute', min_algor='simplex', constraints=False)
            if not i % 100:
                file.write("Iteration %i\n" % i)
                file.write("Muppy heap:\n")
                for line in muppy.summary.format_(muppy.summary.summarize(muppy.get_objects())):
                    file.write("%s\n" % line)
                file.write("\n\n\n")
                file.flush()

        print("Finished!")


# Missing intensity type (allow this script to run outside of the system test framework).
if not hasattr(ds, 'int_type'):
    ds.int_type = 'height'

# Missing temporary directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp'

# Create the data pipe.
pipe.create('rx', 'relax_fit')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'

# Load the sequence.
sequence.read('Ap4Aase.seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path, res_num_col=1)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [
    'T2_ncyc1_ave',
    'T2_ncyc1b_ave',
    'T2_ncyc2_ave',
    'T2_ncyc4_ave',
    'T2_ncyc4b_ave',
    'T2_ncyc6_ave',
    'T2_ncyc9_ave',
    'T2_ncyc9b_ave',
    'T2_ncyc11_ave',
    'T2_ncyc11b_ave'
]

# Relaxation times (in seconds).
times = [
    0.0176,
    0.0176,
    0.0352,
    0.0704,
    0.0704,
    0.1056,
    0.1584,
    0.1584,
    0.1936,
    0.1936
]

# Load the data twice to test data deletion.
for iter in range(2):
    # Loop over the spectra.
    for i in range(len(names)):
        # Load the peak intensities.
        spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method=ds.int_type)

        # Set the relaxation times.
        relax_fit.relax_time(time=times[i], spectrum_id=names[i])

    # Specify the duplicated spectra.
    spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc4_ave', 'T2_ncyc4b_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc9b_ave', 'T2_ncyc9_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc11_ave', 'T2_ncyc11b_ave'])

    # Peak intensity error analysis.
    spectrum.error_analysis()

    # Delete the data.
    if iter == 0:
        for i in range(len(names)):
            spectrum.delete(names[i])

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
minimise.grid_search(inc=11)

# Set up and execute the GUI.
app = wx.App(False)
frame = Testing_frame(None, "GUI memory test")
frame.Show(True)
app.MainLoop()
