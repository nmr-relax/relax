###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
from copy import deepcopy
from math import acos, asin, pi, sqrt
from numpy import array, eye, float64, zeros
from numpy.linalg import norm
from random import shuffle, uniform
from unittest import TestCase

# relax module imports.
from generic_fns.angles import wrap_angles
from maths_fns.rotation_matrix import *


# Global variables (reusable storage).
R = zeros((3, 3), float64)
R2 = zeros((3, 3), float64)


class Test_rotation_matrix(TestCase):
    """Unit tests for the maths_fns.rotation_matrix relax module."""

    def setUp(self):
        """Set up data used by the unit tests."""

        # Axes.
        self.x_axis_pos = array([1, 0, 0], float64)
        self.y_axis_pos = array([0, 1, 0], float64)
        self.z_axis_pos = array([0, 0, 1], float64)

        # Axes (do everything again, this time negative!).
        self.x_axis_neg = array([-1, 0, 0], float64)
        self.y_axis_neg = array([0, -1, 0], float64)
        self.z_axis_neg = array([0, 0, -1], float64)


    def check_return_conversion(self, euler_to_R=None, R_to_euler=None, alpha_start=None, beta_start=None, gamma_start=None, alpha_end=None, beta_end=None, gamma_end=None):
        """Check the Euler angle to rotation matrix to Euler angle conversion."""

        # Print out.
        print_out = ""
        print_out = print_out + "\n\n# Checking the %s() and %s() conversions.\n\n" % (euler_to_R.__name__, R_to_euler.__name__)

        # A small number.
        epsilon = 1e-15

        # End angles.
        if alpha_end == None:
            alpha_end = alpha_start
        if beta_end == None:
            beta_end = beta_start
        if gamma_end == None:
            gamma_end = gamma_start

        # Generate the rotation matrix.
        euler_to_R(alpha_start, beta_start, gamma_start, R)
        print_out = print_out + "R: |%8.5f, %8.5f, %8.5f|\n" % (R[0, 0], R[0, 1], R[0, 2])
        print_out = print_out + "   |%8.5f, %8.5f, %8.5f|\n" % (R[1, 0], R[1, 1], R[1, 2])
        print_out = print_out + "   |%8.5f, %8.5f, %8.5f|\n" % (R[2, 0], R[2, 1], R[2, 2])

        # Get back the angles.
        alpha_new, beta_new, gamma_new = R_to_euler(R)

        # Print out.
        print_out = print_out + "Original angles:     (%8.5f, %8.5f, %8.5f)\n" % (alpha_start, beta_start, gamma_start)
        print_out = print_out + "End angles:          (%8.5f, %8.5f, %8.5f)\n" % (alpha_end, beta_end, gamma_end)
        print_out = print_out + "New angles:          (%8.5f, %8.5f, %8.5f)\n" % (alpha_new, beta_new, gamma_new)

        # Wrap the angles.
        alpha_new = wrap_angles(alpha_new, 0-epsilon, 2*pi-epsilon)
        beta_new = wrap_angles(beta_new, 0-epsilon, 2*pi-epsilon)
        gamma_new = wrap_angles(gamma_new, 0-epsilon, 2*pi-epsilon)

        # Print out.
        print_out = print_out + "New angles (wrapped) (%8.5f, %8.5f, %8.5f)\n" % (alpha_new, beta_new, gamma_new)

        # Second solution required!
        if abs(beta_end - beta_new) > 1e-7:
            # Collapse the multiple beta solutions.
            if beta_new < pi:
                alpha_new = alpha_new + pi
                beta_new = pi - beta_new
                gamma_new = gamma_new + pi
            else:
                alpha_new = alpha_new + pi
                beta_new = 3*pi - beta_new
                gamma_new = gamma_new + pi

            # Wrap the angles.
            alpha_new = wrap_angles(alpha_new, 0-epsilon, 2*pi-epsilon)
            beta_new = wrap_angles(beta_new, 0-epsilon, 2*pi-epsilon)
            gamma_new = wrap_angles(gamma_new, 0-epsilon, 2*pi-epsilon)

            # Print out.
            print_out = print_out + "New angles (2nd sol) (%8.5f, %8.5f, %8.5f)\n" % (alpha_new, beta_new, gamma_new)

        # Print out.
        eps = 1e-5
        if abs(alpha_new - alpha_end) > eps or abs(beta_new - beta_end) > eps or abs(gamma_new - gamma_end) > eps:
            print(print_out)

        # Checks.
        self.assertAlmostEqual(alpha_end, alpha_new)
        self.assertAlmostEqual(beta_end, beta_new)
        self.assertAlmostEqual(gamma_end, gamma_new)


    def check_rotation(self, R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg):
        """Check that the rotation matrix is correct."""

        # Rotate the 6 axes.
        x_new_pos = dot(R, self.x_axis_pos)
        y_new_pos = dot(R, self.y_axis_pos)
        z_new_pos = dot(R, self.z_axis_pos)

        x_new_neg = dot(R, self.x_axis_neg)
        y_new_neg = dot(R, self.y_axis_neg)
        z_new_neg = dot(R, self.z_axis_neg)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x pos rot:  %s" % x_new_pos))
        print(("x pos real: %s\n" % x_real_pos))
        print(("y pos rot:  %s" % y_new_pos))
        print(("y pos real: %s\n" % y_real_pos))
        print(("z pos rot:  %s" % z_new_pos))
        print(("z pos real: %s\n" % z_real_pos))

        print(("x neg rot:  %s" % x_new_neg))
        print(("x neg real: %s\n" % x_real_neg))
        print(("y neg rot:  %s" % y_new_neg))
        print(("y neg real: %s\n" % y_real_neg))
        print(("z neg rot:  %s" % z_new_neg))
        print(("z neg real: %s\n" % z_real_neg))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new_pos[i], x_real_pos[i])
            self.assertAlmostEqual(y_new_pos[i], y_real_pos[i])
            self.assertAlmostEqual(z_new_pos[i], z_real_pos[i])

            self.assertAlmostEqual(x_new_neg[i], x_real_neg[i])
            self.assertAlmostEqual(y_new_neg[i], y_real_neg[i])
            self.assertAlmostEqual(z_new_neg[i], z_real_neg[i])


    def test_axis_angle_to_R_no_rot(self):
        """Test the quaternion to rotation matrix conversion for a zero angle rotation."""

        # Quaternion of zero angle.
        axis = array([-1, 1, 1], float64) / sqrt(3)
        angle = 0.0

        # The rotation matrix.
        axis_angle_to_R(axis, angle, R)
        print("Rotation matrix:\n%s" % R)

        # The correct result.
        R_true = eye(3)

        # Checks.
        for i in range(3):
            for j in range(3):
                self.assertEqual(R[i, j], R_true[i, j])


    def test_axis_angle_to_quaternion_no_rot(self):
        """Test the axis-angle to quaternion conversion for a zero angle rotation."""

        # Random axis and zero angle.
        axis = array([-1, 1, 1], float64) / sqrt(3)
        angle = 0.0

        # The quaternion matrix.
        quat = zeros(4, float64)
        axis_angle_to_quaternion(axis, angle, quat)
        print("Quaternion:\n%s" % quat)

        # The correct result.
        quat_true = array([1, 0, 0, 0], float64)

        # Checks.
        for i in range(4):
            self.assertEqual(quat[i], quat_true[i])


    def test_axis_angle_to_quaternion_180_complex(self):
        """Test the axis-angle to quaternion conversion for a 180 degree rotation about [1, 1, 1]."""

        # Random axis and zero angle.
        axis = array([1, 1, 1], float64) / sqrt(3)
        angle = pi

        # The quaternion matrix.
        quat = zeros(4, float64)
        axis_angle_to_quaternion(axis, angle, quat)
        print("Quaternion:\n%s" % quat)

        # The correct result.
        quat_true = array([0, 1, 1, 1], float64) / sqrt(3)

        # Checks.
        for i in range(4):
            self.assertAlmostEqual(quat[i], quat_true[i])


    def test_axis_angle_to_R_z_30(self):
        """Test the quaternion to rotation matrix conversion for a 30 degree rotation about z."""

        # Axis-angle values.
        axis = array([0, 0, 1], float64)
        angle = pi / 6

        # Generate the rotation matrix.
        axis_angle_to_R(axis, angle, R)
        print("Rotation matrix:\n%s" % R)

        # Rotated pos_axes (real values).
        x_real_pos = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real_pos = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real_pos = array([0, 0, 1], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real_neg = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real_neg = array([0, 0, -1], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_axis_angle_to_R_180_complex(self):
        """Test the quaternion to rotation matrix conversion for a 180 degree rotation about [1, 1, 1]."""

        # Axis-angle values.
        axis = array([1, 1, 1], float64) / sqrt(3)
        angle = 2 * pi / 3

        # Generate the rotation matrix.
        axis_angle_to_R(axis, angle, R)
        print("Rotation matrix:\n%s" % R)

        # Rotated pos axes (real values).
        x_real_pos = array([0, 1, 0], float64)
        y_real_pos = array([0, 0, 1], float64)
        z_real_pos = array([1, 0, 0], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([0, -1, 0], float64)
        y_real_neg = array([0, 0, -1], float64)
        z_real_neg = array([-1, 0, 0], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_euler_cycle_1(self):
        """Cycle through all the hard-coded conversion functions returning to the starting point.

        The nested cycling is as follows:
            - start with random Euler angles alpha, beta, gamma,
            - convert to a rotation matrix using euler_to_R_xyx(),
            - xyx cycle:
                - R_to_euler_xyx()
                - euler_to_R_xyx(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_xyx(),
                - euler_to_axis_angle_xyx(),
                - axis_angle_to_R(),
            - xyz cycle:
                - R_to_euler_xyz()
                - euler_to_R_xyz(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_xyz(),
                - euler_to_axis_angle_xyz(),
                - axis_angle_to_R(),
            - xzx cycle:
                - R_to_euler_xzx()
                - euler_to_R_xzx(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_xzx(),
                - euler_to_axis_angle_xzx(),
                - axis_angle_to_R(),
             - xzy cycle:
                - R_to_euler_xzy()
                - euler_to_R_xzy(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_xzy(),
                - euler_to_axis_angle_xzy(),
                - axis_angle_to_R(),
             - yxy cycle:
                - R_to_euler_yxy()
                - euler_to_R_yxy(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_yxy(),
                - euler_to_axis_angle_yxy(),
                - axis_angle_to_R(),
             - yxz cycle:
                - R_to_euler_yxz()
                - euler_to_R_yxz(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_yxz(),
                - euler_to_axis_angle_yxz(),
                - axis_angle_to_R(),
             - yzx cycle:
                - R_to_euler_yzx()
                - euler_to_R_yzx(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_yzx(),
                - euler_to_axis_angle_yzx(),
                - axis_angle_to_R(),
             - yzy cycle:
                - R_to_euler_yzy()
                - euler_to_R_yzy(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_yzy(),
                - euler_to_axis_angle_yzy(),
                - axis_angle_to_R(),
             - zxy cycle:
                - R_to_euler_zxy()
                - euler_to_R_zxy(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_zxy(),
                - euler_to_axis_angle_zxy(),
                - axis_angle_to_R(),
             - zxz cycle:
                - R_to_euler_zxz()
                - euler_to_R_zxz(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_zxz(),
                - euler_to_axis_angle_zxz(),
                - axis_angle_to_R(),
             - zyx cycle:
                - R_to_euler_zyx()
                - euler_to_R_zyx(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_zyx(),
                - euler_to_axis_angle_zyx(),
                - axis_angle_to_R(),
             - zyz cycle:
                - R_to_euler_zyz()
                - euler_to_R_zyz(),
                - R_to_axis_angle(),
                - axis_angle_to_euler_zyz(),
                - euler_to_axis_angle_zyz(),
                - axis_angle_to_R(),
            - return to start with R_to_euler_xyx().
         """

        # Starting angles.
        alpha_init = uniform(0, 2*pi)
        beta_init =  uniform(0, pi)
        gamma_init = uniform(0, 2*pi)

        # The start point.
        euler_to_R_xyx(alpha_init, beta_init, gamma_init, R)
        euler_to_R_xyx(alpha_init, beta_init, gamma_init, R2)

        # Print out.
        print("Original data:")
        print(("alpha: %s" % alpha_init))
        print(("beta: %s" % beta_init))
        print(("gamma: %s\n" % gamma_init))
        print(("R:\n%s\n" % R2))

        # The different notations.
        sets = ['xyx', 'xyz', 'xzx', 'xzy', 'yxy', 'yxz', 'yzx', 'yzy', 'zxy', 'zxz', 'zyx', 'zyz']
        shuffle(sets)

        # Cycle over the notations.
        for set in sets:
            # Header printout.
            print("\n\n# %s cycle.\n" % set)

            # Alias the functions.
            axis_angle_to_euler = globals()['axis_angle_to_euler_'+set]
            euler_to_axis_angle = globals()['euler_to_axis_angle_'+set]
            euler_to_R = globals()['euler_to_R_'+set]
            R_to_euler = globals()['R_to_euler_'+set]

            # R -> Euler.
            a, b, g = R_to_euler(R)
            print("R -> Euler: [%-8.5f, %-8.5f, %-8.5f]\n" % (a, b, g))

            # Euler -> R
            euler_to_R(a, b, g, R)
            print(("Euler -> R:\n%s\n" % R))

            # R -> axis, angle.
            axis, angle = R_to_axis_angle(R)
            print("R -> axis, angle: [%-8.5f, %-8.5f, %-8.5f], %s\n" % (axis[0], axis[1], axis[2], angle))

            # axis, angle -> Euler.
            a, b, g = axis_angle_to_euler(axis, angle)
            print("axis, angle -> Euler: [%-8.5f, %-8.5f, %-8.5f]\n" % (a, b, g))

            # Euler -> axis, angle.
            axis, angle = euler_to_axis_angle(a, b, g)
            print("Euler -> axis, angle: [%-8.5f, %-8.5f, %-8.5f], %s\n" % (axis[0], axis[1], axis[2], angle))

            # axis, angle -> R.
            axis_angle_to_R(axis, angle, R)
            print(("axis, angle -> R:\n%s\n" % R))

            # Print out the rotation matrix.
            print("Rotation matrix difference:\n%s\n" % (R2-R))

            # Check the rotation matrix.
            for i in range(3):
                for j in range(3):
                    self.assertAlmostEqual(R[i, j], R2[i, j])

        # The end point.
        alpha_end, beta_end, gamma_end = R_to_euler_xyx(R)

        # Print out.
        print("End data:")
        print(("alpha: %s" % alpha_end))
        print(("beta: %s" % beta_end))
        print(("gamma: %s\n" % gamma_end))
        print(("R:\n%s\n" % R))

        # Checks.
        self.assertAlmostEqual(alpha_init, alpha_end)
        self.assertAlmostEqual(beta_init, beta_end)
        self.assertAlmostEqual(gamma_init, gamma_end)


    def test_euler_zyz_to_euler_zyz(self):
        """Bounce around all the conversion functions to see if the original angles are returned."""

        # Starting angles.
        alpha = uniform(0, 2*pi)
        beta =  uniform(0, pi)
        gamma = uniform(0, 2*pi)

        # Print out.
        print("Original angles:")
        print(("alpha: %s" % alpha))
        print(("beta: %s" % beta))
        print(("gamma: %s\n" % gamma))

        # Init.
        axis = zeros(3, float64)
        quat = zeros(4, float64)

        # 1) Euler angles to rotation matrix.
        euler_to_R_zyz(alpha, beta, gamma, R)

        # 2) Rotation matrix to axis-angle.
        axis, angle = R_to_axis_angle(R)

        # 3) Axis-angle to quaternion.
        axis_angle_to_quaternion(axis, angle, quat)

        # 4) Quaternion to axis-angle.
        axis, angle = quaternion_to_axis_angle(quat)

        # 5) Axis-angle to rotation matrix.
        axis_angle_to_R(axis, angle, R)

        # 6) Rotation matrix to quaternion.
        R_to_quaternion(R, quat)

        # 7) Quaternion to rotation matrix.
        quaternion_to_R(quat, R)

        # 8) Rotation matrix to Euler angles.
        alpha_new, beta_new, gamma_new = R_to_euler_zyz(R)

        # 9) Euler angles to axis-angle.
        axis, angle = euler_to_axis_angle_zyz(alpha_new, beta_new, gamma_new)

        # 10) Axis-angle to Euler angles.
        alpha_new, beta_new, gamma_new = axis_angle_to_euler_zyz(axis, angle)

        # Wrap the angles.
        alpha_new = wrap_angles(alpha_new, 0, 2*pi)
        beta_new = wrap_angles(beta_new, 0, 2*pi)
        gamma_new = wrap_angles(gamma_new, 0, 2*pi)

        # Print out.
        print("New angles:")
        print(("alpha: %s" % alpha_new))
        print(("beta: %s" % beta_new))
        print(("gamma: %s\n" % gamma_new))

        # Checks.
        self.assertAlmostEqual(alpha, alpha_new)
        self.assertAlmostEqual(beta, beta_new)
        self.assertAlmostEqual(gamma, gamma_new)


    def test_euler_zyz_to_R_alpha_30(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        euler_to_R_zyz(pi/6, 0.0, 0.0, R)

        # Rotated pos axes (real values).
        x_real_pos = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real_pos = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real_pos = array([0, 0, 1], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real_neg = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real_neg = array([0, 0, -1], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_euler_zyz_to_R_beta_45(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        euler_to_R_zyz(0.0, pi/4, 0.0, R)

        # Rotated pos axes (real values).
        x_real_pos = array([cos(pi/4), 0, -sin(pi/4)], float64)
        y_real_pos = array([0, 1, 0], float64)
        z_real_pos = array([sin(pi/4), 0, cos(pi/4)], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([-cos(pi/4), 0, sin(pi/4)], float64)
        y_real_neg = array([0, -1, 0], float64)
        z_real_neg = array([-sin(pi/4), 0, -cos(pi/4)], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_euler_zyz_to_R_gamma_15(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        euler_to_R_zyz(0.0, 0.0, pi/12, R)

        # Rotated pos axes (real values).
        x_real_pos = array([cos(pi/12), sin(pi/12), 0], float64)
        y_real_pos = array([-sin(pi/12), cos(pi/12), 0], float64)
        z_real_pos = array([0, 0, 1], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([-cos(pi/12), -sin(pi/12), 0], float64)
        y_real_neg = array([sin(pi/12), -cos(pi/12), 0], float64)
        z_real_neg = array([0, 0, -1], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_euler_zyz_to_R_alpha_15_gamma_15(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        euler_to_R_zyz(pi/12, 0.0, pi/12, R)

        # Rotated pos axes (real values).
        x_real_pos = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real_pos = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real_pos = array([0, 0, 1], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real_neg = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real_neg = array([0, 0, -1], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_R_to_axis_angle_no_rot(self):
        """Test the rotation matrix to axis-angle conversion."""

        # Generate the rotation matrix.
        R = array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float64)

        # Get the axis and angle.
        axis, angle = R_to_axis_angle(R)

        # Test the angle.
        self.assertEqual(angle, 0.0)


    def test_R_to_axis_angle_180_complex(self):
        """Test the rotation matrix to axis-angle conversion."""

        # Generate the rotation matrix.
        R = array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float64)

        # Get the axis and angle.
        axis, angle = R_to_axis_angle(R)

        # Test the angle.
        self.assertAlmostEqual(angle, 2 * pi / 3)

        # Test the vector.
        for i in range(3):
            self.assertAlmostEqual(axis[i], 1.0/sqrt(3))


    def test_R_to_euler_to_R_xyx(self):
        """Test the rotation matrix to xyx Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_xyx(R)
        euler_to_R_xyx(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_xyz(self):
        """Test the rotation matrix to xyz Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_xyz(R)
        euler_to_R_xyz(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_xzx(self):
        """Test the rotation matrix to xzx Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_xzx(R)
        euler_to_R_xzx(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_xzy(self):
        """Test the rotation matrix to xzy Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_xzy(R)
        euler_to_R_xzy(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_yxy(self):
        """Test the rotation matrix to yxy Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_yxy(R)
        euler_to_R_yxy(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_yxz(self):
        """Test the rotation matrix to yxz Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_yxz(R)
        euler_to_R_yxz(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_yzx(self):
        """Test the rotation matrix to yzx Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_yzx(R)
        euler_to_R_yzx(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_yzy(self):
        """Test the rotation matrix to yzy Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_yzy(R)
        euler_to_R_yzy(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_zxy(self):
        """Test the rotation matrix to zxy Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_zxy(R)
        euler_to_R_zxy(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_zxz(self):
        """Test the rotation matrix to zxz Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_zxz(R)
        euler_to_R_zxz(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_zyx(self):
        """Test the rotation matrix to zyx Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_zyx(R)
        euler_to_R_zyx(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_to_R_zyz(self):
        """Test the rotation matrix to zyz Euler angle conversion and back again."""

        # Random rotation matrix.
        R_random_hypersphere(R)
        R_orig = deepcopy(R)

        # Convert.
        a, b, g = R_to_euler_zyz(R)
        euler_to_R_zyz(a, b, g, R2)

        # Check the rotation matrix.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(R_orig[i, j], R2[i, j])


    def test_R_to_euler_xyx(self):
        """Test the rotation matrix to xyx Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 0.0, 0.0, 1.0, alpha_end=1.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 1.0, 0.0, 1.0, alpha_end=2.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 1.0, pi/2, 0.5)
        self.check_return_conversion(euler_to_R_xyx, R_to_euler_xyx, 1.0, pi, 0.5, alpha_end=0.5, gamma_end=0.0)


    def test_R_to_euler_xyz(self):
        """Test the rotation matrix to xyz Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 0.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 1.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 1.0, pi/2, 0.5, alpha_end=0.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_xyz, R_to_euler_xyz, 1.0, pi, 0.5)


    def test_R_to_euler_xzx(self):
        """Test the rotation matrix to xzx Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 0.0, 0.0, 1.0, alpha_end=1.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 1.0, 0.0, 1.0, alpha_end=2.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 1.0, pi/2, 0.5)
        self.check_return_conversion(euler_to_R_xzx, R_to_euler_xzx, 1.0, pi, 0.5, alpha_end=0.5, gamma_end=0.0)


    def test_R_to_euler_xzy(self):
        """Test the rotation matrix to xzy Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 0.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 1.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 1.0, pi/2, 0.5, alpha_end=1.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_xzy, R_to_euler_xzy, 1.0, pi, 0.5)


    def test_R_to_euler_yxy(self):
        """Test the rotation matrix to yxy Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 0.0, 0.0, 1.0, alpha_end=1.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 1.0, 0.0, 1.0, alpha_end=2.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 1.0, pi/2, 0.5)
        self.check_return_conversion(euler_to_R_yxy, R_to_euler_yxy, 1.0, pi, 0.5, alpha_end=0.5, gamma_end=0.0)


    def test_R_to_euler_yxz(self):
        """Test the rotation matrix to yxz Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 0.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 1.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 1.0, pi/2, 0.5, alpha_end=1.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_yxz, R_to_euler_yxz, 1.0, pi, 0.5)


    def test_R_to_euler_yzx(self):
        """Test the rotation matrix to yzx Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 0.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 1.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 1.0, pi/2, 0.5, alpha_end=0.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_yzx, R_to_euler_yzx, 1.0, pi, 0.5)


    def test_R_to_euler_yzy(self):
        """Test the rotation matrix to yzy Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 0.0, 0.0, 1.0, alpha_end=1.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 1.0, 0.0, 1.0, alpha_end=2.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 1.0, pi/2, 0.5)
        self.check_return_conversion(euler_to_R_yzy, R_to_euler_yzy, 1.0, pi, 0.5, alpha_end=0.5, gamma_end=0.0)


    def test_R_to_euler_zxy(self):
        """Test the rotation matrix to zxy Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 0.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 1.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 1.0, pi/2, 0.5, alpha_end=0.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zxy, R_to_euler_zxy, 1.0, pi, 0.5)


    def test_R_to_euler_zxz(self):
        """Test the rotation matrix to zxz Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 0.0, 0.0, 1.0, alpha_end=1.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 1.0, 0.0, 1.0, alpha_end=2.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 1.0, pi/2, 0.5)
        self.check_return_conversion(euler_to_R_zxz, R_to_euler_zxz, 1.0, pi, 0.5, alpha_end=0.5, gamma_end=0.0)


    def test_R_to_euler_zyx(self):
        """Test the rotation matrix to zyx Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 5.0, 2.0, 1.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 0.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 1.0, 0.0, 1.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 1.0, pi/2, 0.5, alpha_end=1.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zyx, R_to_euler_zyx, 1.0, pi, 0.5, alpha_end=1.0+pi, beta_end=0.0, gamma_end=0.5+pi)


    def test_R_to_euler_zyz(self):
        """Test the rotation matrix to zyz Euler angle conversion."""

        # Check random numbers, then the problematic angles.
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, uniform(0, 2*pi), uniform(0, pi), uniform(0, 2*pi))
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 0.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, 0.0, 0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 0.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 0.0, 0.0, 1.0, alpha_end=1.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, 1.0, 0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 0.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, 0.0, 1.0, alpha_end=2.0, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, 1.0, 1.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, pi/2, 0.5)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, pi, 0.5, alpha_end=0.5, gamma_end=0.0)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, -pi/2, 0.5, alpha_end=1.0+pi, beta_end=pi/2, gamma_end=0.5+pi)
        self.check_return_conversion(euler_to_R_zyz, R_to_euler_zyz, 1.0, 1.5*pi, 0.5, alpha_end=1.0+pi, beta_end=pi/2, gamma_end=0.5+pi)


    def test_R_to_quaternion_no_rot(self):
        """Test the rotation matrix to quaternion conversion for a zero angle rotation."""

        # Generate the rotation matrix.
        R = array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float64)

        # The quaternion.
        quat = zeros(4, float64)
        R_to_quaternion(R, quat)
        print("Quaternion:\n%s" % quat)

        # The correct result.
        quat_true = array([1, 0, 0, 0], float64)

        # Checks.
        self.assertEqual(norm(quat), 1)
        for i in range(4):
            self.assertAlmostEqual(quat[i], quat_true[i])


    def test_R_to_quaternion_180_complex(self):
        """Test the rotation matrix to quaternion conversion for a 180 degree rotation about [1, 1, 1]."""

        # Generate the rotation matrix.
        R = array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float64)

        # The quaternion.
        quat = zeros(4, float64)
        R_to_quaternion(R, quat)
        print("Quaternion:\n%s" % quat)

        # The correct result.
        quat_true = array([1, 1, 1, 1], float64) / 2

        # Checks.
        self.assertEqual(norm(quat), 1)
        for i in range(4):
            self.assertAlmostEqual(quat[i], quat_true[i])


    def test_reverse_euler_zyz_a0_b0_g0(self):
        """Test the reverse Euler angle conversion for {0, 0, 0}."""

        # The forward angles.
        euler = [0.0, 0.0, 0.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_reverse_euler_zyz_a1_b0_g0(self):
        """Test the reverse Euler angle conversion for {1, 0, 0}."""

        # The forward angles.
        euler = [1.0, 0.0, 0.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_reverse_euler_zyz_a0_b1_g0(self):
        """Test the reverse Euler angle conversion for {0, 1, 0}."""

        # The forward angles.
        euler = [0.0, 1.0, 0.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_reverse_euler_zyz_a0_b0_g1(self):
        """Test the reverse Euler angle conversion for {0, 0, 1}."""

        # The forward angles.
        euler = [0.0, 0.0, 1.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0]+euler[2])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, 0.0)


    def test_reverse_euler_zyz_a1_b1_g0(self):
        """Test the reverse Euler angle conversion for {1, 1, 0}."""

        # The forward angles.
        euler = [1.0, 1.0, 0.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_reverse_euler_zyz_a0_b1_g1(self):
        """Test the reverse Euler angle conversion for {0, 1, 1}."""

        # The forward angles.
        euler = [0.0, 1.0, 1.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_reverse_euler_zyz_a1_b0_g1(self):
        """Test the reverse Euler angle conversion for {1, 0, 1}."""

        # The forward angles.
        euler = [1.0, 0.0, 1.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0]+euler[2])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, 0.0)


    def test_reverse_euler_zyz_a1_b1_g1(self):
        """Test the reverse Euler angle conversion for {1, 1, 1}."""

        # The forward angles.
        euler = [1.0, 1.0, 1.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_reverse_euler_zyz_a1_b0_5_g3(self):
        """Test the reverse Euler angle conversion for {1, 0.5, 3}."""

        # The forward angles.
        euler = [1.0, 0.5, 3.0]

        # Convert twice.
        a, b, g = reverse_euler_zyz(euler[0], euler[1], euler[2])
        a, b, g = reverse_euler_zyz(a, b, g)

        # Check the reversed, reverse angles.
        self.assertAlmostEqual(a, euler[0])
        self.assertAlmostEqual(b, euler[1])
        self.assertAlmostEqual(g, euler[2])


    def test_quaternion_to_axis_angle_no_rot(self):
        """Test the quaternion to rotation matrix conversion for a zero angle rotation."""

        # Quaternion of zero angle.
        quat = array([1, 0, 0, 0], float64)

        # The axis and angle.
        axis, angle = quaternion_to_axis_angle(quat)
        print("Axis:  %s" % axis)
        print("Angle: %s" % angle)

        # The correct result.
        self.assertEqual(angle, 0.0)
        for i in range(3):
            self.assertEqual(axis[i], 0.0)


    def test_quaternion_to_axis_angle_180_complex(self):
        """Test the quaternion to axis-angle conversion for a 180 degree rotation about [1, 1, 1]."""

        # The quaternion.
        quat = array([0, 1, 1, 1], float64) / sqrt(3)

        # The axis and angle.
        axis, angle = quaternion_to_axis_angle(quat)
        print("Axis:  %s" % axis)
        print("Angle: %s" % angle)

        # The correct result.
        self.assertEqual(angle, pi)
        for i in range(3):
            self.assertEqual(axis[i], 1.0 / sqrt(3))



    def test_quaternion_to_R_no_rot(self):
        """Test the quaternion to rotation matrix conversion for a zero angle rotation."""

        # Quaternion of zero angle.
        quat = array([1, 0, 0, 0], float64)

        # The rotation matrix.
        quaternion_to_R(quat, R)
        print("Rotation matrix:\n%s" % R)

        # The correct result.
        R_true = eye(3)

        # Checks.
        for i in range(3):
            for j in range(3):
                self.assertEqual(R[i, j], R_true[i, j])


    def test_quaternion_to_R_z_30(self):
        """Test the quaternion to rotation matrix conversion for a 30 degree rotation about z."""

        # Axis-angle values.
        axis = array([0, 0, 1], float64)
        angle = pi / 6

        # First element.
        w = cos(angle / 2)

        # Vector reduction (quaternion normalisation).
        factor = sqrt(1 - w**2)
        axis = axis * factor

        # Quaternion.
        quat = zeros(4, float64)
        quat[0] = w
        quat[1:] = axis
        print("Quat: %s" % quat)
        print("Quat norm: %s" % norm(quat))

        # Quaternion check.
        w_check = cos(asin(sqrt(quat[1]**2 + quat[2]**2 + quat[3]**2)))
        self.assertEqual(w, w_check)
        self.assertEqual(norm(quat), 1)

        # Generate the rotation matrix.
        quaternion_to_R(quat, R)
        print("Rotation matrix:\n%s" % R)

        # Rotated pos axes (real values).
        x_real_pos = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real_pos = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real_pos = array([0, 0, 1], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real_neg = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real_neg = array([0, 0, -1], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)


    def test_quaternion_to_R_180_complex(self):
        """Test the quaternion to rotation matrix conversion for a 180 degree rotation about [1, 1, 1]."""

        # Axis-angle values.
        axis = array([1, 1, 1], float64) / sqrt(3)
        angle = 2 * pi / 3

        # First element.
        w = cos(angle / 2)

        # Vector reduction (quaternion normalisation).
        factor = sqrt(1 - w**2)
        axis = axis * factor

        # Quaternion.
        quat = zeros(4, float64)
        quat[0] = w
        quat[1:] = axis
        print("Quat: %s" % quat)
        print("Quat norm: %s" % norm(quat))

        # Quaternion check.
        w_check = cos(asin(sqrt(quat[1]**2 + quat[2]**2 + quat[3]**2)))
        self.assertAlmostEqual(w, w_check)
        self.assertEqual(norm(quat), 1)

        # Generate the rotation matrix.
        quaternion_to_R(quat, R)
        print("Rotation matrix:\n%s" % R)

        # Rotated pos axes (real values).
        x_real_pos = array([0, 1, 0], float64)
        y_real_pos = array([0, 0, 1], float64)
        z_real_pos = array([1, 0, 0], float64)

        # Rotated neg axes (real values).
        x_real_neg = array([0, -1, 0], float64)
        y_real_neg = array([0, 0, -1], float64)
        z_real_neg = array([-1, 0, 0], float64)

        # Check the rotation.
        self.check_rotation(R, x_real_pos, y_real_pos, z_real_pos, x_real_neg, y_real_neg, z_real_neg)
