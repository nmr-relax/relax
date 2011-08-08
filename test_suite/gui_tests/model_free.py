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
import numpy
from os import F_OK, access, sep
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.analyses import auto_model_free
from gui.misc import float_to_gui, str_to_gui
from gui.user_functions import relax_data, sequence, value
from gui.wizard import Wiz_window


class Mf(GuiTestCase):
    """Class for testing various aspects specific to the model-free auto-analysis."""

    def test_mf_auto_analysis(self):
        """Test the model-free auto-analysis."""

        # Initialise all the special windows (to sometimes catch rare race conditions).
        self.gui.show_prompt(None)
        self.gui.show_tree(None)
        self.gui.show_pipe_editor(None)

        # Simulate the new analysis wizard.
        self.gui.analysis.menu_new(None)
        page = self.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_mf(None)
        page.analysis_name.SetValue(str_to_gui("Model-free test"))
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

        # Set the values.
        value_set = value.Set_page(wizard, self.gui)
        value_set.set_param('csa')
        value_set.on_execute()
        value_set.set_param('r')
        value_set.on_execute()
        value_set.set_param('heteronuc_type')
        value_set.on_execute()
        value_set.set_param('proton_type')
        value_set.on_execute()

        # The unit vector loading wizard.
        analysis.load_unit_vectors(None)

        # The PDB file.
        page = analysis.vect_wizard.get_page(0)
        page.file.SetValue(str_to_gui(status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep + 'sphere.pdb'))
        analysis.vect_wizard._go_next(None)

        # The unit vectors.
        analysis.vect_wizard._go_next(None)

        # Select only the tm0 and tm1 local tm models.
        analysis.local_tm_model_field.select = [True, True, False, False, False, False, False, False, False, False]
        analysis.local_tm_model_field.modify(None)

        # Select only the m1 and m2 model-free models.
        analysis.mf_model_field.select = [False, True, True, False, False, False, False, False, False, False]
        analysis.mf_model_field.modify(None)

        # Change the grid increments.
        analysis.grid_inc.SetValue(3)
        analysis.data.diff_tensor_grid_inc = {'sphere': 5, 'prolate': 5, 'oblate': 5, 'ellipsoid': 3}

        # Set the number of Monte Carlo simulations.
        analysis.mc_sim_num.SetValue(2)

        # Set the protocol mode to automatic.
        analysis.mode_win.select_full_analysis(None)
        analysis.mode_dialog(None)

        # Check that the data has been correctly updated prior to execution.
        analysis.sync_ds(upload=True)
        self.assertEqual(analysis.data.save_dir, ds.tmpdir)
        self.assertEqual(analysis.data.local_tm_models, ['tm0', 'tm1'])
        self.assertEqual(analysis.data.mf_models, ['m1', 'm2'])
        self.assertEqual(analysis.data.grid_inc, 3)
        self.assertEqual(analysis.data.mc_sim_num, 2)

        # Modify some of the class variables to speed up optimisation.
        auto_model_free.dauvergne_protocol.dAuvergne_protocol.opt_func_tol = 1e-5
        auto_model_free.dauvergne_protocol.dAuvergne_protocol.opt_max_iterations = 1000

        # Execute relax.
        analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

        # Wait for execution to complete.
        analysis.thread.join()

        # Exceptions in the thread.
        self.check_exceptions()

        # Check the relax controller.
        self.assertEqual(self.gui.controller.mc_gauge_mf.GetValue(), 100)
        self.assertEqual(self.gui.controller.progress_gauge_mf.GetValue(), 100)
        self.assertEqual(self.gui.controller.main_gauge.GetValue(), 100)

        # Check the diffusion tensor.
        self.assertEqual(cdp.diff_tensor.type, 'sphere')
        self.assertAlmostEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.fixed, True)

        # The global minimisation info.
        self.assertAlmostEqual(cdp.chi2, 4e-19)

        # The spin ID info.
        mol_names = ["sphere_mol1"] * 9
        res_names = ["GLY"] * 9
        res_nums = range(1, 10)
        spin_names = ["N"] * 9
        spin_nums = numpy.array(range(9)) * 2 + 1

        # Check the spin data.
        i = 0
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # The ID info.
            self.assertEqual(mol_name, mol_names[i])
            self.assertEqual(res_name, res_names[i])
            self.assertEqual(res_num,  res_nums[i])
            self.assertEqual(spin.name, spin_names[i])
            self.assertEqual(spin.num,  spin_nums[i])

            # The data.
            self.assertEqual(spin.select, True)
            self.assertEqual(spin.fixed, False)
            self.assertEqual(spin.proton_type, '1H')
            self.assertEqual(spin.heteronuc_type, '15N')
            self.assertEqual(spin.attached_proton, None)
            self.assertEqual(spin.nucleus, None)
            self.assertAlmostEqual(spin.r, 1.02 * 1e-10)
            self.assertAlmostEqual(spin.csa, -172e-6)

            # The model-free data.
            self.assertEqual(spin.model, 'm2')
            self.assertEqual(spin.equation, 'mf_orig')
            self.assertEqual(len(spin.params), 2)
            self.assertEqual(spin.params[0], 'S2')
            self.assertEqual(spin.params[1], 'te')
            self.assertAlmostEqual(spin.s2, 0.8)
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            self.assertEqual(spin.local_tm, None)
            self.assertAlmostEqual(spin.te, 20e-12)
            self.assertEqual(spin.tf, None)
            self.assertEqual(spin.ts, None)
            self.assertEqual(spin.rex, None)

            # The spin minimisation info.
            self.assertEqual(spin.chi2, None)
            self.assertEqual(spin.iter, None)
            self.assertEqual(spin.f_count, None)
            self.assertEqual(spin.g_count, None)
            self.assertEqual(spin.h_count, None)
            self.assertEqual(spin.warning, None)

            # Increment the index.
            i += 1
