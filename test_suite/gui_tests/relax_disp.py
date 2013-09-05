###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
import wx

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import float_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from pipe_control.mol_res_spin import spin_loop
from pipe_control.pipes import switch
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_IT99, MODEL_LM63, MODEL_NOREX, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_R2EFF, MODEL_TP02
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
            self.assertEqual(spin.intensities['1_0'], data_0[i])
            self.assertEqual(spin.intensities['0_2'], data_2[i])

            # The errors.
            self.assert_(hasattr(spin, 'baseplane_rmsd'))
            self.assertEqual(spin.baseplane_rmsd['0_2'], 3000.0)


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
        file = data_path + 'fake_sequence.in_trunc'
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
            ['500_reference.in',    '500_MHz'+sep+'reference.in_trunc',           None,  500e6],
            ['500_66.667.in',       '500_MHz'+sep+'66.667.in_trunc',           66.6666,  500e6],
            ['500_133.33.in',       '500_MHz'+sep+'133.33.in_trunc',          133.3333,  500e6],
            ['500_133.33.in.bis',   '500_MHz'+sep+'133.33.in.bis_trunc',      133.3333,  500e6],
            ['500_200.in',          '500_MHz'+sep+'200.in_trunc',             200.0000,  500e6],
            ['500_266.67.in',       '500_MHz'+sep+'266.67.in_trunc',          266.6666,  500e6],
            ['500_333.33.in',       '500_MHz'+sep+'333.33.in_trunc',          333.3333,  500e6],
            ['500_400.in',          '500_MHz'+sep+'400.in_trunc',             400.0000,  500e6],
            ['500_466.67.in',       '500_MHz'+sep+'466.67.in_trunc',          466.6666,  500e6],
            ['500_533.33.in',       '500_MHz'+sep+'533.33.in_trunc',          533.3333,  500e6],
            ['500_533.33.in.bis',   '500_MHz'+sep+'533.33.in.bis_trunc',      533.3333,  500e6],
            ['500_600.in',          '500_MHz'+sep+'600.in_trunc',             600.0000,  500e6],
            ['500_666.67.in',       '500_MHz'+sep+'666.67.in_trunc',          666.6666,  500e6],
            ['500_733.33.in',       '500_MHz'+sep+'733.33.in_trunc',          733.3333,  500e6],
            ['500_800.in',          '500_MHz'+sep+'800.in_trunc',             800.0000,  500e6],
            ['500_866.67.in',       '500_MHz'+sep+'866.67.in_trunc',          866.6666,  500e6],
            ['500_933.33.in',       '500_MHz'+sep+'933.33.in_trunc',          933.3333,  500e6],
            ['500_933.33.in.bis',   '500_MHz'+sep+'933.33.in.bis_trunc',      933.3333,  500e6],
            ['500_1000.in',         '500_MHz'+sep+'1000.in_trunc',           1000.0000,  500e6],
            ['800_reference.in',    '800_MHz'+sep+'reference.in_trunc',           None,  800e6],
            ['800_66.667.in',       '800_MHz'+sep+'66.667.in_trunc',           66.6666,  800e6],
            ['800_133.33.in',       '800_MHz'+sep+'133.33.in_trunc',          133.3333,  800e6],
            ['800_133.33.in.bis',   '800_MHz'+sep+'133.33.in.bis_trunc',      133.3333,  800e6],
            ['800_200.in',          '800_MHz'+sep+'200.in_trunc',             200.0000,  800e6],
            ['800_266.67.in',       '800_MHz'+sep+'266.67.in_trunc',          266.6666,  800e6],
            ['800_333.33.in',       '800_MHz'+sep+'333.33.in_trunc',          333.3333,  800e6],
            ['800_400.in',          '800_MHz'+sep+'400.in_trunc',             400.0000,  800e6],
            ['800_466.67.in',       '800_MHz'+sep+'466.67.in_trunc',          466.6666,  800e6],
            ['800_533.33.in',       '800_MHz'+sep+'533.33.in_trunc',          533.3333,  800e6],
            ['800_533.33.in.bis',   '800_MHz'+sep+'533.33.in.bis_trunc',      533.3333,  800e6],
            ['800_600.in',          '800_MHz'+sep+'600.in_trunc',             600.0000,  800e6],
            ['800_666.67.in',       '800_MHz'+sep+'666.67.in_trunc',          666.6666,  800e6],
            ['800_733.33.in',       '800_MHz'+sep+'733.33.in_trunc',          733.3333,  800e6],
            ['800_800.in',          '800_MHz'+sep+'800.in_trunc',             800.0000,  800e6],
            ['800_866.67.in',       '800_MHz'+sep+'866.67.in_trunc',          866.6666,  800e6],
            ['800_933.33.in',       '800_MHz'+sep+'933.33.in_trunc',          933.3333,  800e6],
            ['800_933.33.in.bis',   '800_MHz'+sep+'933.33.in.bis_trunc',      933.3333,  800e6],
            ['800_1000.in',         '800_MHz'+sep+'1000.in_trunc',           1000.0000,  800e6]
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
        page = wizard.get_page(wizard.page_indices['name'])
        page.uf_args['name'].SetValue(str_to_gui("N"))
        page.uf_args['force'].SetValue(True)
        wizard._go_next(None)

        # The spectrum.
        page = wizard.get_page(wizard.page_indices['read'])
        for id, file, cpmg_frq, H_frq in data:
            page.uf_args['file'].SetValue(str_to_gui("%s%s" % (data_path, file)))
            page.uf_args['spectrum_id'].SetValue(str_to_gui(id))
            page.uf_args['int_method'].SetValue(str_to_gui('height'))
            wizard._apply(None)
        wizard._skip(None)

        # The error type.
        page = wizard.get_page(wizard.page_indices['err_type'])
        page.selection = 'repl'
        wizard._go_next(None)

        # Replicated spectra:
        page = wizard.get_page(wizard.page_indices['repl'])
        for id1, id2 in replicated:
            page.uf_args['spectrum_ids'].SetValue(value=id1, index=0)
            page.uf_args['spectrum_ids'].SetValue(value=id2, index=1)
            wizard._apply(None)
        wizard._skip(None)

        # Set the experiment types.
        for id, file, cpmg_frq, H_frq in data:
            wizard.setup_page(page='exp_type', spectrum_id=id, exp_type='cpmg fixed')
            wizard._apply(None)
        wizard._skip(None)

        # Set the spectrometer frequencies.
        page = wizard.get_page(wizard.page_indices['spectrometer_frequency'])
        for id, file, cpmg_frq, H_frq in data:
            page.uf_args['id'].SetValue(str_to_gui(id))
            page.uf_args['frq'].SetValue(float_to_gui(H_frq))
            wizard._apply(None)
        wizard._skip(None)

        # Set the relaxation time.
        page = wizard.get_page(wizard.page_indices['relax_time'])
        for id, file, cpmg_frq, H_frq in data:
            page.uf_args['spectrum_id'].SetValue(str_to_gui(id))
            page.uf_args['time'].SetValue(float_to_gui(0.03))
            wizard._apply(None)
        wizard._skip(None)

        # Set the CPMG frequencies.
        page = wizard.get_page(wizard.page_indices['cpmg_frq'])
        for id, file, cpmg_frq, H_frq in data:
            page.uf_args['spectrum_id'].SetValue(str_to_gui(id))
            page.uf_args['cpmg_frq'].SetValue(float_to_gui(cpmg_frq))
            wizard._apply(None)
        wizard._skip(None)
        wizard._go_next(None)    # Terminate the wizard.

        # Set up the models to use.
        models = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_CR72, MODEL_IT99, MODEL_NS_CPMG_2SITE_EXPANDED]
        for i in range(len(analysis.model_field.models)):
            if analysis.model_field.models[i] in models:
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
            wizard.setup_page(page='exp_type', spectrum_id=id, exp_type='r1rho fixed')
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

        # Deselect all but the 'TP02' model.
        models = [MODEL_R2EFF, MODEL_NOREX, MODEL_TP02]
        for i in range(len(analysis.model_field.models)):
            if analysis.model_field.models[i] in models:
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

        # Switch to the 'TP02' model data pipe, then check for each spin.
        switch('TP02')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[0]/10, r1rho_prime[spin_index][0]/10, 4)
            self.assertAlmostEqual(spin.r2[1]/10, r1rho_prime[spin_index][1]/10, 4)
            self.assertAlmostEqual(spin.dw, delta_omega[spin_index], 3)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 3)

            # Increment the spin index.
            spin_index += 1
