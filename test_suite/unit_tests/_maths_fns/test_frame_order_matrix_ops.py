###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
from math import pi
from numpy import array, eye, float64, zeros
from unittest import TestCase

# relax module imports.
from generic_fns.frame_order import print_frame_order_2nd_degree
from maths_fns.frame_order_matrix_ops import *
from maths_fns.kronecker_product import transpose_23


class Test_frame_order_matrix_ops(TestCase):
    """Unit tests for the maths_fns.frame_order_matrix_ops relax module."""

    def setUp(self):
        """Initialise a few data structures for the tests."""

        # Temp storage.
        self.f2_temp = zeros((9, 9), float64)

        # Set up the identity matrices.
        self.setup_identity()

        # Set up the identity matrices for free rotors.
        self.setup_identity_free_rotor()


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


    def test_compile_2nd_matrix_iso_cone_disorder(self):
        """Check if compile_2nd_matrix_iso_cone() can return the identity matrix for disorder."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, R, 0.0, 0.0, 0.0, pi, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_iso_cone_order(self):
        """Check if compile_2nd_matrix_iso_cone() can return the identity matrix for order."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, R, 0.0, 0.0, 0.0, 1e-5, 1e-10)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order, "Identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_order[i, j])


    def test_compile_2nd_matrix_iso_cone_order2(self):
        """2nd check if compile_2nd_matrix_iso_cone() can return the identity matrix for order."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone(self.f2_temp, R, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order, "Identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_order[i, j])


    def test_compile_2nd_matrix_iso_cone_free_rotor_disorder(self):
        """Check if compile_2nd_matrix_iso_cone_free_rotor() can return the identity matrix for disorder."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, R, z_axis, cone_axis, 0.0, 1.0, 0.0)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Free rotor identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_iso_cone_free_rotor_order(self):
        """Check if compile_2nd_matrix_iso_cone_free_rotor() can return the identity matrix for order."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_iso_cone_free_rotor(self.f2_temp, R, z_axis, cone_axis, 0.0, 1.0, 1.0)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order_free_rotor, "Free rotor identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_order_free_rotor[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_disorder(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the identity matrix for disorder."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, R, 0.0, 0.0, 0.0, pi, pi, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_order(self):
        """Check if compile_2nd_matrix_pseudo_ellipse() can return the identity matrix for order."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(self.f2_temp, R, 0.0, 0.0, 0.0, 1e-5, 1e-10, 1e-5)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order, "Identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_order[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_disorder(self):
        """Check if compile_2nd_matrix_pseudo_ellipse_free_rotor() can return the identity matrix for disorder."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, R, 0.0, 0.0, 0.0, pi, pi)

        # Print outs.
        print_frame_order_2nd_degree(self.I_disorder, "Free rotor identity for disorder")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_disorder[i, j])


    def test_compile_2nd_matrix_pseudo_ellipse_free_rotor_order(self):
        """Check if compile_2nd_matrix_pseudo_ellipse_free_rotor() can return the identity matrix for order."""

        # Init.
        R = eye(3)
        z_axis = array([0, 0, 1], float64)
        cone_axis = zeros(3, float64)

        # Calculate the frame order matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.f2_temp, R, 0.0, 0.0, 0.0, 1e-10, 1e-10)

        # Print outs.
        print_frame_order_2nd_degree(self.I_order_free_rotor, "Free rotor identity for order")
        print_frame_order_2nd_degree(f2, "Compiled frame order")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], self.I_order_free_rotor[i, j])


    def xest_compile_2nd_matrix_pseudo_ellipse(self):
        """Check the operation of the compile_2nd_matrix_pseudo_ellipse() function."""

        # The real 2nd degree frame order matrix.
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
        calc = zeros((9, 9), float64)
        R = zeros((3, 3), float64)
        x = pi/4.0
        y = 3.0*pi/8.0
        z = pi/6.0

        # Calculate the matrix.
        f2 = compile_2nd_matrix_pseudo_ellipse(calc, R, 0, 0, 0, x, y, z)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(f2, "calculated")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(f2[i, j], real[i, j], 4)
