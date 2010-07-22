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
from numpy import array, float64, zeros
from unittest import TestCase

# relax module imports.
from generic_fns.frame_order import print_frame_order_2nd_degree
from maths_fns.frame_order_matrix_ops import *


class Test_frame_order_matrix_ops(TestCase):
    """Unit tests for the maths_fns.frame_order_matrix_ops relax module."""


    def test_compile_2nd_matrix_pseudo_ellipse(self):
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

        # Init.
        calc = zeros((9, 9), float64)
        x = pi/4.0
        y = 3.0*pi/8.0
        z = pi/6.0

        # Calculate the matrix.
        compile_2nd_matrix_pseudo_ellipse(calc, x, y, z)

        # Print out.
        print_frame_order_2nd_degree(real, "real")
        print_frame_order_2nd_degree(calc, "calculated")

        # Check the values.
        for i in range(9):
            for j in range(9):
                print "Element %s, %s." % (i, j)
                self.assertAlmostEqual(calc[i, j], real[i, j], 4)
