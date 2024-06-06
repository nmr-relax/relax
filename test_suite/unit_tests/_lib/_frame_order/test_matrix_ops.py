###############################################################################
#                                                                             #
# Copyright (C) 2010-2014,2024 Edward d'Auvergne                              #
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
from numpy import array, float64, zeros
from unittest import TestCase

# relax module imports.
import dep_check
from lib.frame_order.format import print_frame_order_2nd_degree
from lib.frame_order.free_rotor import compile_2nd_matrix_free_rotor
from lib.frame_order.iso_cone import compile_2nd_matrix_iso_cone
from lib.frame_order.iso_cone_free_rotor import compile_2nd_matrix_iso_cone_free_rotor
from lib.frame_order.iso_cone_torsionless import compile_2nd_matrix_iso_cone_torsionless
from lib.frame_order.pseudo_ellipse import compile_2nd_matrix_pseudo_ellipse
from lib.frame_order.pseudo_ellipse_free_rotor import compile_2nd_matrix_pseudo_ellipse_free_rotor
from lib.frame_order.pseudo_ellipse_torsionless import compile_2nd_matrix_pseudo_ellipse_torsionless
from lib.frame_order.rotor import compile_2nd_matrix_rotor
from lib.frame_order.matrix_ops import reduce_alignment_tensor
from lib.geometry.coord_transform import cartesian_to_spherical, spherical_to_cartesian
from lib.geometry.rotations import euler_to_R_zyz, two_vect_to_R
from lib.linear_algebra.kronecker_product import kron_prod, transpose_23
from status import Status; status = Status()


class Test_matrix_ops(TestCase):
    """Unit tests for the lib.frame_order_matrix_ops relax module."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if scipy is not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Missing module.
        if not dep_check.scipy_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Scipy', 'unit'])

        # Execute the base class method.
        super(Test_matrix_ops, self).__init__(methodName)


    def setUp(self):
        """Initialise a few data structures for the tests."""

        # Temp storage.
        self.f2_temp = zeros((9, 9), float64)
        self.R_temp = zeros((3, 3), float64)
        self.z_axis = array([0, 0, 1], float64)
        self.cone_axis = zeros(3, float64)

        # Set up the identity matrices.
        self.setup_identity()

        # Set up the identity matrices for free rotors.
        self.setup_identity_free_rotor()

        # Out of frame Euler angles.
        self.out_of_frame_alpha = 1.10714871779
        self.out_of_frame_beta = 0.841068670568
        self.out_of_frame_gamma = 5.81953769818


    def calc_Rx2_eigen_axis(self, axis_theta, axis_phi):
        """Calculate the Kronecker product of the eigenframe rotation for the z-axis based frame."""

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_temp)

        # The Kronecker product of the eigenframe rotation.
        return kron_prod(self.R_temp, self.R_temp)


    def calc_Rx2_eigen_full(self, eigen_alpha, eigen_beta, eigen_gamma):
        """Calculate the Kronecker product of the eigenframe rotation for the full eigenframe."""

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_temp)

        # The Kronecker product of the eigenframe rotation.
        return kron_prod(self.R_temp, self.R_temp)


    def setup_identity(self):
        """Set up a few identity matrices."""

        # The order identity matrix.
        self.I_order = zeros((9, 9), float64)
        for i in range(9):
            self.I_order[i, i] = 1.0

        # The disorder identity matrix.
        data = [[0, 0, 1.0/3.0],
                [4, 4, 1.0/3.0],
                [8, 8, 1.0/3.0],
                [0, 4, 1.0/3.0],
                [4, 0, 1.0/3.0],
                [0, 8, 1.0/3.0],
                [8, 0, 1.0/3.0],
                [4, 8, 1.0/3.0],
                [8, 4, 1.0/3.0]]
        self.I_disorder = zeros((9, 9), float64)
        for i, j, val in data:
            self.I_disorder[i, j] = val

        # The half cone matrix.
        data = [[0, 0, 1.0/3.0],
                [4, 4, 1.0/3.0],
                [8, 8, 1.0/3.0],
                [0, 4, 1.0/3.0],
                [4, 0, 1.0/3.0],
                [0, 8, 1.0/3.0],
                [8, 0, 1.0/3.0],
                [4, 8, 1.0/3.0],
                [8, 4, 1.0/3.0],
                [1, 3, -0.25],
                [3, 1, -0.25],
                [1, 1, 0.25],
                [3, 3, 0.25]]
        self.f2_half_cone = zeros((9, 9), float64)
        for i, j, val in data:
            self.f2_half_cone[i, j] = val

        # The half cone matrix rotated 90 degrees about y.
        data = [[0, 0, 1.0/3.0],
                [4, 4, 1.0/3.0],
                [8, 8, 1.0/3.0],
                [0, 4, 1.0/3.0],
                [4, 0, 1.0/3.0],
                [0, 8, 1.0/3.0],
                [8, 0, 1.0/3.0],
                [4, 8, 1.0/3.0],
                [8, 4, 1.0/3.0],
                [5, 7, -0.25],
                [7, 5, -0.25],
                [7, 7, 0.25],
                [5, 5, 0.25]]
        self.f2_half_cone_90_y = zeros((9, 9), float64)
        for i, j, val in data:
            self.f2_half_cone_90_y[i, j] = val


    def setup_identity_free_rotor(self):
        """Set up a few identity matrices."""

        # The order identity matrix for the free rotors.
        data = [[0, 0,  0.5],
                [1, 1,  0.5],
                [3, 3,  0.5],
                [4, 4,  0.5],
                [0, 4,  0.5],
                [4, 0,  0.5],
                [1, 3, -0.5],
                [3, 1, -0.5],
                [8, 8,  1.0]]
        self.I_order_free_rotor = zeros((9, 9), float64)
        for i, j, val in data:
            self.I_order_free_rotor[i, j] = val

        # The disorder identity matrix for the free rotors.
        data = [[0, 0,  0.25],
                [1, 1,  0.125],
                [3, 3,  0.125],
                [4, 4,  0.25],
                [0, 4,  0.25],
                [4, 0,  0.25],
                [1, 3, -0.125],
                [3, 1, -0.125],
                [0, 8,  0.5],
                [8, 0,  0.5],
                [4, 8,  0.5],
                [8, 4,  0.5]]
        self.I_disorder_free_rotor = zeros((9, 9), float64)
        for i, j, val in data:
            self.I_disorder_free_rotor[i, j] = val


    def test_compile_2nd_matrix_free_rotor_point1(self):
        """Check the operation of the compile_2nd_matrix_free_rotor() function."""

        # The simulated in frame free rotor 2nd degree frame order matrix (1e6 ensembles).
        real = array(
                    [[    0.5001,    0.0001,         0,    0.0001,    0.4999,         0,         0,         0,         0],
                     [   -0.0001,    0.5001,         0,   -0.4999,    0.0001,         0,         0,         0,         0],
                     [         0,         0,    0.0006,         0,         0,   -0.0005,         0,         0,         0],
                     [   -0.0001,   -0.4999,         0,    0.5001,    0.0001,         0,         0,         0,         0],
                     [    0.4999,   -0.0001,         0,   -0.0001,    0.5001,         0,         0,         0,         0],
                     [         0,         0,    0.0005,         0,         0,    0.0006,         0,         0,         0],
                     [         0,         0,         0,         0,         0,         0,    0.0006,   -0.0005,         0],
                     [         0,         0,         0,         0,         0,         0,    0.0005,    0.0006,         0],
                     [         0,         0,         0,         0,         0,         0,         0,         0,    1.0000]])

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_free_rotor(self.f2_temp, Rx2_eigen)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s; diff %s." % (i, j, f2[i, j] - real[i, j]))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-3)


    def test_compile_2nd_matrix_free_rotor_point2(self):
        """Check the operation of the compile_2nd_matrix_free_rotor() function."""

        # The simulated free rotor 2nd degree frame order matrix (1e6 ensembles, axis=[2,1,3]).
        real = array(
                    [[    0.3367,   -0.0100,   -0.0307,   -0.0100,    0.3521,   -0.0152,   -0.0307,   -0.0152,    0.3112],
                     [   -0.0104,    0.3520,   -0.0152,   -0.2908,   -0.0559,    0.2602,    0.1989,   -0.1685,    0.0664],
                     [   -0.0306,   -0.0155,    0.3112,    0.1991,   -0.1683,    0.0666,    0.2399,    0.2092,    0.1989],
                     [   -0.0104,   -0.2908,    0.1989,    0.3520,   -0.0559,   -0.1685,   -0.0152,    0.2602,    0.0664],
                     [    0.3520,   -0.0563,   -0.1684,   -0.0563,    0.4362,   -0.0841,   -0.1684,   -0.0841,    0.2118],
                     [   -0.0153,    0.2602,    0.0661,   -0.1684,   -0.0844,    0.2117,    0.2093,   -0.0740,    0.0997],
                     [   -0.0306,    0.1991,    0.2399,   -0.0155,   -0.1683,    0.2092,    0.3112,    0.0666,    0.1989],
                     [   -0.0153,   -0.1684,    0.2093,    0.2602,   -0.0844,   -0.0740,    0.0661,    0.2117,    0.0997],
                     [    0.3113,    0.0663,    0.1991,    0.0663,    0.2117,    0.0993,    0.1991,    0.0993,    0.4770]])

        # The cone axis.
        r, theta, phi = cartesian_to_spherical([2, 1, 3])

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(theta, phi)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_free_rotor(self.f2_temp, Rx2_eigen)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s; diff %s." % (i, j, f2[i, j] - real[i, j]))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-3)


    def test_compile_2nd_matrix_iso_cone_disorder(self):
        """Check if compile_2nd_matrix_iso_cone() can return the identity matrix for disorder."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen, pi, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_iso_cone_half_cone(self):
        """Check if compile_2nd_matrix_iso_cone() can return the matrix for a half cone."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen, pi/2.0, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone[i, j])


    def test_compile_2nd_matrix_iso_cone_half_cone_90_y(self):
        """Check if compile_2nd_matrix_iso_cone() can return the matrix for a half cone rotated 90 degrees about y."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(pi/2.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen, pi/2.0, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone_90_y, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone_90_y[i, j])


    def test_compile_2nd_matrix_iso_cone_order(self):
        """Check if compile_2nd_matrix_iso_cone() can return the identity matrix for order."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen, 1e-5, 1e-10)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order, "Identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_order[i, j])


    def test_compile_2nd_matrix_iso_cone_order2(self):
        """2nd check if compile_2nd_matrix_iso_cone() can return the identity matrix for order."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen, 0.0, 0.0)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order, "Identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_order[i, j])


    def test_compile_2nd_matrix_iso_cone_restriction_test(self):
        """Check if compile_2nd_matrix_iso_cone() can approximate compile_2nd_matrix_iso_cone_free_rotor()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_axis(0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen_a, pi/4.6, pi)
        f2b = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen_b, pi/4.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Isotropic cone frame order")
        print_frame_order_2nd_degree(f2b, "Free rotor isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_iso_cone_restriction_test2(self):
        """Check if compile_2nd_matrix_iso_cone() can approximate compile_2nd_matrix_iso_cone_torsionless()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_axis(0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen_a, pi/4.6, 0)
        f2b = compile_2nd_matrix_iso_cone_torsionless(self.f2_temp, Rx2_eigen_b, pi/4.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Isotropic cone frame order")
        print_frame_order_2nd_degree(f2b, "Torsionless isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_iso_cone_free_rotor_disorder(self):
        """Check if compile_2nd_matrix_iso_cone_free_rotor() can return the identity matrix for disorder."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen, pi)

        # Cannot differentiate full disorder from the half cone in this model!
        f2_ref = self.f2_half_cone

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_iso_cone_free_rotor_half_cone(self):
        """Check if compile_2nd_matrix_iso_cone_free_rotor() can return the matrix for a half cone."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen, pi/2.0)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone[i, j])


    def test_compile_2nd_matrix_iso_cone_free_rotor_half_cone_90_y(self):
        """Check if compile_2nd_matrix_iso_cone_free_rotor() can return the matrix for a half cone rotated 90 degrees about y."""

        # Init.
        self.z_axis = array([1, 0, 0], float64)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen, pi/2.0)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone_90_y, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone_90_y[i, j])


    def test_compile_2nd_matrix_iso_cone_free_rotor_order(self):
        """Check if compile_2nd_matrix_iso_cone_free_rotor() can return the identity matrix for order."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen, 0.0)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order_free_rotor, "Free rotor identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_order_free_rotor[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_point1(self):
        """Check the operation of the compile_2nd_matrix_pseudo_ellipse() function."""

        # The simulated in frame pseudo-ellipse 2nd degree frame order matrix.
        real = array(
                    [[    0.7901,         0,         0,         0,    0.7118,         0,         0,         0,    0.6851],
                     [         0,    0.0816,         0,   -0.0606,         0,         0,         0,         0,         0],
                     [         0,         0,    0.1282,         0,         0,         0,   -0.1224,         0,         0],
                     [         0,   -0.0606,         0,    0.0708,         0,         0,         0,         0,         0],
                     [    0.7118,         0,         0,         0,    0.6756,         0,         0,         0,    0.6429],
                     [         0,         0,         0,         0,         0,    0.2536,         0,   -0.2421,         0],
                     [         0,         0,   -0.1224,         0,         0,         0,    0.1391,         0,         0],
                     [         0,         0,         0,         0,         0,   -0.2421,         0,    0.2427,         0],
                     [    0.6851,         0,         0,         0,    0.6429,         0,         0,         0,    0.6182]], float64)
        transpose_23(real)

        # Init.
        x = pi/4.0
        y = 3.0*pi/8.0
        z = pi/6.0

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, x, y, z)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s; diff %s." % (i, j, f2[i, j] - real[i, j]))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-4)


    def test_compile_2nd_matrix_pseudo_ellipse_point2(self):
        """Check the operation of the compile_2nd_matrix_pseudo_ellipse() function."""

        # The simulated in frame pseudo-ellipse 2nd degree frame order matrix (1e6 ensembles).
        real = array(
                    [[    0.7379,         0,         0,         0,    0.1338,         0,         0,         0,    0.1284],
                     [         0,    0.6637,         0,   -0.1085,         0,         0,         0,         0,         0],
                     [         0,         0,    0.6603,         0,         0,         0,   -0.1181,         0,         0],
                     [         0,   -0.1085,         0,    0.6637,         0,         0,         0,         0,         0],
                     [    0.1154,         0,         0,         0,    0.6309,         0,         0,         0,    0.2536],
                     [         0,         0,         0,         0,         0,    0.6196,         0,   -0.2336,         0],
                     [         0,         0,   -0.1181,         0,         0,         0,    0.6603,         0,         0],
                     [         0,         0,         0,         0,         0,   -0.2336,         0,    0.6196,         0],
                     [    0.1467,         0,         0,         0,    0.2353,         0,         0,         0,    0.6180]], float64)

        # Init.
        x = pi/4.0
        y = 3.0*pi/8.0
        z = 40.0 / 360.0 * 2.0 * pi

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, x, y, z)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s; diff %s." % (i, j, f2[i, j] - real[i, j]))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-3)


    def test_compile_2nd_matrix_pseudo_ellipse_point3(self):
        """Check the operation of the compile_2nd_matrix_pseudo_ellipse() function."""

        # The simulated out of frame pseudo-ellipse 2nd degree frame order matrix (1e6 ensembles).
        real = array(
                    [[    0.6314,    0.0232,   -0.0344,    0.0232,    0.1558,   -0.0222,   -0.0344,   -0.0222,    0.2128],
                     [    0.0220,    0.6366,    0.0069,   -0.1352,    0.0243,   -0.0722,    0.0206,   -0.0277,   -0.0464],
                     [   -0.0332,    0.0097,    0.6137,    0.0222,    0.0668,    0.0173,   -0.1967,    0.0489,   -0.0336],
                     [    0.0220,   -0.1352,    0.0206,    0.6366,    0.0243,   -0.0277,    0.0069,   -0.0722,   -0.0464],
                     [    0.1554,    0.0233,    0.0669,    0.0233,    0.6775,    0.0113,    0.0669,    0.0113,    0.1671],
                     [   -0.0222,   -0.0738,    0.0188,   -0.0286,    0.0113,    0.6310,    0.0507,   -0.1502,    0.0109],
                     [   -0.0332,    0.0222,   -0.1967,    0.0097,    0.0668,    0.0489,    0.6137,    0.0173,   -0.0336],
                     [   -0.0222,   -0.0286,    0.0507,   -0.0738,    0.0113,   -0.1502,    0.0188,    0.6310,    0.0109],
                     [    0.2132,   -0.0465,   -0.0324,   -0.0465,    0.1667,    0.0110,   -0.0324,    0.0110,    0.6201]], float64)

        # Init.
        x = 60.0 / 360.0 * 2.0 * pi
        y = 3.0 * pi / 8.0
        z = pi / 6.0

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(self.out_of_frame_alpha, self.out_of_frame_beta, self.out_of_frame_gamma)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, x, y, z)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s; diff %s." % (i, j, f2[i, j] - real[i, j]))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-3)


    def test_compile_2nd_matrix_pseudo_ellipse_disorder(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the identity matrix for disorder."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, pi, pi, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_half_cone(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the matrix for a half cone."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, pi/2.0, pi/2.0, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_half_cone_90_y(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the matrix for a half cone rotated 90 degrees about y."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, pi/2.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, pi/2.0, pi/2.0, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone_90_y, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone_90_y[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_order(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the identity matrix for order."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen, 1e-2, 1e-2, 1e-10)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order, "Identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")
        print_frame_order_2nd_degree(f2-self.I_order, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_order[i, j], 4)


    def test_compile_2nd_matrix_pseudo_ellipse_restriction_test(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can approximate compile_2nd_matrix_pseudo_ellipse_free_rotor()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen_a, pi/1.6, pi/5.8, pi)
        f2b = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen_b, pi/1.6, pi/5.8)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Free rotor pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_restriction_test2(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can approximate a pi/2 rotated compile_2nd_matrix_pseudo_ellipse_free_rotor()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_full(pi/2, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen_a, pi/1.6, pi/5.8, pi)
        f2b = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen_b, pi/5.8, pi/1.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "pi/2 rotated free rotor pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_restriction_test3(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can approximate compile_2nd_matrix_pseudo_ellipse_torsionless()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen_a, pi/2.1, pi/4.6, 0)
        f2b = compile_2nd_matrix_pseudo_ellipse_torsionless(self.f2_temp, Rx2_eigen_b, pi/2.1, pi/4.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Torsionless pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s; diff %s." % (i, j, f2b[i, j] - f2a[i, j]))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_restriction_test4(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can approximate compile_2nd_matrix_iso_cone()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen_a, pi/4.6, pi/4.6, 0.2)
        f2b = compile_2nd_matrix_iso_cone(self.f2_temp, Rx2_eigen_b, pi/4.6, 0.2)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_restriction_test5(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can approximate compile_2nd_matrix_iso_cone_free_rotor()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen_a, pi/4.6, pi/4.6, pi)
        f2b = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen_b, pi/4.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Free rotor isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_restriction_test6(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can approximate compile_2nd_matrix_iso_cone_torsionless()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, Rx2_eigen_a, pi/8.6, pi/8.6, 0)
        f2b = compile_2nd_matrix_iso_cone_torsionless(self.f2_temp, Rx2_eigen_b, pi/8.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Torsionless isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_disorder(self):
        """Check if compile_2nd_matrix_pseudo_ellipse_free_rotor() can return the identity matrix for disorder."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen, pi, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_half_cone(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the matrix for a half cone."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(pi, 0.0, pi)

        # Calculate the frame order matrix (rotated about z by 2pi).
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen, pi/2.0, pi/2.0)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_half_cone_90_y(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the matrix for a half cone rotated 90 degrees about y."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(pi, pi/2.0, pi)

        # Calculate the frame order matrix (rotated about z by 2pi).
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen, pi/2.0, pi/2.0)

        # Print outs.
        print_frame_order_2nd_degree(self.f2_half_cone_90_y, "The half cone frame order matrix")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.f2_half_cone_90_y[i, j])


    def fixme_test_compile_2nd_matrix_pseudo_ellipse_free_rotor_order(self):
        """Check if compile_2nd_matrix_pseudo_ellipse_free_rotor() can return the identity matrix for order."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen, 1e-10, 1e-10)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order_free_rotor, "Free rotor identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2[i, j], self.I_order_free_rotor[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_point1(self):
        """Check the operation of the compile_2nd_matrix_pseudo_ellipse_free_rotor() function."""

        # The simulated out of frame free rotor pseudo-ellipse 2nd degree frame order matrix (1e6 ensembles).
        real = array(
                    [[    0.3428,   -0.0193,    0.0389,   -0.0193,    0.3137,   -0.0194,    0.0389,   -0.0194,    0.3435],
                     [   -0.0225,    0.2313,    0.0034,   -0.1413,    0.0449,    0.2309,   -0.1830,   -0.1412,   -0.0224],
                     [    0.0417,    0.0091,    0.2142,   -0.1767,   -0.0838,    0.0092,    0.1211,   -0.1770,    0.0421],
                     [   -0.0225,   -0.1413,   -0.1830,    0.2313,    0.0449,   -0.1412,    0.0034,    0.2309,   -0.0224],
                     [    0.3124,    0.0418,   -0.0840,    0.0418,    0.3758,    0.0418,   -0.0840,    0.0418,    0.3118],
                     [   -0.0193,    0.2251,    0.0151,   -0.1476,    0.0389,    0.2251,   -0.1706,   -0.1468,   -0.0196],
                     [    0.0417,   -0.1767,    0.1211,    0.0091,   -0.0838,   -0.1770,    0.2142,    0.0092,    0.0421],
                     [   -0.0193,   -0.1476,   -0.1706,    0.2251,    0.0389,   -0.1468,    0.0151,    0.2251,   -0.0196],
                     [    0.3448,   -0.0225,    0.0450,   -0.0225,    0.3104,   -0.0224,    0.0450,   -0.0224,    0.3447]], float64)

        # Init.
        x = pi/4.0
        y = 50.0 / 360.0 * 2.0 * pi

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(self.out_of_frame_alpha, self.out_of_frame_beta, self.out_of_frame_gamma)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen, x, y)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-3)


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_point2(self):
        """Check the operation of the compile_2nd_matrix_pseudo_ellipse_free_rotor() function."""

        # The simulated out of frame free rotor pseudo-ellipse 2nd degree frame order matrix (1e6 ensembles).
        real = array(
                    [[    0.3251,    0.0163,   -0.0324,    0.0163,    0.3493,    0.0164,   -0.0324,    0.0164,    0.3256],
                     [   -0.0248,    0.1481,   -0.0480,   -0.0500,    0.0492,    0.1475,   -0.1472,   -0.0500,   -0.0244],
                     [    0.0079,    0.0328,    0.0572,   -0.0661,   -0.0163,    0.0331,    0.0074,   -0.0662,    0.0084],
                     [   -0.0248,   -0.0500,   -0.1472,    0.1481,    0.0492,   -0.0500,   -0.0480,    0.1475,   -0.0244],
                     [    0.3289,    0.0081,   -0.0167,    0.0081,    0.3426,    0.0080,   -0.0167,    0.0080,    0.3285],
                     [    0.0163,    0.0669,    0.1139,   -0.1322,   -0.0324,    0.0662,    0.0157,   -0.1307,    0.0161],
                     [    0.0079,   -0.0661,    0.0074,    0.0328,   -0.0163,   -0.0662,    0.0572,    0.0331,    0.0084],
                     [    0.0163,   -0.1322,    0.0157,    0.0669,   -0.0324,   -0.1307,    0.1139,    0.0662,    0.0161],
                     [    0.3459,   -0.0245,    0.0491,   -0.0245,    0.3081,   -0.0244,    0.0491,   -0.0244,    0.3460]], float64)

        # Init.
        x = pi / 4.0
        y = 150.0 / 360.0 * 2.0 * pi

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_full(self.out_of_frame_alpha, self.out_of_frame_beta, self.out_of_frame_gamma)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen, x, y)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-2)


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_restriction_test(self):
        """Check if compile_2nd_matrix_pseudo_ellipse_free_rotor() can approximate compile_2nd_matrix_iso_cone_free_rotor()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 1.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, Rx2_eigen_a, pi/4.6, pi/4.6)
        f2b = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, Rx2_eigen_b, pi/4.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Free rotor pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Free rotor isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_torsionless_restriction_test(self):
        """Check if compile_2nd_matrix_pseudo_ellipse_torsionless() can approximate compile_2nd_matrix_iso_cone_torsionless()."""

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen_a = self.calc_Rx2_eigen_full(0.0, 0.0, 0.0)
        Rx2_eigen_b = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the frame order matrix.
        f2a = compile_2nd_matrix_pseudo_ellipse_torsionless(self.f2_temp, Rx2_eigen_a, pi/4.6, pi/4.6)
        f2b = compile_2nd_matrix_iso_cone_torsionless(self.f2_temp, Rx2_eigen_b, pi/4.6)

        # Print outs.
        print_frame_order_2nd_degree(f2a, "Torsionless pseudo-ellipse frame order")
        print_frame_order_2nd_degree(f2b, "Torsionless isotropic cone frame order")
        print_frame_order_2nd_degree(f2b-f2a, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertAlmostEqual(f2a[i, j], f2b[i, j])


    def test_compile_2nd_matrix_rotor_point1(self):
        """Check the operation of the compile_2nd_matrix_rotor() function."""

        # The simulated in frame rotor 2nd degree frame order matrix (1e7 ensembles).
        real = array(
                    [[  7.06775425e-01,  1.36710179e-04,  0.00000000e+00,  1.36710179e-04, 2.93224575e-01,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                     [ -1.36710179e-04,  7.06775425e-01,  0.00000000e+00, -2.93224575e-01, 1.36710179e-04,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                     [  0.00000000e+00,  0.00000000e+00,  8.27014112e-01,  0.00000000e+00, 0.00000000e+00,  2.19539417e-04,  0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                     [ -1.36710179e-04, -2.93224575e-01,  0.00000000e+00,  7.06775425e-01, 1.36710179e-04,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                     [  2.93224575e-01, -1.36710179e-04,  0.00000000e+00, -1.36710179e-04, 7.06775425e-01,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                     [  0.00000000e+00,  0.00000000e+00, -2.19539417e-04,  0.00000000e+00, 0.00000000e+00,  8.27014112e-01,  0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                     [  0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00,  0.00000000e+00,  8.27014112e-01, 2.19539417e-04, 0.00000000e+00],
                     [  0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00,  0.00000000e+00, -2.19539417e-04, 8.27014112e-01, 0.00000000e+00],
                     [  0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

        # Init.
        sigma_max = 60.0 / 180.0 * pi

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = self.calc_Rx2_eigen_axis(0.0, 0.0)

        # Calculate the matrix.
        f2 = compile_2nd_matrix_rotor(self.f2_temp, Rx2_eigen, sigma_max)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")
        print_frame_order_2nd_degree(real-f2, "difference")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print("Element %s, %s." % (i, j))
                self.assertTrue(abs(f2[i, j] - real[i, j]) < 1e-3)


    def test_reduce_alignment_tensor_order(self):
        """Test the alignment tensor reduction for the order identity matrix."""

        # The tensors.
        A = array([1, 2, 3, 4, 5], float64)
        red = zeros(5, float64)

        # Reduce.
        reduce_alignment_tensor(self.I_order, A, red)

        # Check.
        for i in range(5):
            self.assertEqual(A[i], red[i])


    def test_reduce_alignment_tensor_disorder(self):
        """Test the alignment tensor reduction for the order identity matrix."""

        # The tensors.
        A = array([1, 2, 3, 4, 5], float64)
        red = zeros(5, float64)

        # Reduce.
        reduce_alignment_tensor(self.I_disorder, A, red)

        # Check.
        for i in range(5):
            self.assertEqual(red[i], 0.0)


    def test_reduce_alignment_tensor_half_cone(self):
        """Test the alignment tensor reduction for the order identity matrix."""

        # The tensors.
        A = array([1, 2, 3, 4, 5], float64)
        red = zeros(5, float64)

        # Reduce.
        reduce_alignment_tensor(self.f2_half_cone, A, red)

        # Check.
        for i in range(5):
            self.assertEqual(red[i], 0.0)
