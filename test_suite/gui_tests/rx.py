###############################################################################
#                                                                             #
# Copyright (C) 2006-2008,2011-2013,2024 Edward d'Auvergne                    #
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
from os import F_OK, access, sep
import wx

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import float_to_gui, float_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from pipe_control.mol_res_spin import spin_loop
from pipe_control.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase


class Rx(GuiTestCase):
    """Class for testing various aspects specific to the R1 and R2 analyses."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the C modules are non-functional or for wxPython bugs.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Rx, self).__init__(methodName)

        # Missing module.
        if not dep_check.C_module_exp_fn:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Relax curve-fitting C module', self._skip_type])


    def check_curve_fitting(self):
        """Check the results of the curve-fitting."""

        # Data.
        relax_times = [0.0176, 0.0176, 0.0352, 0.0704, 0.0704, 0.1056, 0.1584, 0.1584, 0.1936, 0.1936]
        chi2 = [None, None, None, 2.916952651567855, 5.4916923952919632, 16.21182245065274, 4.3591263759462926, 9.8925377583244316, None, None, None, 6.0238341559877782]
        rx = [None, None, None, 8.0814894819820662, 8.6478971039559642, 9.5710638183013845, 10.716551838066295, 11.143793935455122, None, None, None, 12.82875370075309]
        i0 = [None, None, None, 1996050.9679875025, 2068490.9458927638, 1611556.5194095275, 1362887.2331948928, 1877670.5623875158, None, None, None, 897044.17382064369]

        # Some checks.
        self.assertEqual(cdp.curve_type, 'exp')
        self.assertEqual(cdp.int_method, 'height')
        self.assertEqual(len(cdp.relax_times), 10)
        cdp_relax_times = sorted(cdp.relax_times.values())
        for i in range(10):
            self.assertAlmostEqual(cdp_relax_times[i], relax_times[i])

        # Check the errors.
        for key in cdp.sigma_I:
            self.assertAlmostEqual(cdp.sigma_I[key], 10578.039482421433)
            self.assertAlmostEqual(cdp.var_I[key], 111894919.29166669)

        # Spin data check.
        i = 0
        for spin in spin_loop():
            # No data present.
            if chi2[i] == None:
                self.assertTrue(not hasattr(spin, 'chi2'))

            # Data present.
            else:
                self.assertAlmostEqual(spin.chi2, chi2[i])
                self.assertAlmostEqual(spin.rx, rx[i])
                self.assertAlmostEqual(spin.i0/1e6, i0[i]/1e6)

            # Increment the spin index.
            i = i + 1
            if i >= 12:
                break


    def test_r1_analysis(self):
        """Test the r1 analysis."""

        # The path to the data files.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'curve_fitting' + sep

        # Simulate the new analysis wizard.
        analysis = self.new_analysis_wizard(analysis_type='r1')

        # The frequency label.
        analysis.field_nmr_frq.SetValue(str_to_gui('600'))

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'Ap4Aase.seq'
        self._execute_uf(uf_name='sequence.read', file=file, mol_name_col=None, res_name_col=2, res_num_col=1, spin_name_col=None, spin_num_col=None)

        # Unresolved spins.
        self._execute_uf(uf_name='deselect.read', file=data_path+'unresolved', mol_name_col=None, res_name_col=None, res_num_col=1, spin_name_col=None, spin_num_col=None, change_all=True)

        # Name the spins.
        self._execute_uf(uf_name='spin.name', name='N')

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

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

        # Replicated spectra.
        replicated = {
            'T2_ncyc1b_ave': 'T2_ncyc1_ave',
            'T2_ncyc4b_ave': 'T2_ncyc4_ave',
            'T2_ncyc9b_ave': 'T2_ncyc9_ave',
            'T2_ncyc11b_ave': 'T2_ncyc11_ave'
        }

        # Number of cycles.
        ncyc = [1,
                1,
                2,
                4,
                4,
                6,
                9,
                9,
                11,
                11
        ]

        # The delay time.
        time = 0.0176

        # Add the spectra and number of cycles.
        for i in range(len(names)):
            # Set up the peak intensity wizard.
            analysis.peak_wizard_launch(None)
            wizard = analysis.peak_wizard

            # The spectrum.
            page = wizard.get_page(wizard.page_indices['read'])
            page.uf_args['file'].SetValue(str_to_gui("%s%s.list" % (data_path, names[i])))
            page.uf_args['spectrum_id'].SetValue(str_to_gui(names[i]))

            # Go to the next page.
            wizard._go_next(None)

            # The error type.
            page = wizard.get_page(wizard.page_indices['err_type'])
            page.selection = 'repl'

            # Go to the next page.
            wizard._go_next(None)

            # Replicated spectra:
            if names[i] in replicated:
                page = wizard.get_page(wizard.page_indices['repl'])
                page.uf_args['spectrum_ids'].SetValue(value=replicated[names[i]], index=1)

            # Go to the next page.
            wizard._go_next(None)

            # Set the delay ime.
            page = wizard.get_page(wizard.page_indices['relax_time'])
            page.uf_args['time'].SetValue(float_to_gui(ncyc[i]*time))

            # Go to the next page (i.e. finish).
            wizard._go_next(None)

        # Set up the nuclear isotopes.
        analysis.select_model()
        uf_store['relax_fit.select_model'].wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Set the number of MC sims.
        analysis.mc_sim_num.SetValue(3)

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

        # Check the data pipe.
        self.assertEqual(cdp_name(), ds.relax_gui.analyses[0].pipe_name)

        # Check the data.
        self.check_curve_fitting()

        # Check the created files.
        self.assertTrue(access(ds.tmpdir+sep+'r1.600.out', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'results.bz2', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'state.bz2', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'grace'+sep+'r1.600.agr', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'grace'+sep+'chi2.agr', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'grace'+sep+'i0.agr', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'grace'+sep+'intensities.agr', F_OK))
        self.assertTrue(access(ds.tmpdir+sep+'grace'+sep+'intensities_norm.agr', F_OK))
