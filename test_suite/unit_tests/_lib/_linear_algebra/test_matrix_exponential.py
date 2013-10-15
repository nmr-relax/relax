###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
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
from numpy import array, float64, zeros
from unittest import TestCase

# relax module imports.
from lib.linear_algebra.matrix_exponential import matrix_exponential


class Test_matrix_exponential(TestCase):
    """Unit tests for the lib.linear_algebra.matrix_exponential relax module."""


    def test_matrix_exponential(self):
        """Test the Kronecker product function kron_prod()."""

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

        # Checks.
        for i in range(3):
            for j in range(3):
                self.assertEqual(eR1_test[i, j], eR1[i, j])
                self.assertEqual(eR2_test[i, j], eR2[i, j])
