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
from gui.misc import str_to_gui


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

        # Reset the relax data storage object.
        ds.__reset__()

        # Destroy the GUI.
        self.gui.Destroy()


    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Directly set up the analysis.
        self.gui.analysis.new_analysis(analysis_type='noe', analysis_name="Steady-state NOE test", pipe_name='noe test')

        # Alias the page.
        page = self.gui.analysis.get_page_from_name("Steady-state NOE test")

        # The frequency label.
        page.field_nmr_frq.SetValue(str_to_gui('500'))

        # Change the results directory.
        page.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # The sequence file.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'Ap4Aase.seq'
        page.field_sequence.SetValue(str_to_gui(file))

        # Unresolved spins.
        page.field_unresolved.SetValue(str_to_gui('3'))

        # The reference spectrum.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'ref_ave.list'
        page.field_ref_noe.SetValue(str_to_gui(file))

        # The sat spectrum.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'sat_ave.list'
        page.field_sat_noe.SetValue(str_to_gui(file))

        # Set the errors.
        page.field_ref_rmsd.SetValue(str_to_gui('3600'))
        page.field_sat_rmsd.SetValue(str_to_gui('3000'))

        # Set the proton name.
        ds.relax_gui.global_setting[3] = 'HN'

        # Execute relax.
        page.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, page.button_exec_id))

        # Wait for execution to complete.
        page.thread.join()

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
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Spin info.
            self.assertEqual(res_nums[i], res_num)

            # Check the intensity data.
            self.assertEqual(sat[i], spin.intensities['sat'])
            self.assertEqual(ref[i], spin.intensities['ref'])

            # Check the NOE data.
            self.assertEqual(noe[i], spin.noe)
            self.assertEqual(noe_err[i], spin.noe_err)

            # Increment the spin index.
            i += 1

        # Check the created files.
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'noe.agr', F_OK))
