###############################################################################
#                                                                             #
# Copyright (C) 2006-2014 Edward d'Auvergne                                   #
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
from math import pi
import platform
import numpy
from numpy import array, float64, transpose
from os import sep
from tempfile import mkdtemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from lib.geometry.rotations import R_to_euler_zyz
from status import Status; status = Status()
from specific_analyses.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from test_suite.system_tests.base_classes import SystemTestCase


# Get the platform information.
SYSTEM = platform.system()
RELEASE = platform.release()
VERSION = platform.version()
WIN32_VER = platform.win32_ver()
DIST = platform.dist()
ARCH = platform.architecture()
MACH = platform.machine()
PROC = platform.processor()
PY_VER = platform.python_version()
NUMPY_VER = numpy.__version__
LIBC_VER = platform.libc_ver()

# Windows system name pain.
if SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
    # Set the system to 'Windows' no matter what.
    SYSTEM = 'Windows'



class Frame_order(SystemTestCase):
    """TestCase class for the functional tests of the frame order theories."""

    def __init__(self, methodName='runTest', skip_tests=True):
        """Skip the tests if scipy is not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        @keyword skip_tests:    A flag which if True will cause a large number of redundant tests to be skipped.
        @type skip_tests:       bool
        """

        # Execute the base class method.
        super(Frame_order, self).__init__(methodName)

        # Tests to skip.
        blacklist = [
            'test_cam_free_rotor_pcs',
            'test_cam_free_rotor_rdc',
            'test_cam_free_rotor2_pcs',
            'test_cam_free_rotor2_rdc',
            'test_cam_iso_cone_pcs',
            'test_cam_iso_cone_rdc',
            'test_cam_iso_cone_free_rotor_pcs',
            'test_cam_iso_cone_free_rotor_rdc',
            'test_cam_iso_cone_free_rotor2_pcs',
            'test_cam_iso_cone_free_rotor2_rdc',
            'test_cam_iso_cone_torsionless_pcs',
            'test_cam_iso_cone_torsionless_rdc',
            'test_cam_pseudo_ellipse2_pcs',
            'test_cam_pseudo_ellipse2_rdc',
            'test_cam_pseudo_ellipse_free_rotor_pcs',
            'test_cam_pseudo_ellipse_free_rotor_rdc',
            'test_cam_pseudo_ellipse_torsionless_pcs',
            'test_cam_pseudo_ellipse_torsionless_rdc',
            'test_cam_rigid_pcs',
            'test_cam_rigid_rdc',
            'test_cam_rotor_pcs',
            'test_cam_rotor_rdc',
            'test_cam_rotor_2_state_pcs',
            'test_cam_rotor_2_state_rdc',
            'test_cam_rotor2_pcs',
            'test_cam_rotor2_rdc'
        ]

        # Skip the blacklisted tests.
        if skip_tests and methodName in blacklist:
            status.skipped_tests.append([methodName, None, self._skip_type])

        # Missing module.
        if not dep_check.scipy_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Scipy', self._skip_type])


    def setUp(self):
        """Set up for all the functional tests."""

        # The path to the CaM scripts.
        self.cam_path = status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'cam'+sep

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()


    def tearDown(self):
        """Clean up after the tests."""

        # Reset the relax data store.
        self.interpreter.reset()

        # Remove flags from the status object.
        if hasattr(status, 'flag_rdc'):
            del status.flag_rdc
        if hasattr(status, 'flag_pcs'):
            del status.flag_pcs


    def check_chi2(self, chi2=0.0, places=4):
        """Check the function evaluation."""

        # Switch back to the original pipe.
        self.interpreter.pipe.switch('frame order')

        # Get the debugging message.
        mesg = self.mesg_opt_debug()

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, chi2, places, msg=mesg)


    def flags(self, rdc=True, pcs=True, opt=False):
        """Set a number of flags for the scripts."""

        # Store the flags.
        status.flag_rdc = rdc
        status.flag_pcs = pcs
        status.flag_opt = opt


    def mesg_opt_debug(self):
        """Method for returning a string to help debug the minimisation.

        @return:        The debugging string.
        @rtype:         str
        """

        # Initialise the string.
        string = 'Optimisation failure.\n\n'

        # Create the string.
        string = string + "%-18s%-25s\n" % ("System: ", SYSTEM)
        string = string + "%-18s%-25s\n" % ("Release: ", RELEASE)
        string = string + "%-18s%-25s\n" % ("Version: ", VERSION)
        string = string + "%-18s%-25s\n" % ("Win32 version: ", (WIN32_VER[0] + " " + WIN32_VER[1] + " " + WIN32_VER[2] + " " + WIN32_VER[3]))
        string = string + "%-18s%-25s\n" % ("Distribution: ", (DIST[0] + " " + DIST[1] + " " + DIST[2]))
        string = string + "%-18s%-25s\n" % ("Architecture: ", (ARCH[0] + " " + ARCH[1]))
        string = string + "%-18s%-25s\n" % ("Machine: ", MACH)
        string = string + "%-18s%-25s\n" % ("Processor: ", PROC)
        string = string + "%-18s%-25s\n" % ("Python version: ", PY_VER)
        string = string + "%-18s%-25s\n" % ("Numpy version: ", NUMPY_VER)
        string = string + "%-18s%-25s\n" % ("Libc version: ", (LIBC_VER[0] + " " + LIBC_VER[1]))


        # Minimisation info.
        string = string + "\n"
        for param in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z', 'ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma', 'eigen_alpha', 'eigen_beta', 'eigen_gamma', 'axis_theta', 'axis_phi', 'cone_theta_x', 'cone_theta_y', 'cone_theta', 'cone_s1', 'cone_sigma_max', 'cone_sigma_max_2']:
            if hasattr(cdp, param):
                obj = getattr(cdp, param)
                string = string + "%-15s %30.17g\n" % (param, obj)

        string = string +   "%-15s %30.17g\n" % ('chi2:', cdp.chi2)
        if hasattr(cdp, 'num_int_pts'):
            string = string +   "%-15s %30i\n" % ('num_int_pts:', cdp.num_int_pts)
        if hasattr(cdp, 'iter') and cdp.iter != None:
            string = string +   "%-15s %30i\n" % ('iter:', cdp.iter)
        if hasattr(cdp, 'f_count') and cdp.f_count != None:
            string = string +   "%-15s %30i\n" % ('f_count:', cdp.f_count)
        if hasattr(cdp, 'g_count') and cdp.g_count != None:
            string = string +   "%-15s %30i\n" % ('g_count:', cdp.g_count)
        if hasattr(cdp, 'h_count') and cdp.h_count != None:
            string = string +   "%-15s %30i\n" % ('h_count:', cdp.h_count)
        if hasattr(cdp, 'warning'):
            string = string +   "%-15s %30s\n" % ('warning:', cdp.warning)

        # Return the string.
        return string


    def space_probe(self, ref_chi2=None, params=None, delta=3.0 / 360.0 * 2.0 * pi):
        """Probe the space around the supposed minimum."""

        # No function intros.
        self.interpreter.intro_off()

        # Check the minimum.
        self.interpreter.minimise.calculate()
        print("%-20s %10.5f" % ("chi2 minimum", cdp.chi2))
        self.assertAlmostEqual(cdp.chi2, ref_chi2)

        # Test around the minimum using small deviations.
        for param in params:
            print("\n\nParam: %s" % param)
            print("%-20s %10.5f" % ("chi2 orig", ref_chi2))

            # Get the current value.
            curr = getattr(cdp, param)

            # Deviate upwards.
            setattr(cdp, param, curr+delta)
            self.interpreter.minimise.calculate()
            print("%-20s %10.5f" % ("chi2 up", cdp.chi2))
            self.assert_(cdp.chi2 > ref_chi2)

            # Deviate downwards.
            setattr(cdp, param, curr-delta)
            self.interpreter.minimise.calculate()
            print("%-20s %10.5f" % ("chi2 down", cdp.chi2))
            self.assert_(cdp.chi2 > ref_chi2)

            # Reset.
            setattr(cdp, param, curr)


    def test_auto_analysis(self):
        """Test the frame order auto-analysis using the rigid CaM test data."""

        # Execute the script.
        self.interpreter.run(script_file=self.cam_path+'auto_analysis_to_rigid.py')


    def test_axis_perm_x_le_y_le_z_permA(self):
        """Test the operation of the frame_order.permute_axes user function for permutation 'A' when x <= y <= z."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Change the original parameters.
        cdp.cone_theta_x = orig_cone_theta_x = 1.0
        cdp.cone_theta_y = orig_cone_theta_y = 2.0
        cdp.cone_sigma_max = orig_cone_sigma_max = 3.0

        # Store the original parameters.
        orig_eigen_alpha = cdp.eigen_alpha
        orig_eigen_beta = cdp.eigen_beta
        orig_eigen_gamma = cdp.eigen_gamma

        # Permute the axes.
        self.interpreter.frame_order.permute_axes('A')

        # Checks of the cone opening angle permutations.
        self.assertEqual(cdp.cone_theta_x, 1.0)
        self.assertEqual(cdp.cone_theta_y, 3.0)
        self.assertEqual(cdp.cone_sigma_max, 2.0)

        # The optimised Eigenframe.
        frame = array([[ 0.519591643135168, -0.302150522797118, -0.799205596800676],
                       [ 0.62357991685585 , -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([frame[:, 0], -frame[:, 2], frame[:, 1]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_axis_perm_x_le_y_le_z_permB(self):
        """Test the operation of the frame_order.permute_axes user function for permutation 'B' when x <= y <= z."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Change the original parameters.
        cdp.cone_theta_x = orig_cone_theta_x = 1.0
        cdp.cone_theta_y = orig_cone_theta_y = 2.0
        cdp.cone_sigma_max = orig_cone_sigma_max = 3.0

        # Store the original parameters.
        orig_eigen_alpha = cdp.eigen_alpha
        orig_eigen_beta = cdp.eigen_beta
        orig_eigen_gamma = cdp.eigen_gamma

        # Permute the axes.
        self.interpreter.frame_order.permute_axes('B')

        # Checks of the cone opening angle permutations.
        self.assertEqual(cdp.cone_theta_x, 2.0)
        self.assertEqual(cdp.cone_theta_y, 3.0)
        self.assertEqual(cdp.cone_sigma_max, 1.0)

        # The optimised Eigenframe.
        frame = array([[ 0.519591643135168, -0.302150522797118, -0.799205596800676],
                       [ 0.62357991685585 , -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([frame[:, 2], frame[:, 0], frame[:, 1]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_axis_perm_x_le_z_le_y_permB(self):
        """Test the operation of the frame_order.permute_axes user function for permutation 'B' when x <= z <= y."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Change the original parameters.
        cdp.cone_theta_x = orig_cone_theta_x = 1.0
        cdp.cone_theta_y = orig_cone_theta_y = 3.0
        cdp.cone_sigma_max = orig_cone_sigma_max = 2.0

        # Store the original parameters.
        orig_eigen_alpha = cdp.eigen_alpha
        orig_eigen_beta = cdp.eigen_beta
        orig_eigen_gamma = cdp.eigen_gamma

        # Permute the axes.
        self.interpreter.frame_order.permute_axes('B')

        # Checks of the cone opening angle permutations.
        self.assertEqual(cdp.cone_theta_x, 2.0)
        self.assertEqual(cdp.cone_theta_y, 3.0)
        self.assertEqual(cdp.cone_sigma_max, 1.0)

        # The optimised Eigenframe.
        frame = array([[ 0.519591643135168, -0.302150522797118, -0.799205596800676],
                       [ 0.62357991685585 , -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([-frame[:, 2], frame[:, 1], frame[:, 0]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_axis_perm_x_le_z_le_y_permA(self):
        """Test the operation of the frame_order.permute_axes user function for permutation 'A' when x <= z <= y."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Change the original parameters.
        cdp.cone_theta_x = orig_cone_theta_x = 1.0
        cdp.cone_theta_y = orig_cone_theta_y = 3.0
        cdp.cone_sigma_max = orig_cone_sigma_max = 2.0

        # Store the original parameters.
        orig_eigen_alpha = cdp.eigen_alpha
        orig_eigen_beta = cdp.eigen_beta
        orig_eigen_gamma = cdp.eigen_gamma

        # Permute the axes.
        self.interpreter.frame_order.permute_axes('A')

        # Checks of the cone opening angle permutations.
        self.assertEqual(cdp.cone_theta_x, 1.0)
        self.assertEqual(cdp.cone_theta_y, 2.0)
        self.assertEqual(cdp.cone_sigma_max, 3.0)

        # The optimised Eigenframe.
        frame = array([[ 0.519591643135168, -0.302150522797118, -0.799205596800676],
                       [ 0.62357991685585 , -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([frame[:, 0], -frame[:, 2], frame[:, 1]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_axis_perm_z_le_x_le_y_permA(self):
        """Test the operation of the frame_order.permute_axes user function for permutation 'A' when z <= x <= y."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Store the original parameters.
        orig_cone_theta_x = cdp.cone_theta_x
        orig_cone_theta_y = cdp.cone_theta_y
        orig_cone_sigma_max = cdp.cone_sigma_max
        orig_eigen_alpha = cdp.eigen_alpha
        orig_eigen_beta = cdp.eigen_beta
        orig_eigen_gamma = cdp.eigen_gamma

        # Permute the axes.
        self.interpreter.frame_order.permute_axes('A')

        # Checks of the cone opening angle permutations.
        self.assertEqual(cdp.cone_theta_x, 0.53277077276728502)
        self.assertEqual(cdp.cone_theta_y, 0.8097621930390525)
        self.assertEqual(cdp.cone_sigma_max, 1.2119285953475074)

        # The optimised Eigenframe.
        frame = array([[ 0.519591643135168, -0.302150522797118, -0.799205596800676],
                       [ 0.62357991685585 , -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([frame[:, 1], frame[:, 2], frame[:, 0]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_axis_perm_z_le_x_le_y_permB(self):
        """Test the operation of the frame_order.permute_axes user function for permutation 'B' when z <= x <= y."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Store the original parameters.
        orig_cone_theta_x = cdp.cone_theta_x
        orig_cone_theta_y = cdp.cone_theta_y
        orig_cone_sigma_max = cdp.cone_sigma_max
        orig_eigen_alpha = cdp.eigen_alpha
        orig_eigen_beta = cdp.eigen_beta
        orig_eigen_gamma = cdp.eigen_gamma

        # Permute the axes.
        self.interpreter.frame_order.permute_axes('B')

        # Checks of the cone opening angle permutations.
        self.assertEqual(cdp.cone_theta_x, 0.53277077276728502)
        self.assertEqual(cdp.cone_theta_y, 1.2119285953475074)
        self.assertEqual(cdp.cone_sigma_max, 0.8097621930390525)

        # The optimised Eigenframe.
        frame = array([[ 0.519591643135168, -0.302150522797118, -0.799205596800676],
                       [ 0.62357991685585 , -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([-frame[:, 2], frame[:, 1], frame[:, 0]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_cam_double_rotor(self):
        """Test the double rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.082433008378229589)


    def test_cam_double_rotor_pcs(self):
        """Test the double rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.0026189545487338103)


    def test_cam_double_rotor_rdc(self):
        """Test the double rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.079814053829495801)


    def test_cam_double_rotor_large_angle(self):
        """Test the double rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.04420414251367831)


    def test_cam_double_rotor_large_angle_pcs(self):
        """Test the double rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.00025808742855180884)


    def test_cam_double_rotor_large_angle_rdc(self):
        """Test the double rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.043946055085127944)


    def test_cam_free_rotor(self):
        """Test the free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.048992338400504688)


    def test_cam_free_rotor_missing_data(self):
        """Test the free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'free_rotor_missing_data.py')
        self.check_chi2(0.037724884620487453)


    def test_cam_free_rotor_pcs(self):
        """Test the free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(1.0828246263831909e-07)


    def test_cam_free_rotor_rdc(self):
        """Test the free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.04899130610303442)


    def test_cam_free_rotor2(self):
        """Test the second free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.067540995069675966)


    def test_cam_free_rotor2_pcs(self):
        """Test the second free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.01079639889927377)


    def test_cam_free_rotor2_rdc(self):
        """Test the second free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.056744492444430819)


    def test_cam_iso_cone(self):
        """Test the isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.047612694541267306)


    def test_cam_iso_cone_pcs(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.0061842204344042893)


    def test_cam_iso_cone_rdc(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.041428474106863025)


    def test_cam_iso_cone_free_rotor(self):
        """Test the isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.011527134355548144)


    def test_cam_iso_cone_free_rotor_pcs(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.00054073128938189553)


    def test_cam_iso_cone_free_rotor_rdc(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.010986403066166248)


    def test_cam_iso_cone_free_rotor2(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.02996954151455445)


    def test_cam_iso_cone_free_rotor2_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.024410594632485034)


    def test_cam_iso_cone_free_rotor2_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.0055589468820694179)


    def test_cam_iso_cone_torsionless(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.048930632669473069)


    def test_cam_iso_cone_torsionless_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.0001814304495273832)


    def test_cam_iso_cone_torsionless_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.048749202219945678)


    def test_cam_pseudo_ellipse(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.094228483127403714)


    def test_cam_pseudo_ellipse_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.06846727616648722)


    def test_cam_pseudo_ellipse_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.03300256897164619)


    def test_cam_pseudo_ellipse2(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.023514665851808478)


    def test_cam_pseudo_ellipse2_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.0053850528961595428)


    def test_cam_pseudo_ellipse2_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.018129612955648935)


    def test_cam_pseudo_ellipse_free_rotor(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.0543303786779369)


    def test_cam_pseudo_ellipse_free_rotor_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.0041254537455716134)


    def test_cam_pseudo_ellipse_free_rotor_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.036975308912984388)


    def test_cam_pseudo_ellipse_torsionless(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.01497741674116292)


    def test_cam_pseudo_ellipse_torsionless_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(2.9799363738575403e-05)


    def test_cam_pseudo_ellipse_torsionless_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.014947617377424345)


    def test_cam_rigid(self):
        """Test the rigid frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(0.081171019382935666)


    def test_cam_rigid_pcs(self):
        """Test the rigid frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(6.1557756577162843e-09)


    def test_cam_rigid_rdc(self):
        """Test the rigid frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(0.081171013227160013)


    def test_cam_rotor(self):
        """Test the rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(0.075072773007664212)


    def test_cam_rotor_pcs(self):
        """Test the rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(1.139566998206629e-06)


    def test_cam_rotor_rdc(self):
        """Test the rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(0.075071633440666002)


    def test_cam_rotor_2_state(self):
        """Test the 2-state rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(0.98321958150473276)


    def test_cam_rotor_2_state_pcs(self):
        """Test the 2-state rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(2.9152704264897967e-05)


    def test_cam_rotor_2_state_rdc(self):
        """Test the 2-state rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(0.98319606148815675)


    def test_cam_rotor2(self):
        """Test the second rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(0.075040490418167072)


    def test_cam_rotor2_pcs(self):
        """Test the second rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(1.5787105392036996e-06)


    def test_cam_rotor2_rdc(self):
        """Test the second rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(0.075038911707627859)


    def test_generate_rotor2_distribution(self):
        """Generate the rotor2 distribution of CaM."""

        # Execute the script.
        self.interpreter.run(script_file=self.cam_path+'generate_rotor2_distribution.py')


    def test_frame_order_pdb_model_ensemble(self):
        """Test the operation of the frame_order.pdb_model user function when an ensemble of structures are loaded."""

        # Create a data pipe.
        self.interpreter.pipe.create('frame_order.pdb_model ensemble failure', 'frame order')

        # Load some lactose structures to create an ensemble.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=data_path, set_model_num=1, set_mol_name='lactose')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=data_path, set_model_num=2, set_mol_name='lactose')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_3.pdb', dir=data_path, set_model_num=3, set_mol_name='lactose')

        # Set the pivot point.
        self.interpreter.frame_order.pivot([0, 0, 0], fix=True)

        # Select a frame order model.
        self.interpreter.frame_order.select_model('rotor')

        # Define the moving part.
        self.interpreter.domain(id='lactose', spin_id=':UNK')

        # Set up the system.
        self.interpreter.value.set(param='ave_pos_x', val=0.0)
        self.interpreter.value.set(param='ave_pos_y', val=0.0)
        self.interpreter.value.set(param='ave_pos_z', val=0.0)
        self.interpreter.value.set(param='ave_pos_alpha', val=0.0)
        self.interpreter.value.set(param='ave_pos_beta', val=0.0)
        self.interpreter.value.set(param='ave_pos_gamma', val=0.0)
        self.interpreter.value.set(param='axis_alpha', val=0.5)
        self.interpreter.value.set(param='cone_sigma_max', val=0.1)

        # Set up Monte Carlo data structures.
        self.interpreter.monte_carlo.setup(10)

        # Create the PDB model.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir)


    def fixme_test_model_free_rotor(self):
        """Test the free rotor frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'free_rotor.py')

        # Check the calculated chi2 value.
        self.assertAlmostEqual(ds.chi2, 0.0216067401326)


    def fixme_test_model_free_rotor_eigenframe(self):
        """Test the free rotor frame order model in the eigenframe."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'free_rotor_eigenframe.py')

        # Check the calculated chi2 value.
        self.assertAlmostEqual(ds.chi2, 0.00673210578744)


    def fixme_test_model_iso_cone(self):
        """Test the isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'iso_cone.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.131890484593)
        chi2_ref.append(0.0539383731611)
        chi2_ref.append(0.0135056297016)
        chi2_ref.append(0.0163432453475)
        chi2_ref.append(0.0775570503917)
        chi2_ref.append(0.0535055367493)
        chi2_ref.append(0.0994746492483)
        chi2_ref.append(0.174830826376)
        chi2_ref.append(0.193036744906)
        chi2_ref.append(0.181480810794)
        chi2_ref.append(0.215863920824)
        chi2_ref.append(0.170088692559)
        chi2_ref.append(0.152634493383)
        chi2_ref.append(0.168711907446)
        chi2_ref.append(0.168405354086)
        chi2_ref.append(0.247439860108)
        chi2_ref.append(0.143487410228)
        chi2_ref.append(0.148318989268)

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_model_iso_cone_free_rotor(self):
        """Test the free rotor isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'iso_cone_free_rotor.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.0177292447567 )
        chi2_ref.append(0.0187585146766 )
        chi2_ref.append(0.0440519894909 )
        chi2_ref.append(0.0225223798489 )
        chi2_ref.append(0.0239979046491 )
        chi2_ref.append(0.0161048633259 )
        chi2_ref.append(0.0267310958091 )
        chi2_ref.append(0.0219820914478 )
        chi2_ref.append(0.0194880630576 )
        chi2_ref.append(0.0348242343833 )
        chi2_ref.append(0.0401631858563 )
        chi2_ref.append(0.0327461783858 )
        chi2_ref.append(0.0391082177884 )
        chi2_ref.append(0.0467056691507 )
        chi2_ref.append(0.0407175857557 )
        chi2_ref.append(0.0441514158832 )
        chi2_ref.append(0.042078718831  )
        chi2_ref.append(0.0403856796359 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_model_iso_cone_free_rotor_eigenframe(self):
        """Test the free rotor isotropic cone frame order model in the eigenframe."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'iso_cone_free_rotor_eigenframe.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.115175446978 )
        chi2_ref.append(0.156911214374 )
        chi2_ref.append(0.209198723492 )
        chi2_ref.append(0.155297079942 )
        chi2_ref.append(0.0684780584219)
        chi2_ref.append(0.0781922435531)
        chi2_ref.append(0.103777394815 )
        chi2_ref.append(0.173740596864 )
        chi2_ref.append(0.199867814969 )
        chi2_ref.append(0.297587241555 )
        chi2_ref.append(0.308539214325 )
        chi2_ref.append(0.2543934866   )
        chi2_ref.append(0.168985365277 )
        chi2_ref.append(0.190780393086 )
        chi2_ref.append(0.186482798104 )
        chi2_ref.append(0.153839910288 )
        chi2_ref.append(0.160863854198 )
        chi2_ref.append(0.157029368992 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_model_pseudo_ellipse(self):
        """Test the pseudo-ellipse frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'pseudo_ellipse.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.0208490007203)
        chi2_ref.append(0.00958146486076)
        chi2_ref.append(0.0405488536626)
        chi2_ref.append(0.0370142845551)
        chi2_ref.append(0.0204537537661)
        chi2_ref.append(0.0186122056988)
        chi2_ref.append(0.0177783016875)
        chi2_ref.append(0.0311747995923)
        chi2_ref.append(0.0225532898175)
        chi2_ref.append(0.0212562065194)
        chi2_ref.append(0.018939663528)
        chi2_ref.append(0.0224686987165)
        chi2_ref.append(0.0201247095045)
        chi2_ref.append(0.0215343817478)
        chi2_ref.append(0.016509302331)
        chi2_ref.append(0.0101988814638)
        chi2_ref.append(0.00989431182393)
        chi2_ref.append(0.0123400971524)

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_model_pseudo_ellipse_free_rotor(self):
        """Test the free rotor pseudo-elliptic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'pseudo_ellipse_free_rotor.py')

        # The reference chi2 values.
        chi2_ref = [[], []]
        chi2_ref[0].append(0.0493245760341)
        chi2_ref[0].append(0.0322727678945)
        chi2_ref[0].append(0.0399505883966)
        chi2_ref[0].append(0.0122539315721)
        chi2_ref[0].append(0.0263840505182)
        chi2_ref[0].append(0.0324871952484)
        chi2_ref[0].append(0.0247369735031)
        chi2_ref[0].append(0.0231896861006)
        chi2_ref[0].append(0.0285947802273)
        chi2_ref[0].append(0.0345542627808)
        chi2_ref[0].append(0.0289869422491)
        chi2_ref[0].append(0.0243038470127)
        chi2_ref[0].append(0.0226686034191)
        chi2_ref[0].append(0.0215714556045)
        chi2_ref[0].append(0.0173836730495)
        chi2_ref[0].append(0.0182530810025)
        chi2_ref[0].append(0.0212669211551)
        chi2_ref[0].append(0.0194359136977)

        chi2_ref[1].append(0.0205287391277)
        chi2_ref[1].append(0.0246463829816)
        chi2_ref[1].append(0.0590186061204)
        chi2_ref[1].append(0.0441193978727)
        chi2_ref[1].append(0.0424299319779)
        chi2_ref[1].append(0.032589994611)
        chi2_ref[1].append(0.0523532207508)
        chi2_ref[1].append(0.0488535879384)
        chi2_ref[1].append(0.0424063218455)
        chi2_ref[1].append(0.0553525984677)
        chi2_ref[1].append(0.0495587286781)
        chi2_ref[1].append(0.0446625345909)
        chi2_ref[1].append(0.0470718361239)
        chi2_ref[1].append(0.0493615476721)
        chi2_ref[1].append(0.0492208206006)
        chi2_ref[1].append(0.0429966323771)
        chi2_ref[1].append(0.0442849187057)
        chi2_ref[1].append(0.0436756306414)
            
        # Check the calculated chi2 values.
        for j in range(2):
            for i in range(18):
                self.assertAlmostEqual(ds.chi2[j][i], chi2_ref[j][i])


    def fixme_test_model_pseudo_ellipse_torsionless(self):
        """Test the pseudo-ellipse frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'pseudo_ellipse_torsionless.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.340228489225)
        chi2_ref.append(0.260847963487)
        chi2_ref.append(0.250610744982)
        chi2_ref.append(0.228947619476)
        chi2_ref.append(0.251996758815)
        chi2_ref.append(0.238724080817)
        chi2_ref.append(0.182383602599)
        chi2_ref.append(0.172830852017)
        chi2_ref.append(0.159757813028)
        chi2_ref.append(0.173833227524)
        chi2_ref.append(0.156168102428)
        chi2_ref.append(0.171406869781)
        chi2_ref.append(0.202653838515)
        chi2_ref.append(0.198919351788)
        chi2_ref.append(0.169463187543)
        chi2_ref.append(0.156867571611)
        chi2_ref.append(0.146139931983)
        chi2_ref.append(0.13307108095 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_model_rotor(self):
        """Test the rotor frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'rotor.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.00410277546707 )
        chi2_ref.append(0.00112443204411 )
        chi2_ref.append(0.00759196190331 )
        chi2_ref.append(0.0956596925692  )
        chi2_ref.append(0.223717470059   )
        chi2_ref.append(0.136723330704   )
        chi2_ref.append(0.0588253217034  )
        chi2_ref.append(0.0774693384156  )
        chi2_ref.append(0.0855477856492  )
        chi2_ref.append(0.198089516589   )
        chi2_ref.append(0.227537351664   )
        chi2_ref.append(0.202005777915   )
        chi2_ref.append(0.192550395736   )
        chi2_ref.append(0.126007906472   )
        chi2_ref.append(0.124053264662   )
        chi2_ref.append(0.18203965973    )
        chi2_ref.append(0.191062017006   )
        chi2_ref.append(0.13580013153    )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_model_rotor_eigenframe(self):
        """Test the rotor frame order model in the eigenframe."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'model_calcs'+sep+'rotor_eigenframe.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.00308229284128)
        chi2_ref.append(0.0117874014708 )
        chi2_ref.append(0.0016108171487 )
        chi2_ref.append(0.00532862954549)
        chi2_ref.append(0.097784753109  )
        chi2_ref.append(0.157147901966  )
        chi2_ref.append(0.182397051711  )
        chi2_ref.append(0.338977916543  )
        chi2_ref.append(0.208516866654  )
        chi2_ref.append(0.137660115226  )
        chi2_ref.append(0.0580816149373 )
        chi2_ref.append(0.0476543367845 )
        chi2_ref.append(0.0360689584006 )
        chi2_ref.append(0.0118024492136 )
        chi2_ref.append(0.0824307041139 )
        chi2_ref.append(0.0920614159956 )
        chi2_ref.append(0.0936464288916 )
        chi2_ref.append(0.0823025718101 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_opendx_map(self):
        """Test the mapping of the Euler angle parameters for OpenDx viewing."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opendx_euler_angle_map.py')


    def fixme_test_opt_rigid_no_rot(self):
        """Test the 'rigid' model for unrotated tensors with no motion."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opt_rigid_no_rot.py')

        # Get the debugging message.
        self.mesg = self.mesg_opt_debug()

        # Test the values.
        self.assertEqual(cdp.iter, 92, msg=self.mesg)
        self.assertEqual(cdp.chi2, 0.0, msg=self.mesg)
        self.assertEqual(cdp.ave_pos_alpha, 0.0, msg=self.mesg)
        self.assertEqual(cdp.ave_pos_beta, 0.0, msg=self.mesg)
        self.assertEqual(cdp.ave_pos_gamma, 0.0, msg=self.mesg)


    def fixme_test_opt_rigid_rand_rot(self):
        """Test the 'rigid' model for randomly rotated tensors with no motion."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opt_rigid_rand_rot.py')

        # Get the debugging message.
        self.mesg = self.mesg_opt_debug()

        # Test the values.
        self.assertAlmostEqual(cdp.chi2, 3.085356555118994e-26, msg=self.mesg)
        self.assertAlmostEqual(cdp.ave_pos_alpha, 5.0700283197712777, msg=self.mesg)
        self.assertAlmostEqual(cdp.ave_pos_beta, 2.5615753919522359, msg=self.mesg)
        self.assertAlmostEqual(cdp.ave_pos_gamma, 0.64895449611163691, msg=self.mesg)


    def fixme_test_parametric_restriction_iso_cone_to_iso_cone_free_rotor(self):
        """Parametric restriction of the isotropic cone to the free rotor isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'parametric_restriction'+sep+'iso_cone_to_iso_cone_free_rotor.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.0177292447567 )
        chi2_ref.append(0.0187585146766 )
        chi2_ref.append(0.0440519894909 )
        chi2_ref.append(0.0225223798489 )
        chi2_ref.append(0.0239979046491 )
        chi2_ref.append(0.0161048633259 )
        chi2_ref.append(0.0267310958091 )
        chi2_ref.append(0.0219820914478 )
        chi2_ref.append(0.0194880630576 )
        chi2_ref.append(0.0348242343833 )
        chi2_ref.append(0.0401631858563 )
        chi2_ref.append(0.0327461783858 )
        chi2_ref.append(0.0391082177884 )
        chi2_ref.append(0.0467056691507 )
        chi2_ref.append(0.0407175857557 )
        chi2_ref.append(0.0441514158832 )
        chi2_ref.append(0.042078718831  )
        chi2_ref.append(0.0403856796359 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_parametric_restriction_pseudo_ellipse_to_iso_cone(self):
        """Parametric restriction of the pseudo-ellipse to the isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'parametric_restriction'+sep+'pseudo_ellipse_to_iso_cone.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.131890484593)
        chi2_ref.append(0.0539383731611)
        chi2_ref.append(0.0135056297016)
        chi2_ref.append(0.0163432453475)
        chi2_ref.append(0.0775570503917)
        chi2_ref.append(0.0535055367493)
        chi2_ref.append(0.0994746492483)
        chi2_ref.append(0.174830826376)
        chi2_ref.append(0.193036744906)
        chi2_ref.append(0.181480810794)
        chi2_ref.append(0.215863920824)
        chi2_ref.append(0.170088692559)
        chi2_ref.append(0.152634493383)
        chi2_ref.append(0.168711907446)
        chi2_ref.append(0.168405354086)
        chi2_ref.append(0.247439860108)
        chi2_ref.append(0.143487410228)
        chi2_ref.append(0.148318989268)

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_parametric_restriction_pseudo_ellipse_to_iso_cone_free_rotor(self):
        """Parametric restriction of the pseudo-ellipse to the free rotor isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'parametric_restriction'+sep+'pseudo_ellipse_to_iso_cone_free_rotor.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.0177292447567 )
        chi2_ref.append(0.0187585146766 )
        chi2_ref.append(0.0440519894909 )
        chi2_ref.append(0.0225223798489 )
        chi2_ref.append(0.0239979046491 )
        chi2_ref.append(0.0161048633259 )
        chi2_ref.append(0.0267310958091 )
        chi2_ref.append(0.0219820914478 )
        chi2_ref.append(0.0194880630576 )
        chi2_ref.append(0.0348242343833 )
        chi2_ref.append(0.0401631858563 )
        chi2_ref.append(0.0327461783858 )
        chi2_ref.append(0.0391082177884 )
        chi2_ref.append(0.0467056691507 )
        chi2_ref.append(0.0407175857557 )
        chi2_ref.append(0.0441514158832 )
        chi2_ref.append(0.042078718831  )
        chi2_ref.append(0.0403856796359 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_parametric_restriction_pseudo_ellipse_free_rotor_to_iso_cone(self):
        """Parametric restriction of the pseudo-ellipse to the isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'parametric_restriction'+sep+'pseudo_ellipse_free_rotor_to_iso_cone.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(16957.4964577)
        chi2_ref.append(15727.13869)
        chi2_ref.append(13903.0982799)
        chi2_ref.append(11719.9390681)
        chi2_ref.append(9488.44060873)
        chi2_ref.append(7425.57820642)
        chi2_ref.append(5713.6467735)
        chi2_ref.append(4393.3273949)
        chi2_ref.append(3452.97770868)
        chi2_ref.append(2771.90973598)
        chi2_ref.append(2247.44444894)
        chi2_ref.append(1788.58977266)
        chi2_ref.append(1348.38250916)
        chi2_ref.append(921.060703519)
        chi2_ref.append(539.03217075)
        chi2_ref.append(244.341444558)
        chi2_ref.append(58.4566671195)
        chi2_ref.append(0.148318989268)

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_parametric_restriction_pseudo_ellipse_free_rotor_to_iso_cone_free_rotor(self):
        """Parametric restriction of the free rotor pseudo-ellipse to the free rotor isotropic cone frame order model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'parametric_restriction'+sep+'pseudo_ellipse_free_rotor_to_iso_cone_free_rotor.py')

        # The reference chi2 values.
        chi2_ref = []
        chi2_ref.append(0.0177292447567 )
        chi2_ref.append(0.0187585146766 )
        chi2_ref.append(0.0440519894909 )
        chi2_ref.append(0.0225223798489 )
        chi2_ref.append(0.0239979046491 )
        chi2_ref.append(0.0161048633259 )
        chi2_ref.append(0.0267310958091 )
        chi2_ref.append(0.0219820914478 )
        chi2_ref.append(0.0194880630576 )
        chi2_ref.append(0.0348242343833 )
        chi2_ref.append(0.0401631858563 )
        chi2_ref.append(0.0327461783858 )
        chi2_ref.append(0.0391082177884 )
        chi2_ref.append(0.0467056691507 )
        chi2_ref.append(0.0407175857557 )
        chi2_ref.append(0.0441514158832 )
        chi2_ref.append(0.042078718831  )
        chi2_ref.append(0.0403856796359 )

        # Check the calculated chi2 values.
        for i in range(18):
            self.assertAlmostEqual(ds.chi2[i], chi2_ref[i])


    def fixme_test_pseudo_ellipse(self):
        """Test the pseudo-ellipse target function."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'pseudo_ellipse.py')

        # The reference chi2 value.
        chi2 = 0.015865464136741975

        # Check the surrounding space.
        self.space_probe(ref_chi2=chi2, params=['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma', 'eigen_alpha', 'eigen_beta', 'eigen_gamma', 'cone_theta_x', 'cone_theta_y', 'cone_sigma_max'])


    def fixme_test_pseudo_ellipse_torsionless(self):
        """Test the torsionless pseudo-ellipse target function."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'pseudo_ellipse_torsionless.py')

        # The reference chi2 value.
        chi2 = 2.8393866813588198

        # Check the surrounding space.
        self.space_probe(ref_chi2=chi2, params=['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma', 'eigen_alpha', 'eigen_beta', 'eigen_gamma', 'cone_theta_x', 'cone_theta_y'])


    def test_rigid_data_to_double_rotor_model(self):
        """Test the double rotor target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_DOUBLE_ROTOR

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.01137748706675365, 5)


    def test_rigid_data_to_free_rotor_model(self):
        """Test the free rotor target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_FREE_ROTOR

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 204026.70481594582)


    def test_rigid_data_to_iso_cone_model(self):
        """Test the iso cone target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_ISO_CONE

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.01137748706675365, 5)


    def test_rigid_data_to_iso_cone_free_rotor_model(self):
        """Test the iso cone, free rotor target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_ISO_CONE_FREE_ROTOR

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 22295.503345237757)


    def test_rigid_data_to_iso_cone_torsionless_model(self):
        """Test the iso cone, torsionless target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_ISO_CONE_TORSIONLESS

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.01137748706675365, 5)


    def test_rigid_data_to_rigid_model(self):
        """Test the rigid target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_RIGID

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.0113763520134, 5)


    def test_rigid_data_to_rotor_model(self):
        """Test the rotor target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_ROTOR

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.011377487066752203, 5)


    def test_rigid_data_to_pseudo_ellipse_model(self):
        """Test the pseudo-ellipse target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_PSEUDO_ELLIPSE

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.01137748706675365, 5)


    def test_rigid_data_to_pseudo_ellipse_torsionless_model(self):
        """Test the pseudo-ellipse, torsionless target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_PSEUDO_ELLIPSE_TORSIONLESS

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.011378666767745968)
