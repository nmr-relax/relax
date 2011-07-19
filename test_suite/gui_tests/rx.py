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
from gui.misc import float_to_gui, int_to_gui, float_to_gui, str_to_gui
from gui.user_functions import deselect, sequence, spin
from gui.wizard import Wiz_window


class Rx(GuiTestCase):
    """Class for testing various aspects specific to the R1 and R2 analyses."""

    def test_r1_analysis(self):
        """Test the r1 analysis."""

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
        deselect_spin = deselect.Spin_page(wizard, self.gui)
        deselect_spin.spin_id.SetValue(str_to_gui(":3, 11, 18, 19, 23, 31, 42, 44, 54, 66, 82, 92, 94, 99, 101, 113, 124, 126, 136, 141, 145, 147, 332, 345, 346, 358, 361"))
        deselect_spin.on_execute()

        # Name the spins.
        page = spin.Name_page(wizard, self.gui)
        page.name.SetValue(str_to_gui('N'))
        page.on_execute()

        # The path to the data files.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'curve_fitting' + sep

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
                page.spectrum_id2.SetValue(str_to_gui(replicated[names[i]]))

            # Go to the next page.
            analysis.wizard._go_next(None)

            # Set the delay time.
            page = analysis.wizard.get_page(analysis.page_indices['relax_time'])
            page.time.SetValue(float_to_gui(ncyc[i]*time))

            # Go to the next page (i.e. finish).
            analysis.wizard._go_next(None)

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
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'r1.agr', F_OK))
