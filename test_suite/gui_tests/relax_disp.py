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
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        page.uf_args['exp_type'].SetValue(str_to_gui('cpmg fixed'))
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
        page.uf_args['heteronuc'].SetValue(str_to_gui('N'))
        page.uf_args['proton'].SetValue(str_to_gui('HN'))
        page.uf_args['int_col'].SetValue([6, 7])
        wizard._go_next(None)

        # The error type.
        page = wizard.get_page(wizard.page_indices['err_type'])
        page.selection = 'rmsd'
        wizard._go_next(None)

        # Set the RMSD.
        page = wizard.get_page(wizard.page_indices['rmsd'])
        page.uf_args['error'].SetValue(float_to_gui(3000.0))
        wizard._go_next(None)

        # The peak intensities.
        data_2 = [337765.90000000002, 1697771.0, 867389.80000000005, 2339480.0, 2574062.0, 1609356.0, 2179341.0, 1563795.0, 1535896.0, 3578841.0]
        data_0 = [636244.59999999998, 3015788.0, 1726064.0, 4039142.0, 4313824.0, 2927111.0, 4067343.0, 2921316.0, 3005234.0, 6352595.0]

        # Data checks.
        for i in range(len(cdp.mol[0].res)):
            # Alias the spin.
            spin = cdp.mol[0].res[i].spin[0]
            print spin

            # The intensities.
            self.assertEqual(spin.intensities['1_0'], data_0[i])
            self.assertEqual(spin.intensities['0_2'], data_2[i])

            # The errors.
            self.assert_(hasattr(spin, 'intensity_err'))
            self.assertEqual(spin.intensity_err['1_0'], 3000.0)
            self.assertEqual(spin.intensity_err['0_2'], 3000.0)


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
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        page.uf_args['exp_type'].SetValue(str_to_gui('cpmg fixed'))
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

        # Deselect the 'CR72' model.
        analysis.model_field.select[2] = False
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
