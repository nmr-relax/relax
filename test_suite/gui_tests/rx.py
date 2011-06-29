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
from shutil import rmtree
from tempfile import mkdtemp
from time import sleep
from unittest import TestCase
import wx

# Dependency checks.
import dep_check

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import cdp_name
from status import Status; status = Status()

# relax GUI imports.
if dep_check.wx_module:
    from gui.relax_gui import Main
from gui.misc import float_to_gui, int_to_gui, str_to_gui


class Rx(TestCase):
    """Class for testing various aspects specific to the R1 and R2 analyses."""

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


    def test_r1_analysis(self):
        """Test the r1 analysis."""

        # The path to the data files.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'curve_fitting'

        # Directly set up the analysis.
        self.gui.analysis.new_analysis(analysis_type='r1', analysis_name="R1 relaxation test", pipe_name='r1 test')

        # Alias the page.
        page = self.gui.analysis.get_page_from_name("R1 relaxation test")

        # The frequency label.
        page.field_nmr_frq.SetValue(str_to_gui('600'))

        # Change the results directory.
        page.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # The sequence file.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'Ap4Aase.seq'
        page.field_sequence.SetValue(str_to_gui(file))

        # Unresolved spins.
        page.field_unresolved.SetValue(str_to_gui("3, 11, 18, 19, 23, 31, 42, 44, 54, 66, 82, 92, 94, 99, 101, 113, 124, 126, 136, 141, 145, 147, 332, 345, 346, 358, 361"))

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

        # Set the delay time.
        page.peak_intensity.delay_time.SetValue(float_to_gui(0.0176))

        # Add the spectra and number of cycles.
        for i in range(len(names)):
            # The spectrum.
            file = data_path + sep + names[i]
            page.peak_intensity.grid.SetCellValue(i, 0, str_to_gui(file))

            # The number of cycles.
            page.peak_intensity.grid.SetCellValue(i, 1, int_to_gui(ncyc[i]))

        # Set the proton name.
        ds.relax_gui.global_setting[3] = 'HN'

        # Execute relax.
        page.execute(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, page.button_exec_id))

        # Wait for execution to complete.
        page.thread.join()

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
        self.assert_(access(ds.tmpdir+sep+'grace'+sep+'r1.agr', F_OK))
