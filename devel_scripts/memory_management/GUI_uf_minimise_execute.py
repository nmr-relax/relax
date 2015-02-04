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
from gui.interpreter import Interpreter
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from lib.errors import RelaxError
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# Base module imports.
from GUI_base import Testing_frame



class Frame(Testing_frame):
    """Testing frame."""

    def test(self):
        """Run the test."""

        # Run for the desired number of iterations.
        for i in self.muppy_loop():
            # Minimise via the GUI user function.
            self._execute_uf(uf_name='minimise.execute', min_algor='simplex', constraints=False)



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
frame = Frame(None, "GUI memory test")
frame.Show(True)
app.MainLoop()
