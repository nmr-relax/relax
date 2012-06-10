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
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import int_to_gui, str_to_gui
from gui.user_functions import deselect, sequence, spin
from gui.wizard import Wiz_window


class Noe(GuiTestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Initialise all the special windows (to sometimes catch rare race conditions).
        self.app.gui.show_prompt(None)
        self.app.gui.show_tree(None)
        self.app.gui.show_pipe_editor(None)

        # Simulate the new analysis wizard.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_noe(None)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Steady-state NOE")

        # The frequency label.
        analysis.field_nmr_frq.SetValue(str_to_gui('500'))

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        wizard = Wiz_window(self.app.gui)
        seq_read = sequence.Read_page(wizard)
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'Ap4Aase.seq'
        seq_read.file.SetValue(str_to_gui(file))
        seq_read.mol_name_col.SetValue(int_to_gui(None))
        seq_read.res_name_col.SetValue(int_to_gui(2))
        seq_read.res_num_col.SetValue(int_to_gui(1))
        seq_read.spin_name_col.SetValue(int_to_gui(None))
        seq_read.spin_num_col.SetValue(int_to_gui(None))
        seq_read.on_execute()

        # Unresolved spins.
        deselect_spin = deselect.Spin_page(wizard)
        deselect_spin.spin_id.SetValue(str_to_gui(":3"))
        deselect_spin.on_execute()

        # Name the spins.
        page = spin.Name_page(wizard)
        page.name.SetValue(str_to_gui('N'))
        page.on_execute()

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # The intensity data.
        ids = ['ref', 'sat']
        files = [
            status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'ref_ave.list',
            status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'sat_ave.list'
        ]
        errors = [3600, 3000]
        types = [1, 0]

        # Loop over the 2 spectra.
        for i in range(2):
            # Set up the peak intensity wizard.
            analysis.peak_wizard(None)

            # The spectrum.
            page = analysis.wizard.get_page(analysis.page_indices['read'])
            page.file.SetValue(str_to_gui(files[i]))
            page.spectrum_id.SetValue(str_to_gui(ids[i]))
            page.proton.SetValue(str_to_gui('HN'))

            # Move down 2 pages.
            analysis.wizard._go_next(None)
            analysis.wizard._go_next(None)

            # Set the errors.
            page = analysis.wizard.get_page(analysis.page_indices['rmsd'])
            page.error.SetValue(int_to_gui(errors[i]))

            # Go to the next page.
            analysis.wizard._go_next(None)

            # Set the type.
            page = analysis.wizard.get_page(analysis.page_indices['spectrum_type'])
            page.spectrum_type.SetSelection(types[i])

            # Go to the next page (i.e. finish).
            analysis.wizard._go_next(None)

        # Execute relax.
        analysis.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, analysis.button_exec_relax.GetId()))

        # Wait for execution to complete.
        analysis.thread.join()

        # Flush all wx events.
        wx.Yield()

        # Exceptions in the thread.
        self.check_exceptions()

        # Check the relax controller.
        if status.relax_mode != 'gui':
            self.assertEqual(self.app.gui.controller.main_gauge.GetValue(), 100)

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
