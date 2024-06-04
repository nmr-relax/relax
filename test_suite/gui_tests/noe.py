###############################################################################
#                                                                             #
# Copyright (C) 2006-2008,2011-2014 Edward d'Auvergne                         #
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
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import str_to_gui
from pipe_control.mol_res_spin import spin_loop
from pipe_control.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase


class Noe(GuiTestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Noe, self).__init__(methodName)

        # Tests to skip.
        blacklist = [
            'test_noe_analysis_memory_leaks'
        ]

        # Skip the blacklisted tests.
        if methodName in blacklist:
            status.skipped_tests.append([methodName, None, self._skip_type])


    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Initialise all the special windows (to sometimes catch rare race conditions).
        self.app.gui.show_prompt(None)
        self.app.gui.show_tree(None)
        self.app.gui.show_pipe_editor(None)

        # Simulate the new analysis wizard.
        analysis = self.new_analysis_wizard(analysis_type='noe')

        # The frequency label.
        analysis.field_nmr_frq.SetValue(str_to_gui('500'))

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'Ap4Aase.seq'
        self._execute_uf(uf_name='sequence.read', file=file, mol_name_col=None, res_name_col=2, res_num_col=1, spin_name_col=None, spin_num_col=None)

        # Unresolved spins.
        self._execute_uf(uf_name='deselect.spin', spin_id=":3")

        # Name the spins.
        self._execute_uf(uf_name='spin.name', name="N")

        # Create a Trp indole N spin.
        self._execute_uf(uf_name='spin.create', res_num=40, spin_name="NE1")

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # The intensity data.
        ids = ['ref', 'sat']
        files = [
            status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'ref_ave.list',
            status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'sat_ave.list'
        ]
        errors = [3600, 3000]
        errors_5 = [122000, 8500]
        types = ['ref', 'sat']

        # Loop over the 2 spectra.
        for i in range(2):
            # Set up the peak intensity wizard.
            analysis.peak_wizard_launch(None)
            wizard = analysis.peak_wizard

            # The spectrum.
            wizard.setup_page(page='read', file=files[i], spectrum_id=ids[i])
            wizard._go_next(None)

            # Move down one pages.
            wizard._go_next(None)

            # Set the errors.
            wizard.setup_page(page='rmsd', error=errors[i])
            wizard._apply(None)
            wizard.setup_page(page='rmsd', error=errors_5[i], spin_id=':5')
            wizard._go_next(None)

            # Set the type and finish.
            wizard.setup_page(page='spectrum_type', spectrum_type=types[i])
            wizard._go_next(None)

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
            self.assertEqual(self.app.gui.controller.main_gauge.GetValue(), 100)

        # The real data.
        res_nums = [4, 5, 6, 40, 40, 55]
        sat = [5050.0, 51643.0, 53663.0, -65111.0, -181131.0, -105322.0]
        ref = [148614.0, 166842.0, 128690.0, 99566.0, 270047.0, 130959.0]
        noe = [0.033980647852826784, 0.30953237194471417, 0.4169943274535706, -0.6539481349054899, -0.6707387973204665, -0.8042364404126482]
        noe_err = [0.02020329903276632, 0.2320024671657343, 0.026067523940084526, 0.038300618865378507, 0.014260663438353431, 0.03183614777183591]

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
            self.assertEqual(sat[i], spin_cont.peak_intensity['sat'])
            self.assertEqual(ref[i], spin_cont.peak_intensity['ref'])

            # Check the NOE data.
            self.assertEqual(noe[i], spin_cont.noe)
            self.assertAlmostEqual(noe_err[i], spin_cont.noe_err)

            # Increment the spin index.
            i += 1

        # Check the created files.
        self.assertTrue(access(ds.tmpdir+sep+'grace'+sep+'noe.agr', F_OK))


    def test_noe_analysis_memory_leaks(self):
        """Test for memory leaks in the NOE analysis.

        This can be monitored using the MS Windows task manager, once the 'USER Objects' column is shown.
        """

        # A large loop (to try to reach the USER Object limit in MS Windows).
        for i in range(1000):
            # Printout for debugging.
            print("\n\n\nCreating the analysis number %i." % (i+1))

            # Simulate the new analysis wizard.
            analysis = self.new_analysis_wizard(analysis_type='noe')

            # Close the analysis.
            self.app.gui.analysis.delete_analysis(0)

            # Printout for debugging.
            print("\n\nClosing the analysis number %i.\n\n\n" % (i+1))

