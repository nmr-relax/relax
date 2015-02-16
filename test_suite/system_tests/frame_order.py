###############################################################################
#                                                                             #
# Copyright (C) 2006-2015 Edward d'Auvergne                                   #
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
from math import cos, pi, sin, sqrt
import platform
import numpy
from numpy import array, dot, eye, float64, transpose, zeros
from os import sep
from tempfile import mkdtemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from lib.frame_order.conversions import create_rotor_axis_alpha, create_rotor_axis_spherical
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from lib.geometry.coord_transform import cartesian_to_spherical
from lib.geometry.rotations import axis_angle_to_R, euler_to_R_zyz, R_to_euler_zyz
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


# Some vectors.
x_axis = array([1, 0, 0], float64)
y_axis = array([0, 1, 0], float64)
z_axis = array([0, 0, 1], float64)
origin = array([0, 0, 0], float64)


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

        # Call the base class tearDown() method to remove the temporary directory.
        super(Frame_order, self).tearDown()

        # Remove flags from the status object.
        if hasattr(status, 'flag_rdc'):
            del status.flag_rdc
        if hasattr(status, 'flag_pcs'):
            del status.flag_pcs


    def check_chi2(self, chi2=0.0, places=4):
        """Check the function evaluation."""

        # Switch back to the original pipe.
        self.interpreter.pipe.switch('frame order')

        # Test the operation of the statistics.model user function.
        self.interpreter.statistics.model()

        # Get the debugging message.
        mesg = self.mesg_opt_debug()

        # Check the chi2 value.
        self.assertAlmostEqual(cdp.chi2, chi2, places, msg=mesg)


    def check_pdb_model_representation(self, data=None, files=None):
        """Check the PDB model representation atom and residue names and numbers and coordinates.

        Propeller blade atoms with the name 'BLD' are skipped, as well as the cone interior residues with the name 'CON'.


        @keyword data:  The list of data to check.  The first dimension is for the representation, and the second for each atom.  The lists of each atom consist of the residue number, residue name, atom number, atom name, and the 3D position.
        @type data:     list of list of lists
        @keyword files: The list of files for each representation.
        @type files:    list of str
        """

        # Loop over the representations.
        for i in range(len(data)):
            # Delete all structural data.
            self.interpreter.structure.delete()

            # Read the contents of the file.
            self.interpreter.structure.read_pdb(file=files[i], dir=ds.tmpdir)

            # Check the atomic coordinates.
            selection = cdp.structure.selection()
            index = 0
            for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
                # Skip the propeller blades.
                if atom_name == 'BLD':
                    continue

                # Skip the cone interior (checking the edge will be sufficient).
                if res_name == 'CON':
                    continue

                # Checks.
                print("Checking residue %s %s, atom %s %s, at position %s." % (data[i][index][0], data[i][index][1], data[i][index][2], data[i][index][3], data[i][index][4]))
                print("      to residue %s %s, atom %s %s, at position %s." % (res_num, res_name, atom_num, atom_name, pos[0]))
                self.assertEqual(data[i][index][0], res_num)
                self.assertEqual(data[i][index][1], res_name)
                self.assertEqual(data[i][index][2], atom_num)
                self.assertEqual(data[i][index][3], atom_name)
                self.assertAlmostEqual(data[i][index][4][0], pos[0][0], 3)
                self.assertAlmostEqual(data[i][index][4][1], pos[0][1], 3)
                self.assertAlmostEqual(data[i][index][4][2], pos[0][2], 3)

                # Increment the index.
                index += 1


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


    def rotate_from_Z(self, origin=origin, length=0.0, angle=0.0, axis=x_axis, R=None, neg=False):
        """Rotate a vector along Z-axis around the origin.

        @keyword origin:    The origin of the final vector.
        @type origin:       numpy 3D, rank-1 array
        @keyword length:    The length of the Z-vector to rotate.
        @type length:       float
        @keyword angle:     The angle in rad to rotate by.
        @type angle:        float
        @keyword axis:      The direction in the xy-plane to rotate the vector along.
        @type axis:         numpy 3D, rank-1 array
        @keyword R:         A rotation matrix to be used before adding the origin.
        @type R:            numpy 3D, rank-2 array
        @keyword neg:       A flag which if True causes the negative Z-axis to be used.
        @type neg:          bool
        @return:            The final rotated vector shifted by the origin.
        @rtype:             numpy 3D, rank-1 array
        """

        # The final point.
        point = zeros(3, float64)

        # Z-axis reduction.
        point[2] = cos(angle)

        # The X and Y-axis increases.
        point[0] = axis[0]*sin(angle)
        point[1] = axis[1]*sin(angle)

        # Inversion.
        if neg:
            for i in range(3):
                point[i] = -point[i]

        # Rotation.
        if R != None:
            point = dot(R, point)

        # Extend the length and add the origin.
        for i in range(3):
            point[i] = point[i]*length + origin[i]

        # Return the point.
        return point


    def setup_model(self, pipe_name='model', model=None, pivot=None, ave_pos_x=None, ave_pos_y=None, ave_pos_z=None, ave_pos_alpha=None, ave_pos_beta=None, ave_pos_gamma=None, pivot_disp=None, axis_alpha=None, axis_theta=None, axis_phi=None, eigen_alpha=None, eigen_beta=None, eigen_gamma=None, cone_theta=None, cone_theta_x=None, cone_theta_y=None, cone_sigma_max=None, cone_sigma_max_2=None):
        """Set up for the given frame order model.

        This will execute the following user functions:

            - pipe.create to set up a data pipe for the model.
            - frame_order.select_model.
            - value.set for all given parameters.
            - frame_order.pivot to define the pivot point.


        @keyword pipe_name:         The name of the new data pipe.
        @type pipe_name:            str
        @keyword model:             The frame order model to setup.
        @type model:                str
        @keyword pivot:             The pivot to setup.
        @type pivot:                list of float
        @keyword ave_pos_x:         The average domain position X coordinate.
        @type ave_pos_x:            None or float
        @keyword ave_pos_y:         The average domain position Y coordinate.
        @type ave_pos_y:            None or float
        @keyword ave_pos_z:         The average domain position Z coordinate.
        @type ave_pos_z:            None or float
        @keyword ave_pos_alpha:     The average domain position alpha Euler rotation angle.
        @type ave_pos_alpha:        None or float
        @keyword ave_pos_beta:      The average domain position beta Euler rotation angle.
        @type ave_pos_beta:         None or float
        @keyword ave_pos_gamma:     The average domain position gamma Euler rotation angle.
        @type ave_pos_gamma:        None or float
        @keyword pivot_disp:        The pivot displacement parameter.
        @type pivot_disp:           None or float
        @keyword axis_alpha:        The motional eigenframe axis alpha angle.
        @type axis_alpha:           None or float
        @keyword axis_theta:        The motional eigenframe axis theta spherical angle.
        @type axis_theta:           None or float
        @keyword axis_phi:          The motional eigenframe axis phi spherical angle.
        @type axis_phi:             None or float
        @keyword eigen_alpha:       The motional eigenframe alpha Euler rotation angle.
        @type eigen_alpha:          None or float
        @keyword eigen_beta:        The motional eigenframe beta Euler rotation angle.
        @type eigen_beta:           None or float
        @keyword eigen_gamma:       The motional eigenframe gamma Euler rotation angle.
        @type eigen_gamma:          None or float
        @keyword cone_theta:        The isotropic cone opening half angle.
        @type cone_theta:           None or float
        @keyword cone_theta_x:      The x-axis half cone angle.
        @type cone_theta_x:         None or float
        @keyword cone_theta_y:      The y-axis half cone angle.
        @type cone_theta_y:         None or float
        @keyword cone_sigma_max:    The maximum torsion angle.
        @type cone_sigma_max:       None or float
        @keyword cone_sigma_max_2:  The second maximum torsion angle.
        @type cone_sigma_max_2:     None or float
        """

        # Create a data pipe.
        self.interpreter.pipe.create(pipe_name='PDB model', pipe_type='frame order')

        # Create a 8 atom structure with the CoM at [0, 0, 0].
        atom_pos = 100.0 * eye(3)
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='X', res_num=1, pos=atom_pos[0], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='Y', res_num=2, pos=atom_pos[1], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='Z', res_num=3, pos=atom_pos[2], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='nX', res_num=4, pos=-atom_pos[0], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='nY', res_num=5, pos=-atom_pos[1], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='nZ', res_num=6, pos=-atom_pos[2], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='N', res_name='C', res_num=7, pos=[0.0, 0.0, 0.0], element='N')
        self.interpreter.structure.add_atom(mol_name='axes', atom_name='Ti', res_name='O', res_num=8, pos=[0.0, 0.0, 0.0], element='Ti')

        # Set up the domains.
        self.interpreter.domain(id='moving', spin_id=':1-7')
        self.interpreter.domain(id='origin', spin_id=':8')
        self.interpreter.frame_order.ref_domain('origin')

        # Select the model.
        self.interpreter.frame_order.select_model(model)

        # Set the average domain position translation parameters.
        if ave_pos_x != None:
            self.interpreter.value.set(param='ave_pos_x', val=ave_pos_x)
        if ave_pos_y != None:
            self.interpreter.value.set(param='ave_pos_y', val=ave_pos_y)
        if ave_pos_z != None:
            self.interpreter.value.set(param='ave_pos_z', val=ave_pos_z)
        if ave_pos_alpha != None:
            self.interpreter.value.set(param='ave_pos_alpha', val=ave_pos_alpha)
        if ave_pos_beta != None:
            self.interpreter.value.set(param='ave_pos_beta', val=ave_pos_beta)
        if ave_pos_gamma != None:
            self.interpreter.value.set(param='ave_pos_gamma', val=ave_pos_gamma)
        if pivot_disp != None:
            self.interpreter.value.set(param='pivot_disp', val=pivot_disp)
        if axis_alpha != None:
            self.interpreter.value.set(param='axis_alpha', val=axis_alpha)
        if axis_theta != None:
            self.interpreter.value.set(param='axis_theta', val=axis_theta)
        if axis_phi != None:
            self.interpreter.value.set(param='axis_phi', val=axis_phi)
        if eigen_alpha != None:
            self.interpreter.value.set(param='eigen_alpha', val=eigen_alpha)
        if eigen_beta != None:
            self.interpreter.value.set(param='eigen_beta', val=eigen_beta)
        if eigen_gamma != None:
            self.interpreter.value.set(param='eigen_gamma', val=eigen_gamma)
        if cone_theta != None:
            self.interpreter.value.set(param='cone_theta', val=cone_theta)
        if cone_theta_x != None:
            self.interpreter.value.set(param='cone_theta_x', val=cone_theta_x)
        if cone_theta_y != None:
            self.interpreter.value.set(param='cone_theta_y', val=cone_theta_y)
        if cone_sigma_max != None:
            self.interpreter.value.set(param='cone_sigma_max', val=cone_sigma_max)
        if cone_sigma_max_2 != None:
            self.interpreter.value.set(param='cone_sigma_max_2', val=cone_sigma_max_2)

        # Set the pivot.
        self.interpreter.frame_order.pivot(pivot=pivot, fix=True)


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


    def test_distribute_free_rotor_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the free rotor model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_free_rotor_z_axis(type='dist')


    def test_distribute_iso_cone_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the isotropic cone model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_iso_cone_z_axis(type='dist')


    def test_distribute_iso_cone_xz_plane_tilt(self):
        """Check the frame_order.distribute user function PDB file for the isotropic cone model with a xz-plane tilt."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_iso_cone_xz_plane_tilt(type='dist')


    def test_distribute_iso_cone_torsionless_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the torsionless isotropic cone model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_iso_cone_torsionless_z_axis(type='dist')


    def test_distribute_pseudo_ellipse_xz_plane_tilt(self):
        """Check the frame_order.distribute user function PDB file for the pseudo-ellipse model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_pseudo_ellipse_xz_plane_tilt(type='dist')


    def test_distribute_pseudo_ellipse_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the pseudo-ellipse model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_pseudo_ellipse_z_axis(type='dist')


    def test_distribute_pseudo_ellipse_free_rotor_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the free rotor pseudo-ellipse model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_pseudo_ellipse_free_rotor_z_axis(type='dist')


    def test_distribute_pseudo_ellipse_torsionless_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the torsionless pseudo-ellipse model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_pseudo_ellipse_torsionless_z_axis(type='dist')


    def test_distribute_rotor_z_axis(self):
        """Check the frame_order.distribute user function PDB file for the rotor model along the z-axis."""

        # Call the equivalent frame_order.simulate user function system test to do everything.
        self.test_simulate_rotor_z_axis(type='dist')


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
        self.interpreter.frame_order.ref_domain('lactose')

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
        self.interpreter.frame_order.ref_domain('lactose')

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


    def test_pdb_model_double_rotor_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the rotor model along the z-axis."""

        # Init.
        pivot2 = array([1, 0, 0], float64)
        pivot_disp = 100
        pivot1 = pivot2 + (z_axis-x_axis)/sqrt(2.0)*pivot_disp
        l = 20.0

        # The axis parameters, and printout.
        eigen_beta = -pi/4.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='double rotor', pivot=pivot2, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, pivot_disp=pivot_disp, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_sigma_max=0.0, cone_sigma_max_2=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=1, size=l)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        data = [
            # The pivots.
            [ 1, 'PIV',    1, 'Piv1',  pivot1],
            [ 1, 'PIV',    2, 'Piv2',  pivot2],

            # The x-axis rotor.
            [ 1, 'RTX',    3, 'CTR',  pivot2],
            [ 2, 'RTX',    4, 'PRP',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0+eigen_beta)],
            [ 3, 'RTX',    5, 'PRP',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0+eigen_beta, neg=True)],
            [ 4, 'RTB',    6, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0+eigen_beta)],
            [ 5, 'RTB',  188, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0+eigen_beta)],
            [ 6, 'RTB',  370, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0+eigen_beta)],
            [ 7, 'RTB',  552, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0+eigen_beta)],
            [ 8, 'RTB',  734, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0+eigen_beta, neg=True)],
            [ 9, 'RTB',  916, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0+eigen_beta, neg=True)],
            [10, 'RTB', 1098, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0+eigen_beta, neg=True)],
            [11, 'RTB', 1280, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0+eigen_beta, neg=True)],
            [12, 'RTL', 1462, 'x-ax', self.rotate_from_Z(origin=pivot2, length=l+2.0, angle=pi/2.0+eigen_beta)],
            [12, 'RTL', 1463, 'x-ax', self.rotate_from_Z(origin=pivot2, length=l+2.0, angle=pi/2.0+eigen_beta, neg=True)],

            # The y-axis rotor.
            [ 1, 'RTX', 1464, 'CTR',  pivot1],
            [ 2, 'RTX', 1465, 'PRP',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis)],
            [ 3, 'RTX', 1466, 'PRP',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis, neg=True)],
            [ 4, 'RTB', 1467, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis)],
            [ 5, 'RTB', 1649, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis)],
            [ 6, 'RTB', 1831, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis)],
            [ 7, 'RTB', 2013, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis)],
            [ 8, 'RTB', 2195, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis, neg=True)],
            [ 9, 'RTB', 2377, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis, neg=True)],
            [10, 'RTB', 2559, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis, neg=True)],
            [11, 'RTB', 2741, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis, neg=True)],
            [12, 'RTL', 2923, 'y-ax', self.rotate_from_Z(origin=pivot1, length=l+2.0, angle=pi/2.0, axis=y_axis)],
            [12, 'RTL', 2924, 'y-ax', self.rotate_from_Z(origin=pivot1, length=l+2.0, angle=pi/2.0, axis=y_axis, neg=True)],

            # The z-axis.
            [ 1, 'AXE', 2925, 'R',  pivot2],
            [ 1, 'AXE', 2926, 'z-ax', pivot1],
            [ 1, 'AXE', 2927, 'z-ax', (pivot1-pivot2)*1.1+pivot2],
        ]

        # Check the data. 
        self.check_pdb_model_representation(data=[data], files=['frame_order.pdb'])


    def test_pdb_model_double_rotor_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the rotor model along the z-axis."""

        # Init.
        pivot2 = array([1, 0, 0], float64)
        pivot_disp = 100
        pivot1 = pivot2 + z_axis*pivot_disp
        l = 30.0

        # The axis parameters, and printout.
        eigen_beta = 0.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='double rotor', pivot=pivot2, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, pivot_disp=pivot_disp, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_sigma_max=0.0, cone_sigma_max_2=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=1, size=l)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        data = [
            # The pivots.
            [ 1, 'PIV',    1, 'Piv1',  pivot1],
            [ 1, 'PIV',    2, 'Piv2',  pivot2],

            # The x-axis rotor.
            [ 1, 'RTX',    3, 'CTR',  pivot2],
            [ 2, 'RTX',    4, 'PRP',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0)],
            [ 3, 'RTX',    5, 'PRP',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0, neg=True)],
            [ 4, 'RTB',    6, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0)],
            [ 5, 'RTB',  188, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0)],
            [ 6, 'RTB',  370, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0)],
            [ 7, 'RTB',  552, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0)],
            [ 8, 'RTB',  734, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0, neg=True)],
            [ 9, 'RTB',  916, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0, neg=True)],
            [10, 'RTB', 1098, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l, angle=pi/2.0, neg=True)],
            [11, 'RTB', 1280, 'BLO',  self.rotate_from_Z(origin=pivot2, length=l-2.0, angle=pi/2.0, neg=True)],
            [12, 'RTL', 1462, 'x-ax', self.rotate_from_Z(origin=pivot2, length=l+2.0, angle=pi/2.0)],
            [12, 'RTL', 1463, 'x-ax', self.rotate_from_Z(origin=pivot2, length=l+2.0, angle=pi/2.0, neg=True)],

            # The y-axis rotor.
            [ 1, 'RTX', 1464, 'CTR',  pivot1],
            [ 2, 'RTX', 1465, 'PRP',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis)],
            [ 3, 'RTX', 1466, 'PRP',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis, neg=True)],
            [ 4, 'RTB', 1467, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis)],
            [ 5, 'RTB', 1649, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis)],
            [ 6, 'RTB', 1831, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis)],
            [ 7, 'RTB', 2013, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis)],
            [ 8, 'RTB', 2195, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis, neg=True)],
            [ 9, 'RTB', 2377, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis, neg=True)],
            [10, 'RTB', 2559, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l, angle=pi/2.0, axis=y_axis, neg=True)],
            [11, 'RTB', 2741, 'BLO',  self.rotate_from_Z(origin=pivot1, length=l-2.0, angle=pi/2.0, axis=y_axis, neg=True)],
            [12, 'RTL', 2923, 'y-ax', self.rotate_from_Z(origin=pivot1, length=l+2.0, angle=pi/2.0, axis=y_axis)],
            [12, 'RTL', 2924, 'y-ax', self.rotate_from_Z(origin=pivot1, length=l+2.0, angle=pi/2.0, axis=y_axis, neg=True)],

            # The z-axis.
            [ 1, 'AXE', 2925, 'R',  pivot2],
            [ 1, 'AXE', 2926, 'z-ax', pivot1],
            [ 1, 'AXE', 2927, 'z-ax', self.rotate_from_Z(origin=pivot2, length=pivot_disp*1.1, angle=0.0)],
        ]

        # Check the data. 
        self.check_pdb_model_representation(data=[data], files=['frame_order.pdb'])


    def test_pdb_model_free_rotor_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the rotor model with a xz-plane tilt."""

        # Init.
        pivot = array([1, 0, 1], float64)
        l = 100.0

        # The axis alpha parameter, and printout.
        axis_alpha = pi / 2.0
        axis =  create_rotor_axis_alpha(pi/2, pivot, array([0, 0, 0], float64))
        print("\nRotor axis:\n    %s" % axis)
        print("Rotor apex (100*axis + [1, 0, 1]):\n    %s" % (l*axis + pivot))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='free rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_alpha=axis_alpha)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=1, size=100.0)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        data = [
            [ 1, 'PIV',    1, 'Piv',  pivot],
            [ 1, 'RTX',    2, 'CTR',  pivot],
            [ 2, 'RTX',    3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 3, 'RTX',    4, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [ 4, 'RTB',    5, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 5, 'RTB',  187, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 6, 'RTB',  369, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 7, 'RTB',  551, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 8, 'RTB',  733, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [ 9, 'RTB',  915, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [10, 'RTB', 1097, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [11, 'RTB', 1279, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [12, 'RTL', 1461, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=-pi/4.0)],
            [12, 'RTL', 1462, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=-pi/4.0, neg=True)]
        ]

        # Check the data. 
        self.check_pdb_model_representation(data=[data], files=['frame_order.pdb'])


    def test_pdb_model_free_rotor_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the free rotor model along the z-axis."""

        # Init.
        pivot = array([1, 0, 0], float64)
        l = 30.0

        # The axis alpha parameter, and printout.
        axis_alpha = pi / 2.0
        axis = create_rotor_axis_alpha(pi/2, pivot, array([0, 0, 0], float64))
        print("\nRotor axis:  %s" % axis)
        print("Rotor apex (100*axis + [1, 0, 0]):\n    %s" % (l*axis + pivot))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='free rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_alpha=axis_alpha)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=1, size=l)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        data = [
            [ 1, 'PIV',    1, 'Piv',  pivot],
            [ 1, 'RTX',    2, 'CTR',  pivot],
            [ 2, 'RTX',    3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 3, 'RTX',    4, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [ 4, 'RTB',    5, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 5, 'RTB',  187, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 6, 'RTB',  369, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 7, 'RTB',  551, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 8, 'RTB',  733, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [ 9, 'RTB',  915, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [10, 'RTB', 1097, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [11, 'RTB', 1279, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [12, 'RTL', 1461, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=0.0)],
            [12, 'RTL', 1462, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=0.0, neg=True)]
        ]

        # Check the data. 
        self.check_pdb_model_representation(data=[data], files=['frame_order.pdb'])


    def test_pdb_model_iso_cone_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the isotropic cone model with a xz-plane tilt."""

        # Init.
        theta = 2.0
        pivot = array([1, 1, 1], float64)
        l = 45.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        axis_theta = -pi/4.0
        axis = create_rotor_axis_spherical(axis_theta, 0.0)
        print("Rotor axis:  %s" % axis)
        R = zeros((3, 3), float64)
        axis_angle_to_R([0, 1, 0], axis_theta, R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=theta, cone_sigma_max=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=axis_theta, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=axis_theta, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=axis_theta, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 733, 'APX',  pivot],
                [ 3, 'CNE', 734, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[0], R=R, neg=neg[i])],
                [ 3, 'CNE', 735, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[1], R=R, neg=neg[i])],
                [ 3, 'CNE', 736, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[2], R=R, neg=neg[i])],
                [ 3, 'CNE', 737, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[3], R=R, neg=neg[i])],
                [ 3, 'CNE', 738, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[4], R=R, neg=neg[i])],
                [ 3, 'CNE', 739, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[5], R=R, neg=neg[i])],
                [ 3, 'CNE', 740, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[6], R=R, neg=neg[i])],
                [ 3, 'CNE', 741, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[7], R=R, neg=neg[i])],
                [ 3, 'CNE', 742, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[8], R=R, neg=neg[i])],
                [ 3, 'CNE', 743, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[9], R=R, neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 804, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=axis_theta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_iso_cone_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the isotropic cone model along the z-axis."""

        # Init.
        theta = 2.0
        pivot = array([1, 0, -2], float64)
        l = 25.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        axis_theta = 0.0
        print("Rotor axis:  %s" % create_rotor_axis_spherical(axis_theta, 0.0))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=theta, cone_sigma_max=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=axis_theta, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=axis_theta, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=axis_theta, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 733, 'APX',  pivot],
                [ 3, 'CNE', 734, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[0], neg=neg[i])],
                [ 3, 'CNE', 735, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[1], neg=neg[i])],
                [ 3, 'CNE', 736, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[2], neg=neg[i])],
                [ 3, 'CNE', 737, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[3], neg=neg[i])],
                [ 3, 'CNE', 738, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[4], neg=neg[i])],
                [ 3, 'CNE', 739, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[5], neg=neg[i])],
                [ 3, 'CNE', 740, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[6], neg=neg[i])],
                [ 3, 'CNE', 741, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[7], neg=neg[i])],
                [ 3, 'CNE', 742, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[8], neg=neg[i])],
                [ 3, 'CNE', 743, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[9], neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 804, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=axis_theta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_iso_cone_free_rotor_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the free rotor isotropic cone model with a xz-plane tilt."""

        # Init.
        theta = 2.0
        pivot = array([1, 1, 1], float64)
        l = 40.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        axis_theta = -pi/4.0
        axis = create_rotor_axis_spherical(axis_theta, 0.0)
        print("Rotor axis:  %s" % axis)
        R = zeros((3, 3), float64)
        axis_angle_to_R([0, 1, 0], axis_theta, R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone, free rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=theta)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=axis_theta, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 733, 'APX',  pivot],
                [ 3, 'CNE', 734, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[0], R=R, neg=neg[i])],
                [ 3, 'CNE', 735, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[1], R=R, neg=neg[i])],
                [ 3, 'CNE', 736, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[2], R=R, neg=neg[i])],
                [ 3, 'CNE', 737, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[3], R=R, neg=neg[i])],
                [ 3, 'CNE', 738, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[4], R=R, neg=neg[i])],
                [ 3, 'CNE', 739, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[5], R=R, neg=neg[i])],
                [ 3, 'CNE', 740, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[6], R=R, neg=neg[i])],
                [ 3, 'CNE', 741, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[7], R=R, neg=neg[i])],
                [ 3, 'CNE', 742, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[8], R=R, neg=neg[i])],
                [ 3, 'CNE', 743, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[9], R=R, neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 804, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=axis_theta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_iso_cone_free_rotor_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the free rotor isotropic cone model along the z-axis."""

        # Init.
        theta = 2.0
        pivot = array([1, 0, -2], float64)
        l = 25.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        axis_theta = 0.0
        axis_phi = 0.0
        print("Rotor axis:  %s" % create_rotor_axis_spherical(axis_theta, axis_phi))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone, free rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=theta)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=axis_theta, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=axis_theta, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 733, 'APX',  pivot],
                [ 3, 'CNE', 734, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[0], neg=neg[i])],
                [ 3, 'CNE', 735, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[1], neg=neg[i])],
                [ 3, 'CNE', 736, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[2], neg=neg[i])],
                [ 3, 'CNE', 737, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[3], neg=neg[i])],
                [ 3, 'CNE', 738, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[4], neg=neg[i])],
                [ 3, 'CNE', 739, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[5], neg=neg[i])],
                [ 3, 'CNE', 740, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[6], neg=neg[i])],
                [ 3, 'CNE', 741, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[7], neg=neg[i])],
                [ 3, 'CNE', 742, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[8], neg=neg[i])],
                [ 3, 'CNE', 743, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[9], neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 804, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=axis_theta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_iso_cone_torsionless_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the torsionless isotropic cone model with a xz-plane tilt."""

        # Init.
        theta = 2.0
        pivot = array([1, 1, 1], float64)
        l = 40.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        axis_theta = -pi/4.0
        axis = create_rotor_axis_spherical(axis_theta, 0.0)
        print("Rotor axis:  %s" % axis)
        R = zeros((3, 3), float64)
        axis_angle_to_R([0, 1, 0], axis_theta, R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone, torsionless', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=theta)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The axis system.
                [ 2, 'AXE',   2, 'R',  pivot],
                [ 2, 'AXE',   3, 'z-ax', self.rotate_from_Z(origin=pivot, length=l, angle=axis_theta, neg=neg[i])],
                [ 2, 'AXE',   4, 'z-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=axis_theta, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE',   5, 'APX',  pivot],
                [ 3, 'CNE',   6, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[0], R=R, neg=neg[i])],
                [ 3, 'CNE',   7, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[1], R=R, neg=neg[i])],
                [ 3, 'CNE',   8, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[2], R=R, neg=neg[i])],
                [ 3, 'CNE',   9, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[3], R=R, neg=neg[i])],
                [ 3, 'CNE',  10, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[4], R=R, neg=neg[i])],
                [ 3, 'CNE',  11, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[5], R=R, neg=neg[i])],
                [ 3, 'CNE',  12, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[6], R=R, neg=neg[i])],
                [ 3, 'CNE',  13, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[7], R=R, neg=neg[i])],
                [ 3, 'CNE',  14, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[8], R=R, neg=neg[i])],
                [ 3, 'CNE',  15, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[9], R=R, neg=neg[i])],

                # Titles.
                [ 1, 'TLE',  76, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=axis_theta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_iso_cone_torsionless_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the torsionless isotropic cone model along the z-axis."""

        # Init.
        theta = 2.0
        pivot = array([1, 0, -2], float64)
        l = 25.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        axis_theta = 0.0
        print("Rotor axis:  %s" % create_rotor_axis_spherical(axis_theta, 0.0))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone, torsionless', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=theta)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The axis system.
                [ 2, 'AXE',   2, 'R',  pivot],
                [ 2, 'AXE',   3, 'z-ax', self.rotate_from_Z(origin=pivot, length=l, angle=axis_theta, neg=neg[i])],
                [ 2, 'AXE',   4, 'z-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=axis_theta, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE',   5, 'APX',  pivot],
                [ 3, 'CNE',   6, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[0], neg=neg[i])],
                [ 3, 'CNE',   7, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[1], neg=neg[i])],
                [ 3, 'CNE',   8, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[2], neg=neg[i])],
                [ 3, 'CNE',   9, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[3], neg=neg[i])],
                [ 3, 'CNE',  10, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[4], neg=neg[i])],
                [ 3, 'CNE',  11, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[5], neg=neg[i])],
                [ 3, 'CNE',  12, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[6], neg=neg[i])],
                [ 3, 'CNE',  13, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[7], neg=neg[i])],
                [ 3, 'CNE',  14, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[8], neg=neg[i])],
                [ 3, 'CNE',  15, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta, axis=vectors[9], neg=neg[i])],

                # Titles.
                [ 1, 'TLE',  76, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=axis_theta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_pseudo_ellipse_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the pseudo-ellipse model with a xz-plane tilt."""

        # Init.
        theta_x = 2.0
        theta_y = 0.1
        pivot = array([1, -2, 1.1], float64)
        l = 50.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        eigen_beta = -pi/2.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=theta_x, cone_theta_y=theta_y, cone_sigma_max=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors and angles.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        theta_max = zeros(10, float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

            # The cone opening angle.
            theta_max[i] = theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=eigen_beta, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=eigen_beta, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=eigen_beta, neg=neg[i])],

                # The axis system.
                [ 1, 'AXE', 733, 'R',  pivot],
                [ 2, 'AXE', 734, 'R',  pivot],
                [ 2, 'AXE', 735, 'x-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0+eigen_beta, neg=neg[i])],
                [ 2, 'AXE', 736, 'x-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0+eigen_beta, neg=neg[i])],
                [ 2, 'AXE', 737, 'R',  pivot],
                [ 2, 'AXE', 738, 'y-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, axis=y_axis, neg=neg[i])],
                [ 2, 'AXE', 739, 'y-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, axis=y_axis, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 740, 'APX',  pivot],
                [ 3, 'CNE', 741, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[0], axis=vectors[0], R=R, neg=neg[i])],
                [ 3, 'CNE', 742, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[1], axis=vectors[1], R=R, neg=neg[i])],
                [ 3, 'CNE', 743, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[2], axis=vectors[2], R=R, neg=neg[i])],
                [ 3, 'CNE', 744, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[3], axis=vectors[3], R=R, neg=neg[i])],
                [ 3, 'CNE', 745, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[4], axis=vectors[4], R=R, neg=neg[i])],
                [ 3, 'CNE', 746, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[5], axis=vectors[5], R=R, neg=neg[i])],
                [ 3, 'CNE', 747, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[6], axis=vectors[6], R=R, neg=neg[i])],
                [ 3, 'CNE', 748, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[7], axis=vectors[7], R=R, neg=neg[i])],
                [ 3, 'CNE', 749, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[8], axis=vectors[8], R=R, neg=neg[i])],
                [ 3, 'CNE', 750, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[9], axis=vectors[9], R=R, neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 811, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=eigen_beta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_pseudo_ellipse_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the pseudo-ellipse model along the z-axis."""

        # Init.
        theta_x = 2.0
        theta_y = 0.1
        pivot = array([1, 1, 1], float64)
        l = 40.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        eigen_beta = 0.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=theta_x, cone_theta_y=theta_y, cone_sigma_max=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors and angles.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        theta_max = zeros(10, float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

            # The cone opening angle.
            theta_max[i] = theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=0.0, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor-2.0, angle=0.0, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=0.0, neg=neg[i])],

                # The axis system.
                [ 1, 'AXE', 733, 'R',  pivot],
                [ 2, 'AXE', 734, 'R',  pivot],
                [ 2, 'AXE', 735, 'x-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, neg=neg[i])],
                [ 2, 'AXE', 736, 'x-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, neg=neg[i])],
                [ 2, 'AXE', 737, 'R',  pivot],
                [ 2, 'AXE', 738, 'y-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, axis=y_axis, neg=neg[i])],
                [ 2, 'AXE', 739, 'y-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, axis=y_axis, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 740, 'APX',  pivot],
                [ 3, 'CNE', 741, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[0], axis=vectors[0], neg=neg[i])],
                [ 3, 'CNE', 742, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[1], axis=vectors[1], neg=neg[i])],
                [ 3, 'CNE', 743, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[2], axis=vectors[2], neg=neg[i])],
                [ 3, 'CNE', 744, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[3], axis=vectors[3], neg=neg[i])],
                [ 3, 'CNE', 745, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[4], axis=vectors[4], neg=neg[i])],
                [ 3, 'CNE', 746, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[5], axis=vectors[5], neg=neg[i])],
                [ 3, 'CNE', 747, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[6], axis=vectors[6], neg=neg[i])],
                [ 3, 'CNE', 748, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[7], axis=vectors[7], neg=neg[i])],
                [ 3, 'CNE', 749, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[8], axis=vectors[8], neg=neg[i])],
                [ 3, 'CNE', 750, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[9], axis=vectors[9], neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 811, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=0.0, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_pseudo_ellipse_free_rotor_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the free rotor pseudo-ellipse model with a xz-plane tilt."""

        # Init.
        theta_x = 2.0
        theta_y = 0.1
        pivot = array([1, -2, 1.1], float64)
        l = 50.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        eigen_beta = -pi/2.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse, free rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=theta_x, cone_theta_y=theta_y)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors and angles.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        theta_max = zeros(10, float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

            # The cone opening angle.
            theta_max[i] = theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=eigen_beta, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=eigen_beta, neg=neg[i])],

                # The axis system.
                [ 1, 'AXE', 733, 'R',  pivot],
                [ 2, 'AXE', 734, 'R',  pivot],
                [ 2, 'AXE', 735, 'x-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0+eigen_beta, neg=neg[i])],
                [ 2, 'AXE', 736, 'x-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0+eigen_beta, neg=neg[i])],
                [ 2, 'AXE', 737, 'R',  pivot],
                [ 2, 'AXE', 738, 'y-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, axis=y_axis, neg=neg[i])],
                [ 2, 'AXE', 739, 'y-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, axis=y_axis, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 740, 'APX',  pivot],
                [ 3, 'CNE', 741, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[0], axis=vectors[0], R=R, neg=neg[i])],
                [ 3, 'CNE', 742, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[1], axis=vectors[1], R=R, neg=neg[i])],
                [ 3, 'CNE', 743, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[2], axis=vectors[2], R=R, neg=neg[i])],
                [ 3, 'CNE', 744, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[3], axis=vectors[3], R=R, neg=neg[i])],
                [ 3, 'CNE', 745, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[4], axis=vectors[4], R=R, neg=neg[i])],
                [ 3, 'CNE', 746, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[5], axis=vectors[5], R=R, neg=neg[i])],
                [ 3, 'CNE', 747, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[6], axis=vectors[6], R=R, neg=neg[i])],
                [ 3, 'CNE', 748, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[7], axis=vectors[7], R=R, neg=neg[i])],
                [ 3, 'CNE', 749, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[8], axis=vectors[8], R=R, neg=neg[i])],
                [ 3, 'CNE', 750, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[9], axis=vectors[9], R=R, neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 811, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=eigen_beta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_pseudo_ellipse_free_rotor_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the free rotor pseudo-ellipse model along the z-axis."""

        # Init.
        theta_x = 2.0
        theta_y = 0.1
        pivot = array([1, 1, 1], float64)
        l = 40.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        eigen_beta = 0.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse, free rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=theta_x, cone_theta_y=theta_y)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors and angles.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        theta_max = zeros(10, float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

            # The cone opening angle.
            theta_max[i] = theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The rotor.
                [ 1, 'RTX',   2, 'CTR',  pivot],
                [ 2, 'RTX',   3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 3, 'RTB',   4, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 4, 'RTB', 186, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 5, 'RTB', 368, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 6, 'RTB', 550, 'BLO',  self.rotate_from_Z(origin=pivot, length=l_rotor, angle=0.0, neg=neg[i])],
                [ 7, 'RTL', 732, 'z-ax', self.rotate_from_Z(origin=pivot, length=l_rotor+2.0, angle=0.0, neg=neg[i])],

                # The axis system.
                [ 1, 'AXE', 733, 'R',  pivot],
                [ 2, 'AXE', 734, 'R',  pivot],
                [ 2, 'AXE', 735, 'x-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, neg=neg[i])],
                [ 2, 'AXE', 736, 'x-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, neg=neg[i])],
                [ 2, 'AXE', 737, 'R',  pivot],
                [ 2, 'AXE', 738, 'y-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, axis=y_axis, neg=neg[i])],
                [ 2, 'AXE', 739, 'y-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, axis=y_axis, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE', 740, 'APX',  pivot],
                [ 3, 'CNE', 741, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[0], axis=vectors[0], neg=neg[i])],
                [ 3, 'CNE', 742, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[1], axis=vectors[1], neg=neg[i])],
                [ 3, 'CNE', 743, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[2], axis=vectors[2], neg=neg[i])],
                [ 3, 'CNE', 744, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[3], axis=vectors[3], neg=neg[i])],
                [ 3, 'CNE', 745, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[4], axis=vectors[4], neg=neg[i])],
                [ 3, 'CNE', 746, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[5], axis=vectors[5], neg=neg[i])],
                [ 3, 'CNE', 747, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[6], axis=vectors[6], neg=neg[i])],
                [ 3, 'CNE', 748, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[7], axis=vectors[7], neg=neg[i])],
                [ 3, 'CNE', 749, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[8], axis=vectors[8], neg=neg[i])],
                [ 3, 'CNE', 750, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[9], axis=vectors[9], neg=neg[i])],

                # Titles.
                [ 1, 'TLE', 811, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=0.0, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_pseudo_ellipse_torsionless_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the torsionless pseudo-ellipse model with a xz-plane tilt."""

        # Init.
        theta_x = 2.0
        theta_y = 0.1
        pivot = array([1, -2, 1.1], float64)
        l = 50.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        eigen_beta = -pi/2.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse, torsionless', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=theta_x, cone_theta_y=theta_y)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors and angles.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        theta_max = zeros(10, float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

            # The cone opening angle.
            theta_max[i] = theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The axis system.
                [ 1, 'AXE',   2, 'R',  pivot],
                [ 2, 'AXE',   3, 'R',  pivot],
                [ 2, 'AXE',   4, 'x-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, R=R, neg=neg[i])],
                [ 2, 'AXE',   5, 'x-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, R=R, neg=neg[i])],
                [ 2, 'AXE',   6, 'R',  pivot],
                [ 2, 'AXE',   7, 'y-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, axis=y_axis, R=R, neg=neg[i])],
                [ 2, 'AXE',   8, 'y-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, axis=y_axis, R=R, neg=neg[i])],
                [ 2, 'AXE',   9, 'R',  pivot],
                [ 2, 'AXE',  10, 'z-ax', self.rotate_from_Z(origin=pivot, length=l, angle=0.0, R=R, neg=neg[i])],
                [ 2, 'AXE',  11, 'z-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=0.0, R=R, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE',  12, 'APX',  pivot],
                [ 3, 'CNE',  13, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[0], axis=vectors[0], R=R, neg=neg[i])],
                [ 3, 'CNE',  14, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[1], axis=vectors[1], R=R, neg=neg[i])],
                [ 3, 'CNE',  15, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[2], axis=vectors[2], R=R, neg=neg[i])],
                [ 3, 'CNE',  16, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[3], axis=vectors[3], R=R, neg=neg[i])],
                [ 3, 'CNE',  17, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[4], axis=vectors[4], R=R, neg=neg[i])],
                [ 3, 'CNE',  18, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[5], axis=vectors[5], R=R, neg=neg[i])],
                [ 3, 'CNE',  19, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[6], axis=vectors[6], R=R, neg=neg[i])],
                [ 3, 'CNE',  20, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[7], axis=vectors[7], R=R, neg=neg[i])],
                [ 3, 'CNE',  21, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[8], axis=vectors[8], R=R, neg=neg[i])],
                [ 3, 'CNE',  22, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[9], axis=vectors[9], R=R, neg=neg[i])],

                # Titles.
                [ 1, 'TLE',  83, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=eigen_beta, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_pseudo_ellipse_torsionless_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the torsionless pseudo-ellipse model along the z-axis."""

        # Init.
        theta_x = 2.0
        theta_y = 0.1
        pivot = array([1, 1, 1], float64)
        l = 40.0
        l_rotor = l + 5.0

        # The axis parameters, and printout.
        eigen_beta = 0.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse, torsionless', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=theta_x, cone_theta_y=theta_y)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=10, size=l)

        # The xy-plane vectors and angles.
        inc = 2.0 * pi / 10.0
        vectors = zeros((10, 3), float64)
        theta_max = zeros(10, float64)
        for i in range(10):
            # The angle phi.
            phi = inc * i

            # The xy-plane, starting along the x-axis.
            vectors[i, 0] = cos(phi)
            vectors[i, 1] = sin(phi)

            # The cone opening angle.
            theta_max[i] = theta_x * theta_y / sqrt((cos(phi)*theta_y)**2 + (sin(phi)*theta_x)**2)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        neg = [False, True]
        tle = ['a', 'b']
        data = []
        for i in range(2):
            data.append([
                # The pivot.
                [ 1, 'PIV',   1, 'Piv',  pivot],

                # The axis system.
                [ 1, 'AXE',   2, 'R',  pivot],
                [ 2, 'AXE',   3, 'R',  pivot],
                [ 2, 'AXE',   4, 'x-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, neg=neg[i])],
                [ 2, 'AXE',   5, 'x-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, neg=neg[i])],
                [ 2, 'AXE',   6, 'R',  pivot],
                [ 2, 'AXE',   7, 'y-ax', self.rotate_from_Z(origin=pivot, length=l, angle=pi/2.0, axis=y_axis, neg=neg[i])],
                [ 2, 'AXE',   8, 'y-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=pi/2.0, axis=y_axis, neg=neg[i])],
                [ 2, 'AXE',   9, 'R',  pivot],
                [ 2, 'AXE',  10, 'z-ax', self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=neg[i])],
                [ 2, 'AXE',  11, 'z-ax', self.rotate_from_Z(origin=pivot, length=l*1.1, angle=0.0, neg=neg[i])],

                # The cone edge.
                [ 3, 'CNE',  12, 'APX',  pivot],
                [ 3, 'CNE',  13, 'H2',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[0], axis=vectors[0], neg=neg[i])],
                [ 3, 'CNE',  14, 'H3',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[1], axis=vectors[1], neg=neg[i])],
                [ 3, 'CNE',  15, 'H4',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[2], axis=vectors[2], neg=neg[i])],
                [ 3, 'CNE',  16, 'H5',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[3], axis=vectors[3], neg=neg[i])],
                [ 3, 'CNE',  17, 'H6',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[4], axis=vectors[4], neg=neg[i])],
                [ 3, 'CNE',  18, 'H7',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[5], axis=vectors[5], neg=neg[i])],
                [ 3, 'CNE',  19, 'H8',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[6], axis=vectors[6], neg=neg[i])],
                [ 3, 'CNE',  20, 'H9',   self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[7], axis=vectors[7], neg=neg[i])],
                [ 3, 'CNE',  21, 'H10',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[8], axis=vectors[8], neg=neg[i])],
                [ 3, 'CNE',  22, 'H11',  self.rotate_from_Z(origin=pivot, length=l, angle=theta_max[9], axis=vectors[9], neg=neg[i])],

                # Titles.
                [ 1, 'TLE',  83, tle[i], self.rotate_from_Z(origin=pivot, length=l+10, angle=0.0, neg=neg[i])]
            ])

        # Check the data. 
        self.check_pdb_model_representation(data=data, files=['frame_order_A.pdb', 'frame_order_B.pdb'])


    def test_pdb_model_rotor_xz_plane_tilt(self):
        """Check the frame_order.pdb_model user function PDB file for the rotor model with a xz-plane tilt."""

        # Init.
        pivot = array([1, 0, 1], float64)
        l = 100.0

        # The axis alpha parameter, and printout.
        axis_alpha = pi / 2.0
        axis =  create_rotor_axis_alpha(pi/2, pivot, array([0, 0, 0], float64))
        print("\nRotor axis:\n    %s" % axis)
        print("Rotor apex (100*axis + [1, 0, 1]):\n    %s" % (l*axis + pivot))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_alpha=axis_alpha, cone_sigma_max=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=1, size=100.0)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        data = [
            [ 1, 'PIV',    1, 'Piv',  pivot],
            [ 1, 'RTX',    2, 'CTR',  pivot],
            [ 2, 'RTX',    3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 3, 'RTX',    4, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [ 4, 'RTB',    5, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 5, 'RTB',  187, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=-pi/4.0)],
            [ 6, 'RTB',  369, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0)],
            [ 7, 'RTB',  551, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=-pi/4.0)],
            [ 8, 'RTB',  733, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [ 9, 'RTB',  915, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=-pi/4.0, neg=True)],
            [10, 'RTB', 1097, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=-pi/4.0, neg=True)],
            [11, 'RTB', 1279, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=-pi/4.0, neg=True)],
            [12, 'RTL', 1461, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=-pi/4.0)],
            [12, 'RTL', 1462, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=-pi/4.0, neg=True)]
        ]

        # Check the data. 
        self.check_pdb_model_representation(data=[data], files=['frame_order.pdb'])


    def test_pdb_model_rotor_z_axis(self):
        """Check the frame_order.pdb_model user function PDB file for the rotor model along the z-axis."""

        # Init.
        pivot = array([1, 0, 0], float64)
        l = 30.0

        # The axis alpha parameter, and printout.
        axis_alpha = pi / 2.0
        axis = create_rotor_axis_alpha(pi/2, pivot, array([0, 0, 0], float64))
        print("\nRotor axis:  %s" % axis)
        print("Rotor apex (100*axis + [1, 0, 0]):\n    %s" % (l*axis + pivot))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='rotor', pivot=pivot, ave_pos_x=0.0, ave_pos_y=0.0, ave_pos_z=0.0, ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_alpha=axis_alpha, cone_sigma_max=0.0)

        # Create the PDB.
        self.interpreter.frame_order.pdb_model(dir=ds.tmpdir, inc=1, size=l)

        # The data, as it should be with everything along the z-axis, shifted from the origin to the pivot.
        data = [
            [ 1, 'PIV',    1, 'Piv',  pivot],
            [ 1, 'RTX',    2, 'CTR',  pivot],
            [ 2, 'RTX',    3, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 3, 'RTX',    4, 'PRP',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [ 4, 'RTB',    5, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 5, 'RTB',  187, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=0.0)],
            [ 6, 'RTB',  369, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0)],
            [ 7, 'RTB',  551, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=0.0)],
            [ 8, 'RTB',  733, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [ 9, 'RTB',  915, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=0.0, neg=True)],
            [10, 'RTB', 1097, 'BLO',  self.rotate_from_Z(origin=pivot, length=l, angle=0.0, neg=True)],
            [11, 'RTB', 1279, 'BLO',  self.rotate_from_Z(origin=pivot, length=l-2.0, angle=0.0, neg=True)],
            [12, 'RTL', 1461, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=0.0)],
            [12, 'RTL', 1462, 'z-ax', self.rotate_from_Z(origin=pivot, length=l+2.0, angle=0.0, neg=True)]
        ]

        # Check the data. 
        self.check_pdb_model_representation(data=[data], files=['frame_order.pdb'])


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


    def test_simulate_double_rotor_mode1_xz_plane_tilt(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the double rotor model with a xz-plane tilt for the first rotation mode."""

        # Init.
        cone_sigma_max = pi / 2.0
        cone_sigma_max_2 = 0.0
        pivot = array([20, 20, -20], float64)
        l = 100.0
        sim_num = 500
        pivot_disp = 100.0

        # The eigenframe.
        eigen_beta = -pi/4.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='double rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=eigen_beta, ave_pos_gamma=0.0, pivot_disp=pivot_disp, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_sigma_max=cone_sigma_max, cone_sigma_max_2=cone_sigma_max_2)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # X vector maxima.
        X_theta_min = cartesian_to_spherical([100, 0, 200])[1]
        X_theta_max = cartesian_to_spherical([-100, 0, 0])[1] + pi
        print("X vector theta range of [%.5f, %.5f]" % (X_theta_min, X_theta_max))

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(dot(transpose(R), new_pos))

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # Check the X and nX vectors.
                if res_name in ['X', 'nX']:
                    self.assert_(theta >= X_theta_min - epsilon)
                    self.assert_(theta <= X_theta_max + epsilon)
                    if phi < 0.1:
                        self.assertAlmostEqual(phi, 0.0, 3)
                    else:
                        self.assertAlmostEqual(phi, pi, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assert_(theta >= pi/4.0 - epsilon)
                    self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], 100.0, 3)

                # Check the Z vector (should not move).
                elif res_name == 'Z':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assertAlmostEqual(new_pos[0], -70.711, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 70.711, 3)

                # Check the nY vector.
                elif res_name == 'nY':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assert_(theta >= pi/4.0 - epsilon)
                    self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], -100.0, 3)

                # Check the nZ vector (should not move).
                elif res_name == 'nZ':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assert_(theta >= pi/4.0 - epsilon)
                    self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)

                # Check the centre.
                elif res_name == 'C':
                    self.assert_(r/100.0 <= 1.4142135623730951 + epsilon)
                    if not (new_pos[0] == 0.0 and new_pos[1] == 0.0 and new_pos[2] == 0.0):
                        self.assert_(theta >= pi/4.0 - epsilon)
                        self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)

                # Check the origin.
                elif res_name == '0':
                    self.assertAlmostEqual(r, 34.641016151377549, 4)
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)


    def test_simulate_double_rotor_mode1_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the double rotor model along the z-axis for the first rotation mode."""

        # Init.
        cone_sigma_max = pi / 2.0
        cone_sigma_max_2 = 0.0
        pivot = array([20, 20, -20], float64)
        l = 100.0
        sim_num = 500
        pivot_disp = 100.0

        # The eigenframe.
        eigen_beta = 0.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='double rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=eigen_beta, ave_pos_gamma=0.0, pivot_disp=pivot_disp, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_sigma_max=cone_sigma_max, cone_sigma_max_2=cone_sigma_max_2)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # X vector maxima.
        X_theta_min = cartesian_to_spherical([100, 0, 200])[1]
        X_theta_max = cartesian_to_spherical([-100, 0, 0])[1] + pi
        print("X vector theta range of [%.5f, %.5f]" % (X_theta_min, X_theta_max))

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # Check the X and nX vectors.
                if res_name in ['X', 'nX']:
                    self.assert_(theta >= X_theta_min - epsilon)
                    self.assert_(theta <= X_theta_max + epsilon)
                    if phi < 0.1:
                        self.assertAlmostEqual(phi, 0.0, 3)
                    else:
                        self.assertAlmostEqual(phi, pi, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assert_(theta >= pi/4.0 - epsilon)
                    self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], 100.0, 3)

                # Check the Z vector (should not move).
                elif res_name == 'Z':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 100.0, 3)

                # Check the nY vector.
                elif res_name == 'nY':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assert_(theta >= pi/4.0 - epsilon)
                    self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], -100.0, 3)

                # Check the nZ vector (should not move).
                elif res_name == 'nZ':
                    self.assert_(r/100.0 >= 1.0 - epsilon)
                    self.assert_(theta >= pi/4.0 - epsilon)
                    self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)

                # Check the centre.
                elif res_name == 'C':
                    self.assert_(r/100.0 <= 1.4142135623730951 + epsilon)
                    if not (new_pos[0] == 0.0 and new_pos[1] == 0.0 and new_pos[2] == 0.0):
                        self.assert_(theta >= pi/4.0 - epsilon)
                        self.assert_(theta <= 2.0*pi - pi/4.0 + epsilon)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)

                # Check the origin.
                elif res_name == '0':
                    self.assertAlmostEqual(r, 34.641016151377549, 4)
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)


    def test_simulate_double_rotor_mode2_xz_plane_tilt(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the double rotor model with a xz-plane tilt for the second rotation mode."""

        # Init.
        cone_sigma_max = 0.0
        cone_sigma_max_2 = pi / 2.0
        pivot = array([20, 20, -20], float64)
        l = 100.0
        sim_num = 500
        pivot_disp = 100.0

        # The eigenframe.
        eigen_beta = -pi/4.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='double rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=eigen_beta, ave_pos_gamma=0.0, pivot_disp=pivot_disp, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_sigma_max=cone_sigma_max, cone_sigma_max_2=cone_sigma_max_2)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(dot(transpose(R), new_pos))

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # Check the X vector.
                if res_name == 'X':
                    self.assertAlmostEqual(new_pos[0], 70.711, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 70.711, 3)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assert_(new_pos[0] >= -70.711 - epsilon)
                    self.assert_(new_pos[0] <= 70.711 + epsilon)
                    self.assert_(new_pos[1] >= 0.0 - epsilon)
                    self.assert_(new_pos[1] <= 100.0 + epsilon)
                    self.assert_(new_pos[2] >= -70.711 - epsilon)
                    self.assert_(new_pos[2] <= 70.711 + epsilon)

                # Check the Z vector (should not move).
                elif res_name == 'Z':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assert_(new_pos[0] >= -70.711 - epsilon)
                    self.assert_(new_pos[0] <= 0.0 + epsilon)
                    self.assert_(new_pos[1] >= -100.0 - epsilon)
                    self.assert_(new_pos[1] <= 100.0 + epsilon)
                    self.assert_(new_pos[2] >= 0.0 - epsilon)
                    self.assert_(new_pos[2] <= 70.711 + epsilon)

                # Check the nX vector.
                elif res_name == 'nX':
                    self.assertAlmostEqual(new_pos[0], -70.711, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], -70.711, 3)

                # Check the nY vector.
                elif res_name == 'nY':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assert_(new_pos[0] >= -70.711 - epsilon)
                    self.assert_(new_pos[0] <= 70.711 + epsilon)
                    self.assert_(new_pos[1] >= -100.0 - epsilon)
                    self.assert_(new_pos[1] <= 0.0 + epsilon)
                    self.assert_(new_pos[2] >= -70.711 - epsilon)
                    self.assert_(new_pos[2] <= 70.711 + epsilon)

                # Check the nZ vector (should not move).
                elif res_name == 'nZ':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assert_(new_pos[0] >= 0.0 - epsilon)
                    self.assert_(new_pos[0] <= 70.711 + epsilon)
                    self.assert_(new_pos[1] >= -100.0 - epsilon)
                    self.assert_(new_pos[1] <= 100.0 + epsilon)
                    self.assert_(new_pos[2] >= -70.711 - epsilon)
                    self.assert_(new_pos[2] <= 0.0 + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 3)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == '0':
                    self.assertAlmostEqual(pos[0], 20.0, 3)
                    self.assertAlmostEqual(pos[1], 20.0, 3)
                    self.assertAlmostEqual(pos[2], -20.0, 3)


    def test_simulate_double_rotor_mode2_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the double rotor model along the z-axis for the second rotation mode."""

        # Init.
        cone_sigma_max = 0.0
        cone_sigma_max_2 = pi / 2.0
        pivot = array([20, 20, -20], float64)
        l = 100.0
        sim_num = 500
        pivot_disp = 100.0

        # The eigenframe.
        eigen_beta = 0.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='double rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=eigen_beta, ave_pos_gamma=0.0, pivot_disp=pivot_disp, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_sigma_max=cone_sigma_max, cone_sigma_max_2=cone_sigma_max_2)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # Check the X and nX vectors.
                if res_name == 'X':
                    self.assertAlmostEqual(new_pos[0], 100.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assert_(new_pos[1] >= 0.0 - epsilon)
                    self.assert_(new_pos[1] <= 100.0 + epsilon)
                    self.assert_(new_pos[2] >= -100.0 - epsilon)
                    self.assert_(new_pos[2] <= 100.0 + epsilon)

                # Check the Z vector (should not move).
                elif res_name == 'Z':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assert_(new_pos[1] >= -100.0 - epsilon)
                    self.assert_(new_pos[1] <= 100.0 + epsilon)
                    self.assert_(new_pos[2] >= 0.0 - epsilon)
                    self.assert_(new_pos[2] <= 100.0 + epsilon)

                # Check the X and nX vectors.
                elif res_name == 'nX':
                    self.assertAlmostEqual(new_pos[0], -100.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the nY vector.
                elif res_name == 'nY':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assert_(new_pos[1] >= -100.0 - epsilon)
                    self.assert_(new_pos[1] <= 0.0 + epsilon)
                    self.assert_(new_pos[2] >= -100.0 - epsilon)
                    self.assert_(new_pos[2] <= 100.0 + epsilon)

                # Check the nZ vector (should not move).
                elif res_name == 'nZ':
                    self.assertAlmostEqual(r/100.0, 1.0, 3)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assert_(new_pos[1] >= -100.0 - epsilon)
                    self.assert_(new_pos[1] <= 100.0 + epsilon)
                    self.assert_(new_pos[2] >= -100.0 - epsilon)
                    self.assert_(new_pos[2] <= 0.0 + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 3)
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == '0':
                    self.assertAlmostEqual(pos[0], 20.0, 3)
                    self.assertAlmostEqual(pos[1], 20.0, 3)
                    self.assertAlmostEqual(pos[2], -20.0, 3)


    def test_simulate_free_rotor_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the free rotor model along the z-axis."""

        # Init.
        pivot = array([1, 0, 0], float64)
        l = 10.0
        sim_num = 500

        # The axis alpha parameter, and printout.
        axis_alpha = pi / 2.0
        axis = create_rotor_axis_alpha(pi/2, pivot, array([0, 0, 0], float64))
        print("\nRotor axis:  %s" % axis)
        print("Rotor apex (100*axis + [1, 0, 0]):\n    %s" % (l*axis + pivot))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='free rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_alpha=axis_alpha)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    self.assertAlmostEqual(theta, pi/2.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assertAlmostEqual(theta, pi/2.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the Z vector (should not move).
                elif res_name == 'Z':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 100.0, 3)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)


    def test_simulate_iso_cone_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the isotropic cone model along the z-axis."""

        # Init.
        cone_theta = 0.5
        cone_sigma_max = 0.3
        pivot = array([1, 0, -2], float64)
        l = 24.0
        sim_num = 500

        # The axis parameters, and printout.
        axis_theta = 0.0
        print("Rotor axis:  %s" % create_rotor_axis_spherical(axis_theta, 0.0))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=cone_theta, cone_sigma_max=cone_sigma_max)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        lateral_slide = 0.07
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    if abs(phi) > max_phi:
                        max_phi = abs(phi)
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)
                    self.assert_(phi >= -cone_sigma_max - lateral_slide)
                    self.assert_(phi <= cone_sigma_max + lateral_slide)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)
                    self.assert_(phi-pi/2.0 >= -cone_sigma_max - lateral_slide)
                    self.assert_(phi-pi/2.0 <= cone_sigma_max + lateral_slide)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    self.assert_(theta <= cone_theta + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi for X and Y: %s" % max_phi)


    def test_simulate_iso_cone_xz_plane_tilt(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the isotropic cone model with a xz-plane tilt."""

        # Init.
        cone_theta = 0.5
        cone_sigma_max = 0.3
        pivot = array([1, 0, -2], float64)
        l = 24.0
        sim_num = 500

        # The axis parameters, and printout.
        axis_theta = -pi/4.0
        axis = create_rotor_axis_spherical(axis_theta, 0.0)
        print("Rotor axis:  %s" % axis)
        R = zeros((3, 3), float64)
        axis_angle_to_R([0, 1, 0], axis_theta, R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=axis_theta, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=cone_theta, cone_sigma_max=cone_sigma_max)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        lateral_slide = 0.07
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(dot(transpose(R), new_pos))

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    if abs(phi) > max_phi:
                        max_phi = abs(phi)
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)
                    self.assert_(phi >= -cone_sigma_max - lateral_slide)
                    self.assert_(phi <= cone_sigma_max + lateral_slide)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)
                    self.assert_(phi-pi/2.0 >= -cone_sigma_max - lateral_slide)
                    self.assert_(phi-pi/2.0 <= cone_sigma_max + lateral_slide)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    self.assert_(theta <= cone_theta + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi for X and Y: %s" % max_phi)


    def test_simulate_iso_cone_free_rotor_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the free rotor isotropic cone model along the z-axis."""

        # Init.
        cone_theta = 0.5
        pivot = array([1, 0, -2], float64)
        l = 24.0
        sim_num = 500

        # The axis parameters, and printout.
        axis_theta = 0.0
        print("Rotor axis:  %s" % create_rotor_axis_spherical(axis_theta, 0.0))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone, free rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=cone_theta)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    self.assert_(theta <= cone_theta + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)


    def test_simulate_iso_cone_torsionless_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the torsionless isotropic cone model along the z-axis."""

        # Init.
        cone_theta = 0.5
        pivot = array([1, 0, -2], float64)
        l = 24.0
        sim_num = 500

        # The axis parameters, and printout.
        axis_theta = 0.0
        print("Rotor axis:  %s" % create_rotor_axis_spherical(axis_theta, 0.0))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='iso cone, torsionless', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_theta=axis_theta, axis_phi=0.0, cone_theta=cone_theta)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        lateral_slide = 0.07
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    if abs(phi) > max_phi:
                        max_phi = abs(phi)
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)
                    self.assert_(phi >= -lateral_slide)
                    self.assert_(phi <= lateral_slide)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assert_(theta >= pi/2.0 - cone_theta - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta + epsilon)
                    self.assert_(phi-pi/2.0 >= -lateral_slide)
                    self.assert_(phi-pi/2.0 <= lateral_slide)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    self.assert_(theta <= cone_theta + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi for X and Y: %s" % max_phi)


    def test_simulate_pseudo_ellipse_xz_plane_tilt(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the pseudo-ellipse model along the z-axis."""

        # Init.
        cone_theta_x = 2.0
        cone_theta_y = 0.5
        cone_sigma_max = 0.1
        pivot = array([1, 0, -2], float64)
        l = 50.0
        sim_num = 500

        # The axis parameters.
        eigen_beta = -pi/4.0
        R = zeros((3, 3), float64)
        euler_to_R_zyz(0.0, eigen_beta, 0.0, R)
        print("Motional eigenframe:\n%s" % R)

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=eigen_beta, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=cone_theta_x, cone_theta_y=cone_theta_y, cone_sigma_max=cone_sigma_max)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        lateral_slide = 0.17
        vertical_slide = 0.02
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(dot(transpose(R), new_pos))

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position [%8.3f, %8.3f, %8.3f], with spherical coordinates [%8.3f, %8.3f, %8.3f]." % (res_num, res_name, atom_num, atom_name, new_pos[0], new_pos[1], new_pos[2], r, theta, phi))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    self.assert_(theta >= pi/2.0 - cone_theta_x - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta_x + epsilon)

                # Check the Y vector.
                elif res_name == 'Y':
                    if abs(phi-pi/2.0) > max_phi:
                        max_phi = abs(phi-pi/2.0)
                    self.assert_(theta >= pi/2.0 - cone_theta_y - vertical_slide)
                    self.assert_(theta <= pi/2.0 + cone_theta_y + vertical_slide)
                    self.assert_(phi-pi/2.0 >= -cone_sigma_max - lateral_slide)
                    self.assert_(phi-pi/2.0 <= cone_sigma_max + lateral_slide)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    theta_max = cone_theta_x * cone_theta_y / sqrt((cos(phi)*cone_theta_y)**2 + (sin(phi)*cone_theta_x)**2)
                    self.assert_(theta <= theta_max + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi-pi/2.0 for Y: %s" % max_phi)


    def test_simulate_pseudo_ellipse_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the pseudo-ellipse model along the z-axis."""

        # Init.
        cone_theta_x = 2.0
        cone_theta_y = 0.5
        cone_sigma_max = 0.1
        pivot = array([1, 0, -2], float64)
        l = 50.0
        sim_num = 500

        # The axis parameters.
        eigen_beta = 0.0

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=cone_theta_x, cone_theta_y=cone_theta_y, cone_sigma_max=cone_sigma_max)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        lateral_slide = 0.17
        vertical_slide = 0.02
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position [%8.3f, %8.3f, %8.3f], with spherical coordinates [%8.3f, %8.3f, %8.3f]." % (res_num, res_name, atom_num, atom_name, new_pos[0], new_pos[1], new_pos[2], r, theta, phi))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    self.assert_(theta >= pi/2.0 - cone_theta_x - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta_x + epsilon)

                # Check the Y vector.
                elif res_name == 'Y':
                    if abs(phi-pi/2.0) > max_phi:
                        max_phi = abs(phi-pi/2.0)
                    self.assert_(theta >= pi/2.0 - cone_theta_y - vertical_slide)
                    self.assert_(theta <= pi/2.0 + cone_theta_y + vertical_slide)
                    self.assert_(phi-pi/2.0 >= -cone_sigma_max - lateral_slide)
                    self.assert_(phi-pi/2.0 <= cone_sigma_max + lateral_slide)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    theta_max = cone_theta_x * cone_theta_y / sqrt((cos(phi)*cone_theta_y)**2 + (sin(phi)*cone_theta_x)**2)
                    self.assert_(theta <= theta_max + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi-pi/2.0 for Y: %s" % max_phi)


    def test_simulate_pseudo_ellipse_free_rotor_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the free rotor pseudo-ellipse model along the z-axis."""

        # Init.
        cone_theta_x = 2.0
        cone_theta_y = 0.5
        pivot = array([1, 0, -2], float64)
        l = 50.0
        sim_num = 500

        # The axis parameters.
        eigen_beta = 0.0

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse, free rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=cone_theta_x, cone_theta_y=cone_theta_y)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position [%8.3f, %8.3f, %8.3f], with spherical coordinates [%8.3f, %8.3f, %8.3f]." % (res_num, res_name, atom_num, atom_name, new_pos[0], new_pos[1], new_pos[2], r, theta, phi))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X and Y vectors.
                if res_name in ['X', 'Y']:
                    self.assert_(theta >= pi/2.0 - cone_theta_x - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta_x + epsilon)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    theta_max = cone_theta_x * cone_theta_y / sqrt((cos(phi)*cone_theta_y)**2 + (sin(phi)*cone_theta_x)**2)
                    self.assert_(theta <= theta_max + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi-pi/2.0 for Y: %s" % max_phi)


    def test_simulate_pseudo_ellipse_torsionless_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the torsionless pseudo-ellipse model along the z-axis."""

        # Init.
        cone_theta_x = 2.0
        cone_theta_y = 0.5
        pivot = array([1, 0, -2], float64)
        l = 50.0
        sim_num = 500

        # The axis parameters.
        eigen_beta = 0.0

        # Set up.
        self.setup_model(pipe_name='PDB model', model='pseudo-ellipse, torsionless', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, eigen_alpha=0.0, eigen_beta=eigen_beta, eigen_gamma=0.0, cone_theta_x=cone_theta_x, cone_theta_y=cone_theta_y)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        epsilon = 1e-3
        max_phi = 0.0
        lateral_slide = 0.23
        vertical_slide = 0.02
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position [%8.3f, %8.3f, %8.3f], with spherical coordinates [%8.3f, %8.3f, %8.3f]." % (res_num, res_name, atom_num, atom_name, new_pos[0], new_pos[1], new_pos[2], r, theta, phi))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    self.assert_(theta >= pi/2.0 - cone_theta_x - epsilon)
                    self.assert_(theta <= pi/2.0 + cone_theta_x + epsilon)

                # Check the Y vector.
                elif res_name == 'Y':
                    if abs(phi-pi/2.0) > max_phi:
                        max_phi = abs(phi-pi/2.0)
                    self.assert_(theta >= pi/2.0 - cone_theta_y - vertical_slide)
                    self.assert_(theta <= pi/2.0 + cone_theta_y + vertical_slide)
                    self.assert_(phi-pi/2.0 >= -lateral_slide)
                    self.assert_(phi-pi/2.0 <= lateral_slide)

                # Check the Z vector (should be in the cone defined by theta).
                elif res_name == 'Z':
                    theta_max = cone_theta_x * cone_theta_y / sqrt((cos(phi)*cone_theta_y)**2 + (sin(phi)*cone_theta_x)**2)
                    self.assert_(theta <= theta_max + epsilon)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)

        # Print out the maximum phi value.
        print("Maximum phi-pi/2.0 for Y: %s" % max_phi)


    def test_simulate_rotor_z_axis(self, type='sim'):
        """Check the frame_order.simulate user function PDB file for the rotor model along the z-axis."""

        # Init.
        cone_sigma_max = 0.3
        pivot = array([1, 0, 0], float64)
        l = 30.0
        sim_num = 500

        # The axis alpha parameter, and printout.
        axis_alpha = pi / 2.0
        axis = create_rotor_axis_alpha(pi/2, pivot, array([0, 0, 0], float64))
        print("\nRotor axis:  %s" % axis)
        print("Rotor apex (100*axis + [1, 0, 0]):\n    %s" % (l*axis + pivot))

        # Set up.
        self.setup_model(pipe_name='PDB model', model='rotor', pivot=pivot, ave_pos_x=pivot[0], ave_pos_y=pivot[1], ave_pos_z=pivot[2], ave_pos_alpha=0.0, ave_pos_beta=0.0, ave_pos_gamma=0.0, axis_alpha=axis_alpha, cone_sigma_max=cone_sigma_max)

        # Create the PDB.
        if type == 'sim':
            self.interpreter.frame_order.simulate(file='simulation.pdb', dir=ds.tmpdir, step_size=10.0, snapshot=10, total=sim_num)
        elif type == 'dist':
            self.interpreter.frame_order.distribute(file='simulation.pdb', dir=ds.tmpdir, total=sim_num)

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Read the contents of the file.
        self.interpreter.structure.read_pdb(file='simulation.pdb', dir=ds.tmpdir)

        # Check the atomic coordinates.
        selection = cdp.structure.selection()
        for res_num, res_name, atom_num, atom_name, pos in cdp.structure.atom_loop(selection=selection, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, pos_flag=True):
            # Loop over all positions.
            for i in range(sim_num):
                # Shift the position back to the origin, and decompose into spherical coordinates.
                new_pos = pos[i] - pivot
                r, theta, phi = cartesian_to_spherical(new_pos)

                # Printout.
                print("Checking residue %s %s, atom %s %s, at shifted position %s, with spherical coordinates %s." % (res_num, res_name, atom_num, atom_name, new_pos, [r, theta, phi]))

                # The vector lengths.
                if res_name in ['X', 'Y', 'Z', 'Xn', 'Yn', 'Zn']:
                    self.assertAlmostEqual(r/100.0, 1.0, 4)
                elif res_name == 'C':
                    self.assertAlmostEqual(r, 0.0, 4)

                # Check the X vector.
                if res_name == 'X':
                    self.assertAlmostEqual(theta, pi/2.0, 3)
                    self.assert_(phi >= -cone_sigma_max)
                    self.assert_(phi <= cone_sigma_max)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the Y vector.
                elif res_name == 'Y':
                    self.assertAlmostEqual(theta, pi/2.0, 3)
                    self.assert_(phi-pi/2.0 >= -cone_sigma_max)
                    self.assert_(phi-pi/2.0 <= cone_sigma_max)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the Z vector (should not move).
                elif res_name == 'Z':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 100.0, 3)

                # Check the centre.
                elif res_name == 'C':
                    self.assertAlmostEqual(new_pos[0], 0.0, 3)
                    self.assertAlmostEqual(new_pos[1], 0.0, 3)
                    self.assertAlmostEqual(new_pos[2], 0.0, 3)

                # Check the origin.
                elif res_name == 'C':
                    self.assertAlmostEqual(pos[0], 0.0, 3)
                    self.assertAlmostEqual(pos[1], 0.0, 3)
                    self.assertAlmostEqual(pos[2], 0.0, 3)


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
