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
from gui.misc import bool_to_gui, float_to_gui, int_to_gui, float_to_gui, str_to_gui
from gui.user_functions import deselect, sequence, spin
from gui.wizard import Wiz_window


class Rx(GuiTestCase):
    """Class for testing various aspects specific to the R1 and R2 analyses."""

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
            self.assertEqual(cdp_relax_times[i], relax_times[i])

        # Check the errors.
        for key in cdp.sigma_I:
            self.assertEqual(cdp.sigma_I[key], 10578.03948242143)
            self.assertEqual(cdp.var_I[key], 111894919.29166666)

        # Spin data check.
        i = 0
        for spin in spin_loop():
            # No data present.
            if chi2[i] == None:
                self.assert_(not hasattr(spin, 'chi2'))

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
        self.gui.analysis.menu_new(None)
        page = self.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_r1(None)
        self.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.gui.analysis.new_wizard.wizard.get_page(1)
        self.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name = self.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name)

        # Alias the analysis.
        analysis = self.gui.analysis.get_page_from_name("R1 relaxation")

        # The frequency label.
        analysis.field_nmr_frq.SetValue(str_to_gui('600'))

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        wizard = Wiz_window()
        seq_read = sequence.Read_page(wizard, self.gui)
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'Ap4Aase.seq'
        seq_read.file.SetValue(str_to_gui(file))
        seq_read.mol_name_col.SetValue(int_to_gui(None))
        seq_read.res_name_col.SetValue(int_to_gui(2))
        seq_read.res_num_col.SetValue(int_to_gui(1))
        seq_read.spin_name_col.SetValue(int_to_gui(None))
        seq_read.spin_num_col.SetValue(int_to_gui(None))
        seq_read.on_execute()

        # Unresolved spins.
        deselect_read = deselect.Read_page(wizard, self.gui)
        deselect_read.file.SetValue(str_to_gui(data_path + 'unresolved'))
        deselect_read.mol_name_col.SetValue(int_to_gui(None))
        deselect_read.res_name_col.SetValue(int_to_gui(None))
        deselect_read.res_num_col.SetValue(int_to_gui(1))
        deselect_read.spin_name_col.SetValue(int_to_gui(None))
        deselect_read.spin_num_col.SetValue(int_to_gui(None))
        deselect_read.change_all.SetValue(bool_to_gui(True))
        deselect_read.on_execute()

        # Name the spins.
        page = spin.Name_page(wizard, self.gui)
        page.name.SetValue(str_to_gui('N'))
        page.on_execute()

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
            analysis.peak_wizard(None)

            # The spectrum.
            page = analysis.wizard.get_page(analysis.page_indices['read'])
            page.file.SetValue(str_to_gui("%s%s.list" % (data_path, names[i])))
            page.spectrum_id.SetValue(str_to_gui(names[i]))
            page.proton.SetValue(str_to_gui('HN'))

            # Go to the next page.
            analysis.wizard._go_next(None)

            # The error type.
            page = analysis.wizard.get_page(analysis.page_indices['err_type'])
            page.selection = 'repl'

            # Go to the next page.
            analysis.wizard._go_next(None)

            # Replicated spectra:
            if names[i] in replicated.keys():
                page = analysis.wizard.get_page(analysis.page_indices['repl'])
                page.spectrum_id_boxes[1].SetStringSelection(str_to_gui(replicated[names[i]]))

            # Go to the next page.
            analysis.wizard._go_next(None)

            # Set the delay time.
            page = analysis.wizard.get_page(analysis.page_indices['relax_time'])
            page.time.SetValue(float_to_gui(ncyc[i]*time))

            # Go to the next page (i.e. finish).
            analysis.wizard._go_next(None)

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
        self.assertEqual(self.gui.controller.mc_gauge_rx.GetValue(), 100)
        self.assertEqual(self.gui.controller.main_gauge.GetValue(), 100)

        # Check the data pipe.
        self.assertEqual(cdp_name(), ds.relax_gui.analyses[0].pipe_name)

        # Check the data.
        self.check_curve_fitting()

        # Check the created files.
        self.assert_(access(ds.tmpdir+sep+'r1.600.out', F_OK))
        self.assert_(access(ds.tmpdir+sep+'results.bz2', F_OK))
        self.assert_(access(ds.tmpdir+sep+'r1.600.save.bz2', F_OK))
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'r1.600.agr', F_OK))
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'chi2.agr', F_OK))
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'i0.agr', F_OK))
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'intensities.agr', F_OK))
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'intensities_norm.agr', F_OK))
