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
from gui.misc import float_to_gui, str_to_gui
from gui.user_functions import relax_data, sequence
from gui.wizard import Wiz_window


class Mf(GuiTestCase):
    """Class for testing various aspects specific to the model-free auto-analysis."""

    def test_mf_auto_analysis(self):
        """Test the model-free auto-analysis."""

        # Simulate the new analysis wizard.
        self.gui.analysis.menu_new(None)
        page = self.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_mf(None)
        page.analysis_name.SetValue("Model-free test")
        self.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.gui.analysis.new_wizard.wizard.get_page(1)
        self.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name = self.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name)

        # Alias the analysis.
        analysis = self.gui.analysis.get_page_from_name("Model-free test")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Set up a wizard window instance for all of the user function pages.
        wizard = Wiz_window()

        # The data path.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep

        # Load the sequence.
        seq_read = sequence.Read_page(wizard, self.gui)
        seq_read.file.SetValue(str_to_gui(data_path + 'noe.500.out'))
        seq_read.on_execute()

        # Load the relaxation data.
        data = [
            ['noe.500.out', 'noe_500', 'NOE', 500e6],
            ['r1.500.out',  'r1_500',  'R1',  500e6],
            ['r2.500.out',  'r2_500',  'R2',  500e6],
            ['noe.900.out', 'noe_900', 'NOE', 900e6],
            ['r1.900.out',  'r1_900',  'R1',  900e6],
            ['r2.900.out',  'r2_900',  'R2',  900e6]
        ]
        for i in range(len(data)):
            relax_data_read = relax_data.Read_page(wizard, self.gui)
            relax_data_read.file.SetValue(str_to_gui(data_path + data[i][0]))
            relax_data_read.ri_id.SetValue(str_to_gui(data[i][1]))
            relax_data_read.ri_type.SetValue(str_to_gui(data[i][2]))
            relax_data_read.frq.SetValue(float_to_gui(data[i][3]))
            relax_data_read.on_execute()

        # Select only the tm0 and tm1 local tm models.
        analysis.local_tm_model_field.select = [True, True, False, False, False, False, False, False, False, False]
        analysis.local_tm_model_field.modify(None)

        # Select only the m1 and m2 model-free models.
        analysis.mf_model_field.select = [False, True, True, False, False, False, False, False, False, False]
        analysis.mf_model_field.modify(None)

        # Change the grid increments.
        analysis.grid_inc.SetValue(3)

        # Set the number of Monte Carlo simulations.
        analysis.mc_sim_num.SetValue(2)

        # Check that the data has been correctly updated prior to execution.
        analysis.sync_ds(upload=True)
        self.assertEqual(analysis.data.save_dir, ds.tmpdir)
        self.assertEqual(analysis.data.local_tm_models, ['tm0', 'tm1'])
        self.assertEqual(analysis.data.mf_models, ['m1', 'm2'])
        self.assertEqual(analysis.data.grid_inc, 3)
        self.assertEqual(analysis.data.mc_sim_num, 2)

        # Execute relax.
        analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_id))

        # Wait for execution to complete.
        analysis.thread.join()

        # Exceptions in the thread.
        self.check_exceptions()

        # The real data.
        res_nums = [4, 5, 6]
        sat = [5050.0, 51643.0, 53663.0]
        ref = [148614.0, 166842.0, 128690.0]
        noe = [0.033980647852826784, 0.30953237194471417, 0.4169943274535706]
        noe_err = [0.02020329903276632, 0.019181416098790607, 0.026067523940084526]

        # Check the data pipe.
        self.assertEqual(cdp_name(), ds.relax_gui.analyses[0].pipe_name)

        # Check the data.
        i = 0
        for spin_cont, mol_name, res_num, res_name in spin_loop(full_info=True):
            # Skip deselected spins.
            if not spin_cont.select:
                continue

            # Spin info.
            self.assertEqual(res_nums[i], res_num)

            # Check the intensity data.
            self.assertEqual(sat[i], spin_cont.intensities['sat'])
            self.assertEqual(ref[i], spin_cont.intensities['ref'])

            # Check the NOE data.
            self.assertEqual(noe[i], spin_cont.noe)
            self.assertEqual(noe_err[i], spin_cont.noe_err)

            # Increment the spin index.
            i += 1

        # Check the created files.
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'noe.agr', F_OK))
