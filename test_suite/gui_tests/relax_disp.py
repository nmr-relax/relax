###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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
"""GUI tests for the relaxation dispersion analyses."""

# Python module imports.
from os import sep
import math
import wx

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import float_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from pipe_control.mol_res_spin import spin_loop
from pipe_control.pipes import switch
from specific_analyses.relax_disp.data import generate_r20_key
from specific_analyses.relax_disp.variables import EXP_TYPE_R1RHO, MODEL_CR72, MODEL_IT99, MODEL_LM63, MODEL_NOREX, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_R2EFF, MODEL_TP02
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase


class Relax_disp(GuiTestCase):
    """GUI test case class for testing various aspects of the relaxation dispersion analyses."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the C modules are non-functional or for wxPython bugs.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Relax_disp, self).__init__(methodName)

        # Missing module.
        if not dep_check.C_module_exp_fn:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Relax curve-fitting C module', self._skip_type])


    def test_bug_20889_multi_col_peak_list(self):
        """Test catching U{bug #20889<https://gna.org/bugs/?20889>}, the custom peak intensity reading with a list of spectrum_ids submitted by Troels E. Linnet."""

        # The path to the files.
        path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep

        # Simulate the new analysis wizard, selecting the fixed time CPMG experiment.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        file = path + 'test.seq'
        self._execute_uf(uf_name='sequence.read', file=file, mol_name_col=1, res_name_col=3, res_num_col=2, spin_name_col=5, spin_num_col=4)

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # Set up the nuclear isotopes.
        analysis.spin_isotope()
        uf_store['spin.isotope'].page.SetValue('spin_id', '')
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Set up the peak intensity wizard.
        analysis.peak_wizard_launch(None)
        wizard = analysis.peak_wizard

        # The spectrum.
        page = wizard.get_page(wizard.page_indices['read'])
        page.uf_args['file'].SetValue(str_to_gui("%stest.seq" % path))
        page.uf_args['spectrum_id'].SetValue(['0_2', '1_0'])
        page.uf_args['int_col'].SetValue([6, 7])
        wizard._go_next(None)

        # The error type.
        page = wizard.get_page(wizard.page_indices['err_type'])
        page.selection = 'rmsd'
        wizard._go_next(None)

        # Set the RMSD.
        page = wizard.get_page(wizard.page_indices['rmsd'])
        page.uf_args['error'].SetValue(float_to_gui(3000.0))
        wizard._ok(None)

        # The peak intensities.
        data_2 = [337765.90000000002, 1697771.0, 867389.80000000005, 2339480.0, 2574062.0, 1609356.0, 2179341.0, 1563795.0, 1535896.0, 3578841.0]
        data_0 = [636244.59999999998, 3015788.0, 1726064.0, 4039142.0, 4313824.0, 2927111.0, 4067343.0, 2921316.0, 3005234.0, 6352595.0]

        # Data checks.
        for i in range(len(cdp.mol[0].res)):
            # Alias the spin.
            spin = cdp.mol[0].res[i].spin[0]

            # The intensities.
            self.assertEqual(spin.peak_intensity['1_0'], data_0[i])
            self.assertEqual(spin.peak_intensity['0_2'], data_2[i])

            # The errors.
            self.assert_(hasattr(spin, 'baseplane_rmsd'))
            self.assertEqual(spin.baseplane_rmsd['0_2'], 3000.0)


    def test_bug_21076_multi_col_peak_list(self):
        """Test catching U{bug #21076<https://gna.org/bugs/?21076>}, loading a multi-spectra NMRPipe seriesTab file through the GUI, Error messages occur."""

        # The paths to the data files.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'dispersion' + sep + 'KTeilum_FMPoulsen_MAkke_2006' + sep + 'acbp_cpmg_disp_101MGuHCl_40C_041223' + sep

        # Simulate the new analysis wizard, selecting the fixed time CPMG experiment.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        file = data_path + 'relax_2_spins_trunc.py'
        self._execute_uf(uf_name='script', file=file, dir=None)

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # Set up the nuclear isotopes.
        analysis.spin_isotope()
        uf_store['spin.isotope'].page.SetValue('spin_id', '')
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Set up the peak intensity wizard.
        analysis.peak_wizard_launch(None)
        wizard = analysis.peak_wizard

        # The spectrum, where the use of Keyword auto will auto-assign spectra Z_A{i}.
        page = wizard.get_page(wizard.page_indices['read'])
        page.uf_args['file'].SetValue(str_to_gui("%sfolded_sparky_corr_final_max_standard_trunc.ser" % data_path))
        page.uf_args['spectrum_id'].SetValue('auto')
        wizard._go_next(None)

        # The error type window.
        page = wizard.get_page(wizard.page_indices['err_type'])
        page.selection = 'rmsd'
        wizard._go_next(None)

        # Get ID from RMSD window.
        page = wizard.get_page(wizard.page_indices['rmsd'])

        # Flush all wx events (to allow the spectrum list GUI element to populate all its rows).
        wx.Yield()

        # Get the first ID from list.
        cur_id = page.uf_args['spectrum_id'].GetValue()

        # Now check that the first is set to 'Z_A0', since the keyword 'auto' was used for spectrum_id.
        self.assertEqual(cur_id, 'Z_A0')

        # Finally close the wizard to allow subsequent tests to be able to operate cleanly.
        wizard.Close()


    def test_bug_22501_close_all_analyses(self):
        """Test catching U{bug #22501<https://gna.org/bugs/index.php?22501>}, 'Close all analyses' raises error."""

        # Simulate the new analysis wizard, selecting the fixed time CPMG experiment.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Closure.
        self.app.gui.analysis.delete_analysis(0)


    def test_hansen_trunc_data(self):
        """Test the GUI analysis with Flemming Hansen's CPMG data truncated to residues 70 and 71."""

        # The paths to the data files.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'dispersion' + sep + 'Hansen' + sep
        data_path_500 = data_path + sep + '500_MHz' + sep
        data_path_800 = data_path + sep + '800_MHz' + sep

        # Simulate the new analysis wizard, selecting the fixed time CPMG experiment.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        file = data_path + 'fake_sequence.in'
        self._execute_uf(uf_name='sequence.read', file=file, mol_name_col=None, res_num_col=1, res_name_col=2, spin_name_col=None, spin_num_col=None)

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # Set up the nuclear isotopes.
        analysis.spin_isotope()
        uf_store['spin.isotope'].page.SetValue('spin_id', '')
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # The spectral data - spectrum ID, peak list file name, CPMG frequency (Hz), spectrometer frequency in Hertz.
        data = [
            ['500_reference.in',    '500_MHz'+sep+'reference.in',           None,  500e6],
            ['500_66.667.in',       '500_MHz'+sep+'66.667.in',           66.6666,  500e6],
            ['500_133.33.in',       '500_MHz'+sep+'133.33.in',          133.3333,  500e6],
            ['500_133.33.in.bis',   '500_MHz'+sep+'133.33.in.bis',      133.3333,  500e6],
            ['500_200.in',          '500_MHz'+sep+'200.in',             200.0000,  500e6],
            ['500_266.67.in',       '500_MHz'+sep+'266.67.in',          266.6666,  500e6],
            ['500_333.33.in',       '500_MHz'+sep+'333.33.in',          333.3333,  500e6],
            ['500_400.in',          '500_MHz'+sep+'400.in',             400.0000,  500e6],
            ['500_466.67.in',       '500_MHz'+sep+'466.67.in',          466.6666,  500e6],
            ['500_533.33.in',       '500_MHz'+sep+'533.33.in',          533.3333,  500e6],
            ['500_533.33.in.bis',   '500_MHz'+sep+'533.33.in.bis',      533.3333,  500e6],
            ['500_600.in',          '500_MHz'+sep+'600.in',             600.0000,  500e6],
            ['500_666.67.in',       '500_MHz'+sep+'666.67.in',          666.6666,  500e6],
            ['500_733.33.in',       '500_MHz'+sep+'733.33.in',          733.3333,  500e6],
            ['500_800.in',          '500_MHz'+sep+'800.in',             800.0000,  500e6],
            ['500_866.67.in',       '500_MHz'+sep+'866.67.in',          866.6666,  500e6],
            ['500_933.33.in',       '500_MHz'+sep+'933.33.in',          933.3333,  500e6],
            ['500_933.33.in.bis',   '500_MHz'+sep+'933.33.in.bis',      933.3333,  500e6],
            ['500_1000.in',         '500_MHz'+sep+'1000.in',           1000.0000,  500e6],
            ['800_reference.in',    '800_MHz'+sep+'reference.in',           None,  800e6],
            ['800_66.667.in',       '800_MHz'+sep+'66.667.in',           66.6666,  800e6],
            ['800_133.33.in',       '800_MHz'+sep+'133.33.in',          133.3333,  800e6],
            ['800_133.33.in.bis',   '800_MHz'+sep+'133.33.in.bis',      133.3333,  800e6],
            ['800_200.in',          '800_MHz'+sep+'200.in',             200.0000,  800e6],
            ['800_266.67.in',       '800_MHz'+sep+'266.67.in',          266.6666,  800e6],
            ['800_333.33.in',       '800_MHz'+sep+'333.33.in',          333.3333,  800e6],
            ['800_400.in',          '800_MHz'+sep+'400.in',             400.0000,  800e6],
            ['800_466.67.in',       '800_MHz'+sep+'466.67.in',          466.6666,  800e6],
            ['800_533.33.in',       '800_MHz'+sep+'533.33.in',          533.3333,  800e6],
            ['800_533.33.in.bis',   '800_MHz'+sep+'533.33.in.bis',      533.3333,  800e6],
            ['800_600.in',          '800_MHz'+sep+'600.in',             600.0000,  800e6],
            ['800_666.67.in',       '800_MHz'+sep+'666.67.in',          666.6666,  800e6],
            ['800_733.33.in',       '800_MHz'+sep+'733.33.in',          733.3333,  800e6],
            ['800_800.in',          '800_MHz'+sep+'800.in',             800.0000,  800e6],
            ['800_866.67.in',       '800_MHz'+sep+'866.67.in',          866.6666,  800e6],
            ['800_933.33.in',       '800_MHz'+sep+'933.33.in',          933.3333,  800e6],
            ['800_933.33.in.bis',   '800_MHz'+sep+'933.33.in.bis',      933.3333,  800e6],
            ['800_1000.in',         '800_MHz'+sep+'1000.in',           1000.0000,  800e6]
        ]

        # Replicated spectra.
        replicated = [
            ['500_133.33.in', '500_133.33.in.bis'],
            ['500_533.33.in', '500_533.33.in.bis'],
            ['500_933.33.in', '500_933.33.in.bis'],
            ['800_133.33.in', '800_133.33.in.bis'],
            ['800_533.33.in', '800_533.33.in.bis'],
            ['800_933.33.in', '800_933.33.in.bis']
        ]

        # Set up the peak intensity wizard.
        analysis.peak_wizard_launch(None)
        wizard = analysis.peak_wizard

        # Spin naming.
        wizard.setup_page(page='name', name="N", force=True)
        wizard._go_next(None)

        # The spectrum.
        for id, file, cpmg_frq, H_frq in data:
            wizard.setup_page(page='read', file=data_path+file, spectrum_id=id, int_method='height', int_col=2, mol_name_col=None, res_num_col=1, res_name_col=None, spin_num_col=None, spin_name_col=None)
            wizard._apply(None)
        wizard._skip(None)

        # The error type.
        page = wizard.get_page(wizard.page_indices['err_type'])
        page.selection = 'repl'
        wizard._go_next(None)

        # Replicated spectra:
        for id1, id2 in replicated:
            wizard.setup_page(page='repl', spectrum_ids=[id1, id2])
            wizard._apply(None)
        wizard._skip(None)

        # Set the experiment types.
        for id, file, cpmg_frq, H_frq in data:
            wizard.setup_page(page='exp_type', spectrum_id=id, exp_type='SQ CPMG')
            wizard._apply(None)
        wizard._skip(None)

        # Set the spectrometer frequencies.
        for id, file, cpmg_frq, H_frq in data:
            wizard.setup_page(page='spectrometer_frequency', id=id, frq=H_frq)
            wizard._apply(None)
        wizard._skip(None)

        # Set the relaxation time.
        for id, file, cpmg_frq, H_frq in data:
            wizard.setup_page(page='relax_time', spectrum_id=id, time=0.03)
            wizard._apply(None)
        wizard._skip(None)

        # Set the CPMG frequencies.
        for id, file, cpmg_frq, H_frq in data:
            wizard.setup_page(page='cpmg_setup', spectrum_id=id, cpmg_frq=cpmg_frq)
            wizard._apply(None)
        wizard._skip(None)

        # Flush all wx events (to allow the spectrum list GUI element to populate all its rows).
        wx.Yield()

        # Simulate right clicking in the spectrum list element to test the popup menu.
        analysis.peak_intensity.on_right_click(Fake_right_click())

        # Simulate the popup menu entries to catch bugs there (just apply the user functions with the currently set values).
        # FIXME: skipping the checks for certain wxPython bugs.
        if status.relax_mode != 'gui' and wx.version() != '2.9.4.1 gtk2 (classic)':
            analysis.peak_intensity.action_relax_disp_cpmg_setup(item=4)
            uf_store['relax_disp.cpmg_setup'].wizard._go_next()
            interpreter.flush()
            analysis.peak_intensity.action_relax_disp_exp_type(item=5)
            uf_store['relax_disp.exp_type'].wizard._go_next()
            interpreter.flush()
            analysis.peak_intensity.action_relax_disp_relax_time(item=0)
            uf_store['relax_disp.relax_time'].wizard._go_next()
            interpreter.flush()
            analysis.peak_intensity.action_spectrometer_frq(item=10)
            uf_store['spectrometer.frequency'].wizard._go_next()
            interpreter.flush()

        # Set up the models to use.
        models = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_CR72, MODEL_IT99, MODEL_NS_CPMG_2SITE_EXPANDED]
        for i in range(len(analysis.model_field.models_stripped)):
            if analysis.model_field.models_stripped[i] in models:
                analysis.model_field.select[i] = True
            else:
                analysis.model_field.select[i] = False
        analysis.model_field.modify()

        # Set the grid search size and number of MC sims.
        analysis.grid_inc.SetValue(4)
        analysis.mc_sim_num.SetValue(3)

        # Optimisation speedups.
        analysis.opt_func_tol = 1e-5
        analysis.opt_max_iterations = 1000

        subset_500 = ['500_reference.in', '500_66.667.in', '500_133.33.in', '500_133.33.in.bis', '500_200.in', '500_266.67.in', '500_333.33.in', '500_400.in', '500_466.67.in', '500_533.33.in', '500_533.33.in.bis', '500_600.in', '500_666.67.in', '500_733.33.in', '500_800.in', '500_866.67.in', '500_933.33.in', '500_933.33.in.bis', '500_1000.in']
        subset_800 = ['800_reference.in', '800_66.667.in', '800_133.33.in', '800_133.33.in.bis', '800_200.in', '800_266.67.in', '800_333.33.in', '800_400.in', '800_466.67.in', '800_533.33.in', '800_533.33.in.bis', '800_600.in', '800_666.67.in', '800_733.33.in', '800_800.in', '800_866.67.in', '800_933.33.in', '800_933.33.in.bis', '800_1000.in']

        # Perform the error analysis.
        self._execute_uf(uf_name='spectrum.error_analysis', subset=subset_500)
        self._execute_uf(uf_name='spectrum.error_analysis', subset=subset_800)

        # Do check of std calculation for 500 MHz
        sum_var_500 = 0.0
        for id_500 in subset_500:
            sum_var_500 += cdp.var_I[id_500]

        # Calculate std
        std_500 = math.sqrt((sum_var_500)/len(subset_500))

        print("Manually calculated standard deviation for 500 MHz: %f"%std_500)
        for id_500 in subset_500:
            self.assertAlmostEqual(cdp.sigma_I[id_500], std_500)

        # Do check of std calculation for 800 MHz
        sum_var_800 = 0.0
        for id_800 in subset_800:
            sum_var_800 += cdp.var_I[id_800]

        # Calculate std
        std_800 = math.sqrt((sum_var_800)/len(subset_800))

        print("Manually calculated standard deviation for 800 MHz: %f"%std_800)
        for id_800 in subset_800:
            self.assertAlmostEqual(cdp.sigma_I[id_800], std_800)

        # Delete all residues but :4, :70 and :71.
        for i in range(1, 100):
            if i in [4, 70, 71]:
                continue
            self._execute_uf(uf_name='residue.delete', res_id=":%s" % i)

        # Execute relax.
        analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

        # Wait for execution to complete.
        analysis.thread.join()

        # Flush all wx events.
        wx.Yield()

        # Exceptions in the thread.
        self.check_exceptions()

        # Check the relax controller.
        # FIXME: skipping the checks for certain wxPython bugs.
        if status.relax_mode != 'gui' and wx.version() != '2.9.4.1 gtk2 (classic)':
            self.assertEqual(self.app.gui.controller.mc_gauge_rx.GetValue(), 100)
            self.assertEqual(self.app.gui.controller.main_gauge.GetValue(), 100)


    def test_read_spins_from_spectrum(self):
        """Test the GUI load spins from a spectrum formatted file."""

        # The path to the files.
        path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep

        # Simulate the dispersion analysis wizard.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Launch the spin viewer window.
        self.app.gui.show_tree()

        # Spin loading wizard:  Initialisation.
        self.app.gui.spin_viewer.load_spins_wizard()

        # Spin loading wizard:  The spectrum.read_spins page.
        page = self.app.gui.spin_viewer.wizard.get_page(0)
        page.selection = 'new spectrum'
        self.app.gui.spin_viewer.wizard._go_next()
        page = self.app.gui.spin_viewer.wizard.get_page(self.app.gui.spin_viewer.wizard._current_page)
        page.uf_args['file'].SetValue(str_to_gui(path + 'seriesTab.ser'))
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Spin loading wizard:  The spin loading.
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Close the spin viewer window.
        self.app.gui.spin_viewer.handler_close()

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, None)
        self.assertEqual(len(cdp.mol[0].res), 3)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 62)
        self.assertEqual(cdp.mol[0].res[0].name, 'W')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'NE1')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 10)
        self.assertEqual(cdp.mol[0].res[1].name, 'L')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 6)
        self.assertEqual(cdp.mol[0].res[2].name, 'V')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 1)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')


    def test_r2eff_err_estimate(self):
        """Test U{task #7822:<https://gna.org/task/?7822>}, Implement user function to estimate R2eff and associated errors for exponential curve fitting.."""

        # The paths to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'+sep

        # Simulate the new analysis wizard, selecting the fixed time CPMG experiment.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        file = data_path + '1_setup_r1rho_GUI.py'
        self._execute_uf(uf_name='script', file=file, dir=None)

        # De select spins
        self._execute_uf(uf_name='deselect.spin', spin_id=":1-100")
        self._execute_uf(uf_name='select.spin', spin_id=":52@N")

        # Deselect all but the 'TP02' model.
        models = [MODEL_R2EFF, MODEL_NOREX]
        for i in range(len(analysis.model_field.models_stripped)):
            if analysis.model_field.models_stripped[i] in models:
                analysis.model_field.select[i] = True
            else:
                analysis.model_field.select[i] = False
        analysis.model_field.modify()

        # Set the grid search size and number of MC sims.
        analysis.grid_inc.SetValue(0)
        analysis.mc_sim_num.SetValue(3)
        analysis.exp_mc_sim_num.SetValue(-1)

        # Execute relax.
        analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

        # Wait for execution to complete.
        analysis.thread.join()

        # Flush all wx events.
        wx.Yield()

        # Exceptions in the thread.
        self.check_exceptions()


    def test_tp02_data_to_tp02(self):
        """Test the GUI analysis with the relaxation dispersion 'TP02' model fitting to the 'TP02' synthetic data."""

        # The paths to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_off_res_tp02'+sep

        # Simulate the new analysis wizard, selecting the fixed time CPMG experiment.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_disp(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle, uf_exec=uf_exec)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Relaxation dispersion")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Create the sequence data.
        self._execute_uf(uf_name='spin.create', res_name='Trp', res_num=1, spin_name='N')
        interpreter.flush()
        self._execute_uf(uf_name='spin.create', res_name='Trp', res_num=2, spin_name='N')
        interpreter.flush()
        self._execute_uf(uf_name='sequence.display')
        interpreter.flush()

        # Set up the nuclear isotopes.
        analysis.spin_isotope()
        uf_store['spin.isotope'].page.SetValue('spin_id', '')
        uf_store['spin.isotope'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Load the chemical shift data.
        self._execute_uf(uf_name='chemical_shift.read', file='ref_500MHz.list', dir=data_path)
        interpreter.flush()

        # The spectral data.
        frq = [500, 800]
        frq_label = ['500MHz', '800MHz']
        error = 200000.0
        data = []
        spin_lock = [None, 1000.0, 1500.0, 2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4500.0, 5000.0, 5500.0, 6000.0]
        for frq_index in range(len(frq)):
            for spin_lock_index in range(len(spin_lock)):
                # The reference.
                if spin_lock[spin_lock_index] == None:
                    id = 'ref_%s' % frq_label[frq_index]
                    file = "ref_%s.list" % frq_label[frq_index]

                # Normal data.
                else:
                    id = "nu_%s_%s" % (spin_lock[spin_lock_index], frq_label[frq_index])
                    file = "nu_%s_%s.list" % (spin_lock[spin_lock_index], frq_label[frq_index])

                # Append the data.
                data.append([id, file, spin_lock[spin_lock_index], frq[frq_index]])

        # Load the R1 data.
        for frq_index in range(len(frq)):
            label = 'R1_%s' % frq_label[frq_index]
            self._execute_uf(uf_name='relax_data.read', ri_id=label, ri_type='R1', frq=frq[frq_index]*1e6, file='%s.out'%label, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
            interpreter.flush()

        # Set up the peak intensity wizard.
        analysis.peak_wizard_launch(None)
        wizard = analysis.peak_wizard

        # The spectra.
        for id, file, field, H_frq in data:
            wizard.setup_page(page='read', file=data_path+file, spectrum_id=id, int_method='height', dim=1)
            wizard._apply(None)
        wizard._skip(None)

        # The error type.
        page = wizard.get_page(wizard.page_indices['err_type'])
        page.selection = 'rmsd'
        wizard._go_next(None)

        # Baseplane RMSD.
        for id, file, field, H_frq in data:
            wizard.setup_page(page='rmsd', spectrum_id=id, error=error)
            wizard._apply(None)
        wizard._skip(None)

        # The experiment type.
        for id, file, field, H_frq in data:
            wizard.setup_page(page='exp_type', spectrum_id=id, exp_type='R1rho')
            wizard._apply(None)
        wizard._skip(None)

        # Set the spectrometer frequency.
        for id, file, field, H_frq in data:
            wizard.setup_page(page='spectrometer_frequency', id=id, frq=H_frq, units='MHz')
            wizard._apply(None)
        wizard._skip(None)

        # Set the relaxation times.
        for id, file, field, H_frq in data:
            wizard.setup_page(page='relax_time', spectrum_id=id, time=0.1)
            wizard._apply(None)
        wizard._skip(None)

        # Set the relaxation dispersion spin-lock field strength (nu1).
        for id, file, field, H_frq in data:
            wizard.setup_page(page='spin_lock_field', spectrum_id=id, field=field)
            wizard._apply(None)
        wizard._skip(None)

        # Set the spin-lock offset.
        for id, file, field, H_frq in data:
            wizard.setup_page(page='spin_lock_offset', spectrum_id=id, offset=110.0)
            wizard._apply(None)
        wizard._skip(None)

        # Flush all wx events (to allow the spectrum list GUI element to populate all its rows).
        wx.Yield()

        # Simulate right clicking in the spectrum list element to test the popup menu.
        analysis.peak_intensity.on_right_click(Fake_right_click())

        # Simulate the popup menu entries to catch bugs there (just apply the user functions with the currently set values).
        # FIXME: skipping the checks for certain wxPython bugs.
        if status.relax_mode != 'gui' and wx.version() != '2.9.4.1 gtk2 (classic)':
            analysis.peak_intensity.action_relax_disp_spin_lock_field(item=4)
            uf_store['relax_disp.spin_lock_field'].wizard._go_next()
            interpreter.flush()
            analysis.peak_intensity.action_relax_disp_exp_type(item=5)
            uf_store['relax_disp.exp_type'].wizard._go_next()
            interpreter.flush()
            analysis.peak_intensity.action_relax_disp_relax_time(item=0)
            uf_store['relax_disp.relax_time'].wizard._go_next()
            interpreter.flush()
            analysis.peak_intensity.action_spectrometer_frq(item=10)
            uf_store['spectrometer.frequency'].wizard._go_next()
            interpreter.flush()

        # Deselect all but the 'TP02' model.
        models = [MODEL_R2EFF, MODEL_NOREX, MODEL_TP02]
        for i in range(len(analysis.model_field.models_stripped)):
            if analysis.model_field.models_stripped[i] in models:
                analysis.model_field.select[i] = True
            else:
                analysis.model_field.select[i] = False
        analysis.model_field.modify()

        # Set the grid search size and number of MC sims.
        analysis.grid_inc.SetValue(4)
        analysis.mc_sim_num.SetValue(3)

        # Optimisation speedups.
        analysis.opt_func_tol = 1e-10
        analysis.opt_max_iterations = 10000

        # Execute relax.
        analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

        # Wait for execution to complete.
        analysis.thread.join()

        # Flush all wx events.
        wx.Yield()

        # Exceptions in the thread.
        self.check_exceptions()

        # Check the relax controller.
        # FIXME: skipping the checks for certain wxPython bugs.
        if status.relax_mode != 'gui' and wx.version() != '2.9.4.1 gtk2 (classic)':
            self.assertEqual(self.app.gui.controller.mc_gauge_rx.GetValue(), 100)
            self.assertEqual(self.app.gui.controller.main_gauge.GetValue(), 100)

        # The original parameters.
        r1rho_prime = [[10.0, 15.0], [12.0, 18.0]]
        pA = 0.7654321
        kex = 1234.56789
        delta_omega = [7.0, 9.0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Switch to the 'TP02' model data pipe, then check for each spin.
        switch("%s - %s" % ('TP02', pipe_bundle))
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index][0]/10, 4)
            self.assertAlmostEqual(spin.r2[r20_key2]/10, r1rho_prime[spin_index][1]/10, 4)
            self.assertAlmostEqual(spin.dw, delta_omega[spin_index], 3)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 3)

            # Increment the spin index.
            spin_index += 1



class Fake_right_click:
    """Simulate a grid_cell_right_click event ."""

    def GetPosition(self):
        """Overwrite the GetPosition() method."""

        # Return roughly the position of the forth row.
        return wx.Point(10, 65)
