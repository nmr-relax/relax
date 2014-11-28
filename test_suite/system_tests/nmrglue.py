##############################################################################
#                                                                             #
# Copyright (C) 2011-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
from os import sep
from tempfile import mkdtemp, NamedTemporaryFile

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.io import file_root
from pipe_control.nmrglue import plot_contour
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase
from extern import nmrglue


class Nmrglue(SystemTestCase):
    """TestCase class for the functionality of the external module nmrglue.
    This is from U{Task #7873<https://gna.org/task/index.php?7873>}: Write wrapper function to nmrglue, to read .ft2 files and process them."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()

        # Create path to nmrglue test data.
        ds.ng_test = status.install_path +sep+ 'extern' +sep+ 'nmrglue' +sep+ 'nmrglue_0_4' +sep+ 'tests' +sep+ 'pipe_proc_tests'


    def test_nmrglue_read(self):
        """Test the userfunction spectrum.nmrglue_read."""

        # Read the spectrum.
        fname = 'freq_real.ft2'
        sp_id = 'test'
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ds.ng_test, spectrum_id=sp_id)

        # Test that the spectrum id has been stored.
        self.assertEqual(cdp.spectrum_ids[0], sp_id)

        # Extract the data.
        dic  = cdp.ngdata[sp_id].dic
        udic  = cdp.ngdata[sp_id].udic
        data = cdp.ngdata[sp_id].data

        # Test the data.
        self.assertEqual(udic[0]['label'], '15N')
        self.assertEqual(udic[1]['label'], '13C')
        self.assertEqual(udic[0]['freq'], True)
        self.assertEqual(udic[1]['freq'], True)
        self.assertEqual(udic[0]['size'], 512)
        self.assertEqual(udic[1]['size'], 4096)


    def test_version(self):
        """Test version of nmrglue."""

        # Test version.
        ng_vers = nmrglue.__version__
        print("Version of nmrglue is %s"%ng_vers)

        # Assert the version to be 0.4.
        self.assertEqual(ng_vers, '0.4')


    def xtest_plot_contour(self):
        """Test the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}."""

        # Read the spectrum.
        fname = 'freq_real.ft2'
        sp_id = 'test'
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ds.ng_test, spectrum_id=sp_id)

        # Call the pipe_control function and get the return axis.
        ax = plot_contour(spectrum_id=sp_id, ppm=True, show=False)

        # Set new limits.
        ax.set_xlim(30, 0)
        ax.set_ylim(15, -20)

        # add some labels
        ax.text(25.0, 0.0, "Test", size=8, color='r')

        # Now show
        import matplotlib.pyplot as plt
        plt.show()


    def xtest_plot_contour_cpmg(self):
        """Test the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Define base path to files.
        base_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'repeated_analysis'+sep+'SOD1'

        # Define folder to all ft files.
        ft2_folder_1 = base_path +sep+ 'cpmg_disp_sod1d90a_060518' +sep+ 'cpmg_disp_sod1d90a_060518_normal.fid' +sep+ 'ft2_data'
        ft2_folder_2 = base_path +sep+ 'cpmg_disp_sod1d90a_060521' +sep+ 'cpmg_disp_sod1d90a_060521_normal.fid' +sep+ 'ft2_data'

        # Read the spectrum.
        fname = '128_0_FT.ft2'
        sp_id = file_root(fname)
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ft2_folder_1, spectrum_id=sp_id)

        # Call the pipe_control function and get the return axis.
        ax = plot_contour(spectrum_id=sp_id, contour_start=200000., contour_num=20, contour_factor=1.20, ppm=True, show=False)

        # Set a new title.
        ax.set_title("CPMG Spectrum")

        # Now show
        import matplotlib.pyplot as plt
        plt.show()