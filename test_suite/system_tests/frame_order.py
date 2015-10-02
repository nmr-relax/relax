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
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from lib.geometry.rotations import R_to_euler_zyz
from status import Status; status = Status()
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

    def __init__(self, methodName='runTest'):
        """Skip the tests if scipy is not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Frame_order, self).__init__(methodName)

        # Tests to skip.
        blacklist = [
            'test_cam_qr_int_free_rotor_pcs',
            'test_cam_qr_int_free_rotor_rdc',
            'test_cam_qr_int_free_rotor2_pcs',
            'test_cam_qr_int_free_rotor2_rdc',
            'test_cam_qr_int_iso_cone_pcs',
            'test_cam_qr_int_iso_cone_rdc',
            'test_cam_qr_int_iso_cone_free_rotor_pcs',
            'test_cam_qr_int_iso_cone_free_rotor_rdc',
            'test_cam_qr_int_iso_cone_free_rotor2_pcs',
            'test_cam_qr_int_iso_cone_free_rotor2_rdc',
            'test_cam_qr_int_iso_cone_torsionless_pcs',
            'test_cam_qr_int_iso_cone_torsionless_rdc',
            'test_cam_qr_int_pseudo_ellipse2_pcs',
            'test_cam_qr_int_pseudo_ellipse2_rdc',
            'test_cam_qr_int_pseudo_ellipse_free_rotor_pcs',
            'test_cam_qr_int_pseudo_ellipse_free_rotor_rdc',
            'test_cam_qr_int_pseudo_ellipse_torsionless_pcs',
            'test_cam_qr_int_pseudo_ellipse_torsionless_rdc',
            'test_cam_qr_int_rigid_pcs',
            'test_cam_qr_int_rigid_rdc',
            'test_cam_qr_int_rotor_pcs',
            'test_cam_qr_int_rotor_rdc',
            'test_cam_qr_int_rotor_2_state_pcs',
            'test_cam_qr_int_rotor_2_state_rdc',
            'test_cam_qr_int_rotor2_pcs',
            'test_cam_qr_int_rotor2_rdc',
            'test_cam_quad_int_free_rotor_pcs',
            'test_cam_quad_int_free_rotor_rdc',
            'test_cam_quad_int_free_rotor2_pcs',
            'test_cam_quad_int_free_rotor2_rdc',
            'test_cam_quad_int_iso_cone_pcs',
            'test_cam_quad_int_iso_cone_rdc',
            'test_cam_quad_int_iso_cone_free_rotor_pcs',
            'test_cam_quad_int_iso_cone_free_rotor_rdc',
            'test_cam_quad_int_iso_cone_free_rotor2_pcs',
            'test_cam_quad_int_iso_cone_free_rotor2_rdc',
            'test_cam_quad_int_iso_cone_torsionless_pcs',
            'test_cam_quad_int_iso_cone_torsionless_rdc',
            'test_cam_quad_int_pseudo_ellipse2_pcs',
            'test_cam_quad_int_pseudo_ellipse2_rdc',
            'test_cam_quad_int_pseudo_ellipse_free_rotor_pcs',
            'test_cam_quad_int_pseudo_ellipse_free_rotor_rdc',
            'test_cam_quad_int_pseudo_ellipse_torsionless_pcs',
            'test_cam_quad_int_pseudo_ellipse_torsionless_rdc',
            'test_cam_quad_int_rigid_pcs',
            'test_cam_quad_int_rigid_rdc',
            'test_cam_quad_int_rotor_pcs',
            'test_cam_quad_int_rotor_rdc',
            'test_cam_quad_int_rotor_2_state_pcs',
            'test_cam_quad_int_rotor_2_state_rdc',
            'test_cam_quad_int_rotor2_pcs',
            'test_cam_quad_int_rotor2_rdc'
        ]

        # Skip the blacklisted tests.
        if methodName in blacklist:
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


    def flags(self, rdc=True, pcs=True, opt=False, quad_int=False):
        """Set a number of flags for the scripts."""

        # Store the flags.
        status.flag_rdc = rdc
        status.flag_pcs = pcs
        status.flag_opt = opt
        status.flag_quad_int = quad_int


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
        for param in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z', 'ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma', 'eigen_alpha', 'eigen_beta', 'eigen_gamma', 'axis_theta', 'axis_phi', 'cone_theta_x', 'cone_theta_y', 'cone_theta', 'cone_sigma_max', 'cone_sigma_max_2']:
            if hasattr(cdp, param):
                obj = getattr(cdp, param)
                string = string + "%-15s %30.17g\n" % (param, obj)

        string = string +   "%-15s %30.17g\n" % ('chi2:', cdp.chi2)
        if hasattr(cdp, 'sobol_max_points'):
            string = string +   "%-15s %30i\n" % ('sobol_max_points:', cdp.sobol_max_points)
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
                       [ 0.62357991685585, -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([-frame[:, 2], frame[:, 1], frame[:, 0]], float64))
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
                       [ 0.62357991685585, -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([frame[:, 2], frame[:, 0], frame[:, 1]], float64))
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
                       [ 0.62357991685585, -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([-frame[:, 2], frame[:, 1], frame[:, 0]], float64))
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
                       [ 0.62357991685585, -0.505348769456744,  0.596465177946379],
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
                       [ 0.62357991685585, -0.505348769456744,  0.596465177946379],
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
                       [ 0.62357991685585, -0.505348769456744,  0.596465177946379],
                       [-0.584099830232939, -0.808286881485765, -0.074159999594586]], float64)

        # Manually permute the frame, and then obtain the Euler angles.
        frame_new = transpose(array([frame[:, 0], -frame[:, 2], frame[:, 1]], float64))
        alpha, beta, gamma = R_to_euler_zyz(frame_new)

        # Check the Eigenframe Euler angles.
        self.assertAlmostEqual(cdp.eigen_alpha, alpha)
        self.assertAlmostEqual(cdp.eigen_beta, beta)
        self.assertAlmostEqual(cdp.eigen_gamma, gamma)


    def test_cam_qr_int_double_rotor(self):
        """Test the double rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.080146041009531946)


    def test_cam_qr_int_double_rotor_pcs(self):
        """Test the double rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.00033425735965255754)


    def test_cam_qr_int_double_rotor_rdc(self):
        """Test the double rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.079814053829495801)


    def test_cam_qr_int_double_rotor_large_angle(self):
        """Test the double rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.046993590502437441)


    def test_cam_qr_int_double_rotor_large_angle_pcs(self):
        """Test the double rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.0030482390409642141)


    def test_cam_qr_int_double_rotor_large_angle_rdc(self):
        """Test the double rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.043946055085127944)


    def test_cam_qr_int_free_rotor(self):
        """Test the free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.049488502147038226)


    def test_cam_qr_int_free_rotor_missing_data(self):
        """Test the free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'free_rotor_missing_data.py')
        self.check_chi2(0.038106832800436169)


    def test_cam_qr_int_free_rotor_pcs(self):
        """Test the free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.00049268587082683434)


    def test_cam_qr_int_free_rotor_rdc(self):
        """Test the free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.04899130610303442)


    def test_cam_qr_int_free_rotor2(self):
        """Test the second free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.069952611688108693)


    def test_cam_qr_int_free_rotor2_pcs(self):
        """Test the second free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.013207545726879745)


    def test_cam_qr_int_free_rotor2_rdc(self):
        """Test the second free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.056744492444430819)


    def test_cam_qr_int_iso_cone(self):
        """Test the isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.046263256206108584)


    def test_cam_qr_int_iso_cone_pcs(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.010223404689484922)


    def test_cam_qr_int_iso_cone_rdc(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.041428474106863025)


    def test_cam_qr_int_iso_cone_free_rotor(self):
        """Test the isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.013068834561396353)


    def test_cam_qr_int_iso_cone_free_rotor_pcs(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.0020824314952301057)


    def test_cam_qr_int_iso_cone_free_rotor_rdc(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.010986403066166248)


    def test_cam_qr_int_iso_cone_free_rotor2(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.13135988423081582)


    def test_cam_qr_int_iso_cone_free_rotor2_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.12580093734874642)


    def test_cam_qr_int_iso_cone_free_rotor2_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.0055589468820694179)


    def test_cam_qr_int_iso_cone_torsionless(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.058320273132310863)


    def test_cam_qr_int_iso_cone_torsionless_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.0095766977930929302)


    def test_cam_qr_int_iso_cone_torsionless_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.048749202219945678)


    def test_cam_qr_int_pseudo_ellipse(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.052923535071890106)


    def test_cam_qr_int_pseudo_ellipse_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.025487205467282097)


    def test_cam_qr_int_pseudo_ellipse_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.03300256897164619)


    def test_cam_qr_int_pseudo_ellipse2(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.041445854907868764)


    def test_cam_qr_int_pseudo_ellipse2_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.02331739779637744)


    def test_cam_qr_int_pseudo_ellipse2_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.018129612955648935)


    def test_cam_qr_int_pseudo_ellipse_free_rotor(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.07886558371162268)


    def test_cam_qr_int_pseudo_ellipse_free_rotor_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.038891355121051734)


    def test_cam_qr_int_pseudo_ellipse_free_rotor_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.039974228590570947)


    def test_cam_qr_int_pseudo_ellipse_torsionless(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.018922576784401186)


    def test_cam_qr_int_pseudo_ellipse_torsionless_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.003977725835776093)


    def test_cam_qr_int_pseudo_ellipse_torsionless_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.014947617377424345)


    def test_cam_qr_int_rigid(self):
        """Test the rigid frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(0.081171019382935666)


    def test_cam_qr_int_rigid_pcs(self):
        """Test the rigid frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(6.1557756577162843e-09)


    def test_cam_qr_int_rigid_rdc(self):
        """Test the rigid frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(0.081171013227160013)


    def test_cam_qr_int_rotor(self):
        """Test the rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(0.075072773007664212)


    def test_cam_qr_int_rotor_pcs(self):
        """Test the rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(1.139566998206629e-06)


    def test_cam_qr_int_rotor_rdc(self):
        """Test the rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(0.075071633440666002)


    def test_cam_qr_int_rotor_2_state(self):
        """Test the 2-state rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags()
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(0.98321958150473276)


    def test_cam_qr_int_rotor_2_state_pcs(self):
        """Test the 2-state rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(2.9152704264897967e-05)


    def test_cam_qr_int_rotor_2_state_rdc(self):
        """Test the 2-state rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(0.98319606148815675)


    def test_cam_qr_int_rotor2(self):
        """Test the second rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(opt=True)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(0.075040490418167072)


    def test_cam_qr_int_rotor2_pcs(self):
        """Test the second rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(1.5787105392036996e-06)


    def test_cam_qr_int_rotor2_rdc(self):
        """Test the second rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(0.075038911707627859)


    def test_cam_quad_int_double_rotor(self):
        """Test the double rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.079828365857374614)


    def test_cam_quad_int_double_rotor_pcs(self):
        """Test the double rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(1.6582207495230563e-05)


    def test_cam_quad_int_double_rotor_rdc(self):
        """Test the double rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'double_rotor.py')
        self.check_chi2(0.079814053829495801)


    def test_cam_quad_int_double_rotor_large_angle(self):
        """Test the double rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.57126501230322546)


    def test_cam_quad_int_double_rotor_large_angle_pcs(self):
        """Test the double rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.5273196608417523)


    def test_cam_quad_int_double_rotor_large_angle_rdc(self):
        """Test the double rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'double_rotor_large_angle.py')
        self.check_chi2(0.043946055085127944)


    def test_cam_quad_int_free_rotor(self):
        """Test the free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.04899586148178818)


    def test_cam_quad_int_free_rotor_missing_data(self):
        """Test the free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor_missing_data.py')
        self.check_chi2(0.037726306126177556)


    def test_cam_quad_int_free_rotor_pcs(self):
        """Test the free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(4.5205576772581238e-08)


    def test_cam_quad_int_free_rotor_rdc(self):
        """Test the free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor.py')
        self.check_chi2(0.04899130610303442)


    def test_cam_quad_int_free_rotor2(self):
        """Test the second free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.06748978555251639)


    def test_cam_quad_int_free_rotor2_pcs(self):
        """Test the second free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.010744719591287448)


    def test_cam_quad_int_free_rotor2_rdc(self):
        """Test the second free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'free_rotor2.py')
        self.check_chi2(0.056744492444430819)


    def test_cam_quad_int_iso_cone(self):
        """Test the isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.041430522432421318)


    def test_cam_quad_int_iso_cone_pcs(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(4.8409613144085089e-08)


    def test_cam_quad_int_iso_cone_rdc(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone.py')
        self.check_chi2(0.041428474106863025)


    def test_cam_quad_int_iso_cone_free_rotor(self):
        """Test the isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.01098760442625833)


    def test_cam_quad_int_iso_cone_free_rotor_pcs(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(1.20136009208203e-06)


    def test_cam_quad_int_iso_cone_free_rotor_rdc(self):
        """Test the isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor.py')
        self.check_chi2(0.010986403066166248)


    def test_cam_quad_int_iso_cone_free_rotor2(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.027527295381115289)


    def test_cam_quad_int_iso_cone_free_rotor2_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.021968348499045869)


    def test_cam_quad_int_iso_cone_free_rotor2_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_free_rotor2.py')
        self.check_chi2(0.0055589468820694179)


    def test_cam_quad_int_iso_cone_torsionless(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.048766438238093554)


    def test_cam_quad_int_iso_cone_torsionless_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(2.2862898875626613e-05)


    def test_cam_quad_int_iso_cone_torsionless_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'iso_cone_torsionless.py')
        self.check_chi2(0.048749202219945678)


    def test_cam_quad_int_pseudo_ellipse(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.033007827805689761)


    def test_cam_quad_int_pseudo_ellipse_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(1.534188648468986e-07)


    def test_cam_quad_int_pseudo_ellipse_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse.py')
        self.check_chi2(0.03300256897164619)


    def test_cam_quad_int_pseudo_ellipse2(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.018129059824815268)


    def test_cam_quad_int_pseudo_ellipse2_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(6.0271332394266001e-07)


    def test_cam_quad_int_pseudo_ellipse2_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse2.py')
        self.check_chi2(0.018129612955648935)


    def test_cam_quad_int_pseudo_ellipse_free_rotor(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.039974493838723132)


    def test_cam_quad_int_pseudo_ellipse_free_rotor_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(2.6524815218336224e-07)


    def test_cam_quad_int_pseudo_ellipse_free_rotor_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_free_rotor.py')
        self.check_chi2(0.039974228590570947)


    def test_cam_quad_int_pseudo_ellipse_torsionless(self):
        """Test the second isotropic cone, free rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.014945243556224312)


    def test_cam_quad_int_pseudo_ellipse_torsionless_pcs(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(3.9260759922047933e-07)


    def test_cam_quad_int_pseudo_ellipse_torsionless_rdc(self):
        """Test the second isotropic cone, free rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'pseudo_ellipse_torsionless.py')
        self.check_chi2(0.014947617377424345)


    def test_cam_quad_int_rigid(self):
        """Test the rigid frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(0.081171019382935666)


    def test_cam_quad_int_rigid_pcs(self):
        """Test the rigid frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(6.1557756577162843e-09)


    def test_cam_quad_int_rigid_rdc(self):
        """Test the rigid frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rigid.py')
        self.check_chi2(0.081171013227160013)


    def test_cam_quad_int_rotor(self):
        """Test the rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(0.075072773007664212)


    def test_cam_quad_int_rotor_pcs(self):
        """Test the rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(1.139566998206629e-06)


    def test_cam_quad_int_rotor_rdc(self):
        """Test the rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor.py')
        self.check_chi2(0.075071633440666002)


    def test_cam_quad_int_rotor_2_state(self):
        """Test the 2-state rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(0.98321958150473276)


    def test_cam_quad_int_rotor_2_state_pcs(self):
        """Test the 2-state rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(2.9152704264897967e-05)


    def test_cam_quad_int_rotor_2_state_rdc(self):
        """Test the 2-state rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor_2_state.py')
        self.check_chi2(0.98319606148815675)


    def test_cam_quad_int_rotor2(self):
        """Test the second rotor frame order model of CaM."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(0.075040490418167072)


    def test_cam_quad_int_rotor2_pcs(self):
        """Test the second rotor frame order model of CaM (with only PCS data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(rdc=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(1.5787105392036996e-06)


    def test_cam_quad_int_rotor2_rdc(self):
        """Test the second rotor frame order model of CaM (with only RDC data)."""

        # The flags, execute the script, and then check the chi2 value.
        self.flags(pcs=False, quad_int=True)
        self.interpreter.run(script_file=self.cam_path+'rotor2.py')
        self.check_chi2(0.075038911707627859)


    def test_count_sobol_points(self):
        """Test the ability of the frame_order.sobol_setup user function to be able to count the number of Sobol' points used for the current parameter values."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Set the number of integration points, and see if they can be counted.
        self.interpreter.frame_order.sobol_setup(20)

        # Check the count.
        self.assertEqual(cdp.sobol_points_used, 20)


    def test_count_sobol_points2(self):
        """Test the frame_order.count_sobol_points user function."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Call the user function.
        self.interpreter.frame_order.count_sobol_points()

        # Check the count.
        self.assertEqual(cdp.sobol_points_used, 20)


    def test_count_sobol_points_free_rotor(self):
        """Test the frame_order.count_sobol_points user function for the free-rotor model."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep+'free_rotor'
        self.interpreter.state.load(data_path+sep+'frame_order')

        # Reset the number of points.
        self.interpreter.frame_order.sobol_setup(20)

        # Call the user function.
        self.interpreter.frame_order.count_sobol_points()

        # Check the count.
        self.assertEqual(cdp.sobol_points_used, 20)


    def test_count_sobol_points_iso_cone_free_rotor(self):
        """Test the frame_order.count_sobol_points user function for the free-rotor isotropic cone model."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep+'iso_cone_free_rotor'
        self.interpreter.state.load(data_path+sep+'frame_order')

        # Reset the number of points.
        self.interpreter.frame_order.sobol_setup(20)

        # Call the user function.
        self.interpreter.frame_order.count_sobol_points()

        # Check the count.
        self.assertEqual(cdp.sobol_points_used, 20)


    def test_count_sobol_points_rigid(self):
        """Test the frame_order.count_sobol_points user function for the rigid model."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep+'rigid'
        self.interpreter.state.load(data_path+sep+'frame_order')

        # Call the user function.
        self.interpreter.frame_order.count_sobol_points()

        # Check the count.
        self.assert_(not hasattr(cdp, 'sobol_points_used'))


    def test_count_sobol_points_rotor(self):
        """Test the frame_order.count_sobol_points user function for the rotor model."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep+'rotor'
        self.interpreter.state.load(data_path+sep+'frame_order')

        # Reset the number of points.
        self.interpreter.frame_order.sobol_setup(20)

        # Call the user function.
        self.interpreter.frame_order.count_sobol_points()

        # Check the count.
        self.assertEqual(cdp.sobol_points_used, 20)


    def test_frame_order_pdb_model_failed_pivot(self):
        """Test the operation of the frame_order.pdb_model user function when the pivot is outside of the PDB limits."""

        # Create a data pipe.
        self.interpreter.pipe.create('frame_order.pdb_model ensemble failure', 'frame order')

        # Load one lactose structure.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=data_path, set_mol_name='lactose')

        # Set the pivot point.
        self.interpreter.frame_order.pivot([-995, 0, 0], fix=True)

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
        self.interpreter.monte_carlo.initial_values()

        # Create the PDB model.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir)


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
        self.interpreter.monte_carlo.initial_values()

        # Create the PDB model.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir)


    def test_generate_rotor2_distribution(self):
        """Generate the rotor2 distribution of CaM."""

        # Execute the script.
        self.interpreter.run(script_file=self.cam_path+'generate_rotor2_distribution.py')


    def test_opendx_map(self):
        """Test the mapping of the Euler angle parameters for OpenDx viewing."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opendx_euler_angle_map.py')


    def test_pdb_model_rotor(self):
        """Check the PDB file created by the frame_order.pdb_model user function for the rotor model."""

        # Create a data pipe.
        self.interpreter.pipe.create(pipe_name='PDB model', pipe_type='frame order')

        # Select the model.
        self.interpreter.frame_order.select_model('rotor')

        # Set the average domain position translation parameters.
        self.interpreter.value.set(param='ave_pos_x', val=0.0)
        self.interpreter.value.set(param='ave_pos_y', val=0.0)
        self.interpreter.value.set(param='ave_pos_z', val=0.0)
        self.interpreter.value.set(param='ave_pos_alpha', val=0.0)
        self.interpreter.value.set(param='ave_pos_beta', val=0.0)
        self.interpreter.value.set(param='ave_pos_gamma', val=0.0)
        self.interpreter.value.set(param='axis_theta', val=0.5)
        self.interpreter.value.set(param='axis_phi', val=0.1)
        self.interpreter.value.set(param='cone_theta', val=0.1)
        self.interpreter.value.set(param='cone_sigma_max', val=0.1)

        # Set the pivot.
        self.interpreter.frame_order.pivot(pivot=[1, 0, 0], fix=True)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir)

        # Read the contents of the file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()


    def test_pseudo_ellipse_zero_cone_angle(self):
        """Catch for a bug in optimisation when the cone_theta_x is set to zero in the pseudo-ellipse models."""

        # Reset.
        self.interpreter.reset()

        # Load the state file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'axis_permutations'
        self.interpreter.state.load(data_path+sep+'cam_pseudo_ellipse')

        # Change the original parameters.
        cdp.cone_theta_x = 0.0
        cdp.cone_theta_y = 2.0

        # Optimisation.
        self.interpreter.minimise.execute('simplex', max_iter=2)


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
        self.assertAlmostEqual(cdp.chi2, 212124.83317383687)


    def test_rigid_data_to_iso_cone_free_rotor_model(self):
        """Test the iso cone, free rotor target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_ISO_CONE_FREE_ROTOR

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 22295.500553417492)


    def test_rigid_data_to_iso_cone_model(self):
        """Test the iso cone target function for the data from a rigid test molecule."""

        # Set the model.
        ds.model = MODEL_ISO_CONE

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'rigid_test.py')

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, 0.01137748706675365, 5)


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
        self.assertAlmostEqual(cdp.chi2, 0.011377491600681364)


    def test_sobol_setup(self):
        """Check the basic operation of the frame_order.sobol_setup user function."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'frame order')

        # Set a number of points.
        self.interpreter.frame_order.sobol_setup(200)


    def test_sobol_setup2(self):
        """Check the operation of the frame_order.sobol_setup user function with just the model specified."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'frame order')

        # Set the model.
        self.interpreter.frame_order.select_model('iso cone')

        # Set a number of points.
        self.interpreter.frame_order.sobol_setup(200)


    def test_sobol_setup3(self):
        """Check the operation of the frame_order.sobol_setup user function with the model and parameters set up."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'frame order')

        # Set the model.
        self.interpreter.frame_order.select_model('iso cone')

        # Set up the system.
        self.interpreter.value.set(param='ave_pos_x', val=0.0)
        self.interpreter.value.set(param='ave_pos_y', val=0.0)
        self.interpreter.value.set(param='ave_pos_z', val=0.0)
        self.interpreter.value.set(param='ave_pos_alpha', val=0.0)
        self.interpreter.value.set(param='ave_pos_beta', val=0.0)
        self.interpreter.value.set(param='ave_pos_gamma', val=0.0)
        self.interpreter.value.set(param='axis_theta', val=0.5)
        self.interpreter.value.set(param='axis_phi', val=0.1)
        self.interpreter.value.set(param='cone_theta', val=0.1)
        self.interpreter.value.set(param='cone_sigma_max', val=0.1)

        # Set a number of points.
        self.interpreter.frame_order.sobol_setup(200)
