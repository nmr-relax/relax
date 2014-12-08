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
import base64
from numpy import array, concatenate, float32, float64, frombuffer, save
from os import path, sep
from tempfile import mkdtemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from lib.errors import RelaxError
from lib.io import file_root, get_file_list
from lib.statistics import linear_corr, linear_corr_intercept
from pipe_control.nmrglue import plot_contour, plot_hist
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase
from extern import nmrglue

# Dependent import.
# If matplotlib module available, then import.
if dep_check.matplotlib_module:
    import matplotlib.pyplot as plt


class Nmrglue(SystemTestCase):
    """TestCase class for the functionality of the external module nmrglue.
    This is from U{Task #7873<https://gna.org/task/index.php?7873>}: Write wrapper function to nmrglue, to read .ft2 files and process them."""

    def __init__(self, methodName='runTest'):
        """Skip certain tests if the C modules are non-functional.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Nmrglue, self).__init__(methodName)

        # If not matplotlib module
        if not dep_check.matplotlib_module:
            # The list of tests to skip.
            to_skip = [
                "test_plot_contour",
                "test_plot_contour_cpmg",
                "test_plot_hist_cpmg",
                "test_plot_hist_cpmg_several",
            ]

            # Store in the status object.
            if methodName in to_skip:
                status.skipped_tests.append([methodName, 'matplotlib module', self._skip_type])



    def plot_plot_contour(self):
        """Plot the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}."""

        # Call setup function.
        self.setup_plot_contour(show=False)

        # Now show
        plt.show()


    def plot_plot_contour_cpmg(self):
        """Plot the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_contour_cpmg(show=False)

        # Now show
        plt.show()


    def plot_plot_correlation(self):
        """Plot data for correlation plot.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_correlation()

        # Show
        plt.show()


    def plot_plot_hist_cpmg(self):
        """Plot the plot_hist function in pipe_control.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_hist_cpmg(show=True)


    def plot_plot_hist_cpmg_several(self):
        """Plot the plot_hist function in pipe_control with several spectra.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_hist_cpmg_several(show=True)


    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()

        # Create path to nmrglue test data.
        ds.ng_test = status.install_path +sep+ 'extern' +sep+ 'nmrglue' +sep+ 'nmrglue_0_4' +sep+ 'tests' +sep+ 'pipe_proc_tests'


    def setup_plot_contour(self, show=False):
        """Setup the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}."""

        # Read the spectrum.
        fname = 'freq_real.ft2'
        sp_id = 'test'
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ds.ng_test, nmrglue_id=sp_id)

        # Call the pipe_control function and get the return axis.
        ax = plot_contour(nmrglue_id=sp_id, ppm=True, show=show)

        # Set new limits.
        ax.set_xlim(30, 0)
        ax.set_ylim(15, -20)

        # add some labels
        ax.text(25.0, 0.0, "Test", size=8, color='r')


    def setup_plot_contour_cpmg(self, show=False):
        """Setup the plot_contour function in pipe_control.
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
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ft2_folder_1, nmrglue_id=sp_id)

        # Call the pipe_control function and get the return axis.
        ax = plot_contour(nmrglue_id=sp_id, contour_start=200000., contour_num=20, contour_factor=1.20, ppm=True, show=show)

        # Set a new title.
        ax.set_title("CPMG Spectrum")


    def setup_plot_correlation(self):
        """Setup data for correlation plot.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Define base path to files.
        base_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'repeated_analysis'+sep+'SOD1'

        # Define folder to all ft files.
        ft2_folder_1 = base_path +sep+ 'cpmg_disp_sod1d90a_060518' +sep+ 'cpmg_disp_sod1d90a_060518_normal.fid' +sep+ 'ft2_data'
        ft2_folder_2 = base_path +sep+ 'cpmg_disp_sod1d90a_060521' +sep+ 'cpmg_disp_sod1d90a_060521_normal.fid' +sep+ 'ft2_data'

        # Get the file list matching a glob pattern for the reference.
        ref_500 = '128_*_FT.ft2'
        ref_500_id = 'ref_500'
        ref_600 = '128_*_FT.ft2'
        ref_600_id = 'ref_600'

        # Get the file lists.
        self.interpreter.io.file_list(glob=ref_500, dir=ft2_folder_1, id=ref_500_id)
        self.interpreter.io.file_list(glob=ref_600, dir=ft2_folder_2, id=ref_600_id)

        # Then get the file list for method.
        met_500 = '126_*_MDD.ft2'
        met_500_id = 'met_500'
        met_600 = '126_*_MDD.ft2'
        met_600_id = 'met_600'

        # Get the file lists.
        self.interpreter.io.file_list(glob=met_500, dir=ft2_folder_1, id=met_500_id)
        self.interpreter.io.file_list(glob=met_600, dir=ft2_folder_2, id=met_600_id)

        # Read the spectra.
        # First loop over the glob id.
        ids_ref = []
        ids_met = []
        for io_id in cdp.io_ids:
            # Get the directory
            io_dir = cdp.io_dir[io_id]

            # Then loop over the file_roots:
            for i, froot in enumerate(cdp.io_file_root[io_id]):
                # Get the basename
                bname = cdp.io_basename[io_id][i]

                # Form new nmrglue id.
                ng_id = froot + '_' + io_id

                # Assign ids to list.
                if 'ref_' in ng_id:
                    ids_ref.append(ng_id)
                elif 'met_' in ng_id:
                    ids_met.append(ng_id)

                # Read the spectrum data.
                self.interpreter.spectrum.nmrglue_read(file=bname, dir=io_dir, nmrglue_id=ng_id)

        # Create an empty reference array.
        np_arr_ref = array([])

        # Loop over id ref:
        for ng_id in ids_ref:
            data = cdp.nmrglue[ng_id].data
            data_flat = data.flatten()
            print(ng_id, data.shape, data_flat.shape)
            np_arr_ref = concatenate( (np_arr_ref,  data_flat) )

        # Create an empty method array.
        np_arr_met = array([])

        # Loop over id ref:
        for ng_id in ids_met:
            data = cdp.nmrglue[ng_id].data
            data_flat = data.flatten()
            print(ng_id, data.shape, data_flat.shape)
            np_arr_met = concatenate( (np_arr_met,  data_flat) )

        # Create correlation plot.
        fig = plt.figure()
        ax = fig.add_subplot(111)

        line = array( [np_arr_ref.min(), np_arr_ref.max()] )

        ax.plot(np_arr_ref, np_arr_met, '+', label='corr')
        ax.plot(line, line, 'r-', label='corr')

        # Try get the linear correlation
        a, r_xy = linear_corr(x=np_arr_ref, y=np_arr_met)
        print(a, r_xy)
        a_int, b_int, r_xy_int = linear_corr_intercept(x=np_arr_ref, y=np_arr_met)
        print(a_int, r_xy, b_int)

        ax.plot(np_arr_ref, np_arr_ref*a, 'g-', label='corr')

        # Set text.
        ax.set_xlabel("All spectrum intensities for reference")
        ax.set_ylabel("All spectrum intensities for method")
        ax.set_title("Correlation plot")


    def setup_plot_hist_cpmg(self, show=False):
        """Setup the plot_hist function in pipe_control.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Define base path to files.
        base_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'repeated_analysis'+sep+'SOD1'

        # Define folder to all ft files.
        ft2_folder_1 = base_path +sep+ 'cpmg_disp_sod1d90a_060518' +sep+ 'cpmg_disp_sod1d90a_060518_normal.fid' +sep+ 'ft2_data'

        # Read the spectrum.
        fname = '128_0_FT.ft2'
        sp_id = file_root(fname)
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ft2_folder_1, nmrglue_id=sp_id)

        # Extract the data.
        dic  = cdp.nmrglue[sp_id].dic
        udic  = cdp.nmrglue[sp_id].udic
        data = cdp.nmrglue[sp_id].data

        # Plot the histogram.
        kwargs = {'bins': 3000, 'range': None, 'normed': False, 'facecolor':'green', 'alpha':0.75}
        plot_hist(ndarray=data, hist_kwargs=kwargs, show=show)


    def setup_plot_hist_cpmg_several(self, show=False):
        """Setup the plot_hist function in pipe_control with several spectra.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Define base path to files.
        base_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'repeated_analysis'+sep+'SOD1'

        # Define folder to all ft files.
        ft2_folder_1 = base_path +sep+ 'cpmg_disp_sod1d90a_060518' +sep+ 'cpmg_disp_sod1d90a_060518_normal.fid' +sep+ 'ft2_data'

        # Get the file list matching a glob pattern.
        ft2_glob_pat = '128_*_FT.ft2'
        basename_list, file_root_list = get_file_list(glob_pattern=ft2_glob_pat, dir=ft2_folder_1)

        # Read the spectra.
        self.interpreter.spectrum.nmrglue_read(file=basename_list, dir=ft2_folder_1, nmrglue_id=file_root_list)

        # Extract the data.
        data_0 = cdp.nmrglue[file_root_list[0]].data
        data_1 = cdp.nmrglue[file_root_list[1]].data

        # First flatten arrays, and then merge them.
        data = concatenate( (data_0.flatten(), data_1.flatten() ) )

        # Plot the histogram.
        kwargs = {'bins': 3000, 'range': None, 'normed': False, 'facecolor':'green', 'alpha':0.75}
        plot_hist(ndarray=data, hist_kwargs=kwargs, show=show)


    def test_nmrglue_read(self):
        """Test the userfunction spectrum.nmrglue_read."""

        # Read the spectrum.
        fname = 'freq_real.ft2'
        sp_id = 'test'
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ds.ng_test, nmrglue_id=sp_id)

        # Test that the spectrum id has been stored.
        self.assertEqual(cdp.nmrglue_ids[0], sp_id)

        # Extract the data.
        dic  = cdp.nmrglue[sp_id].dic
        udic  = cdp.nmrglue[sp_id].udic
        data = cdp.nmrglue[sp_id].data

        # Test the data.
        self.assertEqual(udic[0]['label'], '15N')
        self.assertEqual(udic[1]['label'], '13C')
        self.assertEqual(udic[0]['freq'], True)
        self.assertEqual(udic[1]['freq'], True)
        self.assertEqual(udic[0]['size'], 512)
        self.assertEqual(udic[1]['size'], 4096)


    def test_nmrglue_read_several(self):
        """Test the userfunction spectrum.nmrglue_read with several spectra.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Define base path to files.
        base_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'repeated_analysis'+sep+'SOD1'

        # Define folder to all ft files.
        ft2_folder_1 = base_path +sep+ 'cpmg_disp_sod1d90a_060518' +sep+ 'cpmg_disp_sod1d90a_060518_normal.fid' +sep+ 'ft2_data'

        # Get the file list matching a glob pattern.
        ft2_glob_pat = '128_*_FT.ft2'
        self.interpreter.io.file_list(glob=ft2_glob_pat, dir=ft2_folder_1, id=None)

        # Test the list of stored id.
        self.assertEqual(cdp.io_ids[-1], ft2_glob_pat)

        self.assertEqual(cdp.io_basename[ft2_glob_pat], ['128_0_FT.ft2', '128_1_FT.ft2'])
        self.assertEqual(cdp.io_file_root[ft2_glob_pat], ['128_0_FT', '128_1_FT'])
        self.assertEqual(cdp.io_dir[ft2_glob_pat], ft2_folder_1)

        # Extract from cdp.
        basename_list, file_root_list = cdp.io_basename[ft2_glob_pat], cdp.io_file_root[ft2_glob_pat]

        # First test that expected RelaxErrors are raised.
        self.assertRaises(RelaxError, self.interpreter.spectrum.nmrglue_read, file=basename_list, dir=ft2_folder_1, nmrglue_id='test')
        self.assertRaises(RelaxError, self.interpreter.spectrum.nmrglue_read, file='128_0_FT.ft2', dir=ft2_folder_1, nmrglue_id=file_root_list)

        # Read the spectra.
        self.interpreter.spectrum.nmrglue_read(file=basename_list, dir=ft2_folder_1, nmrglue_id=file_root_list)

        # Test that the spectrum id has been stored.
        self.assertEqual(cdp.nmrglue_ids[0], file_root_list[0])
        self.assertEqual(cdp.nmrglue_ids[1], file_root_list[1])


    def test_plot_contour(self):
        """Test the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}."""

        # Call setup function.
        self.setup_plot_contour(show=False)


    def test_plot_contour_cpmg(self):
        """Test the plot_contour function in pipe_control.
        This is from the U{tutorial<http://jjhelmus.github.io/nmrglue/current/examples/plot_2d_spectrum.html>}.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_contour_cpmg(show=False)


    def test_plot_correlation(self):
        """Test data for correlation plot.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_correlation()


    def test_plot_hist_cpmg(self):
        """Test the plot_hist function in pipe_control.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_hist_cpmg(show=False)


    def test_plot_hist_cpmg_several(self):
        """Test the plot_hist function in pipe_control with several spectra.

        The data is from systemtest -s Relax_disp.test_repeat_cpmg
        U{task #7826<https://gna.org/task/index.php?7826>}. Write an python class for the repeated analysis of dispersion data.
        """

        # Call setup function.
        self.setup_plot_hist_cpmg_several(show=False)


    def test_save_state(self):
        """Test saving a state with numpy arrays, reset relax, and read the state again."""

        # Read the spectrum.
        fname = 'freq_real.ft2'
        sp_id = 'test'
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ds.ng_test, nmrglue_id=sp_id)

        # Get the file size.
        data_size_file = path.getsize(ds.ng_test + sep + fname)
        print("Filesize of .ft2 file is: %i"%(data_size_file) )

        # Test that the spectrum id has been stored.
        self.assertEqual(cdp.nmrglue_ids[0], sp_id)

        # Extract the data.
        dic  = cdp.nmrglue[sp_id].dic
        udic  = cdp.nmrglue[sp_id].udic
        data = cdp.nmrglue[sp_id].data
        print("Type of encoding is:", type(cdp.nmrglue[sp_id].data))

        # Try storing the numpy array, and print size
        data_numpy = ds.tmpdir + sep + 'data.npy'
        print("Storing numpy array to: %s"%data_numpy)
        save(data_numpy, data)
        data_numpy_size = path.getsize(data_numpy)
        print("Filesize of .npy file is: %i"%(data_numpy_size) )

        # Store the directory path, before reset of the controller.
        dirpath = ds.tmpdir

        print("Shape of data is %ix%i"%(data.shape[0], data.shape[1]))
        print("dtype of data is", data.dtype)
        print("Type of data[0][0]: ", type(data[0][0]))

        # Save the results.
        self.interpreter.state.save('state', dir=dirpath, compress_type=1, force=True)

        # Get the file size.
        state_size_file = path.getsize(dirpath + sep + 'state.bz2')
        print("Filesize of state file is %i"%(state_size_file) )

        # Reset of the controller.
        self.interpreter.reset()

        # Load the state again.
        self.interpreter.state.load(dirpath+sep+'state')

        # Decode
        print("Type of decoded is:", type(cdp.nmrglue[sp_id].data))
        print("Shape of numpy array is:", cdp.nmrglue[sp_id].data.shape)

        # Test data.
        print("Testing data array.")
        print("Shape of data is %ix%i, and of cdp.nmrglue[].data is %ix%i"%(data.shape[0], data.shape[1], cdp.nmrglue[sp_id].data.shape[0], cdp.nmrglue[sp_id].data.shape[1]))
        test = data == cdp.nmrglue[sp_id].data
        print(test.all())
        self.assert_(test.all())

        print("Testing dics.")
        # Make tests that they are the same.
        self.assertEqual(dic, cdp.nmrglue[sp_id].dic)
        for id in dic:
            self.assertEqual(dic[id], cdp.nmrglue[sp_id].dic[id])

        self.assertEqual(udic, cdp.nmrglue[sp_id].udic)
        for id in udic:
            self.assertEqual(udic[id], cdp.nmrglue[sp_id].udic[id])


    def test_version(self):
        """Test version of nmrglue."""

        # Test version.
        ng_vers = nmrglue.__version__
        print("Version of nmrglue is %s"%ng_vers)

        # Assert the version to be 0.4.
        self.assertEqual(ng_vers, '0.4')
