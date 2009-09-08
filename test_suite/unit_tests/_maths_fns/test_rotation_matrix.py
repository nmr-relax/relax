###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
from math import acos, asin, pi, sqrt
from numpy import array, eye, float64, zeros
from numpy.linalg import norm
from random import uniform
from unittest import TestCase

# relax module imports.
from generic_fns.angles import wrap_angles
from maths_fns.rotation_matrix import *


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
        R = zeros((3, 3), float64)
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
        R = zeros((3, 3), float64)
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
        R = zeros((3, 3), float64)
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


    def test_euler_zyz_to_R_alpha_30(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        euler_zyz_to_R(pi/6, 0.0, 0.0, R)

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
        R = zeros((3, 3), float64)
        euler_zyz_to_R(0.0, pi/4, 0.0, R)

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
        R = zeros((3, 3), float64)
        euler_zyz_to_R(0.0, 0.0, pi/12, R)

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
        R = zeros((3, 3), float64)
        euler_zyz_to_R(pi/12, 0.0, pi/12, R)

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
        self.assertEqual(angle, 2 * pi / 3)

        # Test the vector.
        for i in range(3):
            self.assertAlmostEqual(axis[i], 1.0/sqrt(3))


    def test_R_to_euler_zyz(self):
        """Test the rotation matrix to zyz Euler angle conversion."""

        # Starting angles.
        alpha = uniform(0, 2*pi)
        beta =  uniform(0, pi)
        gamma = uniform(0, 2*pi)

        # Print out.
        print("Original angles:")
        print(("alpha: %s" % alpha))
        print(("beta: %s" % beta))
        print(("gamma: %s\n" % gamma))

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        euler_zyz_to_R(alpha, beta, gamma, R)

        # Get back the angles.
        alpha_new, beta_new, gamma_new = R_to_euler_zyz(R)

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
        R = zeros((3, 3), float64)
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
        R = zeros((3, 3), float64)
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
        R = zeros((3, 3), float64)
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
