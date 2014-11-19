###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
from numpy import array, float64
from unittest import TestCase

# relax module imports.
from lib.geometry.vectors import vector_angle_acos, vector_angle_atan2, vector_angle_normal


class Test_vectors(TestCase):
    """Unit tests for the lib.geometry.vectors relax module."""

    def test_vector_angle_acos_1(self):
        """Test the vector_angle_acos() function with the vectors [1, 0, 0] and [0, 1, 0]."""

        # Calculate the angle.
        v1 = array([1, 0, 0], float64)
        v2 = array([0, 1, 0], float64)
        angle = vector_angle_acos(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_acos_2(self):
        """Test the vector_angle_acos() function with the vectors [1, 0, 0] and [0, 2, 0]."""

        # Calculate the angle.
        v1 = array([1, 0, 0], float64)
        v2 = array([0, 2, 0], float64)
        angle = vector_angle_acos(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_acos_3(self):
        """Test the vector_angle_acos() function with the vectors [2, 0, 0] and [0, -2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([0, -2, 0], float64)
        angle = vector_angle_acos(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_acos_4(self):
        """Test the vector_angle_acos() function with the vectors [2, 0, 0] and [2, 2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([2, 2, 0], float64)
        angle = vector_angle_acos(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/4.0)


    def test_vector_angle_acos_5(self):
        """Test the vector_angle_acos() function with the vectors [2, 0, 0] and [2, 2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([2, 2, 0], float64)
        angle = vector_angle_acos(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/4.0)


    def test_vector_angle_acos_6(self):
        """Test the vector_angle_acos() function with the vectors [2, 2, 0] and [2, -2, 0]."""

        # Calculate the angle.
        v1 = array([2, 2, 0], float64)
        v2 = array([2, -2, 0], float64)
        angle = vector_angle_acos(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_atan2_1(self):
        """Test the vector_angle_atan2() function with the vectors [1, 0, 0] and [0, 1, 0]."""

        # Calculate the angle.
        v1 = array([1, 0, 0], float64)
        v2 = array([0, 1, 0], float64)
        angle = vector_angle_atan2(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_atan2_2(self):
        """Test the vector_angle_atan2() function with the vectors [1, 0, 0] and [0, 2, 0]."""

        # Calculate the angle.
        v1 = array([1, 0, 0], float64)
        v2 = array([0, 2, 0], float64)
        angle = vector_angle_atan2(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_atan2_3(self):
        """Test the vector_angle_atan2() function with the vectors [2, 0, 0] and [0, -2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([0, -2, 0], float64)
        angle = vector_angle_atan2(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_atan2_4(self):
        """Test the vector_angle_atan2() function with the vectors [2, 0, 0] and [2, 2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([2, 2, 0], float64)
        angle = vector_angle_atan2(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/4.0)


    def test_vector_angle_atan2_5(self):
        """Test the vector_angle_atan2() function with the vectors [2, 0, 0] and [2, 2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([2, 2, 0], float64)
        angle = vector_angle_atan2(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/4.0)


    def test_vector_angle_atan2_6(self):
        """Test the vector_angle_atan2() function with the vectors [2, 2, 0] and [2, -2, 0]."""

        # Calculate the angle.
        v1 = array([2, 2, 0], float64)
        v2 = array([2, -2, 0], float64)
        angle = vector_angle_atan2(v1, v2)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_normal1(self):
        """Test the vector_angle_normal() function with the vectors [1, 0, 0] and [0, 1, 0]."""

        # Calculate the angle.
        v1 = array([1, 0, 0], float64)
        v2 = array([0, 1, 0], float64)
        normal = array([0, 0, 1], float64)
        angle = vector_angle_normal(v1, v2, normal)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_normal2(self):
        """Test the vector_angle_normal() function with the vectors [1, 0, 0] and [0, 2, 0]."""

        # Calculate the angle.
        v1 = array([1, 0, 0], float64)
        v2 = array([0, 2, 0], float64)
        normal = array([0, 0, 1], float64)
        angle = vector_angle_normal(v1, v2, normal)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/2.0)


    def test_vector_angle_normal3(self):
        """Test the vector_angle_normal() function with the vectors [2, 0, 0] and [0, -2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([0, -2, 0], float64)
        normal = array([0, 0, 1], float64)
        angle = vector_angle_normal(v1, v2, normal)

        # Check the angle.
        self.assertAlmostEqual(angle, -pi/2.0)


    def test_vector_angle_normal4(self):
        """Test the vector_angle_normal() function with the vectors [2, 0, 0] and [2, 2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([2, 2, 0], float64)
        normal = array([0, 0, 2], float64)
        angle = vector_angle_normal(v1, v2, normal)

        # Check the angle.
        self.assertAlmostEqual(angle, pi/4.0)


    def test_vector_angle_normal5(self):
        """Test the vector_angle_normal() function with the vectors [2, 0, 0] and [2, 2, 0]."""

        # Calculate the angle.
        v1 = array([2, 0, 0], float64)
        v2 = array([2, 2, 0], float64)
        normal = array([0, 0, -2], float64)
        angle = vector_angle_normal(v1, v2, normal)

        # Check the angle.
        self.assertAlmostEqual(angle, -pi/4.0)


    def test_vector_angle_normal6(self):
        """Test the vector_angle_normal() function with the vectors [2, 2, 0] and [2, -2, 0]."""

        # Calculate the angle.
        v1 = array([2, 2, 0], float64)
        v2 = array([2, -2, 0], float64)
        normal = array([0, 0, 2], float64)
        angle = vector_angle_normal(v1, v2, normal)

        # Check the angle.
        self.assertAlmostEqual(angle, -pi/2.0)
