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

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real = array([0, 0, 1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real = array([0, 0, -1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])


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

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([0, 1, 0], float64)
        y_real = array([0, 0, 1], float64)
        z_real = array([1, 0, 0], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([0, -1, 0], float64)
        y_real = array([0, 0, -1], float64)
        z_real = array([-1, 0, 0], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])


    def test_R_axis_angle_no_rot(self):
        """Test the quaternion to rotation matrix conversion for a zero angle rotation."""

        # Quaternion of zero angle.
        axis = array([-1, 1, 1], float64) / sqrt(3)
        angle = 0.0

        # The rotation matrix.
        R = zeros((3, 3), float64)
        R_axis_angle(R, axis, angle)
        print("Rotation matrix:\n%s" % R)

        # The correct result.
        R_true = eye(3)

        # Checks.
        for i in range(3):
            for j in range(3):
                self.assertEqual(R[i, j], R_true[i, j])


    def test_R_axis_angle_z_30(self):
        """Test the quaternion to rotation matrix conversion for a 30 degree rotation about z."""

        # Axis-angle values.
        axis = array([0, 0, 1], float64)
        angle = pi / 6

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_axis_angle(R, axis, angle)
        print("Rotation matrix:\n%s" % R)

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real = array([0, 0, 1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real = array([0, 0, -1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])


    def test_R_axis_angle_180_complex(self):
        """Test the quaternion to rotation matrix conversion for a 180 degree rotation about [1, 1, 1]."""

        # Axis-angle values.
        axis = array([1, 1, 1], float64) / sqrt(3)
        angle = 2 * pi / 3

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_axis_angle(R, axis, angle)
        print("Rotation matrix:\n%s" % R)

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([0, 1, 0], float64)
        y_real = array([0, 0, 1], float64)
        z_real = array([1, 0, 0], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([0, -1, 0], float64)
        y_real = array([0, 0, -1], float64)
        z_real = array([-1, 0, 0], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertAlmostEqual(x_new[i], x_real[i])
            self.assertAlmostEqual(y_new[i], y_real[i])
            self.assertAlmostEqual(z_new[i], z_real[i])


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


    def test_R_euler_zyz_alpha_30(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_euler_zyz(R, pi/6, 0.0, 0.0)

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real = array([0, 0, 1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real = array([0, 0, -1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])


    def test_R_euler_zyz_beta_45(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_euler_zyz(R, 0.0, pi/4, 0.0)

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([cos(pi/4), 0, -sin(pi/4)], float64)
        y_real = array([0, 1, 0], float64)
        z_real = array([sin(pi/4), 0, cos(pi/4)], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([-cos(pi/4), 0, sin(pi/4)], float64)
        y_real = array([0, -1, 0], float64)
        z_real = array([-sin(pi/4), 0, -cos(pi/4)], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])


    def test_R_euler_zyz_gamma_15(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_euler_zyz(R, 0.0, 0.0, pi/12)

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([cos(pi/12), sin(pi/12), 0], float64)
        y_real = array([-sin(pi/12), cos(pi/12), 0], float64)
        z_real = array([0, 0, 1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([-cos(pi/12), -sin(pi/12), 0], float64)
        y_real = array([sin(pi/12), -cos(pi/12), 0], float64)
        z_real = array([0, 0, -1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])


    def test_R_euler_zyz_alpha_15_gamma_15(self):
        """Test the rotation matrix from zyz Euler angle conversion using a beta angle of pi/4."""

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_euler_zyz(R, pi/12, 0.0, pi/12)

        # Axes.
        x_axis = array([1, 0, 0], float64)
        y_axis = array([0, 1, 0], float64)
        z_axis = array([0, 0, 1], float64)

        # Rotated axis (real values).
        x_real = array([cos(pi/6), sin(pi/6), 0], float64)
        y_real = array([-sin(pi/6), cos(pi/6), 0], float64)
        z_real = array([0, 0, 1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])

        # Axes (do everything again, this time negative!).
        x_axis = array([-1, 0, 0], float64)
        y_axis = array([0, -1, 0], float64)
        z_axis = array([0, 0, -1], float64)

        # Rotated axis (real values).
        x_real = array([-cos(pi/6), -sin(pi/6), 0], float64)
        y_real = array([sin(pi/6), -cos(pi/6), 0], float64)
        z_real = array([0, 0, -1], float64)

        # Rotation.
        x_new = dot(R, x_axis)
        y_new = dot(R, y_axis)
        z_new = dot(R, z_axis)

        # Print out.
        print("Rotated and true axes (beta = pi/4):")
        print(("x rot:  %s" % x_new))
        print(("x real: %s\n" % x_real))
        print(("y rot:  %s" % y_new))
        print(("y real: %s\n" % y_real))
        print(("z rot:  %s" % z_new))
        print(("z real: %s\n" % z_real))

        # Checks.
        for i in range(3):
            self.assertEqual(x_new[i], x_real[i])
            self.assertEqual(y_new[i], y_real[i])
            self.assertEqual(z_new[i], z_real[i])


            self.assertEqual(z_new[i], z_real[i])


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
        R_euler_zyz(R, alpha, beta, gamma)

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
