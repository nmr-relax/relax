###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
from numpy import array, complex64, float64
from unittest import TestCase

# relax module imports.
from lib.linear_algebra.matrix_exponential import matrix_exponential


class Test_matrix_exponential(TestCase):
    """Unit tests for the lib.linear_algebra.matrix_exponential relax module."""


    def test_matrix_exponential(self):
        """Test the matrix exponential function matrix_exponential() with real matrices."""

        # The 3D, rank-2 matrices.
        R1 = array([[1, 4, 5],
                    [-4, 2, 6],
                    [-5, -6, 3]], float64)
        R2 = array([[0, 1, 0],
                    [0, 0, 0],
                    [0, 0, 0]], float64)

        # The real matrix exponentials.
        eR1 = array([[-1.242955024379687, -3.178944439554645,  6.804083368075889],
                     [-6.545353831891249, -2.604941866769356,  1.228233941393001],
                     [ 0.975355249080821, -7.711099455690256, -3.318642157729292]], float64)
        eR2 = array([[ 1.,  0.,  0.],
                     [ 0.,  1.,  0.],
                     [ 0.,  0.,  1.]], float64)

        # The maths.
        eR1_test = matrix_exponential(R1)
        eR2_test = matrix_exponential(R2)

        # Printouts.
        print("Real matrix:\n%s" % eR1)
        print("Calculated matrix:\n%s" % eR1_test)

        # Checks.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(eR1_test[i, j], eR1[i, j])
                self.assertAlmostEqual(eR2_test[i, j], eR2[i, j])


    def test_matrix_exponential2(self):
        """Test the matrix exponential function matrix_exponential() with complex matrices."""

        # The 3D, rank-2 matrix.
        R1 = array([[-0.024156250059605+0.j, 0.021093750372529+0.j],
                    [ 0.021093750372529+0.j, -0.024156250059605-0.587233662605286j]], complex64)

        # The real matrix exponentials.
        eR1 = array([[ 0.976344227790833 -4.17836126871407e-05j,  0.0194285903126001 -0.00587434694170952j],
                     [ 0.0194285865873098 -0.00587435066699982j,  0.812806785106659  -0.540918707847595j]], complex64)

        # The maths.
        eR1_test = matrix_exponential(R1)

        # Printouts.
        print("Real matrix:\n[%20.15g %20.15gj, %20.15g %20.15gj],\n[%20.15g %20.15gj, %20.15g %20.15gj]\n" % (eR1[0, 0].real, eR1[0, 0].imag, eR1[0, 1].real, eR1[0, 1].imag, eR1[1, 0].real, eR1[1, 0].imag, eR1[1, 1].real, eR1[1, 1].imag))
        print("Calculated matrix:\n[%20.15g %20.15gj, %20.15g %20.15gj],\n[%20.15g %20.15gj, %20.15g %20.15gj]\n" % (eR1_test[0, 0].real, eR1_test[0, 0].imag, eR1_test[0, 1].real, eR1_test[0, 1].imag, eR1_test[1, 0].real, eR1_test[1, 0].imag, eR1_test[1, 1].real, eR1_test[1, 1].imag))

        # Checks.
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(eR1_test[i, j].real, eR1[i, j].real, 5)
                self.assertAlmostEqual(eR1_test[i, j].imag, eR1[i, j].imag, 5)
