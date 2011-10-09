###############################################################################
#                                                                             #
# Copyright (C) 2006-2011 Edward d'Auvergne                                   #
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

# Python module imports.
from os import F_OK, access, sep
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.misc import int_to_gui, str_to_gui
from gui.user_functions import deselect, sequence, spin
from gui.wizard import Wiz_window


class State(GuiTestCase):
    """Class for testing various aspects specific to saved states."""

    def test_load_state_no_gui(self):
        """Test the loading of a relax save state with no GUI data."""

        # Simulate the 'Open relax state' menu entry.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'OMP' + sep + 'final_results_trunc_1.3'
        self.app.gui.state_load(file_name=file)

        # Show the pipe editor.
        self.app.gui.show_pipe_editor(None)

        # The menu (this is used to set the selected pipe).
        self.app.gui.pipe_editor.menu(Fake_grid_cell_right_click())

        # Associated an auto-analysis with the data pipe.
        self.app.gui.pipe_editor.associate_auto(None)

        # The index.
        index = 0

        # Test that the model-free analysis tab is loaded.
        self.assert_(not self.app.gui.analysis.init_state)
        self.assertEqual(self.app.gui.analysis._num_analyses, 1)
        self.assertEqual(len(self.app.gui.analysis._analyses), 1)
        self.assertEqual(self.app.gui.analysis.notebook.GetPageCount(), 1)
        self.assert_(self.app.gui.analysis._analyses[index].init_flag)

        # Test the relax data store.
        self.assert_(hasattr(ds, 'relax_gui'))
        self.assertEqual(ds.relax_gui.analyses[index].analysis_name, 'Model-free')
        self.assertEqual(ds.relax_gui.analyses[index].pipe_name, 'a')



class Fake_grid_cell_right_click:
    """Simulate a grid_cell_right_click event ."""

    def GetRow(self):
        """Overwrite the GetRow() method."""

        # Return the first row.
        return 0
