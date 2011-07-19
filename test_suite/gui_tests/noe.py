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
import Queue
from shutil import rmtree
from tempfile import mkdtemp
from time import sleep
from traceback import print_exception
import wx

# Dependency checks.
import dep_check

# relax module imports.
from base_classes import GuiTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import cdp_name
from status import Status; status = Status()

# relax GUI imports.
if dep_check.wx_module:
    from gui.relax_gui import Main
from gui.misc import int_to_gui, str_to_gui
from gui.user_functions import deselect, sequence, spin
from gui.wizard import Wiz_window


class Noe(GuiTestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a temporary directory for the results.
        ds.tmpdir = mkdtemp()

        # Start the GUI.
        self.app = wx.App()

        # Build the GUI.
        self.gui = Main(parent=None, id=-1, title="")


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(ds.tmpdir)

        # Reset relax.
        reset()

        # Destroy the GUI.
        self.gui.Destroy()


    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Directly set up the analysis.
        self.gui.analysis.new_analysis(analysis_type='noe', analysis_name="Steady-state NOE test", pipe_name='noe test')

        # Alias the analysis.
        analysis = self.gui.analysis.get_page_from_name("Steady-state NOE test")

        # The frequency label.
        analysis.field_nmr_frq.SetValue(str_to_gui('500'))

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Load the sequence.
        wizard = Wiz_window(size_x=900, size_y=700)
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
        deselect_spin.spin_id.SetValue(str_to_gui(":3"))
        deselect_spin.on_execute()

        # Name the spins.
        page = spin.Name_page(wizard, self.gui)
        page.name.SetValue(str_to_gui('N'))
        page.on_execute()

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

            # The reference spectrum.
            page = analysis.wizard.get_page(analysis.page_indices['read'])
            page.file.SetValue(str_to_gui(files[i]))
            page.spectrum_id.SetValue(str_to_gui(ids[i]))
            page.heteronuc.SetValue(str_to_gui('HN'))

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
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'noe.agr', F_OK))
