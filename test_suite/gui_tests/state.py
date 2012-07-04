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
from gui.string_conv import int_to_gui, str_to_gui
from gui.wizard import Wiz_window


class State(GuiTestCase):
    """Class for testing various aspects specific to saved states."""

    def test_old_state_loading(self):
        """Test the loading of an old relax 1.3 save state with GUI information."""

        # Simulate the 'Open relax state' menu entry.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'saved_states' + sep + 'gui_analyses_1.3.bz2'
        self.app.gui.state_load(file_name=file)

        # Check the analysis structures.
        names = ['Steady-state NOE', 'R1 relaxation', 'Model-free']
        types = ['NOE', 'R1', 'model-free']
        frq = ['600', '300', None]
        grid_inc = [None, None, 3]
        mc_sim_num = [None, None, 50]
        pipe_names = ['noe (Wed May 30 20:33:21 2012)', 'r1 (Wed May 30 20:55:02 2012)', 'mf (Wed May 30 21:23:17 2012)']
        save_dirs = ['/data/relax/gui/gui_testing/noe', '/data/relax/gui/gui_testing/r1', '/data/relax/gui/gui_testing/mf']
        for i in range(len(ds.relax_gui.analyses)):
            self.assertEqual(ds.relax_gui.analyses[i].analysis_name, names[i])
            self.assertEqual(ds.relax_gui.analyses[i].analysis_type, types[i])
            self.assertEqual(ds.relax_gui.analyses[i].pipe_name, pipe_names[i])
            self.assertEqual(ds.relax_gui.analyses[i].save_dir, save_dirs[i])
            if frq[i] != None:
                self.assertEqual(ds.relax_gui.analyses[i].frq, frq[i])
            if grid_inc[i] != None:
                self.assertEqual(ds.relax_gui.analyses[i].grid_inc, grid_inc[i])
            if mc_sim_num[i] != None:
                self.assertEqual(ds.relax_gui.analyses[i].mc_sim_num, mc_sim_num[i])

        # Data checks.
        self.assertEqual(len(ds), 9)
        pipe_names = ["noe (Wed May 30 20:33:21 2012)", "r1 (Wed May 30 20:55:02 2012)", "mf (Wed May 30 21:23:17 2012)", "local_tm", "sphere", "oblate", "prolate", "ellipsoid", "final"]
        for pipe in pipe_names:
            # Loop over the residues.
            for i in range(len(ds[pipe].mol[0].res)):
                # Alias.
                res = ds[pipe].mol[0].res[i]
                print res.spin[0]

                # Check the 15N spin data.
                self.assertEqual(res.spin[0].name, 'N')

                # Skip the 1H checks for the NOE and R1 pipes, as no 1H data is recreated.
                if pipe in ["noe (Wed May 30 20:33:21 2012)", "r1 (Wed May 30 20:55:02 2012)"]:
                    continue

                # Check the 1H spin data.
                self.assertEqual(res.spin[1].name, 'H')


    def test_load_state_no_gui(self):
        """Test the loading of a relax save state with no GUI data."""

        # Simulate the 'Open relax state' menu entry.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'OMP' + sep + 'final_results_trunc_1.3_v2'
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
