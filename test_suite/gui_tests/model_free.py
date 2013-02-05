###############################################################################
#                                                                             #
# Copyright (C) 2006-2013 Edward d'Auvergne                                   #
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

# Python module imports.
import numpy
from os import F_OK, access, sep
from tempfile import mkdtemp
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.interatomic import interatomic_loop
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.analyses import auto_model_free
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import float_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizard import Wiz_window


class Mf(GuiTestCase):
    """Class for testing various aspects specific to the model-free auto-analysis."""

    def test_bug_20479_gui_final_pipe(self):
        """Catch bug #20479 (https://gna.org/bugs/?20479), the failure to load a relax state in the GUI.

        This was reported by Stanislava Panova (https://gna.org/users/stacy).
        """

        # Simulate the new analysis wizard.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_mf(None)
        page.analysis_name.SetValue(str_to_gui("Model-free test"))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Model-free test")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # The data path.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'bug_20479_gui_final_pipe' + sep

        # Launch the spin viewer window.
        self.app.gui.show_tree()

        # Spin loading wizard:  Initialisation.
        self.app.gui.spin_viewer.load_spins_wizard()

        # Spin loading wizard:  The NOE data file.
        page = self.app.gui.spin_viewer.wizard.get_page(0)
        page.selection = 'sequence'
        self.app.gui.spin_viewer.wizard._go_next()
        page = self.app.gui.spin_viewer.wizard.get_page(self.app.gui.spin_viewer.wizard._current_page)
        page.uf_args['file'].SetValue(str_to_gui(data_path + 'NoeRelN'))
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Spin loading wizard:  The spin loading.
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Close the spin viewer window.
        self.app.gui.spin_viewer.handler_close()

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # Set the element type.
        self._execute_uf(uf_name='spin.element', element='N')

        # Load the relaxation data.
        data = [
            ['NoeRelN', 'noe_800', 'NOE', 800000031.0],
            ['R1850',  'r1_800',  'R1',  800000031.0],
            ['R2863',  'r2_800',  'R2',  800000031.0],
            ['R2604',  'r2_600',  'R2',  599999000.0]
        ]
        for i in range(len(data)):
            self._execute_uf(uf_name='relax_data.read', file=data_path+data[i][0], ri_id=data[i][1], ri_type=data[i][2], frq=data[i][3], mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # Attach the protons.
        self._execute_uf(uf_name='sequence.attach_protons')

        # Dipole-dipole interaction wizard.
        analysis.setup_dipole_pair()        # Initialisation.
        analysis.dipole_wizard._skip()      # Skip the structure.read_pdb user function.
        analysis.dipole_wizard._skip()      # Skip the structure.get_pos user function.
        analysis.dipole_wizard._go_next()   # The dipole_pair.define user function.
        interpreter.flush()                 # Required because of the asynchronous uf call.
        analysis.dipole_wizard._go_next()   # The dipole_pair.set_dist user function.
        interpreter.flush()                 # Required because of the asynchronous uf call.
        analysis.dipole_wizard._skip()      # Skip the dipole_pair.unit_vectors user function.

        # Set up the CSA interaction.
        analysis.value_set_csa()
        uf_store['value.set'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Set up the nuclear isotopes.
        analysis.spin_isotope_heteronuc()
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.
        analysis.spin_isotope_proton()
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Select only the tm0 and tm1 local tm models.
        analysis.local_tm_model_field.select = [True, True, False, False, False, False, False, False, False, False]
        analysis.local_tm_model_field.modify()

        # Select only the m1 and m2 model-free models.
        analysis.mf_model_field.select = [False, True, True, False, False, False, False, False, False, False]
        analysis.mf_model_field.modify()

        # Change the grid increments.
        analysis.grid_inc.SetValue(3)
        analysis.data.diff_tensor_grid_inc = {'sphere': 5, 'prolate': 5, 'oblate': 5, 'ellipsoid': 3}

        # Set the number of Monte Carlo simulations.
        analysis.mc_sim_num.SetValue(2)

        # Set the maximum number of iterations (changing the allowed values).
        analysis.max_iter.control.SetRange(0, 100)
        analysis.max_iter.SetValue(1)

        # Modify some of the class variables to speed up optimisation.
        auto_model_free.dauvergne_protocol.dAuvergne_protocol.opt_func_tol = 1e-5
        auto_model_free.dauvergne_protocol.dAuvergne_protocol.opt_max_iterations = 1000

        # Execute the 'local_tm', 'sphere' and 'final' protocol stages sequentially.
        for protocol in ['local_tm', 'sphere', 'final']:
            # Print out.
            text = "Sequential global model optimisation: %s" % protocol
            char = "%"
            print("\n\n\n\n%s\n%s %s %s\n%s\n\n\n" % (char*(len(text)+4), char, text, char, char*(len(text)+4)))

            # Set the protocol mode.
            if protocol == 'local_tm':
                analysis.mode_win.select_local_tm()
            elif protocol == 'sphere':
                analysis.mode_win.select_sphere()
            else:
                analysis.mode_win.select_final()
            analysis.mode_dialog()

            # Execute relax.
            state = analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

            # Wait for execution to complete.
            if hasattr(analysis, 'thread'):
                analysis.thread.join()

            # Flush all wx events.
            wx.Yield()

            # Exceptions in the thread.
            self.check_exceptions()


    def test_mf_auto_analysis(self):
        """Test the model-free auto-analysis."""

        # Simulate the new analysis wizard.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_mf(None)
        page.analysis_name.SetValue(str_to_gui("Model-free test"))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Model-free test")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # The data path.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep

        # Open and close the about window (mimicking user behaviour).
        analysis._about()
        analysis.about_dialog.Close()

        # Launch the spin viewer window.
        self.app.gui.show_tree()

        # Spin loading wizard:  Initialisation.
        self.app.gui.spin_viewer.load_spins_wizard()

        # Spin loading wizard:  The PDB file.
        page = self.app.gui.spin_viewer.wizard.get_page(0)
        page.selection = 'new pdb'
        self.app.gui.spin_viewer.wizard._go_next()
        page = self.app.gui.spin_viewer.wizard.get_page(self.app.gui.spin_viewer.wizard._current_page)
        page.uf_args['file'].SetValue(str_to_gui(status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep + 'sphere.pdb'))
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Spin loading wizard:  The spin loading.
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Close the spin viewer window.
        self.app.gui.spin_viewer.handler_close()

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

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
            self._execute_uf(uf_name='relax_data.read', file=data_path+data[i][0], ri_id=data[i][1], ri_type=data[i][2], frq=data[i][3], mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # Dipole-dipole interaction wizard:  Initialisation.
        analysis.setup_dipole_pair()

        # Dipole-dipole interaction wizard:  The dipole_pair.define, dipole_pair.set_dist, and dipole_pair.unit_vectors user functions.
        analysis.dipole_wizard._apply()
        interpreter.flush()    # Required because of the asynchronous uf call.
        page = analysis.dipole_wizard.get_page(0)
        page.uf_args['spin_id1'].SetValue(str_to_gui("@NE1"))
        page.uf_args['spin_id2'].SetValue(str_to_gui("@HE1"))
        analysis.dipole_wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.
        analysis.dipole_wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.
        analysis.dipole_wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Set up the CSA interaction.
        analysis.value_set_csa()
        uf_store['value.set'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Set up the nuclear isotopes.
        analysis.spin_isotope_heteronuc()
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.
        analysis.spin_isotope_proton()
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Select only the tm0 and tm1 local tm models.
        analysis.local_tm_model_field.select = [True, True, False, False, False, False, False, False, False, False]
        analysis.local_tm_model_field.modify()

        # Select only the m1 and m2 model-free models.
        analysis.mf_model_field.select = [False, True, True, False, False, False, False, False, False, False]
        analysis.mf_model_field.modify()

        # Change the grid increments.
        analysis.grid_inc.SetValue(3)
        analysis.data.diff_tensor_grid_inc = {'sphere': 5, 'prolate': 5, 'oblate': 5, 'ellipsoid': 3}

        # Set the number of Monte Carlo simulations.
        analysis.mc_sim_num.SetValue(2)

        # Set the maximum number of iterations (changing the allowed values).
        analysis.max_iter.control.SetRange(0, 100)
        analysis.max_iter.SetValue(1)

        # Set the protocol mode to automatic.
        analysis.mode_win.select_full_analysis()
        analysis.mode_dialog()

        # Check that the data has been correctly updated prior to execution.
        analysis.sync_ds(upload=True)
        self.assertEqual(analysis.data.save_dir, ds.tmpdir)
        self.assertEqual(analysis.data.local_tm_models, ['tm0', 'tm1'])
        self.assertEqual(analysis.data.mf_models, ['m1', 'm2'])
        self.assertEqual(analysis.data.grid_inc, 3)
        self.assertEqual(analysis.data.mc_sim_num, 2)
        self.assertEqual(analysis.data.max_iter, 1)
        self.assertEqual(analysis.data.diff_tensor_grid_inc['sphere'], 5)
        self.assertEqual(analysis.data.diff_tensor_grid_inc['prolate'], 5)
        self.assertEqual(analysis.data.diff_tensor_grid_inc['oblate'], 5)
        self.assertEqual(analysis.data.diff_tensor_grid_inc['ellipsoid'], 3)

        # Modify some of the class variables to speed up optimisation.
        auto_model_free.dauvergne_protocol.dAuvergne_protocol.opt_func_tol = 1e-5
        auto_model_free.dauvergne_protocol.dAuvergne_protocol.opt_max_iterations = 1000

        # Execute relax.
        state = analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

        # Wait for execution to complete.
        if hasattr(analysis, 'thread'):
            analysis.thread.join()

        # Flush all wx events.
        wx.Yield()

        # Exceptions in the thread.
        self.check_exceptions()

        # Check the relax controller.
        if status.relax_mode != 'gui':
            self.assertEqual(self.app.gui.controller.mc_gauge_mf.GetValue(), 100)
            self.assertEqual(self.app.gui.controller.progress_gauge_mf.GetValue(), 100)
            self.assertEqual(self.app.gui.controller.main_gauge.GetValue(), 100)

        # Check the diffusion tensor.
        self.assertEqual(cdp.diff_tensor.type, 'sphere')
        self.assertAlmostEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.fixed, True)

        # The global minimisation info.
        self.assertAlmostEqual(cdp.chi2, 4e-19)

        # The spin ID info.
        mol_names = ["sphere_mol1"] * 20
        res_names = ["GLY"] * 20
        res_nums = []
        for i in range(1, 10):
            res_nums.append(i)
            res_nums.append(i)
        res_nums.append(i)
        res_nums.append(i)
        spin_names = ["N", "H"] * 9 + ["NE1", "HE1"]
        spin_nums = list(range(1, 21))
        isotopes = ["15N", "1H"] * 10
        csa = [-172e-6, None] * 10
        select = [True, False] * 10
        fixed = [False, False] * 10
        s2 = [0.8, None] * 10
        te = [20e-12, None] * 10

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
            self.assertEqual(spin.select, select[i])
            self.assertEqual(spin.fixed, fixed[i])
            self.assertEqual(spin.isotope, isotopes[i])
            if csa[i] == None:
                self.assertEqual(spin.csa, None)
            else:
                self.assertAlmostEqual(spin.csa, csa[i])

            # The model-free data.
            self.assertEqual(spin.model, 'm2')
            self.assertEqual(spin.equation, 'mf_orig')
            self.assertEqual(len(spin.params), 2)
            self.assertEqual(spin.params[0], 's2')
            self.assertEqual(spin.params[1], 'te')
            if s2[i] == None:
                self.assertEqual(spin.s2, None)
            else:
                self.assertAlmostEqual(spin.s2, 0.8)
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            self.assertEqual(spin.local_tm, None)
            if te[i] == None:
                self.assertEqual(spin.te, None)
            else:
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

        # Check the interatomic data.
        i = 0
        for interatom in interatomic_loop():
            self.assertAlmostEqual(interatom.r, 1.02 * 1e-10)
